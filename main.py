import streamlit as st
import requests
import fitz

# --- CONFIGURAZIONE API ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE AI - Hub Professionale", layout="wide", page_icon="⚡")

# --- DESIGN "ANIMA E OCCHI" (CSS) ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #1e2a4a, #0d1117); color: #e6edf3; }
    .main-title { font-size: 50px !important; font-weight: 900 !important; background: linear-gradient(90deg, #00f2fe, #4facfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 5px; }
    .stChatMessage { background: rgba(255, 255, 255, 0.05) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 15px !important; }
    .preview-box { border: 2px solid rgba(0, 242, 254, 0.3); border-radius: 20px; padding: 25px; background: rgba(0,0,0,0.3); margin-top: 20px; }
    .fase-box { background: rgba(79, 172, 254, 0.1); border-left: 5px solid #4facfe; padding: 15px; border-radius: 10px; margin: 10px 0; }
    .stButton > button { border-radius: 30px !important; background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%) !important; color: #0d1117 !important; font-weight: bold !important; width: 100%; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<br><br><h1 class='main-title'>⚡ RE-WIRE</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Inserisci la Chiave:", type="password")
        if st.button("ACCEDI"):
            if pwd == "rewire2026": st.session_state.auth = True; st.rerun()
    st.stop()

# --- INIT ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""
if "current_file" not in st.session_state: st.session_state.current_file = None

# --- SIDEBAR: DASHBOARD ---
with st.sidebar:
    st.markdown("<h2 style='color: #4facfe; text-align: center;'>⚡ DASHBOARD</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # 1. CARICATORE FILE
    uploaded_file = st.file_uploader("📂 Carica Documento o Immagine", type=["pdf", "jpg", "png", "jpeg"])
    if uploaded_file:
        if "last_fn" not in st.session_state or st.session_state.last_fn != uploaded_file.name:
            st.session_state.last_fn = uploaded_file.name
            file_bytes = uploaded_file.read()
            if uploaded_file.type == "application/pdf":
                doc = fitz.open(stream=file_bytes, filetype="pdf")
                st.session_state.doc_text = "".join([p.get_text() for p in doc])[:8000]
                st.session_state.current_file = {"name": uploaded_file.name, "type": "pdf", "data": st.session_state.doc_text}
            else:
                st.session_state.doc_text = f"Analisi visiva del file: {uploaded_file.name}"
                st.session_state.current_file = {"name": uploaded_file.name, "type": "img", "data": file_bytes}
            st.rerun()

    st.markdown("---")
    # 2. SELETTORE AMBIENTE
    mode = st.radio("🎯 Seleziona Ambiente:", ["🏠 Famiglia", "💼 Business", "🔬 Specialista"])
    
    st.markdown("---")
    if st.button("🗑️ RESET WORKSPACE"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.current_file = None
        st.rerun()
    
    if st.session_state.messages:
        chat_txt = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        st.download_button("📩 SCARICA REPORT", chat_txt, file_name=f"report_{mode}.txt")

# --- AREA CENTRALE (VISUALIZZAZIONE E ANALISI) ---
if st.session_state.current_file:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"<h3 style='color: #4facfe;'>🖼️ Anteprima</h3>", unsafe_allow_html=True)
        st.markdown('<div class="preview-box">', unsafe_allow_html=True)
        if st.session_state.current_file['type'] == "img":
            st.image(st.session_state.current_file['data'], use_container_width=True)
        else:
            st.write(st.session_state.doc_text)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h3 style='color: #4facfe;'>📝 Annotazioni Fasi</h3>", unsafe_allow_html=True)
        # Template Grafico Interattivo
        st.markdown('<div class="fase-box"><b>Fase 1:</b> Identificazione Contenuto</div>', unsafe_allow_html=True)
        st.text_area("Annotazione (Es. Contesto, Emozioni):", key="f1", height=60)
        
        st.markdown('<div class="fase-box"><b>Fase 2:</b> Analisi Visiva</div>', unsafe_allow_html=True)
        st.text_area("Annotazione (Es. Colori, Forme, Testi):", key="f2", height=60)
        
        st.markdown('<div class="fase-box"><b>Fase 3:</b> Elementi Chiave</div>', unsafe_allow_html=True)
        st.text_area("Annotazione (Es. Relazioni, Simboli):", key="f3", height=60)

else:
    if not st.session_state.messages:
        st.markdown("<br><br><h1 class='main-title'>⚡ RE-WIRE AI</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; font-size: 20px;'>Pronto in modalità: <b>{mode}</b></p>", unsafe_allow_html=True)

st.markdown("---")

# --- CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input(f"Esegui analisi su {st.session_state.current_file['name'] if st.session_state.current_file else 'documento'}..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        sys_msg = f"Sei RE-WIRE AI in modalità {mode}. Analizza basandoti su queste fasi: Identificazione, Analisi Visiva, Elementi Chiave, Interpretazione e Conclusione. Contesto: {st.session_state.doc_text}"
        r = requests.post(API_URL, 
            json={"model": MODEL_ID, "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}]}, 
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
        ans = r.json()['choices'][0]['message']['content']
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
