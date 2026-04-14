import streamlit as st
import pandas as pd
import numpy as np

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Dashboard Prediksi DM Puskesmas", layout="wide")

# 2. HEADER
st.title("🏥 Surabaya Health Predict - Layanan Preventif Diabetes")
st.markdown("Integrasi Data: **Tabel 76 - Pelayanan Kesehatan Penderita Diabetes Melitus (DM) Kota Surabaya 2023**")

# 3. DATA PUSKESMAS & PASIEN DM (Mengacu Struktur Tabel 76)
@st.cache_data
def load_puskesmas_data():
    # Simulasi data agregat pelayanan DM per Puskesmas
    puskesmas_list = [
        {"Kecamatan": "Rungkut", "Puskesmas": "Puskesmas Rungkut", "lat": -7.3235, "lon": 112.7758, "Wilayah": "Surabaya Timur", "Sasaran_DM": 1250, "Mendapat_Pelayanan": 1100},
        {"Kecamatan": "Mulyorejo", "Puskesmas": "Puskesmas Mulyorejo", "lat": -7.2628, "lon": 112.7876, "Wilayah": "Surabaya Timur", "Sasaran_DM": 980, "Mendapat_Pelayanan": 850},
        {"Kecamatan": "Gubeng", "Puskesmas": "Puskesmas Gubeng Masjid", "lat": -7.2662, "lon": 112.7523, "Wilayah": "Surabaya Pusat", "Sasaran_DM": 1050, "Mendapat_Pelayanan": 920},
        {"Kecamatan": "Tegalsari", "Puskesmas": "Puskesmas Kedungdoro", "lat": -7.2581, "lon": 112.7356, "Wilayah": "Surabaya Pusat", "Sasaran_DM": 890, "Mendapat_Pelayanan": 780},
        {"Kecamatan": "Wiyung", "Puskesmas": "Puskesmas Wiyung", "lat": -7.3045, "lon": 112.6934, "Wilayah": "Surabaya Barat", "Sasaran_DM": 1120, "Mendapat_Pelayanan": 1010},
        {"Kecamatan": "Benowo", "Puskesmas": "Puskesmas Benowo", "lat": -7.2514, "lon": 112.6372, "Wilayah": "Surabaya Barat", "Sasaran_DM": 760, "Mendapat_Pelayanan": 650},
        {"Kecamatan": "Pabean Cantian", "Puskesmas": "Puskesmas Perak Timur", "lat": -7.2144, "lon": 112.7351, "Wilayah": "Surabaya Utara", "Sasaran_DM": 940, "Mendapat_Pelayanan": 810},
        {"Kecamatan": "Kenjeran", "Puskesmas": "Puskesmas Tanah Kali Kedinding", "lat": -7.2117, "lon": 112.7664, "Wilayah": "Surabaya Utara", "Sasaran_DM": 1340, "Mendapat_Pelayanan": 1150},
        {"Kecamatan": "Gayungan", "Puskesmas": "Puskesmas Gayungan", "lat": -7.3315, "lon": 112.7276, "Wilayah": "Surabaya Selatan", "Sasaran_DM": 820, "Mendapat_Pelayanan": 750},
        {"Kecamatan": "Wonokromo", "Puskesmas": "Puskesmas Jagir", "lat": -7.3005, "lon": 112.7394, "Wilayah": "Surabaya Selatan", "Sasaran_DM": 1450, "Mendapat_Pelayanan": 1300},
    ]
    
    # Hitung persentase dan bangkitkan titik pasien dummy di sekitar Puskesmas
    data_points = []
    for p in puskesmas_list:
        p["Persentase_Pelayanan (%)"] = round((p["Mendapat_Pelayanan"] / p["Sasaran_DM"]) * 100, 2)
        
        # Simulasi titik pasien individu untuk Geospatial Mapping
        for _ in range(np.random.randint(15, 30)):
            data_points.append({
                "Puskesmas": p["Puskesmas"],
                "lat": p["lat"] + np.random.uniform(-0.008, 0.008),
                "lon": p["lon"] + np.random.uniform(-0.008, 0.008),
                "Risiko_Komplikasi": np.random.choice(['Tinggi', 'Sedang', 'Terkontrol'], p=[0.25, 0.35, 0.40]),
                "Wilayah": p["Wilayah"]
            })
            
    return pd.DataFrame(puskesmas_list), pd.DataFrame(data_points)

df_pusk, df_pasien = load_puskesmas_data()

# 4. SIDEBAR FILTER
st.sidebar.header("Filter Wilayah")
wilayah_selected = st.sidebar.multiselect("Pilih Wilayah Surabaya", 
                                         options=df_pusk['Wilayah'].unique(), 
                                         default=df_pusk['Wilayah'].unique())

df_pusk_filtered = df_pusk[df_pusk['Wilayah'].isin(wilayah_selected)]
df_pasien_filtered = df_pasien[df_pasien['Wilayah'].isin(wilayah_selected)]

# 5. METRIKS UTAMA (Agregasi Data Tabel 76)
col1, col2, col3 = st.columns(3)
total_sasaran = df_pusk_filtered['Sasaran_DM'].sum()
total_pelayanan = df_pusk_filtered['Mendapat_Pelayanan'].sum()
persentase_total = round((total_pelayanan / total_sasaran) * 100, 2) if total_sasaran > 0 else 0

col1.metric("Total Sasaran Penderita DM", f"{total_sasaran:,}")
col2.metric("Mendapat Pelayanan Sesuai Standar", f"{total_pelayanan:,}")
col3.metric("Rata-rata Cakupan Pelayanan", f"{persentase_total}%")

st.divider()

# 6. VISUALISASI PETA GEOSPATIAL
st.subheader(f"📍 Pemetaan Pasien DM Risiko Komplikasi Tinggi")
st.markdown("Titik merah menunjukkan pasien penderita Diabetes Melitus di wilayah terpilih yang diprediksi oleh sistem memiliki **Risiko Komplikasi Tinggi** dan memerlukan intervensi segera (berdasarkan integrasi data biometrik IoT).")
st.map(df_pasien_filtered[df_pasien_filtered['Risiko_Komplikasi'] == 'Tinggi'])

st.divider()

# 7. TABEL DATA (Simulasi Format Tabel 76)
st.subheader("📋 Rekapitulasi Pelayanan Penderita DM per Fasilitas")
st.dataframe(df_pusk_filtered[['Kecamatan', 'Puskesmas', 'Sasaran_DM', 'Mendapat_Pelayanan', 'Persentase_Pelayanan (%)']].reset_index(drop=True), use_container_width=True)
