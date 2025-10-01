# data_loader.py

import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- Konfigurasi Google Sheets ---
GOOGLE_SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

# Nama-nama worksheet (tab) di Google Spreadsheet Anda
WORKSHEET_NAME_PENDUDUK = "Jumlah Penduduk"
WORKSHEET_NAME_PENDIDIKAN = "Jumlah Penduduk (Pendidikan)"
WORKSHEET_NAME_PEKERJAAN_DOMINAN = "Jenis Pekerjaan Dominan"
WORKSHEET_NAME_JENIS_TANAH = "Jenis Tanah"
WORKSHEET_NAME_INDUSTRI_UMKM = "Jumlah Industri UMKM"
WORKSHEET_NAME_KK_RW = "Jumlah KK Menurut RW"
WORKSHEET_NAME_STATUS_PEKERJA = "Jumlah Penduduk (status Pekerja)"
WORKSHEET_NAME_DISABILITAS = "Penduduk Disabilitas"
WORKSHEET_NAME_JENIS_KELAMIN = "Penduduk Menurut Jenis Kelamin"
WORKSHEET_NAME_SARANA_PRASARANA = "Sarana dan Prasarana"
WORKSHEET_NAME_SARANA_KEBERSIHAN = "Sarana Kebersihan"
WORKSHEET_NAME_TENAGA_KERJA = "Tenaga Kerja"

# --- Inisialisasi Koneksi Google Sheets ---
@st.cache_resource(ttl=3600)
def get_gsheets_connection():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn
    except Exception as e:
        st.error(f"Error establishing GSheetsConnection: {e}")
        st.stop()
        return None

# --- Fungsi Generik untuk Memuat Data (KOMPATIBEL DENGAN VERSI LAMA) ---
@st.cache_data(ttl=600)
def load_data_from_gsheets(worksheet_name, usecols=None):
    conn = get_gsheets_connection()
    if conn is None: return pd.DataFrame()
    try:
        df = conn.read(
            worksheet=worksheet_name,
            usecols=usecols,
            ttl=0
        )
        df = df.dropna(how="all")
        return df
    except Exception as e:
        st.error(f"Terjadi error saat membaca data dari Google Sheet '{worksheet_name}': {e}")
        return pd.DataFrame()

# --- Fungsi Generik untuk Menulis Data ---
def write_data_to_gsheets(df_to_write, worksheet_name):
    conn = get_gsheets_connection()
    if conn is None: return False
    try:
        conn.update(
            worksheet=worksheet_name,
            data=df_to_write
        )
        return True
    except Exception as e:
        st.error(f"Terjadi error saat menulis data ke Google Sheet '{worksheet_name}': {e}")
        return False

# --- FUNGSI: Memuat Data Jumlah Penduduk dari Google Sheet ---
# === BAGIAN INI DIKEMBALIKAN SEPERTI SEMULA UNTUK MEMPERBAIKI INDENTATIONERROR ===
@st.cache_data(ttl=60)
def load_penduduk_2020_from_gsheet():
    df = load_data_from_gsheets(WORKSHEET_NAME_PENDUDUK)
    if not df.empty:
        df.columns = df.columns.str.strip()
        required_columns = ['Tahun', 'Jumlah Laki-Laki (orang)', 'Jumlah Perempuan (orang)', 'Jumlah Total (orang)']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Kolom hilang di worksheet '{WORKSHEET_NAME_PENDUDUK}'.")
            return pd.DataFrame()
        for col in ['Jumlah Laki-Laki (orang)', 'Jumlah Perempuan (orang)', 'Jumlah Total (orang)']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(subset=['Jumlah Total (orang)'], inplace=True)
        df = df.sort_values(by='Tahun').reset_index(drop=True)
    return df

# --- FUNGSI: Memuat Data Pendidikan dari Google Sheet ---
@st.cache_data(ttl=60)
def load_pendidikan_data_from_gsheet():
    df = load_data_from_gsheets(WORKSHEET_NAME_PENDIDIKAN)
    if not df.empty:
        df.columns = df.columns.str.strip()
        required_columns = ['No', 'Pendidikan', 'Jumlah']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Kolom hilang di worksheet '{WORKSHEET_NAME_PENDIDIKAN}'.")
            return pd.DataFrame()
        df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
        df.dropna(subset=['Jumlah'], inplace=True)
        education_order = ['Tidak Tamat SD', 'Tamat SD/Sederajat', 'Tamat SMP/Sederajat', 'Tamat SMA/Sederajat', 'Tamat Akademi/Perguruan Tinggi']
        if 'Pendidikan' in df.columns:
            df['Pendidikan'] = pd.Categorical(df['Pendidikan'], categories=education_order, ordered=True)
            df = df.sort_values('Pendidikan').reset_index(drop=True)
    return df

# --- FUNGSI: Memuat Data Jenis Pekerjaan Dominan dari Google Sheet ---
@st.cache_data(ttl=60)
def load_jenis_pekerjaan_dominan_gsheet():
    df = load_data_from_gsheets(WORKSHEET_NAME_PEKERJAAN_DOMINAN)
    if not df.empty:
        df.columns = df.columns.str.strip()
        required_columns = ['No.', 'Tanggal', 'Jenis Pekerjaan', 'Jumlah']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Kolom hilang di worksheet '{WORKSHEET_NAME_PEKERJAAN_DOMINAN}'.")
            return pd.DataFrame()
        df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
        df.dropna(subset=['Jumlah', 'Tanggal'], inplace=True)
        if 'Tanggal' in df.columns:
            df = df.sort_values(by='Tanggal').reset_index(drop=True)
        elif 'No.' in df.columns:
            df = df.sort_values(by='No.').reset_index(drop=True)
    return df

# --- FUNGSI: Memuat Data Jenis Tanah dari Google Sheet ---
@st.cache_data(ttl=60)
def load_jenis_tanah_gsheet():
    df = load_data_from_gsheets(WORKSHEET_NAME_JENIS_TANAH)
    if not df.empty:
        df.columns = df.columns.str.strip()
        numeric_cols = ['Tanah Sawah (Ha)', 'Tanah Kering (Ha)', 'Tanah Basah (Ha)', 'Tanah Perkebunan (Ha)', 'Tanah Fasilitas Umum (Ha)', 'Tanah Hutan (Ha)', 'Total Luas Tanah (Ha)', 'Luas Desa/Kelurahan (Ha)']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(subset=['Total Luas Tanah (Ha)'], inplace=True)
        if 'Tanggal' in df.columns and not df['Tanggal'].empty and df['Tanggal'].iloc[0] is not None:
            try:
                df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
                df.dropna(subset=['Tanggal'], inplace=True)
                df = df.sort_values(by='Tanggal').reset_index(drop=True)
            except Exception: pass
    return df

# --- FUNGSI: Memuat Data Jumlah Industri UMKM dari Google Sheet ---
@st.cache_data(ttl=60)
def load_umkm_data_gsheet():
    df = load_data_from_gsheets(WORKSHEET_NAME_INDUSTRI_UMKM)
    if not df.empty:
        df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
        df.dropna(subset=['Jumlah'], inplace=True)
        if 'No.' in df.columns:
            df = df.sort_values(by='No.').reset_index(drop=True)
    return df

# --- FUNGSI: Memuat Data Jumlah KK Menurut RW dari Google Sheet ---
@st.cache_data(ttl=60)
def load_kk_rw_data_gsheet():
    df = load_data_from_gsheets(WORKSHEET_NAME_KK_RW)
    if not df.empty:
        numeric_cols = ['LAKI- LAKI', 'PEREMPUAN', 'JUMLAH KK']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(subset=['JUMLAH KK'], inplace=True)
        df['JUMLAH KK'] = df['JUMLAH KK'].astype(int)
        df = df.sort_values(by='JUMLAH KK', ascending=False).reset_index(drop=True)
    return df

# --- FUNGSI Memuat Data Jumlah Penduduk (Status Pekerja) dari Google Sheet ---
@st.cache_data(ttl=60)
def load_status_pekerja_data_gsheet():
    df = load_data_from_gsheets(WORKSHEET_NAME_STATUS_PEKERJA)
    if not df.empty:
        df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
        df.dropna(subset=['Jumlah'], inplace=True)
        df['Jumlah'] = df['Jumlah'].astype(int)
        if 'No.' in df.columns:
            df = df.sort_values(by='No.').reset_index(drop=True)
    return df

# --- FUNGSI: Memuat Data Penduduk Disabilitas dari Google Sheet ---
@st.cache_data(ttl=60)
def load_disabilitas_data_gsheet():
    df = load_data_from_gsheets(WORKSHEET_NAME_DISABILITAS)
    if not df.empty:
        numeric_cols = ['Laki-Laki (orang)', 'Perempuan (orang)', 'Jumlah (Orang)']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(subset=['Jumlah (Orang)'], inplace=True)
        if 'Tanggal' in df.columns and not df['Tanggal'].empty and df['Tanggal'].iloc[0] is not None:
            try:
                df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
                df.dropna(subset=['Tanggal'], inplace=True)
                df = df.sort_values(by='Tanggal').reset_index(drop=True)
            except Exception:
                if 'No.' in df.columns:
                    df = df.sort_values(by='No.').reset_index(drop=True)
        elif 'No.' in df.columns:
            df = df.sort_values(by='No.').reset_index(drop=True)
    return df

# --- FUNGSI: Memuat Data Penduduk Menurut Jenis Kelamin dari Google Sheet ---
@st.cache_data(ttl=60)
def load_penduduk_jenis_kelamin_gsheet():
    df = load_data_from_gsheets(WORKSHEET_NAME_JENIS_KELAMIN)
    if not df.empty:
        for col in ['NO', 'RW', 'RT', 'JUMLAH KK', 'LAKI- LAKI', 'PEREMPUAN', 'JUMLAH PENDUDUK']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(subset=['JUMLAH PENDUDUK'], inplace=True)
        df_processed = df.copy()
        df_processed.rename(columns={'NO': 'No', 'JUMLAH KK': 'Jumlah_KK', 'LAKI- LAKI': 'LAKI_LAKI', 'PEREMPUAN': 'PEREMPUAN', 'JUMLAH PENDUDUK': 'Jumlah_Penduduk'}, inplace=True)
        df_processed['RW_RT'] = df_processed['RW'].astype(str) + '-' + df_processed['RT'].astype(str)
        df_processed = df_processed.sort_values(by=['RW', 'RT']).reset_index(drop=True)
        return df_processed
    return pd.DataFrame()

# --- FUNGSI: Memuat Data Sarana dan Prasarana dari Google Sheet ---
@st.cache_data(ttl=60)
def load_sarana_prasarana_from_gsheet():
    df = load_data_from_gsheets(WORKSHEET_NAME_SARANA_PRASARANA)
    if not df.empty:
        for col in ['No.', 'Tahun', 'Jumlah (Unit)']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(subset=['Jumlah (Unit)'], inplace=True)
        df.columns = df.columns.str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_', regex=False)
        if 'No_' in df.columns:
            df.rename(columns={'No_': 'No'}, inplace=True)
        df = df.sort_values(by=['Tahun', 'No']).reset_index(drop=True)
    return df

# --- FUNGSI: Memuat Data Sarana Kebersihan dari Google Sheet ---
@st.cache_data(ttl=60)
def load_sarana_kebersihan_from_gsheet():
    df = load_data_from_gsheets(WORKSHEET_NAME_SARANA_KEBERSIHAN)
    if not df.empty:
        for col in ['No.', 'Jumlah']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(subset=['Jumlah'], inplace=True)
        df.columns = df.columns.str.replace(' ', '_').str.replace('.', '_', regex=False)
        if 'No_' in df.columns:
            df.rename(columns={'No_': 'No'}, inplace=True)
        df = df.sort_values(by=['No']).reset_index(drop=True)
    return df

# --- FUNGSI: Memuat Data Tenaga Kerja dari Google Sheet ---
@st.cache_data(ttl=60)
def load_tenaga_kerja_from_gsheet():
    df = load_data_from_gsheets(WORKSHEET_NAME_TENAGA_KERJA)
    if not df.empty:
        for col in ['No.', 'Laki-Laki (Orang)', 'Perempuan (Orang)', 'Jumlah']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df.dropna(subset=['Jumlah'], inplace=True)
        df.columns = df.columns.str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_', regex=False)
        if 'No_' in df.columns:
            df.rename(columns={'No_': 'No'}, inplace=True)
        df = df.sort_values(by=['No']).reset_index(drop=True)
    return df

# --- FUNGSI: Membaca URL Infografis dari Google Sheet ---
@st.cache_data(ttl=600)
def load_infografis_urls_from_gsheet():
    conn = get_gsheets_connection()
    if conn is None:
        return []
    try:
        df = conn.read(worksheet="Infografis", usecols=["URL_Gambar"], ttl=0)
        df = df.dropna(how="all")
        return df["URL_Gambar"].tolist()
    except Exception as e:
        st.error(f"Gagal membaca worksheet 'Infografis'. Detail: {e}")
        return []