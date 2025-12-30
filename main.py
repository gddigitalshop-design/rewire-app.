import streamlit as st
import google.generativeai as genai
from PIL import Image
import fitz
import io

# --- 1. CONFIGURAZIONE GOOGLE (Versione 2026) ---
GEMINI_API_KEY = "AIzaSyCxnOHGouptLrRn491MLvOJrDyqF8aMC9Y"
genai.configure(api_key=GEMINI_API_KEY)

# Usiamo 'gemini-1.5-flash-latest' per stabilità a lungo termine
try:
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except:
    model = genai.GenerativeModel('gemini-pro-vision') # Fallback storico

st.set_page_config(page_title="RE-WIRE Business Intelligence", layout="wide", page_icon="🧠")

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

# --- 3. GESTIONE FILE ---
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
        st.image(img_obj, width=350)
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
                # Se c'è un'immagine, la inviamo come lista [testo, immagine]
                if img_obj:
                    response = model.generate_content([prompt, img_obj])
                else:
                    response = model.generate_content(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Errore tecnico: {e}")
                st.info("Prova a ricaricare la pagina o controlla la tua chiave API.")
