import streamlit as st
import requests
import base64
from PIL import Image

# ---------------------------------------------------------
# 1. SETUP UI - DARK MODE PROFESSIONALE
# ---------------------------------------------------------
st.set_page_config(page_title="REWIRE AI PRO", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    /* Sfondo scuro per evitare l'effetto accecante */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Sidebar ancora più scura */
    [data-testid="stSidebar"] { background-color: #000000 !important; }
    
    /* Messaggi della chat: contrasto elevato */
    [data-testid="stChatMessage"] {
        background-color: #1e293b !important; /* Blu scuro/grigio */
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
    }

    /* Testo bianco puro nei messaggi */
    [data-testid="stChatMessageContent"] p, .stMarkdown p {
        color: #ffffff !important;
        font-size: 16px !important;
    }

    /* BARRA CHAT: Sfondo scuro e bordo colorato per visibilità totale */
    [data-testid="stChatInput"] {
        background-color: #1e293b !important;
        border: 2px solid #6366f1 !important;
        border-radius: 10px !important;
    }
    
    /* Bottoni */
    .stButton>button {
        background-color: #6366f1; color: white; border-radius: 8px; border: none;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. LOGICA DI ACCESSO
# ---------------------------------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sicurezza Chiave API
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("Configura la chiave API nei Secrets di Streamlit.")
    st.stop()

# ---------------------------------------------------------
# 3. SCHERMATA LOGIN
# ---------------------------------------------------------
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h1 style='text-align: center; color: #6366f1;'>⚡ REWIRE AI</h1>", unsafe_allow_html=True)
        with st.form("login"):
            pwd = st.text_input("Licenza Pro 2026:", type="password")
            if st.form_submit_button("SBLOCCA SISTEMA"):
                if pwd == "rewire2026":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Password errata.")
    st.stop()

# ---------------------------------------------------------
# 4. DASHBOARD E SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.title("⚙️ Pannello")
    st.write("Stato: **Premium**")
    uploaded_file = st.file_uploader("Allega un file", type=["png", "jpg", "jpeg", "txt"])
    if st.button("🗑️ Reset Memoria"):
        st.session_state.messages = []
        st.rerun()
    if st.button("🚪 Logout"):
        st.session_state.auth = False
        st.rerun()

# ---------------------------------------------------------
# 5. CORE CHAT (GROQ)
# ---------------------------------------------------------
st.markdown("<h2 style='color: #6366f1;'>🚀 Smart AI Workspace</h2>", unsafe_allow_html=True)

# Visualizza messaggi
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Input Barra Chat (Ora perfettamente visibile)
if prompt := st.chat_input("Digita la tua richiesta qui..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Verifica Immagine per Vision
    img_b64 = None
    if uploaded_file and any(x in uploaded_file.name.lower() for x in ['jpg','png','jpeg']):
        img_b64 = base64.b64encode(uploaded_file.getvalue()).decode()

    # Risposta AI
    with st.chat_message("assistant"):
        with st.spinner("Rewire AI sta analizzando..."):
            try:
                model = "llama-3.2-11b-vision-preview" if img_b64 else "llama-3.3-70b-versatile"
                headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
                
                msgs = [{"role": "system", "content": "Sei Rewire AI. Rispondi in modo professionale in italiano."}]
                for m in st.session_state.messages[-4:]:
                    msgs.append({"role": m["role"], "content": m["content"]})
                
                if img_b64:
                    content = [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                else:
                    content = prompt
                
                msgs.append({"role": "user", "content": content})
                
                r = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                                 headers=headers, 
                                 json={"model": model, "messages": msgs})
                
                ans = r.json()['choices'][0]['message']['content']
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            except Exception as e:
                st.error("Errore API. Controlla la chiave nei Secrets.")
