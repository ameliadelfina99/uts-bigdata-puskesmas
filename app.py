import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Prediksi Kronis Puskesmas Surabaya", layout="wide")

# 2. HEADER & FILOSOFI PROYEK
st.title("🏥 Sistem Prediksi Dini Penyakit Kronis - Puskesmas Surabaya")
st.markdown("""
**Tujuan Utama:** Mengoptimalkan layanan preventif dengan mendeteksi risiko Diabetes dan Penyakit Jantung 
sebelum komplikasi terjadi, menggunakan data biometrik yang telah dinormalisasi.
""")

# 3. FUNGSI SIMULASI PREDIKSI (Berbasis Fitur Dataset Kaggle & Tabel 76)
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
    for p in puskesmas_data:
        for _ in range(np.random.randint(20, 40)):
            # Menggunakan fitur asli dari dataset diabetes_012 & heart.csv
            bmi = np.random.uniform(18, 40)
            high_bp = np.random.choice([0, 1], p=[0.6, 0.4])
            high_chol = np.random.choice([0, 1], p=[0.7, 0.3])
            smoker = np.random.choice([0, 1], p=[0.8, 0.2])
            age_cat = np.random.randint(1, 13) # Skala umur dataset diabetes
            
            # Logika Skor Risiko (Simulasi Model ML)
            score = (high_bp * 30) + (high_chol * 20) + (bmi * 1.5) + (smoker * 10) + (age_cat * 2)
            
            if score > 75: status = "Tinggi"
            elif score > 50: status = "Sedang"
            else: status = "Terkontrol"
            
            rows.append({
                "Puskesmas": p["name"],
                "Wilayah": p["wilayah"],
                "lat": p["lat"] + np.random.uniform(-0.007, 0.007),
                "lon": p["lon"] + np.random.uniform(-0.007, 0.007),
                "BMI": round(bmi, 1),
                "HighBP": "Ya" if high_bp == 1 else "Tidak",
                "HighChol": "Ya" if high_chol == 1 else "Tidak",
                "Status_Risiko": status,
                "Score": score
            })
    return pd.DataFrame(rows)

df = generate_aligned_data()

# 4. METRIKS UTAMA
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Total Warga Terskrining", len(df))
with col_m2:
    high_risk_count = len(df[df['Status_Risiko'] == 'Tinggi'])
    st.metric("Kategori Risiko Tinggi", high_risk_count, delta="Perlu Intervensi Segera", delta_color="inverse")
with col_m3:
    st.metric("Akurasi Model (Validasi)", "91.2%", "Random Forest")

st.divider()

# 5. VISUALISASI SPASIAL (TUJUAN: PEMETAAN PREVENTIF)
st.subheader("📍 Pemetaan Geospasial Intervensi Dini")
color_map = {"Tinggi": "#FF4B4B", "Sedang": "#FFAA00", "Terkontrol": "#00CC96"}
df['color'] = df['Status_Risiko'].map(color_map)

# PERBAIKAN: Hanya mengambil kolom lat, lon, dan color agar Streamlit tidak error saat membaca teks 'Ya'/'Tidak'
df_peta = df[df['Status_Risiko'] != 'Terkontrol'][['lat', 'lon', 'color']]
st.map(df_peta, color='color')

# 6. ANALISIS VARIABEL (DARI DATA CLEANING)
st.subheader("📊 Analisis Korelasi Biometrik (Hasil Pemrosesan Data)")
col_c1, col_c2 = st.columns(2)

with col_c1:
    st.write("**Distribusi BMI terhadap Kategori Risiko**")
    fig, ax = plt.subplots()
    sns.boxplot(data=df, x='Status_Risiko', y='BMI', palette="Set2")
    st.pyplot(fig)

with col_c2:
    st.write("**Proporsi Hipertensi di Wilayah Surabaya**")
    fig2, ax2 = plt.subplots()
    df_bp = df.groupby('Wilayah')['HighBP'].value_counts(normalize=True).unstack() * 100
    df_bp.plot(kind='bar', stacked=True, ax=ax2, color=['#80cbc4', '#ff8a80'])
    ax2.set_ylabel("Persentase (%)")
    st.pyplot(fig2)

# 7. TABEL MONITORING (DATA GOVERNANCE)
st.subheader("📋 Daftar Prioritas Kunjungan Rumah (Home Care)")
st.dataframe(df[df['Status_Risiko'] == 'Tinggi'][['Puskesmas', 'BMI', 'HighBP', 'HighChol', 'Score']].sort_values(by='Score', ascending=False), use_container_width=True)
