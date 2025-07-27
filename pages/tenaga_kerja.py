import streamlit as st
import pandas as pd
import altair as alt
import io
from fpdf import FPDF
from data_loader import load_tenaga_kerja_from_gsheet

# Nonaktifkan batas baris Altair agar bisa memproses data besar
alt.data_transformers.disable_max_rows()

# --- Fungsi Helper untuk Konversi Data ---
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DataTenagaKerja')
    processed_data = output.getvalue()
    return processed_data

def df_to_pdf(df):
    pdf = FPDF(orientation='L', unit='mm', format='A4') # Ubah ke Landscape jika kolom banyak
    pdf.add_page()
    pdf.set_font("Arial", size=8)

    pdf.cell(0, 10, txt="Data Tenaga Kerja", ln=True, align='C')
    pdf.ln(5)

    df_for_pdf = df.copy()
    # Kolom 'No' seharusnya sudah ada dan diubah namanya di data_loader
    # Jika tidak, pastikan 'No' di DF Anda setelah preprocessing di data_loader
    if 'No' not in df_for_pdf.columns: # Periksa 'No' tanpa titik
        df_for_pdf.insert(0, 'No', range(1, 1 + len(df_for_pdf)))
    
    # --- PERUBAHAN PENTING DI SINI ---
    # Sesuaikan dengan nama kolom yang akan ditampilkan di PDF
    headers_display = ['No', 'Kriteria', 'Laki-Laki (Orang)', 'Perempuan (Orang)', 'Jumlah']
    # Sesuaikan dengan nama kolom yang sudah distandarisasi di DataFrame setelah data_loader
    headers_df_map = {
        'No': 'No',
        'Kriteria': 'Kriteria',
        'Laki-Laki (Orang)': 'Laki-Laki_Orang',
        'Perempuan (Orang)': 'Perempuan_Orang',
        'Jumlah': 'Jumlah'
    } 

    # Sesuaikan lebar kolom untuk mode Landscape
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

    for row_index, row_data_original in df.iterrows(): # Gunakan df asli dari input fungsi
        # Buat dictionary dari row_data_original dengan nama kolom yang sudah distandarisasi
        row_data_processed = {headers_df_map[k]: row_data_original[k] for k in headers_df_map if k in row_data_original.index}
        
        # Tambahkan 'No' ke row_data_processed untuk baris ini
        row_data_processed['No'] = row_index + 1 # Nomor urut dimulai dari 1

        if pdf.get_y() + 10 > pdf.h - 20: # Jika mendekati batas bawah halaman
            pdf.add_page()
            pdf.set_y(20) # Mulai dari atas halaman baru
            x_current_new_page = pdf.get_x()
            for i, header_display in enumerate(headers_display): # Cetak header lagi di halaman baru
                current_col_width = col_widths.get(header_display, 30)
                pdf.set_xy(x_current_new_page, pdf.get_y())
                pdf.multi_cell(current_col_width, 5, str(header_display).encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
                x_current_new_page += current_col_width
            pdf.ln(5) # Spasi setelah header di halaman baru

        y_current_row = pdf.get_y()
        x_current_row = pdf.get_x()
        
        # Perbaikan: Iterasi berdasarkan headers_display untuk urutan yang benar
        for header_display_name in headers_display:
            header_df_name = headers_df_map[header_display_name] # Dapatkan nama kolom di DataFrame
            current_col_width = col_widths.get(header_display_name, 30)

            data = row_data_processed.get(header_df_name, '') # Ambil data, gunakan get() untuk menghindari KeyError
            
            # Menghilangkan ".0" untuk nilai numerik
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

# --- FUNGSI BARU: Mendapatkan Objek Grafik untuk Halaman ini ---
def get_tenaga_kerja_chart():
    """
    Membuat dan mengembalikan objek grafik Altair untuk Data Tenaga Kerja.
    """
    df_tenaga_kerja = load_tenaga_kerja_from_gsheet()

    if df_tenaga_kerja.empty:
        st.info("Data tidak tersedia untuk grafik ini.")
        return None
    
    # Visualisasi pie chart tetap menggunakan 'Kriteria' dan 'Jumlah'
    if 'Kriteria' in df_tenaga_kerja.columns and 'Jumlah' in df_tenaga_kerja.columns:
        # Base chart untuk donut dengan perhitungan persentase
        base = alt.Chart(df_tenaga_kerja).encode(
            theta=alt.Theta("Jumlah:Q", stack=True)
        ).properties(
            title="Distribusi Tenaga Kerja Berdasarkan Kriteria"
        ).transform_joinaggregate(
            TotalJumlah=alt.JoinAggregateFieldDef(op='sum', field='Jumlah', as_='TotalJumlah')
        ).transform_calculate(
            percent="datum.Jumlah / datum.TotalJumlah"
        )

        # Donut chart
        pie = base.mark_arc(outerRadius=120, innerRadius=80).encode(
            color=alt.Color("Kriteria:N", title="Kriteria"),
            order=alt.Order("Jumlah:Q", sort="descending"),
            tooltip=[
                alt.Tooltip("Kriteria:N", title="Kriteria"),
                alt.Tooltip("Jumlah:Q", title="Jumlah", format=".0f"),
                alt.Tooltip("percent:Q", title="Persentase", format=".1%")
            ]
        )

        # Text labels for percentages
        text_percent = base.mark_text(radius=140).encode(
            text=alt.Text("percent:Q", format=".1%"),
            order=alt.Order("Jumlah:Q", sort="descending"),
            color=alt.value("black")
        )

        # Text labels for counts (jumlah orang)
        text_count = base.mark_text(radius=100).encode(
            text=alt.Text("Jumlah:Q", format=".0f"),
            order=alt.Order("Jumlah:Q", sort="descending"),
            color=alt.value("white")
        )
        
        final_chart = pie + text_percent + text_count
        return final_chart
    else:
        st.warning("Kolom 'Kriteria' atau 'Jumlah' tidak ditemukan untuk visualisasi pie chart. Pastikan nama kolom di Google Sheet Anda sesuai.")
        return None

# --- Fungsi utama untuk halaman ini ---
def run():
    st.title("Data Tenaga Kerja")
    st.markdown("---")

    df_tenaga_kerja = load_tenaga_kerja_from_gsheet()

    if not df_tenaga_kerja.empty:
        st.subheader("Tabel Data Tenaga Kerja")
        # st.dataframe akan otomatis menampilkan semua kolom
        st.dataframe(df_tenaga_kerja)

        st.subheader("Distribusi Tenaga Kerja Berdasarkan Kriteria")

        chart_obj = get_tenaga_kerja_chart()
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True)
        else:
            st.info("Tidak dapat menampilkan grafik karena data tidak tersedia atau tidak valid.")


        # --- Tombol Download ---
        st.markdown("---")
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
        st.info("Belum ada data tenaga kerja yang valid untuk divisualisasikan. Pastikan Google Sheet Anda dapat diakses dan memiliki data yang benar di worksheet 'Tenaga Kerja' dengan kolom 'No.', 'Kriteria', 'Laki-Laki (Orang)', 'Perempuan (Orang)', dan 'Jumlah'.")

if __name__ == '__main__':
    run()