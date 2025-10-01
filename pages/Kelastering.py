# pages/Klastering.py

import streamlit as st
import pandas as pd
from sklearn.cluster import KMeans
import io
from data_loader import load_data_from_gsheets, get_gsheets_connection

# --- NAMA WORKSHEET ---
WORKSHEET_MENTAH = "CMentah"
WORKSHEET_BERSIH = "HClastering"
WORKSHEET_HASIL = "CKepadatan"

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
    st.title("⚙️ Halaman Proses Klastering")
    st.header("1. Input dan Preprocessing Data")
    st.info(
        "**Langkah A:** Klik **'Masukkan/Ubah Data'** untuk mengedit data di worksheet **CMentah**.\n\n"
        "**Langkah B:** Jika sudah, klik **'Preprocessing Data'** untuk memulai pembersihan."
    )

    col1, col2 = st.columns(2)
    with col1:
        link_google_sheet = "https://docs.google.com/spreadsheets/d/1NqSvNpPpCtrhVGsIADEg-SNO5KKASq22vDbY0CndsQQ/edit?gid=1142471842#gid=1142471842"
        st.markdown(
            f'<a href="{link_google_sheet}" target="_blank" style="text-decoration: none;">'
            f'<button style="width:100%; background-color:#28a745;color:white;padding:12px 24px;border:none;border-radius:8px;cursor:pointer;font-size:16px;">'
            f'🔗 Masukkan/Ubah Data'
            f'</button></a>', unsafe_allow_html=True
        )

    with col2:
        if st.button("🔍 Preprocessing Data", type="secondary", use_container_width=True):
            with st.spinner("Mohon tunggu... Melakukan preprocessing..."):
                df_mentah = load_data_from_gsheets(WORKSHEET_MENTAH)
                if not df_mentah.empty:
                    df_processed = df_mentah.copy()
                    df_processed.dropna(inplace=True)
                    df_processed.drop_duplicates(inplace=True)
                    df_processed.reset_index(drop=True, inplace=True)
                    
                    # === BAGIAN INI DIKEMBALIKAN KE VERSI YANG BENAR ===
                    # Langsung mencoba menulis data dan menangkap error jika gagal.
                    # Ini cara yang lebih sederhana dan efektif.
                    try:
                        conn = get_gsheets_connection()
                        conn.update(worksheet=WORKSHEET_BERSIH, data=df_processed)
                        st.success(f"✅ Preprocessing berhasil! Data bersih disimpan di '{WORKSHEET_BERSIH}'.")
                        st.session_state['data_bersih'] = df_processed
                        if 'hasil_akhir' in st.session_state:
                            del st.session_state['hasil_akhir']
                    except Exception as e:
                        # Pesan error ini akan otomatis memberitahu jika worksheet tidak ditemukan.
                        st.error(f"Gagal menyimpan data. Pastikan worksheet '{WORKSHEET_BERSIH}' ada dan izin sudah benar. Detail: {e}")
                else:
                    st.error(f"Gagal memuat data dari '{WORKSHEET_MENTAH}'.")

    st.markdown("---")

    # --- TAHAP 2: ANALISIS K-MEANS ---
    if 'data_bersih' in st.session_state:
        st.header("2. Analisis K-Means")
        st.write(f"Berikut adalah data dari worksheet **'{WORKSHEET_BERSIH}'** yang siap untuk dianalisis.")
        st.dataframe(st.session_state['data_bersih'])

        if st.button("🚀 Jalankan Klastering K-Means", type="primary"):
            with st.spinner("Sistem sedang menjalankan algoritma K-Means..."):
                df_bersih = st.session_state['data_bersih']
                numeric_cols = df_bersih.select_dtypes(include=['number']).columns.tolist()
                
                if 'RW' in numeric_cols:
                    numeric_cols.remove('RW')
                
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
                    
                    label_mapping = {
                        sorted_clusters[0]: 'Sepi',
                        sorted_clusters[1]: 'Normal',
                        sorted_clusters[2]: 'Padat'
                    }
                    df_hasil['Label'] = df_hasil['Klaster'].map(label_mapping)
                    
                    st.success("✅ Analisis K-Means Selesai!")
                    st.session_state['hasil_akhir'] = df_hasil

    # --- TAHAP 3: TAMPILKAN HASIL AKHIR, SIMPAN, DAN DOWNLOAD ---
    if 'hasil_akhir' in st.session_state:
        st.header("3. Hasil Akhir Klastering")
        df_final = st.session_state['hasil_akhir']
        
        if 'RW' in df_final.columns:
            kolom_utama = ['RW', 'Klaster', 'Label']
        else:
            kolom_utama = ['Klaster', 'Label']
        kolom_lain = [kol for kol in df_final.columns if kol not in kolom_utama]
        st.dataframe(df_final[kolom_utama + kolom_lain])

        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Simpan Hasil ke Google Sheets", use_container_width=True):
                with st.spinner("Menyimpan hasil..."):
                    try:
                        conn = get_gsheets_connection()
                        conn.update(worksheet=WORKSHEET_HASIL, data=df_final)
                        st.success(f"Hasil berhasil disimpan di worksheet '{WORKSHEET_HASIL}'!")
                    except Exception as e:
                        st.error(f"Gagal menyimpan hasil. Pastikan worksheet '{WORKSHEET_HASIL}' ada. Detail: {e}")
        
        with col2:
            excel_data = to_excel(df_final)
            st.download_button(
                label="📄 Download Hasil (Excel)",
                data=excel_data,
                file_name="hasil_klastering_kepadatan.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )