# 🚀 Quick Start Guide

Panduan cepat untuk menjalankan Drowsiness Detection System v2.0

---

## 📋 Prerequisites

- Python 3.8 atau lebih tinggi
- pip (Python package manager)
- Git (opsional, untuk clone repository)

---

## ⚡ Instalasi Cepat

### 1. Clone atau Download Repository
```bash
git clone https://github.com/enr-gwen/drowsiness-detection.git
cd drowsiness-detection
```

Atau download ZIP dan extract.

---

### 2. Install Dependencies

**Opsi A: Install Semua (Recommended)**
```bash
pip install -r requirements.txt
```

**Opsi B: Install Satu per Satu**
```bash
pip install streamlit>=1.32.0
pip install pandas>=2.0.0
pip install numpy>=1.24.0
pip install scikit-learn>=1.3.0
pip install imbalanced-learn>=0.11.0
pip install xgboost>=2.0.0
pip install matplotlib>=3.7.0
pip install plotly>=5.18.0
```

---

### 3. Verifikasi Instalasi
```bash
python -c "import streamlit; print(f'Streamlit version: {streamlit.__version__}')"
```

Pastikan versi Streamlit >= 1.32.0

---

### 4. Jalankan Aplikasi
```bash
streamlit run app.py
```

Aplikasi akan terbuka otomatis di browser pada `http://localhost:8501`

---

## 🎮 Cara Menggunakan

### Mode 1: Demo Otomatis
1. Pilih tab **"Demo Otomatis"**
2. Klik tombol **"🔄 Ambil Sampel Baru"**
3. Lihat hasil prediksi dan confidence level
4. Klik **"📥 Download Hasil"** untuk menyimpan hasil

### Mode 2: Input Manual
1. Pilih tab **"Input Manual"**
2. Pilih mode input:
   - **🎚️ Slider Input**: Input nilai satu per satu
   - **📝 Table Editor**: Edit langsung di tabel (lebih cepat!)
3. Masukkan nilai sensor
4. Klik **"🔍 Prediksi"**
5. Download hasil jika diperlukan

### Mode 3: Interpretasi Model
1. Pilih tab **"Interpretasi Model"**
2. Pilih jenis visualisasi:
   - **📊 Plotly (Interaktif)**: Hover, zoom, pan
   - **📈 Matplotlib (Statis)**: Chart tradisional
3. Lihat sensor mana yang paling berpengaruh

### Mode 4: Tentang Proyek
1. Pilih tab **"Tentang Proyek"**
2. Baca informasi lengkap tentang:
   - Latar belakang
   - Dataset
   - Arsitektur pipeline
   - Performa model

---

## 🔧 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'streamlit'"
**Solusi:**
```bash
pip install streamlit
```

### Error: "st.toast is not defined"
**Solusi:** Upgrade Streamlit
```bash
pip install streamlit --upgrade
```

### Error: "FileNotFoundError: fordTrain.csv"
**Solusi:** Pastikan file `fordTrain.csv` ada di folder yang sama dengan `app.py`

### Error: "ModuleNotFoundError: No module named 'winsorizer_transformer'"
**Solusi:** Pastikan file `winsorizer_transformer.py` ada di folder yang sama dengan `app.py`

### Error: "FileNotFoundError: models/full_pipeline.pkl"
**Solusi:** Pastikan folder `models/` berisi:
- `full_pipeline.pkl`
- `optimal_threshold.pkl`
- `feature_names.pkl`

### Aplikasi Lambat
**Solusi:**
1. Pastikan menggunakan Python 3.8+
2. Close aplikasi lain yang berat
3. Restart aplikasi Streamlit

---

## 📱 Akses dari Perangkat Lain

### Akses dari HP/Tablet di Jaringan yang Sama
1. Cari IP address komputer Anda:
   ```bash
   # Windows
   ipconfig
   
   # Mac/Linux
   ifconfig
   ```
2. Jalankan Streamlit dengan network access:
   ```bash
   streamlit run app.py --server.address 0.0.0.0
   ```
3. Buka browser di HP/Tablet, akses:
   ```
   http://<IP_ADDRESS>:8501
   ```

---

## 🎯 Tips & Tricks

### 1. Keyboard Shortcuts
- `R` - Rerun aplikasi
- `C` - Clear cache
- `Ctrl + C` - Stop server (di terminal)

### 2. Kustomisasi Port
```bash
streamlit run app.py --server.port 8080
```

### 3. Dark Mode
Klik ⋮ (menu) di pojok kanan atas → Settings → Theme → Dark

### 4. Auto-reload saat Development
Streamlit otomatis reload saat file `.py` diubah

---

## 📊 Sample Data

Dataset `fordTrain.csv` berisi:
- **604,329 observasi**
- **24 fitur sensor** (P1-P7, V2-V11, E1-E11)
- **Label IsAlert** (1 = Alert, 0 = Drowsy)

---

## 🆘 Butuh Bantuan?

- 📖 [Dokumentasi Lengkap](UPGRADE_NOTES.md)
- 🐛 [Report Bug](https://github.com/enr-gwen/drowsiness-detection/issues)
- 💬 [Diskusi](https://github.com/enr-gwen/drowsiness-detection/discussions)

---

## 🎓 Credits

**Kelompok 18** - Mata Kuliah Sains Data  
Fakultas Informatika, Universitas Siliwangi

---

**Selamat mencoba! 🚀**
