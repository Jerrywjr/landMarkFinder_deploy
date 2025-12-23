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

st.title("🌍 Landmark Recognition")

# -----------------------------
# Session State
# -----------------------------
if "vl_failed" not in st.session_state:
    st.session_state.vl_failed = False

if "result" not in st.session_state:
    st.session_state.result = ""

# -----------------------------
# Helper Functions
# -----------------------------
def image_to_base64(image: Image.Image) -> str:
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def call_vl_model(image_b64, language):
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    prompt = (
        "Identify the landmark in the image.\n"
        "Return name, city, country and a short introduction."
        if language == "English"
        else
        "识别图片中的地标建筑，并给出名称、城市、国家和简要介绍。"
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

    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def call_text_model(name, language):
    api_key = os.getenv("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"

    prompt = (
        f"Introduce the landmark {name} in 4 sentences."
        if language == "English"
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
left, right = st.columns([1, 1.2])

# ========== LEFT ==========
with left:
    st.subheader("📷 Input")

    lang = st.radio("Language / 语言", ["English", "中文"])

    uploaded_file = st.file_uploader(
        "Upload an image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Preview", use_container_width=True)

        if st.button("🔍 Identify Landmark"):
            with st.spinner("Analyzing image..."):
                try:
                    img_b64 = image_to_base64(image)
                    st.session_state.result = call_vl_model(img_b64, lang)
                    st.session_state.vl_failed = False
                except Exception:
                    st.session_state.vl_failed = True
                    st.session_state.result = ""

    if st.session_state.vl_failed:
        st.warning("Image recognition unavailable. Enter landmark manually:")
        landmark_name = st.text_input(
            "Landmark name",
            placeholder="Eiffel Tower / 埃菲尔铁塔"
        )

        if landmark_name:
            with st.spinner("Generating introduction..."):
                st.session_state.result = call_text_model(
                    landmark_name, lang
                )

# ========== RIGHT ==========
with right:
    st.subheader("🧭 Result")

    if st.session_state.result:
        st.write(st.session_state.result)

        # ---- TTS ----
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
        st.info("Result will appear here." if lang == "English" else "结果将在此显示。")
