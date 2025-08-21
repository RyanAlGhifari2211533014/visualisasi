import streamlit as st
import pandas as pd
import altair as alt
import io
from fpdf import FPDF
from data_loader import load_jenis_tanah_gsheet

alt.data_transformers.disable_max_rows()

# Fungsi to_excel dan df_to_pdf tidak diubah, biarkan seperti semula
def to_excel(df: pd.DataFrame):
    df_filtered = df.drop(columns=['Tanggal', 'Status', 'Total Luas Tanah (Ha)', 'Luas Desa/Kelurahan (Ha)'], errors='ignore')
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name='DataJenisTanah')
    return output.getvalue()

def df_to_pdf(df: pd.DataFrame):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, 'Data Jenis Tanah', 0, 1, 'C')
    pdf.ln(10)
    df_for_pdf = df.drop(columns=['Tanggal', 'Status', 'Total Luas Tanah (Ha)', 'Luas Desa/Kelurahan (Ha)'], errors='ignore')
    df_for_pdf.insert(0, 'No.', range(1, 1 + len(df_for_pdf)))
    pdf.set_font("Arial", "B", 8)
    effective_page_width = pdf.w - 2 * pdf.l_margin
    col_widths = {'No.': 10, 'Tanah Sawah (Ha)': 25, 'Tanah Kering (Ha)': 25, 'Tanah Basah (Ha)': 25, 'Tanah Perkebunan (Ha)': 30, 'Tanah Fasilitas Umum (Ha)': 30, 'Tanah Hutan (Ha)': 25}
    headers = df_for_pdf.columns.tolist()
    remaining_width = effective_page_width - sum(col_widths.get(h, 0) for h in headers)
    remaining_cols = len(headers) - sum(1 for h in headers if h in col_widths)
    default_col_width = remaining_width / remaining_cols if remaining_cols > 0 else 20
    if default_col_width < 10: default_col_width = 10
    y_start_headers = pdf.get_y()
    x_current = pdf.get_x()
    max_y_after_headers = y_start_headers
    for i, header in enumerate(headers):
        current_col_width = col_widths.get(header, default_col_width)
        pdf.set_xy(x_current, y_start_headers)
        pdf.multi_cell(current_col_width, 4, str(header).encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
        x_current += current_col_width
        max_y_after_headers = max(max_y_after_headers, pdf.get_y())
    pdf.set_y(max_y_after_headers)
    pdf.set_font("Arial", "", 7)
    for index, row in df_for_pdf.iterrows():
        for i, item in enumerate(row):
            header = headers[i]
            current_col_width = col_widths.get(header, default_col_width)
            formatted_item = str(item)
            if isinstance(item, (int, float)):
                if float(item).is_integer():
                    formatted_item = str(int(item))
                else:
                    formatted_item = f"{item:,.2f}"
            pdf.cell(current_col_width, 10, formatted_item.encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
        pdf.ln(10)
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, "Sumber: Kelurahan Kubu Marapalam", align='C')
    
    return bytes(pdf.output())
    

# <<< DIUBAH: Fungsi get_jenis_tanah_chart diperbarui sepenuhnya >>>
def get_jenis_tanah_chart():
    df_tanah = load_jenis_tanah_gsheet()
    if df_tanah.empty:
        return None

    land_cols = ['Tanah Sawah (Ha)', 'Tanah Kering (Ha)', 'Tanah Basah (Ha)', 'Tanah Perkebunan (Ha)', 'Tanah Fasilitas Umum (Ha)', 'Tanah Hutan (Ha)']
    existing_land_cols = [col for col in land_cols if col in df_tanah.columns]

    if existing_land_cols:
        df_melted = df_tanah[existing_land_cols].iloc[0:1].melt(var_name='Jenis Tanah', value_name='Luas (Ha)')
        df_melted['Jenis Tanah'] = df_melted['Jenis Tanah'].str.replace(' \\(Ha\\)', '', regex=True)
        
        chart = alt.Chart(df_melted).mark_bar(
            cornerRadius=5
        ).encode(
            x=alt.X('Luas (Ha):Q', title='Luas (Hektar)'),
            y=alt.Y('Jenis Tanah:N', sort='-x', title='Jenis Tanah'),
            color=alt.Color('Luas (Ha):Q',
                            scale=alt.Scale(scheme='blues'),
                            legend=None),
            tooltip=[
                alt.Tooltip('Jenis Tanah:N', title='Jenis Tanah'),
                alt.Tooltip('Luas (Ha):Q', format='.2f', title='Luas (Ha)')
            ]
        ).properties(
            title={
                "text": 'Perbandingan Luas Berbagai Jenis Tanah',
                "anchor": "start"
            }
        )
        return chart
    return None

def run():
    st.title("🗺️ Jenis Tanah")
    df_tanah = load_jenis_tanah_gsheet()
    if not df_tanah.empty:
        st.subheader("Tabel Luas tanah menurut Jenis dan Pemafaatan")
        df_display = df_tanah.drop(columns=['Tanggal', 'Total Luas Tanah (Ha)', 'Luas Desa/Kelurahan (Ha)', 'Status'], errors='ignore')
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.markdown("---")

        st.subheader("Grafik Perbandingan Luas Berbagai Jenis Tanah")
        chart_obj = get_jenis_tanah_chart()
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True)
        else:
            st.info("Tidak dapat menampilkan grafik.")

        df_excel = to_excel(df_tanah)
        pdf_data = df_to_pdf(df_tanah)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download as XLSX", df_excel, "data_jenis_tanah.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            st.download_button("Download as PDF", pdf_data, "data_jenis_tanah.pdf", "application/pdf", use_container_width=True)
    else:
        st.info("Belum ada data jenis tanah yang valid untuk divisualisasikan.")
