import streamlit as st
from groq import Groq
import random
import urllib.parse
import requests
import io
from PIL import Image

# --------------------------------------------------
# 1. CONFIGURAZIONE PAGINA
# --------------------------------------------------
st.set_page_config(
    page_title="RE-WIRE Business",
    layout="wide"
)

# --------------------------------------------------
# 2. STATO SESSIONE
# --------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_role" not in st.session_state:
    st.session_state.user_role = None

if "current_img_data" not in st.session_state:
    st.session_state.current_img_data = None

if "current_template" not in st.session_state:
    st.session_state.current_template = None

# --------------------------------------------------
# 3. SISTEMA LOGIN
# --------------------------------------------------
USERS = {
    "admin": "tuapassword123",
    "cliente1": "rewire2025"
}

def login_system():
    st.markdown(
        "<h1 style='text-align:center;color:#007BFF;'>RE-WIRE PLATFORM</h1>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("ACCEDI", use_container_width=True):
            if
