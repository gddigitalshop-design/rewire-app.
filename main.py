import streamlit as st
import requests
import base64
from PIL import Image
import io

# ---------------------------------------------------------
# 1. SETUP UI - DARK MODE PREMIUM
# ---------------------------------------------------------
st.set_page_config(page_title="REWIRE AI PRO", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #000000 !important; }
    [data-testid="stChatMessage"] {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
    }
    [data-testid="stChatMessageContent"] p { color: #ffffff !important; }
    [data-testid="stChatInput"] {
        border: 2px solid #6366f1 !important;
        background-color: #1e293b !important;
    }
    .stButton>button { background-color: #6366f1; color: white; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. INIZIALIZZAZIONE
# ---------------------------------------------------------
if "auth" not in st.session_state: st.session_state.auth = False
if "messages" not in st.session_state: st.session_state.messages = []

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("Configura GROQ_API_KEY nei Secrets.")
    st.stop()

# ---------------------------------------------------------
# 3. LOGIN
# ---------------------------------------------------------
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h1 style='text-align: center; color: #6366f1;'>⚡ REWIRE AI</h1>", unsafe_allow_html=True)
        with st.form("login"):
            pwd = st.text_input("Licenza Pro 2026:", type="password")
            if st.form_submit_button("SBLOCCA"):
                if pwd == "rewire2026":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Password errata.")
    st.stop()

# ---------------------------------------------------------
# 4. SIDEBAR E CARICAMENTO FILE
# ---------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Pannello")
    uploaded_file = st.file_uploader("Allega un'immagine", type=["png", "jpg", "jpeg"])
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()
    if st.button("🚪 Logout"):
        st.session_state.auth = False
        st.rerun()

# ---------------------------------------------------------
# 5. AREA CHAT
# ---------------------------------------------------------
st.markdown("<h2 style='color: #6366f1;'>🚀 Smart AI Workspace</h2>", unsafe_allow_html=True)

# Visualizzazione cronologia messaggi (Inclusi i file salvati nello stato)
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if "image" in m:
            st.image(m["image"], width=300)
        st.markdown(m["content"])

# INPUT CHAT
if prompt := st.chat_input("Chiedi qualcosa..."):
    
    # Prepariamo il dizionario del messaggio utente
    user_msg = {"role": "user", "content": prompt}
    
    # Se c'è un file caricato, lo aggiungiamo al messaggio e lo mostriamo
    img_b64 = None
    if uploaded_file:
        img_data = uploaded_file.getvalue()
        user_msg["image"] = img_data # Salviamo i byte per visualizzarli dopo
        img_b64 = base64.b64encode(img_data).decode()

    # Mostriamo il messaggio utente immediatamente
    with st.chat_message("user"):
        if uploaded_file:
            st.image(uploaded_file, width=300)
        st.markdown(prompt)
    
    st.session_state.messages.append(user_msg)

    # RISPOSTA AI
    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            try:
                model = "llama-3.2-11b-vision-preview" if img_b64 else "llama-3.3-70b-versatile"
                headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
                
                # Costruiamo il payload per Groq
                msgs_payload = [{"role": "system", "content": "Sei Rewire AI, rispondi in italiano."}]
                # Aggiungiamo cronologia (solo testo per semplicità nelle API, tranne l'ultimo)
                for m in st.session_state.messages[-4:-1]:
                    msgs_payload.append({"role": m["role"], "content": m["content"]})
                
                if img_b64:
                    content = [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                else:
                    content = prompt
                
                msgs_
