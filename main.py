import streamlit as st
from groq import Groq
import base64
from PIL import Image

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business Vision", layout="wide")

# --- 2. LOGIN (Password: rewire2026) ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Accesso RE-WIRE")
    pwd = st.text_input("Inserisci Password Licenza", type="password")
    if st.button("ENTRA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. CONFIGURAZIONE CHIAVE (Semplificata) ---
# Incolla qui la tua chiave tra le virgolette
CHIAVE_MIA = "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"
client = Groq(api_key=CHIAVE_MIA)

# --- 4. FUNZIONAMENTO APP ---
st.title("🧠 RE-WIRE Business Brain")

with st.sidebar:
    st.header("⚙️ Pannello")
    file = st.file_uploader("Carica Immagine", type=["jpg", "png", "jpeg"])
    if st.button("Esci"):
        st.session_state.auth = False
        st.rerun()

if file:
    st.image(file, width=400)
    domanda = st.text_input("Cosa vuoi sapere?", "Descrivi per un bambino")
    
    if st.button("🚀 ANALIZZA ORA"):
        try:
            # Codifica immagine
            base64_image = base64.b64encode(file.getvalue()).decode('utf-8')

            # Chiamata all'AI
            chat_completion = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": domanda},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }]
            )
            st.success(chat_completion.choices[0].message.content)
        except Exception as e:
            st.error(f"Errore: {e}")
