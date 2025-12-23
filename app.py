import streamlit as st
import requests
from PIL import Image
import base64
import io
import os
import re

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
        "manual": "Enter landmark name",
        "confirm": "✅ Confirm",
        "placeholder": "Eiffel Tower",
        "waiting": "Result will appear here.",
        "name": "Name",
        "location": "Location",
        "intro": "Introduction",
        "start_speech": "🔊 Start Reading",
        "stop_speech": "⏹ Stop Reading"
    },
    "中文": {
        "title": "🌍 地标识别系统",
        "input": "📷 输入",
        "upload": "上传图片",
        "identify": "🔍 识别地标",
        "result": "🧭 识别结果",
        "preview": "图片预览",
        "busy": "图像识别服务繁忙",
        "manual": "输入地标名称",
        "confirm": "✅ 确认",
        "placeholder": "埃菲尔铁塔",
        "waiting": "结果将在此显示。",
        "name": "名称",
        "location": "位置",
        "intro": "简介",
        "start_speech": "🔊 开始朗读",
        "stop_speech": "⏹ 停止朗读"
    }
}

# -----------------------------
# Session State
# -----------------------------
for k in ["result", "vl_failed", "parsed", "speech_playing"]:
    if k not in st.session_state:
        st.session_state[k] = None
if "speech_playing" not in st.session_state:
    st.session_state.speech_playing = False

# -----------------------------
# Helpers
# -----------------------------
def image_to_base64(image):
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def call_vl_model(image_b64, lang):
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"

    prompt = (
        "Identify the landmark in the image.\nReturn Name, City, Country, and a short introduction."
        if lang == "English"
        else "识别图片中的地标建筑，返回名称、城市、国家和简要介绍。"
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
        f"Introduce the landmark {name}.\nReturn name, location and introduction."
        if lang == "English"
        else f"请介绍地标建筑{name}，返回名称、位置和简介。"
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


def parse_result(text):
    """
    Extract name/location/intro from model output
    """
    name_match = re.search(r"(名称|Name)[:：]\s*(.*)", text)
    location_match = re.search(r"(位置|Location|City|Country)[:：]\s*(.*)", text)

    name = name_match.group(2).strip() if name_match else None
    location = location_match.group(2).strip() if location_match else None

    intro = text
    if name:
        intro = re.sub(r"(名称|Name)[:：]\s*.*", "", intro)
    if location:
        intro = re.sub(r"(位置|Location|City|Country)[:：]\s*.*", "", intro)
    intro = intro.strip() or text

    return {"name": name or "—", "location": location or "—", "intro": intro}


def render_tts(text, lang, start=True):
    """
    Insert JS for TTS with start/stop control
    """
    js = f"""
    <script>
    window.speechSynthesis.cancel();
    var msg = new SpeechSynthesisUtterance("{text}");
    msg.lang = "{'en-US' if lang=='English' else 'zh-CN'}";
    if({str(start).lower()}){{ speechSynthesis.speak(msg); }}
    window.stopSpeech = function(){{ speechSynthesis.cancel(); }};
    </script>
    """
    st.components.v1.html(js, height=0)


# -----------------------------
# Layout
# -----------------------------
left, right = st.columns([1, 1.3])
lang = st.radio("Language / 语言", ["English", "中文"])
T = UI[lang]

# ---------- LEFT ----------
with left:
    st.subheader(T["input"])
    uploaded = st.file_uploader(T["upload"], type=["jpg", "jpeg", "png"])

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        b64 = image_to_base64(image)
        st.markdown(
            f"""
            <img src="data:image/png;base64,{b64}"
                 style="max-height:240px; max-width:100%; object-fit:contain;
                        border-radius:8px;" />
            """,
            unsafe_allow_html=True
        )

        if st.button(T["identify"]):
            try:
                raw = call_vl_model(b64, lang)
                st.session_state.result = raw
                st.session_state.parsed = parse_result(raw)
                st.session_state.vl_failed = False
            except:
                st.session_state.vl_failed = True
                st.session_state.result = None

    if st.session_state.vl_failed:
        st.warning(T["busy"])
        manual = st.text_input(T["manual"], placeholder=T["placeholder"])
        if st.button(T["confirm"]) and manual:
            raw = call_text_model(manual, lang)
            st.session_state.result = raw
            st.session_state.parsed = parse_result(raw)

# ---------- RIGHT ----------
with right:
    st.subheader(T["result"])
    if st.session_state.result:
        result_text = st.session_state.result.strip()
        st.markdown(
            f"""
            <div style="
                padding:16px;
                border-radius:12px;
                background:rgba(128,128,128,0.08);
                white-space:pre-wrap;
            ">
                {result_text}
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---- TTS Controls ----
        st.button(T["start_speech"], on_click=render_tts, args=(result_text, lang, True))
        st.button(T["stop_speech"], on_click=render_tts, args=("", lang, False))
    else:
        st.info(T["waiting"])

