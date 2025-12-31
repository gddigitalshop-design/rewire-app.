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

# --- LOGIN (Stessa logica) ---
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
if "current_img" not in st.session_state: st.session_state.current_img = None

# --- SIDEBAR ---
with st.sidebar:
    st.header("📁 Carica Documento")
    file = st.file_uploader("Trascina PDF o Foto", type=["pdf", "jpg", "jpeg", "png"])
    
    if file:
        if "last_file" not in st.session_state or st.session_state.last_file != file.name:
            st.session_state.messages = []
            st.session_state.last_file = file.name
            
            if file.type in ["image/jpeg", "image/png"]:
                image = Image.open(file)
                st.session_state.current_img = image
                st.session_state.doc_text = f"[Analisi Immagine: {file.name}]"
            elif file.type == "application/pdf":
                doc = fitz.open(stream=file.read(), filetype="pdf")
                st.session_state.doc_text = "".join([p.get_text() for p in doc])[:4000]
                st.session_state.current_img = None
            st.rerun()

    if st.button("🗑️ Reset Totale"):
        st.session_state.clear()
        st.rerun()

# --- AREA CENTRALE: VISUALIZZAZIONE FILE ---
st.markdown("<h2 style='text-align: center;'>📄 File in Analisi</h2>", unsafe_allow_html=True)

container_file = st.container(border=True)
with container_file:
    if st.session_state.current_img:
        # VISUALIZZA FOTO AL CENTRO
        st.image(st.session_state.current_img, caption="Immagine Caricata", use_container_width=True)
    elif st.session_state.doc_text:
        # VISUALIZZA TESTO PDF AL CENTRO
        st.info("Testo estratto dal documento:")
        st.write(st.session_state.doc_text[:1000] + "...")
    else:
        st.write("Nessun file visualizzato. Carica un documento dalla sidebar.")

st.divider()

# --- CHAT & TEMPLATE ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Chiedi all'AI o scrivi 'Applica Template'..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        # Logica Template: Se l'utente chiede un template, l'AI usa una struttura fissa
        system_instruction = "Sei un analista. Se richiesto un template, usa: 1. Riassunto, 2. Punti Critici, 3. Azioni Consigliate."
        
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": f"{system_instruction} | Contesto: {st.session_state.doc_text}"},
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            r = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
            ans = r.json()['choices'][0]['message']['content']
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
        except:
            st.error("Errore AI")
    st.rerun()
