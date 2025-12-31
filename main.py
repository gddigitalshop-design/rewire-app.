import streamlit as st
import requests
import base64
from PIL import Image
import io
import json
import os

# ========================================================
#                 CONFIGURAZIONE
# ========================================================

# Inserisci la tua chiave Groq in .streamlit/secrets.toml
# GROQ_API_KEY="gsk_abcdef1234567890"
API_KEY = st.secrets.get("GROQ_API_KEY")
if not API_KEY:
    st.error("❌ Devi inserire la tua GROQ_API_KEY in .streamlit/secrets.toml")
    st.stop()

URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.2-90b-vision-instant"

st.set_page_config(page_title="RE-WIRE AI", layout="wide")

# ========================================================
#
