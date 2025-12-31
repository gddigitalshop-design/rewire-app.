import streamlit as st
import requests
import base64
from PIL import Image
import io

# ---------------------------------------------------------
# 1. CONFIGURAZIONE UI (PROFESSIONALE E PULITA)
# ---------------------------------------------------------
st.set_page_config(page_title="REWIRE AI PRO", page_icon="⚡", layout="wide")

# CSS per garantire leggibilità assoluta (Testo Nero su Sfondo Chiaro)
st.markdown("""
<style>
    .stApp { background-color: #ffffff; color: #1a1a1a; }
    
    /* Sidebar scura ed elegante */
    [data-testid="stSidebar"] { background-color: #111827 !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    
    /* Messaggi della chat leggibili */
    [data-testid="stChatMessage"] {
        background-color: #f3f4f6 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 12px;
        color: #1a1a1a !important;
    }
    
    /* Forza il colore nero per ogni paragrafo nei messaggi */
    [data-testid="stChatMessageContent"] p { color: #1a1a1a !important; }
    
    /* Bottone stile Enterprise */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #4F46E5;
        color: white !important;
        border: none;
        padding: 10px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. INIZIALIZZAZIONE STATI E API
# ---------------------------------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# Tentativo di recupero chiave API
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    st.error("Errore: Inserisci la 'GROQ_API_KEY' nei Secrets di Streamlit.")
    st.stop()

API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ---------------------------------------------------------
# 3. LOGICA DI ACCESSO (LOGIN)
# ---------------------------------------------------------
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1 style='text-align: center; color: #1a1a1a;'>⚡ REWIRE AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666;'>Licenza Enterprise v.2026</p>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            pwd = st.text_input("Inserisci Password Licenza:", type="password")
            submit = st.form_submit_button("ACCEDI AL SISTEMA")
            
            if submit:
                if pwd == "rewire2026":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Credenziali non valide.")
    st.stop()

# ---------------------------------------------------------
# 4. BARRA LATERALE (FUNZIONI DI AFFITTO/VENDITA)
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛠️ Pannello Strumenti")
    st.success("Stato: Licenza Attiva")
    st.markdown("---")
    
    # Caricamento file
    uploaded_file = st.file_uploader("📁 Carica un file (Immagini o Testo)", type=["png", "jpg", "jpeg", "txt"])
    
    # Template Pronti
    template = st.selectbox("🎯 Azioni Rapide:", [
        "Chat Standard",
        "Analisi Dettagliata Immagine",
        "Riassunto Professionale",
        "Correzione Bozza"
    ])
    
    st.markdown("---")
    if st.button("🗑️ Cancella Memoria Chat"):
        st.session_state.messages = []
        st.rerun()
        
    if st.button("🚪 Termina Sessione"):
        st.session_state.auth = False
        st.rerun()

# ---------------------------------------------------------
# 5. FUNZIONE CORE API (NESSUN ERRORE DI SINTASSI)
# ---------------------------------------------------------
def get_ai_response(user_input, image_b64=None):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Sceglie il modello: Vision se c'è un'immagine, altrimenti il 70B
    model_name = "llama-3.2-11b-vision-preview" if image_b64 else "llama-3.3-70b-versatile"
    
    # Costruzione del Payload
    messages = [{"role": "system", "content": "Sei Rewire AI, un assistente di alto livello. Rispondi in italiano."}]
    
    # Aggiunge cronologia per dare memoria
    for msg in st.session_state.messages[-4:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Gestione contenuto (Vision vs Text)
    if image_b64:
        user_content = [
            {"type": "text", "text": user_input},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
        ]
    else:
        user_content = user_input
        
    messages.append({"role": "user", "content": user_content})

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": 0.6
    }
