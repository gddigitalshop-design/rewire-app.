import streamlit as st
import requests
import fitz

# --- CONFIGURAZIONE API ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE AI - Hub Multifunzione", layout="wide", page_icon="⚡")

# --- DESIGN "PREMIUM GLASS" (CSS) ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #1e2a4a, #0d1117); color: #e6edf3; }
    .main-title { font-size: 50px !important; font-weight: 900 !important; background: linear-gradient(90deg, #00f2fe, #4facfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 0px; }
    .stChatMessage { background: rgba(255, 255, 255, 0.05) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 15px !important; margin-bottom: 10px; }
    [data-testid="stSidebar"] { background-color: rgba(13, 17, 23, 0.9); border-right: 1px solid rgba(0, 242, 254, 0.2); }
    .stButton > button { border-radius: 20px !important; background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%) !important; color: #0d1117 !important; font-weight: bold !important; width: 100%; border: none !important; transition: 0.3s; }
    .stButton > button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4); }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<br><br><h1 class='main-title'>⚡ RE-WIRE</h1>", unsafe_allow_html=True)
        with st.container(border=True):
            pwd = st.text_input("Chiave d'Accesso Premium:", type="password")
            if st.button("ACCEDI AL SISTEMA"):
                if pwd == "rewire2026": st.session_state.auth = True; st.rerun()
                else: st.error("Chiave errata.")
    st.stop()

# --- INIZIALIZZAZIONE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""

# --- SIDEBAR: SELETTORE MODALITÀ ---
with st.sidebar:
    st.markdown("<h2 style='color: #4facfe; text-align: center;'>DASHBOARD</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # 1. SCELTA DELLA MODALITÀ (IL CUORE DELLA TUA DOMANDA)
    mode = st.radio("🎯 Seleziona Ambiente:", ["🏠 Famiglia", "💼 Lavoro / Business", "🐝 Specialista (Apicoltura)"])
    
    st.markdown("---")
    st.markdown("### 🚀 Azioni Rapide")
    
    # Comandi dinamici in base alla modalità
    if mode == "🏠 Famiglia":
        if st.button("📊 Genera Template Casa"):
            st.session_state.force_prompt = "Genera il template RE-WIRE per CASA (Spesa, Pulizie, Medici) con tabelle."
    
    elif mode == "💼 Lavoro / Business":
        if st.button("📈 Genera Piano Progetto"):
            st.session_state.force_prompt = "Genera un template BUSINESS per la gestione di un progetto, con Task, Responsabile, Scadenza e Budget."
    
    else: # Apicoltura
        if st.button("🍯 Registro Arnie"):
            st.session_state.force_prompt = "Genera un registro per APICOLTURA: ID Arnia, Stato Regina, Scorte Cibo e Trattamenti effettuati."

    st.markdown("---")
    if st.button("🗑️ RESET WORKSPACE"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.rerun()
    
    if st.session_state.messages:
        chat_txt = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
        st.download_button("📩 SCARICA REPORT", chat_txt, file_name=f"report_{mode}.txt")

# --- LOGICA DI RISPOSTA AUTOMATICA ---
if "force_prompt" in st.session_state:
    p = st.session_state.force_prompt
    del st.session_state.force_prompt
    st.session_state.messages.append({"role": "user", "content": p})
    
    system_instr = f"Sei RE-WIRE AI in modalità {mode}. Fornisci template professionali, fluidi e precisi per questo specifico settore."
    
    r = requests.post(API_URL, json={"model": MODEL_ID, "messages": [{"role": "system", "content": system_instr}, {"role": "user", "content": p}]}, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
    ans = r.json()['choices'][0]['message']['content']
    st.session_state.messages.append({"role": "assistant", "content": ans})

# --- AREA CENTRALE ---
if not st.session_state.messages:
    st.markdown("<br><br><h1 class='main-title'>⚡ RE-WIRE AI</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 20px;'>Pronto per operare in modalità: <b>{mode}</b></p>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; opacity: 0.5;'>Scegli un'azione rapida a sinistra o scrivi un comando qui sotto.</p>", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input(f"Chiedi a RE-WIRE ({mode})..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        sys_msg = f"Sei RE-WIRE AI ottimizzato per {mode}. Sii brillante, amichevole e molto accurato."
        r = requests.post(API_URL, json={"model": MODEL_ID, "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": prompt}]}, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
        ans = r.json()['choices'][0]['message']['content']
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
