import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from PIL import Image

# --- 1. CONFIGURAZIONE API ---
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
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGICA DI MEMORIA ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_context" not in st.session_state:
    st.session_state.doc_context = ""

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🚀 RE-WIRE Hub")
    st.write("Motore: **Gemini 1.5 Flash**")
    st.divider()
    
    uploaded_file = st.file_uploader("Carica Immagine o PDF", type=["jpg", "png", "jpeg", "pdf", "txt"])
    
    img_to_send = None
    if uploaded_file:
        if uploaded_file.type in ["image/jpeg", "image/png"]:
            img_to_send = Image.open(uploaded_file)
            st.image(img_to_send, caption="Immagine caricata", use_container_width=True)
        elif uploaded_file.type == "application/pdf":
            try:
                reader = PdfReader(uploaded_file)
                text = ""
                for page in reader.pages: text += page.extract_text() + "\n"
                st.session_state.doc_context = text
                st.success("Testo PDF estratto!")
            except:
                st.error("Errore lettura PDF")
    
    if st.button("🗑️ RESET CHAT", use_container_width=True):
        st.session_state.messages = []
        st.session_state.doc_context = ""
        st.rerun()

# --- 5. AREA CHAT ---
st.title("🧠 RE-WIRE Business Brain")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(f'<div class="report-box">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

prompt = st.chat_input("Scrivi qui (es. Descrivi l'immagine per un bambino)...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            try:
                # CORREZIONE QUI: Usiamo il nome del modello senza prefissi strani
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                # Prepariamo la richiesta
                request_content = []
                
                # Aggiungiamo il prompt testuale
                full_prompt = prompt
                if st.session_state.doc_context:
                    full_prompt += f"\n\nUsa queste informazioni dal PDF: {st.session_state.doc_context[:5000]}"
                
                request_content.append(full_prompt)
                
                # Se c'è un'immagine, la aggiungiamo alla lista
                if img_to_send:
                    request_content.append(img_to_send)

                # Generazione
                response = model.generate_content(request_content)
                
                if response.text:
                    answer = response.text
                    st.markdown(f'<div class="report-box">{answer}</div>', unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error("L'AI non ha prodotto testo. Riprova con un'altra immagine.")
                
            except Exception as e:
                st.error(f"Errore di connessione: {e}")
