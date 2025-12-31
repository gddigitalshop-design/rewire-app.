import streamlit as st
import requests
import base64

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.2-11b-vision-preview" # MODELLO CON OCCHI REALI
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI PRO", layout="wide")

# --- FUNZIONI TECNICHE ---
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# --- INTERFACCIA ---
with st.sidebar:
    st.markdown("# ⚡ DASHBOARD")
    uploaded_file = st.file_uploader("Carica immagine", type=["jpg", "png", "jpeg"], label_visibility="collapsed")
    mode = st.radio("Ambiente", ["🏠 Famiglia", "💼 Business", "🔬 Specialista"])
    if st.button("🗑️ RESET"):
        st.session_state.clear()
        st.rerun()

if uploaded_file:
    file_bytes = uploaded_file.read()
    base64_image = encode_image(file_bytes)
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(file_bytes, caption="Immagine Caricata")
    with col2:
        st.info(f"Modalità {mode} attiva. Analisi visiva in corso...")

# --- LOGICA CHAT ---
if "messages" not in st.session_state: st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Cosa vedi in questa immagine?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    if uploaded_file:
        payload = {
            "model": MODEL_ID,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Analizza questa immagine come esperto in modalità {mode}. Ignora il nome del file. Descrivi esattamente i soggetti (robot, teschi, persone, ecc.)."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}},
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
        }
        
        try:
            response = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
            res = response.json()
            if 'choices' in res:
                ans = res['choices'][0]['message']['content']
                with st.chat_message("assistant"):
                    st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            else:
                st.error("Errore API: Il modello Vision potrebbe essere temporaneamente non disponibile.")
        except Exception as e:
            st.error(f"Errore di sistema: {e}")
