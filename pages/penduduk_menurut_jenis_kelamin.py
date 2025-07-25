# D:\visualisasi\pages\penduduk_menurut_jenis_kelamin.py

import streamlit as st
import pandas as pd
import altair as alt
import io
from fpdf import FPDF
from data_loader import load_penduduk_jenis_kelamin_from_gsheet

# --- Fungsi Helper untuk Konversi Data ---
def to_excel(df):
    """
    Mengonversi DataFrame ke format Excel (BytesIO) untuk diunduh.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DataPendudukJK')
    processed_data = output.getvalue()
    return processed_data

def df_to_pdf(df):
    """
    Mengonversi DataFrame ke format PDF (BytesIO) menggunakan fpdf.
    """
    pdf = FPDF(orientation='L', unit='mm', format='A4') # Gunakan Landscape
    pdf.add_page()
    pdf.set_font("Arial", size=8)

    # Menambahkan judul
    pdf.cell(0, 10, txt="Data Penduduk Menurut Jenis Kelamin", ln=True, align='C')
    pdf.ln(5)

    df_for_pdf = df.copy()
    # Kolom 'No' sudah distandarisasi di data_loader
    
    # Menambahkan header kolom
    headers_display = ['No', 'RW', 'RT', 'Jumlah KK', 'Laki-Laki', 'Perempuan', 'Jumlah Penduduk']
    # Nama kolom setelah standardisasi di data_loader
    headers_df = ['No', 'RW', 'RT', 'Jumlah_KK', 'LAKI_LAKI', 'PEREMPUAN', 'Jumlah_Penduduk'] 

    col_widths = {
        'No': 15,
        'RW': 20,
        'RT': 20,
        'Jumlah KK': 30,
        'Laki-Laki': 30,
        'Perempuan': 30,
        'Jumlah Penduduk': 40
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
        if pdf.get_y() + 10 > pdf.h - 20:
            pdf.add_page()
            pdf.set_y(20)
            x_current_new_page = pdf.get_x()
            for i, header_display in enumerate(headers_display):
                current_col_width = col_widths.get(header_display, 30)
                pdf.set_xy(x_current_new_page, pdf.get_y())
                pdf.multi_cell(current_col_width, 5, str(header_display).encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
                x_current_new_page += current_col_width
            pdf.ln(5)

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
    st.title("Data Penduduk Menurut Jenis Kelamin")
    st.markdown("---")

    df_penduduk_jk = load_penduduk_jenis_kelamin_from_gsheet()

    if not df_penduduk_jk.empty:
        st.subheader("Tabel Data Penduduk Menurut Jenis Kelamin")
        st.dataframe(df_penduduk_jk)

        # --- Visualisasi Data ---
        st.subheader("Perbandingan Jumlah Penduduk Laki-laki dan Perempuan per RT-RW")

        # Melt DataFrame untuk visualisasi perbandingan jenis kelamin
        # Menggunakan nama kolom yang sudah distandarisasi: 'LAKI_LAKI', 'PEREMPUAN'
        df_melted = df_penduduk_jk.melt(
            id_vars=['RT_RW'], # Kolom gabungan RT-RW sudah dibuat di data_loader
            value_vars=['LAKI_LAKI', 'PEREMPUAN'], 
            var_name='Jenis_Kelamin', 
            value_name='Jumlah'
        )

        # Ganti nama kolom agar lebih user-friendly di visualisasi
        df_melted['Jenis_Kelamin'] = df_melted['Jenis_Kelamin'].replace({
            'LAKI_LAKI': 'Laki-laki',
            'PEREMPUAN': 'Perempuan'
        })
        
        # Bar Chart Grouped: Laki-laki dan Perempuan per RT-RW
        chart = alt.Chart(df_melted).mark_bar(size=14).encode(
            x=alt.X('RT_RW:N', title='RT - RW', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Jumlah:Q', title='Jumlah Penduduk'),
            color=alt.Color('Jenis_Kelamin:N', title='Jenis Kelamin', scale=alt.Scale(scheme='set2')),
            xOffset='Jenis_Kelamin:N',
            tooltip=[
                alt.Tooltip('RT_RW:N', title='RT-RW'),
                alt.Tooltip('Jenis_Kelamin:N', title='Jenis Kelamin'),
                alt.Tooltip('Jumlah:Q', title='Jumlah', format='.0f')
            ]
        ).properties(
            title='👥 Jumlah Penduduk Laki-laki dan Perempuan per RT-RW',
            width=700, # Bisa disesuaikan atau pakai 'container'
            height=400
        ).configure_axis(
            grid=False
        ).configure_view(
            stroke=None
        )
        st.altair_chart(chart, use_container_width=True) # Menggunakan use_container_width=True untuk responsif

        st.markdown("---")
        st.subheader("Total Jumlah Penduduk per RW")
        chart_total_penduduk_rw = alt.Chart(df_penduduk_jk).mark_bar().encode(
            x=alt.X('RW:N', title='RW', axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
            y=alt.Y('Jumlah_Penduduk:Q', title='Total Penduduk', axis=alt.Axis(labelFontSize=12, titleFontSize=14)), # Menggunakan nama standar
            color=alt.Color('Jumlah_Penduduk:Q', scale=alt.Scale(scheme='viridis'), legend=None),
            tooltip=[
                alt.Tooltip('RW:N', title='RW'),
                alt.Tooltip('Jumlah_Penduduk:Q', title='Total Penduduk', format='.0f'),
                alt.Tooltip('Jumlah_KK:Q', title='Jumlah KK', format='.0f') 
            ]
        ).properties(
            title=alt.TitleParams(
                text='Distribusi Total Jumlah Penduduk per RW',
                fontSize=18,
                anchor='start'
            ),
            width='container',
            height=300
        ).configure_axis(
            grid=False
        ).configure_view(
            stroke=None
        )
        st.altair_chart(chart_total_penduduk_rw, use_container_width=True)


        # --- Tombol Download ---
        st.markdown("---")
        st.subheader("Unduh Data")
        
        df_excel_data = to_excel(df_penduduk_jk)
        pdf_data = df_to_pdf(df_penduduk_jk)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download as XLSX",
                data=df_excel_data,
                file_name="data_penduduk_jenis_kelamin.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col2:
            st.download_button(
                label="Download as PDF",
                data=pdf_data,
                file_name="data_penduduk_jenis_kelamin.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        st.info("Belum ada data penduduk menurut jenis kelamin yang valid untuk divisualisasikan. Pastikan Google Sheet Anda dapat diakses dan memiliki data yang benar di worksheet 'Penduduk Menurut Jenis Kelamin' dengan kolom 'NO', 'RW', 'RT', 'JUMLAH KK', 'LAKI- LAKI', 'PEREMPUAN', dan 'JUMLAH PENDUDUK'.")

if __name__ == '__main__':
    run()