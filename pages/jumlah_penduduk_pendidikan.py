# File: pages/jumlah_penduduk_pendidikan.py

import streamlit as st
import pandas as pd
import altair as alt # Impor Altair
import io
from fpdf import FPDF # Pastikan 'fpdf2' terinstal.

# Impor fungsi pemuat data yang sudah diperbarui dari data_loader
from data_loader import load_pendidikan_data_from_gsheet

# Nonaktifkan batas baris Altair agar bisa memproses data besar
alt.data_transformers.disable_max_rows()

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

    # Perbaikan: Tambahkan kolom 'No' ke DataFrame untuk PDF jika belum ada
    df_for_pdf = df.copy()
    if 'No' not in df_for_pdf.columns: 
        df_for_pdf.insert(0, 'No', range(1, 1 + len(df_for_pdf))) 

    pdf.set_font("Arial", "B", 10)
    effective_page_width = pdf.w - 2 * pdf.l_margin
    
    # Sesuaikan lebar kolom untuk PDF
    col_widths = {
        'No': 15,
        'Pendidikan': 90, # Lebar lebih besar untuk tingkat pendidikan
        'Jumlah': 30
    }
    
    headers = df_for_pdf.columns.tolist()
    # Hitung lebar default untuk kolom yang tidak didefinisikan secara eksplisit
    remaining_width = effective_page_width - sum(col_widths.get(h, 0) for h in headers)
    remaining_cols = len(headers) - sum(1 for h in headers if h in col_widths)
    default_col_width = remaining_width / remaining_cols if remaining_cols > 0 else 30
    
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
            
            pdf.cell(current_col_width, 10, formatted_item.encode('latin-1', 'replace').decode('latin-1'), border=1, ln=False)
        pdf.ln(10) # Pindah ke baris baru setelah setiap baris data
    
    # Tambahkan teks sumber di bagian bawah tabel
    pdf.set_y(pdf.get_y() + 5) # Tambahkan 5mm spasi setelah tabel
    pdf.set_font("Arial", size=8) # Ukuran font lebih kecil untuk sumber
    pdf.cell(0, 10, "Sumber: Kelurahan Kubu Marapalam", align='C')

    return bytes(pdf.output())

# --- FUNGSI BARU: Mendapatkan Objek Grafik untuk Halaman ini ---
def get_pendidikan_chart():
    """
    Membuat dan mengembalikan objek grafik Altair untuk Jumlah Penduduk (Pendidikan).
    """
    df_pendidikan = load_pendidikan_data_from_gsheet()

    if df_pendidikan.empty:
        st.info("Data tidak tersedia untuk grafik ini.")
        return None
    
    # Pastikan kolom yang dibutuhkan ada untuk grafik
    if 'Pendidikan' in df_pendidikan.columns and 'Jumlah' in df_pendidikan.columns:
        # Membuat bar chart horizontal dengan Altair
        chart = alt.Chart(df_pendidikan).mark_bar(
            cornerRadiusEnd=4 # Sudut bar lebih lembut di ujung
        ).encode(
            x=alt.X('Jumlah:Q', title='Jumlah Orang'),
            y=alt.Y('Pendidikan:N', sort='-x', title='Tingkat Pendidikan'), # Sortir berdasarkan Jumlah secara menurun
            color=alt.Color('Pendidikan:N', legend=None), # Warna berdasarkan Pendidikan, tanpa legenda
            tooltip=[
                alt.Tooltip('Pendidikan:N', title='Tingkat Pendidikan'),
                alt.Tooltip('Jumlah:Q', title='Jumlah', format='.0f') # Format angka tanpa desimal
            ]
        ).properties(
            title='Distribusi Penduduk Berdasarkan Pendidikan'
        )

        # Menambahkan label angka di ujung setiap bar
        text = chart.mark_text(
            align='left',
            baseline='middle',
            dx=3 # Jarak label dari batang
        ).encode(
            x='Jumlah:Q',
            y=alt.Y('Pendidikan:N', sort='-x'),
            text=alt.Text('Jumlah:Q', format='.0f') # Format angka tanpa desimal
        )

        final_chart = chart + text # Gabungkan bar chart dan label
        return final_chart
    else:
        st.warning("Kolom 'Pendidikan' atau 'Jumlah' tidak ditemukan untuk visualisasi grafik. Pastikan nama kolom di Google Sheet Anda sesuai.")
        return None

# --- Fungsi utama untuk menjalankan halaman ---
def run():
    """
    Merender halaman 'Jumlah Penduduk (Pendidikan)'.
    """
    st.title("🎓 Jumlah Penduduk Berdasarkan Tingkat Pendidikan")

    # Muat data dari Google Sheets
    df_pendidikan = load_pendidikan_data_from_gsheet()

    if not df_pendidikan.empty:
        # --- PERBAIKAN: Hilangkan .0 dari kolom 'No' dan pastikan tipe data sesuai ---
        if 'No' in df_pendidikan.columns:
            # Konversi kolom 'No' ke numerik, dengan errors='coerce' untuk mengubah non-angka menjadi NaN
            df_pendidikan['No'] = pd.to_numeric(df_pendidikan['No'], errors='coerce')
            # Kemudian, ubah NaN menjadi 0 (atau string kosong jika ingin barisnya tetap ada tapi No-nya kosong)
            # Lalu konversi ke integer jika bukan NaN, atau biarkan NaN untuk float atau non-numerik.
            # Karena Anda ingin menghilangkan .0, kita asumsikan nilainya harus bulat atau kosong.
            df_pendidikan['No'] = df_pendidikan['No'].apply(lambda x: int(x) if pd.notna(x) else None)
            # Untuk tampilan di Streamlit, kita bisa langsung menggunakan integer atau None.
            # Jika ada None, Streamlit akan menampilkannya sebagai kosong secara default.

        # --- Tampilkan Tabel Data ---
        st.subheader("Tabel Rincian Data Pendidikan")
        
        # --- LOGIKA TAMBAHAN UNTUK BARIS TOTAL SAJA ---
        df_display = df_pendidikan.copy() # Buat salinan untuk ditampilkan

        if 'Jumlah' in df_display.columns:
            # Pastikan 'Jumlah' adalah numerik sebelum dijumlahkan
            df_display['Jumlah'] = pd.to_numeric(df_display['Jumlah'], errors='coerce').fillna(0)
            total_jumlah = df_display['Jumlah'].sum()
            
            # Buat baris total
            total_row_dict = {col: '' for col in df_display.columns} # Inisialisasi semua kolom kosong
            # Isi kolom yang relevan
            total_row_dict['No'] = '' 
            total_row_dict['Pendidikan'] = 'TOTAL' 
            total_row_dict['Jumlah'] = total_jumlah 
            
            # Gabungkan baris total ke DataFrame tampilan
            df_display = pd.concat([df_display, pd.DataFrame([total_row_dict])], ignore_index=True)
        
        st.dataframe(df_display, use_container_width=True, hide_index=True) # Gunakan df_display dengan hide_index
        st.markdown("---")

        # --- Tampilkan Visualisasi dengan Altair ---
        st.subheader("Grafik Distribusi Pendidikan")
        
        chart_obj = get_pendidikan_chart() # Panggil fungsi pembuat grafik
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True) # Tampilkan grafik di halaman ini
        else:
            st.info("Tidak dapat menampilkan grafik karena data tidak tersedia atau tidak valid.")

        # --- Siapkan Data dan Tombol Download ---
        # Penting: Gunakan df_pendidikan ASLI (TANPA baris total) untuk export
        df_excel = to_excel(df_pendidikan)
        pdf_data = df_to_pdf(df_pendidikan)

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="Download as XLSX",
                data=df_excel,
                file_name="data_pendidikan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="data_pendidikan.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("Belum ada data pendidikan yang valid untuk divisualisasikan. Pastikan Google Sheet Anda dapat diakses dan memiliki data yang benar di worksheet 'Jumlah Penduduk (Pendidikan)' dengan kolom 'No', 'Pendidikan', dan 'Jumlah'.")

# Bagian ini hanya akan dieksekusi jika file ini dijalankan secara langsung, bukan sebagai modul yang diimpor oleh main.py.
if __name__ == '__main__':
    run()