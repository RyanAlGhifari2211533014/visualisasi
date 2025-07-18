# how to run:
# 1. Open your terminal or command prompt.
# 2. Navigate to this project folder location (e.g., cd your_project_folder).
# 3. Run the Streamlit app: streamlit run main.py

# Make sure you have installed these libraries:
# pip install streamlit
# pip install streamlit-option-menu
# pip install pandas
# pip install altair
# pip install matplotlib
# pip install seaborn
# pip install openpyxl

import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd # Still needed for initial session_state setup if any
import datetime # Still needed for initial session_state setup if any

# Import data loading functions
# BENAR:
from data_loader import load_penduduk_data_from_excel, load_pendidikan_data_from_excel

# Import page modules
from pages import home
from pages import jumlah_penduduk_2020_2025
from pages import jumlah_penduduk_pendidikan

# Import other pages as you create them:
# from pages import jenis_tanah
# from pages import jumlah_industri_umkm
# ...and so on for all your menu options

# --- CSS Injection ---
def load_css(file_name):
    """Loads and injects CSS from a file into the Streamlit app."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file '{file_name}' not found. Skipping CSS loading.")

# Call CSS
load_css("main.css")

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Dashboard Data Kelurahan",
    page_icon="📊",
    layout="wide", # Use wide layout for better visualization
    initial_sidebar_state="expanded"
)

# --- Initialize Session State for other data (if not loaded from specific files) ---
# This acts as a temporary "database" for data not yet sourced from persistent files/DB.
# IMPORTANT: For persistent data, replace these with actual database connections (e.g., Firestore).
if 'data_pendidikan' not in st.session_state:
    st.session_state.data_pendidikan = pd.DataFrame({
        'Tingkat Pendidikan': ['SD', 'SMP', 'SMA', 'Diploma', 'Sarjana', 'Pascasarjana'],
        'Jumlah': [3000, 2500, 2000, 800, 1200, 300]
    })
# Add other initial session state data here if needed for other pages

# --- Sidebar Navigation ---
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
            'Tenaga Kerja','Admin'
        ],
        icons=[
            'house', 'graph-up', 'mortarboard', 'person-workspace', 'map', 'building',
            'people', 'person-badge', 'universal-access', 'gender-ambiguous',
            'hospital', 'trash', 'briefcase','admin'
        ],
        menu_icon="cast",
        default_index=0
    )

# --- Page Routing ---
# Based on the selected option, call the run() function of the corresponding page module.
if selected == 'Home':
    home.run()
elif selected == 'Jumlah Penduduk (2020-2025)':
    jumlah_penduduk_2020_2025.run()
elif selected == 'Jumlah Penduduk (Pendidikan)':
    jumlah_penduduk_pendidikan.run()
elif selected == 'Jenis Pekerjaan Dominan':
    jenis_pekerjaan_dominan.run()
# Add elif blocks for other pages here:
# elif selected == 'Jenis Tanah':
#     jenis_tanah.run()
# ... and so on
