# D:\visualisasi\pages\sarana_dan_prasarana.py

import streamlit as st
import pandas as pd
import altair as alt
import io
from fpdf import FPDF
# Pastikan ini mengimpor fungsi yang benar dari data_loader
from data_loader import load_sarana_prasarana_from_gsheet

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

def df_to_pdf(df):
    """
    Mengonversi DataFrame ke format PDF (BytesIO) menggunakan fpdf.
    """
    pdf = FPDF(orientation='L', unit='mm', format='A4') # Gunakan Landscape karena banyak kolom
    pdf.add_page()
    pdf.set_font("Arial", size=8)

    # Menambahkan judul
    pdf.cell(0, 10, txt="Data Sarana dan Prasarana", ln=True, align='C')
    pdf.ln(5)

    df_for_pdf = df.copy()
    # Kolom 'No' seharusnya sudah ada dan diubah namanya di data_loader
    if 'No' not in df_for_pdf.columns:
        df_for_pdf.insert(0, 'No', range(1, 1 + len(df_for_pdf)))
    
    # Menambahkan header kolom
    headers_display = ['No.', 'Tahun', 'Jenis Sarana dan Prasarana', 'Jumlah (Unit)']
    headers_df = ['No', 'Tahun', 'Jenis_Sarana_dan_Prasarana', 'Jumlah_Unit'] # Nama kolom setelah standardisasi di data_loader

    col_widths = {
        'No.': 15,
        'Tahun': 25,
        'Jenis Sarana dan Prasarana': 90,
        'Jumlah (Unit)': 40
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
    st.title("Data Sarana dan Prasarana")
    st.markdown("---")

    # Memuat data sarana dan prasarana
    df_sarana_prasarana = load_sarana_prasarana_from_gsheet()

    if not df_sarana_prasarana.empty:
        st.subheader("Tabel Data Sarana dan Prasarana")
        st.dataframe(df_sarana_prasarana)

        # --- Visualisasi Data ---
        st.subheader("Visualisasi Jumlah Sarana dan Prasarana")

        # Menggunakan kolom yang sudah distandarisasi oleh data_loader
        # 'Jenis_Sarana_dan_Prasarana', 'Jumlah_Unit'
        if 'Jenis_Sarana_dan_Prasarana' in df_sarana_prasarana.columns and 'Jumlah_Unit' in df_sarana_prasarana.columns:
            chart_sarana = alt.Chart(df_sarana_prasarana).mark_bar(
                cornerRadiusTopLeft=5,
                cornerRadiusTopRight=5
            ).encode(
                x=alt.X('Jumlah_Unit:Q', title='Jumlah Unit', axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
                y=alt.Y('Jenis_Sarana_dan_Prasarana:N', sort='-x', title='Jenis Sarana dan Prasarana',
                        axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
                color=alt.Color('Jumlah_Unit:Q', scale=alt.Scale(scheme='blues'), legend=None),
                tooltip=[
                    alt.Tooltip('Jenis_Sarana_dan_Prasarana:N', title='Jenis Sarana'),
                    alt.Tooltip('Jumlah_Unit:Q', title='Jumlah Unit', format='.0f')
                ]
            ).properties(
                title=alt.TitleParams(
                    text='Visualisasi Jumlah Sarana dan Prasarana',
                    fontSize=18,
                    anchor='start'
                ),
                width='container',
                height=400
            ).configure_axis(
                grid=False
            ).configure_view(
                stroke=None
            )
            st.altair_chart(chart_sarana, use_container_width=True)
        else:
            st.warning("Kolom 'Jenis Sarana dan Prasarana' atau 'Jumlah (Unit)' tidak ditemukan untuk visualisasi. Pastikan nama kolom di Google Sheet Anda sesuai.")


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