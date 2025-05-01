# -*- coding: utf-8 -*-
"""
Created on Fri Apr 25 07:57:41 2025

@author: pikac
"""

# Gerekli kütüphaneler
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import QFT
from qiskit.quantum_info import Statevector
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
import numpy as np
import matplotlib.pyplot as plt

# --- Spyder için grafik ayarı ---
plt.ion()

# Ağırlıklı atak verileri (güncellenmiş)
weighted_attacks = {
    6: 0.9,
    7: 0.3,
    10: 1.0,
    26: 0.4,
    27: 1.0,
    43: 0.9,
    46: 0.4,
    55: 0.6,
    79: 0.9
}

# 90 dakikalık sinyal (başlangıçta 0)
signal = [0] * 90
for t, val in weighted_attacks.items():
    signal[t] = val

# Grafik 1: Maç boyunca ağırlıklı hücum aktivitesi
plt.figure(figsize=(10, 3))
plt.plot(signal, label='Ağırlıklı Hücum Aktivitesi', color='darkred')
plt.xlabel("Dakika")
plt.ylabel("Atak Şiddeti")
plt.title("Maç Boyunca Galatasaray Hücum Gücü (Güncel)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()

# 8 parçaya böl (~11 dakika her parça)
compressed = [sum(signal[i*11:(i+1)*11]) for i in range(8)]

# Grafik 2: 8 parçaya göre toplam hücum şiddeti
plt.figure(figsize=(7, 3))
plt.bar(range(8), compressed, tick_label=[f"{i*11}-{(i+1)*11}" for i in range(8)], color='gold')
plt.xlabel("Zaman Aralığı (dakika)")
plt.ylabel("Toplam Atak Şiddeti")
plt.title("Zamana Göre Hücumların Yoğunluğu (Güncel)")
plt.tight_layout()
plt.show()

# Normalize et (kuantum devresi için)
normalized = np.array(compressed) / np.linalg.norm(compressed)

# QFT için Statevector devresi
qc_sv = QuantumCircuit(3)
qc_sv.initialize(normalized, range(3))
qc_sv.append(QFT(3, do_swaps=False), range(3))

state = Statevector.from_instruction(qc_sv)
amplitudes = np.abs(state.data)**2

# Grafik 3: QFT sonucu olasılık dağılımı
plt.figure(figsize=(7, 3))
plt.bar(range(8), amplitudes, color='deepskyblue')
plt.xlabel("Frekans (bit dizisi 0-7)")
plt.ylabel("Olasılık (Genlik²)")
plt.title("QFT Frekans Spektrumu (Güncel)")
plt.tight_layout()
plt.show()

# Qiskit ile ölçüm devresi
qc = QuantumCircuit(3)
qc.initialize(normalized, range(3))
qc.append(QFT(3), range(3))
qc.measure_all()

# Simülasyon (Qiskit Aer)
backend = AerSimulator()
qc_transpiled = transpile(qc, backend=backend)
job = backend.run(qc_transpiled, shots=1024)
result = job.result()
counts = result.get_counts()

# Grafik 4: Qiskit ölçüm histogramı
plot_histogram(counts, title="QFT ile Galatasaray Hücum Frekans Analizi (Güncel)")
plt.show()
