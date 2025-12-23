import streamlit as st
import requests
from PIL import Image
import base64
import io
import os

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Landmark Recognition",
    page_icon="🌍",
    layout="wide"
)

# -----------------------------
# UI Text (i18n)
# -----------------------------
UI = {
    "English": {
        "title": "🌍 Landmark Recognition",
        "input": "📷 Input",
        "upload": "Upload an image",
        "identify": "🔍 Identify Landmark",
        "result": "🧭 Result",
        "preview": "Image Preview",
        "busy": "Image recognition service is busy.",
        "manual": "Enter landmark name manually",
        "placeholder": "Eiffel Tower",
        "waiting": "Result will appear here."
    },
    "中文": {
        "title": "🌍 地标识别系统",
        "input": "📷 输入",
        "upload": "上传图片",
        "identify": "🔍 识别地标",
        "result": "🧭 识别结果",
        "preview": "图片预览",
        "busy": "图像识别服务繁忙",
        "manual": "手动输入地标名称",
        "placeholder": "埃菲尔铁塔",
        "waiting": "结果将在此显示。"
    }
}

# -----------------------------
# Session State
# -----------------------------
if "result" not in st.session_state:
    st.session_state.result = ""
if "vl_failed" not in st.session_state:
    st.session_state.vl_failed = False

# -----------------------------
# Helper Functions
# -----------------------------
def image_to_base64(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def call_vl_model(image_b64, lang):
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"

    prompt = (
        "Identify the landmark in the image and give a short introduction."
        if lang == "English"
        else
        "识别图片中的地标建筑并给出简要介绍。"
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

    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=60
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def call_text_model(name, lang):
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"

    prompt = (
        f"Introduce the landmark {name} in 4 sentences."
        if lang == "English"
        else
        f"请用中文介绍地标建筑 {name}，约4句话。"
    )

    payload = {
        "model": "xiaomi/mimo-v2-flash:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    r = requests.post(
        url,
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=30
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

# -----------------------------
# Layout
# -----------------------------
left, right = st.columns([1, 1.3])

# ---------- LEFT ----------
with left:
    lang = st.radio("Language / 语言", ["English", "中文"])
    T = UI[lang]

    st.subheader(T["input"])
    uploaded = st.file_uploader(T["upload"], type=["jpg", "jpeg", "png"])

    if uploaded:
        image = Image.open(uploaded).convert("RGB")

        # Fixed-size image preview
        st.markdown(
            f"""
            <div style="text-align:center;">
                <img src="data:image/png;base64,{image_to_base64(image)}"
                     style="max-height:260px; max-width:100%; object-fit:contain;" />
                <div style="font-size:0.85em; color:gray;">{T["preview"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(T["identify"]):
            try:
                st.session_state.result = call_vl_model(
                    image_to_base64(image), lang
                )
                st.session_state.vl_failed = False
            except Exception:
                st.session_state.vl_failed = True
                st.session_state.result = ""

    if st.session_state.vl_failed:
        st.warning(T["busy"])
        name = st.text_input(T["manual"], placeholder=T["placeholder"])
        if name:
            st.session_state.result = call_text_model(name, lang)

# ---------- RIGHT ----------
with right:
    st.subheader(T["result"])

    if st.session_state.result:
        st.write(st.session_state.result)

        # TTS
        tts = st.session_state.result.replace("\n", " ")
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
    else:
        st.info(T["waiting"])
