# -*- coding: utf-8 -*-
"""
Created on Sun Apr  6 08:21:57 2025

@author: pikac
"""
# Gerekli kütüphaneleri içe aktarma
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator, StatevectorSimulator
from qiskit.visualization import plot_histogram, plot_bloch_multivector, plot_state_city

# Devre oluşturma
qc = QuantumCircuit(3, 3) # q_0, q_1, q_2 ve c_0, c_1, c_2

# Kapıları uygulama
qc.h(0) # q_0'a h kapısı uygulama
qc.h(1) # q_1'e h kapısı uygulama

qc.x(0) # q_0'a x kapısı uygulama
qc.x(1) # q_1'e x kapısı uygulama

qc.ccx(0, 1, 2) # devreye toffoli kapısı uygulama
# q_0 ve q_1 kontrol, q_1 hedef

# Devreyi çizdirme
print("Devre Şeması: ")
print(qc.draw())

# Simülasyon ve sonuçlar
simulator = AerSimulator()
qc.measure([0, 1, 2], [0, 1, 2]) # ölçüm yapma
job = simulator.run(qc, shots = 1024)
result = job.result()
counts = result.get_counts()
print("\nAerSimulator Sonuçları:")
print(counts)
plot_histogram(counts)

# StatevectorSimulator ile kuantum durumu alma (ölçüm öncesi)
state_simulator = StatevectorSimulator()
qc_no_meause = QuantumCircuit(3)
qc_no_meause.h(0)
qc_no_meause.h(1)
qc_no_meause.x(0)
qc_no_meause.x(1)
qc_no_meause.ccx(0, 1, 2)
job_state = state_simulator.run(qc_no_meause)
state = job_state.result().get_statevector()
print("Kuantum durumu: ")
print(state)

# Görselleştirme
print("\nBloch Küresi Görselleştirme:")
plot_bloch_multivector(state)

print("\nState City Görselleştirme:")
plot_state_city(state)

