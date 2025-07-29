import streamlit as st
import pandas as pd
import altair as alt
import io
from fpdf import FPDF

# Import fungsi pemuat data dari data_loader
# Pastikan file data_loader.py berada di direktori yang sama atau dapat diakses
from data_loader import load_penduduk_jenis_kelamin_gsheet

# Nonaktifkan batas baris Altair agar bisa memproses data besar
alt.data_transformers.disable_max_rows()

# --- Fungsi Helper untuk Konversi Data ---
def to_excel(df: pd.DataFrame):
    """
    Mengonversi DataFrame ke format Excel (BytesIO) untuk diunduh.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DataPendudukJK')
    processed_data = output.getvalue()
    return processed_data

def df_to_pdf(df: pd.DataFrame):
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
    # Perbaikan: Pastikan kolom 'No' ditambahkan jika belum ada
    if 'No' not in df_for_pdf.columns:
        df_for_pdf.insert(0, 'No', range(1, 1 + len(df_for_pdf)))
    
    # Menentukan header yang akan ditampilkan dan lebar kolomnya
    # Penting: Gunakan nama kolom yang sudah distandarisasi oleh data_loader.py
    headers_display = ['No', 'RW', 'RT', 'Jumlah KK', 'Laki-Laki', 'Perempuan', 'Jumlah Penduduk']
    # Pemetaan nama kolom di DataFrame (setelah standardisasi di data_loader)
    headers_df_map = {
        'No': 'No', # 'No' sudah dibuat di df_for_pdf.insert
        'RW': 'RW',
        'RT': 'RT',
        'Jumlah KK': 'Jumlah_KK', # Nama kolom setelah direname di data_loader
        'Laki-Laki': 'LAKI_LAKI', # Nama kolom setelah direname di data_loader
        'Perempuan': 'PEREMPUAN', # Nama kolom setelah direname di data_loader
        'Jumlah Penduduk': 'Jumlah_Penduduk' # Nama kolom setelah direname di data_loader
    }

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

    # Data Baris Tabel
    pdf.set_font("Arial", "", 7) # Font untuk data, sedikit lebih kecil
    for row_index, row_data_original in df.iterrows(): # Gunakan df asli dari input fungsi
        # Buat dictionary dari row_data_original dengan nama kolom yang sudah distandarisasi
        row_data_for_display = {}
        for display_header, df_column_name in headers_df_map.items():
            if df_column_name in row_data_original.index:
                row_data_for_display[display_header] = row_data_original[df_column_name]
            elif display_header == 'No': # Handle 'No' column separately
                row_data_for_display['No'] = row_index + 1

        if pdf.get_y() + 10 > pdf.h - 20: # Cek apakah perlu halaman baru
            pdf.add_page()
            pdf.set_y(20)
            x_current_new_page = pdf.get_x()
            for i, header_display in enumerate(headers_display):
                current_col_width = col_widths.get(header_display, 30)
                pdf.set_xy(x_current_new_page, pdf.get_y())
                pdf.multi_cell(current_col_width, 5, str(header_display).encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
                x_current_new_page += current_col_width
            pdf.ln(5)

        # Perbaikan: Iterasi berdasarkan headers_display untuk urutan yang benar
        for header_display_name in headers_display:
            current_col_width = col_widths.get(header_display_name, 30)

            # Ambil data dari dictionary yang sudah disiapkan
            data = row_data_for_display.get(header_display_name, '')
            
            # Perbaikan: Menghilangkan ".0" untuk nilai numerik
            formatted_data = str(data)
            if isinstance(data, (int, float)):
                if float(data).is_integer():
                    formatted_data = str(int(data))
                else:
                    formatted_data = str(data)
            
            pdf.cell(current_col_width, 10, formatted_data.encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
        pdf.ln(10)

    pdf.set_y(pdf.get_y() + 5)
    pdf.set_font("Arial", size=8)
    pdf.cell(0, 10, "Sumber: Kelurahan Kubu Marapalam", align='C')
    
    #return pdf.output(dest='S').encode('latin-1')
    return bytes(pdf.output())

# --- FUNGSI BARU: Mendapatkan Objek Grafik untuk Halaman ini ---
def get_penduduk_jenis_kelamin_chart1(df_penduduk_jk: pd.DataFrame):
    """
    Membuat dan mengembalikan objek grafik Altair untuk Penduduk Menurut Jenis Kelamin.
    Menerima DataFrame sebagai argumen.
    """
    if df_penduduk_jk.empty:
        st.info("Data tidak tersedia untuk grafik ini.")
    
    # Pastikan kolom yang dibutuhkan ada untuk grafik
    # PENTING: Gunakan nama kolom yang sudah distandarisasi oleh data_loader.py
    if 'RW_RT' in df_penduduk_jk.columns and 'LAKI_LAKI' in df_penduduk_jk.columns and 'PEREMPUAN' in df_penduduk_jk.columns:
        # Melt DataFrame untuk visualisasi perbandingan jenis kelamin
        df_melted = df_penduduk_jk.melt(
            id_vars=['RW_RT'], 
            value_vars=['LAKI_LAKI', 'PEREMPUAN'], # <-- Gunakan nama kolom yang sudah direname
            var_name='Jenis_Kelamin', 
            value_name='Jumlah'
        )

        # Ganti nama kolom agar lebih user-friendly di visualisasi
        df_melted['Jenis_Kelamin'] = df_melted['Jenis_Kelamin'].replace({
            'LAKI_LAKI': 'Laki-laki', # <-- Gunakan nama kolom yang sudah direname
            'PEREMPUAN': 'Perempuan'
        })
        
        # Bar Chart Grouped: Laki-laki dan Perempuan per RT-RW
        chart = alt.Chart(df_melted).mark_bar(size=14).encode(
            x=alt.X('RW_RT:N', title='RW - RT', axis=alt.Axis(labelAngle=-45)),
            y=alt.Y('Jumlah:Q', title='Jumlah Penduduk'),
            color=alt.Color('Jenis_Kelamin:N', title='Jenis Kelamin', scale=alt.Scale(scheme='set2')),
            xOffset='Jenis_Kelamin:N',
            tooltip=[
                alt.Tooltip('RW_RT:N', title='RW-RT'),
                alt.Tooltip('Jenis_Kelamin:N', title='Jenis Kelamin'),
                alt.Tooltip('Jumlah:Q', title='Jumlah', format='.0f')
            ]
        ).properties(
            title='👥 Jumlah Penduduk Laki-laki dan Perempuan per RW-RT',
            width=700, # Bisa disesuaikan atau pakai 'container'
            height=400
        )
        
        # Menambahkan label angka di atas setiap bar
        text = chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-5 # Jarak label dari batang
        ).encode(
            text=alt.Text('Jumlah:Q', format='.0f'),
            x=alt.X('RW_RT:N'),
            y=alt.Y('Jumlah:Q'),
            color=alt.value("black"), # Warna teks
            xOffset='Jenis_Kelamin:N'
        )
        return chart

# def get_penduduk_jenis_kelamin_chart2(df_penduduk_jk: pd.DataFrame):
#         # Chart Total Jumlah Penduduk per RW
#         # PENTING: Gunakan nama kolom yang sudah distandarisasi oleh data_loader.py
#         if 'RW' in df_penduduk_jk.columns and 'Jumlah_Penduduk' in df_penduduk_jk.columns:
#             chart_total_penduduk_rw = alt.Chart(df_penduduk_jk).mark_bar().encode(
#                 x=alt.X('RW:N', title='RW', axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
#                 y=alt.Y('Jumlah_Penduduk:Q', title='Total Penduduk', axis=alt.Axis(labelFontSize=12, titleFontSize=14)), # <-- Gunakan nama kolom yang sudah direname
#                 color=alt.Color('Jumlah_Penduduk:Q', scale=alt.Scale(scheme='viridis'), legend=None), # <-- Gunakan nama kolom yang sudah direname
#                 tooltip=[
#                     alt.Tooltip('RW:N', title='RW'),
#                     alt.Tooltip('Jumlah_Penduduk:Q', title='Total Penduduk', format='.0f'), # <-- Gunakan nama kolom yang sudah direname
#                     alt.Tooltip('Jumlah_KK:Q', title='Jumlah KK', format='.0f') # <-- Gunakan nama kolom yang sudah direname
#                 ]
#             ).properties(
#                 title=alt.TitleParams(
#                     text='Distribusi Total Jumlah Penduduk per RW',
#                     fontSize=18,
#                     anchor='start'
#                 ),
#                 width='container',
#                 height=300
#             )
#             return  chart_total_penduduk_rw
#         else:
#             st.warning("Kolom 'RW' atau 'Jumlah_Penduduk' tidak ditemukan untuk visualisasi total penduduk per RW. Pastikan nama kolom di Google Sheet Anda sesuai.")

# --- Fungsi utama untuk halaman ini ---
def run():
    st.title("Data Penduduk Menurut Jenis Kelamin")
    st.markdown("---")
    
    # Muat data terlebih dahulu
    df_penduduk_jk = load_penduduk_jenis_kelamin_gsheet()
    
    if not df_penduduk_jk.empty:
        st.subheader("Tabel Data Penduduk Menurut Jenis Kelamin")
        st.dataframe(df_penduduk_jk, use_container_width=True) # Tambahkan use_container_width
        st.markdown("---")

        # --- Visualisasi Data ---
        st.subheader("Perbandingan Jumlah Penduduk Laki-laki dan Perempuan per RT-RW")

        # Panggil fungsi pembuat grafik dengan DataFrame yang sudah dimuat
        chart_obj = get_penduduk_jenis_kelamin_chart1(df_penduduk_jk)
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True)
        else:
            st.info("Tidak dapat menampilkan grafik karena data tidak tersedia atau tidak valid.")

        st.markdown("---")
        st.subheader("Total Jumlah Penduduk per RW")

        # chart_obj = get_penduduk_jenis_kelamin_chart2(df_penduduk_jk)
        # if chart_obj:
        #     st.altair_chart(chart_obj, use_container_width=True)
        # else:
        #     st.info("Tidak dapat menampilkan grafik karena data tidak tersedia atau tidak valid.")


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
