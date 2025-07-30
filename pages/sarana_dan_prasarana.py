import streamlit as st
import pandas as pd
import altair as alt # Menggunakan Altair untuk visualisasi
import io
from fpdf import FPDF # Pastikan 'fpdf2' terinstal.

# Pastikan ini mengimpor fungsi yang benar dari data_loader
from data_loader import load_sarana_prasarana_from_gsheet

# Nonaktifkan batas baris Altair agar bisa memproses data besar
alt.data_transformers.disable_max_rows()

# --- Fungsi Helper untuk Konversi Data ---
def to_excel(df):
    """
    Mengonversi DataFrame ke format Excel (BytesIO) untuk diunduh.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DataSaranaPrasarana')
    processed_data = output.getvalue()
    return processed_data

def df_to_pdf(df: pd.DataFrame):
    """
    Mengonversi DataFrame ke format PDF (BytesIO) menggunakan fpdf.
    Fungsi ini telah diperbaiki untuk mengatasi masalah layout dan data kosong.
    """
    pdf = FPDF(orientation='L', unit='mm', format='A4') # 'L' untuk Landscape
    pdf.add_page()
    
    # Menambahkan judul utama
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt="Data Sarana dan Prasarana", ln=True, align='C')
    pdf.ln(5) # Memberi jarak setelah judul

    # Menyiapkan nama kolom untuk tampilan dan untuk akses data di DataFrame
    # Nama kolom ini harus sesuai dengan yang dihasilkan oleh data_loader.py
    headers_df = ['No', 'Tahun', 'Jenis_Sarana_dan_Prasarana', 'Jumlah_Unit']
    headers_display = ['No', 'Tahun', 'Jenis Sarana dan Prasarana', 'Jumlah (Unit)']
    
    # Menentukan lebar setiap kolom
    col_widths = {
        'No': 15,
        'Tahun': 25,
        'Jenis Sarana dan Prasarana': 180, # Lebar diperbesar
        'Jumlah (Unit)': 40
    }

    # --- PERBAIKAN 1: Menyederhanakan proses pembuatan header ---
    pdf.set_font("Arial", "B", 10) # Font tebal untuk header
    
    # Loop untuk membuat header tabel dalam satu baris
    for i, header_text in enumerate(headers_display):
        width = col_widths[header_text]
        pdf.cell(width, 10, header_text, border=1, align='C')
    pdf.ln() # Pindah ke baris baru setelah semua header selesai dicetak

    # --- PERBAIKAN 2: Memperbaiki loop untuk mengambil dan mencetak data ---
    pdf.set_font("Arial", "", 10) # Font normal untuk isi tabel
    
    # Loop melalui setiap baris di DataFrame
    for index, row in df.iterrows():
        # Loop melalui setiap kolom yang ingin kita tampilkan
        for i, header_display_text in enumerate(headers_display):
            width = col_widths[header_display_text]
            # Ambil nama kolom yang sesuai untuk DataFrame
            df_col_name = headers_df[i]
            
            # Ambil data dari baris menggunakan nama kolom yang benar
            data = row[df_col_name]
            
            # Format data untuk menghilangkan .0 jika itu integer
            formatted_data = str(data)
            if isinstance(data, (int, float)) and float(data).is_integer():
                formatted_data = str(int(data))
            
            # Cetak sel data
            pdf.cell(width, 10, formatted_data.encode('latin-1', 'replace').decode('latin-1'), border=1)
        pdf.ln() # Pindah ke baris baru untuk data selanjutnya

    # Menambahkan sumber di bagian bawah
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font("Arial", "I", 8) # Font miring untuk sumber
    pdf.cell(0, 10, "Sumber: Kelurahan Kubu Marapalam", align='C')

    return bytes(pdf.output())

# --- FUNGSI BARU: Mendapatkan Objek Grafik untuk Halaman ini ---
def get_sarana_prasarana_chart():
    """
    Membuat dan mengembalikan objek grafik Altair untuk Sarana dan Prasarana.
    """
    df_sarana_prasarana = load_sarana_prasarana_from_gsheet()

    if df_sarana_prasarana.empty:
        st.info("Data tidak tersedia untuk grafik ini.")
        return None
    
    # Menggunakan kolom yang sudah distandarisasi oleh data_loader
    # 'Jenis_Sarana_dan_Prasarana', 'Jumlah_Unit'
    if 'Jenis_Sarana_dan_Prasarana' in df_sarana_prasarana.columns and 'Jumlah_Unit' in df_sarana_prasarana.columns:
        chart_sarana = alt.Chart(df_sarana_prasarana).mark_bar(
            cornerRadiusTopLeft=5,
            cornerRadiusTopRight=5
        ).encode(
            x=alt.X('Jumlah_Unit:Q', title='Jumlah Unit'),
            y=alt.Y('Jenis_Sarana_dan_Prasarana:N', sort='-x', title='Jenis Sarana dan Prasarana'),
            color=alt.Color('Jumlah_Unit:Q', scale=alt.Scale(scheme='blues'), legend=None),
            tooltip=[
                alt.Tooltip('Jenis_Sarana_dan_Prasarana:N', title='Jenis Sarana'),
                alt.Tooltip('Jumlah_Unit:Q', title='Jumlah Unit', format='.0f')
            ]
        ).properties(
            title='Visualisasi Jumlah Sarana dan Prasarana'
        ).configure_axis(
            grid=False
        ).configure_view(
            stroke=None
        )
        return chart_sarana
    else:
        st.warning("Kolom 'Jenis_Sarana_dan_Prasarana' atau 'Jumlah_Unit' tidak ditemukan untuk visualisasi. Pastikan nama kolom di Google Sheet Anda sesuai.")
        return None

# --- Fungsi utama untuk halaman ini ---
def run():
    st.title("Data Sarana dan Prasarana")
    st.markdown("---")

    # Memuat data sarana dan prasarana
    df_sarana_prasarana = load_sarana_prasarana_from_gsheet()

    if not df_sarana_prasarana.empty:
        st.subheader("Tabel Data Sarana dan Prasarana")
        st.dataframe(df_sarana_prasarana, use_container_width=True, hide_index=True)

        # --- Visualisasi Data ---  
        st.subheader("Visualisasi Jumlah Sarana dan Prasarana")

        chart_obj = get_sarana_prasarana_chart()
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True)
            st.markdown(
                """
                <div style="background-color:#e6f3ff; padding: 10px; border-radius: 5px;">
                    <p style="font-size: 14px; color: #333;">
                        Grafik ini menunjukkan jumlah sarana dan prasarana di kelurahan.
                        Data ini penting untuk perencanaan dan pengembangan infrastruktur.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("Tidak dapat menampilkan grafik karena data tidak tersedia atau tidak valid.")

        # --- Tombol Download ---
        st.markdown("---")
        st.subheader("Unduh Data")
        
        df_excel_data = to_excel(df_sarana_prasarana)
        pdf_data = df_to_pdf(df_sarana_prasarana)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download as XLSX",
                data=df_excel_data,
                file_name="data_sarana_dan_prasarana.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col2:
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="data_sarana_dan_prasarana.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("Belum ada data sarana dan prasarana yang valid untuk divisualisasikan. Pastikan Google Sheet Anda dapat diakses dan memiliki data yang benar di worksheet 'Sarana dan Prasarana' dengan kolom 'No.', 'Tahun', 'Jenis Sarana dan Prasarana', dan 'Jumlah (Unit)'.")

if __name__ == '__main__':
    run()