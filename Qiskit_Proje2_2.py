# Gerekli kütüphaneler import ediliyor
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import plot_histogram
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
import matplotlib.pyplot as plt
import numpy as np

# Verilen şifreyi doğru tahmin etmek için Oracle oluşturuluyor
def create_true_oracle(secret_password):
    n = len(secret_password)  # Şifrenin uzunluğu
    oracle = QuantumCircuit(n, name="Oracle")  # Oracle için bir kuantum devresi oluşturuluyor
    for i, bit in enumerate(reversed(secret_password)):  # Şifreyi ters sırayla döngüye sokuyoruz
        if bit == '0':  # Eğer bit '0' ise, X kapısı ekliyoruz
            oracle.x(i)
    
    # Oracle için Grover devresi adımları
    oracle.h(n-1)  # Son qubit için Hadamard kapısı
    oracle.mcx(list(range(n-1)), n-1)  # Çoklu kontrol (MCX) kapısı
    oracle.h(n-1)  # Son qubit için tekrar Hadamard
    for i, bit in enumerate(reversed(secret_password)):  # Şifreyi tekrar ters sırayla kullanıyoruz
        if bit == '0':
            oracle.x(i)
    
    return oracle  # Şifreyi doğru tahmin etmek için Oracle devresini döndürüyoruz

# Grover'ın algoritmasındaki Diffuser devresi oluşturuluyor
def create_diffuser(n_qubits):
    qc = QuantumCircuit(n_qubits, name="Diffuser")
    qc.h(range(n_qubits))  # Tüm qubitlere Hadamard kapısı
    qc.x(range(n_qubits))  # X kapısı (bit flip)
    qc.h(n_qubits-1)  # Son qubit için Hadamard
    qc.mcx(list(range(n_qubits-1)), n_qubits-1)  # Çoklu kontrol (MCX) kapısı
    qc.h(n_qubits-1)  # Son qubit için Hadamard
    qc.x(range(n_qubits))  # X kapısı (bit flip)
    qc.h(range(n_qubits))  # Tüm qubitlere Hadamard kapısı
    return qc  # Diffuser devresi döndürülüyor

# Grover'ın arama algoritmasını çalıştıran fonksiyon
def run_grover(secret_password, noise_level=0.0, iterations=1, shots=1024):
    n = len(secret_password)  # Şifrenin uzunluğu
    qc = QuantumCircuit(n, n)  # n qubitlik bir kuantum devresi oluşturuluyor
    qc.h(range(n))  # Başlangıçta tüm qubitlere Hadamard kapısı

    # Oracle ve Diffuser devreleri oluşturuluyor
    oracle = create_true_oracle(secret_password)
    diffuser = create_diffuser(n)

    # Grover algoritması için iterasyonlar
    for _ in range(iterations):
        qc.append(oracle, range(n))  # Oracle devresi ekleniyor
        qc.append(diffuser, range(n))  # Diffuser devresi ekleniyor

    qc.measure(range(n), range(n))  # Sonuçlar ölçülüyor
    
    # Gürültü modeli ayarlanıyor
    noise_model = None
    if noise_level > 0:
        noise_model = NoiseModel()  # Gürültü modelini başlatıyoruz
        error_1q = depolarizing_error(noise_level, 1)  # 1 qubit için depolarizasyon hatası
        error_2q = depolarizing_error(noise_level, 2)  # 2 qubit için depolarizasyon hatası
        noise_model.add_all_qubit_quantum_error(error_1q, ['h', 'x', 'z'])  # H, X, Z kapılarına hatalar ekleniyor
        noise_model.add_all_qubit_quantum_error(error_2q, ['cx', 'mcx'])  # CX ve MCX kapılarına hatalar ekleniyor
    
    # Simülasyon yapacak backend seçiliyor
    backend = AerSimulator(noise_model=noise_model)

    # Eğer gürültü seviyesi varsa, okuma hatası ekleniyor
    if noise_level > 0:
        from qiskit_aer.noise import ReadoutError
        ro_error = ReadoutError([[1 - noise_level, noise_level], [noise_level, 1 - noise_level]])  # Okuma hatası matrisi
        noise_model.add_all_qubit_readout_error(ro_error)  # Okuma hatası modeline ekleniyor
    
    # Devre transpile ediliyor
    transpiled_qc = transpile(qc, backend)
    
    # Simülasyon çalıştırılıyor ve sonuçlar alınıyor
    job = backend.run(transpiled_qc, shots=shots)
    result = job.result()
    counts = result.get_counts()  # Ölçüm sonuçları

    # Sonuçların histogramı çiziliyor
    title = f"Grover Sonuçları (Gürültü: {noise_level})"
    plot_histogram(counts, title=title)
    plt.show()

    return counts  # Sonuçlar döndürülüyor

# Sonuçları analiz eden ve yazdıran fonksiyon
def analyze_results(counts, password):
    sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)  # Sonuçları sıralıyoruz
    print("\nEn yüksek 5 sonuç:")
    for state, count in sorted_counts[:5]:  # İlk 5 sonucu yazdırıyoruz
        print(f"{state}: {count} ({'✔' if state == password else '✖'})")
  
    # Sonuçları doğru (1) veya yanlış (0) olarak işaretliyoruz
    result_output = {state: 1 if state == password else 0 for state, _ in sorted_counts}

    print(f"\nŞifre Durumu: {result_output}")
    
    # Doğru şifreyi bulma olasılığı hesaplanıyor
    correct_prob = counts.get(password, 0) / sum(counts.values())
    print(f"Doğru sonuç ({password}) olasılığı: {correct_prob:.4f}")
    
    return correct_prob  # Olasılık döndürülüyor

# Tüm projeyi çalıştıran ana fonksiyon
def run_full_project():
    secret_password = input("Şifre girin: ")  # Aranan şifre
    optimal_iterations = round((np.pi/4) * np.sqrt(2**len(secret_password)))  # Optimal iterasyon sayısı

    print(f"\n🔐 Aranan Şifre: {secret_password}")
    print(f"🔁 Optimal İterasyon Sayısı: {optimal_iterations}")

    # Gürültüsüz simülasyon
    print("\n=== Gürültüsüz Simülasyon ===")
    counts_noiseless = run_grover(secret_password, noise_level=0.0, iterations=optimal_iterations)
    correct_prob_noiseless = analyze_results(counts_noiseless, secret_password)

    # Gürültülü simülasyon (0.02)
    print("\n=== Gürültülü Simülasyon (0.02) ===")
    counts_noisy = run_grover(secret_password, noise_level=0.02, iterations=optimal_iterations)
    correct_prob_noisy = analyze_results(counts_noisy, secret_password)

    # Sonuç karşılaştırması
    print("\n=== Sonuç Karşılaştırması ===")
    print(f"Gürültüsüz olasılık: {correct_prob_noiseless:.4f}")
    print(f"Gürültülü olasılık: {correct_prob_noisy:.4f}")

# Projeyi çalıştırıyoruz
run_full_project()
