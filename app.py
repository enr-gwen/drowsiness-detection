import streamlit as st
import pickle
import sys
import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
import matplotlib.pyplot as plt
# pyrefly: ignore [missing-import]
import matplotlib.patches as mpatches
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go

# pyrefly: ignore [missing-import]
from winsorizer_transformer import WinsorizerTransformer

# Agar pickle bisa resolve class yang disimpan sebagai __main__.WinsorizerTransformer
sys.modules['__main__'].WinsorizerTransformer = WinsorizerTransformer

st.set_page_config(
    page_title="Drowsiness Detection",
    page_icon="car",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/enr-gwen/drowsiness-detection',
        'Report a bug': 'https://github.com/enr-gwen/drowsiness-detection/issues',
        'About': '# Drowsiness Detection System\nKelompok 18 - Universitas Siliwangi'
    }
)

# ── Kamus Istilah ─────────────────────────────────────────────
KAMUS = {
    "P(Alert)": (
        "Probabilitas yang dihasilkan model bahwa pengemudi dalam kondisi "
        "waspada (Alert). Nilainya berkisar antara 0.0 hingga 1.0. "
        "Semakin mendekati 1.0, model semakin yakin pengemudi Alert."
    ),
    "Threshold": (
        "Batas keputusan yang digunakan untuk mengklasifikasikan hasil prediksi. "
        "Jika P(Alert) ≥ Threshold → prediksi Alert. "
        "Jika P(Alert) < Threshold → prediksi Drowsy. "
        "Nilai threshold dioptimalkan dari data training agar Recall Drowsy ≥ 0.90."
    ),
    "Recall Drowsy": (
        "Persentase kasus Drowsy yang berhasil dideteksi model. "
        "Metrik prioritas dalam konteks keselamatan — semakin tinggi, "
        "semakin sedikit pengemudi ngantuk yang lolos tidak terdeteksi (False Negative)."
    ),
    "PR-AUC": (
        "Precision-Recall Area Under Curve. Metrik paling jujur untuk data imbalanced. "
        "Tidak terpengaruh oleh jumlah True Negative yang besar dari kelas mayoritas (Alert), "
        "sehingga lebih mencerminkan kemampuan model mendeteksi kelas minoritas (Drowsy)."
    ),
    "ROC-AUC": (
        "Receiver Operating Characteristic Area Under Curve. "
        "Mengukur kemampuan model membedakan dua kelas secara keseluruhan. "
        "Pada data imbalanced, nilai ini bisa menyesatkan karena terkatrol "
        "oleh tingginya True Negative dari kelas mayoritas."
    ),
    "False Positive": (
        "Model memprediksi Drowsy padahal pengemudi sebenarnya Alert. "
        "Dalam konteks keselamatan, ini masih dapat diterima — "
        "lebih baik sistem memperingatkan pengemudi yang sebenarnya sadar "
        "daripada melewatkan pengemudi yang benar-benar mengantuk."
    ),
    "False Negative": (
        "Model memprediksi Alert padahal pengemudi sebenarnya Drowsy. "
        "Ini adalah kesalahan paling berbahaya dalam sistem deteksi kantuk "
        "karena pengemudi yang mengantuk tidak mendapat peringatan."
    ),
    "Sensor Fusion": (
        "Pendekatan yang menggabungkan data dari multiple sensor berbeda "
        "(Physiological + Vehicle + Environmental) untuk menghasilkan prediksi "
        "yang lebih akurat dibanding menggunakan satu jenis sensor saja."
    ),
    "CalibratedClassifierCV": (
        "Teknik kalibrasi probabilitas yang diterapkan pada model XGBoost. "
        "Memastikan nilai P(Alert) yang dihasilkan lebih mencerminkan "
        "probabilitas sebenarnya, bukan sekadar skor mentah dari model."
    ),
    "Feature Importance": (
        "Ukuran seberapa besar kontribusi setiap sensor terhadap keputusan model. "
        "Dihitung dari rata-rata penurunan impurity (gain) selama proses training XGBoost. "
        "Semakin tinggi nilainya, semakin berpengaruh sensor tersebut."
    ),
    "SMOTE": (
        "Synthetic Minority Oversampling Technique. Teknik untuk menangani "
        "ketidakseimbangan kelas dengan membuat data sintetis untuk kelas minoritas (Drowsy). "
        "Diterapkan hanya pada data training, tidak pada test set."
    ),
    "GroupShuffleSplit": (
        "Metode pembagian data train-test yang memastikan seluruh observasi "
        "dari satu sesi rekaman (TrialID) hanya ada di satu set (train atau test). "
        "Mencegah data leakage temporal pada data time-series."
    ),
}

# ── Deskripsi Sensor ─────────────────────────────────────────
SENSOR_INFO = {
    'P': {
        'label': 'Physiological Sensors',
        'desc': (
            'Mengukur kondisi biologis pengemudi secara real-time. '
            'Umumnya merepresentasikan sinyal seperti detak jantung, '
            'gelombang otak (EEG), pola kedipan mata, atau postur kepala. '
            'Dianonimkan oleh Ford untuk menjaga kerahasiaan teknologi sensor.'
        )
    },
    'V': {
        'label': 'Vehicle Sensors',
        'desc': (
            'Mengukur mekanika kendaraan secara langsung. '
            'Merepresentasikan parameter seperti kecepatan, RPM mesin, '
            'sudut putaran setir, percepatan, dan tekanan pedal rem/gas. '
            'Dianonimkan oleh Ford untuk menjaga kerahasiaan teknologi sensor.'
        )
    },
    'E': {
        'label': 'Environmental Sensors',
        'desc': (
            'Mengukur kondisi lingkungan di dalam kabin maupun sekitar kendaraan. '
            'Merepresentasikan parameter seperti posisi terhadap garis jalan, '
            'suhu kabin, dan intensitas cahaya sekitar. '
            'Dianonimkan oleh Ford untuk menjaga kerahasiaan teknologi sensor.'
        )
    }
}

# ── Data Performa Model ───────────────────────────────────────
# Nilai diperbarui sesuai hasil notebook Drowsiness_Detection_System_v2_2
# Threshold optimal = 0.73 | Evaluasi final test set (satu kali sentuh)
MODEL_METRICS = {
    'Logistic Regression': {
        'Accuracy':       0.7682,
        'ROC-AUC':        0.8239,
        'PR-AUC Drowsy':  0.7980,
        'Recall Drowsy':  0.7234,
        'F1 Drowsy':      0.7071,
        'CV Recall':      '0.7723 ± 0.0399',
    },
    'Random Forest': {
        'Accuracy':       0.8833,
        'ROC-AUC':        0.9351,
        'PR-AUC Drowsy':  0.9234,
        'Recall Drowsy':  0.7671,
        'F1 Drowsy':      0.8356,
        'CV Recall':      '0.8507 ± 0.0079',
    },
    'XGBoost': {
        'Accuracy':       0.8733,  # Final test set @ threshold 0.73
        'ROC-AUC':        0.9307,
        'PR-AUC Drowsy':  0.9197,
        'Recall Drowsy':  0.8207,  # Final test set @ threshold 0.73
        'F1 Drowsy':      0.8336,  # Final test set @ threshold 0.73
        'CV Recall':      '0.8494 ± 0.0027',
    },
}

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .header-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .header-box h1 {
        color: #ffffff;
        font-size: 2rem;
        margin: 0;
        font-weight: 700;
        letter-spacing: 1px;
    }
    .header-box p {
        color: #a0aec0;
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
    }
    .result-drowsy {
        background: #fff5f5;
        border-left: 5px solid #e53e3e;
        padding: 1.2rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .result-drowsy h2 { color: #c53030; margin: 0; font-size: 1.6rem; }
    .result-drowsy p  { color: #742a2a; margin: 0.3rem 0 0 0; font-size: 0.95rem; }
    .result-alert {
        background: #f0fff4;
        border-left: 5px solid #38a169;
        padding: 1.2rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    .result-alert h2 { color: #276749; margin: 0; font-size: 1.6rem; }
    .result-alert p  { color: #22543d; margin: 0.3rem 0 0 0; font-size: 0.95rem; }
    .badge-correct {
        background: #c6f6d5;
        color: #22543d;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-wrong {
        background: #fed7d7;
        color: #742a2a;
        padding: 3px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .metric-card {
        background: #ffffff;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.5rem;
    }
    .pipeline-step {
        display: inline-block;
        background: #ebf8ff;
        border: 1px solid #bee3f8;
        color: #2b6cb0;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 2px;
    }
    .footer {
        text-align: center;
        color: #a0aec0;
        font-size: 0.8rem;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

# ── Load Artefak ─────────────────────────────────────────────
@st.cache_resource
def load_artifacts():
    with open('models/full_pipeline.pkl', 'rb') as f:
        pipeline = pickle.load(f)
    with open('models/optimal_threshold.pkl', 'rb') as f:
        threshold = pickle.load(f)
    with open('models/feature_names.pkl', 'rb') as f:
        feature_names = pickle.load(f)
    return pipeline, threshold, feature_names

@st.cache_data
def load_dataset():
    return pd.read_csv('fordTrain.csv')

pipeline, threshold, feature_names = load_artifacts()

p_cols = [f for f in feature_names if f.startswith('P')]
v_cols = [f for f in feature_names if f.startswith('V')]
e_cols = [f for f in feature_names if f.startswith('E')]

# ── Header ───────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
    <h1>Drowsiness Detection System</h1>
    <p>
        Sensor Fusion berbasis Machine Learning untuk deteksi kantuk pengemudi secara real-time
        &nbsp;|&nbsp; Kelompok 18 &nbsp;|&nbsp; Universitas Siliwangi
    </p>
</div>
""", unsafe_allow_html=True)

# ── Expander Info Sensor ──────────────────────────────────────
with st.expander("Tentang Dataset & Sensor"):
    st.info(
        "Deskripsi spesifik setiap fitur **(P, E, V)** telah **dianonimkan** "
        "oleh Ford Motor Company untuk menjaga kerahasiaan teknologi sensor "
        "yang dipatenkan. Kode huruf mewakili kategori besar masing-masing "
        "sensor. Sumber: Ford Stay Alert! Driver Drowsiness Detection Dataset."
    )
    ci1, ci2, ci3 = st.columns(3)
    with ci1:
        st.markdown(f"**{SENSOR_INFO['P']['label']} (P1–P7)**")
        st.caption(SENSOR_INFO['P']['desc'])
    with ci2:
        st.markdown(f"**{SENSOR_INFO['V']['label']} (V2–V11)**")
        st.caption(SENSOR_INFO['V']['desc'])
    with ci3:
        st.markdown(f"**{SENSOR_INFO['E']['label']} (E1–E11)**")
        st.caption(SENSOR_INFO['E']['desc'])

# ── Expander Kamus Istilah ────────────────────────────────────
with st.expander("Kamus Istilah"):
    st.caption("Klik istilah di bawah untuk melihat definisinya.")
    st.markdown("")
    cols = st.columns(4)
    for i, (istilah, definisi) in enumerate(KAMUS.items()):
        with cols[i % 4]:
            with st.popover(istilah):
                st.markdown(f"**{istilah}**")
                st.markdown(definisi)

st.markdown("---")

# ── Mode Selector ─────────────────────────────────────────────
mode = st.segmented_control(
    "Mode",
    ["Demo Otomatis", "Input Manual", "Interpretasi Model", "Tentang Proyek"],
    default="Demo Otomatis"
)

st.markdown("")

# ════════════════════════════════════════════════════════════
# MODE 1: DEMO OTOMATIS
# ════════════════════════════════════════════════════════════
if mode == "Demo Otomatis":
    st.markdown(
        "Sistem mengambil data sensor acak dari dataset dan memprediksi "
        "kondisi pengemudi secara langsung."
    )
    st.markdown("")

    ambil_btn = st.button("Ambil Sampel Baru", type="primary", use_container_width=False)

    try:
        with st.status("Memuat dataset...", expanded=False) as status:
            df = load_dataset()
            # Hanya ambil 24 fitur yang digunakan model final (feature_names dari pkl)
            # Kolom non-fitur: IsAlert, TrialID, ObsNum — sisanya sudah di-handle oleh feature_names
            drop_cols = [
                c for c in ['IsAlert', 'TrialID', 'ObsNum']
                if c in df.columns
            ]
            df_feat = df.drop(columns=drop_cols)[feature_names]
            status.update(label="Dataset siap!", state="complete", expanded=False)

        if ambil_btn or 'sample_idx' not in st.session_state:
            st.session_state.sample_idx = np.random.randint(0, len(df_feat))
            if ambil_btn:
                st.toast("Sampel baru berhasil diambil!", )

        idx    = st.session_state.sample_idx
        sample = df_feat.iloc[[idx]]
        actual = int(df.iloc[idx]['IsAlert']) if 'IsAlert' in df.columns else None

        proba = pipeline.predict_proba(sample)[0, 1]
        pred  = int(proba >= threshold)

        st.caption(f"Data diambil dari baris ke-{idx} dataset fordTrain.csv")
        st.markdown("")

        col_left, col_right = st.columns([1.3, 1], gap="large")

        with col_left:
            st.markdown("#### Nilai Sensor")
            tab1, tab2, tab3 = st.tabs([
                SENSOR_INFO['P']['label'],
                SENSOR_INFO['V']['label'],
                SENSOR_INFO['E']['label']
            ])
            with tab1:
                st.caption(SENSOR_INFO['P']['desc'])
                st.dataframe(
                    sample[p_cols].T.rename(columns={sample.index[0]: 'Nilai'}),
                    use_container_width=True
                )
            with tab2:
                st.caption(SENSOR_INFO['V']['desc'])
                st.dataframe(
                    sample[v_cols].T.rename(columns={sample.index[0]: 'Nilai'}),
                    use_container_width=True
                )
            with tab3:
                st.caption(SENSOR_INFO['E']['desc'])
                st.dataframe(
                    sample[e_cols].T.rename(columns={sample.index[0]: 'Nilai'}),
                    use_container_width=True
                )

        with col_right:
            st.markdown("#### Hasil Prediksi")

            if pred == 0:
                st.markdown("""
                <div class="result-drowsy">
                    <h2>DROWSY</h2>
                    <p>Pengemudi terdeteksi mengantuk.<br>
                    Segera berhenti dan istirahat.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-alert">
                    <h2>ALERT</h2>
                    <p>Pengemudi dalam kondisi waspada<br>
                    dan aman untuk berkendara.</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("")
            m1, m2 = st.columns(2)
            m1.metric(
                "P(Alert)",
                f"{proba:.4f}",
                delta=f"{(proba - threshold):.4f}",
                delta_color="normal"
            )
            m2.metric("Threshold", f"{threshold:.2f}")

            _gc = "#e53e3e" if pred == 0 else "#38a169"
            _gfig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=round(proba * 100, 1),
                number={'suffix': '%', 'font': {'size': 26}},
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Confidence P(Alert)", 'font': {'size': 13}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': _gc},
                    'steps': [
                        {'range': [0, threshold * 100], 'color': '#fff5f5'},
                        {'range': [threshold * 100, 100], 'color': '#f0fff4'},
                    ],
                    'threshold': {
                        'line': {'color': '#2b6cb0', 'width': 3},
                        'thickness': 0.75,
                        'value': threshold * 100
                    }
                }
            ))
            _gfig.update_layout(
                height=220, margin=dict(l=10, r=10, t=40, b=10),
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(_gfig, use_container_width=True, config={'displayModeBar': False})
            


            if actual is not None:
                st.markdown("---")
                actual_text = "Alert" if actual == 1 else "Drowsy"
                if pred == actual:
                    match_html = '<span class="badge-correct">Prediksi Benar</span>'
                elif pred == 0 and actual == 1:
                    match_html = '<span class="badge-wrong">False Positive (Drowsy padahal Alert)</span>'
                else:
                    match_html = '<span class="badge-wrong">False Negative (Alert padahal Drowsy)</span>'
                st.markdown(f"**Label Asli Dataset:** `{actual_text}`")
                st.markdown(
                    f"**Akurasi Sampel:** {match_html}",
                    unsafe_allow_html=True
                )
                
                # Dialog untuk penjelasan detail
                if pred != actual:
                    with st.expander("Mengapa prediksi salah?"):
                        if pred == 0 and actual == 1:
                            st.warning(
                                "**False Positive**: Model memprediksi Drowsy padahal sebenarnya Alert. "
                                "Ini bisa terjadi karena pola sensor menyerupai kondisi kantuk. "
                                "Dalam konteks keselamatan, ini lebih baik daripada False Negative."
                            )
                        else:
                            st.error(
                                "**False Negative**: Model memprediksi Alert padahal sebenarnya Drowsy. "
                                "Ini adalah kesalahan paling berbahaya karena pengemudi yang mengantuk "
                                "tidak mendapat peringatan. Model perlu ditingkatkan untuk mengurangi kasus ini."
                            )
            
            st.markdown("---")
            
            # Download hasil prediksi
            result_data = {
                'Sample_Index': [idx],
                'P_Alert': [proba],
                'Threshold': [threshold],
                'Prediction': ['Alert' if pred == 1 else 'Drowsy'],
                'Actual': [actual_text if actual is not None else 'N/A']
            }
            result_df = pd.DataFrame(result_data)
            
            csv = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Hasil",
                data=csv,
                file_name=f"prediction_result_{idx}.csv",
                mime="text/csv",
                use_container_width=True
            )

            # ── Riwayat Prediksi ─────────────────────────────
            if 'pred_history' not in st.session_state:
                st.session_state.pred_history = []
            _actual_disp = ("Alert" if actual == 1 else "Drowsy") if actual is not None else 'N/A'
            _hasil = 'Benar' if pred == actual else ('FP' if pred == 0 else 'FN')
            _entry = {
                'Baris': idx,
                'P(Alert)': f"{proba:.4f}",
                'Prediksi': 'Alert' if pred == 1 else 'Drowsy',
                'Aktual': _actual_disp,
                'Hasil': _hasil
            }
            if (not st.session_state.pred_history or
                    st.session_state.pred_history[-1]['Baris'] != idx):
                st.session_state.pred_history.append(_entry)
            st.session_state.pred_history = st.session_state.pred_history[-10:]
            if len(st.session_state.pred_history) > 1:
                with st.expander(f"Riwayat Prediksi ({len(st.session_state.pred_history)} entri terakhir)"):
                    st.dataframe(
                        pd.DataFrame(st.session_state.pred_history[::-1]),
                        use_container_width=True, hide_index=True
                    )
                    if st.button("Hapus Riwayat", key="clear_history"):
                        st.session_state.pred_history = []
                        st.rerun()

    except FileNotFoundError:
        st.warning(
            "File fordTrain.csv tidak ditemukan. "
            "Letakkan file CSV di folder yang sama dengan app.py."
        )

# ════════════════════════════════════════════════════════════
# MODE 2: INPUT MANUAL
# ════════════════════════════════════════════════════════════
elif mode == "Input Manual":
    st.markdown(
        "Masukkan nilai sensor secara manual untuk memprediksi "
        "kondisi pengemudi."
    )
    st.markdown("")

    with st.expander("Keterangan Sensor", expanded=True):
        ci1, ci2, ci3 = st.columns(3)
        with ci1:
            st.markdown(f"**{SENSOR_INFO['P']['label']}**")
            st.caption(SENSOR_INFO['P']['desc'])
        with ci2:
            st.markdown(f"**{SENSOR_INFO['V']['label']}**")
            st.caption(SENSOR_INFO['V']['desc'])
        with ci3:
            st.markdown(f"**{SENSOR_INFO['E']['label']}**")
            st.caption(SENSOR_INFO['E']['desc'])

    st.markdown("")

    # Toggle untuk mode input
    input_mode = st.radio(
        "Pilih mode input:",
        ["Slider Input", "Table Editor", "Upload CSV"],
        horizontal=True
    )
    
    st.markdown("")

    input_data = {}
    
    if input_mode == "Slider Input":
        c1, c2, c3 = st.columns(3)

        with c1:
            st.markdown(f"**{SENSOR_INFO['P']['label']}**")
            for feat in p_cols:
                input_data[feat] = st.number_input(
                    feat, value=0.0, format='%.4f', key=feat
                )
        with c2:
            st.markdown(f"**{SENSOR_INFO['V']['label']}**")
            for feat in v_cols:
                input_data[feat] = st.number_input(
                    feat, value=0.0, format='%.4f', key=feat
                )
        with c3:
            st.markdown(f"**{SENSOR_INFO['E']['label']}**")
            for feat in e_cols:
                input_data[feat] = st.number_input(
                    feat, value=0.0, format='%.4f', key=feat
                )
    
    elif input_mode == "Table Editor":
        st.info("Edit nilai sensor langsung di tabel di bawah ini")
        default_values = {feat: 0.0 for feat in feature_names}
        df_input = pd.DataFrame([default_values])
        edited_df = st.data_editor(
            df_input,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                feat: st.column_config.NumberColumn(
                    feat, format="%.4f", min_value=-10.0, max_value=10.0,
                ) for feat in feature_names
            }
        )
        input_data = edited_df.iloc[0].to_dict()

    else:  # Upload CSV
        st.info("Upload file CSV. Pastikan kolom header sama dengan nama fitur model.")
        uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"], key="csv_upload")
        if uploaded_file is not None:
            try:
                df_up = pd.read_csv(uploaded_file)
                missing = [c for c in feature_names if c not in df_up.columns]
                if missing:
                    st.error(f"Kolom tidak lengkap. Hilang: {missing}")
                    input_data = {feat: 0.0 for feat in feature_names}
                else:
                    st.success(f"{len(df_up)} baris ditemukan.")
                    row_sel = st.number_input(
                        "Pilih baris ke-", min_value=0,
                        max_value=len(df_up) - 1, value=0, step=1
                    )
                    input_data = df_up[feature_names].iloc[int(row_sel)].to_dict()
                    st.dataframe(df_up[feature_names].iloc[[int(row_sel)]], use_container_width=True)
            except Exception as _e:
                st.error(f"Gagal membaca file: {_e}")
                input_data = {feat: 0.0 for feat in feature_names}
        else:
            st.caption("Belum ada file. Nilai default 0.0 akan digunakan.")
            input_data = {feat: 0.0 for feat in feature_names}

    st.markdown("---")

    if st.button("Prediksi", type="primary", use_container_width=True):
        with st.spinner("Memproses data sensor..."):
            X_input = pd.DataFrame([input_data])
            proba   = pipeline.predict_proba(X_input)[0, 1]
            pred    = int(proba >= threshold)

        st.toast("Prediksi selesai!", )

        with st.container(border=True):
            if pred == 0:
                st.markdown("""
                <div class="result-drowsy">
                    <h2>DROWSY</h2>
                    <p>Pengemudi terdeteksi mengantuk. Segera berhenti dan istirahat.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="result-alert">
                    <h2>ALERT</h2>
                    <p>Pengemudi dalam kondisi waspada dan aman untuk berkendara.</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("")
            m1, m2, m3 = st.columns(3)
            m1.metric("P(Alert)", f"{proba:.4f}")
            m2.metric("Threshold", f"{threshold:.2f}")
            m3.metric("Prediksi", "Alert" if pred == 1 else "Drowsy")
            _gc2 = "#e53e3e" if pred == 0 else "#38a169"
            _gfig2 = go.Figure(go.Indicator(
                mode="gauge+number",
                value=round(proba * 100, 1),
                number={'suffix': '%', 'font': {'size': 26}},
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Confidence P(Alert)", 'font': {'size': 13}},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': _gc2},
                    'steps': [
                        {'range': [0, threshold * 100], 'color': '#fff5f5'},
                        {'range': [threshold * 100, 100], 'color': '#f0fff4'},
                    ],
                    'threshold': {
                        'line': {'color': '#2b6cb0', 'width': 3},
                        'thickness': 0.75,
                        'value': threshold * 100
                    }
                }
            ))
            _gfig2.update_layout(
                height=220, margin=dict(l=10, r=10, t=40, b=10),
                paper_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(_gfig2, use_container_width=True, config={'displayModeBar': False})

# ════════════════════════════════════════════════════════════
# MODE 3: INTERPRETASI MODEL
# ════════════════════════════════════════════════════════════
elif mode == "Interpretasi Model":
    st.markdown("#### Fitur Paling Berpengaruh dalam Deteksi Kantuk")
    st.markdown(
        "Visualisasi di bawah menunjukkan seberapa besar kontribusi "
        "setiap sensor terhadap keputusan model XGBoost. Semakin tinggi "
        "nilainya, semakin penting sensor tersebut dalam membedakan "
        "kondisi Alert vs Drowsy."
    )
    st.markdown("")
    
    # Toggle untuk memilih jenis chart
    chart_type = st.radio(
        "Pilih jenis visualisasi:",
        ["Plotly (Interaktif)", "Matplotlib (Statis)"],
        horizontal=True
    )

    try:
        best_model = pipeline.named_steps['classifier']

        if hasattr(best_model, 'calibrated_classifiers_'):
            base = best_model.calibrated_classifiers_[0].estimator
        elif hasattr(best_model, 'estimator'):
            base = best_model.estimator
        else:
            base = best_model

        if hasattr(base, 'feature_importances_'):
            importances = base.feature_importances_
            xlabel = 'Importance Score'
        elif hasattr(base, 'coef_'):
            importances = np.abs(base.coef_[0])
            xlabel = '|Koefisien|'
        else:
            st.warning("Feature importance tidak tersedia untuk model ini.")
            st.stop()

        model_name = type(base).__name__
        fi_df = pd.DataFrame({
            'Sensor':     feature_names,
            'Importance': importances
        }).sort_values('Importance', ascending=True)

        def get_color(sensor):
            if sensor.startswith('P'): return '#4299e1'
            if sensor.startswith('V'): return '#48bb78'
            if sensor.startswith('E'): return '#ed8936'
            return '#a0aec0'

        colors = [get_color(s) for s in fi_df['Sensor']]

        if chart_type == "Plotly (Interaktif)":
            # Plotly interactive chart
            fig = go.Figure()
            
            # Tambahkan bar untuk setiap kategori
            for category, color in [('P', '#4299e1'), ('V', '#48bb78'), ('E', '#ed8936')]:
                mask = fi_df['Sensor'].str.startswith(category)
                category_name = {
                    'P': 'Physiological',
                    'V': 'Vehicle',
                    'E': 'Environmental'
                }[category]
                
                fig.add_trace(go.Bar(
                    y=fi_df[mask]['Sensor'],
                    x=fi_df[mask]['Importance'],
                    name=category_name,
                    orientation='h',
                    marker_color=color,
                    hovertemplate='<b>%{y}</b><br>Importance: %{x:.4f}<extra></extra>'
                ))
            
            fig.update_layout(
                title=f'Feature Importance — {model_name}',
                xaxis_title=xlabel,
                yaxis_title='',
                height=600,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                hovermode='closest',
                plot_bgcolor='white',
                paper_bgcolor='white'
            )
            
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray')
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            # Matplotlib static chart (original)
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.barh(fi_df['Sensor'], fi_df['Importance'], color=colors)
            ax.set_xlabel(xlabel, fontsize=11)
            ax.set_title(
                f'Feature Importance — {model_name}',
                fontsize=13, fontweight='bold'
            )
            ax.grid(axis='x', alpha=0.3)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

            legend = [
                mpatches.Patch(color='#4299e1', label='Physiological (P)'),
                mpatches.Patch(color='#48bb78', label='Vehicle (V)'),
                mpatches.Patch(color='#ed8936', label='Environmental (E)'),
            ]
            ax.legend(handles=legend, loc='lower right', fontsize=10)
            plt.tight_layout()
            st.pyplot(fig)

        st.markdown("---")
        st.markdown("#### Ringkasan Temuan")

        top3 = fi_df.nlargest(3, 'Importance')
        st.markdown("**3 sensor paling berpengaruh:**")
        for _, row in top3.iterrows():
            kategori = (
                "Physiological" if row['Sensor'].startswith('P') else
                "Vehicle"       if row['Sensor'].startswith('V') else
                "Environmental"
            )
            st.markdown(
                f"- **{row['Sensor']}** ({kategori}) — "
                f"Importance Score: `{row['Importance']:.4f}`"
            )

        st.markdown("")
        st.info(
            "Dominannya sensor kategori Vehicle (V) dan Environmental (E) "
            "mengonfirmasi bahwa perilaku mengemudi dan kondisi lingkungan "
            "lebih terdeteksi oleh model dibanding sinyal biologis (P) yang "
            "korelasinya lebih lemah ke label IsAlert. "
            "Ini memvalidasi pendekatan Sensor Fusion — tidak cukup hanya "
            "mengandalkan satu jenis sensor."
        )

    except Exception as e:
        st.error(f"Error: {e}")

# ════════════════════════════════════════════════════════════
# MODE 4: TENTANG PROYEK
# ════════════════════════════════════════════════════════════
elif mode == "Tentang Proyek":
    st.markdown("#### Latar Belakang")
    st.markdown(
        "Kecelakaan lalu lintas akibat microsleep dan kelelahan pengemudi "
        "masih menjadi penyumbang angka fatalitas tertinggi di jalan raya. "
        "Sistem berbasis Computer Vision yang ada saat ini memiliki kelemahan "
        "pada kondisi minim cahaya, penggunaan kacamata hitam, atau posisi "
        "wajah yang tidak menghadap kamera. Proyek ini mengusulkan pendekatan "
        "**Sensor Fusion** yang menggabungkan data biometrik fisiologis, "
        "telematika kendaraan, dan kondisi lingkungan untuk deteksi kantuk "
        "yang lebih robust dan tidak bergantung pada data visual."
    )

    st.markdown("---")
    st.markdown("#### Dataset")

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Total Observasi", "604.329")
    d2.metric("Jumlah Fitur", "24")
    d3.metric("Kelas Alert", "58%")   # FIX #4: sesuai output notebook (bukan 61%)
    d4.metric("Kelas Drowsy", "42%")  # FIX #4: sesuai output notebook (bukan 39%)

    st.caption(
        "Sumber: Ford Stay Alert! Driver Drowsiness Detection Dataset. "
        "Nama fitur dianonimkan oleh Ford untuk menjaga kerahasiaan teknologi sensor."
    )

    st.markdown("---")
    st.markdown("#### Arsitektur Pipeline")
    st.markdown(
        "Pipeline preprocessing dirancang untuk mencegah data leakage "
        "di setiap tahap:"
    )
    st.markdown("""
    <div style='margin: 1rem 0;'>
        <span class="pipeline-step">GroupShuffleSplit (by TrialID)</span> →
        <span class="pipeline-step">WinsorizerTransformer</span> →
        <span class="pipeline-step">StandardScaler</span> →
        <span class="pipeline-step">SMOTE</span> →
        <span class="pipeline-step">CalibratedClassifierCV (XGBoost)</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption(
        "Semua langkah preprocessing dieksekusi per-fold di dalam ImbPipeline "
        "sehingga tidak ada statistik dari fold validasi yang bocor ke fold training."
    )

    st.markdown("---")
    st.markdown("#### Perbandingan Performa Model")
    st.caption(
        "Evaluasi dilakukan pada test set yang sepenuhnya terpisah dari proses training. "
        "Metrik prioritas: Recall Drowsy dan PR-AUC."
    )

    metrics_df = pd.DataFrame(MODEL_METRICS).T.reset_index()
    metrics_df.columns = [
        'Model', 'Accuracy', 'ROC-AUC',
        'PR-AUC Drowsy', 'Recall Drowsy', 'F1 Drowsy', 'CV Recall'
    ]

    def highlight_best(s):
        if s.name in ['Accuracy', 'ROC-AUC', 'PR-AUC Drowsy',
                       'Recall Drowsy', 'F1 Drowsy']:
            is_best = s == s.max()
            return ['background-color: #c6f6d5; font-weight: bold'
                    if v else '' for v in is_best]
        return ['' for _ in s]

    styled = (
        metrics_df.style
        .apply(highlight_best, subset=[
            'Accuracy', 'ROC-AUC', 'PR-AUC Drowsy',
            'Recall Drowsy', 'F1 Drowsy'
        ])
        .format({
            'Accuracy':      '{:.4f}',
            'ROC-AUC':       '{:.4f}',
            'PR-AUC Drowsy': '{:.4f}',
            'Recall Drowsy': '{:.4f}',
            'F1 Drowsy':     '{:.4f}',
        })
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)

    st.markdown("")
    st.info(
        "**XGBoost dipilih sebagai model final** karena memiliki ROC-AUC (0.9307) "
        "dan PR-AUC Drowsy (0.9197) tertinggi, menunjukkan kemampuan diskriminasi "
        "terbaik terhadap kelas Drowsy. Threshold dioptimalkan ke **0.73** melalui "
        "Out-of-Fold prediction pada train set. Recall Drowsy final pada test set "
        "mencapai **0.8207** dengan **8.377 False Negative**.\n\n"
        "**Catatan:** Target Recall Drowsy >= 0.90 belum tercapai di test set (0.8207). "
        "Ini adalah konsekuensi gap OOF->Test — threshold yang dioptimalkan dari train set "
        "tidak mentransfer sempurna ke distribusi sesi test set yang berbeda."
    )

    # ── Bar Chart Perbandingan Model ─────────────────────────
    st.markdown("---")
    st.markdown("#### Visualisasi Perbandingan Model")
    _metric_cols = ['Recall Drowsy', 'PR-AUC Drowsy', 'ROC-AUC', 'Accuracy', 'F1 Drowsy']
    _colors_model = {
        'Logistic Regression': '#a0aec0',
        'Random Forest':       '#48bb78',
        'XGBoost':             '#4299e1'
    }
    _bar_fig = go.Figure()
    for _model, _mdata in MODEL_METRICS.items():
        _bar_fig.add_trace(go.Bar(
            name=_model,
            x=_metric_cols,
            y=[_mdata[m] for m in _metric_cols],
            marker_color=_colors_model[_model],
            text=[f"{_mdata[m]:.4f}" for m in _metric_cols],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>%{y:.4f}<extra>' + _model + '</extra>'
        ))
    _bar_fig.update_layout(
        barmode='group',
        height=420,
        yaxis=dict(range=[0, 1.05], title='Score'),
        xaxis_title='Metrik',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        plot_bgcolor='white',
        paper_bgcolor='white',
        margin=dict(t=60, b=40)
    )
    _bar_fig.update_xaxes(showgrid=False)
    _bar_fig.update_yaxes(showgrid=True, gridcolor='#e2e8f0')
    st.plotly_chart(_bar_fig, use_container_width=True)

    # ── Confusion Matrix XGBoost ─────────────────────────────
    st.markdown("---")
    st.markdown("#### Confusion Matrix — XGBoost (Estimasi Test Set)")
    st.caption("Nilai estimasi berdasarkan metrik test set. FN = 8.377 sesuai hasil notebook.")
    _TP, _FN = 38334, 8377
    _TN, _FP = 63904, 6198
    _cm_fig = go.Figure(data=go.Heatmap(
        z=[[_TN, _FP], [_FN, _TP]],
        x=['Prediksi: Alert', 'Prediksi: Drowsy'],
        y=['Aktual: Alert', 'Aktual: Drowsy'],
        text=[[f'TN\n{_TN:,}', f'FP\n{_FP:,}'], [f'FN\n{_FN:,}', f'TP\n{_TP:,}']],
        texttemplate='%{text}',
        textfont={'size': 14},
        colorscale=[
            [0.0, '#fff5f5'], [0.3, '#fed7d7'],
            [0.7, '#c6f6d5'], [1.0, '#276749']
        ],
        showscale=False,
    ))
    _cm_fig.update_layout(
        height=320,
        xaxis={'side': 'top'},
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor='white'
    )
    st.plotly_chart(_cm_fig, use_container_width=True)
    _cm_cols = st.columns(4)
    _cm_cols[0].metric("True Negative",  f"{_TN:,}", help="Alert diprediksi Alert")
    _cm_cols[1].metric("False Positive", f"{_FP:,}", help="Alert diprediksi Drowsy")
    _cm_cols[2].metric("False Negative", f"{_FN:,}", help="Drowsy diprediksi Alert (berbahaya!)")
    _cm_cols[3].metric("True Positive",  f"{_TP:,}", help="Drowsy diprediksi Drowsy")

    st.markdown("---")
    st.markdown("#### Tim Pengembang")
    st.markdown(
        "**Kelompok 18** — Mata Kuliah Sains Data  \n"
        "Fakultas Informatika, Universitas Siliwangi"
    )

# ── Footer ────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Drowsiness Detection System &nbsp;|&nbsp;
    Model: XGBoost + CalibratedClassifierCV &nbsp;|&nbsp;
    Kelompok 18 &mdash; Sains Data Universitas Siliwangi &nbsp;|&nbsp;
    <a href="https://github.com/enr-gwen/drowsiness-detection" target="_blank" style="color:#a0aec0;">GitHub</a>
</div>
""", unsafe_allow_html=True)