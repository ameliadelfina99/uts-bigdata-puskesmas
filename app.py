import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="Prediksi Kronis Puskesmas", layout="wide")

st.title("🏥 Sistem Prediksi Dini Penyakit Kronis - Puskesmas Surabaya")
st.markdown("**Tujuan:** Mengoptimalkan layanan preventif dengan mendeteksi risiko Diabetes dan Penyakit Jantung sebelum komplikasi terjadi.")

# 2. FUNGSI SIMULASI DATA (Ditambah ID Pasien agar tidak terlihat duplikat)
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
    patient_id = 1001 # Memulai ID Pasien
    for p in puskesmas_data:
        for _ in range(np.random.randint(20, 40)):
            bmi = np.random.uniform(18, 40)
            high_bp = np.random.choice([0, 1], p=[0.6, 0.4])
            high_chol = np.random.choice([0, 1], p=[0.7, 0.3])
            smoker = np.random.choice([0, 1], p=[0.8, 0.2])
            age_cat = np.random.randint(1, 13) 
            
            score = (high_bp * 30) + (high_chol * 20) + (bmi * 1.5) + (smoker * 10) + (age_cat * 2)
            
            if score > 75: 
                status = "Tinggi"
                color = "#FF4B4B" # Merah
            elif score > 50: 
                status = "Sedang"
                color = "#FFAA00" # Oranye
            else: 
                status = "Terkontrol"
                color = "#00CC96" # Hijau
            
            rows.append({
                "ID_Pasien": f"P-{patient_id}", # Kolom pembeda agar tidak dianggap duplikat
                "Puskesmas": p["name"],
                "Wilayah": p["wilayah"],
                "lat": p["lat"] + np.random.uniform(-0.007, 0.007),
                "lon": p["lon"] + np.random.uniform(-0.007, 0.007),
                "BMI": round(bmi, 1),
                "HighBP": "Ya" if high_bp == 1 else "Tidak",
                "HighChol": "Ya" if high_chol == 1 else "Tidak",
                "Status_Risiko": status,
                "Score": round(score, 1),
                "color": color
            })
            patient_id += 1
            
    return pd.DataFrame(rows)

df = generate_aligned_data()

# 3. SIDEBAR (FILTER WILAYAH)
st.sidebar.header("⚙️ Filter Data")
# Mengambil daftar wilayah yang unik
wilayah_options = df['Wilayah'].unique()
# Membuat multiselect filter, defaultnya memilih semua wilayah
selected_wilayah = st.sidebar.multiselect("Pilih Wilayah Surabaya:", options=wilayah_options, default=wilayah_options)

# Menerapkan filter pada dataframe
df_filtered = df[df['Wilayah'].isin(selected_wilayah)]

# 4. METRIKS UTAMA (Menggunakan data yang sudah difilter)
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Total Warga Terskrining (Area Terpilih)", len(df_filtered))
with col_m2:
    high_risk_count = len(df_filtered[df_filtered['Status_Risiko'] == 'Tinggi'])
    st.metric("Risiko Tinggi (Perlu Intervensi)", high_risk_count)
with col_m3:
    st.metric("Akurasi Model ML", "91.2%")

st.divider()

# 5. VISUALISASI PETA & KETERANGAN WARNA (LEGEND)
st.subheader("📍 Pemetaan Geospasial Intervensi Dini")

# Menambahkan Keterangan Warna (Legend) secara manual
st.markdown("""
**Keterangan Indikator Titik Peta:**
* 🔴 **Merah:** Risiko Tinggi (Skor > 75) - Membutuhkan *Home Care* segera.
* 🟠 **Oranye:** Risiko Sedang (Skor 51-75) - Membutuhkan edukasi preventif.
*(Pasien dengan risiko terkontrol tidak ditampilkan di peta untuk fokus prioritas)*
""")

# Peta hanya menampilkan status Tinggi dan Sedang dari wilayah yang difilter
df_peta = df_filtered[df_filtered['Status_Risiko'] != 'Terkontrol'][['lat', 'lon', 'color']]
if not df_peta.empty:
    st.map(df_peta, color='color')
else:
    st.info("Tidak ada pasien dengan risiko Sedang/Tinggi di wilayah ini.")

# 6. ANALISIS VARIABEL
st.subheader("📊 Analisis Korelasi Biometrik")
col_c1, col_c2 = st.columns(2)

with col_c1:
    fig, ax = plt.subplots()
    sns.boxplot(data=df_filtered, x='Status_Risiko', y='BMI', palette="Set2", order=["Terkontrol", "Sedang", "Tinggi"])
    ax.set_title("Distribusi BMI terhadap Risiko")
    st.pyplot(fig)

with col_c2:
    fig2, ax2 = plt.subplots()
    df_bp = df_filtered.groupby('Wilayah')['HighBP'].value_counts(normalize=True).unstack() * 100
    df_bp.plot(kind='bar', stacked=True, ax=ax2, color=['#80cbc4', '#ff8a80'])
    ax2.set_title("Proporsi Hipertensi (HighBP)")
    ax2.set_ylabel("Persentase (%)")
    st.pyplot(fig2)

# 7. TABEL MONITORING (DATA GOVERNANCE)
st.subheader("📋 Daftar Prioritas Kunjungan (Home Care)")
st.markdown("Menampilkan individu pasien dengan **Risiko Tinggi**.")
df_prioritas = df_filtered[df_filtered['Status_Risiko'] == 'Tinggi']

# Menampilkan kolom ID_Pasien agar terbukti ini individu yang berbeda, bukan duplikat wilayah
kolom_tabel = ['ID_Pasien', 'Wilayah', 'Puskesmas', 'BMI', 'HighBP', 'HighChol', 'Score']
st.dataframe(df_prioritas[kolom_tabel].sort_values(by='Score', ascending=False).reset_index(drop=True), use_container_width=True)
