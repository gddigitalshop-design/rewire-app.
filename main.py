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

# --- DESIGN PREMIUM ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #1e2a4a, #0d1117); color: #e6edf3; }
    .main-title { font-size: 50px !important; font-weight: 900 !important; background: linear-gradient(90deg, #00f2fe, #4facfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
    .stChatMessage { background: rgba(255, 255, 255, 0.05) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 15px !important; }
    [data-testid="stSidebar"] { background-color: rgba(13, 17, 23, 0.9); border-right: 1px solid rgba(0, 242, 254, 0.2); }
    .stButton > button { border-radius: 20px !important; background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%) !important; color: #0d1117 !important; font-weight: bold !important; width: 100%; border: none !important; }
    .preview-box { border: 1px solid rgba(0, 242, 254, 0.3); border-radius: 15px; padding: 20px; background: rgba(255,255,255,0.02); margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<br><br><h1 class='main-title'>⚡ RE-WIRE</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Chiave d'Accesso:", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "rewire2026": st.session_state.auth = True; st.rerun()
    st.stop()

# --- INIT ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""
if "current_file" not in st.session_state: st.session_state.current_file = None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='color: #4facfe; text-align: center;'>⚡ DASHBOARD</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    uploaded_file = st.file_uploader("📂 Carica Documento (PDF/IMG)", type=["pdf", "jpg", "png", "jpeg"])
    if uploaded_file:
        if "last_fn" not in st.session_state or st.session_state.last_fn != uploaded_file.name:
            with st.status("🧠 Analisi file...") as status:
                st.session_state.last_fn = uploaded_file.name
                file_bytes = uploaded_file.read()
                if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=file_bytes, filetype="pdf")
                    st.session_state.doc_text = "".join([p.get_text() for p in doc])[:8000]
                    st.session_state.current_file = {"name": uploaded_file.name, "type": "pdf", "data": st.session_state.doc_text}
                else:
                    st.session_state.doc_text = f"Analisi immagine: {uploaded_file.name}"
                    st.session_state.current_file = {"name": uploaded_file.name, "type": "img", "data": file_bytes}
                status.update(label="✅ Caricato!", state="complete")
            st.rerun()

    st.markdown("---")
    mode = st.radio("🎯 Ambiente:", ["🏠 Famiglia", "💼 Business", "🔬 Specialista"])
    
    st.markdown("---")
    if st.button("🗑️ RESET WORKSPACE"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.current_file = None
        st.rerun()

# --- AREA CENTRALE (VISUALIZZAZIONE FILE) ---
if st.session_state.current_file:
    st.markdown(f"<h3 style='text-align: center; color: #4facfe;'>📄 VISUALIZZAZIONE: {st.session_state.current_file['name']}</h3>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        if st.session_state.current_file['type'] == "img":
            # APRE L'IMMAGINE AL CENTRO
            st.image(st.session_state.current_file['data'], use_container_width=True)
        else:
            # MOSTRA IL TESTO DEL PDF
            with st.expander("🔍 Leggi testo estratto dal PDF"):
                st.write(st.session_state.current_file['data'])
        st.markdown('</div>', unsafe_allow_html=True)
else:
    if not st.session_state.messages:
        st.markdown("<br><br><h1 class='main-title'>⚡ RE-WIRE AI</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 20px;'>Modalità: <b>{mode}</b></p>", unsafe_allow_html=True)

st.markdown("---")

# --- CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input(f"Chiedi a RE-WIRE ({mode})..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        sys_msg = f"Sei RE-WIRE AI ({mode}). Analizza questo contesto: {st.session_state.doc_text}"
        try:
            r = requests.post(API_URL, 
                json={"model": MODEL_ID, "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}]}, 
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
            ans = r.json()['choices'][0]['message']['content']
        except: ans = "Errore AI."
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
