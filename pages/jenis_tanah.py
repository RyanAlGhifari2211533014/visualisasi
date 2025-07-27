import streamlit as st
import pandas as pd
import altair as alt # Menggunakan Altair untuk visualisasi
import io
from fpdf import FPDF # Pastikan 'fpdf2' terinstal.

# Import fungsi pemuat data
from data_loader import load_jenis_tanah_gsheet

# Nonaktifkan batas baris Altair agar bisa memproses data besar
alt.data_transformers.disable_max_rows()

# --- Fungsi Konversi untuk Download ---

def to_excel(df: pd.DataFrame):
    """
    Mengonversi DataFrame Pandas menjadi file Excel di dalam memori.
    Akan mengecualikan kolom 'Tanggal' dan 'Status' jika ada.
    """
    # Buat salinan DataFrame dan hapus kolom yang tidak diinginkan
    df_filtered = df.drop(columns=['Tanggal', 'Status', 'Total Luas Tanah (Ha)', 'Luas Desa/Kelurahan (Ha)'], errors='ignore')
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: # Menggunakan xlsxwriter untuk Excel
        df_filtered.to_excel(writer, index=False, sheet_name='DataJenisTanah')
    processed_data = output.getvalue()
    return processed_data

def df_to_pdf(df: pd.DataFrame):
    """
    Mengonversi DataFrame Pandas menjadi file PDF untuk data Jenis Tanah.
    Akan mengecualikan kolom 'Tanggal' dan 'Status'.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4") # 'P' untuk Portrait
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    
    pdf.cell(0, 10, 'Data Jenis Tanah', 0, 1, 'C')
    pdf.ln(10)

    # Buat salinan DataFrame dan hapus kolom yang tidak diinginkan
    df_for_pdf = df.drop(columns=['Tanggal', 'Status', 'Total Luas Tanah (Ha)', 'Luas Desa/Kelurahan (Ha)'], errors='ignore')
    
    # Perbaikan: Tambahkan kolom 'No' ke DataFrame untuk PDF
    # Asumsi kolom 'No.' tidak ada di data asli, jadi kita tambahkan indeks
    df_for_pdf.insert(0, 'No.', range(1, 1 + len(df_for_pdf))) 

    # Header Kolom Tabel
    pdf.set_font("Arial", "B", 8) # Mengurangi font header sedikit lagi
    effective_page_width = pdf.w - 2 * pdf.l_margin
    
    # Menentukan lebar kolom secara manual untuk kontrol yang lebih baik
    # Sesuaikan lebar agar pas di Portrait
    col_widths = {
        'No.': 10,
        'Tanah Sawah (Ha)': 25,
        'Tanah Kering (Ha)': 25,
        'Tanah Basah (Ha)': 25,
        'Tanah Perkebunan (Ha)': 30,
        'Tanah Fasilitas Umum (Ha)': 30,
        'Tanah Hutan (Ha)': 25
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
        # Menggunakan MultiCell untuk header yang panjang agar bisa wrap text
        pdf.multi_cell(current_col_width, 4, str(header).encode('latin-1', 'replace').decode('latin-1'), border=1, align='C') # Ketinggian baris lebih kecil
        x_current += current_col_width
        max_y_after_headers = max(max_y_after_headers, pdf.get_y())
    
    pdf.set_y(max_y_after_headers) 

    # Data Baris Tabel
    pdf.set_font("Arial", "", 7) # Font untuk data, sedikit lebih kecil
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
                    formatted_item = f"{item:,.2f}" # Format float dengan 2 desimal jika ada
            
            pdf.cell(current_col_width, 10, formatted_item.encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
        pdf.ln(10) # Pindah ke baris baru setelah setiap baris data
    
    # Tambahkan teks sumber di bagian bawah tabel
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, "Sumber: Kelurahan Kubu Marapalam", align='C')

    return bytes(pdf.output())

# --- FUNGSI BARU: Mendapatkan Objek Grafik untuk Halaman ini ---
def get_jenis_tanah_chart():
    """
    Membuat dan mengembalikan objek grafik Altair untuk Jenis Tanah.
    """
    df_tanah = load_jenis_tanah_gsheet()

    if df_tanah.empty:
        st.info("Data tidak tersedia untuk grafik ini.")
        return None

    # Kolom-kolom jenis tanah yang akan divisualisasikan
    land_cols = [
        'Tanah Sawah (Ha)', 'Tanah Kering (Ha)', 'Tanah Basah (Ha)',
        'Tanah Perkebunan (Ha)', 'Tanah Fasilitas Umum (Ha)', 'Tanah Hutan (Ha)'
    ]
    
    # Pastikan kolom-kolom ini ada di DataFrame
    existing_land_cols = [col for col in land_cols if col in df_tanah.columns]

    if existing_land_cols:
        # Melt DataFrame untuk format yang cocok dengan bar chart Altair
        # Mengambil hanya baris pertama (data terbaru) atau rata-rata jika ada banyak baris per jenis tanah
        # Asumsi data per jenis tanah adalah satu baris per tanggal, kita ambil yang terbaru
        df_melted = df_tanah[existing_land_cols].iloc[0:1].melt(var_name='Jenis Tanah', value_name='Luas (Ha)')
        
        # Membersihkan nama jenis tanah (menghilangkan ' (Ha)')
        df_melted['Jenis Tanah'] = df_melted['Jenis Tanah'].str.replace(' \(Ha\)', '', regex=True)
        
        # Sortir data untuk visualisasi
        df_melted_sorted = df_melted.sort_values('Luas (Ha)', ascending=False)

        chart = alt.Chart(df_melted_sorted).mark_bar(
            cornerRadiusEnd=4
        ).encode(
            x=alt.X('Luas (Ha):Q', title='Luas (Hektar)'),
            y=alt.Y('Jenis Tanah:N', sort='-x', title='Jenis Tanah'),
            color=alt.Color('Jenis Tanah:N', legend=None),
            tooltip=[
                alt.Tooltip('Jenis Tanah:N', title='Jenis Tanah'),
                alt.Tooltip('Luas (Ha):Q', format='.2f', title='Luas (Ha)') # Format 2 desimal
            ]
        ).properties(
            title='Perbandingan Luas Berbagai Jenis Tanah'
        )

        # Menambahkan label angka di ujung bar
        text = chart.mark_text(
            align='left',
            baseline='middle',
            dx=3 # Jarak label dari batang
        ).encode(
            x='Luas (Ha):Q',
            y=alt.Y('Jenis Tanah:N', sort='-x'),
            text=alt.Text('Luas (Ha):Q', format='.2f') # Format 2 desimal
        )

        final_chart = chart + text
        return final_chart
    else:
        st.warning("Kolom jenis tanah yang diperlukan tidak ditemukan untuk visualisasi grafik. Pastikan nama kolom di Google Sheet Anda sesuai.")
        return None

# --- Fungsi utama untuk menjalankan halaman ---

def run():
    """
    Merender halaman 'Jenis Tanah'.
    """
    st.title("🗺️ Jenis Tanah")

    # Muat data dari Google Sheets
    df_tanah = load_jenis_tanah_gsheet()

    if not df_tanah.empty:
        # --- Tampilkan Tabel Data (tanpa kolom Tanggal, Total, Luas Desa, Status) ---
        st.subheader("Tabel Rincian Jenis Tanah")
        df_display = df_tanah.drop(columns=['Tanggal', 'Total Luas Tanah (Ha)', 'Luas Desa/Kelurahan (Ha)', 'Status'], errors='ignore')
        st.dataframe(df_display, use_container_width=True)
        st.markdown("---")

        # --- Tampilkan Visualisasi dengan Altair ---
        st.subheader("Grafik Perbandingan Luas Berbagai Jenis Tanah")
        
        chart_obj = get_jenis_tanah_chart() # Panggil fungsi pembuat grafik
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True)

            st.markdown(
                """
                <div style="background-color:#e6f3ff; padding: 10px; border-radius: 5px;">
                    <p style="font-size: 14px; color: #333;">
                        Grafik ini menunjukkan perbandingan luas berbagai jenis tanah di kelurahan.
                        Data ini penting untuk perencanaan tata ruang dan pengelolaan sumber daya.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.info("Tidak dapat menampilkan grafik karena data tidak tersedia atau tidak valid.")

        # --- Siapkan Data dan Tombol Download ---
        df_excel = to_excel(df_tanah) # df_tanah sudah dimuat dari GSheet
        pdf_data = df_to_pdf(df_tanah) # df_tanah sudah dimuat dari GSheet

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="Download as XLSX",
                data=df_excel,
                file_name="data_jenis_tanah.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="data_jenis_tanah.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("Belum ada data jenis tanah yang valid untuk divisualisasikan. Pastikan Google Sheet Anda dapat diakses dan memiliki data yang benar di worksheet 'Jenis Tanah' dengan kolom yang diperlukan.")