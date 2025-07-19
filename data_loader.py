import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# URL Google Sheets — Harus disesuaikan dengan isi file .streamlit/secrets.toml
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1NC-XuHgZ6adaTzL7XI55MnxNGCSwtGy9p8eXnF_xhzs"

# --- FUNGSI: Memuat Data Jumlah Penduduk dari Google Sheet ---
@st.cache_data
def load_penduduk_data_from_gsheet():
    """
    Memuat dan memproses data jumlah penduduk dari Google Sheet.

    Worksheet yang digunakan: 'Jumlah Penduduk'
    Wajib memiliki kolom: 'Tahun', 'Jumlah Total (orang)'
    """
    try:
        # Membuka koneksi Google Sheets sesuai secrets.toml
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Membaca worksheet
        df = conn.read(
            spreadsheet=GOOGLE_SHEET_URL,
            worksheet="Jumlah Penduduk",
            usecols=[0, 1]
        )

        # Membersihkan nama kolom
        df.columns = df.columns.str.strip()

        # Validasi keberadaan kolom yang diperlukan
        required_columns = ['Tahun', 'Jumlah Total (orang)']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Kolom {required_columns} tidak ditemukan di worksheet.")
            return pd.DataFrame()

        # Konversi jumlah ke numerik, hapus nilai kosong
        df['Jumlah Total (orang)'] = pd.to_numeric(df['Jumlah Total (orang)'], errors='coerce')
        df.dropna(subset=['Jumlah Total (orang)'], inplace=True)

        # Urutkan berdasarkan tahun
        df = df.sort_values(by='Tahun').reset_index(drop=True)
        return df

    except Exception as e:
        st.error(f"Gagal memuat data penduduk dari Google Sheets: {e}")
        return pd.DataFrame()


# --- FUNGSI: Memuat Data Pendidikan dari Google Sheet ---
@st.cache_data
def load_pendidikan_data_from_gsheet():
    """
    Memuat dan memproses data pendidikan dari Google Sheet.

    Worksheet yang digunakan: 'Jumlah Pendidikan'
    Wajib memiliki kolom: 'Pendidikan', 'Jumlah'
    """
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)

        df = conn.read(
            spreadsheet=GOOGLE_SHEET_URL,
            worksheet="Jumlah Pendidikan",
            usecols=[0, 1]
        )

        # Bersihkan kolom
        df.columns = df.columns.str.strip()

        required_columns = ['Pendidikan', 'Jumlah']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Kolom {required_columns} tidak ditemukan di worksheet.")
            return pd.DataFrame()

        # Proses angka
        df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
        df.dropna(subset=['Jumlah'], inplace=True)
        df['Jumlah'] = df['Jumlah'].astype(int)

        # Ganti nama kolom agar seragam
        df.rename(columns={'Pendidikan': 'Tingkat Pendidikan'}, inplace=True)
        return df

    except Exception as e:
        st.error(f"Gagal memuat data pendidikan dari Google Sheets: {e}")
        return pd.DataFrame()


# --- FUNGSI: Simpan Sementara ke Session State ---
def save_data_penduduk_tahun_to_session(new_row):
    """
    Simpan perubahan data penduduk secara lokal (sementara) di session_state.
    Tidak menyimpan ke Google Sheets — hanya untuk kebutuhan edit sementara.

    new_row = {'Tahun': ..., 'Jumlah Total (orang)': ...}
    """
    current_df = st.session_state.get(f'cached_{load_penduduk_data_from_gsheet.__name__}', pd.DataFrame())

    if current_df.empty:
        # Inisialisasi struktur DataFrame jika kosong
        current_df = pd.DataFrame(columns=['Tahun', 'Jumlah Total (orang)'])

    # Update jika tahun sudah ada
    if new_row['Tahun'] in current_df['Tahun'].values:
        current_df.loc[current_df['Tahun'] == new_row['Tahun'], 'Jumlah Total (orang)'] = new_row['Jumlah Total (orang)']
    else:
        # Tambah baris baru
        new_df_row = pd.DataFrame([new_row])
        current_df = pd.concat([current_df, new_df_row], ignore_index=True)

    # Urutkan ulang dan simpan kembali ke session_state
    current_df = current_df.sort_values(by='Tahun').reset_index(drop=True)
    st.session_state[f'cached_{load_penduduk_data_from_gsheet.__name__}'] = current_df
