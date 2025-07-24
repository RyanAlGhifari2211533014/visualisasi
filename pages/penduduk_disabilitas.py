import streamlit as st
import pandas as pd
import altair as alt # Menggunakan Altair untuk visualisasi
import io
from fpdf import FPDF # Pastikan 'fpdf2' terinstal.

# Import fungsi pemuat data
from data_loader import load_disabilitas_data_gsheet

# Nonaktifkan batas baris Altair agar bisa memproses data besar
alt.data_transformers.disable_max_rows()

# --- Fungsi Konversi untuk Download ---

def to_excel(df: pd.DataFrame):
    """
    Mengonversi DataFrame Pandas menjadi file Excel di dalam memori.
    Akan mengecualikan kolom 'No.' dan 'Tanggal' jika ada.
    """
    # Buat salinan DataFrame dan hapus kolom yang tidak diinginkan
    df_filtered = df.drop(columns=['No.', 'Tanggal'], errors='ignore')
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: # Menggunakan xlsxwriter untuk Excel
        df_filtered.to_excel(writer, index=False, sheet_name='DataDisabilitas')
    processed_data = output.getvalue()
    return processed_data

def df_to_pdf(df: pd.DataFrame):
    """
    Mengonversi DataFrame Pandas menjadi file PDF untuk data Penduduk Disabilitas.
    Akan mengecualikan kolom 'No.' dan 'Tanggal', dan mempertahankan format sebelumnya.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4") # 'P' untuk Portrait
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    
    pdf.cell(0, 10, 'Data Penduduk Disabilitas', 0, 1, 'C')
    pdf.ln(10)

    # Buat salinan DataFrame dan hapus kolom yang tidak diinginkan
    df_for_pdf = df.drop(columns=['No.', 'Tanggal'], errors='ignore')
    
    # Perbaikan: Tambahkan kolom 'No' ke DataFrame untuk PDF sebagai nomor urut
    df_for_pdf.insert(0, 'No.', range(1, 1 + len(df_for_pdf))) 

    # Header Kolom Tabel
    pdf.set_font("Arial", "B", 8) # Mengurangi font header sedikit lagi
    effective_page_width = pdf.w - 2 * pdf.l_margin
    
    # Menentukan lebar kolom secara manual untuk kontrol yang lebih baik
    col_widths = {
        'No.': 15,
        'Jenis Cacat': 70, # Lebih lebar untuk jenis cacat
        'Laki-Laki (orang)': 35,
        'Perempuan (orang)': 35,
        'Jumlah (Orang)': 35
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
                    formatted_item = str(item) # Biarkan float jika ada desimal
            
            pdf.cell(current_col_width, 10, formatted_item.encode('latin-1', 'replace').decode('latin-1'), border=1, ln=False)
        pdf.ln(10) # Pindah ke baris baru setelah setiap baris data
    
    # Tambahkan teks sumber di bagian bawah tabel
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, "Sumber: Kelurahan Kubu Marapalam", align='C')

    return bytes(pdf.output())

# --- Fungsi utama untuk menjalankan halaman ---

def run():
    """
    Merender halaman 'Penduduk Disabilitas'.
    """
    st.title("♿ Penduduk Disabilitas")

    # Muat data dari Google Sheets
    df_disabilitas = load_disabilitas_data_gsheet()

    if not df_disabilitas.empty:
        # --- Tampilkan Tabel Data (tanpa kolom No., Tanggal) ---
        st.subheader("Tabel Rincian Data Disabilitas")
        df_display = df_disabilitas.drop(columns=['No.', 'Tanggal'], errors='ignore')
        st.dataframe(df_display, use_container_width=True)
        st.markdown("---")

        # --- Tampilkan Visualisasi dengan Altair ---
        st.subheader("Grafik Jumlah Penyandang Disabilitas Berdasarkan Jenis Kelamin")
        
        # Kolom-kolom yang akan divisualisasikan
        gender_cols = ['Laki-Laki (orang)', 'Perempuan (orang)']
        
        # Pastikan kolom 'Jenis Cacat' dan kolom gender ada
        if 'Jenis Cacat' in df_disabilitas.columns and all(col in df_disabilitas.columns for col in gender_cols):
            # Ubah data menjadi format long agar bisa divisualisasikan
            df_melted = df_disabilitas.melt(
                id_vars=['Jenis Cacat'],
                value_vars=gender_cols,
                var_name='Jenis Kelamin',
                value_name='Jumlah'
            )

            # Ganti nama kolom agar lebih user-friendly
            df_melted['Jenis Kelamin'] = df_melted['Jenis Kelamin'].replace({
                'Laki-Laki (orang)': 'Laki-laki',
                'Perempuan (orang)': 'Perempuan'
            })

            # Buat bar chart vertikal dengan offset agar bar laki-laki & perempuan terpisah
            chart = alt.Chart(df_melted).mark_bar().encode(
                x=alt.X('Jenis Cacat:N', title='Jenis Disabilitas', axis=alt.Axis(labelAngle=-45)),
                y=alt.Y('Jumlah:Q', title='Jumlah Orang'),
                color=alt.Color('Jenis Kelamin:N', title='Jenis Kelamin', scale=alt.Scale(range=['#1f77b4', '#ff7f0e'])), # Warna untuk Laki-laki/Perempuan
                xOffset='Jenis Kelamin:N', # Offset untuk memisahkan bar
                tooltip=[
                    alt.Tooltip('Jenis Cacat:N', title='Jenis Disabilitas'),
                    alt.Tooltip('Jenis Kelamin:N', title='Jenis Kelamin'),
                    alt.Tooltip('Jumlah:Q', title='Jumlah', format='.0f') # Format tanpa desimal
                ]
            ).properties(
                title='Jumlah Penyandang Disabilitas Berdasarkan Jenis Kelamin (Bar Terpisah)'
            )

            # Menambahkan label angka di atas setiap bar
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-5 # Jarak label dari batang
            ).encode(
                text=alt.Text('Jumlah:Q', format='.0f'),
                x=alt.X('Jenis Cacat:N'),
                y=alt.Y('Jumlah:Q'),
                color=alt.value("black"), # Warna teks
                xOffset='Jenis Kelamin:N'
            )

            final_chart = chart + text
            st.altair_chart(final_chart, use_container_width=True)
        else:
            st.warning("Kolom yang diperlukan ('Jenis Cacat', 'Laki-Laki (orang)', 'Perempuan (orang)') tidak ditemukan untuk visualisasi grafik. Pastikan nama kolom di Google Sheet Anda sesuai.")

        # --- Siapkan Data dan Tombol Download ---
        df_excel = to_excel(df_disabilitas) # df_disabilitas sudah dimuat dari GSheet
        pdf_data = df_to_pdf(df_disabilitas) # df_disabilitas sudah dimuat dari GSheet

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="Download as XLSX",
                data=df_excel,
                file_name="data_disabilitas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="data_disabilitas.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("Belum ada data disabilitas yang valid untuk divisualisasikan. Pastikan Google Sheet Anda dapat diakses dan memiliki data yang benar di worksheet 'Penduduk Disabilitas' dengan kolom yang diperlukan.")