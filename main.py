import streamlit as st
import requests
import fitz
import time

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE Business Chat", layout="wide")

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- MEMORIA ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""

# --- FUNZIONE LETTURA PDF (ULTRA-LEGGERA) ---
def get_content(uploaded_file):
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        # Riduciamo drasticamente a 3000 caratteri per stare nei 6000 token di limite
        return "".join([page.get_text() for page in doc])[:3000]
    except Exception as e:
        return f"Errore: {e}"

# --- INTERFACCIA ---
st.title("🧠 RE-WIRE Business Intelligence")

with st.sidebar:
    st.header("📁 Documento")
    file = st.file_uploader("Carica PDF", type=["pdf"])
    if file:
        st.session_state.doc_text = get_content(file)
        st.success("Documento ottimizzato.")
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# Mostra Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Chat
if prompt := st.chat_input("Chiedi all'AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso (rispettando i limiti)..."):
            # Prepariamo i messaggi (solo gli ultimi 2 per risparmiare token)
            messages_payload = [
                {"role": "system", "content": f"Rispondi brevemente usando: {st.session_state.doc_text}"}
            ]
            for m in st.session_state.messages[-2:]:
                messages_payload.append(m)

            # --- LOGICA DI RETRY AUTOMATICO ---
            max_retries = 2
            for i in range(max_retries):
                try:
                    response = requests.post(
                        API_URL, 
                        json={"model": MODEL_ID, "messages": messages_payload, "temperature": 0.1},
                        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        answer = response.json()['choices'][0]['message']['content']
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        break
                    elif response.status_code == 429:
                        if i < max_retries - 1:
                            st.warning("Server occupato, riprovo tra 6 secondi...")
                            time.sleep(6.5) # Aspetta che il limite si resetti
                            continue
                        else:
                            st.error("Limite API raggiunto. Attendi 10 secondi e riprova.")
                    else:
                        st.error(f"Errore {response.status_code}")
                        break
                except Exception as e:
                    st.error(f"Errore di rete: {e}")
                    break
