import streamlit as st
import pandas as pd
import altair as alt
import io
from fpdf import FPDF
from data_loader import load_jenis_pekerjaan_dominan_gsheet

alt.data_transformers.disable_max_rows()

def to_excel(df: pd.DataFrame):
    df_filtered = df.drop(columns=['Tanggal'], errors='ignore')
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name='DataPekerjaan')
    return output.getvalue()

def df_to_pdf(df: pd.DataFrame):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, 'Data Jenis Pekerjaan Dominan', 0, 1, 'C')
    pdf.ln(10)
    df_for_pdf = df.drop(columns=['Tanggal'], errors='ignore')
    if 'No.' not in df_for_pdf.columns:
        df_for_pdf.insert(0, 'No.', range(1, 1 + len(df_for_pdf))) 
    pdf.set_font("Arial", "B", 10)
    effective_page_width = pdf.w - 2 * pdf.l_margin
    col_widths = {'No.': 15, 'Jenis Pekerjaan': 100, 'Jumlah': 30}
    headers = df_for_pdf.columns.tolist()
    remaining_width = effective_page_width - sum(col_widths.get(h, 0) for h in headers)
    remaining_cols = len(headers) - sum(1 for h in headers if h in col_widths)
    default_col_width = remaining_width / remaining_cols if remaining_cols > 0 else 30
    if default_col_width < 10: default_col_width = 10
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
            formatted_item = str(item)
            if isinstance(item, (int, float)) and float(item).is_integer():
                formatted_item = str(int(item))
            pdf.cell(current_col_width, 10, formatted_item.encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
        pdf.ln()
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, "Sumber: Kelurahan Kubu Marapalam", align='C')
    return bytes(pdf.output())

# <<< DIUBAH: Fungsi get_jenis_pekerjaan_chart diperbarui sepenuhnya >>>
def get_jenis_pekerjaan_chart():
    df_pekerjaan = load_jenis_pekerjaan_dominan_gsheet()
    if df_pekerjaan.empty:
        return None
    
    if 'Jenis Pekerjaan' in df_pekerjaan.columns and 'Jumlah' in df_pekerjaan.columns:
        chart = alt.Chart(df_pekerjaan).mark_bar(
            cornerRadius=5
        ).encode(
            x=alt.X('Jumlah:Q', title='Jumlah Orang'),
            y=alt.Y('Jenis Pekerjaan:N', sort='-x', title='Jenis Pekerjaan'),
            # Menggunakan skema warna gradasi biru berdasarkan nilai
            color=alt.Color('Jumlah:Q', 
                            scale=alt.Scale(scheme='blues'), 
                            legend=None),
            tooltip=[
                alt.Tooltip('Jenis Pekerjaan:N', title='Jenis Pekerjaan'),
                alt.Tooltip('Jumlah:Q', title='Jumlah', format='.0f')
            ]
        ).properties(
            title={
                "text": 'Distribusi Jenis Pekerjaan Dominan',
                "anchor": "start"
            }
        )
        # Label teks di ujung bar dihapus agar UI lebih bersih
        return chart
    return None

def run():
    st.title("👷‍♂️ Jenis Pekerjaan Dominan")
    df_pekerjaan = load_jenis_pekerjaan_dominan_gsheet()
    if not df_pekerjaan.empty:
        st.subheader("Tabel Rincian Jenis Pekerjaan Dominan")
        df_display = df_pekerjaan.drop(columns=['Tanggal'], errors='ignore')
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.markdown("---")

        st.subheader("Grafik Distribusi Jenis Pekerjaan Dominan")
        chart_obj = get_jenis_pekerjaan_chart()
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True)
        else:
            st.info("Tidak dapat menampilkan grafik.")

        df_excel = to_excel(df_pekerjaan)
        pdf_data = df_to_pdf(df_pekerjaan)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download as XLSX", df_excel, "data_jenis_pekerjaan.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            st.download_button("Download as PDF", pdf_data, "data_jenis_pekerjaan.pdf", "application/pdf", use_container_width=True)
    else:
        st.info("Belum ada data jenis pekerjaan yang valid untuk divisualisasikan.")
