# File: pages/jumlah_penduduk_pendidikan.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
from fpdf import FPDF

# Impor fungsi pemuat data yang sudah diperbarui dari data_loader
#from data_loader import load_pendidikan_data_from_excel
from data_loader import load_pendidikan_data_from_gsheet

# --- Fungsi Konversi untuk Download ---

def to_excel(df: pd.DataFrame):
    """
    Mengonversi DataFrame Pandas menjadi file Excel di dalam memori.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Data Pendidikan')
    processed_data = output.getvalue()
    return processed_data

def df_to_pdf(df: pd.DataFrame):
    """
    Mengonversi DataFrame Pandas menjadi file PDF.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4") # 'P' untuk Portrait
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    
    pdf.cell(0, 10, 'Data Penduduk Berdasarkan Tingkat Pendidikan', 0, 1, 'C')
    pdf.ln(10)

    pdf.set_font("Arial", "B", 10)
    effective_page_width = pdf.w - 2 * pdf.l_margin
    col_width = effective_page_width / len(df.columns)

    for col_header in df.columns:
        pdf.cell(col_width, 10, col_header, border=1, align='C')
    pdf.ln()

    pdf.set_font("Arial", "", 9)
    for index, row in df.iterrows():
        for item in row:
            # Mengonversi semua item menjadi string untuk dicetak di PDF
            pdf.cell(col_width, 10, str(item), border=1, align='C')
        pdf.ln()
    
    return bytes(pdf.output())

# --- Fungsi utama untuk menjalankan halaman ---

def run():
    """
    Merender halaman 'Jumlah Penduduk (Pendidikan)'.
    """
    st.title("🎓 Jumlah Penduduk Berdasarkan Tingkat Pendidikan")

    # Muat data dari file Excel menggunakan fungsi baru
    df_pendidikan = load_pendidikan_data_from_gsheet()

    if not df_pendidikan.empty:
        # --- Tampilkan Visualisasi ---
        st.subheader("Grafik Distribusi Pendidikan")
        
        # Membuat grafik batang horizontal dengan Matplotlib dan Seaborn
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.set_style("whitegrid")
        
        # Menggunakan barplot dari Seaborn
        sns.barplot(x='Jumlah', y='Tingkat Pendidikan', data=df_pendidikan, ax=ax, orient='h', palette='viridis')
        
        ax.set_xlabel('Jumlah Orang', fontsize=12)
        ax.set_ylabel('Tingkat Pendidikan', fontsize=12)
        ax.set_title('Distribusi Penduduk Berdasarkan Pendidikan', fontsize=14, pad=20)
        
        # Menambahkan label angka di ujung setiap bar
        for index, value in enumerate(df_pendidikan['Jumlah']):
            ax.text(value, index, f' {value}', va='center', fontsize=10)
            
        plt.tight_layout()
        st.pyplot(fig)

        # --- Tampilkan Tabel Data ---
        st.subheader("Tabel Rincian Data Pendidikan")
        st.dataframe(df_pendidikan, use_container_width=True)
        st.markdown("---")

        # --- Siapkan Data dan Tombol Download ---
        df_excel = to_excel(df_pendidikan)
        pdf_data = df_to_pdf(df_pendidikan)

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="📥 Download as XLSX",
                data=df_excel,
                file_name="data_pendidikan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            st.download_button(
                label="📄 Download as PDF",
                data=pdf_data,
                file_name="data_pendidikan.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.warning("Data pendidikan tidak dapat dimuat. Pastikan file 'Jumlah Penduduk (Pendidikan).xlsx' ada dan formatnya benar.")

