import urllib.parse
import google.generativeai as genai
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="BANANA PRO UGC Studio", page_icon="⚡", layout="centered"
)

st.title("⚡ AI UGC Image Generator Studio")
st.write("Generator Foto UGC Otomatis - Mengubah Wajah & Produk Menjadi Foto")

# Sidebar
api_key = st.sidebar.text_input("Masukkan Gemini API Key", type="password")

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
        with st.spinner("1/2 Menganalisis struktur wajah & produk..."):
            try:
                genai.configure(api_key=api_key)

                # Deteksi model aktif dari akun
                available_models = [
                    m.name.replace("models/", "")
                    for m in genai.list_models()
                    if "generateContent" in m.supported_generation_methods
                ]

                if not available_models:
                    st.error("API Key tidak valid atau tidak memiliki akses.")
                    st.stop()

                img_avatar = Image.open(avatar_file)
                img_product = Image.open(product_file)

                system_instruction = f"""
                Analisis foto wajah (Gambar 1) dan produk (Gambar 2).
                Buat 1 kalimat prompt ringkas dalam bahasa Inggris untuk generator gambar.
                Format: A photo of an Indonesian person with the face from Image 1, wearing the outfit from Image 2, sitting at {prompt_input}, 8k resolution, highly detailed, photorealistic, warm lighting, shot on 35mm lens.
                Tulis HANYA kalimat prompt Inggris tersebut tanpa karakter lain.
                """

                prompt_text = ""
                for model_name in available_models:
                    try:
                        model = genai.GenerativeModel(model_name)
                        res = model.generate_content(
                            [img_avatar, img_product, system_instruction]
                        )
                        if res.text:
                            prompt_text = res.text.strip()
                            break
                    except Exception:
                        continue

                if not prompt_text:
                    st.error("Gagal menyusun instruksi visual dari gambar.")
                    st.stop()

                st.info("2/2 Memproses rendering foto UGC...")

                # Mengirim prompt ke Image Engine (Flux Engine)
                encoded_prompt = urllib.parse.quote(prompt_text)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true&model=flux"

                # Menampilkan FOTO LANGSUNG di aplikasi
                st.image(
                    image_url,
                    caption="Hasil Render Foto UGC (Rasio 9:16)",
                    use_container_width=True,
                )
                st.success("Foto UGC Berhasil Digenerate!")

                with st.expander("Lihat Detail Prompt"):
                    st.code(prompt_text)

            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
