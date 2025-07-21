import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# ✅ Mengambil URL spreadsheet dari secrets.toml
# Ini adalah URL lengkap Google Sheet (misalnya, https://docs.google.com/spreadsheets/d/ID_SPREADSHEET_ANDA/edit...).
# Nilai ini diambil dari bagian 'connections.gsheets' di file secrets.toml Anda.
GOOGLE_SHEET_URL = st.secrets["connections"]["gsheets"]["spreadsheet"]

# --- FUNGSI: Memuat Data Jumlah Penduduk dari Google Sheet ---
@st.cache_data
def load_penduduk_data_from_gsheet():
    """
    Memuat dan memproses data jumlah penduduk dari Google Sheet.

    Worksheet yang digunakan: 'Jumlah Penduduk (2020-2025)'
    Wajib memiliki kolom: 'Tahun', 'Jumlah Laki-Laki (orang)', 'Jumlah Perempuan (orang)', 'Jumlah Total (orang)', 'Jumlah Kepala Keluarga (KK)'
    """
    try:
        # Membuka koneksi Google Sheets sesuai secrets.toml.
        # 'gsheets' di sini merujuk pada nama koneksi yang didefinisikan di [connections.gsheets].
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Membaca data dari worksheet yang spesifik dalam spreadsheet yang ditentukan URL-nya.
        # worksheet="Jumlah Penduduk (2020-2025)" adalah nama TAB di dalam Google Sheet "DATABASE".
        df = conn.read(
            spreadsheet=GOOGLE_SHEET_URL,
            worksheet="Jumlah Penduduk (2020-2025)", # <--- Pastikan nama tab ini PERSIS sama di Google Sheet "DATABASE" Anda
            # usecols=None # Menghapus usecols agar semua kolom yang ada di sheet dimuat.
            # Atau bisa juga specify kolom yang ingin diambil jika tidak semua dibutuhkan:
            # usecols=['Tahun', 'Jumlah Laki-Laki (orang)', 'Jumlah Perempuan (orang)', 'Jumlah Total (orang)', 'Jumlah Kepala Keluarga (KK)']
            # Namun, karena ada validasi di bawah, memuat semua lebih aman jika memang semua akan dicek.
        )

        # Membersihkan nama kolom (menghilangkan spasi ekstra) untuk penanganan yang konsisten.
        df.columns = df.columns.str.strip()

        # Validasi keberadaan kolom yang diperlukan.
        # Nama kolom harus PERSIS sama dengan yang ada di header Google Sheet Anda (termasuk kapitalisasi).
        required_columns = [
            'Tahun',
            'Jumlah Laki-Laki (orang)',
            'Jumlah Perempuan (orang)',
            'Jumlah Total (orang)',
            'Jumlah Kepala Keluarga (KK)'
        ]
        if not all(col in df.columns for col in required_columns):
            missing_cols = [col for col in required_columns if col not in df.columns]
            st.error(f"Kolom yang diperlukan tidak ditemukan di worksheet 'Jumlah Penduduk (2020-2025)'. "
                     f"Kolom yang hilang: {missing_cols}. "
                     f"Pastikan nama kolom di Google Sheet sudah benar (perhatikan kapitalisasi dan spasi).")
            return pd.DataFrame()

        # Konversi kolom numerik ke tipe data numerik.
        # 'errors="coerce"' akan mengubah nilai yang tidak bisa dikonversi menjadi NaN (Not a Number).
        # Menghapus baris yang memiliki nilai NaN di kolom 'Jumlah Total (orang)' (yaitu, data yang gagal dikonversi atau kosong).
        # Ini penting agar perhitungan atau visualisasi tidak error.
        df['Jumlah Laki-Laki (orang)'] = pd.to_numeric(df['Jumlah Laki-Laki (orang)'], errors='coerce')
        df['Jumlah Perempuan (orang)'] = pd.to_numeric(df['Jumlah Perempuan (orang)'], errors='coerce')
        df['Jumlah Total (orang)'] = pd.to_numeric(df['Jumlah Total (orang)'], errors='coerce')
        df['Jumlah Kepala Keluarga (KK)'] = pd.to_numeric(df['Jumlah Kepala Keluarga (KK)'], errors='coerce')

        # Hapus baris di mana 'Jumlah Total (orang)' adalah NaN
        df.dropna(subset=['Jumlah Total (orang)'], inplace=True)

        # Urutkan DataFrame berdasarkan kolom 'Tahun' secara ascending dan reset indeksnya.
        df = df.sort_values(by='Tahun').reset_index(drop=True)
        return df

    except Exception as e:
        # Menampilkan pesan error yang lebih informatif jika terjadi masalah saat memuat data.
        st.error(f"Gagal memuat data penduduk dari Google Sheets. Pastikan: "
                 f"\n- Nama tab/worksheet di Google Sheet Anda adalah 'Jumlah Penduduk (2020-2025)' (perhatikan kapitalisasi, spasi, tanda kurung)."
                 f"\n- Kolom header di tab tersebut PERSIS sama dengan daftar yang Anda berikan (Tahun, Jumlah Laki-Laki (orang), dll.)."
                 f"\n- Akun layanan Google Anda memiliki akses 'Pelihat' atau 'Editor' ke spreadsheet ini."
                 f"\n- URL spreadsheet di .streamlit/secrets.toml sudah benar."
                 f"\nDetail kesalahan: {e}")
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
        # Membuka koneksi Google Sheets menggunakan nama koneksi yang sama.
        conn = st.connection("gsheets", type=GSheetsConnection)

        # Membaca worksheet 'Jumlah Pendidikan'.
        df = conn.read(
            spreadsheet=GOOGLE_SHEET_URL,
            worksheet="Jumlah Pendidikan", # <--- Pastikan nama tab ini PERSIS sama di Google Sheet "DATABASE" Anda
            usecols=[0, 1]
        )

        # Bersihkan nama kolom.
        df.columns = df.columns.str.strip()

        # Validasi keberadaan kolom yang diperlukan.
        required_columns = ['Pendidikan', 'Jumlah']
        if not all(col in df.columns for col in required_columns):
            st.error(f"Kolom {required_columns} tidak ditemukan di worksheet 'Jumlah Pendidikan'. Pastikan nama kolom di Google Sheet sudah benar.")
            return pd.DataFrame()

        # Proses angka: konversi ke numerik dan pastikan integer.
        df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce')
        df.dropna(subset=['Jumlah'], inplace=True)
        df['Jumlah'] = df['Jumlah'].astype(int) # Mengonversi ke integer setelah membersihkan NaN

        # Ganti nama kolom 'Pendidikan' menjadi 'Tingkat Pendidikan' agar seragam dengan penamaan di aplikasi.
        df.rename(columns={'Pendidikan': 'Tingkat Pendidikan'}, inplace=True)
        return df

    except Exception as e:
        st.error(f"Gagal memuat data pendidikan dari Google Sheets. Pastikan: "
                 f"\n- Nama tab/worksheet di Google Sheet Anda adalah 'Jumlah Pendidikan' (perhatikan kapitalisasi, spasi)."
                 f"\n- Kolom header di tab tersebut adalah 'Pendidikan' dan 'Jumlah'."
                 f"\n- Akun layanan Google Anda memiliki akses 'Pelihat' atau 'Editor' ke spreadsheet ini."
                 f"\n- URL spreadsheet di .streamlit/secrets.toml sudah benar."
                 f"\nDetail kesalahan: {e}")
        return pd.DataFrame()


# --- FUNGSI: Simpan Sementara ke Session State ---
def save_data_penduduk_tahun_to_session(new_row):
    """
    Simpan perubahan data penduduk secara lokal (sementara) di session_state.
    Ini TIDAK menyimpan perubahan ke Google Sheets — hanya untuk kebutuhan edit sementara di UI.

    new_row = {'Tahun': ..., 'Jumlah Laki-Laki (orang)': ..., 'Jumlah Perempuan (orang)': ..., 'Jumlah Total (orang)': ..., 'Jumlah Kepala Keluarga (KK)': ...}
    """
    # Mengambil DataFrame yang sudah ada dari session_state atau DataFrame kosong jika belum ada.
    # Nama kunci session_state disesuaikan dengan nama fungsi load_penduduk_data_from_gsheet
    # untuk koherensi dengan st.cache_data jika digunakan dengan session_state.
    current_df = st.session_state.get(f'cached_{load_penduduk_data_from_gsheet.__name__}', pd.DataFrame())

    if current_df.empty:
        # Inisialisasi struktur DataFrame jika saat ini kosong dengan kolom yang diharapkan.
        current_df = pd.DataFrame(columns=[
            'Tahun',
            'Jumlah Laki-Laki (orang)',
            'Jumlah Perempuan (orang)',
            'Jumlah Total (orang)',
            'Jumlah Kepala Keluarga (KK)'
        ])

    # Memeriksa apakah 'Tahun' dari new_row sudah ada di DataFrame yang ada.
    if new_row['Tahun'] in current_df['Tahun'].values:
        # Jika tahun sudah ada, perbarui semua nilai kolom yang relevan.
        for col in new_row:
            current_df.loc[current_df['Tahun'] == new_row['Tahun'], col] = new_row[col]
    else:
        # Jika tahun belum ada, tambahkan baris baru ke DataFrame.
        new_df_row = pd.DataFrame([new_row])
        current_df = pd.concat([current_df, new_df_row], ignore_index=True)

    # Urutkan kembali DataFrame berdasarkan 'Tahun' dan simpan kembali ke session_state.
    current_df = current_df.sort_values(by='Tahun').reset_index(drop=True)
    st.session_state[f'cached_{load_penduduk_data_from_gsheet.__name__}'] = current_df