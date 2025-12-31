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

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>⚡ RE-WIRE LOGIN</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Chiave d'accesso:", type="password")
        if st.button("ENTRA", use_container_width=True):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- INIZIALIZZAZIONE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""
if "current_file_data" not in st.session_state: st.session_state.current_file_data = None

# --- SIDEBAR ---
with st.sidebar:
    st.header("📁 Carica Documento")
    uploaded_file = st.file_uploader("Trascina PDF o Foto", type=["pdf", "jpg", "jpeg", "png"])
    
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

    if st.button("🗑️ Reset Totale"):
        st.session_state.clear()
        st.rerun()

# --- AREA CENTRALE: VISUALIZZAZIONE FILE ---
st.markdown("<h2 style='text-align: center;'>📄 Documento Attuale</h2>", unsafe_allow_html=True)

with st.container(border=True):
    if st.session_state.current_file_data:
        f = st.session_state.current_file_data
        if f["type"] == "image":
            st.image(f["data"], caption=f["name"], use_container_width=True)
        else:
            st.info(f"Testo PDF: {f['name']}")
            st.write(f["data"][:1000] + "...")
    else:
        st.write("Nessun file caricato.")

st.divider()

# --- CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Chiedi all'AI o scrivi 'Template Grafico'..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        # Logica Template Decisa
        if "template grafico" in prompt.lower():
            ans = (
                "### 🎨 Analisi Template Grafico\n"
                "- **Concetto:** Analisi visiva del file caricato.\n"
                "- **Layout:** Struttura consigliata basata sul contenuto.\n"
                "- **Colori:** Palette suggerita.\n"
                "- **Mood:** Atmosfera percepita."
            )
        else:
            payload = {
                "model": MODEL_ID,
                "messages": [
                    {"role": "system", "content": f"Sei un assistente business. Contesto: {st.session_state.doc_text}"},
                    {"role": "user", "content": prompt}
                ]
            }
            try:
                r = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
                ans = r.json()['choices'][0]['message']['content']
            except:
                ans = "Errore di connessione."
        
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
