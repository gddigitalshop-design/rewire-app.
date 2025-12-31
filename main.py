import streamlit as st
import requests
import fitz
from PIL import Image
import io

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE Business AI", layout="wide", page_icon="👁️")

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

# --- INIZIALIZZAZIONE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""
if "file_processed" not in st.session_state: st.session_state.file_processed = False

# --- FUNZIONE ANALISI ---
def analyze_content(text):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": "Sei un analista. Descrivi e analizza il contenuto fornito in modo professionale."},
            {"role": "user", "content": f"Dati estratti: {text}"}
        ],
        "temperature": 0.2
    }
    try:
        response = requests.post(API_URL, json=payload, headers=headers)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Errore nell'analisi del contenuto."

# --- INTERFACCIA ---
st.title("🧠 RE-WIRE Intelligence")

with st.sidebar:
    st.header("📁 Carica Foto o PDF")
    file = st.file_uploader("Trascina qui il file", type=["pdf", "jpg", "jpeg", "png"])
    
    if file:
        # Mostra l'anteprima se è una foto
        if file.type in ["image/jpeg", "image/png"]:
            st.image(file, caption="Anteprima Caricata", use_container_width=True)
            
        if not st.session_state.file_processed:
            with st.spinner("Lettura in corso..."):
                if file.type == "application/pdf":
                    doc = fitz.open(stream=file.read(), filetype="pdf")
                    st.session_state.doc_text = "".join([page.get_text() for page in doc])[:4000]
                else:
                    # Logica per le immagini (Simulazione OCR per stabilità)
                    st.session_state.doc_text = f"L'utente ha caricato l'immagine: {file.name}. Analizza le sue domande su questo file."
                
                res = analyze_content(st.session_state.doc_text)
                st.session_state.messages.append({"role": "assistant", "content": res})
                st.session_state.file_processed = True
                st.rerun()

    if st.button("🗑️ Carica Nuovo"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.file_processed = False
        st.rerun()

# --- AREA SALVATAGGIO ---
if st.session_state.messages:
    report_data = "--- REPORT RE-WIRE ---\n\n"
    for m in st.session_state.messages:
        report_data += f"{m['role'].upper()}: {m['content']}\n\n"
    
    st.download_button(
        label="📥 SALVA TUTTO IL LAVORO",
        data=report_data,
        file_name="Analisi_REWIRE.txt",
        mime="text/plain",
        key="save_work"
    )
    st.divider()

# Visualizzazione Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Chiedi all'AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": f"Documento: {st.session_state.doc_text}"},
                {"role": "user", "content": prompt}
            ]
        }
        res = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
        answer = res.json()['choices'][0]['message']['content']
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.rerun()
