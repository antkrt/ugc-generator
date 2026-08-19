import re
import urllib.parse
import urllib.request
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
        with st.spinner("1/2 Menganalisis wajah & produk..."):
            try:
                genai.configure(api_key=api_key)

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
                Buatlah 1 kalimat deskripsi prompt dalam bahasa Inggris tanpa tanda baca aneh.
                Contoh hasil: A photorealistic commercial portrait of an Indonesian person wearing the outfit from Image 2, sitting at {prompt_input}, 8k resolution, warm ambient lighting.
                PENTING: Jangan gunakan bullet points, jangan gunakan tanda bintang (*), dan jangan gunakan baris baru.
                """

                raw_prompt = ""
                for model_name in available_models:
                    try:
                        model = genai.GenerativeModel(model_name)
                        res = model.generate_content(
                            [img_avatar, img_product, system_instruction]
                        )
                        if res.text:
                            raw_prompt = res.text
                            break
                    except Exception:
                        continue

                # Membersihkan teks dari simbol markdown, asterisk, dan enter agar URL tidak rusak
                prompt_clean = re.sub(r"[^a-zA-Z0-9\s,.]", "", raw_prompt)
                prompt_clean = " ".join(prompt_clean.split())

                if len(prompt_clean) < 10:
                    prompt_clean = f"A photorealistic portrait of a person wearing stylish clothes sitting at {prompt_input}, 8k resolution, warm lighting"

                st.info("2/2 Memproses rendering foto UGC...")

                # Mengirim prompt bersih ke Image Engine
                encoded_prompt = urllib.parse.quote(prompt_clean)
                image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true&model=flux"

                # Mengunduh file gambar ke memori secara langsung
                req = urllib.request.Request(
                    image_url, headers={"User-Agent": "Mozilla/5.0"}
                )
                with urllib.request.urlopen(req, timeout=45) as response:
                    image_bytes = response.read()

                # Menampilkan FOTO LANGSUNG dari data gambar
                st.image(
                    image_bytes,
                    caption="Hasil Render Foto UGC (Rasio 9:16)",
                    use_container_width=True,
                )
                st.success("Foto UGC Berhasil Digenerate!")

                with st.expander("Lihat Detail Prompt"):
                    st.write(prompt_clean)

            except Exception as e:
                st.error(
                    f"Gagal memuat gambar: {e}. Silakan tekan tombol Generate sekali lagi."
                )
