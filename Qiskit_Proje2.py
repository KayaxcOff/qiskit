# -*- coding: utf-8 -*-
"""
Created on Thu May  1 08:16:12 2025

@author: pikac
"""

from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit.quantum_info import Statevector
import numpy as np
import matplotlib.pyplot as plt
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

def create_oracle(secret_password):
    """Verilen şifre için bir oracle devresi oluşturur"""
    oracle = QuantumCircuit(len(secret_password), name="Oracle")
    
    # Şifreye göre phase flip uygula
    for i, bit in enumerate(reversed(secret_password)):  # Qiskit bit sıralaması için reversed
        if bit == '1':
            oracle.z(i)
    
    return oracle

def create_diffuser(n_qubits):
    """Grover diffuser devresini oluşturur"""
    qc = QuantumCircuit(n_qubits, name="Diffuser")
    
    # Tüm qubitlere Hadamard uygula
    qc.h(range(n_qubits))
    
    # Tüm qubitlere X uygula
    qc.x(range(n_qubits))
    
    # Çoklu kontrollü Z kapısı (n-1 kontrollü X ve H)
    qc.h(n_qubits-1)
    qc.mcx(list(range(n_qubits-1)), n_qubits-1)  # Düzeltilmiş mcx argümanları
    qc.h(n_qubits-1)
    
    # Tüm qubitlere tekrar X uygula
    qc.x(range(n_qubits))
    
    # Tüm qubitlere Hadamard uygula
    qc.h(range(n_qubits))
    
    return qc

def run_grover(secret_password, noise_level=0.0, iterations=1, shots=1024):
    """Grover algoritmasını manuel olarak uygular"""
    n = len(secret_password)
    qc = QuantumCircuit(n, n)
    
    # Başlangıç süperpozisyonu
    qc.h(range(n))
    
    # Oracle ve diffuser'ı belirtilen iterasyon sayısı kadar uygula
    oracle = create_oracle(secret_password)
    diffuser = create_diffuser(n)
    
    for _ in range(iterations):
        qc.append(oracle, range(n))
        qc.append(diffuser, range(n))
    
    # Ölçüm yap
    qc.measure(range(n), range(n))
    
    # Simülatör seçimi ve gürültü modeli
    backend = AerSimulator()
    if noise_level > 0:
        # Tek ve çift qubitli kapılar için ayrı gürültü modelleri
        noise_model = NoiseModel()
        
        # Tek qubitli kapılar için gürültü
        error_1q = depolarizing_error(noise_level, 1)
        noise_model.add_all_qubit_quantum_error(error_1q, ['h', 'x', 'z'])
        
        # İki qubitli kapılar için gürültü
        error_2q = depolarizing_error(noise_level, 2)
        noise_model.add_all_qubit_quantum_error(error_2q, ['cx'])
        
        backend = AerSimulator(noise_model=noise_model)
    
    # Devreyi çalıştır
    transpiled_qc = transpile(qc, backend)
    job = backend.run(transpiled_qc, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    print("Sonuçlar:", dict(sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]))
    plot_histogram(counts, title=f"Grover Sonuçları (Gürültü: {noise_level})")
    plt.show()
    
    return counts

def analyze_results(counts, password):
    """Sonuçları analiz eder"""
    # En yüksek olasılıklı sonuçları göster
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    print("\nEn yüksek 5 sonuç:")
    for state, count in sorted_counts[:5]:
        print(f"{state}: {count} ({'✔' if state == password else '✖'})")
    
    # Doğru sonucun görülme oranı
    correct_prob = counts.get(password, 0) / sum(counts.values())
    print(f"\nDoğru sonuç ({password}) olasılığı: {correct_prob:.4f}")
    
    return correct_prob

def run_full_project():
    secret_password = '1010'  # Kırmak istediğimiz şifre
    optimal_iterations = 2  # 4 qubit için daha iyi sonuç verir
    
    # 1. Gürültüsüz simülasyon
    print("\n=== Gürültüsüz Simülasyon ===")
    counts_noiseless = run_grover(secret_password, noise_level=0.0, iterations=optimal_iterations)
    correct_prob_noiseless = analyze_results(counts_noiseless, secret_password)
    
    # 2. Gürültülü simülasyon (daha düşük gürültü seviyesi)
    print("\n=== Gürültülü Simülasyon (0.02) ===")
    counts_noisy = run_grover(secret_password, noise_level=0.02, iterations=optimal_iterations)
    correct_prob_noisy = analyze_results(counts_noisy, secret_password)
    
    # Sonuçları karşılaştır
    print("\n=== Sonuç Karşılaştırması ===")
    print(f"Gürültüsüz doğruluk: {max(counts_noiseless, key=counts_noiseless.get) == secret_password}")
    print(f"Gürültülü doğruluk: {max(counts_noisy, key=counts_noisy.get) == secret_password}")
    print(f"Gürültüsüz doğru sonuç olasılığı: {correct_prob_noiseless:.4f}")
    print(f"Gürültülü doğru sonuç olasılığı: {correct_prob_noisy:.4f}")

run_full_project()