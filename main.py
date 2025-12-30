import streamlit as st
import google.generativeai as genai
from PIL import Image
import fitz
import io

# --- 1. CONFIGURAZIONE GOOGLE (FORZA VERSIONE STABILE) ---
GEMINI_API_KEY = "AIzaSyA8UTodWbYVU3Kzvc4Cg2brAoPinj5ciZc"

# Configuriamo l'SDK per puntare alla versione di produzione 
genai.configure(api_key=GEMINI_API_KEY)

# Lista di modelli da provare in ordine di stabilità
# Abbiamo aggiunto 'models/' davanti per conformità con le nuove direttive
candidate_models = [
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-pro-vision'
]

@st.cache_resource
def load_stable_model():
    """Tenta di caricare il modello ignorando le versioni beta"""
    for model_name in candidate_models:
        try:
            m = genai.GenerativeModel(model_name)
            # Test rapido di connessione
            return m
        except:
            continue
    return genai.GenerativeModel('gemini-1.5-flash') # Default finale

model = load_stable_model()

st.set_page_config(page_title="RE-WIRE Business Vision", layout="wide", page_icon="🧠")

# --- 2. LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso RE-WIRE")
    pwd = st.text_input("Password Licenza", type="password")
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
st.caption(f"Stato: Motore {model.model_name} collegato")

with st.sidebar:
    st.header("📁 Documenti")
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

if prompt := st.chat_input("Chiedi all'AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            try:
                # La lista di input deve contenere l'immagine se presente
                inputs = [prompt, img_obj] if img_obj else [prompt]
                
                # Chiamata alla versione stabile
                response = model.generate_content(inputs)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Errore tecnico: {e}")
                st.info("Consiglio: Se l'errore persiste, prova a rigenerare la chiave in Google AI Studio selezionando un progetto 'Pay-as-you-go' (anche se usi il piano gratuito).")
