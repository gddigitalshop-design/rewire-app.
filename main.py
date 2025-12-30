import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from PIL import Image

# --- 1. CONFIGURAZIONE API ---
# Uso la tua nuova chiave
API_KEY = "AIzaSyAI6SNpjbh0nft9dlzxHADUiquQBXDC1pE"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="RE-WIRE | AI Strategic Partner", layout="wide", page_icon="🧠")

# --- 2. STILE PERSONALIZZATO ---
st.markdown("""
    <style>
    .report-box { 
        background-color: #1E1E1E; color: #FFFFFF; padding: 25px; 
        border-radius: 15px; border-left: 5px solid #FF4B4B; 
        line-height: 1.6; margin-bottom: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MEMORIA SESSIONE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# --- 4. BARRA LATERALE ---
with st.sidebar:
    st.title("🚀 RE-WIRE Hub")
    st.write("Stato: **Motore Gemini Online**")
    st.divider()
    
    uploaded_file = st.file_uploader("Carica Immagine o PDF", type=["jpg", "png", "jpeg", "pdf", "txt"])
    
    current_image = None
    if uploaded_file:
        if uploaded_file.type in ["image/jpeg", "image/png"]:
            current_image = Image.open(uploaded_file)
            st.image(current_image, caption="Immagine pronta", use_container_width=True)
        elif uploaded_file.type == "application/pdf":
            try:
                reader = PdfReader(uploaded_file)
                full_text = ""
                for page in reader.pages:
                    full_text += page.extract_text() + "\n"
                st.session_state.pdf_text = full_text
                st.success("PDF caricato correttamente!")
            except:
                st.error("Errore nella lettura del PDF.")
    
    st.divider()
    if st.button("🗑️ AZZERA CONVERSAZIONE", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.rerun()

# --- 5. AREA DI LAVORO (CHAT) ---
st.title("🧠 RE-WIRE Business Brain")

# Visualizzazione Cronologia
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(f'<div class="report-box">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# Input Utente
prompt = st.chat_input("Di cosa hai bisogno oggi?")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("RE-WIRE sta elaborando..."):
            try:
                # TENTATIVO CON GEMINI 1.5 FLASH (Veloce)
                # Se questo dà 404, il blocco 'except' catturerà l'errore
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Prepariamo il contenuto
                content_list = []
                
                # Testo principale + contesto PDF
                final_prompt = prompt
                if st.session_state.pdf_text:
                    final_prompt += f"\n\n[RIFERIMENTO DOCUMENTO]:\n{st.session_state.pdf_text[:8000]}"
                
                content_list.append(final_prompt)
                
                # Aggiungiamo l'immagine se caricata
                if current_image:
                    content_list.append(current_image)

                # Generazione
                response = model.generate_content(content_list)
                
                if response:
                    res_text = response.text
                    st.markdown(f'<div class="report-box">{res_text}</div>', unsafe_allow_html=True)
                    st.session_state.messages.append({"role": "assistant", "content": res_text})
                
            except Exception as e:
                # FALLBACK: Se Flash fallisce, prova il modello Pro o mostra errore utile
                if "404" in str(e):
                    st.error("Errore: Il modello non è stato trovato. Assicurati di aver abilitato le API di Gemini nel tuo Google AI Studio.")
                else:
                    st.error(f"Si è verificato un problema: {e}")
