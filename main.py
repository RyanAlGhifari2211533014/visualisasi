# === CARA MENJALANKAN ===
# 1. Buka terminal atau CMD.
# 2. Masuk ke folder proyek (contoh: cd D:\visualisasi)
# 3. Jalankan perintah: streamlit run main.py

# encodeuntuk python versi 13
# return pdf.output(dest='S').encode('latin-1')

# === PASTIKAN LIBRARY TERINSTAL ===
# Pastikan semua library ini terinstal di lingkungan Python Anda.
# Anda bisa menginstalnya dengan:
# pip install streamlit
# pip install streamlit-option-menu
# pip install pandas
# pip install altair
# pip install matplotlib
# pip install seaborn
# pip install openpyxl
# pip install fpdf2
# pip install st-gsheets-connection
# pip install XlsxWriter

# === IMPORT LIBRARY UTAMA ===
import streamlit as st
from streamlit_option_menu import option_menu # Untuk navigasi sidebar yang interaktif
import pandas as pd # Untuk manipulasi data

# === SETTING HALAMAN UTAMA STREAMLIT ===
st.set_page_config(
    page_title="Dashboard Data Kelurahan", # Judul yang muncul di tab browser
    page_icon="📊", # Ikon yang muncul di tab browser
    layout="wide",  # Membuat tampilan aplikasi lebih lebar
    initial_sidebar_state="expanded" # Sidebar akan terbuka secara default
)

# === FUNGSI UNTUK MEMUAT CSS KUSTOM JIKA ADA ===
# Fungsi ini mencoba membaca dan menerapkan file CSS eksternal untuk styling kustom.
# Struktur dan fungsionalitas fungsi ini TIDAK BERUBAH.
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"File CSS '{file_name}' tidak ditemukan. CSS tidak dimuat.")

# Panggil fungsi untuk memuat CSS. Pastikan ada file 'main.css' di direktori yang sama dengan main.py
# Pemanggilan ini dan fungsionalitasnya TIDAK BERUBAH.
load_css("main.css")

# === IMPORT FUNGSI-FUNGSI HALAMAN ===
# Mengimpor modul-modul halaman dari folder 'pages'.
# Setiap modul diasumsikan memiliki fungsi 'run()' yang akan dipanggil.
from pages import home
from pages import jumlah_penduduk
from pages import jumlah_penduduk_pendidikan
# Tambahkan import untuk halaman lain di sini saat Anda membuatnya
from pages import jenis_pekerjaan_dominan
from pages import jenis_tanah
from pages import jumlah_industri_umkm
from pages import jumlah_kk_menurut_rw
from pages import jumlah_penduduk_status_pekerja
from pages import penduduk_disabilitas
from pages import penduduk_menurut_jenis_kelamin
from pages import sarana_dan_prasarana
from pages import sarana_kebersihan
from pages import tenaga_kerja
from pages import admin
from data_loader import GOOGLE_SHEET_URL
# from pages import admin

# === SIDEBAR NAVIGASI ===
# Blok 'with st.sidebar:' menempatkan semua elemen di dalamnya ke dalam sidebar Streamlit.
with st.sidebar:
    st.title("SIGEMA") # Judul di sidebar

    # Membuat menu opsi navigasi menggunakan streamlit-option_menu
    selected = option_menu(
        menu_title='Menu Utama', # Judul untuk menu ini
        options=[
            'Home',
            'Jumlah Penduduk (2020-2025)',
            'Jumlah Penduduk (Pendidikan)',
            'Jenis Pekerjaan Dominan', # Placeholder, perlu dibuat halamannya
            'Jenis Tanah', # Placeholder, perlu dibuat halamannya
            'Jumlah Industri UMKM', # Placeholder, perlu dibuat halamannya
            'Jumlah KK Menurut RW', # Placeholder, perlu dibuat halamannya
            'Jumlah Penduduk (Status Pekerja)', # Placeholder, perlu dibuat halamannya
            'Penduduk Disabilitas', # Placeholder, perlu dibuat halamannya
            'Penduduk Menurut Jenis Kelamin', # Placeholder, perlu dibuat halamannya
            'Sarana dan Prasarana', # Placeholder, perlu dibuat halamannya
            'Sarana Kebersihan', # Placeholder, perlu dibuat halamannya
            'Tenaga Kerja', # Placeholder, perlu dibuat halamannya
            'Peta',
            'Admin' # Placeholder, perlu dibuat halamannya
        ],
        icons=[ # Ikon untuk setiap opsi menu (sesuaikan dengan ikon Bootstrap yang tersedia)
            'house', 'graph-up', 'mortarboard', 'person-workspace', 'map', 'building',
            'people', 'person-badge', 'universal-access', 'person-fill-gear',
            'hospital', 'trash', 'briefcase', 'gear'
        ],
        menu_icon="cast", # Ikon untuk judul menu
        default_index=0 # Indeks opsi yang dipilih secara default (0 = Home)
    )

# === ROUTING KE SETIAP HALAMAN BERDASARKAN MENU YANG DIPILIH ===
# Bagian ini menentukan halaman mana yang akan ditampilkan berdasarkan opsi yang dipilih di sidebar.
if selected == 'Home':
    home.run() # Memanggil fungsi run() dari modul home
elif selected == 'Jumlah Penduduk':
    jumlah_penduduk.run() # Memanggil fungsi run() dari modul jumlah_penduduk_2020_2025
elif selected == 'Jumlah Penduduk (Pendidikan)':
    jumlah_penduduk_pendidikan.run() # Memanggil fungsi run() dari modul jumlah_penduduk_pendidikan
elif selected == 'Jenis Pekerjaan Dominan':
    jenis_pekerjaan_dominan.run()
elif selected == 'Jenis Tanah':
    jenis_tanah.run()
elif selected == 'Jumlah Industri UMKM':
    jumlah_industri_umkm.run()
elif selected == 'Jumlah KK Menurut RW':
    jumlah_kk_menurut_rw.run()
elif selected == 'Jumlah Penduduk (Status Pekerja)':
    jumlah_penduduk_status_pekerja.run()
elif selected == 'Penduduk Disabilitas':
    penduduk_disabilitas.run()
elif selected == 'Penduduk Menurut Jenis Kelamin':
    penduduk_menurut_jenis_kelamin.run()
elif selected == 'Sarana dan Prasarana':
    sarana_dan_prasarana.run()
elif selected == 'Sarana Kebersihan':
    sarana_kebersihan.run()
elif selected == 'Tenaga Kerja':
    tenaga_kerja.run()
elif selected == 'Admin': # BARU: Logika untuk opsi Admin
    st.subheader("Akses Halaman Admin")
    st.write("Klik tombol di bawah untuk membuka Google Sheet database Anda:")
    st.markdown(f'<a href="{GOOGLE_SHEET_URL}" target="_blank"><button style="background-color:#4CAF50;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;">Buka Google Sheet Database</button></a>', unsafe_allow_html=True)
    st.info("Pastikan Anda sudah login ke akun Google yang memiliki akses ke spreadsheet ini.")

elif selected == 'Peta': # BARU: Logika untuk opsi Peta
    st.subheader("Akses Halaman Peta")
    st.write("Klik tombol di bawah untuk membuka :")
    st.markdown(f'<a href="https://earth.google.com/earth/d/1UDWR2S6sygquKm74PC_WlKcv2_kqZIO-?usp=sharing" target="_blank"><button style="background-color:#4CAF50;color:white;padding:10px 20px;border:none;border-radius:5px;cursor:pointer;">Buka Peta Database</button></a>', unsafe_allow_html=True)
    st.info("Pastikan Anda sudah login ke akun Google yang memiliki akses ke spreadsheet ini.")
    