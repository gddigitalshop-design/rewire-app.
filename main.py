import streamlit as st
import requests
import fitz
from PIL import Image
import io

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI", layout="wide", page_icon="⚡")

# --- STILE CSS PERSONALIZZATO (IL "TRUCCO" PER LA GRAFICA) ---
st.markdown("""
    <style>
    /* Sfondo generale e font */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        color: #ffffff;
    }
    
    /* Titoli */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        background: -webkit-linear-gradient(#00f2fe, #4facfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
    }

    /* Container Documenti */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        margin-bottom: 10px;
    }

    /* Input Fields */
    .stTextInput > div > div > input {
        background-color: rgba(0, 0, 0, 0.3) !important;
        color: white !important;
        border: 1px solid #4facfe !important;
        border-radius: 10px;
    }

    /* Bottoni */
    .stButton > button {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        border-radius: 20px;
        font-weight: bold;
        transition: all 0.3s ease;
        text-transform: uppercase;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0px 0px 15px rgba(79, 172, 254, 0.6);
    }
    
    /* Divider colorato */
    hr {
        border-top: 2px solid rgba(79, 172, 254, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGICA DI AUTENTICAZIONE ---
if "auth" not in st.session_state: 
    st.session_state.auth = False

if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>⚡ RE-WIRE AI</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #4facfe;'>Premium Intelligence Access</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            pwd = st.text_input("Inserisci la Chiave d'Accesso:", type="password")
            if st.button("SBLOCCA ACCESSO", use_container_width=True):
                if pwd == "rewire2026":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Chiave errata. Riprova.")
    st.stop()

# --- INIZIALIZZAZIONE SESSIONE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""
if "current_file_data" not in st.session_state: st.session_state.current_file_data = None

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80) # Icona decorativa
    st.header("🗂️ Workspace")
    uploaded_file = st.file_uploader("Carica PDF o Immagine", type=["pdf", "jpg", "jpeg", "png"])
    
    if uploaded_file:
        if "last_file_name" not in st.session_state or st.session_state.last_file_name != uploaded_file.name:
            st.session_state.messages = []
            st.session_state.last_file_name = uploaded_file.name
            
            if uploaded_file.type in ["image/jpeg", "image/png"]:
                img_bytes = uploaded_file.read()
                st.session_state.current_file_data = {"type": "image", "data": img_bytes, "name": uploaded_file.name}
                st.session_state.doc_text = f"Analisi immagine: {uploaded_file.name}"
            elif uploaded_file.type == "application/pdf":
                doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                text = "".join([p.get_text() for p in doc])[:4000]
                st.session_state.doc_text = text
                st.session_state.current_file_data = {"type": "pdf", "data": text, "name": uploaded_file.name}
            st.rerun()

    st.markdown("---")
    # FIX: Reset selettivo per non perdere il login
    if st.button("🗑️ Svuota Chat e File"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.current_file_data = None
        if "last_file_name" in st.session_state: del st.session_state.last_file_name
        st.rerun()

# --- AREA CENTRALE ---
st.markdown("<h2 style='text-align: center;'>📄 Preview Contenuto</h2>", unsafe_allow_html=True)

with st.container():
    if st.session_state.current_file_data:
        f = st.session_state.current_file_data
        col_left, col_mid, col_right = st.columns([1, 6, 1])
        with col_mid:
            if f["type"] == "image":
                st.image(f["data"], caption=f["name"], use_container_width=True)
            else:
                st.success(f"✅ PDF Caricato: {f['name']}")
                with st.expander("Leggi estratto testo"):
                    st.write(f["data"][:1500] + "...")
    else:
        st.markdown("<p style='text-align: center; opacity: 0.6;'>In attesa di un documento da analizzare...</p>", unsafe_allow_html=True)

st.markdown("<br><hr><br>", unsafe_allow_html=True)

# --- CHAT INTERFACE ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Chiedi all'AI o analizza il documento..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        if "template grafico" in prompt.lower():
            ans = (
                "### 🎨 Analisi Visiva Proposta\n"
                "- **Stile:** Minimalista e futuristico.\n"
                "- **Palette:** Blu Elettrico (#00f2fe) e Deep Space (#0f0c29).\n"
                "- **Consiglio:** Utilizzare icone neon per i punti chiave."
            )
        else:
            payload = {
                "model": MODEL_ID,
                "messages": [
                    {"role": "system", "content": f"Sei un assistente business esperto. Analizza questo contesto: {st.session_state.doc_text}"},
                    {"role": "user", "content": prompt}
                ]
            }
            try:
                r = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
                ans = r.json()['choices'][0]['message']['content']
            except:
                ans = "⚠️ Ops! Problema di connessione con il cervello AI."
        
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
