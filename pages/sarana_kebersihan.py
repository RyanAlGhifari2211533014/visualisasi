import streamlit as st
import pandas as pd
import altair as alt
import io
from fpdf import FPDF

# Pastikan ini mengimpor fungsi yang benar dari data_loader
from data_loader import load_sarana_kebersihan_from_gsheet

# Nonaktifkan batas baris Altair agar bisa memproses data besar
alt.data_transformers.disable_max_rows()

# --- Fungsi Helper untuk Konversi Data ---
def to_excel(df):
    """
    Mengonversi DataFrame ke format Excel (BytesIO) untuk diunduh.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DataSaranaKebersihan')
    processed_data = output.getvalue()
    return processed_data

def df_to_pdf(df):
    """
    Mengonversi DataFrame ke format PDF (BytesIO) menggunakan fpdf.
    """
    pdf = FPDF(orientation='P', unit='mm', format='A4') # Portrait karena hanya 3 kolom
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)

    # Menambahkan judul
    pdf.cell(0, 10, txt="Data Sarana Kebersihan", ln=True, align='C')
    pdf.ln(5)

    df_for_pdf = df.copy()
    # Kolom 'No' seharusnya sudah ada dan diubah namanya di data_loader
    if 'No' not in df_for_pdf.columns:
        df_for_pdf.insert(0, 'No', range(1, 1 + len(df_for_pdf)))
    
    # Menambahkan header kolom
    headers_display = ['No.', 'Jenis', 'Jumlah']
    # Perbaikan: Sesuaikan dengan nama kolom yang benar dari data_loader
    headers_df_map = {
        'No.': 'No',
        'Jenis': 'Jenis',
        'Jumlah': 'Jumlah'
    }

    col_widths = {
        'No.': 20,
        'Jenis': 100,
        'Jumlah': 40
    }
    
    y_start_headers = pdf.get_y()
    x_current = pdf.get_x()
    max_y_after_headers = y_start_headers

    for i, header_display in enumerate(headers_display):
        current_col_width = col_widths.get(header_display, 30)
        pdf.set_xy(x_current, y_start_headers)
        pdf.multi_cell(current_col_width, 5, str(header_display).encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
        x_current += current_col_width
        max_y_after_headers = max(max_y_after_headers, pdf.get_y())

    pdf.set_y(max_y_after_headers) 

    for row_index, row_data_original in df.iterrows(): # Gunakan df asli dari input fungsi
        # Buat dictionary dari row_data_original dengan nama kolom yang sudah distandarisasi
        row_data_processed = {headers_df_map[k]: row_data_original[k] for k in headers_df_map if k in row_data_original.index}
        
        # Tambahkan 'No' ke row_data_processed untuk baris ini
        row_data_processed['No'] = row_index + 1 # Nomor urut dimulai dari 1

        if pdf.get_y() + 10 > pdf.h - 20: # Jika mendekati batas bawah halaman
            pdf.add_page()
            pdf.set_y(20) # Mulai dari atas halaman baru
            x_current_new_page = pdf.get_x()
            for i, header_display in enumerate(headers_display): # Cetak header lagi di halaman baru
                current_col_width = col_widths.get(header_display, 30)
                pdf.set_xy(x_current_new_page, pdf.get_y())
                pdf.multi_cell(current_col_width, 5, str(header_display).encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
                x_current_new_page += current_col_width
            pdf.ln(5) # Spasi setelah header di halaman baru

        y_current_row = pdf.get_y()
        x_current_row = pdf.get_x()
        
        # Perbaikan: Iterasi berdasarkan headers_display untuk urutan yang benar
        for header_display_name in headers_display:
            header_df_name = headers_df_map[header_display_name] # Dapatkan nama kolom di DataFrame
            current_col_width = col_widths.get(header_display_name, 30)

            data = row_data_processed.get(header_df_name, '') # Ambil data, gunakan get() untuk menghindari KeyError
            
            # Menghilangkan ".0" untuk nilai numerik
            formatted_data = str(data)
            if isinstance(data, (int, float)):
                if float(data).is_integer():
                    formatted_data = str(int(data))
                else:
                    formatted_data = str(data)
            
            pdf.cell(current_col_width, 10, formatted_data.encode('latin-1', 'replace').decode('latin-1'), border=1, ln=False)
        pdf.ln(10)

    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, "Sumber: Kelurahan Kubu Marapalam", align='C')

    return bytes(pdf.output())

# --- FUNGSI BARU: Mendapatkan Objek Grafik untuk Halaman ini ---
def get_sarana_kebersihan_chart():
    """
    Membuat dan mengembalikan objek grafik Altair untuk Sarana Kebersihan.
    """
    df_sarana_kebersihan = load_sarana_kebersihan_from_gsheet()

    if df_sarana_kebersihan.empty:
        st.info("Data tidak tersedia untuk grafik ini.")
        return None
    
    # Menggunakan kolom 'Jenis' dan 'Jumlah' untuk visualisasi
    if 'Jenis' in df_sarana_kebersihan.columns and 'Jumlah' in df_sarana_kebersihan.columns:
        chart_bar = alt.Chart(df_sarana_kebersihan).mark_bar(
            cornerRadiusTopLeft=5,
            cornerRadiusTopRight=5
        ).encode(
            x=alt.X('Jumlah:Q', title='Jumlah Unit'),
            y=alt.Y('Jenis:N', sort='-x', title='Jenis Sarana Kebersihan'),
            color=alt.Color('Jumlah:Q', scale=alt.Scale(scheme='greens'), legend=None), # Ganti skema warna
            tooltip=[
                alt.Tooltip('Jenis:N', title='Jenis Sarana'), 
                alt.Tooltip('Jumlah:Q', title='Jumlah Unit', format='.0f')
            ]
        ).properties(
            title='Visualisasi Jumlah Sarana Kebersihan'
        ).configure_axis(
            grid=False
        ).configure_view(
            stroke=None
        )
        return chart_bar
    else:
        st.warning("Kolom 'Jenis' atau 'Jumlah' tidak ditemukan untuk visualisasi. Pastikan nama kolom di Google Sheet Anda sesuai.")
        return None

# --- Fungsi utama untuk halaman ini ---
def run():
    st.title("Data Sarana Kebersihan")
    st.markdown("---")

    # Memuat data sarana kebersihan
    df_sarana_kebersihan = load_sarana_kebersihan_from_gsheet()

    if not df_sarana_kebersihan.empty:
        st.subheader("Tabel Data Sarana Kebersihan")
        st.dataframe(df_sarana_kebersihan, use_container_width=True, hide_index=True)

        # --- Visualisasi Data ---
        st.subheader("Distribusi Sarana Kebersihan")

        chart_obj = get_sarana_kebersihan_chart()
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True)
        else:
            st.info("Tidak dapat menampilkan grafik karena data tidak tersedia atau tidak valid.")

        # --- Tombol Download ---
        st.markdown("---")
        st.subheader("Unduh Data")
        
        df_excel_data = to_excel(df_sarana_kebersihan)
        pdf_data = df_to_pdf(df_sarana_kebersihan)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download as XLSX",
                data=df_excel_data,
                file_name="data_sarana_kebersihan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col2:
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="data_sarana_kebersihan.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("Belum ada data sarana kebersihan yang valid untuk divisualisasikan. Pastikan Google Sheet Anda dapat diakses dan memiliki data yang benar di worksheet 'Sarana Kebersihan' dengan kolom 'No.', 'Jenis', dan 'Jumlah'.")

if __name__ == '__main__':
    run()