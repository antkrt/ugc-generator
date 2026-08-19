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
        with st.spinner("Mencari model aktif dan memproses gambar..."):
            try:
                genai.configure(api_key=api_key)

                # 1. Deteksi model yang BENAR-BENAR aktif di akun Anda
                available_models = []
                for m in genai.list_models():
                    if "generateContent" in m.supported_generation_methods:
                        clean_name = m.name.replace("models/", "")
                        available_models.append(clean_name)

                if not available_models:
                    st.error(
                        "Tidak ada model yang ditemukan pada API Key ini. Pastikan API Key valid."
                    )
                    st.stop()

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

                response = None
                success_model = None
                last_error = None

                # 2. Coba jalankan hanya menggunakan model resmi dari akun Anda
                for model_name in available_models:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(
                            [img_avatar, img_product, system_instruction]
                        )
                        success_model = model_name
                        break
                    except Exception as err:
                        last_error = err
                        continue

                if response and response.text:
                    st.success("Prompt UGC Berhasil Dibuat!")
                    st.caption(f"Model Aktif Digunakan: **{success_model}**")
                    st.subheader("Hasil Prompt untuk Engine Gambar:")
                    st.code(response.text, language="text")
                else:
                    st.error(f"Gagal memproses. Detail error: {last_error}")

            except Exception as e:
                st.error(f"Terjadi kesalahan koneksi API Key: {e}")                response = None
                used_model = None
                last_error = None

                # Sistem Fallback: coba setiap kandidat model sampai berhasil
                for model_name in candidate_models:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(
                            [img_avatar, img_product, system_instruction]
                        )
                        used_model = model_name
                        break
                    except Exception as err:
                        last_error = err
                        continue

                if response and response.text:
                    st.success("Prompt UGC Berhasil Dibuat!")
                    st.caption(f"Model Aktif Digunakan: **{used_model}**")
                    st.subheader("Hasil Prompt untuk Engine Gambar:")
                    st.code(response.text, language="text")
                else:
                    st.error(
                        f"Gagal memproses gambar. Detail error: {last_error}"
                    )

            except Exception as e:
                st.error(f"Terjadi kesalahan sistem: {e}")
