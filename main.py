# how to run:
# 1. command promp
# 2. go to this project folder location (navigate using dir and cd)
# 3. streamlit run {file name you want to run}

# pip install st-pages streamlit
# pip install streamlit-option-menu

import streamlit as st
from streamlit_option_menu import option_menu

# navigasi sidebar
with st.sidebar :
    selected = option_menu ('Dashboard',
                            ['Home',
                             'Jumlah Penduduk (2020-2025)', 
                             'Jumlah Penduduk (Pendidikan)',
                             'Jenis Pekerjaan Dominan',
                             'Jenis Tanah',
                             'Jumlah Industri UMKM',
                             'Jumlah KK Menurut RW',
                             'Jumlah Penduduk (status Pekerja',
                             'Penduduk Disabilitas',
                             'Penduduk Menurut Jenis Kelamin',
                             'Sarana dan Prasarana',
                             'Sarana Kebersihan',
                             'Tenaga Kerja'], icons=[
                               'house', 'graph-up', 'mortarboard', 'person-workspace', 'map', 'building',
                               'people', 'person-badge', 'universal-access', 'gender-ambiguous',
                               'hospital', 'trash', 'briefcase'
                           ], # Anda bisa menyesuaikan ikon dari Bootstrap Icons
                           menu_icon="cast", # Ikon untuk menu utama
                           default_index=0
                           )
    
if (selected == 'Jumlah Penduduk (2020-2025)'):
    st.title('Jumlah Penduduk (2020-2025)')

print("ini tabel Jumlah Penduduk (2020-2025)")

if (selected == 'Jumlah Penduduk (Pendidikan)') :
    st.title("Jumlah Penduduk (Pendidikan)")
print("ini tabel 'Jumlah Penduduk (Pendidikan)'")

if (selected == 'Jenis Pekerjaan Dominan') :
    st.title("Jenis Pekerjaan Dominan")
    