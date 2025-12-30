import streamlit as st
import google.generativeai as genai
from PIL import Image
from PyPDF2 import PdfReader

# --- 1. CONFIGURAZIONE API ---
# Inserisco la tua chiave che abbiamo testato
API_KEY = "AIzaSyAI6SNpjbh0nft9dlzxHADUiquQBXDC1pE"
genai.configure(api_key=API_KEY)

# --- 2. CONFIGURAZIONE PAGINA & STILE ---
st.set_page_config(page_title="RE-WIRE Business Vision", layout="wide")

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

# --- 3. MEMORIA SESSIONE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. SIDEBAR (IL PEZZO CHE HAI TESTATO) ---
with st.sidebar:
    st.title("🚀 RE-WIRE Hub")
    st.write("Configurazione: **Gemini Vision Attivo**")
    st.divider()
    
    st.subheader("📁 Carica Allegato")
    # Questo è il widget che hai confermato funzionare:
    file_caricato = st.file_uploader("Scegli un'immagine o un PDF", type=["jpg", "png", "jpeg", "pdf"])
    
    immagine_per_ai = None
    testo_pdf = ""

    if file_caricato:
        if file_caricato.type in ["image/jpeg", "image/png"]:
            immagine_per_ai = Image.open(file_caricato)
            st.image(immagine_per_ai, caption="Anteprima Immagine", use_container_width=True)
        elif file_caricato.type == "application/pdf":
            reader = PdfReader(file_caricato)
            for page in reader.pages:
                testo_pdf += page.extract_text() + "\n"
            st.success("PDF caricato!")

    if st.button("🗑️ CANCELLA CHAT", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- 5. CHAT PRINCIPALE ---
st.title("🧠 RE-WIRE Business Brain")

# Visualizza messaggi precedenti
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(f'<div class="report-box">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# Input Utente
prompt = st.chat_input("Scrivi qui la tua richiesta (es. 'Fai un testo per bambini')...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            try:
                # Usiamo il modello Flash che hai testato con successo
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Prepariamo la richiesta multimodale
                input_data = []
                testo_completo = prompt
                if testo_pdf:
                    testo_completo += f"\n\nUsa queste info: {testo_pdf[:5000]}"
                
                input_data.append(testo_completo)
                if immagine_per_ai:
                    input_data.append(immagine_per_ai)

                # Risposta dell'AI
                response = model.generate_content(input_data)
                risposta_testo = response.text
                
                st.markdown(f'<div class="report-box">{risposta_testo}</div>', unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": risposta_testo})
                
            except Exception as e:
                st.error(f"Errore: {e}")
