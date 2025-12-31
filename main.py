import streamlit as st
import requests
import fitz
from PIL import Image
import io

# --- CONFIGURAZIONE API ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE AI", layout="wide", page_icon="⚡")

# --- DESIGN "ANIMA E OCCHI" (CSS AVANZATO) ---
st.markdown("""
    <style>
    /* Sfondo animato e profondo */
    .stApp {
        background: radial-gradient(circle at top right, #1e2a4a, #0d1117);
        color: #e6edf3;
    }
    
    /* Header e Logo Animato */
    .main-title {
        font-size: 50px !important;
        font-weight: 900 !important;
        background: linear-gradient(90deg, #00f2fe, #4facfe, #00f2fe);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
        text-align: center;
        margin-bottom: 0px;
    }
    
    @keyframes shine {
        to { background-position: 200% center; }
    }

    /* Messaggio di Benvenuto Sprizzante */
    .welcome-text {
        text-align: center;
        font-size: 24px;
        color: #4facfe;
        font-weight: 300;
        margin-bottom: 30px;
    }

    /* Sidebar elegante */
    [data-testid="stSidebar"] {
        background-color: rgba(13, 17, 23, 0.8);
        border-right: 1px solid rgba(79, 172, 254, 0.2);
        backdrop-filter: blur(10px);
    }

    /* Chat Bubbles stile Glass */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }

    /* Bottoni */
    .stButton > button {
        border-radius: 30px !important;
        background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%) !important;
        color: #0d1117 !important;
        font-weight: bold !important;
        border: none !important;
        padding: 0.5rem 2rem !important;
        transition: 0.3s all !important;
    }
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 20px rgba(79, 172, 254, 0.4) !important;
    }

    /* Esnasione Documenti */
    .stExpander {
        background: rgba(0,0,0,0.2) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(79, 172, 254, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN (Protetto) ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<br><br><h1 class='main-title'>⚡ RE-WIRE</h1>", unsafe_allow_html=True)
        st.markdown("<p class='welcome-text'>L'intelligenza che ti serve.</p>", unsafe_allow_html=True)
        with st.container(border=True):
            pwd = st.text_input("Inserisci la chiave d'accesso per sbloccare l'anima dell'AI:", type="password")
            if st.button("ACCEDI AL FUTURO"):
                if pwd == "rewire2026":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Chiave non valida.")
    st.stop()

# --- INIT ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""
if "current_file" not in st.session_state: st.session_state.current_file = None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='font-size: 25px;'>⚡ RE-WIRE AI</h1>", unsafe_allow_html=True)
    st.markdown("---")
    file = st.file_uploader("📂 Carica la tua risorsa (PDF/Immagini)", type=["pdf", "jpg", "png", "jpeg"])
    
    if file:
        if "last_fn" not in st.session_state or st.session_state.last_fn != file.name:
            st.session_state.messages = []
            st.session_state.last_fn = file.name
            if file.type == "application/pdf":
                doc = fitz.open(stream=file.read(), filetype="pdf")
                st.session_state.doc_text = "".join([p.get_text() for p in doc])[:4000]
                st.session_state.current_file = {"type": "pdf", "name": file.name}
            else:
                st.session_state.doc_text = f"Analisi immagine: {file.name}"
                st.session_state.current_file = {"type": "img", "data": file.read(), "name": file.name}
            st.rerun()

    if st.button("🗑️ RESET SESSIONE"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.current_file = None
        st.rerun()
    
    # EXPORT REPORT
    if st.session_state.messages:
        chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        st.download_button("📩 SCARICA REPORT CHAT", chat_history, file_name="report_rewire.txt")

# --- AREA PRINCIPALE ---
if not st.session_state.current_file:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>⚡ RE-WIRE AI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='welcome-text'>Buongiorno! Cosa posso fare per te oggi?</p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.4;'>Carica un documento dalla barra laterale per iniziare a lavorare con piacere.</p>", unsafe_allow_html=True)
else:
    st.markdown(f"<h3 style='text-align: center;'>💎 ANALISI ATTIVA: {st.session_state.current_file['name']}</h3>", unsafe_allow_html=True)
    with st.expander("👁️ Visualizza Contenuto Documento"):
        if st.session_state.current_file['type'] == "img":
            st.image(st.session_state.current_file['data'])
        else:
            st.write(st.session_state.doc_text)

st.markdown("---")

# --- CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Scrivi qui, lasciati ispirare..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            r = requests.post(API_URL, 
                json={"model": MODEL_ID, "messages": [
                    {"role": "system", "content": "Sei RE-WIRE AI, un assistente brillante, amichevole e professionale. Il tuo obiettivo è rendere il lavoro dell'utente un piacere."},
                    {"role": "user", "content": f"Contesto: {st.session_state.doc_text}\n\nDomanda: {prompt}"}
                ]}, 
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
            ans = r.json()['choices'][0]['message']['content']
        except: ans = "Ops! C'è stato un piccolo intoppo tecnico. Riprova?"
        
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
