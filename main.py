import streamlit as st
import requests
import base64
from PIL import Image
import io
import json
import os

# ============================================================
#                  CONFIGURAZIONE BASE APP
# ============================================================

API_KEY = st.secrets.get("GROQ_API_KEY")
if not API_KEY:
    st.error("❌ Devi inserire la GROQ_API_KEY in .streamlit/secrets.toml")
    st.stop()

CHAT_MODEL = "llama-3.2-11b-instant"
VISION_MODEL = "llama-3.2-90b-vision-instant"

API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(
    page_title="HELP KID AI",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# ============================================================
#                        STILE CUSTOM
# ============================================================

st.markdown("""
<style>
    body {
        background-color: #F3F4F9;
    }
    .block-container {
        padding-top: 1rem;
    }
    .title-logo {
        text-align:center;
        font-size: 44px;
        font-weight: 900;
        color: #4B6FFF;
        margin-bottom: 0px;
        margin-top: -10px;
    }
    .subtitle {
        text-align:center;
        color:#6A6A8A;
        font-size:18px;
        margin-bottom:40px;
    }
    .chat-box {
        background: #FFFFFF;
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 20px;
    }
