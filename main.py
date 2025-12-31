import streamlit as st
import google.generativeai as genai
from PIL import Image
import fitz
import io

# --- 1. CONFIGURAZIONE GOOGLE GEMINI ---
# Usiamo la tua chiave Google che abbiamo testato prima
API_KEY = "AIzaSyA8UTodWbYVU3Kzvc4Cg2brAoPinj5ciZc"
genai.configure(api_key=API_KEY)

# Usiamo il nome del modello "stabile" senza prefissi beta
MODEL_ID = 'gemini-1.5-flash'
model = genai.GenerativeModel(MODEL_ID)

st.set_page_config(page_title="RE-WIRE Business Vision", layout="wide", page_icon="🧠")

# --- 2. LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Password Licenza", type="password")
    if st.button("SBLOCCA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. FUNZIONI ---
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

if "messages" not in st.session_state:
    st.session_state.messages = []

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

if prompt := st.chat_input("Analizza questo documento..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            try:
                # Se c'è un'immagine, la inviamo come lista [immagine, testo]
                # Invertire l'ordine [img, testo] spesso risolve i problemi di visione
                if img_obj:
                    response = model.generate_content([img_obj, prompt])
                else:
                    response = model.generate_content(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Errore tecnico: {e}")
                st.info("Se vedi ancora 404, vai su Google AI Studio e attiva 'Generative Language API'.")
