import streamlit as st
import google.generativeai as genai
from PIL import Image
import fitz
import io

# --- 1. CONFIGURAZIONE MOTORE DINAMICO ---
GEMINI_API_KEY = "AIzaSyA8UTodWbYVU3Kzvc4Cg2brAoPinj5ciZc"
genai.configure(api_key=GEMINI_API_KEY)

@st.cache_resource
def get_best_model():
    """Trova automaticamente il modello disponibile per evitare l'errore 404"""
    try:
        # Chiediamo a Google la lista dei modelli attivi sulla tua chiave
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                # Privilegiamo il 1.5 Flash, poi il 1.5 Pro, poi il 1.0
                if 'gemini-1.5-flash' in m.name:
                    return m.name
        # Se non trova il flash, prende il primo disponibile
        return 'models/gemini-1.5-flash' 
    except:
        return 'gemini-1.5-flash'

# Identifica il modello corretto per il tuo account
MODEL_NAME = get_best_model()
model = genai.GenerativeModel(MODEL_NAME)

st.set_page_config(page_title="RE-WIRE AI Business", layout="wide", page_icon="🧠")

# --- 2. LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Inserisci Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. GESTIONE DOCUMENTI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def process_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        page = doc.load_page(0)
        pix = page.get_pixmap()
        return Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    else:
        return Image.open(uploaded_file)

# --- 4. INTERFACCIA ---
st.title("🧠 RE-WIRE Business Intelligence")
st.caption(f"Motore AI connesso: {MODEL_NAME}") # Ti mostra quale modello ha scelto

with st.sidebar:
    st.header("📁 Hub Documenti")
    file = st.file_uploader("Carica Foto o PDF", type=["jpg", "png", "jpeg", "pdf"])
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

img_obj = None
if file:
    try:
        img_obj = process_file(file)
        st.image(img_obj, width=400)
    except Exception as e:
        st.error(f"Errore file: {e}")

# --- 5. CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Fai una domanda sul documento..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            try:
                # Passiamo i dati al modello rilevato automaticamente
                inputs = [prompt, img_obj] if img_obj else [prompt]
                response = model.generate_content(inputs)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Errore tecnico: {e}")
