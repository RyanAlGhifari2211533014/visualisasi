import streamlit as st

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
    
    st.info("Pilih salah satu opsi dari sidebar untuk melihat visualisasi data.")

    # Optional: Add some general statistics or a welcoming image
    st.image("https://placehold.co/600x300/E0F2F7/2C3E50?text=Visualisasi+Data+Kelurahan", use_column_width=True)
    st.markdown("---")
    st.write("Made by @TimCihuy")
