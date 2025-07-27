import streamlit as st
import pandas as pd
import altair as alt # Impor Altair
# Hapus matplotlib.pyplot dan seaborn karena akan menggunakan Altair
# import matplotlib.pyplot as plt
# import seaborn as sns
import io
from fpdf import FPDF # Pastikan 'fpdf2' terinstal.

# Import fungsi pemuat data
from data_loader import load_jenis_pekerjaan_dominan_gsheet

# Nonaktifkan batas baris Altair agar bisa memproses data besar
alt.data_transformers.disable_max_rows()

# --- Fungsi Konversi untuk Download ---

def to_excel(df: pd.DataFrame):
    """
    Mengonversi DataFrame Pandas menjadi file Excel di dalam memori.
    Akan mengecualikan kolom 'Tanggal' jika ada.
    """
    # Buat salinan DataFrame dan hapus kolom 'Tanggal' jika ada
    df_filtered = df.drop(columns=['Tanggal'], errors='ignore')
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: # Menggunakan xlsxwriter untuk Excel
        df_filtered.to_excel(writer, index=False, sheet_name='DataPekerjaan')
    processed_data = output.getvalue()
    return processed_data

def df_to_pdf(df: pd.DataFrame):
    """
    Mengonversi DataFrame Pandas menjadi file PDF untuk data Jenis Pekerjaan.
    Akan mengecualikan kolom 'Tanggal' dan mempertahankan format sebelumnya.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4") # 'P' untuk Portrait
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    
    pdf.cell(0, 10, 'Data Jenis Pekerjaan Dominan', 0, 1, 'C')
    pdf.ln(10)

    # Buat salinan DataFrame dan hapus kolom 'Tanggal' jika ada
    df_for_pdf = df.drop(columns=['Tanggal'], errors='ignore')
    
    # Perbaikan: Tambahkan kolom 'No' ke DataFrame untuk PDF jika belum ada
    if 'No.' not in df_for_pdf.columns: # Cek jika kolom 'No.' sudah ada dari GSheet
        df_for_pdf.insert(0, 'No.', range(1, 1 + len(df_for_pdf))) 

    # Header Kolom Tabel
    pdf.set_font("Arial", "B", 10)
    effective_page_width = pdf.w - 2 * pdf.l_margin
    
    # Menentukan lebar kolom secara manual untuk kontrol yang lebih baik
    col_widths = {
        'No.': 15,
        'Jenis Pekerjaan': 100, # Lebih lebar untuk nama pekerjaan
        'Jumlah': 30
    }
    
    headers = df_for_pdf.columns.tolist()
    # Hitung lebar default untuk kolom yang tidak didefinisikan secara eksplisit
    # Pastikan pembagian tidak oleh nol
    remaining_width = effective_page_width - sum(col_widths.get(h, 0) for h in headers)
    remaining_cols = len(headers) - sum(1 for h in headers if h in col_widths)
    default_col_width = remaining_width / remaining_cols if remaining_cols > 0 else 30
    
    # Pastikan default_col_width tidak negatif atau terlalu kecil
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
                    formatted_item = str(item)
            
            pdf.cell(current_col_width, 10, formatted_item.encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
        pdf.ln()
    
    # Tambahkan teks sumber di bagian bawah tabel
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, "Sumber: Kelurahan Kubu Marapalam", align='C')

    return bytes(pdf.output())

# --- FUNGSI BARU: Mendapatkan Objek Grafik untuk Halaman ini ---
def get_jenis_pekerjaan_chart():
    """
    Membuat dan mengembalikan objek grafik Altair untuk Jenis Pekerjaan Dominan.
    """
    df_pekerjaan = load_jenis_pekerjaan_dominan_gsheet()

    if df_pekerjaan.empty:
        st.info("Data tidak tersedia untuk grafik ini.")
        return None
    
    # Pastikan kolom yang dibutuhkan ada untuk grafik
    if 'Jenis Pekerjaan' in df_pekerjaan.columns and 'Jumlah' in df_pekerjaan.columns:
        # Membuat bar chart horizontal dengan Altair
        chart = alt.Chart(df_pekerjaan).mark_bar(
            cornerRadiusEnd=4
        ).encode(
            x=alt.X('Jumlah:Q', title='Jumlah Unit Usaha'),
            y=alt.Y('Jenis Pekerjaan:N', sort='-x', title='Jenis Industri'), # Sortir berdasarkan Jumlah secara menurun
            color=alt.Color('Jenis Pekerjaan:N', legend=None), # Warna berdasarkan Jenis, tanpa legenda
            tooltip=[
                alt.Tooltip('Jenis Pekerjaan:N', title='Jenis Industri'),
                alt.Tooltip('Jumlah:Q', title='Jumlah', format='.0f') # Format angka tanpa desimal
            ]
        ).properties(
            title='Jumlah Unit Usaha per Jenis Industri UMKM'
        )

        # Menambahkan label angka di ujung setiap bar
        text = chart.mark_text(
            align='left',
            baseline='middle',
            dx=3 # Jarak label dari batang
        ).encode(
            x='Jumlah:Q',
            y=alt.Y('Jenis Pekerjaan:N', sort='-x'),
            text=alt.Text('Jumlah:Q', format='.0f') # Format angka tanpa desimal
        )

        final_chart = chart + text # Gabungkan bar chart dan label
        return final_chart
    else:
        st.warning("Kolom 'Jenis Pekerjaan' atau 'Jumlah' tidak ditemukan untuk visualisasi grafik. Pastikan nama kolom di Google Sheet Anda sesuai.")
        return None

# --- Fungsi utama untuk menjalankan halaman ---

def run():
    """
    Merender halaman 'Jenis Pekerjaan Dominan'.
    """
    st.title("👷‍♂️ Jenis Pekerjaan Dominan")

    # Muat data dari Google Sheets
    df_pekerjaan = load_jenis_pekerjaan_dominan_gsheet()

    if not df_pekerjaan.empty:
        # --- Tampilkan Tabel Data (tanpa kolom Tanggal) ---
        st.subheader("Tabel Rincian Jenis Pekerjaan Dominan")
        df_display = df_pekerjaan.drop(columns=['Tanggal'], errors='ignore')
        st.dataframe(df_display, use_container_width=True)
        st.markdown("---")

        # --- Tampilkan Visualisasi ---
        st.subheader("Grafik Distribusi Jenis Pekerjaan Dominan")
        
        chart_obj = get_jenis_pekerjaan_chart() # Panggil fungsi pembuat grafik
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True)

            st.markdown(
                """
                <div style="background-color:#e6f3ff; padding: 10px; border-radius: 5px;">
                    <p style="font-size: 14px; color: #333;">
                        Grafik ini menunjukkan jenis pekerjaan yang paling dominan di kelurahan.
                        Data ini dapat membantu dalam perencanaan program pelatihan atau pengembangan ekonomi lokal.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("Tidak dapat menampilkan grafik karena data tidak tersedia atau tidak valid.")

        # --- Siapkan Data dan Tombol Download ---
        # Data untuk Excel dan PDF sudah difilter agar tidak menyertakan kolom 'Tanggal'
        df_excel = to_excel(df_pekerjaan)
        pdf_data = df_to_pdf(df_pekerjaan)

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="Download as XLSX",
                data=df_excel,
                file_name="data_jenis_pekerjaan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="data_jenis_pekerjaan.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("Belum ada data jenis pekerjaan yang valid untuk divisualisasikan. Pastikan Google Sheet Anda dapat diakses dan memiliki data yang benar di worksheet 'Jenis Pekerjaan Dominan' dengan kolom 'No.', 'Tanggal', 'Jenis Pekerjaan', dan 'Jumlah'.")