import streamlit as st
import requests
import base64
from PIL import Image
import io

# ============================================
#               CONFIG SICURA
# ============================================
# Inserisci la chiave in .streamlit/secrets.toml
API_KEY = st.secrets.get("GROQ_API_KEY", None)

if not API_KEY:
    st.error("❌ API Key mancante in st.secrets! Aggiungila prima di procedere.")
    st.stop()

MODELS_TO_TRY = [
    "llama-3.2-11b-vision-preview",
    "llama-3.2-90b-vision-instant",
    "llama-3.2-11b-vision-instant"
]

URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI PRO", layout="wide")

# ============================================
#                 LOGIN
# ============================================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>⚡ RE-WIRE ACCESS</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        pwd = st.text_input("Password", type="password")
        if st.button("ACCEDI"):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Accesso negato")
    st.stop()

# ============================================
#              IMAGE HANDLING
# ============================================
def prepare_image(uploaded_file):
    try:
        img = Image.open(uploaded_file).convert("RGB")
        img.thumbnail((768, 768))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=88)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        st.error(f"Errore nel processare l'immagine: {e}")
        return None

# ============================================
#              MEMORIA SESSIONE
# ============================================
if "chat" not in st.session_state:
    st.session_state.chat = []
if "img" not in st.session_state:
    st.session_state.img = None

# ============================================
#                    SIDEBAR
# ============================================
with st.sidebar:
    st.title("⚡ DASHBOARD")

    file = st.file_uploader("Carica Immagine", type=["jpg", "jpeg", "png"])
    if file:
        st.session_state.img = prepare_image(file)
        st.image(file, caption="Visione Attiva")

    if st.button("RESET"):
        st.session_state.chat.clear()
        st.session_state.img = None
        st.rerun()

# ============================================
#                   CHAT UI
# ============================================
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ============================================
#                   PROCESSO CHAT
# ============================================
if prompt := st.chat_input("Chiedi qualcosa..."):
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        success = False

        for model in MODELS_TO_TRY:
            payload = {
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Agisci come RE-WIRE AI. Descrivi fedelmente robot/bambini/teschi. Domanda: {prompt}"}
                    ]
                }],
                "temperature": 0.5
            }

            # Inserimento immagine se esiste
            if st.session_state.img:
                payload["messages"][0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.img}"}
                })

            try:
                r = requests.post(
                    URL,
                    headers={"Authorization": f"Bearer {API_KEY}"},
                    json=payload,
                    timeout=20
                )

                if r.status_code == 200:
                    ans = r.json()["choices"][0]["message"]["content"]
                    st.markdown(ans)
                    st.session_state.chat.append({"role": "assistant", "content": ans})
                    success = True
                    break

                else:
                    st.write(f"⚠️ Modello {model} ha risposto con errore: {r.status_code}")

            except requests.exceptions.Timeout:
                st.write(f"⏳ Timeout per modello {model}, passo al prossimo...")
            except Exception as e:
                st.write(f"❌ Errore usando modello {model}: {e}")

        if not success:
            st.error("❌ Nessun modello Vision disponibile. Riprova più tardi.")
