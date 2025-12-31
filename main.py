import streamlit as st
import requests
import base64
from PIL import Image
import io

# ---------------------
# CONFIGURAZIONE
# ---------------------
st.set_page_config(
    page_title="REWIRE AI",
    page_icon="⚡",
    layout="wide"
)

GROQ_API_KEY = "INSERISCI_LA_TUA_CHIAVE"  # <<< METTI QUI LA TUA NUOVA CHIAVE
API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

# ---------------------
# STILE
# ---------------------
st.markdown("""
<style>
body { background-color: #f2f4ff; }
.chat-bubble {
    background: white;
    padding: 16px;
    border-radius: 16px;
    margin-bottom: 10px;
    font-size: 18px;
    box-shadow: 0px 2px 4px rgba(0,0,0,0.15);
}
#MainMenu, header, footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------------
# LOGIN
# ---------------------
if "auth" not in st.session_state:
    st.session_st_
