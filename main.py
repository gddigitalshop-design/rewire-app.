import streamlit as st
import requests
import base64
from PIL import Image
import io

# ---------------------------------------------------------
# 1. CONFIGURAZIONE UI E STILE (DESIGN PREMIUM)
# ---------------------------------------------------------
st.set_page_config(page_title="REWIRE AI PRO", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    [data-testid="stSidebar"] { background-color: #111827; color: white; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; border: 1px solid #e5e7eb; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #4F46E5; color: white; border: none; }
    .stButton>button:hover { background-color: #4338CA; border: none; }
    .status-badge { padding: 5px 10px; border-radius: 20px; font-size: 12px; background-color: #10B981; color: white; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. INIZIALIZZAZIONE E SICUREZZA
# ---------------------------------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# Recupero chiavi dai Secrets di Streamlit
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("Errore: Chiave API non configurata nei Secrets.")
    st.stop()

API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ---------------------------------------------------------
# 3. PAGINA DI LOGIN
# ---------------------------------------------------------
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1 style='text-align: center;'>⚡ REWIRE AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Professional AI Enterprise Suite</p>", unsafe_allow_html=True)
        with st.container():
            pwd = st.text_input("Inserisci Password Licenza:", type="password")
            if st.button("ATTIVA LICENZA"):
                if pwd == "rewire2026":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Password errata. Contatta il supporto per l'affitto.")
    st.stop()

# ---------------------------------------------------------
# 4. SIDEBAR - GESTIONE E TEMPLATE
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712139.png", width=80)
    st.title("Rewire Control")
    st.markdown('<span class="status-badge">● Licenza Attiva</span>', unsafe_allow_html=True)
    st.write(f"Scadenza: 31/12/2026")
    
    st.markdown("---")
    st.subheader("📁 File & Media")
    uploaded_file = st.file_uploader("Carica immagine o documento", type=["png", "jpg", "jpeg", "pdf", "txt"])
    
    st.subheader("📝 Template Rapidi")
    template = st.selectbox("Seleziona azione:", [
        "Chat Libera", 
        "Analisi Tecnica Immagine", 
        "Riassunto Documento", 
        "Scrittura Email Professionale"
    ])
    
    if st.button("🗑️ Svuota Conversazione"):
        st.session_state.messages = []
        st.rerun()

    if st.button("🚪 Logout"):
        st.session_state.auth = False
        st.rerun()

# ---------------------------------------------------------
# 5. LOGICA API GROQ
# ---------------------------------------------------------
def process_ai_response(user_input, image_b64=None):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    # Se c'è un'immagine usa il modello Vision, altrimenti Llama 3.3
    model = "llama-3.2-11b-vision-preview" if image_b64 else "llama-3.3-70b-versatile"
    
    if image_b64:
        content = [
            {"type": "text", "text": user_input},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
        ]
    else:
        content = user_input

    messages = [{"role": "system", "content": "Sei Rewire AI, un assistente professionale e preciso."}]
    # Aggiungi cronologia (ultimi 4 messaggi)
    for m in st.session_state.messages[-4:]:
        messages.append({"role": m["role"], "content": m["content"]})
    
    messages.append({"role": "user", "content": content})

    payload = {"model": model, "messages": messages, "temperature": 0.5}
    
    res = requests.post(API_URL, headers=headers, json=payload)
    if res.status_code == 200:
        return res.json()['choices'][0]['message']['content']
    return "Errore nella comunicazione con il server AI."

# ---------------------------------------------------------
# 6. AREA CHAT PRINCIPALE
# ---------------------------------------------------------
st.title("🚀 Smart Workspace")

# Mostra cronologia
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(
