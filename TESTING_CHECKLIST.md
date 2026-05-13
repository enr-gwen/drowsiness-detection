# ✅ Testing Checklist - Drowsiness Detection v2.0

## 🔍 Pre-Testing Setup

- [x] Streamlit version: 1.57.0 ✅ (Mendukung semua fitur baru)
- [ ] Dependencies terinstall semua
- [ ] File `fordTrain.csv` tersedia
- [ ] Folder `models/` berisi 3 file pkl
- [ ] File `winsorizer_transformer.py` tersedia

---

## 🧪 Testing Scenarios

### 1. Mode Demo Otomatis

#### Test 1.1: Loading Dataset
- [ ] Buka aplikasi
- [ ] Pilih tab "Demo Otomatis"
- [ ] Status container "📊 Memuat dataset..." muncul
- [ ] Status berubah menjadi "✅ Dataset siap!"
- [ ] **Expected**: Loading indicator muncul dan hilang setelah selesai

#### Test 1.2: Ambil Sampel Baru
- [ ] Klik tombol "🔄 Ambil Sampel Baru"
- [ ] Toast notification "✅ Sampel baru berhasil diambil!" muncul
- [ ] Data sensor ditampilkan dalam 3 tab (P, V, E)
- [ ] Hasil prediksi muncul (DROWSY atau ALERT)
- [ ] **Expected**: Toast muncul di pojok kanan atas, data berubah

#### Test 1.3: Metric dengan Delta
- [ ] Lihat metric "P(Alert)"
- [ ] Delta (selisih dari threshold) ditampilkan
- [ ] Delta berwarna hijau jika positif, merah jika negatif
- [ ] **Expected**: Delta muncul di bawah nilai P(Alert)

#### Test 1.4: Progress Bar dengan Text
- [ ] Progress bar ditampilkan
- [ ] Text "Model yakin X% pengemudi dalam kondisi Alert" muncul di dalam progress bar
- [ ] **Expected**: Text terintegrasi dalam progress bar, bukan caption terpisah

#### Test 1.5: Download Hasil
- [ ] Klik tombol "📥 Download Hasil"
- [ ] File CSV terdownload
- [ ] Buka file CSV, cek isinya
- [ ] **Expected**: File berisi Sample_Index, P_Alert, Threshold, Prediction, Actual

#### Test 1.6: Error Explanation (jika prediksi salah)
- [ ] Jika prediksi salah, expander "ℹ️ Mengapa prediksi salah?" muncul
- [ ] Klik expander
- [ ] Penjelasan False Positive atau False Negative ditampilkan
- [ ] **Expected**: Penjelasan sesuai dengan jenis error

---

### 2. Mode Input Manual

#### Test 2.1: Toggle Input Mode
- [ ] Pilih tab "Input Manual"
- [ ] Radio button "🎚️ Slider Input" dan "📝 Table Editor" muncul
- [ ] Pilih "🎚️ Slider Input"
- [ ] Slider untuk semua sensor muncul
- [ ] **Expected**: Slider mode aktif

#### Test 2.2: Slider Input
- [ ] Ubah nilai beberapa sensor dengan slider
- [ ] Nilai berubah sesuai input
- [ ] **Expected**: Slider responsif

#### Test 2.3: Table Editor
- [ ] Pilih "📝 Table Editor"
- [ ] Tabel dengan semua sensor muncul
- [ ] Edit beberapa nilai langsung di tabel
- [ ] Nilai berubah sesuai input
- [ ] **Expected**: Table editor responsif, lebih cepat dari slider

#### Test 2.4: Prediksi dengan Spinner
- [ ] Klik tombol "🔍 Prediksi"
- [ ] Spinner "Memproses data sensor..." muncul
- [ ] Toast "✅ Prediksi selesai!" muncul setelah selesai
- [ ] **Expected**: Spinner muncul saat proses, toast muncul setelah selesai

#### Test 2.5: Container dengan Border
- [ ] Hasil prediksi ditampilkan dalam container dengan border
- [ ] Border terlihat jelas
- [ ] **Expected**: Container menonjol dengan border

#### Test 2.6: Download Hasil Manual
- [ ] Klik tombol "📥 Download Hasil"
- [ ] File CSV terdownload
- [ ] Buka file CSV, cek isinya
- [ ] **Expected**: File berisi P_Alert, Threshold, Prediction, dan semua nilai sensor

---

### 3. Mode Interpretasi Model

#### Test 3.1: Toggle Chart Type
- [ ] Pilih tab "Interpretasi Model"
- [ ] Radio button "📊 Plotly (Interaktif)" dan "📈 Matplotlib (Statis)" muncul
- [ ] **Expected**: Toggle muncul

#### Test 3.2: Plotly Interactive Chart
- [ ] Pilih "📊 Plotly (Interaktif)"
- [ ] Chart horizontal bar muncul
- [ ] Hover mouse ke bar → tooltip muncul
- [ ] Zoom in/out dengan scroll mouse
- [ ] Pan dengan drag mouse
- [ ] Klik legend untuk hide/show kategori
- [ ] **Expected**: Chart interaktif, semua fitur berfungsi

#### Test 3.3: Plotly Export
- [ ] Klik icon camera di pojok kanan atas chart
- [ ] Chart terdownload sebagai PNG
- [ ] **Expected**: Export berfungsi

#### Test 3.4: Matplotlib Static Chart
- [ ] Pilih "📈 Matplotlib (Statis)"
- [ ] Chart horizontal bar muncul (statis)
- [ ] **Expected**: Chart statis seperti sebelumnya

#### Test 3.5: Feature Importance Data
- [ ] Scroll ke bawah
- [ ] Ringkasan "3 sensor paling berpengaruh" muncul
- [ ] **Expected**: Data sesuai dengan chart

---

### 4. Mode Tentang Proyek

#### Test 4.1: Informasi Lengkap
- [ ] Pilih tab "Tentang Proyek"
- [ ] Latar belakang ditampilkan
- [ ] Metrics dataset ditampilkan (4 kolom)
- [ ] Arsitektur pipeline ditampilkan
- [ ] Tabel performa model ditampilkan
- [ ] **Expected**: Semua informasi lengkap

#### Test 4.2: Styled Dataframe
- [ ] Tabel performa model memiliki highlighting
- [ ] Nilai terbaik di-highlight dengan warna hijau
- [ ] **Expected**: Highlighting berfungsi

---

### 5. General UI/UX

#### Test 5.1: Page Configuration
- [ ] Klik menu ⋮ di pojok kanan atas
- [ ] Menu "Get Help" ada
- [ ] Menu "Report a bug" ada
- [ ] Menu "About" ada
- [ ] **Expected**: Menu items muncul

#### Test 5.2: Emoji Icons
- [ ] Semua button menggunakan emoji (🔄, 🔍, 📥)
- [ ] Emoji terlihat jelas
- [ ] **Expected**: Emoji native, bukan text

#### Test 5.3: Responsive Layout
- [ ] Resize browser window
- [ ] Layout menyesuaikan
- [ ] **Expected**: Responsive

#### Test 5.4: Kamus Istilah
- [ ] Expand "Kamus Istilah"
- [ ] Klik salah satu istilah (popover)
- [ ] Definisi muncul
- [ ] **Expected**: Popover berfungsi

#### Test 5.5: Info Sensor
- [ ] Expand "Tentang Dataset & Sensor"
- [ ] Informasi 3 kategori sensor muncul
- [ ] **Expected**: Informasi lengkap

---

## 🐛 Bug Tracking

| Bug ID | Deskripsi | Severity | Status |
|--------|-----------|----------|--------|
| - | - | - | - |

---

## 📊 Test Results Summary

- **Total Tests**: 30
- **Passed**: ___
- **Failed**: ___
- **Skipped**: ___
- **Success Rate**: ___%

---

## 🔧 Environment Info

- **OS**: Linux
- **Python**: 3.x
- **Streamlit**: 1.57.0
- **Browser**: ___________
- **Screen Resolution**: ___________

---

## 📝 Notes

Catatan tambahan selama testing:

```
[Tulis catatan di sini]
```

---

## ✅ Sign-off

- [ ] Semua fitur baru berfungsi dengan baik
- [ ] Tidak ada breaking changes
- [ ] Dokumentasi lengkap
- [ ] Ready for production

**Tested by**: ___________  
**Date**: ___________  
**Signature**: ___________

---

## 🚀 Deployment Checklist

Setelah testing selesai:

- [ ] Update version number di app.py
- [ ] Commit semua perubahan ke Git
- [ ] Push ke repository
- [ ] Update README.md jika perlu
- [ ] Deploy ke production (jika ada)
- [ ] Notify team members

---

**Happy Testing! 🎉**
