import streamlit as st
import requests
import base64
from PIL import Image
import io
import json
import os

# -------------------------------------------------------
#                 CONFIGURAZIONE
# -------------------------------------------------------
API_KEY = "INSERISCI_LA_TUA_API_KEY"
URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.2-11b-vision-preview"

st.set_page_config(page_title="RE-WIRE AI", layout="wide")


# -------------------------------------------------------
#         FUNZIONE PER PREPARARE L’IMMAGINE
# -------------------------------------------------------
def prepare_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((900, 900))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


# -------------------------------------------------------
#               INIZIALIZZAZIONE SESSIONE
# -------------------------------------------------------
if "chat" not in st.session_state:
    st.session_state.chat = []

if "img" not in st.session_state:
    st.session_state.img = None

if "project_name" not in st.session_state:
    st.session_state.project_name = ""


# -------------------------------------------------------
#                   TESTATA GRAFICA
# -------------------------------------------------------
st.markdown(
    "<h1 style='text-align:center; color:#6A5ACD;'>⚡ RE-WIRE AI</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center; font-size:18px; color:#666;'>La tua AI che descrive immagini, crea piani, organizza la vita e risolve problemi.</p>",
    unsafe_allow_html=True
)

st.write("---")


# -------------------------------------------------------
#                     SIDEBAR
# -------------------------------------------------------
with st.sidebar:

    st.header("📁 Gestione Progetto")

    st.session_state.project_name = st.text_input("Nome progetto", value=st.session_state.project_name)

    if st.button("💾 Salva progetto"):
        if st.session_state.project_name.strip() != "":
            data = {
                "chat": st.session_state.chat,
                "img": st.session_state.img
            }
            with open(f"{st.session_state.project_name}.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            st.success("Progetto salvato!")

    if st.button("📂 Carica progetto"):
        filename = f"{st.session_state.project_name}.json"
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state.chat = data.get("chat", [])
                st.session_state.img = data.get("img", None)
            st.success("Progetto caricato!")
            st.experimental_rerun()
        else:
            st.error("Progetto non trovato.")

    st.write("---")

    st.header("🖼 Analisi Immagine")
    file = st.file_uploader("Carica immagine", type=["jpg", "jpeg", "png"])
    if file:
        st.session_state.img = prepare_image(file)
        st.image(file, caption="Immagine caricata", use_column_width=True)

    st.write("---")

    if st.button("🔄 Reset Chat"):
        st.session_state.chat = []
        st.session_state.img = None
        st.experimental_rerun()


# -------------------------------------------------------
#                TEMPLATES RAPIDI
# -------------------------------------------------------
st.subheader("📌 Template veloci")

c1, c2, c3, c4, c5 = st.columns(5)

if c1.button("👪 Famiglia"):
    st.session_state.chat.append({"role": "user", "content": "Fammi un piano settimanale per la famiglia."})
    st.experimental_rerun()

if c2.button("💼 Lavoro"):
    st.session_state.chat.append({"role": "user", "content": "Organizza il mio lavoro giornaliero."})
    st.experimental_rerun()

if c3.button("🎨 Hobby"):
    st.session_state.chat.append({"role": "user", "content": "Suggerisci un nuovo hobby creativo."})
    st.experimental_rerun()

if c4.button("🥗 Dieta"):
    st.session_state.chat.append({"role": "user", "content": "Crea un piano alimentare settimanale."})
    st.experimental_rerun()

if c5.button("❓ Problemi"):
    st.session_state.chat.append({"role": "user", "content": "Aiutami a risolvere un problema quotidiano."})
    st.experimental_rerun()


st.write("---")


# -------------------------------------------------------
#                  CHAT ESISTENTE
# -------------------------------------------------------
for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# -------------------------------------------------------
#                 NUOVO MESSAGGIO
# -------------------------------------------------------
prompt = st.chat_input("Scrivi qui il tuo messaggio...")

if prompt:

    st.session_state.chat.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        try:
            content_block = [{"type": "text", "text": prompt}]

            if st.session_state.img:
                content_block.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{st.session_state.img}"
                    }
                })

            payload = {
                "model": MODEL,
                "messages": [{
                    "role": "user",
                    "content": content_block
                }],
                "temperature": 0.4
            }

            response = requests.post(
                URL,
                headers={"Authorization": f"Bearer {API_KEY}"},
                json=payload,
                timeout=20
            )

            if response.status_code != 200:
                st.error(f"Errore modello: {response.status_code}")
            else:
                ans = response.json()["choices"][0]["message"]["content"]
                st.write(ans)
                st.session_state.chat.append({"role": "assistant", "content": ans})

        except Exception as e:
            st.error(f"Errore: {e}")

    st.experimental_rerun()
