import streamlit as st
import requests
import fitz

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

# --- SIDEBAR: MODALITÀ E FILE ---
with st.sidebar:
    st.markdown("<h2 style='color: #4facfe; text-align: center;'>⚡ DASHBOARD</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # 1. CARICATORE FILE (RIPRISTINATO)
    uploaded_file = st.file_uploader("📂 Carica Documento (PDF/IMG)", type=["pdf", "jpg", "png", "jpeg"])
    if uploaded_file:
        if "last_fn" not in st.session_state or st.session_state.last_fn != uploaded_file.name:
            with st.status("🧠 Analisi file...") as status:
                st.session_state.last_fn = uploaded_file.name
                if uploaded_file.type == "application/pdf":
                    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
                    st.session_state.doc_text = "".join([p.get_text() for p in doc])[:8000]
                    st.session_state.current_file = {"name": uploaded_file.name, "type": "pdf"}
                else:
                    st.session_state.doc_text = f"Contenuto immagine: {uploaded_file.name}"
                    st.session_state.current_file = {"name": uploaded_file.name, "type": "img", "data": uploaded_file.read()}
                status.update(label="✅ File pronto!", state="complete")
            st.rerun()

    st.markdown("---")
    # 2. SELETTORE AMBIENTE
    mode = st.radio("🎯 Ambiente di Lavoro:", ["🏠 Famiglia", "💼 Business", "🔬 Specialista"])
    
    st.markdown("---")
    if st.button("🗑️ RESET WORKSPACE"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.current_file = None
        st.rerun()
    
    if st.session_state.messages:
        chat_txt = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        st.download_button("📩 SCARICA REPORT", chat_txt, file_name=f"report_rewire.txt")

# --- AREA CENTRALE ---
if st.session_state.current_file:
    st.markdown(f"<p style='text-align: center; color: #4facfe;'>📄 File attivo: {st.session_state.current_file['name']}</p>", unsafe_allow_html=True)
elif not st.session_state.messages:
    st.markdown("<br><br><h1 class='main-title'>⚡ RE-WIRE AI</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 20px;'>Modalità attiva: <b>{mode}</b></p>", unsafe_allow_html=True)

# Visualizzazione Chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

# Input Chat
if prompt := st.chat_input(f"Chiedi a RE-WIRE ({mode})..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        sys_msg = f"Sei RE-WIRE AI in modalità {mode}. Usa il contesto del file se presente: {st.session_state.doc_text}"
        try:
            r = requests.post(API_URL, 
                json={"model": MODEL_ID, "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}]}, 
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
            ans = r.json()['choices'][0]['message']['content']
        except: ans = "Errore di connessione."
        
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
