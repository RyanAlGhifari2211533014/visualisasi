# D:\visualisasi\pages\tenaga_kerja.py

import streamlit as st
import pandas as pd
import altair as alt
import io
from fpdf import FPDF
from data_loader import load_tenaga_kerja_from_gsheet

# --- Fungsi Helper untuk Konversi Data ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DataTenagaKerja')
    processed_data = output.getvalue()
    return processed_data

def df_to_pdf(df):
    pdf = FPDF(orientation='L', unit='mm', format='A4') # Ubah ke Landscape jika kolom banyak
    pdf.add_page()
    pdf.set_font("Arial", size=8)

    pdf.cell(0, 10, txt="Data Tenaga Kerja", ln=True, align='C')
    pdf.ln(5)

    df_for_pdf = df.copy()
    # Kolom 'No' seharusnya sudah ada dan diubah namanya di data_loader
    # Jika tidak, pastikan 'No' di DF Anda setelah preprocessing di data_loader
    if 'No' not in df_for_pdf.columns: # Periksa 'No' tanpa titik
        df_for_pdf.insert(0, 'No', range(1, 1 + len(df_for_pdf)))
    
    # --- PERUBAHAN PENTING DI SINI ---
    # Sesuaikan dengan nama kolom yang akan ditampilkan di PDF
    headers_display = ['No', 'Kriteria', 'Laki-Laki (Orang)', 'Perempuan (Orang)', 'Jumlah']
    # Sesuaikan dengan nama kolom yang sudah distandarisasi di DataFrame setelah data_loader
    headers_df = ['No', 'Kriteria', 'Laki-Laki_Orang', 'Perempuan_Orang', 'Jumlah'] 

    # Sesuaikan lebar kolom untuk mode Landscape
    col_widths = {
        'No': 15,
        'Kriteria': 60,
        'Laki-Laki (Orang)': 40,
        'Perempuan (Orang)': 40,
        'Jumlah': 30
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

    for row_index, row_data in df_for_pdf.iterrows():
        # Tambahkan pengecekan halaman baru jika baris terlalu panjang
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
        
        for i, header_df_name in enumerate(headers_df):
            header_display_name = headers_display[i]
            current_col_width = col_widths.get(header_display_name, 30)

            data = row_data[header_df_name]
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
    
    #untuk versi pyton 13.0.0
    #return pdf.output(dest='S').encode('utf-8')
    return bytes(pdf.output())

# --- Fungsi utama untuk halaman ini ---
def run():
    st.title("Data Tenaga Kerja")
    st.markdown("---")

    df_tenaga_kerja = load_tenaga_kerja_from_gsheet()

    if not df_tenaga_kerja.empty:
        st.subheader("Tabel Data Tenaga Kerja")
        # st.dataframe akan otomatis menampilkan semua kolom
        st.dataframe(df_tenaga_kerja)

        st.subheader("Distribusi Tenaga Kerja Berdasarkan Kriteria")

        # Visualisasi pie chart tetap menggunakan 'Kriteria' dan 'Jumlah'
        # karena itu yang ada di visualisasi asli Anda
        if 'Kriteria' in df_tenaga_kerja.columns and 'Jumlah' in df_tenaga_kerja.columns:
            chart_pie = alt.Chart(df_tenaga_kerja).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Jumlah", type="quantitative"),
                color=alt.Color(field="Kriteria", type="nominal", title='Kriteria Tenaga Kerja'),
                tooltip=[
                    alt.Tooltip('Kriteria', title='Kriteria'), 
                    alt.Tooltip('Jumlah', title='Jumlah', format='.0f') 
                ]
            ).properties(
                title="Distribusi Tenaga Kerja Berdasarkan Kriteria (Pie Chart)"
            )
            st.altair_chart(chart_pie, use_container_width=True)
        else:
            st.warning("Kolom 'Kriteria' atau 'Jumlah' tidak ditemukan untuk visualisasi pie chart. Pastikan nama kolom di Google Sheet Anda sesuai.")


        # --- Tombol Download ---
        st.markdown("---")
        st.subheader("Unduh Data")
        
        df_excel_data = to_excel(df_tenaga_kerja)
        pdf_data = df_to_pdf(df_tenaga_kerja)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download as XLSX",
                data=df_excel_data,
                file_name="data_tenaga_kerja.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col2:
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="data_tenaga_kerja.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("Belum ada data tenaga kerja yang valid untuk divisualisasikan. Pastikan Google Sheet Anda dapat diakses dan memiliki data yang benar di worksheet 'Tenaga Kerja' dengan kolom 'No.', 'Kriteria', 'Laki-Laki (Orang)', 'Perempuan (Orang)', dan 'Jumlah'.")

if __name__ == '__main__':
    run()

