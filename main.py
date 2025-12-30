import streamlit as st
import google.generativeai as genai
from PIL import Image
import fitz  # PyMuPDF
import io

# --- 1. CONFIGURAZIONE GOOGLE GEMINI (Nomi modelli 2026) ---
GEMINI_API_KEY = "AIzaSyCxnOHGouptLrRn491MLvOJrDyqF8aMC9Y"
genai.configure(api_key=GEMINI_API_KEY)

# Abbiamo cambiato 'gemini-1.5-flash' con 'models/gemini-1.5-flash' 
# che è il percorso corretto richiesto dalle nuove API
model = genai.GenerativeModel('models/gemini-1.5-flash')

st.set_page_config(page_title="RE-WIRE AI Business", layout="wide", page_icon="🧠")

# --- 2. LOGIN DI SICUREZZA ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 RE-WIRE AI | Accesso Clienti")
    pwd = st.text_input("Inserisci Password Licenza", type="password")
    if st.button("ACCEDI AL SISTEMA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Password errata.")
    st.stop()

# --- 3. GESTIONE MEMORIA E FILE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def process_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        page = doc.load_page(0)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img
    else:
        return Image.open(uploaded_file)

# --- 4. INTERFACCIA PRINCIPALE ---
st.title("🧠 RE-WIRE Business Intelligence")

with st.sidebar:
    st.header("📁 Documenti")
    file = st.file_uploader("Carica Foto o PDF", type=["jpg", "png", "jpeg", "pdf"])
    if st.button("🗑️ Svuota Chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("Sistema attivo: Gemini Flash Stable")

img_obj = None
if file:
    try:
        img_obj = process_file(file)
        st.image(img_obj, width=350, caption="Documento pronto per analisi")
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
                # La nuova sintassi richiede una lista [testo, immagine]
                if img_obj:
                    response = model.generate_content([prompt, img_obj])
                else:
                    response = model.generate_content(prompt)
                
                risposta_finale = response.text
                st.markdown(risposta_finale)
                st.session_state.messages.append({"role": "assistant", "content": risposta_finale})
            except Exception as e:
                st.error(f"Errore tecnico: {e}")
                st.info("Verifica che la tua chiave API sia attiva su Google AI Studio.")
