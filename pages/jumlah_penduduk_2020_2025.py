import streamlit as st
import pandas as pd
import altair as alt # Asumsi Anda menggunakan Altair untuk visualisasi
from data_loader import load_penduduk_data_from_gsheet # Impor fungsi dari data_loader.py

import io # Diperlukan untuk BytesIO
from fpdf import FPDF # Diperlukan untuk menghasilkan PDF. Pastikan 'fpdf2' terinstal.

# --- Fungsi Helper untuk Konversi Data ---
def to_excel(df):
    """
    Mengonversi DataFrame ke format Excel (BytesIO) untuk diunduh.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DataPenduduk')
    processed_data = output.getvalue()
    return processed_data

def df_to_pdf(df):
    """
    Mengonversi DataFrame ke format PDF (BytesIO) menggunakan fpdf.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Menambahkan judul
    pdf.cell(200, 10, txt="Data Jumlah Penduduk (2020-2025)", ln=True, align='C')
    pdf.ln(5) # Spasi

    # Menambahkan header kolom
    headers = df.columns.tolist()
    # Atur lebar kolom secara dinamis berdasarkan lebar halaman atau jumlah kolom
    # Jika ada banyak kolom, ini mungkin perlu disesuaikan lebih lanjut
    # (pdf.w - 2 * pdf.l_margin) adalah lebar area yang bisa dicetak
    col_width = (pdf.w - 2 * pdf.l_margin) / len(headers) if len(headers) > 0 else 0

    if len(headers) > 0:
        for i, header in enumerate(headers):
            # Menggunakan .encode('latin-1') untuk teks yang aman di PDF
            # 'replace' akan mengganti karakter yang tidak bisa di-encode dengan '?'
            pdf.cell(col_width, 10, str(header).encode('latin-1', 'replace').decode('latin-1'), border=1, ln=(i == len(headers) - 1))
    else:
        pdf.cell(200, 10, "Tidak ada kolom yang ditemukan.", ln=True)

    # Menambahkan baris data
    for row in df.itertuples(index=False):
        for i, data in enumerate(row):
            # Menggunakan .encode('latin-1') untuk teks yang aman di PDF
            pdf.cell(col_width, 10, str(data).encode('latin-1', 'replace').decode('latin-1'), border=1, ln=(i == len(row) - 1))

    # Baris yang diperbaiki: tambahkan encoding
    return pdf.output(dest='S').encode('latin-1')


# --- Fungsi utama untuk halaman ini ---
def run():
    st.title("Jumlah Penduduk (2020-2025)")
    st.markdown("---") # Garis pemisah

    # Memuat data penduduk
    df_penduduk = load_penduduk_data_from_gsheet()

    if not df_penduduk.empty:
        st.subheader("Data Mentah Jumlah Penduduk")
        st.dataframe(df_penduduk)

        # --- Visualisasi Data ---
        st.subheader("Tren Jumlah Penduduk dari Tahun ke Tahun")

        # Pastikan nama kolom 'Tahun' dan 'Jumlah Total (orang)' ada untuk grafik
        # Nama kolom yang dicari di sini harus sesuai dengan nama kolom di Google Sheet Anda
        # yaitu 'Tahun' dan 'Jumlah Total (orang)' sesuai diskusi sebelumnya.
        if 'Tahun' in df_penduduk.columns and 'Jumlah Total (orang)' in df_penduduk.columns:
            chart = alt.Chart(df_penduduk).mark_line(point=True).encode(
                x=alt.X('Tahun:O', title='Tahun'), # 'O' untuk data ordinal/kategorikal
                y=alt.Y('Jumlah Total (orang):Q', title='Jumlah Penduduk'), # 'Q' untuk data kuantitatif
                tooltip=[
                    'Tahun',
                    'Jumlah Laki-Laki (orang)',
                    'Jumlah Perempuan (orang)',
                    'Jumlah Total (orang)',
                    'Jumlah Kepala Keluarga (KK)'
                ]
            ).properties(
                title='Perkembangan Jumlah Penduduk 2020-2025'
            ).interactive()

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
        else:
            st.warning("Kolom 'Tahun' atau 'Jumlah Total (orang)' tidak ditemukan untuk visualisasi grafik. Pastikan nama kolom di Google Sheet Anda sesuai.")

        # Contoh metrik sederhana
        # Pastikan nama kolom di sini cocok dengan yang dimuat dari Google Sheet: 'Tahun', 'Jumlah Total (orang)'
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
                    # Mencari tahun sebelumnya yang ada di data
                    tahun_sebelumnya_data = df_penduduk[df_penduduk['Tahun'] < tahun_terbaru]['Tahun'].max()
                    if pd.notna(tahun_sebelumnya_data): # Pastikan tahun sebelumnya bukan NaN
                        jumlah_sebelumnya = df_penduduk[df_penduduk['Tahun'] == tahun_sebelumnya_data]['Jumlah Total (orang)'].iloc[0]
                        perubahan = jumlah_terbaru - jumlah_sebelumnya
                        st.metric(label=f"Perubahan dari Tahun {tahun_sebelumnya_data}", value=f"{perubahan:,.0f} orang", delta=f"{perubahan:,.0f}")
                    else:
                        st.info("Tidak cukup data untuk menghitung perubahan dari tahun sebelumnya (tahun sebelumnya tidak ditemukan).")
                else:
                    st.info("Tidak cukup data untuk menghitung perubahan dari tahun sebelumnya.")

        st.markdown("---") # Garis pemisah

        # --- Siapkan Data dan Tombol Download ---
        df_excel = to_excel(df_penduduk)
        pdf_data = df_to_pdf(df_penduduk)

        col1, col2 = st.columns(2)
        # Download Dengan XLSX
        with col1:
            st.download_button(
                label="Download as XLSX",
                data=df_excel,
                file_name="data_penduduk.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        # Download Dengan PDF
        with col2:
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="data_penduduk.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        # Pesan ini ditampilkan jika df_penduduk kosong setelah mencoba memuat data.
        st.info("Belum ada data jumlah penduduk yang valid untuk divisualisasikan. Pastikan Google Sheet Anda dapat diakses dan memiliki data yang benar di worksheet 'Jumlah Penduduk (2020-2025)' dengan kolom 'Tahun', 'Jumlah Laki-Laki (orang)', 'Jumlah Perempuan (orang)', 'Jumlah Total (orang)', dan 'Jumlah Kepala Keluarga (KK)'.")

# Bagian ini hanya akan dieksekusi jika file ini dijalankan secara langsung, bukan sebagai modul yang diimpor oleh main.py.
if __name__ == '__main__':
    run()