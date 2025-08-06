import streamlit as st
import pandas as pd
import altair as alt
from data_loader import load_penduduk_2020_from_gsheet
import io
from fpdf import FPDF

alt.data_transformers.disable_max_rows()

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DataPenduduk')
    return output.getvalue()

def df_to_pdf(df):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", size=7)
    pdf.cell(0, 10, txt="Data Jumlah Penduduk", ln=True, align='C')
    pdf.ln(5)
    df_for_pdf = df.copy()
    df_for_pdf.insert(0, 'No', range(1, 1 + len(df_for_pdf)))
    headers = df_for_pdf.columns.tolist()
    col_widths = {'No': 15, 'Tahun': 25, 'Jumlah Laki-Laki (orang)': 35, 'Jumlah Perempuan (orang)': 35, 'Jumlah Total (orang)': 35, 'Jumlah Kepala Keluarga (KK)': 40}
    default_col_width = (pdf.w - 2 * pdf.l_margin - sum(col_widths.values())) / (len(headers) - len(col_widths)) if (len(headers) - len(col_widths)) > 0 else 30
    if len(headers) > 0:
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
        for row_data in df_for_pdf.itertuples(index=False):
            for i, data in enumerate(row_data):
                header = headers[i]
                current_col_width = col_widths.get(header, default_col_width)
                formatted_data = str(data)
                if isinstance(data, (int, float)) and float(data).is_integer():
                    formatted_data = str(int(data))
                pdf.cell(current_col_width, 10, formatted_data.encode('latin-1', 'replace').decode('latin-1'), border=1, ln=False)
            pdf.ln(10)
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, "Sumber: Kelurahan Kubu Marapalam", align='C')
    
    #return bytes(pdf.output())
    return bytes(pdf.output(), 'utf-8')

# <<< DIUBAH: Fungsi get_penduduk_tahun_chart diperbarui sepenuhnya >>>
def get_penduduk_tahun_chart():
    df_penduduk = load_penduduk_2020_from_gsheet()
    if df_penduduk.empty:
        return None

    if 'Tahun' in df_penduduk.columns and 'Jumlah Total (orang)' in df_penduduk.columns:
        nearest = alt.selection_point(nearest=True, on='mouseover', fields=['Tahun'], empty=False)

        line = alt.Chart(df_penduduk).mark_line(
            color='#004488',  # Warna biru tua
            strokeWidth=3
        ).encode(
            x=alt.X('Tahun:O', title='Tahun', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Jumlah Total (orang):Q', title='Jumlah Penduduk'),
        )

        points = line.mark_point(
            color='#66B2FF' # Warna titik biru muda
        ).encode(
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        )

        text = line.mark_text(align='left', dx=5, dy=-15, stroke='white', strokeWidth=3).encode(
            text=alt.condition(nearest, 'Jumlah Total (orang):Q', alt.value(' '), format=',.0f')
        )
        
        rules = alt.Chart(df_penduduk).mark_rule(color='gray').encode(
            x='Tahun:O',
        ).transform_filter(
            nearest
        )

        chart = alt.layer(line, points, rules, text).properties(
            title={"text": "Perkembangan Jumlah Penduduk", "anchor": "start"}
        ).add_params(nearest)
        return chart
    return None

def run():
    st.title("📈 Jumlah Penduduk")
    df_penduduk = load_penduduk_2020_from_gsheet()
    if not df_penduduk.empty:
        st.subheader("Data Jumlah Penduduk")
        st.dataframe(df_penduduk, use_container_width=True, hide_index=True)
        st.markdown("---")
        st.subheader("Tren Jumlah Penduduk dari Tahun ke Tahun")
        chart_obj = get_penduduk_tahun_chart()
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True)
        else:
            st.info("Tidak dapat menampilkan grafik.")
        
        if 'Tahun' in df_penduduk.columns and 'Jumlah Total (orang)' in df_penduduk.columns:
            tahun_terbaru = df_penduduk['Tahun'].max()
            jumlah_terbaru = df_penduduk[df_penduduk['Tahun'] == tahun_terbaru]['Jumlah Total (orang)'].iloc[0]
            st.markdown("---")
            st.subheader("Ringkasan Data")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label=f"Tahun Data Terakhir ({tahun_terbaru})", value=f"{jumlah_terbaru:,.0f} orang")
            with col2:
                if len(df_penduduk) > 1:
                    tahun_sebelumnya_data = df_penduduk[df_penduduk['Tahun'] < tahun_terbaru]['Tahun'].max()
                    if pd.notna(tahun_sebelumnya_data):
                        jumlah_sebelumnya = df_penduduk[df_penduduk['Tahun'] == tahun_sebelumnya_data]['Jumlah Total (orang)'].iloc[0]
                        perubahan = jumlah_terbaru - jumlah_sebelumnya
                        st.metric(label=f"Perubahan dari Tahun {tahun_sebelumnya_data}", value=f"{perubahan:,.0f} orang", delta=f"{perubahan:,.0f}")
        
        st.markdown("---")
        df_excel = to_excel(df_penduduk)
        pdf_data = df_to_pdf(df_penduduk)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download as XLSX", df_excel, "data_penduduk.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            st.download_button("Download as PDF", pdf_data, "data_penduduk.pdf", "application/pdf", use_container_width=True)
    else:
        st.info("Belum ada data jumlah penduduk yang valid untuk divisualisasikan.")
