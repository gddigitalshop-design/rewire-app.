import streamlit as st
import google.generativeai as genai
from PIL import Image
import fitz  # PyMuPDF per i PDF
import io

# --- 1. CONFIGURAZIONE MOTORE GOOGLE STABLE ---
# Utilizziamo la tua nuova chiave API
GEMINI_API_KEY = "AIzaSyA8UTodWbYVU3Kzvc4Cg2brAoPinj5ciZc"
genai.configure(api_key=GEMINI_API_KEY)

# Puntiamo al modello Flash 1.5, il più affidabile per la visione
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="RE-WIRE Business Vision", layout="wide", page_icon="🧠")

# --- 2. SISTEMA DI LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 RE-WIRE AI | Accesso Licenza")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Inserisci Password Licenza", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Accesso negato. Password errata.")
    st.stop()

# --- 3. GESTIONE DOCUMENTI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def process_file(uploaded_file):
    """Estrae l'immagine da una foto o dalla prima pagina di un PDF"""
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

with st.sidebar:
    st.header("📁 Hub Documenti")
    file = st.file_uploader("Carica una foto o un PDF", type=["jpg", "png", "jpeg", "pdf"])
    if st.button("🗑️ Svuota Chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("Versione 2026.1 - Motore Gemini Stable")

# Anteprima del documento
img_obj = None
if file:
    try:
        img_obj = process_file(file)
        st.image(img_obj, width=400, caption="Documento pronto per l'analisi")
    except Exception as e:
        st.error(f"Errore caricamento: {e}")

# --- 5. CHAT INTERATTIVA ---
# Mostra la cronologia messaggi
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Barra di input per l'utente
if prompt := st.chat_input("Fai una domanda sul documento..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi RE-WIRE in corso..."):
            try:
                # Se c'è un'immagine, la inviamo insieme al prompt testuale
                if img_obj:
                    response = model.generate_content([prompt, img_obj])
                else:
                    response = model.generate_content(prompt)
                
                # Visualizza e salva la risposta
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"⚠️ Errore di connessione: {e}")
                st.info("Assicurati di non aver superato i limiti della tua chiave API.")
