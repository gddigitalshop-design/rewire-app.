import streamlit as st
import google.generativeai as genai
from PIL import Image
import fitz
import io

# --- 1. CONFIGURAZIONE ---
GEMINI_API_KEY = "AIzaSyA8UTodWbYVU3Kzvc4Cg2brAoPinj5ciZc"
genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="RE-WIRE AI Business", layout="wide", page_icon="🧠")

# --- 2. LOGIN (Password: rewire2026) ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Inserisci Password Licenza", type="password")
    if st.button("SBLOCCA SISTEMA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. FUNZIONI TECNICHE ---
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
                # FORZIAMO IL MODELLO ALL'INTERNO DELLA CHIAMATA
                # Usiamo il nome corto senza 'models/' per evitare il 404
                vision_model = genai.GenerativeModel('gemini-1.5-flash')
                
                if img_obj:
                    # Se c'è l'immagine, usiamo la lista [testo, immagine]
                    response = vision_model.generate_content([prompt, img_obj])
                else:
                    response = vision_model.generate_content(prompt)
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                # SE FALLISCE, PROVIAMO IL MODELLO PRO (Backup estremo)
                try:
                    backup_model = genai.GenerativeModel('gemini-1.5-pro')
                    response = backup_model.generate_content([prompt, img_obj] if img_obj else prompt)
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e2:
                    st.error(f"Errore critico Google: {e2}")
                    st.info("Nota per l'amministratore: Controlla che il piano 'Pay-as-you-go' sia attivo su Google AI Studio per abilitare i modelli Flash 1.5.")
