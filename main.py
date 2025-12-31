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
if "current_file_data" not in st.session_state: st.session_state.current_file_data = None # Per salvare l'immagine/PDF

# --- SIDEBAR ---
with st.sidebar:
    st.header("📁 Carica Documento")
    uploaded_file = st.file_uploader("Trascina PDF o Foto", type=["pdf", "jpg", "jpeg", "png"])
    
    if uploaded_file:
        if "last_file_name" not in st.session_state or st.session_state.last_file_name != uploaded_file.name:
            st.session_state.messages = []
            st.session_state.last_file_name = uploaded_file.name
            
            with st.spinner(f"Elaborazione {uploaded_file.name}..."):
                if uploaded_file.type in ["image/jpeg", "image/png"]:
                    image_data = uploaded_file.read()
                    st.session_state.current_file_data = {"type": "image", "data": image_data, "name": uploaded_file.name}
                    st.session_state.doc_text = f"[Contenuto Immagine: {uploaded_file.name}]"
                    st.session_state.messages.append({"role": "assistant", "content": f"📸 Hai caricato l'immagine: `{uploaded_file.name}`. La sto guardando con attenzione!"})
                elif uploaded_file.type == "application/pdf":
                    pdf_data = uploaded_file.read()
                    doc = fitz.open(stream=pdf_data, filetype="pdf")
                    text = "".join([p.get_text() for p in doc])[:4000]
                    st.session_state.doc_text = text
                    st.session_state.current_file_data = {"type": "pdf", "data": text, "name": uploaded_file.name}
                    st.session_state.messages.append({"role": "assistant", "content": f"📄 Ho estratto il testo dal PDF: `{uploaded_file.name}`. Pronto per l'analisi!"})
                st.rerun()

    if st.button("🗑️ Reset Totale"):
        st.session_state.clear()
        st.rerun()

# --- AREA CENTRALE: VISUALIZZAZIONE FILE (Migliorata) ---
st.markdown("<h2 style='text-align: center;'>📄 Documento Attuale</h2>", unsafe_allow_html=True)

container_file = st.container(border=True)
with container_file:
    if st.session_state.current_file_data:
        file_info = st.session_state.current_file_data
        if file_info["type"] == "image":
            st.image(file_info["data"], caption=f"Immagine: {file_info['name']}", use_container_width=True)
        elif file_info["type"] == "pdf":
            st.info(f"Anteprima Testo dal PDF: {file_info['name']}")
            st.write(file_info["data"][:1000] + "...") # Mostra un'anteprima del testo
    else:
        st.write("Nessun file caricato al momento. Carica un PDF o una foto dalla barra laterale per iniziare l'analisi.")

st.divider()

# --- CHAT & LOGICA TEMPLATE ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Chiedi all'AI (es: 'Genera template grafico' o 'Riassumi questo documento')..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        context = st.session_state.doc_text if st.session_state.doc_text else "Nessun documento."
        
        # Logica per il template grafico (Più specifica)
        if "template grafico" in prompt.lower() and st.session_state.current_file_data and st.session_state.current_file_data["type"] == "image":
            response_content = f"Certo! Per l'immagine **{st.session_state.current_file_data['name']}**, ecco un'analisi per il tuo template grafico:\n\n"
            response_content += "- **Tema/Concetto:** [Descrivi il tema principale o il messaggio vis
