import streamlit as st
import google.generativeai as genai
from PIL import Image
import fitz  # PyMuPDF
import io

# --- 1. CONFIGURAZIONE GOOGLE GEMINI (Versione Stabile) ---
GEMINI_API_KEY = "AIzaSyCxnOHGouptLrRn491MLvOJrDyqF8aMC9Y"

# Forza l'uso della versione stabile delle API invece della beta
genai.configure(api_key=GEMINI_API_KEY)

# Usiamo il modello Flash: è il più compatibile con le immagini
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="RE-WIRE AI Business", layout="wide", page_icon="🧠")

# --- 2. LOGIN (Password: rewire2026) ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Inserisci Password", type="password")
    if st.button("SBLOCCA SISTEMA"):
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

with st.sidebar:
    st.header("📁 Hub Documenti")
    file = st.file_uploader("Carica Foto o PDF", type=["jpg", "png", "jpeg", "pdf"])
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("Motore: Gemini 1.5 Flash Stable")

img_obj = None
if file:
    try:
        img_obj = process_file(file)
        st.image(img_obj, width=400, caption="Documento analizzabile")
    except Exception as e:
        st.error(f"Errore caricamento: {e}")

# --- 5. CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Chiedi all'AI sul documento..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            try:
                # Se c'è un'immagine, la passiamo insieme al testo
                if img_obj:
                    # Nota: usiamo generate_content che è il metodo standard
                    response = model.generate_content([prompt, img_obj])
                else:
                    response = model.generate_content(prompt)
                
                res_text = response.text
                st.markdown(res_text)
                st.session_state.messages.append({"role": "assistant", "content": res_text})
            except Exception as e:
                st.error(f"Errore: {e}")
                st.info("Controlla che la chiave API sia attiva o prova a ricaricare.")
