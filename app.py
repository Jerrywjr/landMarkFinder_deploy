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
# Helper Functions
# -----------------------------
def image_to_base64(image: Image.Image) -> str:
    """
    Convert PIL Image to base64 string
    """
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def call_openrouter(image_base64: str) -> str:
    """
    Call OpenRouter API with DeepSeek V3.1 Nex N1
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return "❌ OPENROUTER_API_KEY is not set."

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # These two headers are recommended by OpenRouter
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "Landmark Recognition App"
    }

    prompt = (
        "You are a professional travel guide.\n\n"
        "Identify the landmark in the image.\n"
        "If identifiable, respond exactly in this format:\n\n"
        "Name:\n"
        "City, Country:\n"
        "Brief introduction (3–4 sentences):\n\n"
        "If you are not confident, clearly say so and explain why."
    )

    payload = {
        "model": "deepseek/deepseek-v3.1-nex-n1",
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
            result = call_openrouter(img_b64)

        st.subheader("🧭 Result")
        st.write(result)

else:
    st.info("Please upload an image to begin.")
