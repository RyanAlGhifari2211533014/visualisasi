import streamlit as st
import pandas as pd
import altair as alt 
import io
from fpdf import FPDF
import numpy as np
from data_loader import load_umkm_data_gsheet

alt.data_transformers.disable_max_rows()

# --- Fungsi Konversi (Tidak diubah) ---
def to_excel(df: pd.DataFrame):
    df_filtered = df.drop(columns=['No.'], errors='ignore')
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name='DataUMKM')
    return output.getvalue()

def df_to_pdf(df: pd.DataFrame):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, 'Data Jumlah Industri UMKM', 0, 1, 'C')
    pdf.ln(10)
    df_for_pdf = df.drop(columns=['No.'], errors='ignore')
    df_for_pdf.insert(0, 'No.', range(1, 1 + len(df_for_pdf))) 
    pdf.set_font("Arial", "B", 10)
    effective_page_width = pdf.w - 2 * pdf.l_margin
    col_widths = {'No.': 15, 'Jenis': 100, 'Jumlah': 40}
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
            if isinstance(item, (int, float)):
                if float(item).is_integer():
                    formatted_item = str(int(item))
                else:
                    formatted_item = str(item)
            pdf.cell(current_col_width, 10, formatted_item.encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
        pdf.ln()
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, "Sumber: Kelurahan Kubu Marapalam", align='C')
    
    #return bytes(pdf.output())
    return bytes(pdf.output(), 'utf-8')

# <<< DIUBAH: Fungsi get_umkm_chart diperbarui sepenuhnya >>>
def get_umkm_chart():
    df_umkm = load_umkm_data_gsheet()

    if df_umkm.empty:
        return None
    
    if 'Jenis' in df_umkm.columns and 'Jumlah' in df_umkm.columns:
        highlight = alt.selection_point(on='mouseover', fields=['Jenis'], empty=False)

        # Palet warna konsisten
        color_scheme = alt.condition(
            highlight,
            alt.value('#00A9E0'),  # Warna teal untuk sorotan
            alt.value('#00529B')   # Warna biru utama untuk dasar
        )

        chart = alt.Chart(df_umkm).mark_bar(
            cornerRadius=5,
        ).encode(
            x=alt.X('Jumlah:Q', title='Jumlah Unit Usaha'),
            y=alt.Y('Jenis:N', sort='-x', title='Jenis Industri'),
            color=color_scheme,
            tooltip=[
                alt.Tooltip('Jenis:N', title='Jenis Industri'),
                alt.Tooltip('Jumlah:Q', title='Jumlah', format='.0f')
            ]
        ).properties(
            title={
                "text": "Jumlah Unit Usaha per Jenis Industri UMKM",
                "anchor": "start"
            }
        ).add_params(
            highlight
        )
        return chart
    return None

def run():
    st.title("🏭 Jumlah Industri UMKM")
    df_umkm = load_umkm_data_gsheet()
    if not df_umkm.empty:
        # Pembersihan data (tidak diubah)
        for col in df_umkm.columns:
            df_umkm[col] = df_umkm[col].astype(str).str.strip().replace(r'^\s*$', np.nan, regex=True).replace('None', np.nan)
        df_umkm['Jenis'] = df_umkm['Jenis'].astype(object).fillna('Tidak Diketahui').astype(str)
        df_umkm['Jumlah'] = pd.to_numeric(df_umkm['Jumlah'], errors='coerce').fillna(0).astype(int)
        df_umkm = df_umkm[(df_umkm['Jenis'] != 'Tidak Diketahui') | (df_umkm['Jumlah'] != 0)].copy()
        if 'No.' in df_umkm.columns:
            df_umkm['No.'] = pd.to_numeric(df_umkm['No.'], errors='coerce').apply(lambda x: int(x) if pd.notna(x) else None)
        
        st.subheader("Tabel Rincian Industri UMKM")
        df_display = df_umkm.copy()
        if 'Jumlah' in df_display.columns:
            total_jumlah = df_display['Jumlah'].sum()
            total_row_dict = {col: '' for col in df_display.columns}
            total_row_dict['No.'] = ''
            total_row_dict['Jenis'] = 'TOTAL' 
            total_row_dict['Jumlah'] = total_jumlah 
            df_display = pd.concat([df_display, pd.DataFrame([total_row_dict])], ignore_index=True)
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.markdown("---")
        
        st.subheader("Grafik Jumlah Unit Usaha per Jenis Industri UMKM")
        chart_obj = get_umkm_chart()
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True)
        else:
            st.info("Tidak dapat menampilkan grafik.")
        
        df_excel = to_excel(df_umkm)
        pdf_data = df_to_pdf(df_umkm)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download as XLSX", df_excel, "data_umkm.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            st.download_button("Download as PDF", pdf_data, "data_umkm.pdf", "application/pdf", use_container_width=True)
    else:
        st.info("Belum ada data UMKM yang valid untuk divisualisasikan.")
