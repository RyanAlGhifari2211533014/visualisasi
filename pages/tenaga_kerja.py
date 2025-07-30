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
    pdf = FPDF(orientation='L', unit='mm', format='A4')  # Ubah ke Landscape jika kolom banyak
    pdf.add_page()
    pdf.set_font("Arial", size=8)

    pdf.cell(0, 10, txt="Data Tenaga Kerja", ln=True, align='C')
    pdf.ln(5)

    df_for_pdf = df.copy()

    if 'No' not in df_for_pdf.columns:  # Periksa 'No' tanpa titik
        df_for_pdf.insert(0, 'No', range(1, 1 + len(df_for_pdf)))

    headers_display = ['No', 'Kriteria', 'Laki-Laki (Orang)', 'Perempuan (Orang)', 'Jumlah']
    headers_df = ['No', 'Kriteria', 'Laki-Laki_Orang', 'Perempuan_Orang', 'Jumlah']

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

    return bytes(pdf.output())

# --- Fungsi utama untuk halaman ini ---
def get_tenaga_kerja_chart(df):
    if 'Kriteria' in df.columns and 'Jumlah' in df.columns:
        chart_pie = alt.Chart(df).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="Jumlah", type="quantitative"),
            color=alt.Color(field="Kriteria", type="nominal", title='Kriteria Tenaga Kerja'),
            tooltip=[
                alt.Tooltip('Kriteria', title='Kriteria'),
                alt.Tooltip('Jumlah', title='Jumlah', format='.0f')
            ]
        ).properties(
            title="Distribusi Tenaga Kerja Berdasarkan Kriteria (Pie Chart)"
        )
        return chart_pie
    else:
        return None

def run():
    st.title("Data Tenaga Kerja")
    st.markdown("---")

    # Memuat data tenaga kerja
    df_tenaga_kerja = load_tenaga_kerja_from_gsheet()

    if not df_tenaga_kerja.empty:
        st.subheader("Data Tenaga Kerja")
        st.dataframe(df_tenaga_kerja, use_container_width=True, hide_index=True)

        # --- Visualisasi Data ---
        chart_obj = get_tenaga_kerja_chart(df_tenaga_kerja)
        if chart_obj is not None:
            st.altair_chart(chart_obj, use_container_width=True)
        else:
            st.info("Tidak dapat menampilkan grafik karena data tidak tersedia atau tidak valid.")
            
        st.markdown("---")
        # --- Tombol Download ---
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
        # Pesan ini ditampilkan jika df_tenaga_kerja kosong setelah mencoba memuat data.
        st.info("Belum ada data tenaga kerja yang valid untuk divisualisasikan. Pastikan Google Sheet Anda dapat diakses dan memiliki data yang benar di worksheet 'Jumlah Penduduk (2020-2025)' dengan kolom 'Tahun', 'Jumlah Laki-Laki (orang)', 'Jumlah Perempuan (orang)', 'Jumlah Total (orang)', dan 'Jumlah Kepala Keluarga (KK)'.")

# Bagian ini hanya akan dieksekusi jika file ini dijalankan secara langsung, bukan sebagai modul yang diimpor oleh main.py.
if __name__ == '__main__':
    run()
