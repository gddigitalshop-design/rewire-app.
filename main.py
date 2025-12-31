import streamlit as st
import requests
import base64
from PIL import Image
import io
import json
import os

# ========================================================
#                 CONFIGURAZIONE
# ========================================================
API_KEY = st.secrets.get("GROQ_API_KEY")
if not API_KEY:
    st.error("❌ Devi inserire la tua GROQ_API_KEY in .streamlit/secrets.toml")
    st.stop()

URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.2-11b-vision-preview"   # MODELLO CORRETTO

st.set_page_config(page_title="RE-WIRE AI", layout="wide")


# ========================================================
#               FUNZIONE PREPARA IMMAGINE
# ========================================================
def prepare_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((900, 900))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# ========================================================
#               SESSIONE
# ========================================================
if "chat" not in st.session_state:
    st.session_state.chat = []

if "img" not in st.session_state:
    st.session_state.img = None




# ========================================================
#               SIDEBAR
# ========================================================
with st.sidebar:
    file = st.file_uploader("Carica immagine", type=["jpg", "jpeg", "png"])
    if file:
        st.session_state.img = prepare_image(file)
        st.image(file, caption="Immagine caricata", use_column_width=True)




# ========================================================
#                  CHAT ESISTENTE
# ========================================================
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])




# ========================================================
#                 NUOVO MESSAGGIO
# ========================================================
prompt = st.chat_input("Scrivi qui...")

if prompt:
    st.session_state.chat.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        try:

            # BLOCCO MESSAGGIO
            content_block = [{"type": "text", "text": prompt}]

            # SE C'È UN'IMMAGINE, LA AGGIUNGO NEL FORMATO CORRETTO
            if st.session_state.img:
                content_block.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{st.session_state.img}"
                        }
                    }
                )

            payload = {
                "model": MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": content_block
                    }
                ],
                "temperature": 0.4
            }

            # CHIAMATA
            r = requests.post(
                URL,
                headers={"Authorization": f"Bearer {API_KEY}"},
                json=payload
            )

            # ERRORE API?
            if r.status_code != 200:
                st.error(f"❌ Errore modello: {r.status_code}")
                st.write(r.text)
                st.stop()

            # RISPOSTA
            ans = r.json()["choices"][0]["message"]["content"]
            st.write(ans)

            st.session_state.chat.append(
                {"role": "assistant", "content": ans}
            )

        except Exception as e:
            st.error(f"Errore: {e}")

    st.rerun()
