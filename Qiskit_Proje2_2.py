# -*- coding: utf-8 -*-
"""
Created on Thu May  1 08:32:42 2025

@author: pikac
"""

from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
import matplotlib.pyplot as plt
import numpy as np

def create_true_oracle(secret_password):
    n = len(secret_password)
    oracle = QuantumCircuit(n, name="Oracle")
    for i, bit in enumerate(reversed(secret_password)):
        if bit == '0':
            oracle.x(i)
    oracle.h(n-1)
    oracle.mcx(list(range(n-1)), n-1)
    oracle.h(n-1)
    for i, bit in enumerate(reversed(secret_password)):
        if bit == '0':
            oracle.x(i)
    return oracle

def create_diffuser(n_qubits):
    qc = QuantumCircuit(n_qubits, name="Diffuser")
    qc.h(range(n_qubits))
    qc.x(range(n_qubits))
    qc.h(n_qubits-1)
    qc.mcx(list(range(n_qubits-1)), n_qubits-1)
    qc.h(n_qubits-1)
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))
    return qc

def run_grover(secret_password, noise_level=0.0, iterations=1, shots=1024):
    n = len(secret_password)
    qc = QuantumCircuit(n, n)
    qc.h(range(n))
    
    oracle = create_true_oracle(secret_password)
    diffuser = create_diffuser(n)
    
    for _ in range(iterations):
        qc.append(oracle, range(n))
        qc.append(diffuser, range(n))
    
    qc.measure(range(n), range(n))
    
    # Gürültü modeli
    noise_model = None
    if noise_level > 0:
        noise_model = NoiseModel()
        error_1q = depolarizing_error(noise_level, 1)
        error_2q = depolarizing_error(noise_level, 2)
        noise_model.add_all_qubit_quantum_error(error_1q, ['h', 'x', 'z'])
        noise_model.add_all_qubit_quantum_error(error_2q, ['cx', 'mcx'])
    
    backend = AerSimulator(noise_model=noise_model)
    
    # Basit hata azaltma (measurement error mitigation)
    if noise_level > 0:
        from qiskit_aer.noise import ReadoutError
        ro_error = ReadoutError([[1 - noise_level, noise_level], 
                               [noise_level, 1 - noise_level]])
        noise_model.add_all_qubit_readout_error(ro_error)
    
    transpiled_qc = transpile(qc, backend)
    job = backend.run(transpiled_qc, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    title = f"Grover Sonuçları (Gürültü: {noise_level})"
    plot_histogram(counts, title=title)
    plt.show()
    
    return counts

def analyze_results(counts, password):
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    print("\nEn yüksek 5 sonuç:")
    for state, count in sorted_counts[:5]:
        print(f"{state}: {count} ({'✔' if state == password else '✖'})")
    correct_prob = counts.get(password, 0) / sum(counts.values())
    print(f"Doğru sonuç ({password}) olasılığı: {correct_prob:.4f}")
    return correct_prob

def run_full_project():
    secret_password = '1010'
    optimal_iterations = round((np.pi/4) * np.sqrt(2**len(secret_password)))
    
    print(f"\n🔐 Aranan Şifre: {secret_password}")
    print(f"🔁 Optimal İterasyon Sayısı: {optimal_iterations}")
    
    print("\n=== Gürültüsüz Simülasyon ===")
    counts_noiseless = run_grover(secret_password, noise_level=0.0, iterations=optimal_iterations)
    correct_prob_noiseless = analyze_results(counts_noiseless, secret_password)
    
    print("\n=== Gürültülü Simülasyon (0.02) ===")
    counts_noisy = run_grover(secret_password, noise_level=0.02, iterations=optimal_iterations)
    correct_prob_noisy = analyze_results(counts_noisy, secret_password)
    
    print("\n=== Sonuç Karşılaştırması ===")
    print(f"Gürültüsüz olasılık: {correct_prob_noiseless:.4f}")
    print(f"Gürültülü olasılık: {correct_prob_noisy:.4f}")

run_full_project()