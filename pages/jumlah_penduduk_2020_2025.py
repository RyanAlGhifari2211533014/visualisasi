# File: pages/jumlah_penduduk_2020_2025.py

# 📥 Import Library yang Dibutuhkan
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
from fpdf import FPDF

# 📡 Import fungsi koneksi data Google Sheets dari data_loader.py
from data_loader import load_penduduk_data_from_gsheet

# 🔁 Fungsi konversi DataFrame ke file celEx (.xlsx)
def to_gsheet(df: pd.DataFrame):
    output = io.BytesIO()
    with pd.gsheetxcelWriter(output, engine='openpyxl') as writer:
        df.to_gsheet(writer, index=False, sheet_name='Data Penduduk')
    return output.getvalue()

# 📄 Fungsi konversi DataFrame ke file PDF menggunakan fpdf
def df_to_pdf(df: pd.DataFrame):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 10)

    # Hitung lebar kolom agar pas dalam halaman
    effective_page_width = pdf.w - 2 * pdf.l_margin
    col_width = effective_page_width / len(df.columns)

    # 🔠 Tulis header kolom
    for col_header in df.columns:
        pdf.cell(col_width, 10, str(col_header), border=1, align='C')
    pdf.ln()

    # 🧾 Tulis isi data
    pdf.set_font("Arial", "", 8)
    for _, row in df.iterrows():
        for item in row:
            pdf.cell(col_width, 10, str(item), border=1, align='C')
        pdf.ln()

    # 🔙 Kembalikan hasil PDF sebagai bytes
    return pdf.output(dest='S').encode('latin1')

# 🚀 Fungsi utama untuk menampilkan halaman Streamlit
def run():
    # 📃 Konfigurasi tampilan halaman
    st.set_page_config(page_title="Jumlah Penduduk", layout="wide")
    st.title('📊 Jumlah Penduduk (2020-2025)')

    # 🔄 Load data dari Google Sheets melalui fungsi di data_loader.py
    df_penduduk_tahun = load_penduduk_data_from_gsheet()

    # ✅ Cek apakah data valid dan kolom yang dibutuhkan tersedia
    if not df_penduduk_tahun.empty and 'Tahun' in df_penduduk_tahun.columns and 'Jumlah Total (orang)' in df_penduduk_tahun.columns:
        st.subheader("📈 Grafik Tren Jumlah Penduduk Tahunan")

        # 🎨 Setup visualisasi dengan Matplotlib dan Seaborn
        fig, ax = plt.subplots(figsize=(12, 7))
        sns.set(style="whitegrid")

        # 📉 Buat garis tren populasi per tahun
        sns.lineplot(
            x='Tahun',
            y='Jumlah Total (orang)',
            data=df_penduduk_tahun,
            marker='o',
            linewidth=2.5,
            ax=ax
        )

        # 🏷️ Set judul dan label
        ax.set_title('Tren Jumlah Penduduk Total (2020 - 2025)', fontsize=16, pad=20)
        ax.set_xlabel('Tahun', fontsize=12)
        ax.set_ylabel('Jumlah Penduduk (Orang)', fontsize=12)
        ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
        plt.xticks(rotation=45)

        # 🔢 Tampilkan label angka di atas titik grafik
        for index, row in df_penduduk_tahun.iterrows():
            ax.text(
                row['Tahun'],
                row['Jumlah Total (orang)'] + (df_penduduk_tahun['Jumlah Total (orang)'].max() * 0.01),
                f"{int(row['Jumlah Total (orang)'])}",
                ha='center', va='bottom', fontsize=10
            )

        plt.tight_layout()

        # 📌 Tampilkan grafik di halaman Streamlit
        st.pyplot(fig)

        # 🧮 Tampilkan tabel data mentah
        st.subheader("📋 Tabel Data Penduduk")
        st.dataframe(df_penduduk_tahun, use_container_width=True)
        st.markdown("---")

        # 💾 Siapkan data untuk diunduh dalam format Excel dan PDF
        df_excel = to_excel(df_penduduk_tahun)
        pdf_data = df_to_pdf(df_penduduk_tahun)

        # ⬇️ Buat tombol download untuk XLSX dan PDF
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="⬇️ Download sebagai XLSX",
                data=df_excel,
                file_name="data_penduduk.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col2:
            st.download_button(
                label="⬇️ Download sebagai PDF",
                data=pdf_data,
                file_name="data_penduduk.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    else:
        # ⚠️ Jika data tidak valid atau kolom penting tidak ada
        st.info("Belum ada data jumlah penduduk yang valid. Pastikan kolom 'Tahun' dan 'Jumlah Total (orang)' tersedia.")
