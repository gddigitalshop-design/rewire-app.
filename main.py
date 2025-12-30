import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from PIL import Image
import io

# --- 1. CONFIGURAZIONE API ---
# Inserisco la tua chiave direttamente per testarla, ma ricorda di metterla nei Secrets in futuro!
API_KEY = "AIzaSyApziQVDY3_L9-q_NSOufAFab_syWdRFYY"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="RE-WIRE | AI Vision & Strategy", layout="wide", page_icon="🧠")

# --- 2. STILE CSS ---
st.markdown("""
    <style>
    .report-box { 
        background-color: #1E1E1E; color: #FFFFFF; padding: 25px; 
        border-radius: 15px; border-left: 5px solid #FF4B4B; 
        line-height: 1.6; margin-bottom: 20px;
    }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGICA DI MEMORIA ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_context" not in st.session_state:
    st.session_state.doc_context = ""

# --- 4. SIDEBAR (CARICAMENTO FILE) ---
with st.sidebar:
    st.title("🚀 RE-WIRE Hub")
    st.write("Stato: **Gemini Vision Attivo**")
    st.divider()
    
    uploaded_file = st.file_uploader("Carica Immagine (JPG/PNG) o PDF", type=["jpg", "png", "jpeg", "pdf", "txt"])
    
    img_to_send = None
    if uploaded_file:
        if uploaded_file.type in ["image/jpeg", "image/png"]:
            img_to_send = Image.open(uploaded_file)
            st.image(img_to_send, caption="Anteprima Immagine", use_container_width=True)
        elif uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            text = ""
            for page in reader.pages: text += page.extract_text() + "\n"
            st.session_state.doc_context = text
            st.success("Testo PDF estratto!")
    
    st.divider()
    if st.button("🧹 NUOVA SESSIONE", use_container_width=True):
        st.session_state.messages = []
        st.session_state.doc_context = ""
        st.rerun()

# --- 5. AREA CHAT ---
st.title("🧠 RE-WIRE Business Brain")

# Mostra lo storico
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(f'<div class="report-box">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# Input Utente
prompt = st.chat_input("Chiedimi qualsiasi cosa, carica un'immagine o chiedi un testo per bambini...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("RE-WIRE sta elaborando (Gemini Vision)..."):
            try:
                # Scegliamo il modello Flash per velocità e visione
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Costruiamo la richiesta
                request_parts = [prompt]
                
                # Aggiungiamo l'immagine se presente
                if img_to_send:
                    request_parts.append(img_to_send)
                
                # Aggiungiamo il contesto del PDF se presente
                if st.session_state.doc_context:
                    request_parts.append(f"\n\nContesto Documento: {st.session_state.doc_context[:10000]}")

                # Generazione risposta
                response = model.generate_content(request_parts)
                answer = response.text
                
                st.markdown(f'<div class="report-box">{answer}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                st.error(f"Errore tecnico: {e}")
