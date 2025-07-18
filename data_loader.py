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
def load_data_pendidikan():
    """
    Loads education data. Currently from st.session_state (temporary).
    For persistent data, replace with actual database connection.
    """
    # Inisialisasi data dummy jika belum ada di session_state (untuk demo)
    if 'data_pendidikan' not in st.session_state:
        st.session_state.data_pendidikan = pd.DataFrame({
            'Tingkat Pendidikan': ['SD', 'SMP', 'SMA', 'Diploma', 'Sarjana', 'Pascasarjana'],
            'Jumlah': [3000, 2500, 2000, 800, 1200, 300]
        })
    return st.session_state.data_pendidikan

# Fungsi untuk menyimpan data penduduk tahunan (simulasi ke st.session_state)
# PENTING: Ini hanya memengaruhi sesi saat ini, BUKAN file Excel asli.
# Untuk persistensi, ini harus diganti dengan operasi ke database sungguhan.
def save_data_penduduk_tahun_to_session(new_row):
    """
    Saves new/updated population data to st.session_state (temporary).
    For persistent storage, replace with database write operations.
    """
    # Get the current cached data
    current_df = st.session_state.get(f'cached_{load_penduduk_data_from_excel.__name__}', pd.DataFrame())
    
    # If the current_df is empty, initialize it with columns
    if current_df.empty:
        current_df = pd.DataFrame(columns=['Tahun', 'Jumlah Total (orang)'])

    # Check if the year already exists
    if new_row['Tahun'] in current_df['Tahun'].values:
        # Update existing row
        current_df.loc[current_df['Tahun'] == new_row['Tahun'], 'Jumlah Total (orang)'] = new_row['Jumlah Total (orang)']
    else:
        # Add new row
        new_df_row = pd.DataFrame([new_row])
        current_df = pd.concat([current_df, new_df_row], ignore_index=True)
    
    # Sort and reset index
    current_df = current_df.sort_values(by='Tahun').reset_index(drop=True)
    
    # Update the cached data in session state
    st.session_state[f'cached_{load_penduduk_data_from_excel.__name__}'] = current_df

