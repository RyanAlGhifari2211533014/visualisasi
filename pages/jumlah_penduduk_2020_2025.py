# File: D:\visualisasi\pages\jumlah_penduduk_2020_2025.py

import streamlit as st
import pandas as pd
import altair as alt # Asumsikan Anda menggunakan Altair untuk visualisasi
from data_loader import load_penduduk_data_from_gsheet # Impor fungsi dari data_loader.py

# --- Fungsi utama untuk halaman ini ---
def run():
    st.title("Jumlah Penduduk (2020-2025)")
    st.markdown("---") # Garis pemisah

    # Memuat data penduduk
    # Pastikan load_penduduk_data_from_gsheet() tersedia dan berfungsi dengan baik.
    df_penduduk = load_penduduk_data_from_gsheet()

    if not df_penduduk.empty:
        st.subheader("Data Mentah Jumlah Penduduk")
        st.dataframe(df_penduduk)

        # --- Visualisasi Data ---
        st.subheader("Tren Jumlah Penduduk dari Tahun ke Tahun")

        # Membuat chart menggunakan Altair
        chart = alt.Chart(df_penduduk).mark_line(point=True).encode(
            x=alt.X('Tahun:O', title='Tahun'), # 'O' untuk data ordinal/kategorikal
            y=alt.Y('Jumlah Total (orang):Q', title='Jumlah Penduduk'), # 'Q' untuk data kuantitatif
            tooltip=['Tahun', 'Jumlah Total (orang)']
        ).properties(
            title='Perkembangan Jumlah Penduduk 2020-2025'
        ).interactive() # Membuat chart interaktif (zoom, pan)

        st.altair_chart(chart, use_container_width=True)

        st.markdown(
            """
            <div style="background-color:#e6f3ff; padding: 10px; border-radius: 5px;">
                <p style="font-size: 14px; color: #333;">
                    Grafik di atas menunjukkan perubahan jumlah penduduk dari tahun ke tahun.
                    Data ini penting untuk analisis demografi dan perencanaan.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Contoh metrik sederhana
        if 'Tahun' in df_penduduk.columns and 'Jumlah Total (orang)' in df_penduduk.columns:
            tahun_terbaru = df_penduduk['Tahun'].max()
            jumlah_terbaru = df_penduduk[df_penduduk['Tahun'] == tahun_terbaru]['Jumlah Total (orang)'].iloc[0]

            st.markdown("---")
            st.subheader("Ringkasan Data")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label=f"Tahun Data Terakhir ({tahun_terbaru})", value=f"{jumlah_terbaru:,.0f} orang")
            with col2:
                # Menghitung perubahan jika ada lebih dari satu tahun data
                if len(df_penduduk) > 1:
                    jumlah_sebelumnya = df_penduduk[df_penduduk['Tahun'] == df_penduduk['Tahun'].max() - 1]['Jumlah Total (orang)'].iloc[0] if df_penduduk['Tahun'].max() - 1 in df_penduduk['Tahun'].values else None
                    if jumlah_sebelumnya is not None:
                        perubahan = jumlah_terbaru - jumlah_sebelumnya
                        st.metric(label=f"Perubahan dari Tahun Sebelumnya", value=f"{perubahan:,.0f} orang", delta=f"{perubahan:,.0f}")
                    else:
                        st.info("Tidak cukup data untuk menghitung perubahan dari tahun sebelumnya.")
                else:
                    st.info("Tidak cukup data untuk menghitung perubahan dari tahun sebelumnya.")

    else:
        st.warning("Tidak dapat menampilkan data. Pastikan Google Sheet 'Jumlah Penduduk' memiliki data yang benar.")

# Jika Anda menjalankan file ini secara langsung (bukan sebagai modul), panggil run().
# Ini biasanya tidak terjadi jika file ini dipanggil dari main.py.
if __name__ == '__main__':
    run()