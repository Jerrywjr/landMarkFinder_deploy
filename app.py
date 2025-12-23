import streamlit as st
import requests
from PIL import Image
import base64
import io
import os
import json

# -----------------------------
# Streamlit Page Config
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
lang = st.radio("Select Language / 选择语言", ["English", "中文"])

# -----------------------------
# Helper Functions
# -----------------------------
def image_to_base64(image: Image.Image) -> str:
    """
    Convert PIL Image to base64 string
    """
    image = image.resize((512, 512))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def call_openrouter(image_base64: str, language: str) -> str:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "❌ OPENROUTER_API_KEY is not set."

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "Landmark Recognition App"
    }

    prompt = (
        "Identify the landmark in the image and briefly introduce it."
        if language == "English"
        else "请识别图片中的地标并做简要介绍。"
    )

    payload = {
        "model": "qwen/qwen-2.5-vl-7b-instruct:free",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url",
                 "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
            ]
        }],
        "temperature": 0.2
    }

    for attempt in range(2):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.RequestException:
            if attempt == 1:
                return "❌ The AI service is temporarily unavailable. Please try again later."

    payload = {
        "model": "qwen/qwen-2.5-vl-7b-instruct:free",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.2
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        return f"❌ API request failed:\n{e}"

    except (KeyError, json.JSONDecodeError):
        return "❌ Unexpected response format from model."


# -----------------------------
# UI
# -----------------------------
uploaded_file = st.file_uploader(
    "📷 Upload a landmark image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="Uploaded Image", use_container_width=True)

    if st.button("🔍 Identify Landmark"):
        with st.spinner("Analyzing image..."):
            img_b64 = image_to_base64(image)
            result = call_openrouter(img_b64, lang)

        st.subheader("🧭 Result")
        st.write(result)

        # -----------------------------
        # Text-to-Speech
        # -----------------------------
        tts_text = result.replace("\n", " ")
        tts_code = f"""
        <script>
        var msg = new SpeechSynthesisUtterance("{tts_text}");
        msg.lang = "{'en-US' if lang=='English' else 'zh-CN'}";
        window.speechSynthesis.speak(msg);
        </script>
        """
        st.components.v1.html(tts_code, height=0)

else:
    st.info("Please upload an image to begin." if lang=="English" else "请上传图片开始识别。")
