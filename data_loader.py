import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# --- Konfigurasi Google Sheets ---
# ID Spreadsheet Anda (bisa ditemukan di URL Google Sheet Anda)
# Pastikan ini sesuai dengan Google Sheet yang Anda bagikan ke Service Account!
# Ambil URL Spreadsheet dari Streamlit secrets
GOOGLE_SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

# Nama-nama worksheet (tab) di Google Spreadsheet Anda
WORKSHEET_NAME_PENDUDUK = "Jumlah Penduduk (2020-2025)"
WORKSHEET_NAME_PENDIDIKAN = "Jumlah Penduduk (Pendidikan)" # Pastikan nama ini sudah benar di GSheet
WORKSHEET_NAME_PEKERJAAN_DOMINAN = "Jenis Pekerjaan Dominan"
WORKSHEET_NAME_JENIS_TANAH = "Jenis Tanah"
WORKSHEET_NAME_INDUSTRI_UMKM = "Jumlah Industri UMKM"
WORKSHEET_NAME_KK_RW = "Jumlah KK Menurut RW"
WORKSHEET_NAME_STATUS_PEKERJA = "Jumlah Penduduk (status Pekerja)"
WORKSHEET_NAME_DISABILITAS = "Penduduk Disabilitas"

# --- Inisialisasi Koneksi Google Sheets ---
@st.cache_resource(ttl=3600) # Cache the connection object for 1 hour
def get_gsheets_connection():
    """Establishes and returns a Streamlit GSheetsConnection."""
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn
    except Exception as e:
        st.error(f"Error establishing GSheetsConnection: {e}. "
                 "Pastikan Anda telah menginstal 'streamlit-gsheets' dan mengatur secrets dengan benar.")
        st.stop() # Stop the app if connection fails
        return None

# --- Fungsi Generik untuk Memuat Data dari Google Sheets ---
@st.cache_data(ttl=60) # Cache data for 1 minute for faster loading
def load_data_from_gsheets(worksheet_name, usecols=None):
    """Loads data from a specified worksheet in Google Sheets using st.connection."""
    conn = get_gsheets_connection()
    if conn is None:
        return pd.DataFrame()

    try:
        # ttl for read operation is applied per read call
        df = conn.read(
            spreadsheet=GOOGLE_SHEET_URL,
            worksheet=worksheet_name,
            usecols=usecols,
            ttl=5 # TTL for the read operation itself
        ) 
        df = df.dropna(how="all") # Drop rows that are entirely empty
        return df
    except Exception as e:
        st.error(f"Terjadi error saat membaca data dari Google Sheet '{worksheet_name}': {e}")
        return pd.DataFrame()

# --- Fungsi Generik untuk Menulis/Memperbarui Data ke Google Sheets ---
def write_data_to_gsheets(df_to_write, worksheet_name):
    """Writes (overwrites) a DataFrame to a specified worksheet in Google Sheets."""
    conn = get_gsheets_connection()
    if conn is None:
        return False

    try:
        conn.write(
            spreadsheet=GOOGLE_SHEET_URL,
            worksheet=worksheet_name,
            df=df_to_write
        )
        return True
    except Exception as e:
        st.error(f"Terjadi error saat menulis data ke Google Sheet '{worksheet_name}': {e}")
        return False

# --- FUNGSI: Memuat Data Jumlah Penduduk (2020-2025) dari Google Sheet ---
@st.cache_data(ttl=60)
def load_penduduk_2020_from_gsheet():
    """
    Memuat dan memproses data jumlah penduduk dari Google Sheet.

    Worksheet yang digunakan: 'Jumlah Penduduk (2020-2025)'
    Wajib memiliki kolom: 'Tahun', 'Jumlah Laki-Laki (orang)', 'Jumlah Perempuan (orang)', 'Jumlah Total (orang)', 'Jumlah Kepala Keluarga (KK)'
    """
    df = load_data_from_gsheets(WORKSHEET_NAME_PENDUDUK)
    if not df.empty:
        df.columns = df.columns.str.strip() # Membersihkan nama kolom

        required_columns = [
            'Tahun',
            'Jumlah Laki-Laki (orang)',
            'Jumlah Perempuan (orang)',
            'Jumlah Total (orang)',
            'Jumlah Kepala Keluarga (KK)'
        ]
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            st.error(f"Kolom yang diperlukan tidak ditemukan di worksheet '{WORKSHEET_NAME_PENDUDUK}'. "
                     f"Kolom yang hilang: {missing_cols}. "
                     f"Pastikan nama kolom di Google Sheet sudah benar (perhatikan kapitalisasi dan spasi).")
            return pd.DataFrame()

        # Konversi kolom numerik
        for col in ['Jumlah Laki-Laki (orang)', 'Jumlah Perempuan (orang)', 'Jumlah Total (orang)', 'Jumlah Kepala Keluarga (KK)']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.dropna(subset=['Jumlah Total (orang)'], inplace=True) # Hapus baris dengan NaN di kolom kunci

        df = df.sort_values(by='Tahun').reset_index(drop=True)
    return df

# --- FUNGSI: Memuat Data Pendidikan dari Google Sheet ---
@st.cache_data(ttl=60)
def load_pendidikan_data_from_gsheet():
    """
    Memuat dan memproses data jumlah penduduk (pendidikan) dari Google Sheet.

    Worksheet yang digunakan: 'Jumlah Penduduk (Pendidikan)'
    Wajib memiliki kolom: 'No', 'Pendidikan', 'Jumlah'
    """
    df = load_data_from_gsheets(WORKSHEET_NAME_PENDIDIKAN)
    if not df.empty:
        df.columns = df.columns.str.strip() # Membersihkan nama kolom

        required_columns = ['No', 'Pendidikan', 'Jumlah']
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            st.error(f"Kolom yang diperlukan tidak ditemukan di worksheet '{WORKSHEET_NAME_PENDIDIKAN}'. "
                     f"Kolom yang hilang: {missing_cols}. "
                     f"Pastikan nama kolom di Google Sheet sudah benar (perhatikan kapitalisasi dan spasi).")
            return pd.DataFrame()

        # Konversi kolom 'Jumlah' ke numerik
        df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
        df.dropna(subset=['Jumlah'], inplace=True) # Hapus baris dengan NaN di kolom 'Jumlah'

        # Menetapkan urutan alami untuk kategori pendidikan
        education_order = [
            'Tidak Tamat SD',
            'Tamat SD/Sederajat',
            'Tamat SMP/Sederajat',
            'Tamat SMA/Sederajat'
        ]
        # Pastikan kolom 'Pendidikan' ada sebelum membuat kategori
        if 'Pendidikan' in df.columns:
            df['Pendidikan'] = pd.Categorical(df['Pendidikan'], categories=education_order, ordered=True)
            df = df.sort_values('Pendidikan').reset_index(drop=True)
        else:
            st.warning(f"Kolom 'Pendidikan' tidak ditemukan di worksheet '{WORKSHEET_NAME_PENDIDIKAN}'. Pengurutan kategori tidak dapat dilakukan.")
    return df

# --- FUNGSI: Memuat Data Jenis Pekerjaan Dominan dari Google Sheet ---
@st.cache_data(ttl=60)
def load_jenis_pekerjaan_dominan_gsheet():
    """
    Memuat dan memproses data jenis pekerjaan dominan dari Google Sheet.
    Worksheet yang digunakan: 'Jenis Pekerjaan Dominan'
    Wajib memiliki kolom: 'No.', 'Tanggal', 'Jenis Pekerjaan', 'Jumlah'
    """
    df = load_data_from_gsheets(WORKSHEET_NAME_PEKERJAAN_DOMINAN)
    if not df.empty:
        df.columns = df.columns.str.strip() # Membersihkan nama kolom

        required_columns = ['No.', 'Tanggal', 'Jenis Pekerjaan', 'Jumlah']
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            st.error(f"Kolom yang diperlukan tidak ditemukan di worksheet '{WORKSHEET_NAME_PEKERJAAN_DOMINAN}'. "
                     f"Kolom yang hilang: {missing_cols}. "
                     f"Pastikan nama kolom di Google Sheet sudah benar (perhatikan kapitalisasi dan spasi).")
            return pd.DataFrame()

        # Konversi kolom 'Jumlah' ke numerik
        df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
        df.dropna(subset=['Jumlah'], inplace=True) # Hapus baris dengan NaN di kolom 'Jumlah'
        
        # Konversi kolom 'Tanggal' ke datetime jika diperlukan untuk sorting/filter
        # df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
        df.dropna(subset=['Tanggal'], inplace=True)

        # Sortir berdasarkan Tanggal atau No. jika ada
        if 'Tanggal' in df.columns:
            df = df.sort_values(by='Tanggal').reset_index(drop=True)
        elif 'No.' in df.columns:
            df = df.sort_values(by='No.').reset_index(drop=True)
    return df

# --- FUNGSI: Memuat Data Jenis Tanah dari Google Sheet ---
@st.cache_data(ttl=60)
def load_jenis_tanah_gsheet():
    """
    Memuat dan memproses data jenis tanah dari Google Sheet.
    Worksheet yang digunakan: 'Jenis Tanah'
    Wajib memiliki kolom: 'Tanggal', 'Tanah Sawah (Ha)', 'Tanah Kering (Ha)', 'Tanah Basah (Ha)',
    'Tanah Perkebunan (Ha)', 'Tanah Fasilitas Umum (Ha)', 'Tanah Hutan (Ha)',
    'Total Luas Tanah (Ha)', 'Luas Desa/Kelurahan (Ha)', 'Status'
    """
    df = load_data_from_gsheets(WORKSHEET_NAME_JENIS_TANAH)
    if df.empty:
        return pd.DataFrame()

    df.columns = df.columns.str.strip() # Membersihkan nama kolom

    required_columns = [
        'Tanggal', 'Tanah Sawah (Ha)', 'Tanah Kering (Ha)', 'Tanah Basah (Ha)',
        'Tanah Perkebunan (Ha)', 'Tanah Fasilitas Umum (Ha)', 'Tanah Hutan (Ha)',
        'Total Luas Tanah (Ha)', 'Luas Desa/Kelurahan (Ha)', 'Status'
    ]
    if not all(col in df.columns for col in required_columns):
        missing_cols = [col for col in required_columns if col not in df.columns]
        st.error(f"Kolom yang diperlukan tidak ditemukan di worksheet '{WORKSHEET_NAME_JENIS_TANAH}'. "
                 f"Kolom yang hilang: {missing_cols}. "
                 f"Pastikan nama kolom di Google Sheet sudah benar (perhatikan kapitalisasi dan spasi).")
        return pd.DataFrame()

    # Konversi kolom numerik
    numeric_cols = [
        'Tanah Sawah (Ha)', 'Tanah Kering (Ha)', 'Tanah Basah (Ha)',
        'Tanah Perkebunan (Ha)', 'Tanah Fasilitas Umum (Ha)', 'Tanah Hutan (Ha)',
        'Total Luas Tanah (Ha)', 'Luas Desa/Kelurahan (Ha)'
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Hapus baris yang memiliki NaN di kolom kunci (misalnya 'Total Luas Tanah (Ha)')
    df.dropna(subset=['Total Luas Tanah (Ha)'], inplace=True)

    # Konversi kolom 'Tanggal' ke datetime
    if 'Tanggal' in df.columns and not df['Tanggal'].empty and df['Tanggal'].iloc[0] is not None:
        try:
            df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
            df.dropna(subset=['Tanggal'], inplace=True)
            df = df.sort_values(by='Tanggal').reset_index(drop=True)
        except Exception as date_e:
            st.warning(f"Kolom 'Tanggal' tidak dapat dikonversi ke format tanggal yang valid. Sorting berdasarkan tanggal mungkin tidak akurat. Detail: {date_e}")
            # Jika tanggal bermasalah, tidak ada kolom lain untuk sorting otomatis, jadi biarkan saja.
    return df

# --- FUNGSI: Memuat Data Jumlah Industri UMKM dari Google Sheet ---
@st.cache_data(ttl=60)
def load_umkm_data_gsheet():
    """
    Memuat dan memproses data Jumlah Industri UMKM dari Google Sheet.
    Worksheet yang digunakan: 'Jumlah Industri UMKM'
    Wajib memiliki kolom: 'No.', 'Jenis', 'Jumlah'
    """
    df = load_data_from_gsheets(WORKSHEET_NAME_INDUSTRI_UMKM)
    if df.empty:
        return pd.DataFrame()

    df.columns = df.columns.str.strip() # Membersihkan nama kolom

    required_columns = ['No.', 'Jenis', 'Jumlah']
    if not all(col in df.columns for col in required_columns):
        missing_cols = [col for col in required_columns if col not in df.columns]
        st.error(f"Kolom yang diperlukan tidak ditemukan di worksheet '{WORKSHEET_NAME_INDUSTRI_UMKM}'. "
                 f"Kolom yang hilang: {missing_cols}. "
                 f"Pastikan nama kolom di Google Sheet sudah benar (perhatikan kapitalisasi dan spasi).")
        return pd.DataFrame()

    # Konversi kolom 'Jumlah' ke numerik
    df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
    df.dropna(subset=['Jumlah'], inplace=True) # Hapus baris dengan NaN di kolom 'Jumlah'
    
    # Sortir berdasarkan 'No.' jika ada
    if 'No.' in df.columns:
        df = df.sort_values(by='No.').reset_index(drop=True)
    return df

# --- FUNGSI: Memuat Data Jumlah KK Menurut RW dari Google Sheet ---
@st.cache_data(ttl=60)
def load_kk_rw_data_gsheet():
    """
    Memuat dan memproses data Jumlah KK Menurut RW dari Google Sheet.
    Worksheet yang digunakan: 'Jumlah KK Menurut RW'
    Wajib memiliki kolom: 'RW', 'LAKI- LAKI', 'PEREMPUAN', 'JUMLAH KK'
    """
    df = load_data_from_gsheets(WORKSHEET_NAME_KK_RW)
    if df.empty:
        return pd.DataFrame()

    df.columns = df.columns.str.strip() # Membersihkan nama kolom

    required_columns = ['RW', 'LAKI- LAKI', 'PEREMPUAN', 'JUMLAH KK']
    if not all(col in df.columns for col in required_columns):
        missing_cols = [col for col in required_columns if col not in df.columns]
        st.error(f"Kolom yang diperlukan tidak ditemukan di worksheet '{WORKSHEET_NAME_KK_RW}'. "
                 f"Kolom yang hilang: {missing_cols}. "
                 f"Pastikan nama kolom di Google Sheet sudah benar (perhatikan kapitalisasi dan spasi).")
        return pd.DataFrame()

    # Hapus baris yang tidak memiliki data 'JUMLAH KK' (biasanya baris total atau kosong)
    df.dropna(subset=['JUMLAH KK'], inplace=True)

    # Konversi kolom numerik
    numeric_cols = ['LAKI- LAKI', 'PEREMPUAN', 'JUMLAH KK']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df.dropna(subset=['JUMLAH KK'], inplace=True) # Hapus baris dengan NaN di kolom 'JUMLAH KK'

    # Mengubah tipe data 'JUMLAH KK' menjadi angka bulat (integer)
    df['JUMLAH KK'] = df['JUMLAH KK'].astype(int)

    # Sortir berdasarkan 'JUMLAH KK'
    df = df.sort_values(by='JUMLAH KK', ascending=False).reset_index(drop=True)
    return df

# --- FUNGSI Memuat Data Jumlah Penduduk (Status Pekerja) dari Google Sheet ---
@st.cache_data(ttl=60)
def load_status_pekerja_data_gsheet():
    """
    Memuat dan memproses data Jumlah Penduduk (Status Pekerja) dari Google Sheet.
    Worksheet yang digunakan: 'Jumlah Penduduk (Status Pekerja)'
    Wajib memiliki kolom: 'No.', 'Kriteria', 'Jumlah'
    """
    df = load_data_from_gsheets(WORKSHEET_NAME_STATUS_PEKERJA)
    if df.empty:
        return pd.DataFrame()

    df.columns = df.columns.str.strip() # Membersihkan nama kolom

    required_columns = ['No.', 'Kriteria', 'Jumlah']
    if not all(col in df.columns for col in required_columns):
        missing_cols = [col for col in required_columns if col not in df.columns]
        st.error(f"Kolom yang diperlukan tidak ditemukan di worksheet '{WORKSHEET_NAME_STATUS_PEKERJA}'. "
                 f"Kolom yang hilang: {missing_cols}. "
                 f"Pastikan nama kolom di Google Sheet sudah benar (perhatikan kapitalisasi dan spasi).")
        return pd.DataFrame()

    # Konversi kolom 'Jumlah' ke numerik
    df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
    df.dropna(subset=['Jumlah'], inplace=True) # Hapus baris dengan NaN di kolom 'Jumlah'
    
    # Mengubah tipe data 'Jumlah' menjadi angka bulat (integer)
    df['Jumlah'] = df['Jumlah'].astype(int)

    # Sortir berdasarkan 'No.' jika ada (atau 'Jumlah' jika lebih relevan untuk pie chart)
    if 'No.' in df.columns:
        df = df.sort_values(by='No.').reset_index(drop=True)
    # Anda bisa juga menambahkan sorting berdasarkan Jumlah jika ingin urutan slice yang berbeda
    # df = df.sort_values(by='Jumlah', ascending=False).reset_index(drop=True)
    return df

    # --- FUNGSI BARU: Memuat Data Penduduk Disabilitas dari Google Sheet ---
@st.cache_data(ttl=60)
def load_disabilitas_data_gsheet():
    """
    Memuat dan memproses data Penduduk Disabilitas dari Google Sheet.
    Worksheet yang digunakan: 'Penduduk Disabilitas'
    Wajib memiliki kolom: 'No.', 'Tanggal', 'Jenis Cacat', 'Laki-Laki (orang)', 'Perempuan (orang)', 'Jumlah (Orang)'
    """
    df = load_data_from_gsheets(WORKSHEET_NAME_DISABILITAS)
    if df.empty:
        return pd.DataFrame()

    df.columns = df.columns.str.strip() # Membersihkan nama kolom

    required_columns = ['No.', 'Tanggal', 'Jenis Cacat', 'Laki-Laki (orang)', 'Perempuan (orang)', 'Jumlah (Orang)']
    if not all(col in df.columns for col in required_columns):
        missing_cols = [col for col in required_columns if col not in df.columns]
        st.error(f"Kolom yang diperlukan tidak ditemukan di worksheet '{WORKSHEET_NAME_DISABILITAS}'. "
                 f"Kolom yang hilang: {missing_cols}. "
                 f"Pastikan nama kolom di Google Sheet sudah benar (perhatikan kapitalisasi dan spasi).")
        return pd.DataFrame()

    # Konversi kolom numerik
    numeric_cols = ['Laki-Laki (orang)', 'Perempuan (orang)', 'Jumlah (Orang)']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df.dropna(subset=['Jumlah (Orang)'], inplace=True) # Hapus baris dengan NaN di kolom 'Jumlah (Orang)'

    # Konversi kolom 'Tanggal' ke datetime jika diperlukan untuk sorting/filter
    if 'Tanggal' in df.columns and not df['Tanggal'].empty and df['Tanggal'].iloc[0] is not None:
        try:
            df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')
            df.dropna(subset=['Tanggal'], inplace=True)
            df = df.sort_values(by='Tanggal').reset_index(drop=True)
        except Exception as date_e:
            st.warning(f"Kolom 'Tanggal' tidak dapat dikonversi ke format tanggal yang valid. Sorting berdasarkan tanggal mungkin tidak akurat. Detail: {date_e}")
            if 'No.' in df.columns:
                df = df.sort_values(by='No.').reset_index(drop=True)
    elif 'No.' in df.columns:
        df = df.sort_values(by='No.').reset_index(drop=True)
    return df