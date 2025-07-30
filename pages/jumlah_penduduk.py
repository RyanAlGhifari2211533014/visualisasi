import streamlit as st
import pandas as pd
import altair as alt # Asumsi Anda menggunakan Altair untuk visualisasi
from data_loader import load_penduduk_2020_from_gsheet # Impor fungsi dari data_loader.py

import io # Diperlukan untuk BytesIO
from fpdf import FPDF # Diperlukan untuk menghasilkan PDF. Pastikan 'fpdf2' terinstal.

# Nonaktifkan batas baris Altair agar bisa memproses data besar
alt.data_transformers.disable_max_rows()

# --- Fungsi Helper untuk Konversi Data ---
def to_excel(df):
    """
    Mengonversi DataFrame ke format Excel (BytesIO) untuk diunduh.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='DataPenduduk')
    processed_data = output.getvalue()
    return processed_data

def df_to_pdf(df):
    """
    Mengonversi DataFrame ke format PDF (BytesIO) menggunakan fpdf.
    """
    # Mengubah orientasi halaman menjadi Portrait ('P')
    # Mengurangi ukuran font agar lebih banyak konten muat
    pdf = FPDF(orientation='P', unit='mm', format='A4') # 'P' for Portrait
    pdf.add_page()
    pdf.set_font("Arial", size=7) # Mengurangi ukuran font

    # Menambahkan judul
    # Lebar halaman A4 Portrait adalah 210mm, margin default 10mm di setiap sisi
    pdf.cell(0, 10, txt="Data Jumlah Penduduk", ln=True, align='C') # Lebar 0 agar cell mengambil sisa lebar halaman
    pdf.ln(5) # Spasi

    # Perbaikan: Tambahkan kolom 'No' ke DataFrame untuk PDF
    df_for_pdf = df.copy()
    df_for_pdf.insert(0, 'No', range(1, 1 + len(df_for_pdf))) # Tambahkan kolom 'No' di awal

    # Menambahkan header kolom
    headers = df_for_pdf.columns.tolist() # Gunakan header dari DataFrame yang sudah ada kolom 'No'
    
    # Menentukan lebar kolom secara manual untuk kontrol yang lebih baik di mode Portrait
    # Total lebar area yang bisa dicetak A4 Portrait = 210 - (2 * 10) = 190mm
    # Sesuaikan lebar kolom agar totalnya tidak melebihi lebar area yang bisa dicetak
    col_widths = {
        'No': 15, # Lebar untuk kolom nomor
        'Tahun': 25,
        'Jumlah Laki-Laki (orang)': 35,
        'Jumlah Perempuan (orang)': 35,
        'Jumlah Total (orang)': 35,
        'Jumlah Kepala Keluarga (KK)': 40
    }
    
    # Fallback untuk kolom yang tidak didefinisikan secara eksplisit
    default_col_width = (pdf.w - 2 * pdf.l_margin - sum(col_widths.values())) / (len(headers) - len(col_widths)) if (len(headers) - len(col_widths)) > 0 else 30


    if len(headers) > 0:
        # Cetak header
        y_start_headers = pdf.get_y()
        x_current = pdf.get_x()
        max_y_after_headers = y_start_headers # Lacak posisi Y terendah yang dicapai oleh header

        for i, header in enumerate(headers):
            current_col_width = col_widths.get(header, default_col_width)
            # Menggunakan MultiCell untuk header yang panjang agar bisa wrap text
            pdf.set_xy(x_current, y_start_headers) # Set posisi X dan Y saat ini
            pdf.multi_cell(current_col_width, 5, str(header).encode('latin-1', 'replace').decode('latin-1'), border=1, align='C')
            x_current += current_col_width # Update posisi X untuk kolom berikutnya
            max_y_after_headers = max(max_y_after_headers, pdf.get_y()) # Perbarui max Y

        # Pindah ke baris baru setelah semua header dicetak.
        pdf.set_y(max_y_after_headers) 


        # Menambahkan baris data
        for row_data in df_for_pdf.itertuples(index=False): # Gunakan df_for_pdf
            # Simpan posisi Y awal untuk baris ini
            y_current_row = pdf.get_y()
            x_current_row = pdf.get_x() # Simpan posisi X awal untuk baris ini
            
            for i, data in enumerate(row_data):
                header = headers[i] # Dapatkan nama header untuk kolom saat ini
                current_col_width = col_widths.get(header, default_col_width)
                
                # Menghilangkan ".0" untuk nilai numerik
                formatted_data = str(data)
                if isinstance(data, (int, float)): # Cek apakah data adalah integer atau float
                    if float(data).is_integer(): # Cek apakah nilai float adalah bilangan bulat (misal 2020.0, 2834.0)
                        formatted_data = str(int(data))
                    else:
                        formatted_data = str(data) # Biarkan float jika ada desimal
                
                pdf.cell(current_col_width, 10, formatted_data.encode('latin-1', 'replace').decode('latin-1'), border=1, ln=False)
            pdf.ln(10) # Pindah ke baris baru setelah setiap baris data
    else:
        pdf.cell(0, 10, "Tidak ada kolom yang ditemukan.", ln=True)

    # Tambahkan teks sumber di bagian bawah tabel
    # Atur posisi Y ke posisi saat ini (setelah tabel berakhir) + sedikit margin
    pdf.set_y(pdf.get_y() + 5) # Tambahkan 5mm spasi setelah tabel
    pdf.set_font("Arial", size=8) # Ukuran font lebih kecil untuk sumber
    pdf.cell(0, 10, "Sumber: Kelurahan Kubu Marapalam", align='C')


    return bytes(pdf.output(dest='S'))

# --- FUNGSI BARU: Mendapatkan Objek Grafik untuk Halaman ini ---
def get_penduduk_tahun_chart():
    """
    Membuat dan mengembalikan objek grafik Altair untuk Jumlah Penduduk.
    """
    df_penduduk = load_penduduk_2020_from_gsheet()

    if df_penduduk.empty:
        st.info("Data tidak tersedia untuk grafik ini.")
        return None

    # Pastikan nama kolom 'Tahun' dan 'Jumlah Total (orang)' ada untuk grafik
    if 'Tahun' in df_penduduk.columns and 'Jumlah Total (orang)' in df_penduduk.columns:
        chart = alt.Chart(df_penduduk).mark_line(point=True).encode(
            x=alt.X('Tahun:O', title='Tahun'), # 'O' untuk data ordinal/kategorikal
            y=alt.Y('Jumlah Total (orang):Q', title='Jumlah Penduduk'), # 'Q' untuk data kuantitatif
            tooltip=[
                alt.Tooltip('Tahun', title='Tahun'),
                alt.Tooltip('Jumlah Laki-Laki (orang)', title='Laki-laki', format='.0f'),
                alt.Tooltip('Jumlah Perempuan (orang)', title='Perempuan', format='.0f'),
                alt.Tooltip('Jumlah Total (orang)', title='Total', format='.0f'),
                alt.Tooltip('Jumlah Kepala Keluarga (KK)', title='Jumlah KK', format='.0f')
            ]
        ).properties(
            title='Perkembangan Jumlah Penduduk'
        ).interactive()

        return chart
    else:
        st.warning("Kolom 'Tahun' atau 'Jumlah Total (orang)' tidak ditemukan untuk visualisasi grafik. Pastikan nama kolom di Google Sheet Anda sesuai.")
        return None

# --- Fungsi utama untuk halaman ini ---
def run():
    st.title("Jumlah Penduduk")
    st.markdown("---") # Garis pemisah

    # Memuat data penduduk
    df_penduduk = load_penduduk_2020_from_gsheet()

    if not df_penduduk.empty:
        st.subheader("Data Jumlah Penduduk")
        st.dataframe(df_penduduk)

        # --- Visualisasi Data ---
        st.subheader("Tren Jumlah Penduduk dari Tahun ke Tahun")

        chart_obj = get_penduduk_tahun_chart() # Panggil fungsi pembuat grafik
        if chart_obj:
            st.altair_chart(chart_obj, use_container_width=True) # Tampilkan grafik di halaman ini
        else:
            st.info("Tidak dapat menampilkan grafik karena data tidak tersedia atau tidak valid.")

        # Contoh metrik sederhana
        # Pastikan nama kolom di sini cocok dengan yang dimuat dari Google Sheet: 'Tahun', 'Jumlah Total (orang)'
        if 'Tahun' in df_penduduk.columns and 'Jumlah Total (orang)' in df_penduduk.columns:
            tahun_terbaru = df_penduduk['Tahun'].max()
            jumlah_terbaru = df_penduduk[df_penduduk['Tahun'] == tahun_terbaru]['Jumlah Total (orang)'].iloc[0]

            st.markdown("---")
            st.subheader("Ringkasan Data")
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label=f"Tahun Data Terakhir ({tahun_terbaru})", value=f"{jumlah_terbaru:,.0f} orang")
            with col2:
                # Menghitung perubahan jika ada lebih dari satu tahun data
                if len(df_penduduk) > 1:
                    # Mencari tahun sebelumnya yang ada di data
                    tahun_sebelumnya_data = df_penduduk[df_penduduk['Tahun'] < tahun_terbaru]['Tahun'].max()
                    if pd.notna(tahun_sebelumnya_data): # Pastikan tahun sebelumnya bukan NaN
                        jumlah_sebelumnya = df_penduduk[df_penduduk['Tahun'] == tahun_sebelumnya_data]['Jumlah Total (orang)'].iloc[0]
                        perubahan = jumlah_terbaru - jumlah_sebelumnya
                        st.metric(label=f"Perubahan dari Tahun {tahun_sebelumnya_data}", value=f"{perubahan:,.0f} orang", delta=f"{perubahan:,.0f}")
                    else:
                        st.info("Tidak cukup data untuk menghitung perubahan dari tahun sebelumnya (tahun sebelumnya tidak ditemukan).")
                else:
                    st.info("Tidak cukup data untuk menghitung perubahan dari tahun sebelumnya.")

        st.markdown("---") # Garis pemisah

        # --- Siapkan Data dan Tombol Download ---
        df_excel = to_excel(df_penduduk)
        pdf_data = df_to_pdf(df_penduduk) # Panggil fungsi df_to_pdf yang sudah diperbaiki

        col1, col2 = st.columns(2)
        # Download Dengan XLSX
        with col1:
            st.download_button(
                label="Download as XLSX",
                data=df_excel,
                file_name="data_penduduk.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        # Download Dengan PDF
        with col2:
            st.download_button(
                label="Download as PDF",
                data=pdf_data, # Gunakan output langsung dari df_to_pdf
                file_name="data_penduduk.pdf",
                mime="application/pdf",
                use_container_width=True
            )
    else:
        # Pesan ini ditampilkan jika df_penduduk kosong setelah mencoba memuat data.
        st.info("Belum ada data jumlah penduduk yang valid untuk divisualisasikan. Pastikan Google Sheet Anda dapat diakses dan memiliki data yang benar di worksheet 'Jumlah Penduduk' dengan kolom 'Tahun', 'Jumlah Laki-Laki (orang)', 'Jumlah Perempuan (orang)', 'Jumlah Total (orang)', dan 'Jumlah Kepala Keluarga (KK)'.")

# Bagian ini hanya akan dieksekusi jika file ini dijalankan secara langsung, bukan sebagai modul yang diimpor oleh main.py.
if __name__ == '__main__':
    run()