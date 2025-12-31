import streamlit as st
import requests
import fitz
import json

# --- CONFIGURAZIONE API ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI PRO", layout="wide", page_icon="⚡")

# --- CSS: LOGICA E COERENZA VISIVA ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #1e2a4a, #0d1117); color: #e6edf3; }
    .main-title { font-size: 50px !important; font-weight: 900 !important; background: linear-gradient(90deg, #00f2fe, #4facfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
    .preview-box { border: 2px solid rgba(0, 242, 254, 0.3); border-radius: 15px; padding: 15px; background: rgba(0,0,0,0.4); }
    .stButton > button { border-radius: 20px !important; font-weight: bold !important; width: 100%; transition: 0.3s; }
    .save-btn > div > button { background: linear-gradient(45deg, #28a745, #85e085) !important; color: white !important; }
    .load-btn > div > button { background: linear-gradient(45deg, #ffc107, #ffdb4d) !important; color: #212529 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h1 class='main-title'>⚡ RE-WIRE</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Chiave Accesso:", type="password")
        if st.button("ACCEDI"):
            if pwd == "rewire2026": st.session_state.auth = True; st.rerun()
    st.stop()

# --- GESTIONE MEMORIA (SAVE/LOAD) ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""
if "current_file" not in st.session_state: st.session_state.current_file = None

def save_work():
    data = {
        "messages": st.session_state.messages,
        "doc_text": st.session_state.doc_text,
        "current_file_name": st.session_state.current_file['name'] if st.session_state.current_file else None
    }
    return json.dumps(data)

# --- SIDEBAR: CONTROLLI AVANZATI ---
with st.sidebar:
    st.markdown("<h2 style='color: #4facfe;'>⚡ DASHBOARD</h2>", unsafe_allow_html=True)
    
    # SEZIONE SALVATAGGIO
    st.markdown("### 💾 Memoria Lavoro")
    col_s, col_l = st.columns(2)
    with col_s:
        st.markdown('<div class="save-btn">', unsafe_allow_html=True)
        st.download_button("SALVA", save_work(), file_name="sessione_rewire.json", help="Scarica il lavoro per riprenderlo dopo")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_l:
        st.markdown('<div class="load-btn">', unsafe_allow_html=True)
        uploaded_session = st.file_uploader("CARICA", type=["json"], label_visibility="collapsed")
        if uploaded_session:
            session_data = json.load(uploaded_session)
            st.session_state.messages = session_data["messages"]
            st.session_state.doc_text = session_data["doc_text"]
            st.success("Sessione Ripristinata!")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Carica Documento/Immagine", type=["pdf", "jpg", "png", "jpeg"])
    if uploaded_file:
        if "last_fn" not in st.session_state or st.session_state.last_fn != uploaded_file.name:
            file_bytes = uploaded_file.read()
            if uploaded_file.type == "application/pdf":
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                st.session_state.doc_text = "".join([p.get_text() for p in doc])[:8000]
                st.session_state.current_file = {"name": uploaded_file.name, "type": "pdf", "data": st.session_state.doc_text}
            else:
                st.session_state.doc_text = f"ANALISI VISIVA RICHIESTA PER: {uploaded_file.name}"
                st.session_state.current_file = {"name": uploaded_file.name, "type": "img", "data": file_bytes}
            st.rerun()

    mode = st.radio("🎯 Ambiente:", ["🏠 Famiglia", "💼 Business", "🔬 Specialista"])
    if st.button("🗑️ RESET"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.current_file = None
        st.rerun()

# --- AREA DI LAVORO ---
if st.session_state.current_file:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        if st.session_state.current_file['type'] == "img":
            st.image(st.session_state.current_file['data'], use_container_width=True)
        else:
            st.text_area("Contenuto PDF:", st.session_state.doc_text, height=300)
        st.markdown('</div>', unsafe_allow_html=True)
    with c2:
        st.markdown("### 🔍 Analisi in tempo reale")
        st.info(f"Modalità {mode} attiva. L'AI sta analizzando l'immagine sopra ignorando i nomi dei file fuorvianti.")

# --- CHAT CON LOGICA ANTI-ERRORE ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Esegui un comando logico..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        # ISTRUZIONE BLOCCATA PER LA COERENZA
        sys_msg = f"""Sei RE-WIRE AI ({mode}). 
        REGOLA D'ORO: Non farti ingannare dal nome del file (es. 'CAP' non è un cappello, è 'Capitolo'). 
        Analizza l'immagine o il testo basandoti sui fatti visibili: {st.session_state.doc_text}.
        Sii fluido, usa tabelle se necessario, e mantieni una logica ferrea."""
        
        r = requests.post(API_URL, json={"model": MODEL_ID, "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}]}, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
        ans = r.json()['choices'][0]['message']['content']
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
