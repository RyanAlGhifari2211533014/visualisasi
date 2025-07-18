import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

# Import data loading and saving functions from data_loader
from data_loader import load_penduduk_data_from_excel, save_data_penduduk_tahun_to_session

def run():
    """
    Renders the 'Jumlah Penduduk (2020-2025)' page, including chart, table, and data input form.
    """
    st.title('📊 Jumlah Penduduk (2020-2025)')

    # Muat data dari file Excel (data awal)
    # Coba ambil dari session_state terlebih dahulu jika sudah dimodifikasi oleh form
    # Jika tidak ada di session_state, baru muat dari Excel
    if f'cached_{load_penduduk_data_from_excel.__name__}' in st.session_state:
        df_penduduk_tahun = st.session_state[f'cached_{load_penduduk_data_from_excel.__name__}']
    else:
        df_penduduk_tahun = load_penduduk_data_from_excel()
        # Simpan ke session_state agar konsisten jika ada modifikasi
        st.session_state[f'cached_{load_penduduk_data_from_excel.__name__}'] = df_penduduk_tahun


    # Tampilkan Visualisasi Data Penduduk
    st.subheader("Grafik Tren Jumlah Penduduk Tahunan")
    # Pastikan DataFrame tidak kosong dan kolom yang dibutuhkan ada
    if not df_penduduk_tahun.empty and 'Tahun' in df_penduduk_tahun.columns and 'Jumlah Total (orang)' in df_penduduk_tahun.columns:
        # Membuat figure matplotlib
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.set(style="whitegrid")

        # Membuat line plot menggunakan seaborn
        sns.lineplot(
            x='Tahun',
            y='Jumlah Total (orang)',
            data=df_penduduk_tahun,
            marker='o', # Menambahkan penanda titik untuk setiap tahun
            linewidth=2.5,
            ax=ax # Menentukan axis untuk plot
        )

        # Menambahkan judul dan label yang jelas
        ax.set_title('Tren Jumlah Penduduk Total (2020 - 2025)', fontsize=16, pad=20)
        ax.set_xlabel('Tahun', fontsize=12)
        ax.set_ylabel('Jumlah Penduduk (Orang)', fontsize=12)

        # Mengatur agar sumbu X hanya menampilkan angka bulat (tahun)
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        plt.xticks(rotation=45) # Memutar label tahun agar tidak tumpang tindih

        # Menambahkan label angka di setiap titik data
        for index, row in df_penduduk_tahun.iterrows():
            ax.text(row['Tahun'], row['Jumlah Total (orang)'] + (df_penduduk_tahun['Jumlah Total (orang)'].max() * 0.01), # Posisi teks sedikit di atas titik
                    f"{int(row['Jumlah Total (orang)'])}", # Format sebagai integer
                    ha='center', va='bottom', fontsize=10) # va='bottom' untuk posisi vertikal

        plt.tight_layout() # Merapikan layout
        st.pyplot(fig) # Menampilkan plot di Streamlit

        st.subheader("Tabel Data Penduduk")
        st.dataframe(df_penduduk_tahun, use_container_width=True)
    else:
        st.info("Belum ada data jumlah penduduk yang valid untuk divisualisasikan. Pastikan file Excel ada dan memiliki kolom 'Tahun' serta 'Jumlah Total (orang)' dengan data yang benar.")

