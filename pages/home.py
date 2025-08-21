import streamlit as st

# Import semua fungsi get_chart() dari setiap halaman
from pages.jumlah_penduduk import get_penduduk_tahun_chart
from pages.jumlah_penduduk_pendidikan import get_pendidikan_chart
from pages.jenis_pekerjaan_dominan import get_jenis_pekerjaan_chart
from pages.jenis_tanah import get_jenis_tanah_chart
from pages.jumlah_industri_umkm import get_umkm_chart
from pages.jumlah_kk_menurut_rw import get_kk_rw_chart
from pages.jumlah_penduduk_status_pekerja import get_status_pekerja_chart
from pages.penduduk_disabilitas import get_disabilitas_chart
from pages.penduduk_menurut_jenis_kelamin import get_penduduk_jenis_kelamin_chart1
from pages.sarana_dan_prasarana import get_sarana_prasarana_chart
from pages.sarana_kebersihan import get_sarana_kebersihan_chart
from pages.tenaga_kerja import get_tenaga_kerja_chart

# Impor fungsi pemuat data yang diperlukan
from data_loader import load_infografis_urls_from_gsheet, load_penduduk_jenis_kelamin_gsheet, load_tenaga_kerja_from_gsheet

def display_slideshow():
    """
    Fungsi ini mengambil URL gambar dari Google Sheet dan menampilkannya
    sebagai slideshow interaktif.
    """
    image_urls = load_infografis_urls_from_gsheet()

    if not image_urls:
        st.info("Saat ini belum ada infografis untuk ditampilkan.")
        return

    if 'home_slide_index' not in st.session_state:
        st.session_state.home_slide_index = 0
    
    if st.session_state.home_slide_index >= len(image_urls):
        st.session_state.home_slide_index = 0

    st.image(image_urls[st.session_state.home_slide_index], use_container_width=True)

    col1, col2, col3 = st.columns([2, 8, 2])

    with col1:
        if st.button("⬅️ Sebelumnya", use_container_width=True, key="home_prev"):
            if st.session_state.home_slide_index > 0:
                st.session_state.home_slide_index -= 1
                st.rerun()

    with col3:
        if st.button("Berikutnya ➡️", use_container_width=True, key="home_next"):
            if st.session_state.home_slide_index < len(image_urls) - 1:
                st.session_state.home_slide_index += 1
                st.rerun()
            
    with col2:
        st.write("") 
        st.markdown(f"<p style='text-align: center; color: grey;'>Infografis {st.session_state.home_slide_index + 1} dari {len(image_urls)}</p>", unsafe_allow_html=True)


def run():
    st.title("Selamat Datang di Dashboard Kelurahan Marapalam")
    st.markdown("""
        <div style="text-align: center;">
            <p style="font-size: 1.2em;">
                Dashboard SIGEMA (Sistem Informasi Geospasial Marapalam) ini
                menyajikan berbagai visualisasi data penting mengenai kelurahan.
                Gunakan menu di sidebar untuk menjelajahi berbagai kategori data secara detail.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- Slideshow Infografis ---
    # with st.container(border=True):
    #     st.subheader("📊 Infografis Terbaru")
    #     display_slideshow()
    
    # --- Grafik Perkembangan Penduduk ---
    with st.container(border=True):
        st.subheader("📈 Trend Jumlah Penduduk Tahun 2023-2025")
        chart_penduduk_tahun = get_penduduk_tahun_chart()
        if chart_penduduk_tahun:
             st.altair_chart(chart_penduduk_tahun, use_container_width=True)
        else:
            st.info("Grafik tidak tersedia.")
        
    # --- Baris 1: Pendidikan & Pekerjaan ---
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("🎓 Distribusi Pendidikan")
            chart_pendidikan = get_pendidikan_chart()
            if chart_pendidikan:
                st.altair_chart(chart_pendidikan, use_container_width=True)
            else:
                st.info("Grafik tidak tersedia.")
    with col2:
        with st.container(border=True):
            st.subheader("👷‍♂️ Jenis Pekerjaan Dominan")
            chart_pekerjaan = get_jenis_pekerjaan_chart()
            if chart_pekerjaan:
                st.altair_chart(chart_pekerjaan, use_container_width=True)
            else:
                st.info("Grafik tidak tersedia.")
    
    # --- Baris 2: Jenis Tanah, UMKM, dan KK per RW ---
    col3, col4, col5 = st.columns(3)
    with col3:
        with st.container(border=True):
            st.subheader("🗺️ Perbandingan Jenis Tanah")
            chart_jenis_tanah = get_jenis_tanah_chart()
            if chart_jenis_tanah:
                st.altair_chart(chart_jenis_tanah, use_container_width=True)
            else:
                st.info("Grafik tidak tersedia.")
    with col4:
        with st.container(border=True):
            st.subheader("🏭 Jumlah Industri UMKM")
            chart_umkm = get_umkm_chart()
            if chart_umkm:
                st.altair_chart(chart_umkm, use_container_width=True)
            else:
                st.info("Grafik tidak tersedia.")
    with col5:
        with st.container(border=True):
            st.subheader("👨‍👩‍👧‍👦 Jumlah KK Menurut RW")
            chart_kk_rw = get_kk_rw_chart()
            if chart_kk_rw:
                st.altair_chart(chart_kk_rw, use_container_width=True)
            else:
                st.info("Grafik tidak tersedia.")

    # --- Baris 3: Status Pekerja & Disabilitas ---
    col6, col7 = st.columns(2)
    with col6:
        with st.container(border=True):
            st.subheader("👨‍💼 Proporsi Status Pekerja")
            chart_status_pekerja = get_status_pekerja_chart()
            if chart_status_pekerja:
                st.altair_chart(chart_status_pekerja, use_container_width=True)
            else:
                st.info("Grafik tidak tersedia.")
    with col7:
        with st.container(border=True):
            st.subheader("♿ Jumlah Disabilitas")
            chart_disabilitas = get_disabilitas_chart()
            if chart_disabilitas:
                st.altair_chart(chart_disabilitas, use_container_width=True)
            else:
                st.info("Grafik tidak tersedia.")

    # --- Grafik Jenis Kelamin ---
    with st.container(border=True):
        st.subheader("♀️ /♂️ Jumlah Penduduk Menurut Jenis Kelamin")
        df_penduduk_jk_home = load_penduduk_jenis_kelamin_gsheet()
        chart_kelamin = get_penduduk_jenis_kelamin_chart1(df_penduduk_jk_home)
        if chart_kelamin:
            st.altair_chart(chart_kelamin, use_container_width=True)
        else:
            st.info("Grafik Jumlah Penduduk Menurut Jenis Kelamin tidak tersedia atau data kosong.")
    
    # --- Baris 4: Sarana & Prasarana dan Kebersihan ---
    col8, col9 = st.columns(2)
    with col8:
        with st.container(border=True):
            st.subheader("🏢 Sarana dan Prasarana")
            chart_sarana = get_sarana_prasarana_chart()
            if chart_sarana:
                st.altair_chart(chart_sarana, use_container_width=True)
            else:
                st.info("Grafik tidak tersedia.")
    with col9:
        with st.container(border=True):
            st.subheader("🗑️ Sarana Kebersihan")
            chart_kebersihan = get_sarana_kebersihan_chart()
            if chart_kebersihan:
                st.altair_chart(chart_kebersihan, use_container_width=True)
            else:
                st.info("Grafik tidak tersedia.")

    # --- Grafik Tenaga Kerja ---
    with st.container(border=True):
        st.subheader("✊ Tenaga Kerja")
        df = load_tenaga_kerja_from_gsheet()
        chart_tenaga = get_tenaga_kerja_chart(df)
        if chart_tenaga:
            st.altair_chart(chart_tenaga, use_container_width=True)
        else:
            st.info("Grafik Tenaga Kerja tidak tersedia atau data kosong.")

    st.write("Dibuat oleh @Tim_Cihuy")