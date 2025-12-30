import streamlit as st
import requests
import base64
from PIL import Image
import fitz
import io

# --- 1. CONFIGURAZIONE DIRETTA ---
API_KEY = "AIzaSyA8UTodWbYVU3Kzvc4Cg2brAoPinj5ciZc"
# URL della versione STABILE v1 (evitiamo la v1beta che dà errore)
API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}"

st.set_page_config(page_title="RE-WIRE Business Vision", layout="wide", page_icon="🧠")

# --- 2. LOGIN (Password: rewire2026) ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Inserisci Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. FUNZIONI TECNICHE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def process_file_to_base64(uploaded_file):
    if uploaded_file.type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        page = doc.load_page(0)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    else:
        img = Image.open(uploaded_file)
    
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8'), img

# --- 4. INTERFACCIA ---
st.title("🧠 RE-WIRE Business Intelligence")

with st.sidebar:
    st.header("📁 Hub Documenti")
    file = st.file_uploader("Carica Foto o PDF", type=["jpg", "png", "jpeg", "pdf"])
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

img_b64 = None
if file:
    img_b64, img_display = process_file_to_base64(file)
    st.image(img_display, width=400)

# --- 5. CHAT CON CHIAMATA DIRETTA ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Fai una domanda..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            # Costruiamo il pacchetto dati (JSON) da inviare a Google
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            if img_b64:
                payload["contents"][0]["parts"].append({
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": img_b64
                    }
                })

            try:
                response = requests.post(API_URL, json=payload)
                result = response.json()
                
                if response.status_code == 200:
                    answer = result['candidates'][0]['content']['parts'][0]['text']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Errore API {response.status_code}: {result.get('error', {}).get('message', 'Errore ignoto')}")
            except Exception as e:
                st.error(f"Errore di connessione: {e}")
