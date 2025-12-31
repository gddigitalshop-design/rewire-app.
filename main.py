import streamlit as st
import requests
import fitz  # PyMuPDF
from PIL import Image
import io

# --- 1. CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE Business Chat", layout="wide", page_icon="🧠")

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

# --- 3. INIZIALIZZAZIONE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""

# --- 4. FUNZIONE LETTURA PDF ---
def get_content(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            full_text = "".join([page.get_text() for page in doc])
            return full_text[:7000] # Taglio di sicurezza per i token
        else:
            return "" # Per ora le immagini passano come vuote senza OCR
    except:
        return ""

# --- 5. INTERFACCIA ---
st.title("🧠 RE-WIRE Interactive Intelligence")

with st.sidebar:
    st.header("📁 Documento Corrente")
    file = st.file_uploader("Carica PDF", type=["pdf"])
    
    if file:
        new_text = get_content(file)
        if new_text != st.session_state.doc_text:
            st.session_state.doc_text = new_text
            st.session_state.messages = [] # Reset chat se cambi documento
            st.success("Nuovo documento caricato!")

    if st.button("🗑️ Svuota Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 6. LOGICA CHAT ---
# Visualizzazione storica
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Utente
if prompt := st.chat_input("Fai una domanda sul file..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # TRUCCO: Il System Prompt contiene SEMPRE il documento
            messages_payload = [
                {
                    "role": "system", 
                    "content": f"Sei un assistente AI professionale. Il contenuto del documento su cui devi rispondere è il seguente: {st.session_state.doc_text}. Se il documento è vuoto, chiedi all'utente di caricarne uno."
                }
            ]
            
            # Aggiungiamo la cronologia (ultimi 6 messaggi)
            for m in st.session_state.messages[-6:]:
                messages_payload.append(m)

            payload = {
                "model": MODEL_ID,
                "messages": messages_payload,
                "temperature": 0.3
            }

            try:
                response = requests.post(API_URL, json=payload, headers=headers)
                if response.status_code == 200:
                    answer = response.json()['choices'][0]['message']['content']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    st.error("Errore di connessione API.")
            except Exception as e:
                st.error(f"Errore: {e}")
