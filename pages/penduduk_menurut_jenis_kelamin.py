import streamlit as st
import pandas as pd
import altair as alt
import io
from fpdf import FPDF

# Import fungsi pemuat data dari data_loader
from data_loader import load_penduduk_jenis_kelamin_gsheet

# Nonaktifkan batas baris Altair agar bisa memproses data besar
alt.data_transformers.disable_max_rows()

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
    # Perbaikan: Pastikan kolom 'No' ditambahkan jika belum ada
    if 'No' not in df_for_pdf.columns:
        df_for_pdf.insert(0, 'No', range(1, 1 + len(df_for_pdf)))
    
    # Menentukan header yang akan ditampilkan dan lebar kolomnya
    headers_display = ['No', 'RW', 'RT', 'Jumlah KK', 'Laki-Laki', 'Perempuan', 'Jumlah Penduduk']
    # Nama kolom yang sesuai di DataFrame (setelah standardisasi di data_loader)
    # Perbaikan: Gunakan nama kolom yang sudah distandarisasi di data_loader
    headers_df_map = {
        'No': 'NO',
        'RW': 'RW',
        'RT': 'RT',
        'Jumlah KK': 'Jumlah KK',
        'Laki-Laki': 'LAKI- LAKI',
        'Perempuan': 'PEREMPUAN',
        'Jumlah Penduduk': 'JUMLAH PENDUDUK'
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
        row_data_processed = {headers_df_map[k]: row_data_original[k] for k in headers_df_map if k in row_data_original.index}
        
        # Tambahkan 'No' ke row_data_processed untuk baris ini
        row_data_processed['No'] = row_index + 1 # Nomor urut dimulai dari 1

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

        y_current_row = pdf.get_y()
        x_current_row = pdf.get_x()
        
        # Perbaikan: Iterasi berdasarkan headers_display untuk urutan yang benar
        for header_display_name in headers_display:
            header_df_name = headers_df_map[header_display_name] # Dapatkan nama kolom di DataFrame
            current_col_width = col_widths.get(header_display_name, 30)

            data = row_data_processed.get(header_df_name, '') # Ambil data, gunakan get() untuk menghindari KeyError
            
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

    return bytes(pdf.output())

# --- FUNGSI BARU: Mendapatkan Objek Grafik untuk Halaman ini ---
def get_penduduk_jenis_kelamin_chart():
    """
    Membuat dan mengembalikan objek grafik Altair untuk Penduduk Menurut Jenis Kelamin.
    """
    df_penduduk_jk = load_penduduk_jenis_kelamin_gsheet()

    if df_penduduk_jk.empty:
        st.info("Data tidak tersedia untuk grafik ini.")
        return None
    
    # Pastikan kolom yang dibutuhkan ada untuk grafik
    # Perbaikan: Gunakan nama kolom yang sudah distandarisasi di data_loader: 'LAKI- LAKI', 'PEREMPUAN'
    if 'RW_RT' in df_penduduk_jk.columns and 'LAKI- LAKI' in df_penduduk_jk.columns and 'PEREMPUAN' in df_penduduk_jk.columns:
        # Melt DataFrame untuk visualisasi perbandingan jenis kelamin
        df_melted = df_penduduk_jk.melt(
            id_vars=['RW_RT'], 
            value_vars=['LAKI- LAKI', 'PEREMPUAN'], 
            var_name='Jenis_Kelamin', 
            value_name='Jumlah'
        )

        # Ganti nama kolom agar lebih user-friendly di visualisasi
        df_melted['Jenis_Kelamin'] = df_melted['Jenis_Kelamin'].replace({
            'LAKI- LAKI': 'Laki-laki',
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
        ).configure_axis(
            grid=False
        ).configure_view(
            stroke=None
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

        final_chart_grouped = chart + text
        
        # Chart Total Jumlah Penduduk per RW
        # Perbaikan: Pastikan kolom 'RW' dan 'JUMLAH PENDUDUK' ada di df_penduduk_jk
        if 'RW' in df_penduduk_jk.columns and 'JUMLAH PENDUDUK' in df_penduduk_jk.columns:
            chart_total_penduduk_rw = alt.Chart(df_penduduk_jk).mark_bar().encode(
                x=alt.X('RW:N', title='RW', axis=alt.Axis(labelFontSize=12, titleFontSize=14)),
                y=alt.Y('JUMLAH PENDUDUK:Q', title='Total Penduduk', axis=alt.Axis(labelFontSize=12, titleFontSize=14)), # Menggunakan nama standar
                color=alt.Color('JUMLAH PENDUDUK:Q', scale=alt.Scale(scheme='viridis'), legend=None),
                tooltip=[
                    alt.Tooltip('RW:N', title='RW'),
                    alt.Tooltip('JUMLAH PENDUDUK:Q', title='Total Penduduk', format='.0f'),
                    alt.Tooltip('JUMLAH KK:Q', title='Jumlah KK', format='.0f') 
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
            # Mengembalikan kedua chart dalam layer atau sebagai list
            # Untuk home.py, mungkin lebih baik mengembalikan satu objek layer atau VConcatChart
            # Untuk halaman ini, kita bisa mengembalikan VConcatChart
            return alt.VConcatChart(vconcat=[final_chart_grouped, chart_total_penduduk_rw])
        else:
            st.warning("Kolom 'RW' atau 'JUMLAH PENDUDUK' tidak ditemukan untuk visualisasi total penduduk per RW. Pastikan nama kolom di Google Sheet Anda sesuai.")
            return final_chart_grouped # Tetap kembalikan chart grouped jika total tidak bisa dibuat
    else:
        st.warning("Kolom yang diperlukan tidak ditemukan untuk visualisasi grafik. Pastikan nama kolom di Google Sheet Anda sesuai.")
        return None

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

        chart_obj = get_penduduk_jenis_kelamin_chart()
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True)
        else:
            st.info("Tidak dapat menampilkan grafik karena data tidak tersedia atau tidak valid.")

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