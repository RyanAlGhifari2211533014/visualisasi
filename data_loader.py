import streamlit as st
import pandas as pd

# --- Fungsi untuk Memuat Data dari File Excel ---
# Menggunakan st.cache_data agar data hanya dimuat sekali dan di-cache
@st.cache_data
def load_penduduk_data_from_excel():
    """
    Loads and preprocesses population data from an Excel file.
    Expects 'Jumlah Penduduk (2020-2025).xlsx' with 'Tahun' and 'Jumlah Total (orang)' columns.
    """
    file_path = 'Jumlah Penduduk (2020-2025).xlsx'
    try:
        df = pd.read_excel(file_path)
        
        # Pre-processing: Sort data by 'Tahun'
        if 'Tahun' in df.columns:
            # Ensure 'Jumlah Total (orang)' column exists and is numeric
            if 'Jumlah Total (orang)' in df.columns:
                df['Jumlah Total (orang)'] = pd.to_numeric(df['Jumlah Total (orang)'], errors='coerce')
                df = df.dropna(subset=['Jumlah Total (orang)']) # Drop rows with NaN values after conversion
            else:
                st.error(f"Kolom 'Jumlah Total (orang)' tidak ditemukan di file '{file_path}'. Pastikan nama kolom sudah benar.")
                return pd.DataFrame()
                
            df_processed = df.sort_values(by='Tahun', ascending=True).reset_index(drop=True)
            return df_processed
        else:
            st.error(f"Kolom 'Tahun' tidak ditemukan di file '{file_path}'.")
            return pd.DataFrame() # Return empty DataFrame if column is missing
    except FileNotFoundError:
        st.error(f"File '{file_path}' tidak ditemukan. Pastikan file berada di folder yang sama dengan main.py.")
        return pd.DataFrame() # Return empty DataFrame if file is not found
    except Exception as e:
        st.error(f"Terjadi error saat membaca file Excel: {e}. Pastikan format file dan isinya valid.")
        return pd.DataFrame() # Return empty DataFrame if any other error occurs

# --- Fungsi untuk Memuat Data Pendidikan (Simulasi dari st.session_state) ---
# Ini akan tetap menggunakan st.session_state karena belum ada file Excel spesifik untuknya.
# Untuk data persisten, ini juga perlu diganti dengan koneksi database sungguhan.
@st.cache_data
def load_pendidikan_data_from_excel():
    """
    Memuat dan memproses data penduduk berdasarkan pendidikan dari file Excel.
    """
    file_path = 'Jumlah Penduduk (Pendidikan).xlsx'
    try:
        df = pd.read_excel(file_path)
        
        # Membersihkan spasi ekstra dari nama kolom
        df.columns = df.columns.str.strip()
        
        # Kolom yang wajib ada di file Excel pendidikan
        required_columns = ['Pendidikan', 'Jumlah']
        
        # Periksa apakah semua kolom yang dibutuhkan ada
        if all(col in df.columns for col in required_columns):
            # Konversi kolom 'Jumlah' menjadi numerik, ganti error dengan NaN
            df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
            
            # Hapus baris di mana data 'Jumlah' tidak valid (kosong atau bukan angka)
            df.dropna(subset=['Jumlah'], inplace=True)
            
            # Pastikan tipe data kolom jumlah adalah integer
            df['Jumlah'] = df['Jumlah'].astype(int)

            # Ganti nama kolom agar konsisten dengan halaman tampilan
            df.rename(columns={'Pendidikan': 'Tingkat Pendidikan'}, inplace=True)
            
            # Hapus kolom 'No' jika ada, karena tidak diperlukan untuk visualisasi
            if 'No' in df.columns:
                df = df.drop(columns=['No'])

            return df
        else:
            st.error(f"Satu atau lebih kolom berikut tidak ditemukan di '{file_path}': {', '.join(required_columns)}")
            return pd.DataFrame()

    except FileNotFoundError:
        st.error(f"File '{file_path}' tidak ditemukan. Pastikan file berada di folder yang sama dengan main.py.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Terjadi error saat membaca file Excel '{file_path}': {e}.")
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

    required_columns = ['No.', 'Kriteria',	'Jumlah']
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

# --- FUNGSI: Memuat Data Penduduk Menurut Jenis Kelamin dari Google Sheet ---
@st.cache_data(ttl=60)
def load_penduduk_jenis_kelamin_from_gsheet():
    """
    Memuat dan memproses data penduduk menurut jenis kelamin dari Google Sheet.

    Worksheet yang digunakan: 'Penduduk Menurut Jenis Kelamin'
    Wajib memiliki kolom: 'NO', 'RW', 'RT', 'JUMLAH KK', 'LAKI- LAKI', 'PEREMPUAN', 'JUMLAH PENDUDUK'
    """
    df = load_data_from_gsheets(WORKSHEET_NAME_PENDUDUK_JENIS_KELAMIN)
    if not df.empty:
        df.columns = df.columns.str.strip() # Membersihkan spasi di awal/akhir nama kolom

        required_columns = [
            'NO',
            'RW',
            'RT',
            'JUMLAH KK',
            'LAKI- LAKI', # Harus persis seperti di Google Sheet Anda
            'PEREMPUAN',
            'JUMLAH PENDUDUK'
        ]
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            st.error(f"Kolom yang diperlukan tidak ditemukan di worksheet '{WORKSHEET_NAME_PENDUDUK_JENIS_KELAMIN}'. "
                     f"Kolom yang hilang: {missing_cols}. "
                     f"Pastikan nama kolom di Google Sheet sudah benar (perhatikan kapitalisasi dan spasi).")
            return pd.DataFrame()

        # Konversi kolom numerik
        for col in ['NO', 'RW', 'RT', 'JUMLAH KK', 'LAKI- LAKI', 'PEREMPUAN', 'JUMLAH PENDUDUK']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.dropna(subset=['JUMLAH PENDUDUK'], inplace=True)

        # --- PERBAIKAN STANDARISASI NAMA KOLOM UNTUK ALTAR DAN PENGGUNAAN LAIN ---
        # Buat salinan DataFrame untuk menghindari SettingWithCopyWarning
        df_processed = df.copy()

        # Ubah nama kolom secara eksplisit agar konsisten dan mudah diakses
        df_processed.rename(columns={
            'NO': 'No',
            'JUMLAH KK': 'Jumlah_KK',
            'LAKI- LAKI': 'LAKI_LAKI', # Ini akan mengatasi spasi di tengah
            'JUMLAH PENDUDUK': 'Jumlah_Penduduk'
        }, inplace=True)
        
        # Tambahkan kolom gabungan RT-RW langsung di data loader
        # Ini akan memastikan 'RT_RW' selalu tersedia
        df_processed['RT_RW'] = df_processed['RT'].astype(str) + '-' + df_processed['RW'].astype(str)

        df_processed = df_processed.sort_values(by=['RW', 'RT']).reset_index(drop=True)
    return df_processed

# --- FUNGSI: Memuat Data Sarana dan Prasarana dari Google Sheet ---
@st.cache_data(ttl=60)
def load_sarana_prasarana_from_gsheet():
    """
    Memuat dan memproses data sarana dan prasarana dari Google Sheet.

    Worksheet yang digunakan: 'Sarana dan Prasarana'
    Wajib memiliki kolom: 'No.', 'Tahun', 'Jenis Sarana dan Prasarana', 'Jumlah (Unit)'
    """
    df = load_data_from_gsheets(WORKSHEET_NAME_SARANA_PRASARANA)
    if not df.empty:
        df.columns = df.columns.str.strip() # Membersihkan spasi di awal/akhir nama kolom

        required_columns = [
            'No.',
            'Tahun',
            'Jenis Sarana dan Prasarana',
            'Jumlah (Unit)'
        ]
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            st.error(f"Kolom yang diperlukan tidak ditemukan di worksheet '{WORKSHEET_NAME_SARANA_PRASARANA}'. "
                     f"Kolom yang hilang: {missing_cols}. "
                     f"Pastikan nama kolom di Google Sheet sudah benar (perhatikan kapitalisasi dan spasi).")
            return pd.DataFrame()

        # Konversi kolom numerik
        for col in ['No.', 'Tahun', 'Jumlah (Unit)']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.dropna(subset=['Jumlah (Unit)'], inplace=True) # Hapus baris dengan NaN di kolom 'Jumlah (Unit)'

        # Standarisasi nama kolom untuk Altair (mengganti spasi, tanda kurung, dan titik dengan underscore)
        df.columns = df.columns.str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_', regex=False)
        
        # Mengganti 'No._' menjadi 'No' untuk kemudahan akses
        if 'No_' in df.columns:
            df.rename(columns={'No_': 'No'}, inplace=True)

        df = df.sort_values(by=['Tahun', 'No']).reset_index(drop=True)
    return df

# --- FUNGSI: Memuat Data Sarana Kebersihan dari Google Sheet ---
@st.cache_data(ttl=60)
def load_sarana_kebersihan_from_gsheet():
    """
    Memuat dan memproses data sarana kebersihan dari Google Sheet.

    Worksheet yang digunakan: 'Sarana Kebersihan'
    Wajib memiliki kolom: 'No.', 'Jenis', 'Jumlah'
    """
    df = load_data_from_gsheets(WORKSHEET_NAME_SARANA_KEBERSIHAN)
    if not df.empty:
        df.columns = df.columns.str.strip() # Membersihkan spasi di awal/akhir nama kolom

        required_columns = [
            'No.',
            'Jenis',
            'Jumlah'
        ]
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            st.error(f"Kolom yang diperlukan tidak ditemukan di worksheet '{WORKSHEET_NAME_SARANA_KEBERSIHAN}'. "
                     f"Kolom yang hilang: {missing_cols}. "
                     f"Pastikan nama kolom di Google Sheet sudah benar (perhatikan kapitalisasi dan spasi).")
            return pd.DataFrame()

        # Konversi kolom numerik
        for col in ['No.', 'Jumlah']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.dropna(subset=['Jumlah'], inplace=True) # Hapus baris dengan NaN di kolom 'Jumlah'

        # Standarisasi nama kolom untuk Altair (mengganti spasi dan titik dengan underscore)
        df.columns = df.columns.str.replace(' ', '_').str.replace('.', '_', regex=False)
        
        # Mengganti 'No._' menjadi 'No' untuk kemudahan akses
        if 'No_' in df.columns:
            df.rename(columns={'No_': 'No'}, inplace=True)

        df = df.sort_values(by=['No']).reset_index(drop=True)
    return df

# --- FUNGSI: Memuat Data Tenaga Kerja dari Google Sheet ---
@st.cache_data(ttl=60)
def load_tenaga_kerja_from_gsheet():
    """
    Memuat dan memproses data tenaga kerja dari Google Sheet.

    Worksheet yang digunakan: 'Tenaga Kerja'
    Wajib memiliki kolom: 'No.', 'Kriteria', 'Laki-Laki (Orang)', 'Perempuan (Orang)', 'Jumlah'
    """
    df = load_data_from_gsheets(WORKSHEET_NAME_TENAGA_KERJA)
    if not df.empty:
        df.columns = df.columns.str.strip() # Membersihkan spasi di awal/akhir nama kolom

        # --- PERUBAHAN PENTING DI SINI ---
        # Sesuaikan dengan nama kolom yang persis ada di Google Sheet Anda
        required_columns = [
            'No.',
            'Kriteria',
            'Laki-Laki (Orang)',
            'Perempuan (Orang)',
            'Jumlah'
        ]
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            st.error(f"Kolom yang diperlukan tidak ditemukan di worksheet '{WORKSHEET_NAME_TENAGA_KERJA}'. "
                     f"Kolom yang hilang: {missing_cols}. "
                     f"Pastikan nama kolom di Google Sheet sudah benar (perhatikan kapitalisasi dan spasi).")
            return pd.DataFrame()

        # Konversi kolom numerik
        # Perhatikan 'No.' sekarang dengan titik
        for col in ['No.', 'Laki-Laki (Orang)', 'Perempuan (Orang)', 'Jumlah']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df.dropna(subset=['Jumlah'], inplace=True) # Hapus baris dengan NaN di kolom 'Jumlah'

        # --- PERUBAHAN PENTING DI SINI ---
        # Standarisasi nama kolom untuk Altair (mengganti spasi, tanda kurung, dan titik dengan underscore)
        # Serta mengganti 'No.' menjadi 'No' atau 'No_' untuk kemudahan akses
        df.columns = df.columns.str.replace(' ', '_').str.replace('(', '').str.replace(')', '').str.replace('.', '_', regex=False)
        # Contoh: 'Laki-Laki (Orang)' akan jadi 'Laki-Laki_Orang'
        # 'No.' akan jadi 'No_'

        # Jika Anda ingin 'No.' menjadi 'No' tanpa underscore, bisa tambahkan rename eksplisit:
        if 'No_' in df.columns:
            df.rename(columns={'No_': 'No'}, inplace=True)


        df = df.sort_values(by=['No']).reset_index(drop=True) # Urutkan berdasarkan kolom 'No' yang baru
    return df
