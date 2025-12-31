import streamlit as st
import requests
import base64
from PIL import Image
import io

# --- CONFIGURAZIONE RE-WIRE ---
API_KEY = "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"
MODEL_ID = "llama-3.2-11b-vision-instant" # MODELLO ATTIVO
URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI PRO", layout="wide")

# --- 1. LOGIN (Per vendere l'app) ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center;'>⚡ RE-WIRE ACCESS</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        pwd = st.text_input("Inserisci Chiave", type="password")
        if st.button("ACCEDI"):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Chiave Errata")
    st.stop()

# --- 2. FUNZIONI TECNICHE ---
def prepare_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((800, 800))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 3. MEMORIA SESSIONE ---
if "chat" not in st.session_state:
    st.session_state.chat = []
if "img" not in st.session_state:
    st.session_state.img = None

# --- 4. INTERFACCIA ---
with st.sidebar:
    st.title("⚡ DASHBOARD")
    file = st.file_uploader("Carica Immagine", type=["jpg", "png", "jpeg"])
    if file:
        st.session_state.img = prepare_image(file)
        st.image(file, caption="Immagine Pronta")
    
    if st.button("🗑️ RESET"):
        st.session_state.chat = []
        st.session_state.img = None
        st.rerun()

# --- 5. CHAT ---
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Scrivi qui..."):
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        payload = {
            "model": MODEL_ID,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Agisci come RE-WIRE AI. Analizza l'immagine se presente e rispondi a: {prompt}"}
                ]
            }],
            "temperature": 0.5
        }
        
        if st.session_state.img:
            payload["messages"][0]["content"].append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.img}"}
            })

        try:
            r = requests.post(URL, headers={"Authorization": f"Bearer {API_KEY}"}, json=payload)
            res = r.json()
            if r.status_code == 200:
                answer = res['choices'][0]['message']['content']
                st.markdown(answer)
                st.session_state.chat.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Errore: {res.get('error', {}).get('message', 'Errore API')}")
        except Exception as e:
            st.error(f"Sistema offline: {e}")
