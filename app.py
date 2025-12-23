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
        "intro": "Introduction"
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
        "intro": "简介"
    }
}

# -----------------------------
# Session State
# -----------------------------
for k in ["result", "vl_failed", "parsed"]:
    if k not in st.session_state:
        st.session_state[k] = None

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
    从模型输出中提取名称、位置、简介，避免重复显示
    """
    name_match = re.search(r"(名称|Name)[:：]\s*(.*)", text)
    location_match = re.search(r"(位置|Location|City|Country)[:：]\s*(.*)", text)

    name = name_match.group(2).strip() if name_match else None
    location = location_match.group(2).strip() if location_match else None

    # 去掉原始文本中的标签
    intro = text
    if name:
        intro = re.sub(r"(名称|Name)[:：].*", "", intro)
    if location:
        intro = re.sub(r"(位置|Location|City|Country)[:：].*", "", intro)
    intro = intro.strip()
    if not intro:
        intro = text  # fallback

    return {"name": name or "—", "location": location or "—", "intro": intro}


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
        b64 = image_to_base64(image)

        # 图片预览固定高度
        st.markdown(
            f"""
            <img src="data:image/png;base64,{b64}"
                 style="max-height:240px; max-width:100%;
                        object-fit:contain;
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
            except Exception:
                st.session_state.vl_failed = True
                st.session_state.result = None

    if st.session_state.vl_failed:
        st.warning(T["busy"])
        manual_name = st.text_input(T["manual"], placeholder=T["placeholder"])
        if st.button(T["confirm"]) and manual_name:
            raw = call_text_model(manual_name, lang)
            st.session_state.result = raw
            st.session_state.parsed = parse_result(raw)

# ---------- RIGHT ----------
with right:
    st.subheader(T["result"])

    if st.session_state.parsed:
        p = st.session_state.parsed
        st.markdown(
            f"""
            <div style="
                padding:16px;
                border-radius:12px;
                background:rgba(128,128,128,0.08);
            ">
                <h4>{T['name']}</h4>
                <p>{p['name']}</p>

                <h4>{T['location']}</h4>
                <p>{p['location']}</p>

                <h4>{T['intro']}</h4>
                <p>{p['intro']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # TTS
        tts = p["intro"].replace("\n", " ")
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
