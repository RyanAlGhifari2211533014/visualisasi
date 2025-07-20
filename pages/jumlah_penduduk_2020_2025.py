# pages/jumlah_penduduk_2020_2025.py
import streamlit as st
import altair as alt # Import Altair untuk membuat grafik
from data_loader import load_penduduk_data_from_gsheet, save_data_penduduk_tahun_to_session
import pandas as pd

def run():
    """
    Merender konten halaman Jumlah Penduduk (2020-2025),
    memuat data dari Google Sheet, menampilkan tabel, dan grafik.
    """
    # Pastikan TIDAK ADA BARIS st.set_page_config() DI SINI.
    # Contoh yang TIDAK boleh ada:
    # st.set_page_config(layout="wide", page_title="Halaman Penduduk")

    st.title("📊 Data Jumlah Penduduk (2020-2025)")
    st.markdown("Halaman ini menampilkan data jumlah penduduk dari tahun 2020 hingga 2025.")

    # --- Muat Data dari Google Sheet ---
    df_penduduk = load_penduduk_data_from_gsheet()

    if f'cached_{load_penduduk_data_from_gsheet.__name__}' not in st.session_state:
        st.session_state[f'cached_{load_penduduk_data_from_gsheet.__name__}'] = df_penduduk.copy()

    # --- Tampilkan Tabel Data ---
    if not df_penduduk.empty:
        st.subheader("Tabel Data Jumlah Penduduk")
        st.dataframe(df_penduduk)

        # --- Form Input Data (untuk pengeditan/penambahan data sementara) ---
        st.subheader("Tambah/Edit Data Jumlah Penduduk (Sementara)")
        st.info("Perubahan di sini hanya akan berlaku sementara di aplikasi ini dan tidak tersimpan di Google Sheet.")

        with st.form("form_add_edit_penduduk"):
            col1, col2 = st.columns(2)
            with col1:
                tahun_input = st.number_input("Tahun", min_value=2000, max_value=2050, value=2025, step=1)
            with col2:
                jumlah_input = st.number_input("Jumlah Total (orang)", min_value=0, value=10000, step=100)

            submitted = st.form_submit_button("Simpan Data (sementara)")
            if submitted:
                new_row = {'Tahun': int(tahun_input), 'Jumlah Total (orang)': int(jumlah_input)}
                save_data_penduduk_tahun_to_session(new_row)
                st.success(f"Data untuk tahun {tahun_input} berhasil diperbarui/ditambahkan secara sementara.")
                df_penduduk = st.session_state.get(f'cached_{load_penduduk_data_from_gsheet.__name__}', pd.DataFrame())
                st.dataframe(df_penduduk)


        # --- Visualisasi ---
        st.subheader("Grafik Jumlah Penduduk per Tahun")
        if not df_penduduk.empty:
            chart = alt.Chart(df_penduduk).mark_line(point=True).encode(
                x=alt.X('Tahun:O', axis=alt.Axis(title='Tahun', format='d')),
                y=alt.Y('Jumlah Total (orang):Q', title='Jumlah Penduduk'),
                tooltip=['Tahun', 'Jumlah Total (orang)']
            ).properties(
                title='Tren Jumlah Penduduk'
            ).interactive()

            st.altair_chart(chart, use_container_width=True)
        else:
            st.warning("Tidak ada data jumlah penduduk yang tersedia untuk visualisasi.")

    else:
        st.warning("Gagal memuat data jumlah penduduk dari Google Sheet. Pastikan URL dan nama worksheet sudah benar, dan sheet dapat diakses.")