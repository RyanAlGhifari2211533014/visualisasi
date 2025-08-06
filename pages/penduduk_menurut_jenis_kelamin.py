import streamlit as st
import pandas as pd
import altair as alt
import io
from fpdf import FPDF
from data_loader import load_penduduk_jenis_kelamin_gsheet

alt.data_transformers.disable_max_rows()

def to_excel(df: pd.DataFrame):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DataPendudukJK')
    return output.getvalue()

def df_to_pdf(df: pd.DataFrame):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt="Data Penduduk Menurut Jenis Kelamin", ln=True, align='C')
    pdf.ln(5)
    headers_df = ['No', 'RW', 'RT', 'Jumlah_KK', 'LAKI_LAKI', 'PEREMPUAN', 'Jumlah_Penduduk']
    headers_display = ['No', 'RW', 'RT', 'Jumlah KK', 'Laki-Laki', 'Perempuan', 'Jumlah Penduduk']
    col_widths = {'No': 15, 'RW': 20, 'RT': 20, 'Jumlah KK': 35, 'Laki-Laki': 35, 'Perempuan': 35, 'Jumlah Penduduk': 45}
    pdf.set_font("Arial", "B", 10)
    for i, header_text in enumerate(headers_display):
        width = col_widths[header_text]
        pdf.cell(width, 10, header_text, border=1, align='C')
    pdf.ln()
    pdf.set_font("Arial", "", 10)
    for index, row in df.iterrows():
        for i, header_display_text in enumerate(headers_display):
            width = col_widths[header_display_text]
            df_col_name = headers_df[i]
            data = row[df_col_name]
            formatted_data = str(data)
            if isinstance(data, (int, float)) and float(data).is_integer():
                formatted_data = str(int(data))
            pdf.cell(width, 10, formatted_data.encode('latin-1', 'replace').decode('latin-1'), border=1)
        pdf.ln()
    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font("Arial", "I", 8)
    pdf.cell(0, 10, "Sumber: Kelurahan Kubu Marapalam", align='C')
    
    return bytes(pdf.output())
   

# <<< DIUBAH: Fungsi get_penduduk_jenis_kelamin_chart1 diperbarui sepenuhnya >>>
def get_penduduk_jenis_kelamin_chart1(df_penduduk_jk: pd.DataFrame):
    if df_penduduk_jk.empty:
        return None
    
    if 'RW_RT' in df_penduduk_jk.columns and 'LAKI_LAKI' in df_penduduk_jk.columns and 'PEREMPUAN' in df_penduduk_jk.columns:
        df_melted = df_penduduk_jk.melt(
            id_vars=['RW_RT'], 
            value_vars=['LAKI_LAKI', 'PEREMPUAN'],
            var_name='Jenis_Kelamin', 
            value_name='Jumlah'
        )
        df_melted['Jenis_Kelamin'] = df_melted['Jenis_Kelamin'].replace({'LAKI_LAKI': 'Laki-laki', 'PEREMPUAN': 'Perempuan'})
        
        chart = alt.Chart(df_melted).mark_bar(size=14).encode(
            x=alt.X('RW_RT:N', title='RW - RT', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Jumlah:Q', title='Jumlah Penduduk'),
            # Menggunakan dua warna biru yang berbeda
            color=alt.Color('Jenis_Kelamin:N', title='Jenis Kelamin', 
                            scale=alt.Scale(range=['#004488', '#66B2FF'])), # Biru tua dan biru muda
            xOffset='Jenis_Kelamin:N',
            tooltip=[
                alt.Tooltip('RW_RT:N', title='RW-RT'),
                alt.Tooltip('Jenis_Kelamin:N', title='Jenis Kelamin'),
                alt.Tooltip('Jumlah:Q', title='Jumlah', format='.0f')
            ]
        ).properties(
            title={
                "text": 'Jumlah Penduduk Laki-laki dan Perempuan per RW-RT',
                "anchor": "start"
            }
        )
        # Label teks di atas bar dihapus agar UI lebih bersih
        return chart
    return None

def run():
    st.title("♀️ /♂️ Penduduk Menurut Jenis Kelamin")
    df_penduduk_jk = load_penduduk_jenis_kelamin_gsheet()
    if not df_penduduk_jk.empty:
        st.subheader("Tabel Data Penduduk Menurut Jenis Kelamin")
        st.dataframe(df_penduduk_jk, use_container_width=True, hide_index=True)
        st.markdown("---")

        st.subheader("Perbandingan Jumlah Penduduk Laki-laki dan Perempuan per RT-RW")
        chart_obj = get_penduduk_jenis_kelamin_chart1(df_penduduk_jk)
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True)
        else:
            st.info("Tidak dapat menampilkan grafik.")

        st.markdown("---")
        df_excel_data = to_excel(df_penduduk_jk)
        pdf_data = df_to_pdf(df_penduduk_jk)
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download as XLSX", df_excel_data, "data_penduduk_jenis_kelamin.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            st.download_button("Download as PDF", pdf_data, "data_penduduk_jenis_kelamin.pdf", "application/pdf", use_container_width=True)
    else:
        st.info("Belum ada data penduduk menurut jenis kelamin yang valid untuk divisualisasikan.")
