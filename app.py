import google.generativeai as genai
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="BANGMANPRO Studio", page_icon="⚡", layout="centered"
)

st.title("⚡ AI UGC Generator Studio")
st.write("Generator UGC berbasis AI - Gabungkan Wajah & Produk secara Otomatis")

# Sidebar untuk API Key
api_key = st.sidebar.text_input("Masukkan Gemini API Key", type="password")

# Form Upload
col1, col2 = st.columns(2)
with col1:
    avatar_file = st.file_uploader(
        "1. Upload Foto Wajah", type=["jpg", "png", "jpeg"]
    )
with col2:
    product_file = st.file_uploader(
        "2. Upload Produk/Pakaian", type=["jpg", "png", "jpeg"]
    )

prompt_input = st.text_input(
    "3. Prompt Tambahan (Suasana/Latar)",
    "sedang duduk santai di cafe estetik sambil minum kopi",
)

if st.button("🚀 GENERATE MASTERPIECE", use_container_width=True):
    if not api_key:
        st.error("Silakan masukkan Gemini API Key terlebih dahulu di sidebar!")
    elif not avatar_file or not product_file:
        st.warning("Mohon unggah foto wajah dan foto produk!")
    else:
        with st.spinner("Sedang memproses instruksi UGC..."):
            try:
                genai.configure(api_key=api_key)

                # Mendapatkan daftar model aktif dari API Key secara akurat
                valid_models = [
                    m.name
                    for m in genai.list_models()
                    if "generateContent" in m.supported_generation_methods
                ]

                # Cari model versi flash yang valid
                chosen_model = None
                for model_name in valid_models:
                    if "flash" in model_name.lower():
                        chosen_model = model_name
                        break

                if not chosen_model and valid_models:
                    chosen_model = valid_models[0]

                model = genai.GenerativeModel(chosen_model)

                img_avatar = Image.open(avatar_file)
                img_product = Image.open(product_file)

                system_instruction = f"""
                Analisis kedua gambar berikut. Gambar 1 adalah foto wajah subjek, Gambar 2 adalah produk/pakaian.
                Buatlah deskripsi prompt gambar UGC ultra-realistis dalam bahasa Inggris dengan rincian:
                - Subjek: Mempertahankan bentuk wajah dan ekspresi dari Gambar 1.
                - Pakaian: Memakai produk/pakaian dari Gambar 2 secara alami.
                - Latar belakang & Suasana: {prompt_input}.
                - Gaya Foto: Commercial UGC photography, 8k resolution, highly detailed texture, photorealistic, warm natural lighting, shot on 35mm lens, f/1.8.
                """

                response = model.generate_content(
                    [img_avatar, img_product, system_instruction]
                )

                st.success("Prompt UGC Berhasil Dibuat!")
                st.caption(f"Engine Aktif: {chosen_model}")
                st.subheader("Hasil Prompt untuk Engine Gambar:")
                st.code(response.text, language="text")

            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
