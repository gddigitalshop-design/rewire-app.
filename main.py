import streamlit as st
import requests
import base64
from PIL import Image
import io

# --- 1. CONFIGURAZIONE GROQ (Bypass Google 404) ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.2-11b-vision-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI Business", layout="wide", page_icon="🧠")

# --- 2. LOGIN SICURO ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Inserisci Password Licenza", type="password")
    if st.button("SBLOCCA SISTEMA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. FUNZIONE VISIONE ---
def encode_image(uploaded_file):
    img = Image.open(uploaded_file)
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- 4. INTERFACCIA ---
st.title("🧠 RE-WIRE Business Intelligence")
st.subheader("Analisi Documenti con Llama 3.2 Vision")

file = st.file_uploader("Carica una foto del documento", type=["jpg", "png", "jpeg"])

if file:
    img_b64 = encode_image(file)
    st.image(file, width=400, caption="Documento pronto")
    
    prompt = st.text_input("Cosa vuoi sapere?", "Analizza questo documento e riassumi i dati")
    
    if st.button("ESEGUI ANALISI"):
        with st.spinner("Analisi ultra-rapida in corso..."):
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": MODEL_ID,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                }],
                "temperature": 0.1
            }

            try:
                response = requests.post(API_URL, json=payload, headers=headers)
                if response.status_code == 200:
                    answer = response.json()['choices'][0]['message']['content']
                    st.success("Analisi completata!")
                    st.markdown(f"### Risultato:\n{answer}")
                else:
                    st.error(f"Errore {response.status_code}: Controlla se il modello {MODEL_ID} è attivo nel tuo pannello Groq.")
            except Exception as e:
                st.error(f"Errore di connessione: {e}")

with st.sidebar:
    st.caption("Licenza: Business Gold")
    if st.button("Logout"):
        st.session_state.auth = False
        st.rerun()
