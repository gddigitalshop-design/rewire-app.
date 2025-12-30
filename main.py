import streamlit as st
from groq import Groq
import base64

# --- CONFIGURAZIONE ---
API_KEY_GROQ = "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"
client = Groq(api_key=API_KEY_GROQ)

st.set_page_config(page_title="RE-WIRE Business Vision", layout="wide")

# --- LOGIN ---
if "loggato" not in st.session_state:
    st.session_state.loggato = False

if not st.session_state.loggato:
    st.title("🔐 Accesso RE-WIRE")
    psw = st.text_input("Inserisci Password", type="password")
    if st.button("ENTRA"):
        if psw == "rewire2026":
            st.session_state.loggato = True
            st.rerun()
        else:
            st.error("Password errata")
    st.stop()

# --- APP ---
st.title("🧠 RE-WIRE AI Vision")

with st.sidebar:
    st.header("Caricamento")
    foto = st.file_uploader("Scegli una foto", type=["jpg", "png", "jpeg"])
    if st.button("Esci"):
        st.session_state.loggato = False
        st.rerun()

if foto:
    st.image(foto, width=300)
    testo_input = st.text_input("Cosa vuoi chiedere?", "Descrivi per un bambino")
    
    if st.button("🚀 ANALIZZA"):
        try:
            base64_foto = base64.b64encode(foto.getvalue()).decode('utf-8')

            # CAMBIO MODELLO QUI: llama-3.2-11b-vision-instant
            risposta = client.chat.completions.create(
                model="llama-3.2-11b-vision-instant", 
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": testo_input},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_foto}"}}
                    ]
                }]
            )
            st.success(risposta.choices[0].message.content)
        except Exception as e:
            st.error(f"Errore: {e}")
            st.info("Se l'errore persiste, prova a usare il modello: llama-3.3-70b-versatile")
