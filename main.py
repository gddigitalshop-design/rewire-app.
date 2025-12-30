import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from PIL import Image

# --- 1. CONFIGURAZIONE API & MODELLO ---
API_KEY = "AIzaSyAI6SNpjbh0nft9dlzxHADUiquQBXDC1pE"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="RE-WIRE | AI Strategic Partner", layout="wide", page_icon="🧠")

# --- 2. STILE PREMIUM (BOX NERO E ROSSO) ---
st.markdown("""
    <style>
    .report-box { 
        background-color: #1E1E1E; color: #FFFFFF; padding: 25px; 
        border-radius: 15px; border-left: 5px solid #FF4B4B; 
        line-height: 1.6; margin-bottom: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MEMORIA DELLA SESSIONE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""

# --- 4. BARRA LATERALE (STRUMENTI) ---
with st.sidebar:
    st.title("🚀 RE-WIRE Hub")
    st.info("Oggi è il 30 Dicembre 2025")
    st.divider()
    
    st.subheader("📁 Carica Allegati")
    file = st.file_uploader("Immagine (JPG/PNG) o PDF", type=["jpg", "png", "jpeg", "pdf"])
    
    current_img = None
    if file:
        if file.type in ["image/jpeg", "image/png"]:
            current_img = Image.open(file)
            st.image(current_img, caption="Immagine pronta", use_container_width=True)
        elif file.type == "application/pdf":
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            st.session_state.pdf_context = text
            st.success("PDF caricato in memoria!")

    st.divider()
    if st.button("🗑️ AZZERA TUTTO", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pdf_context = ""
        st.rerun()

# --- 5. AREA CHAT PRINCIPALE ---
st.title("🧠 RE-WIRE Business Brain")

# Mostra i messaggi salvati
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(f'<div class="report-box">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# Input dell'utente
prompt = st.chat_input("Scrivi qui la tua richiesta...")

if prompt:
    # 1. Mostra il messaggio dell'utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Genera la risposta dell'AI
    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Prepariamo il pacchetto da inviare all'AI
                contenuto_da_inviare = []
                
                # Testo + eventuale contesto del PDF
                testo_finale = prompt
                if st.session_state.pdf_context:
                    testo_finale += f"\n\n[CONTESTO PDF CARICATO]:\n{st.session_state.pdf_text[:5000]}"
                
                contenuto_da_inviare.append(testo_finale)
                
                # Aggiungiamo l'immagine se presente
                if current_img:
                    contenuto_da_inviare.append(current_img)

                # Chiamata all'API
                response = model.generate_content(contenuto_da_inviare)
                risposta_ai = response.text
                
                # Visualizzazione elegante
                st.markdown(f'<div class="report-box">{risposta_ai}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": risposta_ai})
                
            except Exception as e:
                st.error(f"Errore: {e}")
