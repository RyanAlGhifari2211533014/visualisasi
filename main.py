# === CARA MENJALANKAN ===
# 1. Buka terminal atau CMD.
# 2. Masuk ke folder proyek (contoh: cd D:\visualisasi)
# 3. Jalankan perintah: streamlit run main.py

# === PASTIKAN LIBRARY TERINSTAL ===
# pip install streamlit streamlit-option-menu pandas altair matplotlib seaborn openpyxl fpdf2 streamlit_gsheets

# === IMPORT LIBRARY UTAMA ===
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import datetime

# === SETTING HALAMAN UTAMA STREAMLIT ===
st.set_page_config(
    page_title="Dashboard Data Kelurahan",
    page_icon="📊",
    layout="wide",  # Membuat tampilan lebih lebar
    initial_sidebar_state="expanded"
)

# === FUNGSI UNTUK MEMUAT CSS KUSTOM JIKA ADA ===
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"File CSS '{file_name}' tidak ditemukan. CSS tidak dimuat.")

# Panggil CSS jika ada file "main.css"
load_css("main.css")

# === IMPORT FUNGSI-FUNGSI HALAMAN ===
from pages import home
from pages import jumlah_penduduk_2020_2025
from pages import jumlah_penduduk_pendidikan
# Tambahkan halaman lain jika sudah tersedia di folder /pages
# from pages import jenis_tanah
# from pages import jenis_pekerjaan_dominan
# dan lainnya

# === DATA SEMENTARA UNTUK PENDIDIKAN (HANYA JIKA BELUM DARI G-SHEET) ===
if 'data_pendidikan' not in st.session_state:
    st.session_state.data_pendidikan = pd.DataFrame({
        'Tingkat Pendidikan': ['SD', 'SMP', 'SMA', 'Diploma', 'Sarjana', 'Pascasarjana'],
        'Jumlah': [3000, 2500, 2000, 800, 1200, 300]
    })

# === SIDEBAR NAVIGASI ===
with st.sidebar:
    st.title("Dashboard Data Kelurahan")
    selected = option_menu(
        menu_title='Menu Utama',
        options=[
            'Home',
            'Jumlah Penduduk (2020-2025)',
            'Jumlah Penduduk (Pendidikan)',
            'Jenis Pekerjaan Dominan',
            'Jenis Tanah',
            'Jumlah Industri UMKM',
            'Jumlah KK Menurut RW',
            'Jumlah Penduduk (Status Pekerja)',
            'Penduduk Disabilitas',
            'Penduduk Menurut Jenis Kelamin',
            'Sarana dan Prasarana',
            'Sarana Kebersihan',
            'Tenaga Kerja',
            'Admin'
        ],
        icons=[
            'house', 'graph-up', 'mortarboard', 'person-workspace', 'map', 'building',
            'people', 'person-badge', 'universal-access', 'gender-ambiguous',
            'hospital', 'trash', 'briefcase', 'gear'
        ],
        menu_icon="cast",
        default_index=0
    )

# === ROUTING KE SETIAP HALAMAN BERDASARKAN MENU YANG DIPILIH ===
if selected == 'Home':
    home.run()
elif selected == 'Jumlah Penduduk (2020-2025)':
    jumlah_penduduk_2020_2025.run()
elif selected == 'Jumlah Penduduk (Pendidikan)':
    jumlah_penduduk_pendidikan.run()
# Tambahkan pemanggilan halaman lain bila sudah dibuat:
# elif selected == 'Jenis Pekerjaan Dominan':
#     jenis_pekerjaan_dominan.run()
# elif selected == 'Jenis Tanah':
#     jenis_tanah.run()
# ... dan seterusnya
