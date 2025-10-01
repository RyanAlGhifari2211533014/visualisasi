# pages/Klastering.py

import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import io
from data_loader import load_data_from_gsheets, get_gsheets_connection

# --- NAMA WORKSHEET ---
WORKSHEET_MENTAH = "CMentah"
WORKSHEET_BERSIH = "HClastering"
WORKSHEET_HASIL_Kepadatan = "CKepadatan"
WORKSHEET_HASIL_Demografi = "Cdemografi"

# --- FUNGSI PEMBANTU UNTUK DOWNLOAD EXCEL ---
def to_excel(df):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Hasil Klastering')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

# --- FUNGSI UTAMA HALAMAN ---
def run():
    # <<< DITAMBAHKAN: Blok untuk memuat hasil terakhir saat halaman dibuka >>>
    # Logika ini hanya berjalan satu kali untuk memuat data dari Google Sheets
    if 'init_load_complete' not in st.session_state:
        # 1. Coba muat data bersih terakhir
        df_bersih_terakhir = load_data_from_gsheets(WORKSHEET_BERSIH)
        if not df_bersih_terakhir.empty:
            st.session_state['data_bersih'] = df_bersih_terakhir

        # 2. Coba muat hasil analisis kepadatan terakhir
        df_kepadatan_terakhir = load_data_from_gsheets(WORKSHEET_HASIL_Kepadatan)
        if not df_kepadatan_terakhir.empty:
            st.session_state['hasil_akhir_kepadatan'] = df_kepadatan_terakhir
        
        # 3. Coba muat hasil analisis demografi terakhir
        df_demografi_terakhir = load_data_from_gsheets(WORKSHEET_HASIL_Demografi)
        if not df_demografi_terakhir.empty:
            st.session_state['hasil_akhir_demografi'] = df_demografi_terakhir
        
        st.toast("Data & hasil analisis terakhir berhasil dimuat.", icon="")
        # Tandai bahwa proses muat awal sudah selesai
        st.session_state['init_load_complete'] = True

    st.title("Halaman Proses Klastering")
    st.header("1. Input dan Bersihkan Data")
    st.info(
           """
    Memasukan Data Baru

    Langkah 1 : Tekan tombol Masukan / Ubah data
    
    Langkah 2 : Pastikan Data di dalam Google Sheet Kosong
    
    Langkah 3 : Jika terdapat data maka tekan ctrl + A bersamaan lalu hapus semua data
    
    Langkah 4 : Setelah pasti data sudah kosong anda hanya perlu Copy paste data yang anda ingin proses ke halaman google sheet
    
    Langkah 5 : Kembali ke halaman Web
    
    Langkah 6 : Tekan Tombol preprocessing data untuk memulai
    
    Langkah 7 : Setelah preprocessing selesai tekan tombol Jalankan Analisis di bawah table Analisis Kepadatan atau Analisis Demografi
    
    Langkah 8 : Hasil kelastering akan muncul di dalam table
    
    Langkah 9 : Lihat menu paling bawah di table hasil tiap kalstering pilih simpan data ke Google sheet
    
    Langkah 10 : Setelah selsai mengikuti, Anda sudah berhasil melakukan Clustering data
    
    Langkah 11 : Selamat Mencoba
    """
    
    )

    col1, col2 = st.columns(2)
    with col1:
        link_google_sheet = "https://docs.google.com/spreadsheets/d/1NqSvNpPpCtrhVGsIADEg-SNO5KKASq22vDbY0CndsQQ/edit?gid=1142471842#gid=1142471842"
        st.markdown(
            f'<a href="{link_google_sheet}" target="_blank" style="text-decoration: none;">'
            f'<button style="width:100%; background-color:#28a745;color:white;padding:12px 24px;border:none;border-radius:8px;cursor:pointer;font-size:16px;">'
            f'Masukkan/Ubah Data'
            f'</button></a>', unsafe_allow_html=True
        )

    with col2:
        if st.button("Preprocessing Data", type="secondary", use_container_width=True):
            with st.spinner("Mohon tunggu... Melakukan preprocessing..."):
                df_mentah = load_data_from_gsheets(WORKSHEET_MENTAH)
                if not df_mentah.empty:
                    df_processed = df_mentah.copy()
                    df_processed.dropna(inplace=True)
                    df_processed.drop_duplicates(inplace=True)
                    df_processed.reset_index(drop=True, inplace=True)
                    
                    df_processed.columns = df_processed.columns.str.strip().str.lower().str.replace(' ', '_', regex=False)

                    try:
                        conn = get_gsheets_connection()
                        conn.update(worksheet=WORKSHEET_BERSIH, data=df_processed)
                        st.success(f"Preprocessing berhasil! Data bersih disimpan di '{WORKSHEET_BERSIH}'.")
                        st.session_state['data_bersih'] = df_processed
                        if 'hasil_akhir_kepadatan' in st.session_state: del st.session_state['hasil_akhir_kepadatan']
                        if 'hasil_akhir_demografi' in st.session_state: del st.session_state['hasil_akhir_demografi']
                    except Exception as e:
                        st.error(f"Gagal menyimpan data. Pastikan worksheet '{WORKSHEET_BERSIH}' ada. Detail: {e}")
                else:
                    st.error(f"Gagal memuat data dari '{WORKSHEET_MENTAH}'.")

    st.markdown("---")

    if 'data_bersih' in st.session_state:
        st.header("2. Analisis Klastering Kepadatan Penduduk")
        st.write("Data bersih yang siap untuk dianalisis:")
        st.dataframe(st.session_state['data_bersih'])

        if st.button("Jalankan Klastering Kepadatan", type="primary"):
            with st.spinner("Menjalankan algoritma Klastering Kepadatan penduduk..."):
                df_bersih = st.session_state['data_bersih']
                numeric_cols = df_bersih.select_dtypes(include=['number']).columns.tolist()
                
                if 'rw' in numeric_cols: numeric_cols.remove('rw')
                
                if not numeric_cols:
                    st.error("Tidak ditemukan kolom data numerik untuk analisis.")
                else:
                    data_for_clustering = df_bersih[numeric_cols]
                    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
                    kmeans.fit(data_for_clustering)
                    df_hasil = df_bersih.copy()
                    df_hasil['Klaster'] = kmeans.labels_
                    
                    cluster_means = df_hasil.groupby('Klaster')[numeric_cols].mean()
                    cluster_scores = cluster_means.sum(axis=1)
                    sorted_clusters = cluster_scores.sort_values().index
                    label_mapping = {sorted_clusters[0]: 'Sepi', sorted_clusters[1]: 'Normal', sorted_clusters[2]: 'Padat'}
                    
                    df_hasil['Label'] = df_hasil['Klaster'].map(label_mapping)
                    
                    st.success("Analisis Klastering Kepadatan Selesai!")
                    st.session_state['hasil_akhir_kepadatan'] = df_hasil

    if 'hasil_akhir_kepadatan' in st.session_state:
        st.header("3. Hasil Kalstering Kepadatan Penduduk")
        df_final_kepadatan = st.session_state['hasil_akhir_kepadatan']
        
        if 'rw' in df_final_kepadatan.columns:
            kolom_utama = ['rw', 'Klaster', 'Label']
        else:
            kolom_utama = ['Klaster', 'Label']
            
        kolom_lain = [kol for kol in df_final_kepadatan.columns if kol not in kolom_utama]
        st.dataframe(df_final_kepadatan[kolom_utama + kolom_lain])

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Simpan Hasil Kepadatan", use_container_width=True):
                with st.spinner("Menyimpan hasil kepadatan..."):
                    conn = get_gsheets_connection()
                    conn.update(worksheet=WORKSHEET_HASIL_Kepadatan, data=df_final_kepadatan)
                    st.success(f"Hasil berhasil disimpan di worksheet '{WORKSHEET_HASIL_Kepadatan}'!")
        with col2:
            excel_data = to_excel(df_final_kepadatan)
            st.download_button(label="Download Hasil Kepadatan", data=excel_data, file_name="hasil_kepadatan.xlsx", use_container_width=True)

        st.markdown("---")
        
        st.header("Analisis Klastering Demografi dan Prencanaan Sosial")
        if st.button("Jalankan Analisis"):
            with st.spinner("Menjalankan Analisis Demografi..."):
                df_bersih = st.session_state['data_bersih']
                
                required_cols = ['total_penduduk', 'jumlah_kk']
                if not all(col in df_bersih.columns for col in required_cols):
                    st.error(f"Gagal! Data tidak memiliki kolom '{required_cols[0]}' dan '{required_cols[1]}'.")
                else:
                    df_demografi = df_bersih.copy()
                    df_demografi['rata2_anggota_keluarga'] = df_demografi['total_penduduk'] / (df_demografi['jumlah_kk'] + 1e-6)
                    
                    data_for_clustering_demo = df_demografi[['rata2_anggota_keluarga']]
                    kmeans_demo = KMeans(n_clusters=3, random_state=42, n_init=10)
                    kmeans_demo.fit(data_for_clustering_demo)
                    
                    df_demografi['Klaster_Demografi'] = kmeans_demo.labels_
                    cluster_means_demo = df_demografi.groupby('Klaster_Demografi')['rata2_anggota_keluarga'].mean()
                    sorted_clusters_demo = cluster_means_demo.sort_values().index
                    label_mapping_demo = {sorted_clusters_demo[0]: 'Keluarga Kecil', sorted_clusters_demo[1]: 'Keluarga Sedang', sorted_clusters_demo[2]: 'Keluarga Besar'}
                    
                    df_demografi['Label_Demografi'] = df_demografi['Klaster_Demografi'].map(label_mapping_demo)
                    
                    st.success("Analisis Selesai!")
                    st.session_state['hasil_akhir_demografi'] = df_demografi

    if 'hasil_akhir_demografi' in st.session_state:
        st.subheader("Hasil Analisis")
        df_final_demografi = st.session_state['hasil_akhir_demografi']
        
        kolom_tampil = ['rw', 'Label_Demografi', 'rata2_anggota_keluarga', 'total_penduduk', 'jumlah_kk']
        st.dataframe(df_final_demografi[kolom_tampil])
        
        col3, col4 = st.columns(2)
        with col3:
            if st.button("Simpan Hasil Demografi", use_container_width=True):
                with st.spinner("Menyimpan hasil demografi..."):
                    conn = get_gsheets_connection()
                    conn.update(worksheet=WORKSHEET_HASIL_Demografi, data=df_final_demografi)
                    st.success(f"Hasil berhasil disimpan di worksheet '{WORKSHEET_HASIL_Demografi}'!")
        with col4:
            excel_data_demo = to_excel(df_final_demografi)
            st.download_button(label=" Download Hasil Demografi", data=excel_data_demo, file_name="hasil_demografi.xlsx", use_container_width=True)