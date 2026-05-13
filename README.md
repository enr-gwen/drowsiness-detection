# Drowsiness Detection System

> Sistem deteksi kantuk pengemudi berbasis **Sensor Fusion** dan **Machine Learning**  
> Kelompok 18 — Mata Kuliah Sains Data | Fakultas Informatika, Universitas Siliwangi

---

## ✨ Fitur Terbaru (v2.0)

- 🍞 **Toast Notifications** - Feedback visual yang tidak mengganggu
- 📊 **Plotly Interactive Charts** - Visualisasi interaktif dengan zoom & hover
- 📝 **Table Editor** - Input manual yang lebih cepat dan efisien
- 📥 **Download Results** - Unduh hasil prediksi dalam format CSV
- 🎯 **Metric Deltas** - Lihat selisih P(Alert) dengan threshold
- 💡 **Error Explanations** - Penjelasan detail tentang False Positive/Negative
- ⚡ **Status Containers** - Loading indicator yang informatif
- 🎨 **Enhanced UI** - Border containers, emoji icons, dan spinner

> 📖 **Lihat detail lengkap upgrade di [UPGRADE_NOTES.md](UPGRADE_NOTES.md)**

---

## Deskripsi Proyek

Proyek ini mengembangkan sistem deteksi kantuk pengemudi (*driver drowsiness detection*) menggunakan pendekatan **Sensor Fusion** yang menggabungkan tiga kategori data sensor secara bersamaan:

- **Physiological Sensors (P)** — Sinyal biologis pengemudi (EEG, detak jantung, kedipan mata, dll.)
- **Vehicle Sensors (V)** — Mekanika kendaraan (kecepatan, RPM, sudut setir, dll.)
- **Environmental Sensors (E)** — Kondisi lingkungan kabin dan sekitar kendaraan

Sistem ini menjawab keterbatasan pendekatan Computer Vision tradisional yang rentan terhadap kondisi minim cahaya, kacamata hitam, dan posisi wajah yang tidak ideal.

---

## Dataset

**Ford Stay Alert! Driver Drowsiness Detection Dataset**

| Keterangan | Detail |
|---|---|
| Total Observasi | 604.329 baris |
| Jumlah Fitur | 24 (P1–P7, V2–V11, E1–E11) |
| Kelas Alert | ~58% |
| Kelas Drowsy | ~42% |
| Label | `IsAlert` (1 = Alert, 0 = Drowsy) |

> **Catatan:** Nama fitur **dianonimkan** oleh Ford Motor Company untuk menjaga kerahasiaan teknologi sensor yang dipatenkan.

---

## Arsitektur Pipeline

```
GroupShuffleSplit (by TrialID)
        ↓
WinsorizerTransformer  (clip outlier per fold — no leakage)
        ↓
StandardScaler
        ↓
SMOTE  (oversampling hanya pada training fold)
        ↓
CalibratedClassifierCV (XGBoost)
```

Pipeline dirancang dengan ketat untuk **mencegah data leakage** di setiap tahap. `GroupShuffleSplit` memastikan seluruh observasi dari satu sesi rekaman (`TrialID`) hanya ada di satu set (train/test).

---

## Performa Model

| Model | Accuracy | ROC-AUC | PR-AUC | Recall Drowsy | F1 Drowsy |
|---|---|---|---|---|---|
| Logistic Regression | 0.7682 | 0.8239 | 0.7980 | 0.7234 | 0.7071 |
| Random Forest | 0.8833 | 0.9351 | 0.9234 | 0.7671 | 0.8356 |
| **XGBoost** (Best) | **0.8808** | **0.9307** | **0.9197** | **0.7738** | **0.8339** |

**Model final: XGBoost + CalibratedClassifierCV**  
- Threshold optimal: `0.73`  
- Recall Drowsy pada test set: `0.8207` (8.377 False Negative)  

> **Catatan:** Target Recall Drowsy >= 0.90 belum tercapai di test set — ini adalah konsekuensi gap OOF->Test akibat perbedaan distribusi sesi rekaman.

---

## Cara Menjalankan

### 1. Clone repo
```bash
git clone https://github.com/<username>/drowsiness-detection.git
cd drowsiness-detection
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Siapkan dataset
File `fordTrain.csv` sudah tersedia di dalam repo ini.

### 4. Jalankan Streamlit app
```bash
streamlit run app.py
```

---

## Struktur Folder

```
drowsiness-detection/
├── app.py                              # Streamlit dashboard
├── winsorizer_transformer.py           # Custom sklearn transformer
├── models/
│   ├── full_pipeline.pkl               # Pipeline inference (XGBoost)
│   ├── optimal_threshold.pkl           # Threshold optimal (0.73)
│   └── feature_names.pkl              # Nama 24 fitur input
├── Drowsiness_Detection_System_v2_2.ipynb  # Notebook training & evaluasi
├── requirements.txt
└── README.md
```

---

## Dependencies

```txt
streamlit>=1.32.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
imbalanced-learn>=0.11.0
xgboost>=2.0.0
matplotlib>=3.7.0
plotly>=5.18.0
```

**Update dependencies:**
```bash
pip install -r requirements.txt --upgrade
```

---

## Tim Pengembang

**Kelompok 18** — Mata Kuliah Sains Data  
Fakultas Informatika, Universitas Siliwangi

---

## Lisensi

Dataset: © Ford Motor Company (dianonimkan, digunakan untuk keperluan akademis)  
Kode: MIT License
