import streamlit as st
import google.generativeai as genai
from PIL import Image
import fitz  # PyMuPDF
import io

# --- 1. CONFIGURAZIONE GOOGLE GEMINI ---
# La tua chiave API appena fornita
GEMINI_API_KEY = "AIzaSyCxnOHGouptLrRn491MLvOJrDyqF8aMC9Y"
genai.configure(api_key=GEMINI_API_KEY)

# Usiamo il modello Flash 1.5: ultra-veloce e perfetto per la visione
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="RE-WIRE Business Intelligence", layout="wide", page_icon="🧠")

# --- 2. LOGIN DI PROTEZIONE ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Inserisci Password", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Accesso negato. Password errata.")
    st.stop()

# --- 3. GESTIONE MEMORIA E DOCUMENTI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def process_file(uploaded_file):
    """Gestisce sia Immagini che PDF (estraendo la prima pagina)"""
    if uploaded_file.type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        page = doc.load_page(0)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img
    else:
        return Image.open(uploaded_file)

# --- 4. INTERFACCIA UTENTE ---
st.title("🧠 RE-WIRE Business Intelligence")
st.subheader("Analisi AI Avanzata - Immagini e PDF")

with st.sidebar:
    st.header("📁 Hub Documenti")
    file = st.file_uploader("Carica una foto o un PDF", type=["jpg", "png", "jpeg", "pdf"])
    if st.button("🗑️ Svuota Chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("Motore: Google Gemini 1.5 Flash")

# Gestione del file caricato
img_obj = None
if file:
    try:
        img_obj = process_file(file)
        st.image(img_obj, width=400, caption="Documento caricato correttamente")
    except Exception as e:
        st.error(f"Errore nel caricamento del file: {e}")

# --- 5. CHAT INTERATTIVA ---
# Visualizza lo storico della conversazione
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input dell'utente
if prompt := st.chat_input("Fai una domanda sul documento..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("L'AI sta analizzando..."):
            try:
                # Gemini accetta una lista che può contenere sia testo che l'oggetto immagine direttamente
                input_data = [prompt]
                if img_obj:
                    input_data.append(img_obj)
                
                response = model.generate_content(input_data)
                risposta_testo = response.text
                
                st.markdown(risposta_testo)
                st.session_state.messages.append({"role": "assistant", "content": risposta_testo})
            except Exception as e:
                st.error(f"Errore tecnico con Gemini: {e}")
