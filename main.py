import streamlit as st
import requests
import fitz  # PyMuPDF
from PIL import Image
import io

# --- 1. CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE Business Chat", layout="wide")

# --- 2. LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. INIZIALIZZAZIONE MEMORIA CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [] # Qui salviamo la cronologia
if "doc_text" not in st.session_state:
    st.session_state.doc_text = "" # Qui salviamo il testo del documento

# --- 4. FUNZIONE ESTRAZIONE ---
def get_content(uploaded_file):
    if uploaded_file.type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        return "".join([page.get_text() for page in doc])[:8000] # Limite prudenziale
    else:
        return "[Immagine/File non testuale]"

# --- 5. INTERFACCIA ---
st.title("🧠 RE-WIRE Interactive Intelligence")

with st.sidebar:
    st.header("📁 Carica Documento")
    file = st.file_uploader("PDF o Immagine", type=["pdf", "jpg", "png", "jpeg"])
    if file:
        st.session_state.doc_text = get_content(file)
        st.success("Documento caricato e letto!")
    
    if st.button("🗑️ Svuota Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 6. LOGICA CHAT ---
# Visualizza i messaggi precedenti
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input dell'utente
if prompt := st.chat_input("Chiedi all'AI sul documento..."):
    # Aggiungi messaggio utente alla memoria
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Risposta dell'Assistant
    with st.chat_message("assistant"):
        with st.spinner("Sto pensando..."):
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Prepariamo il contesto: Documento + Cronologia
            context = f"CONTESTO DOCUMENTO: {st.session_state.doc_text}\n\n"
            messages_payload = [{"role": "system", "content": "Sei un assistente business esperto. Rispondi basandoti sul documento fornito."}]
            
            # Aggiungiamo la storia della chat (ultimi 5 messaggi per non superare i limiti)
            for m in st.session_state.messages[-5:]:
                messages_payload.append(m)

            # Inseriamo il contesto nel primo messaggio se c'è un documento
            if st.session_state.doc_text:
                messages_payload[1]["content"] = context + messages_payload[1]["content"]

            payload = {
                "model": MODEL_ID,
                "messages": messages_payload,
                "temperature": 0.5
            }

            try:
                response = requests.post(API_URL, json=payload, headers=headers)
                if response.status_code == 200:
                    full_response = response.json()['choices'][0]['message']['content']
                    st.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                else:
                    st.error(f"Errore API: {response.status_code}")
            except Exception as e:
                st.error(f"Errore: {e}")
