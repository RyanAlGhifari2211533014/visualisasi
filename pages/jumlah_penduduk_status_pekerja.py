import streamlit as st
import pandas as pd
import altair as alt
import io
from fpdf import FPDF
from data_loader import load_status_pekerja_data_gsheet

alt.data_transformers.disable_max_rows()

# --- Fungsi Konversi (Tidak diubah) ---
def to_excel(df: pd.DataFrame):
    df_filtered = df.drop(columns=['No.'], errors='ignore')
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_filtered.to_excel(writer, index=False, sheet_name='DataStatusPekerja')
    return output.getvalue()

def df_to_pdf(df: pd.DataFrame):
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, 'Data Penduduk Berdasarkan Status Pekerjaan', 0, 1, 'C')
    pdf.ln(10)
    df_for_pdf = df.drop(columns=['No.'], errors='ignore')
    df_for_pdf.insert(0, 'No.', range(1, 1 + len(df_for_pdf))) 
    pdf.set_font("Arial", "B", 10)
    effective_page_width = pdf.w - 2 * pdf.l_margin
    col_widths = {'No.': 15, 'Kriteria': 100, 'Jumlah': 40}
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
    
    return bytes(pdf.output())
   
# <<< DIUBAH: Fungsi get_status_pekerja_chart diperbarui sepenuhnya >>>
def get_status_pekerja_chart():
    df_status_pekerja = load_status_pekerja_data_gsheet()

    if df_status_pekerja.empty:
        return None

    if 'Kriteria' in df_status_pekerja.columns and 'Jumlah' in df_status_pekerja.columns:
        
        # Palet warna konsisten
        color_range = ['#00529B', '#00A9E0', '#4CB5F5', '#89D6FB', '#BEE9FC']

        chart = alt.Chart(df_status_pekerja).mark_arc(
            innerRadius=70, # Membuat lubang di tengah
            outerRadius=110
        ).encode(
            theta=alt.Theta("Jumlah:Q", stack=True),
            color=alt.Color("Kriteria:N", 
                scale=alt.Scale(range=color_range),
                legend=alt.Legend(title="Status Pekerja")
            ),
            order=alt.Order("Jumlah:Q", sort="descending"),
            tooltip=[
                alt.Tooltip("Kriteria:N", title="Kriteria"),
                alt.Tooltip("Jumlah:Q", title="Jumlah", format=",.0f"),
            ]
        ).properties(
            title='Proporsi Penduduk Berdasarkan Status Pekerjaan'
        )
        return chart
    return None

def run():
    st.title("👨‍💼 Jumlah Penduduk Menurut Status Bekerja")
    df_status_pekerja = load_status_pekerja_data_gsheet()
    if not df_status_pekerja.empty:
        st.subheader("Tabel Rincian Status Pekerja")
        df_display = df_status_pekerja.drop(columns=['No.'], errors='ignore')
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        st.markdown("---")

        st.subheader("Grafik Proporsi Penduduk Berdasarkan Status Pekerjaan")
        chart_obj = get_status_pekerja_chart()
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True)
            total_penduduk = df_status_pekerja['Jumlah'].sum()
            st.markdown(f"**Total Penduduk: {total_penduduk:,.0f} Orang**")
        else:
            st.info("Tidak dapat menampilkan grafik.")

        st.markdown("---")
        df_excel = to_excel(df_status_pekerja)
        pdf_data = df_to_pdf(df_status_pekerja)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download as XLSX", df_excel, "data_status_pekerja.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            st.download_button("Download as PDF", pdf_data, "data_status_pekerja.pdf", "application/pdf", use_container_width=True)
    else:
        st.info("Belum ada data status pekerja yang valid untuk divisualisasikan.")

