import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import base64
import os

st.set_page_config(
    page_title="Dashboard Data Kelurahan",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {
        background-color: #EFF2F6;
    }
    .stApp {
        color: #111111;
    }
    [data-testid="stSidebar"] h1 {
        color: #FFFFFF;
        padding-top: 1rem;
    }
    [data-testid="stSidebar"] {
        background-color: #111111;
    }
    .main [data-testid="stVerticalBlock"], .main [data-testid="stHorizontalBlock"] {
        background-color: #FFFFFF;
        border: 1px solid rgba(0,0,0,0.1);
        border-radius: 10px;
        padding: 1.5rem 1.5rem 2rem 1.5rem;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.02);
        transition: 0.3s;
        margin-bottom: 1rem;
    }
    .main .block-container {
        background-color: transparent;
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

from pages import home, jumlah_penduduk, jumlah_penduduk_pendidikan, jenis_pekerjaan_dominan, jenis_tanah, jumlah_industri_umkm, jumlah_kk_menurut_rw, jumlah_penduduk_status_pekerja, penduduk_disabilitas, penduduk_menurut_jenis_kelamin, sarana_dan_prasarana, sarana_kebersihan, tenaga_kerja, admin
from data_loader import GOOGLE_SHEET_URL

with st.sidebar:
    st.title("SIGEMA")
    selected = option_menu(
        menu_title=None, 
        options=['Home', 'Jumlah Penduduk', 'Jumlah Penduduk (Pendidikan)', 'Jenis Pekerjaan Dominan', 'Jenis Tanah', 'Jumlah Industri UMKM', 'Jumlah KK Menurut RW', 'Jumlah Penduduk (Status Pekerja)', 'Penduduk Disabilitas', 'Penduduk Menurut Jenis Kelamin', 'Sarana dan Prasarana', 'Sarana Kebersihan', 'Tenaga Kerja', 'Peta', 'Admin', 'Infografis', 'Kelurahan'],
        icons=['house', 'graph-up', 'mortarboard', 'person-workspace', 'map', 'building', 'people', 'person-badge', 'universal-access', 'person-fill-gear', 'hospital', 'trash', 'briefcase', 'gear'],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#111111"},
            "icon": {"color": "white", "font-size": "1rem"}, 
            "nav-link": {"font-size": "1rem", "text-align": "left", "margin":"0px", "color":"#FFFFFF", "--hover-color": "#444444"},
            "nav-link-selected": {"background-color": "#004488"}, 
        }
    )
    
    

if selected == 'Home': home.run()
elif selected == 'Jumlah Penduduk': jumlah_penduduk.run()
elif selected == 'Jumlah Penduduk (Pendidikan)': jumlah_penduduk_pendidikan.run()
elif selected == 'Jenis Pekerjaan Dominan': jenis_pekerjaan_dominan.run()
elif selected == 'Jenis Tanah': jenis_tanah.run()
elif selected == 'Jumlah Industri UMKM': jumlah_industri_umkm.run()
elif selected == 'Jumlah KK Menurut RW': jumlah_kk_menurut_rw.run()
elif selected == 'Jumlah Penduduk (Status Pekerja)': jumlah_penduduk_status_pekerja.run()
elif selected == 'Penduduk Disabilitas': penduduk_disabilitas.run()
elif selected == 'Penduduk Menurut Jenis Kelamin': penduduk_menurut_jenis_kelamin.run()
elif selected == 'Sarana dan Prasarana': sarana_dan_prasarana.run()
elif selected == 'Sarana Kebersihan': sarana_kebersihan.run()
elif selected == 'Tenaga Kerja': tenaga_kerja.run()
elif selected == 'Admin':
    st.title("🔑 Akses Admin")
    st.write("Klik tombol di bawah untuk membuka dan mengedit database di Google Sheets:")
    st.markdown(f'<a href="{GOOGLE_SHEET_URL}" target="_blank" style="text-decoration: none;"><button style="background-color:#1a73e8;color:white;padding:12px 24px;border:none;border-radius:8px;cursor:pointer;font-size:16px;">Buka Google Sheet</button></a>', unsafe_allow_html=True)
    st.info("Pastikan Anda sudah login ke akun Google yang memiliki akses edit ke spreadsheet ini.")
# <<< DIUBAH: Mengembalikan logika untuk menu Peta >>>
elif selected == 'Peta':
    st.title("🗺️ Peta Geospasial")
    st.write("Klik tombol di bawah untuk membuka peta interaktif kelurahan:")
    # Ganti URL ini dengan URL Google Earth Anda yang benar
    PETA_URL = "https://earth.google.com/earth/d/17GwLPOj3Yh1kg8KS_sBaGdHtlp10Dc-k?usp=sharing"
    st.markdown(f'<a href="{PETA_URL}" target="_blank" style="text-decoration: none;"><button style="background-color:#1a73e8;color:white;padding:12px 24px;border:none;border-radius:8px;cursor:pointer;font-size:16px;">Buka Peta</button></a>', unsafe_allow_html=True)
elif selected == 'Infografis':
    st.title("INFOGRAFIS")
    st.write("Klik tombol di bawah untuk membuka Infografis kelurahan:")
    INFOGRAFIS_URL = "https://inografis.my.canva.site/"
    st.markdown(f'<a href="{INFOGRAFIS_URL}" target="_blank" style="text-decoration: none;"><button style="background-color:#1a73e8;color:white;padding:12px 24px;border:none;border-radius:8px;cursor:pointer;font-size:16px;">Buka Infografis</button></a>', unsafe_allow_html=True)
elif selected == 'Profil Kelurahan':
    st.title("Profil Kelurahan")
    st.write("Klik tombol di bawah untuk membuka Profil kelurahan:")
    PROFIL_URL = "https://drive.google.com/drive/folders/1YXKb_3bCBtjo1fd2KFJBv0cCoQ0UhqzL?usp=drive_link"
    st.markdown(f'<a href="{PROFIL_URL}" target="_blank" style="text-decoration: none;"><button style="background-color:#1a73e8;color:white;padding:12px 24px;border:none;border-radius:8px;cursor:pointer;font-size:16px;">Buka Profil</button></a>', unsafe_allow_html=True)
