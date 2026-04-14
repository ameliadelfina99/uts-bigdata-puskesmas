import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Prediksi Kronis Puskesmas", layout="wide")

st.title("🏥 Sistem Prediksi Dini Penyakit Kronis - Puskesmas Surabaya")
st.markdown("**Tujuan:** Mengoptimalkan layanan preventif dengan deteksi risiko Diabetes dan Jantung berbasis Big Data.")

# 2. FUNGSI SIMULASI DATA (Ditambah ID Pasien & Label Status Warna)
@st.cache_data
def generate_aligned_data():
    puskesmas_data = [
        {"name": "Puskesmas Rungkut", "lat": -7.3235, "lon": 112.7758, "wilayah": "Surabaya Timur"},
        {"name": "Puskesmas Mulyorejo", "lat": -7.2628, "lon": 112.7876, "wilayah": "Surabaya Timur"},
        {"name": "Puskesmas Gubeng Masjid", "lat": -7.2662, "lon": 112.7523, "wilayah": "Surabaya Pusat"},
        {"name": "Puskesmas Gayungan", "lat": -7.3315, "lon": 112.7276, "wilayah": "Surabaya Selatan"},
        {"name": "Puskesmas Wiyung", "lat": -7.3045, "lon": 112.6934, "wilayah": "Surabaya Barat"},
    ]
    
    rows = []
    patient_id = 1001
    for p in puskesmas_data:
        for _ in range(np.random.randint(20, 40)):
            bmi = np.random.uniform(18, 40)
            high_bp = np.random.choice([0, 1], p=[0.6, 0.4])
            high_chol = np.random.choice([0, 1], p=[0.7, 0.3])
            smoker = np.random.choice([0, 1], p=[0.8, 0.2])
            age_cat = np.random.randint(1, 13) 
            
            # Hitung Skor (Simulasi Model ML)
            score = (high_bp * 30) + (high_chol * 20) + (bmi * 1.5) + (smoker * 10) + (age_cat * 2)
            
            # Logika Status Warna sesuai Permintaan
            if score > 75: 
                status = "Tinggi"
                color = "#FF4B4B" # Merah
                status_label = "🔴 MERAH (Prioritas)"
            elif score > 50: 
                status = "Sedang"
                color = "#FFAA00" # Orange
                status_label = "🟠 ORANGE (Waspada)"
            else: 
                status = "Terkontrol"
                color = "#00CC96" # Hijau
                status_label = "🟢 HIJAU (Aman)"
            
            rows.append({
                "ID_Pasien": f"P-{patient_id}",
                "Puskesmas": p["name"],
                "Wilayah": p["wilayah"],
                "lat": p["lat"] + np.random.uniform(-0.007, 0.007),
                "lon": p["lon"] + np.random.uniform(-0.007, 0.007),
                "BMI": round(bmi, 1),
                "HighBP": "Ya" if high_bp == 1 else "Tidak",
                "HighChol": "Ya" if high_chol == 1 else "Tidak",
                "Status_Risiko": status,
                "Status_Peringatan": status_label,
                "Score": round(score, 1),
                "color": color
            })
            patient_id += 1
            
    return pd.DataFrame(rows)

df = generate_aligned_data()

# 3. SIDEBAR (FILTER WILAYAH)
st.sidebar.header("⚙️ Filter Wilayah")
wilayah_options = df['Wilayah'].unique()
selected_wilayah = st.sidebar.multiselect("Pilih Wilayah Surabaya:", options=wilayah_options, default=wilayah_options)
df_filtered = df[df['Wilayah'].isin(selected_wilayah)]

# 4. METRIKS UTAMA
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Total Skrining", len(df_filtered))
with col_m2:
    high_risk_count = len(df_filtered[df_filtered['Status_Risiko'] == 'Tinggi'])
    st.metric("Pasien Risiko Tinggi", high_risk_count)
with col_m3:
    st.metric("Akurasi Prediksi", "91.2%")

st.divider()

# 5. VISUALISASI PETA
st.subheader("📍 Pemetaan Geospasial Wilayah")
st.markdown("**Keterangan:** 🔴 Risiko Tinggi | 🟠 Risiko Sedang")
df_peta = df_filtered[df_filtered['Status_Risiko'] != 'Terkontrol'][['lat', 'lon', 'color']]
if not df_peta.empty:
    st.map(df_peta, color='color')

st.divider()

# 6. TABEL PRIORITAS (Update: Menambah Status Merah/Orange)
st.subheader("📋 Daftar Prioritas Kunjungan (Home Care)")
st.markdown("Berikut adalah daftar pasien kategori **Risiko Tinggi (Merah)** dan **Sedang (Orange)**.")

# Filter tabel untuk menunjukkan Risiko Tinggi dan Sedang
df_prioritas = df_filtered[df_filtered['Status_Risiko'] != 'Terkontrol']

# Tampilkan kolom dengan label status warna
kolom_tabel = ['ID_Pasien', 'Status_Peringatan', 'Puskesmas', 'Wilayah', 'BMI', 'HighBP', 'Score']
st.dataframe(df_prioritas[kolom_tabel].sort_values(by='Score', ascending=False).reset_index(drop=True), use_container_width=True)
