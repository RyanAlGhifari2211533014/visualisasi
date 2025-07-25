import streamlit as st
import pandas as pd
import altair as alt # Menggunakan Altair untuk visualisasi
import io
from fpdf import FPDF # Pastikan 'fpdf2' terinstal.

# Import fungsi pemuat data
from data_loader import load_kk_rw_data_gsheet

# Nonaktifkan batas baris Altair agar bisa memproses data besar
alt.data_transformers.disable_max_rows()

# --- Fungsi Konversi untuk Download ---

def to_excel(df: pd.DataFrame):
    """
    Mengonversi DataFrame Pandas menjadi file Excel di dalam memori.
    Akan mengecualikan kolom 'LAKI- LAKI' dan 'PEREMPUAN' jika ada, sesuai dengan visualisasi Colab.
    """
    # Buat salinan DataFrame dan hapus kolom yang tidak diinginkan
    df_filtered = df.drop(columns=['LAKI- LAKI', 'PEREMPUAN'], errors='ignore')
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: # Menggunakan xlsxwriter untuk Excel
        df_filtered.to_excel(writer, index=False, sheet_name='DataKK_RW')
    processed_data = output.getvalue()
    return processed_data

def df_to_pdf(df: pd.DataFrame):
    """
    Mengonversi DataFrame Pandas menjadi file PDF untuk data Jumlah KK Menurut RW.
    Akan mengecualikan kolom 'LAKI- LAKI' dan 'PEREMPUAN', dan mempertahankan format sebelumnya.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4") # 'P' untuk Portrait
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    
    pdf.cell(0, 10, 'Data Jumlah Kepala Keluarga (KK) per RW', 0, 1, 'C')
    pdf.ln(10)

    # Buat salinan DataFrame dan hapus kolom yang tidak diinginkan
    df_for_pdf = df.drop(columns=['LAKI- LAKI', 'PEREMPUAN'], errors='ignore')
    
    # Perbaikan: Tambahkan kolom 'No' ke DataFrame untuk PDF sebagai nomor urut
    df_for_pdf.insert(0, 'No.', range(1, 1 + len(df_for_pdf))) 

    # Header Kolom Tabel
    pdf.set_font("Arial", "B", 10)
    effective_page_width = pdf.w - 2 * pdf.l_margin
    
    # Menentukan lebar kolom secara manual untuk kontrol yang lebih baik
    col_widths = {
        'No.': 15,
        'RW': 40, # Lebar untuk RW
        'JUMLAH KK': 60 # Lebar untuk Jumlah KK
    }
    
    headers = df_for_pdf.columns.tolist()
    # Hitung lebar default untuk kolom yang tidak didefinisikan secara eksplisit
    remaining_width = effective_page_width - sum(col_widths.get(h, 0) for h in headers)
    remaining_cols = len(headers) - sum(1 for h in headers if h in col_widths)
    default_col_width = remaining_width / remaining_cols if remaining_cols > 0 else 20
    
    if default_col_width < 10: default_col_width = 10

    # Cetak header
    y_start_headers = pdf.get_y()
    x_current = pdf.get_x()
    max_y_after_headers = y_start_headers

    for i, header in enumerate(headers):
        current_col_width = col_widths.get(header, default_col_width)
        pdf.set_xy(x_current, y_start_headers)
        pdf.multi_cell(current_col_width, 5, str(header).encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
        x_current += current_col_width
        max_y_after_headers = max(max_y_after_headers, pdf.get_y())
    
    pdf.set_y(max_y_after_headers) 

    # Data Baris Tabel
    pdf.set_font("Arial", "", 9)
    for index, row in df_for_pdf.iterrows():
        for i, item in enumerate(row):
            header = headers[i]
            current_col_width = col_widths.get(header, default_col_width)
            
            # Menghilangkan ".0" untuk nilai numerik
            formatted_item = str(item)
            if isinstance(item, (int, float)):
                if float(item).is_integer():
                    formatted_item = str(int(item))
                else:
                    formatted_item = str(item) # Biarkan float jika ada desimal
            
            pdf.cell(current_col_width, 10, formatted_item.encode('latin-1', 'replace').decode('latin-1'), border=1, ln=False)
        pdf.ln()
    
    # Tambahkan teks sumber di bagian bawah tabel
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, "Sumber: Kelurahan Kubu Marapalam", align='C')

    return bytes(pdf.output())

# --- Fungsi utama untuk menjalankan halaman ---

def run():
    """
    Merender halaman 'Jumlah KK Menurut RW'.
    """
    st.title("👨‍👩‍👧‍👦 Jumlah KK Menurut RW")

    # Muat data dari Google Sheets
    df_kk_rw = load_kk_rw_data_gsheet()

    if not df_kk_rw.empty:
        # --- Tampilkan Tabel Data (tanpa kolom LAKI- LAKI, PEREMPUAN) ---
        st.subheader("Tabel Rincian Jumlah Kepala Keluarga per RW")
        df_display = df_kk_rw.drop(columns=['LAKI- LAKI', 'PEREMPUAN'], errors='ignore')
        st.dataframe(df_display, use_container_width=True)
        st.markdown("---")

        # --- Tampilkan Visualisasi dengan Altair ---
        st.subheader("Grafik Perbandingan Jumlah Kepala Keluarga (KK) per RW")
        
        # Pastikan kolom yang dibutuhkan ada untuk grafik
        if 'RW' in df_kk_rw.columns and 'JUMLAH KK' in df_kk_rw.columns:
            # Mengurutkan data berdasarkan 'JUMLAH KK'
            df_sorted = df_kk_rw.sort_values('JUMLAH KK', ascending=False)

            chart = alt.Chart(df_sorted).mark_bar(
                cornerRadiusEnd=4
            ).encode(
                x=alt.X('JUMLAH KK:Q', title='Jumlah Kepala Keluarga (KK)'),
                y=alt.Y('RW:N', sort='-x', title='Wilayah RW'), # Sortir berdasarkan Jumlah KK secara menurun
                color=alt.Color('RW:N', legend=None), # Warna berdasarkan RW, tanpa legenda
                tooltip=[
                    alt.Tooltip('RW:N', title='Wilayah RW'),
                    alt.Tooltip('JUMLAH KK:Q', title='Jumlah KK')
                ]
            ).properties(
                title='Perbandingan Jumlah Kepala Keluarga (KK) per RW'
            )

            # Menambahkan label angka di ujung setiap bar
            text = chart.mark_text(
                align='left',
                baseline='middle',
                dx=3 # Jarak label dari batang
            ).encode(
                x='JUMLAH KK:Q',
                y=alt.Y('RW:N', sort='-x'),
                text=alt.Text('JUMLAH KK:Q', format='.0f') # Format angka tanpa desimal
            )

            final_chart = chart + text # Gabungkan bar chart dan label
            st.altair_chart(final_chart, use_container_width=True)
        else:
            st.warning("Kolom 'RW' atau 'JUMLAH KK' tidak ditemukan untuk visualisasi grafik. Pastikan nama kolom di Google Sheet Anda sesuai.")

        # --- Siapkan Data dan Tombol Download ---
        df_excel = to_excel(df_kk_rw) # df_kk_rw sudah dimuat dari GSheet
        pdf_data = df_to_pdf(df_kk_rw) # df_kk_rw sudah dimuat dari GSheet

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="Download as XLSX",
                data=df_excel,
                file_name="data_kk_rw.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="data_kk_rw.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("Belum ada data jumlah KK per RW yang valid untuk divisualisasikan. Pastikan Google Sheet Anda dapat diakses dan memiliki data yang benar di worksheet 'Jumlah KK Menurut RW' dengan kolom 'RW', 'LAKI- LAKI', 'PEREMPUAN', dan 'JUMLAH KK'.")