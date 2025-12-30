import streamlit as st
import google.generativeai as genai
from PIL import Image
from PyPDF2 import PdfReader

# --- 1. CONFIGURAZIONE API ---
API_KEY = "AIzaSyAI6SNpjbh0nft9dlzxHADUiquQBXDC1pE"

# Configurazione forzata sulla versione stabile
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="RE-WIRE Business Vision", layout="wide")

# --- 2. STILE PREMIUM ---
st.markdown("""
    <style>
    .report-box { 
        background-color: #1E1E1E; color: #FFFFFF; padding: 25px; 
        border-radius: 15px; border-left: 5px solid #FF4B4B; 
        line-height: 1.6; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MEMORIA SESSIONE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# --- 4. SIDEBAR (LA PARTE CHE HAI TESTATO) ---
with st.sidebar:
    st.title("🚀 RE-WIRE Hub")
    st.divider()
    
    # Il caricamento che funzionava
    file_caricato = st.file_uploader("Carica immagine o PDF", type=["jpg", "png", "jpeg", "pdf"])
    
    immagine_per_ai = None
    if file_caricato:
        if file_caricato.type in ["image/jpeg", "image/png"]:
            immagine_per_ai = Image.open(file_caricato)
            st.image(immagine_per_ai, caption="Immagine pronta", use_container_width=True)
        elif file_caricato.type == "application/pdf":
            reader = PdfReader(file_caricato)
            testo = ""
            for page in reader.pages:
                testo += page.extract_text() + "\n"
            st.session_state.pdf_text = testo
            st.success("Documento letto!")

    if st.button("🗑️ RESET CHAT"):
        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.rerun()

# --- 5. CHAT E ANALISI ---
st.title("🧠 RE-WIRE Business Brain")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f'<div class="report-box">{msg["content"]}</div>' if msg["role"] == "assistant" else msg["content"], unsafe_allow_html=True)

prompt = st.chat_input("Scrivi qui (es. Descrivi per bambini)...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            try:
                # TRUCCO: Specifichiamo il modello in modo che eviti la versione beta
                # Proviamo 'gemini-1.5-flash-latest' che è il più robusto
                model = genai.GenerativeModel('models/gemini-1.5-flash')
                
                contenuto = [prompt]
                if immagine_per_ai:
                    contenuto.append(immagine_per_ai)
                if st.session_state.pdf_text:
                    contenuto[0] += f"\n\nUsa queste info: {st.session_state.pdf_text[:5000]}"

                response = model.generate_content(contenuto)
                
                st.markdown(f'<div class="report-box">{response.text}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                # Se fallisce ancora, il problema è nella chiave o nei contratti Google
                st.error(f"Errore: {e}")
                st.info("⚠️ Soluzione rapida: Vai su https://aistudio.google.com/ e accetta i Termini di Servizio.")
