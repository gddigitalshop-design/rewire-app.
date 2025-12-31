import streamlit as st
import requests
import fitz

# --- CONFIGURAZIONE API ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI", layout="wide", page_icon="⚡")

# --- CSS (MANTENIAMO IL LOOK PREMIUM) ---
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #1e2a4a, #0d1117); color: #e6edf3; }
    .main-title { font-size: 55px !important; font-weight: 900 !important; background: linear-gradient(90deg, #00f2fe, #4facfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
    .stChatMessage { background: rgba(255, 255, 255, 0.04) !important; border: 1px solid rgba(255, 255, 255, 0.1) !important; border-radius: 20px !important; }
    .stButton > button { border-radius: 30px !important; background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%) !important; color: #0d1117 !important; font-weight: bold !important; border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.8, 1])
    with col:
        st.markdown("<h1 class='main-title'>⚡ RE-WIRE</h1>", unsafe_allow_html=True)
        pwd = st.text_input("🔑 Chiave d'Accesso:", type="password")
        if st.button("SBLOCCA RE-WIRE"):
            if pwd == "rewire2026": st.session_state.auth = True; st.rerun()
    st.stop()

# --- INIT ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""

# --- SIDEBAR CON COMANDI RAPIDI ---
with st.sidebar:
    st.markdown("<h1 style='font-size: 25px; color: #4facfe;'>⚡ RE-WIRE AI</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown("### 🚀 Azioni Rapide")
    # Questo tasto genera il template senza che tu debba scrivere nulla o spiegare nulla!
    if st.button("🏠 GENERA TEMPLATE CASA"):
        st.session_state.messages = [] # Reset pulito
        st.session_state.force_prompt = "Genera il template organizzativo RE-WIRE per la mia casa (Spesa, Pulizie, Medici) con tabelle e spazi per 'CHI LO FA' e 'STATO'."
    
    st.markdown("---")
    if st.button("🗑️ RESET TOTALE"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.rerun()

# --- LOGICA DI RISPOSTA AUTOMATICA (PER AZIONI RAPIDE) ---
if "force_prompt" in st.session_state:
    p = st.session_state.force_prompt
    del st.session_state.force_prompt
    # Inseriamo il prompt forzato nella chat
    st.session_state.messages.append({"role": "user", "content": p})
    # Chiamata API immediata
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": "Sei l'assistente RE-WIRE. Conosci a memoria i template organizzativi per la casa. Non fare domande, genera direttamente le tabelle richieste."},
            {"role": "user", "content": p}
        ]
    }
    r = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
    ans = r.json()['choices'][0]['message']['content']
    st.session_state.messages.append({"role": "assistant", "content": ans})

# --- AREA CHAT ---
if not st.session_state.messages:
    st.markdown("<br><br><h1 class='main-title'>⚡ RE-WIRE AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Buongiorno! Usa i comandi rapidi a sinistra o scrivi qui sotto.</p>", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Scrivi qui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        r = requests.post(API_URL, json={"model": MODEL_ID, "messages": [{"role": "system", "content": "Sei RE-WIRE AI, assistente casa."}, {"role": "user", "content": prompt}]}, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
        ans = r.json()['choices'][0]['message']['content']
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
