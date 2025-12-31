import streamlit as st
import requests
import base64
from PIL import Image
import fitz
import io

# --- 1. CONFIGURAZIONE OPENAI (La più stabile per la vendita) ---
# Inserisci qui la tua chiave OpenAI (inizia con sk-...)
OPENAI_API_KEY = "INSERISCI_QUI_LA_TUA_CHIAVE_OPENAI"
API_URL = "https://api.openai.com/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE Business Vision", layout="wide", page_icon="🧠")

# --- 2. LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Inserisci Password Licenza", type="password")
    if st.button("SBLOCCA SISTEMA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. FUNZIONI ---
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

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("📁 Hub Documenti")
    file = st.file_uploader("Carica Foto o PDF", type=["jpg", "png", "jpeg", "pdf"])
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("Motore: GPT-4o-mini (Professional)")

img_b64 = None
if file:
    img_b64, img_display = process_file_to_base64(file)
    st.image(img_display, width=400)

# --- 5. CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Chiedi all'AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi professionale in corso..."):
            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Payload standard OpenAI Vision
            payload = {
                "model": "gpt-4o-mini",
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{img_b64}" if img_b64 else ""}
                        }
                    ] if img_b64 else prompt
                }],
                "max_tokens": 1000
            }

            try:
                response = requests.post(API_URL, json=payload, headers=headers)
                result = response.json()
                
                if response.status_code == 200:
                    answer = result['choices'][0]['message']['content']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error(f"Errore: {result.get('error', {}).get('message')}")
            except Exception as e:
                st.error(f"Connessione fallita: {e}")
