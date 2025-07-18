# File: pages/jumlah_penduduk_2020_2025.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
from fpdf import FPDF

# Import data loading functions from data_loader
from data_loader import load_penduduk_data_from_excel

# --- Fungsi Konversi untuk Download ---

def to_excel(df: pd.DataFrame):
    """
    Mengonversi DataFrame Pandas menjadi file Excel di dalam memori.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data Penduduk')
    processed_data = output.getvalue()
    return processed_data

def df_to_pdf(df: pd.DataFrame):
    """
    Mengonversi DataFrame Pandas menjadi file PDF.
    """
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 10)
    
    effective_page_width = pdf.w - 2 * pdf.l_margin
    col_width = effective_page_width / len(df.columns)

    for col_header in df.columns:
        pdf.cell(col_width, 10, col_header, border=1, align='C')
    pdf.ln()

    pdf.set_font("Arial", "", 8)
    for index, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1, align='C')
        pdf.ln()
    
    # --- PERBAIKAN DI SINI ---
    # Konversi output 'bytearray' dari FPDF menjadi 'bytes' yang diterima oleh Streamlit.
    return bytes(pdf.output())


# --- Fungsi utama untuk menjalankan halaman ---

def run():
    """
    Merender halaman 'Jumlah Penduduk (2020-2025)', termasuk grafik, tabel, dan tombol download.
    """
    st.title('📊 Jumlah Penduduk (2020-2025)')

    # Muat data dari file Excel
    df_penduduk_tahun = load_penduduk_data_from_excel()

    # Pastikan DataFrame tidak kosong sebelum melanjutkan
    if not df_penduduk_tahun.empty and 'Tahun' in df_penduduk_tahun.columns and 'Jumlah Total (orang)' in df_penduduk_tahun.columns:
        
        # --- Tampilkan Visualisasi Data Penduduk ---
        st.subheader("Grafik Tren Jumlah Penduduk Tahunan")
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.set(style="whitegrid")

        sns.lineplot(
            x='Tahun',
            y='Jumlah Total (orang)',
            data=df_penduduk_tahun,
            marker='o',
            linewidth=2.5,
            ax=ax
        )

        ax.set_title('Tren Jumlah Penduduk Total (2020 - 2025)', fontsize=16, pad=20)
        ax.set_xlabel('Tahun', fontsize=12)
        ax.set_ylabel('Jumlah Penduduk (Orang)', fontsize=12)
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        plt.xticks(rotation=45)

        for index, row in df_penduduk_tahun.iterrows():
            ax.text(row['Tahun'], row['Jumlah Total (orang)'] + (df_penduduk_tahun['Jumlah Total (orang)'].max() * 0.01),
                    f"{int(row['Jumlah Total (orang)'])}",
                    ha='center', va='bottom', fontsize=10)

        plt.tight_layout()
        st.pyplot(fig)

        # --- Tampilkan Tabel Data ---
        st.subheader("Tabel Data Penduduk")
        st.dataframe(df_penduduk_tahun, use_container_width=True)
        st.markdown("---") # Garis pemisah

        # --- Siapkan Data dan Tombol Download ---
        df_excel = to_excel(df_penduduk_tahun)
        pdf_data = df_to_pdf(df_penduduk_tahun)

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
        #Download Dengan PDF
        with col2:
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="data_penduduk.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("Belum ada data jumlah penduduk yang valid untuk divisualisasikan. Pastikan file Excel ada dan memiliki kolom 'Tahun' serta 'Jumlah Total (orang)' dengan data yang benar.")

