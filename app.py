import streamlit as st
import requests
from PIL import Image
import base64
import io
import os
import re

# =============================
# Page Config
# =============================
st.set_page_config(
    page_title="Landmark Recognition",
    page_icon="🌍",
    layout="wide"
)

# =============================
# UI Text (i18n)
# =============================
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
        "speech_start": "▶️ Start Speech",
        "speech_stop": "⏹ Stop Speech"
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
        "speech_start": "🔊 开始播报",
        "speech_stop": "🔇 停止播报"
    }
}

# =============================
# Session State
# =============================
for key in ["result", "vl_failed", "parsed"]:
    if key not in st.session_state:
        st.session_state[key] = None

# =============================
# Helper Functions
# =============================
def image_to_base64(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def parse_result(text: str):
    name = re.search(r"Name[:：]\s*(.*)", text)
    loc = re.search(r"(City.*Country|城市.*国家)[:：]\s*(.*)", text)
    intro = text.split("\n")[-1]

    return {
        "name": name.group(1) if name else "",
        "location": loc.group(2) if loc else "",
        "intro": intro
    }


def call_vl_model(image_b64, lang):
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"

    prompt = (
        "Identify the landmark in the image.\n"
        "Return:\nName:\nCity, Country:\nBrief introduction."
        if lang == "English"
        else
        "识别图片中的地标建筑。\n返回：\n名称：\n城市，国家：\n简要介绍。"
    )

    payload = {
        "model": "qwen/qwen-2.5-vl-7b-instruct:free",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
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

# =============================
# Layout
# =============================
left, right = st.columns([1, 1.3])

# ---------- LEFT ----------
with left:
    lang = st.radio("Language / 语言", ["English", "中文"])
    T = UI[lang]

    st.subheader(T["input"])
    uploaded = st.file_uploader(T["upload"], type=["jpg", "jpeg", "png"])

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.markdown(
            f"""
            <img src="data:image/png;base64,{image_to_base64(image)}"
                 style="max-height:240px; max-width:100%; object-fit:contain;" />
            """,
            unsafe_allow_html=True
        )

        if st.button(T["identify"]):
            try:
                res = call_vl_model(image_to_base64(image), lang)
                st.session_state.result = res
                st.session_state.parsed = parse_result(res)
                st.session_state.vl_failed = False
            except Exception:
                st.session_state.vl_failed = True

    if st.session_state.vl_failed:
        name = st.text_input(T["manual"], placeholder=T["placeholder"])
        if st.button(T["confirm"]) and name:
            res = call_text_model(name, lang)
            st.session_state.result = res
            st.session_state.parsed = {
                "name": name,
                "location": "",
                "intro": res
            }

# ---------- RIGHT ----------
with right:
    st.subheader(T["result"])

    if st.session_state.parsed:
        p = st.session_state.parsed

        st.markdown(f"""
        <div style="border:1px solid var(--secondary-background-color);
                    border-radius:10px; padding:16px;">
            <h3>{p["name"]}</h3>
            <p><b>{p["location"]}</b></p>
            <p>{p["intro"]}</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button(T["speech_start"]):
                st.components.v1.html(
                    f"""
                    <script>
                    window.speechSynthesis.cancel();
                    var msg = new SpeechSynthesisUtterance("{p["intro"]}");
                    msg.lang = "{'en-US' if lang=='English' else 'zh-CN'}";
                    speechSynthesis.speak(msg);
                    </script>
                    """,
                    height=0
                )
        with col2:
            if st.button(T["speech_stop"]):
                st.components.v1.html(
                    "<script>speechSynthesis.cancel();</script>",
                    height=0
                )
    else:
        st.info(T["waiting"])
