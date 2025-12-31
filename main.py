import streamlit as st
import requests
import fitz
from PIL import Image
import io

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE Business AI", layout="wide", page_icon="🧠")

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Inserisci Password", type="password")
    if st.button("SBLOCCA SISTEMA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- INIZIALIZZAZIONE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""
if "file_processed" not in st.session_state: st.session_state.file_processed = False

# --- INTERFACCIA ---
st.title("🧠 RE-WIRE Intelligence")

with st.sidebar:
    st.header("📁 Caricamento Documento")
    file = st.file_uploader("Trascina PDF o Foto", type=["pdf", "jpg", "jpeg", "png"])
    
    if file:
        if file.type in ["image/jpeg", "image/png"]:
            st.image(file, caption="Anteprima Foto", use_container_width=True)
            
        if not st.session_state.file_processed:
            with st.spinner("Lettura file in corso..."):
                if file.type == "application/pdf":
                    doc = fitz.open(stream=file.read(), filetype="pdf")
                    st.session_state.doc_text = "".join([page.get_text() for page in doc])[:4000]
                else:
                    # OCR PROVVISORIO: Informa l'AI del file
                    st.session_state.doc_text = f"[Immagine caricata: {file.name}]"
                
                # Analisi automatica iniziale
                st.session_state.file_processed = True
                st.rerun()

    st.divider()
    if st.button("🗑️ Carica Nuovo File"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.file_processed = False
        st.rerun()

# --- AREA SALVATAGGIO (Sempre visibile se c'è attività) ---
if st.session_state.messages:
    st.subheader("📥 Esportazione Lavoro")
    report_completo = "REPORT RE-WIRE\n" + "="*20 + "\n\n"
    for m in st.session_state.messages:
        report_completo += f"{m['role'].upper()}: {m['content']}\n\n"
    
    st.download_button(
        label="💾 SCARICA TUTTO IL LAVORO (.txt)",
        data=report_completo,
        file_name="Analisi_Business_REWIRE.txt",
        mime="text/plain",
        key="save_final"
    )
    st.divider()

# --- CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Fai una domanda sul file..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": f"Agisci come analista business. Dati documento: {st.session_state.doc_text}"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }
        res = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
        ans = res.json()['choices'][0]['message']['content']
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
