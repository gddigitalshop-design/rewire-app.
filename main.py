import streamlit as st
import requests
import base64
from PIL import Image
import io

# 1. SETUP UI - DARK MODE PROFESSIONALE
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

# 2. INIZIALIZZAZIONE STATI
if "auth" not in st.session_state:
    st.session_state.auth = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# Recupero chiave dai Secrets
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Errore: Chiave API mancante nei Secrets.")
    st.stop()

# 3. LOGIN
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h1 style='text-align: center; color: #6366f1;'>⚡ REWIRE AI</h1>", unsafe_allow_html=True)
        with st.form("login_panel"):
            pwd = st.text_input("Password Licenza 2026:", type="password")
            if st.form_submit_button("SBLOCCA APPLICAZIONE"):
                if pwd == "rewire2026":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Password errata.")
    st.stop()

# 4. SIDEBAR
with st.sidebar:
    st.title("⚙️ Pannello Controllo")
    uploaded_file = st.file_uploader("Allega immagine per analisi", type=["png", "jpg", "jpeg"])
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()
    if st.button("🚪 Logout"):
        st.session_state.auth = False
        st.rerun()

# 5. VISUALIZZAZIONE CHAT
st.markdown("<h2 style='color: #6366f1;'>🚀 Smart AI Workspace</h2>", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if "image" in m:
            st.image(m["image"], width=300)
        st.markdown(m["content"])

# 6. LOGICA DI RISPOSTA
if prompt := st.chat_input("Scrivi un messaggio o chiedi dell'immagine..."):
    
    # Gestione Immagine
    img_b64 = None
    current_user_msg = {"role": "user", "content": prompt}
    
    if uploaded_file:
        raw_data = uploaded_file.getvalue()
        current_user_msg["image"] = raw_data # Salvataggio per visualizzazione
        img_b64 = base64.b64encode(raw_data).decode()

    # Mostra messaggio utente
    with st.chat_message("user"):
        if uploaded_file:
            st.image(uploaded_file, width=300)
        st.markdown(prompt)
    
    st.session_state.messages.append(current_user_msg)

    # Chiamata API Groq
    with st.chat_message("assistant"):
        with st.spinner("Rewire sta elaborando..."):
            try:
                # Scelta modello
                selected_model = "llama-3.2-11b-vision-preview" if img_b64 else "llama-3.3-70b-versatile"
                
                # Costruzione messaggi per API
                api_msgs = [{"role": "system", "content": "Sei Rewire AI, un assistente professionale."}]
                for m in st.session_state.messages[-5:-1]:
                    api_msgs.append({"role": m["role"], "content": m["content"]})
                
                if img_b64:
                    user_payload = [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                else:
                    user_payload = prompt
                
                api_msgs.append({"role": "user", "content": user_payload})

                # Chiamata effettiva
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    json={"model": selected_model, "messages": api_msgs, "temperature": 0.5},
                    timeout=30
                )
                
                full_response = response.json()['choices'][0]['message']['content']
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Errore tecnico: {str(e)}")
