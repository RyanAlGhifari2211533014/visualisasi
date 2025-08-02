import streamlit as st
import pandas as pd
import altair as alt
import io
from fpdf import FPDF
from data_loader import load_disabilitas_data_gsheet

alt.data_transformers.disable_max_rows()

# Fungsi to_excel dan df_to_pdf tidak diubah, biarkan seperti semula
def to_excel(df: pd.DataFrame):
    df_filtered = df.drop(columns=['No.', 'Tanggal'], errors='ignore')
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name='DataDisabilitas')
    return output.getvalue()

def df_to_pdf(df: pd.DataFrame):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, 'Data Penduduk Disabilitas', 0, 1, 'C')
    pdf.ln(10)
    df_for_pdf = df.drop(columns=['No.', 'Tanggal'], errors='ignore')
    df_for_pdf.insert(0, 'No.', range(1, 1 + len(df_for_pdf)))
    pdf.set_font("Arial", "B", 8)
    effective_page_width = pdf.w - 2 * pdf.l_margin
    col_widths = {'No.': 15, 'Jenis Cacat': 70, 'Laki-Laki (orang)': 35, 'Perempuan (orang)': 35, 'Jumlah (Orang)': 35}
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
            if isinstance(item, (int, float)) and float(item).is_integer():
                formatted_item = str(int(item))
            pdf.cell(current_col_width, 10, formatted_item.encode('latin-1', 'replace').decode('latin-1'), border=1, ln=False)
        pdf.ln(10)
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, "Sumber: Kelurahan Kubu Marapalam", align='C')
    return bytes(pdf.output())

# <<< DIUBAH: Fungsi get_disabilitas_chart diperbarui sepenuhnya >>>
def get_disabilitas_chart():
    df_disabilitas = load_disabilitas_data_gsheet()
    if df_disabilitas.empty:
        return None
    
    gender_cols = ['Laki-Laki (orang)', 'Perempuan (orang)']
    if 'Jenis Cacat' in df_disabilitas.columns and all(col in df_disabilitas.columns for col in gender_cols):
        df_melted = df_disabilitas.melt(
            id_vars=['Jenis Cacat'],
            value_vars=gender_cols,
            var_name='Jenis Kelamin',
            value_name='Jumlah'
        )
        df_melted['Jenis Kelamin'] = df_melted['Jenis Kelamin'].replace({
            'Laki-Laki (orang)': 'Laki-laki',
            'Perempuan (orang)': 'Perempuan'
        })

        chart = alt.Chart(df_melted).mark_bar(
            cornerRadius=5,
            size=18
        ).encode(
            x=alt.X('Jenis Cacat:N', title='Jenis Disabilitas', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Jumlah:Q', title='Jumlah Orang'),
            color=alt.Color('Jenis Kelamin:N', title='Jenis Kelamin',
                            scale=alt.Scale(range=['#004488', '#66B2FF'])), # Biru tua & biru muda
            xOffset='Jenis Kelamin:N',
            tooltip=[
                alt.Tooltip('Jenis Cacat:N', title='Jenis Disabilitas'),
                alt.Tooltip('Jenis Kelamin:N', title='Jenis Kelamin'),
                alt.Tooltip('Jumlah:Q', title='Jumlah', format='.0f')
            ]
        ).properties(
            title={
                "text": 'Jumlah Penyandang Disabilitas Berdasarkan Jenis Kelamin',
                "anchor": "start"
            }
        )
        return chart
    return None

def run():
    st.title("♿ Penduduk Disabilitas")
    df_disabilitas = load_disabilitas_data_gsheet()
    if not df_disabilitas.empty:
        st.subheader("Tabel Rincian Data Disabilitas")
        df_display = df_disabilitas.drop(columns=['No.', 'Tanggal'], errors='ignore')
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.markdown("---")

        st.subheader("Grafik Jumlah Penyandang Disabilitas Berdasarkan Jenis Kelamin")
        chart_obj = get_disabilitas_chart()
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True)
        else:
            st.info("Tidak dapat menampilkan grafik.")

        df_excel = to_excel(df_disabilitas)
        pdf_data = df_to_pdf(df_disabilitas)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download as XLSX", df_excel, "data_disabilitas.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            st.download_button("Download as PDF", pdf_data, "data_disabilitas.pdf", "application/pdf", use_container_width=True)
    else:
        st.info("Belum ada data disabilitas yang valid untuk divisualisasikan.")
