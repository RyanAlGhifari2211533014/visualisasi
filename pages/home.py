import streamlit as st

# Import fungsi get_chart() dari setiap halaman
# Pastikan Anda sudah membuat fungsi get_chart_name() di setiap file halaman yang relevan
# dan mereka mengembalikan objek Altair Chart (atau None jika data kosong/error).
from pages.jumlah_penduduk_2020_2025 import get_penduduk_tahun_chart
from pages.jumlah_penduduk_pendidikan import get_pendidikan_chart
from pages.jenis_pekerjaan_dominan import get_jenis_pekerjaan_chart
from pages.jenis_tanah import get_jenis_tanah_chart
from pages.jumlah_industri_umkm import get_umkm_chart
from pages.jumlah_kk_menurut_rw import get_kk_rw_chart
from pages.jumlah_penduduk_status_pekerja import get_status_pekerja_chart
from pages.penduduk_disabilitas import get_disabilitas_chart

# PENTING: Impor fungsi pemuat data yang diperlukan untuk grafik di home.py
from data_loader import load_penduduk_jenis_kelamin_gsheet # <-- Pastikan baris ini ada dan benar
from data_loader import load_tenaga_kerja_from_gsheet
from pages.penduduk_menurut_jenis_kelamin import get_penduduk_jenis_kelamin_chart

from pages.sarana_dan_prasarana import get_sarana_prasarana_chart
from pages.sarana_kebersihan import get_sarana_kebersihan_chart
from pages.tenaga_kerja import get_tenaga_kerja_chart
# Tambahkan impor untuk halaman lain yang ingin Anda tampilkan grafiknya di home.py
# ... dan seterusnya untuk semua halaman yang relevan

def run():
    """
    Renders the Home page content with summary charts.
    """
    st.title("Selamat Datang di Dashboard Data Kelurahan 👋")
    st.markdown("""
        <div style="text-align: center;">
            <p style="font-size: 1.2em;">
                Dashboard ini menyajikan berbagai visualisasi data penting mengenai kelurahan Anda.
                Gunakan menu di sidebar untuk menjelajahi berbagai kategori data secara detail.
            </p>
            <p style="font-size: 1.1em; color: #555;">
                Berikut adalah ringkasan grafik utama:
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # --- Tampilkan Grafik dari Halaman Lain ---

    # Grafik Jumlah Penduduk (2020-2025)
    st.subheader("📈 Perkembangan Jumlah Penduduk")
    chart_penduduk_tahun = get_penduduk_tahun_chart()
    if chart_penduduk_tahun:
        st.altair_chart(chart_penduduk_tahun, use_container_width=True)
    else:
        st.info("Grafik jumlah penduduk tidak tersedia atau data kosong.")
    st.markdown("---")

    # Grafik Jumlah Penduduk (Pendidikan)
    st.subheader("🎓 Distribusi Penduduk Berdasarkan Pendidikan")
    chart_pendidikan = get_pendidikan_chart()
    if chart_pendidikan:
        st.altair_chart(chart_pendidikan, use_container_width=True)
    else:
        st.info("Grafik pendidikan tidak tersedia atau data kosong.")
    st.markdown("---")

    # Grafik Jenis Pekerjaan Dominan
    st.subheader("👷‍♂️ Jenis Pekerjaan Dominan")
    chart_pekerjaan = get_jenis_pekerjaan_chart()
    if chart_pekerjaan:
        st.altair_chart(chart_pekerjaan, use_container_width=True)
    else:
        st.info("Grafik jenis pekerjaan tidak tersedia atau data kosong.")
    st.markdown("---")

    # Grafik Jenis Tanah
    st.subheader("🗺️ Perbandingan Luas Berbagai Jenis Tanah")
    chart_jenis_tanah = get_jenis_tanah_chart()
    if chart_jenis_tanah:
        st.altair_chart(chart_jenis_tanah, use_container_width=True)
    else:
        st.info("Grafik jenis tanah tidak tersedia atau data kosong.")
    st.markdown("---")

    # Grafik Jumlah Industri UMKM
    st.subheader("🏭 Jumlah Industri UMKM")
    chart_umkm = get_umkm_chart()
    if chart_umkm:
        st.altair_chart(chart_umkm, use_container_width=True)
    else:
        st.info("Grafik UMKM tidak tersedia atau data kosong.")
    st.markdown("---")

    # Grafik Jumlah KK Menurut RW
    st.subheader("👨‍👩‍👧‍👦 Jumlah Kepala Keluarga (KK) per RW")
    chart_kk_rw = get_kk_rw_chart()
    if chart_kk_rw:
        st.altair_chart(chart_kk_rw, use_container_width=True)
    else:
        st.info("Grafik jumlah KK per RW tidak tersedia atau data kosong.")
    st.markdown("---")

    # Grafik Jumlah Penduduk (Status Pekerja)
    st.subheader("👨‍💼 Proporsi Penduduk Berdasarkan Status Pekerjaan")
    chart_status_pekerja = get_status_pekerja_chart()
    if chart_status_pekerja:
        st.altair_chart(chart_status_pekerja, use_container_width=True)
    else:
        st.info("Grafik status pekerja tidak tersedia atau data kosong.")
    st.markdown("---")

    # Grafik Penduduk Disabilitas
    st.subheader("♿ Jumlah Penyandang Disabilitas")
    chart_disabilitas = get_disabilitas_chart()
    if chart_disabilitas:
        st.altair_chart(chart_disabilitas, use_container_width=True)
    else:
        st.info("Grafik disabilitas tidak tersedia atau data kosong.")
    st.markdown("---")

    # Grafik Jumlah Penduduk Menurut Jenis Kelamin
    st.subheader("⚧ Jumlah Penduduk Menurut Jenis Kelamin")
    # Perbaikan: Muat data terlebih dahulu sebelum memanggil fungsi grafik
    df_penduduk_jk_home = load_penduduk_jenis_kelamin_gsheet() # <-- Baris ini memuat data
    chart_kelamin = get_penduduk_jenis_kelamin_chart(df_penduduk_jk_home) # <-- Baris ini meneruskan data
    if chart_kelamin:
        st.altair_chart(chart_kelamin, use_container_width=True)
    else:
        st.info("Grafik Jumlah Penduduk Menurut Jenis Kelamin tidak tersedia atau data kosong.")
    st.markdown("---")

    # Grafik sarana dan prasarana
    st.subheader("🏢 Sarana dan Prasarana")
    chart_sarana = get_sarana_prasarana_chart()
    if chart_sarana:
        st.altair_chart(chart_sarana, use_container_width=True)
    else:
        st.info("Grafik Sarana dan Prasarana tidak tersedia atau data kosong.")
    st.markdown("---")

    # Grafik sarana kebersihan
    st.subheader("🗑️ Sarana Kebersihan")
    chart_kebersihan = get_sarana_kebersihan_chart()
    if chart_kebersihan:
        st.altair_chart(chart_kebersihan, use_container_width=True)
    else:
        st.info("Grafik Sarana kebersihan tidak tersedia atau data kosong.")
    st.markdown("---")

    # Grafik tenaga kerja
    st.subheader("✊ Tenaga Kerja")
    df = load_tenaga_kerja_from_gsheet() # <-- Baris ini memuat data
    chart_tenaga = get_tenaga_kerja_chart(df)
    if chart_tenaga:
        st.altair_chart(chart_tenaga, use_container_width=True)
    else:
        st.info("Grafik Tenaga Kerja tidak tersedia atau data kosong.")
    st.markdown("---")

    st.write("Dibuat oleh @TimCihuy")
