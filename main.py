import streamlit as st
import requests
import fitz
import json

# --- CONFIGURAZIONE API ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI PRO", layout="wide", page_icon="⚡")

# --- CSS: PULIZIA TOTALE DASHBOARD ---
st.markdown("""
    <style>
    .stApp { background: #0d1117; color: #e6edf3; }
    .main-title { font-size: 45px !important; font-weight: 800; background: linear-gradient(90deg, #00f2fe, #4facfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
    section[data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    
    /* Nasconde i testi standard del caricatore per pulizia */
    .stFileUploader label { display: none; }
    .stFileUploader section > div { display: none; }
    .stFileUploader section::before { content: "📂 TRASCINA QUI (FOTO, PDF o SESSIONE)"; color: #4facfe; font-weight: bold; }
    
    .img-container { border: 2px solid #4facfe; border-radius: 15px; overflow: hidden; background: black; box-shadow: 0 10px 30px rgba(0,0,0,0.5); margin-bottom: 20px; }
    .stButton > button { border-radius: 12px !important; background: linear-gradient(45deg, #4facfe, #00f2fe) !important; color: #0d1117 !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h1 class='main-title'>⚡ RE-WIRE</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Chiave Accesso:", type="password")
        if st.button("SBLOCCA"):
            if pwd == "rewire2026": st.session_state.auth = True; st.rerun()
    st.stop()

# --- INIT SESSION ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""
if "current_file" not in st.session_state: st.session_state.current_file = None

# --- SIDEBAR UNIFICATA ---
with st.sidebar:
    st.markdown("<h1 style='color:#4facfe; font-size:24px; text-align:center;'>⚡ DASHBOARD</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # UNICO CARICATORE INTELLIGENTE
    uploaded = st.file_uploader("Upload", type=["json", "pdf", "jpg", "png", "jpeg"])
    
    if uploaded:
        if uploaded.type == "application/json":
            data = json.load(uploaded)
            st.session_state.messages = data.get("messages", [])
            st.session_state.doc_text = data.get("doc_text", "")
            st.success("✅ Lavoro Ripristinato")
        else:
            if "last_fn" not in st.session_state or st.session_state.last_fn != uploaded.name:
                st.session_state.last_fn = uploaded.name
                if uploaded.type == "application/pdf":
                    doc = fitz.open(stream=uploaded.read(), filetype="pdf")
                    st.session_state.doc_text = "".join([p.get_text() for p in doc])[:8000]
                    st.session_state.current_file = {"type": "pdf", "name": uploaded.name}
                else:
                    st.session_state.current_file = {"type": "img", "data": uploaded.read(), "name": uploaded.name}
                    st.session_state.doc_text = f"Analisi visiva: {uploaded.name}"
                st.rerun()

    st.markdown("---")
    mode = st.radio("🎯 AMBIENTE", ["🏠 Famiglia", "💼 Business", "🔬 Specialista"])
    
    # SALVATAGGIO RAPIDO
    if st.session_state.messages:
        session_json = json.dumps({"messages": st.session_state.messages, "doc_text": st.session_state.doc_text})
        st.download_button("📥 SALVA LAVORO CORRENTE", session_json, file_name="sessione_rewire.json")

    if st.button("🗑️ RESET TOTALE"):
        st.session_state.clear()
        st.session_state.auth = True
        st.rerun()

# --- AREA DI LAVORO ---
if st.session_state.current_file:
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown('<div class="img-container">', unsafe_allow_html=True)
        if st.session_state.current_file["type"] == "img":
            st.image(st.session_state.current_file["data"])
        else:
            st.info(f"PDF Attivo: {st.session_state.current_file['name']}")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown(f"### 📋 Analisi {mode}")
        st.write("L'AI è pronta. Usa la chat sotto per approfondire il contenuto.")

# --- CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Inserisci comando o analisi..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        # LOGICA RIGIDA ANTI-ERRORE
        context = f"Sei RE-WIRE AI ({mode}). Ignora nomi file come 'CAP' (non sono cappelli). Analizza basandoti su: {st.session_state.doc_text}"
        r = requests.post(API_URL, 
            json={"model": MODEL_ID, "messages": [{"role": "system", "content": context}, {"role": "user", "content": prompt}]}, 
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
        ans = r.json()['choices'][0]['message']['content']
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
