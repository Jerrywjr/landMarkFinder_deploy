import streamlit as st
import requests
from PIL import Image
import base64
import io
import os
import json

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Landmark Recognition",
    page_icon="🌍",
    layout="centered"
)

st.title("🌍 Landmark Recognition")
st.caption("Upload a photo and let AI tell you where it is.")

# -----------------------------
# Language Selection
# -----------------------------
lang = st.radio("Language / 语言", ["English", "中文"])

# -----------------------------
# Helper Functions
# -----------------------------
def image_to_base64(image: Image.Image) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


# ---------- VL Model ----------
def call_vl_model(image_b64: str, language: str):
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    if language == "English":
        prompt = (
            "Identify the landmark in the image.\n"
            "Return:\n"
            "Name:\nCity, Country:\nBrief introduction (3–4 sentences)."
        )
    else:
        prompt = (
            "识别图片中的地标建筑。\n"
            "返回格式：\n"
            "名称：\n城市，国家：\n简要介绍（3–4句话）。"
        )

    payload = {
        "model": "qwen/qwen-2.5-vl-7b-instruct:free",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_b64}"
                    }
                }
            ]
        }],
        "temperature": 0.2
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


# ---------- Text Model ----------
def call_text_model(landmark_name: str, language: str):
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    if language == "English":
        prompt = f"Introduce the landmark {landmark_name} in 4 sentences."
    else:
        prompt = f"请用中文介绍地标建筑 {landmark_name}，约4句话。"

    payload = {
        "model": "xiaomi/mimo-v2-flash:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


# -----------------------------
# UI
# -----------------------------
uploaded_file = st.file_uploader(
    "📷 Upload an image / 上传图片",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, use_container_width=True)

    if st.button("🔍 Identify"):
        with st.spinner("Analyzing image..."):
            try:
                img_b64 = image_to_base64(image)
                result = call_vl_model(img_b64, lang)
                st.subheader("🧭 Result")
                st.write(result)

                # ---- TTS ----
                tts = result.replace("\n", " ")
                st.components.v1.html(
                    f"""
                    <script>
                    var msg = new SpeechSynthesisUtterance("{tts}");
                    msg.lang = "{'en-US' if lang=='English' else 'zh-CN'}";
                    speechSynthesis.speak(msg);
                    </script>
                    """,
                    height=0
                )

            except Exception:
                st.warning("⚠️ Image recognition service is busy.")

                landmark = st.text_input(
                    "Enter landmark name manually:",
                    placeholder="Eiffel Tower / 埃菲尔铁塔"
                )

                if landmark:
                    intro = call_text_model(landmark, lang)
                    st.subheader("🧭 Result")
                    st.write(intro)

else:
    st.info("Please upload an image." if lang == "English" else "请上传图片。")
