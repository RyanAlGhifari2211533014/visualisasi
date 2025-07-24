import streamlit as st
from pages import jumlah_penduduk_status_pekerja
from pages import penduduk_disabilitas
def run():
    """
    Renders the Home page content.
    """
    st.title("Selamat Datang di Dashboard Data Kelurahan 👋")
    st.markdown("""
        <div style="text-align: center;">
            <p style="font-size: 1.2em;">
                Dashboard ini menyajikan berbagai visualisasi data penting mengenai kelurahan Anda.
                Gunakan menu di sidebar untuk menjelajahi berbagai kategori data.
            </p>
            <p style="font-size: 1.1em; color: #555;">
                Data ini akan membantu dalam pengambilan keputusan dan pemahaman kondisi kelurahan.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.write("Berikut adalah proporsi penduduk berdasarkan status pekerjaan:")
    penduduk_disabilitas.create_disabilitas_chart_only()
    jumlah_penduduk_status_pekerja.create_status_pekerja_chart_only()

    st.info("Pilih salah satu opsi dari sidebar untuk melihat visualisasi data.")

    st.markdown("---")
    st.write("Dibuat oleh @timcihuy")
