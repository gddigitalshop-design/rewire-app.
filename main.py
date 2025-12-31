import streamlit as st
import requests
import fitz
import time

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE Business AI", layout="wide", page_icon="📄")

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Inserisci Password", type="password")
    if st.button("SBLOCCA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- INIZIALIZZAZIONE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""

# --- FUNZIONE SALVATAGGIO ---
def prepare_report():
    report = "--- REPORT ANALISI RE-WIRE ---\n\n"
    for msg in st.session_state.messages:
        role = "CLIENTE" if msg["role"] == "user" else "AI RE-WIRE"
        report += f"{role}: {msg['content']}\n\n"
    return report

# --- INTERFACCIA ---
st.title("🧠 RE-WIRE Business Intelligence")

with st.sidebar:
    st.header("📁 Gestione Documenti")
    file = st.file_uploader("Carica PDF", type=["pdf"])
    if file:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        st.session_state.doc_text = "".join([page.get_text() for page in doc])[:3000]
        st.success("Documento letto con successo.")

    st.divider()
    st.header("💾 Esportazione")
    
    if st.session_state.messages:
        # Pulsante di Download per il Report
        report_data = prepare_report()
        st.download_button(
            label="📥 SCARICA REPORT (TXT)",
            data=report_data,
            file_name="Analisi_RE-WIRE.txt",
            mime="text/plain"
        )
    else:
        st.info("Inizia una chat per generare un report scaricabile.")

    if st.button("🗑️ Reset Totale"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.rerun()

# --- CHAT ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Fai una domanda..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi..."):
            messages_payload = [{"role": "system", "content": f"Usa queste info: {st.session_state.doc_text}"}]
            for m in st.session_state.messages[-2:]:
                messages_payload.append(m)

            try:
                response = requests.post(
                    API_URL, 
                    json={"model": MODEL_ID, "messages": messages_payload, "temperature": 0.1},
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    timeout=15
                )
                if response.status_code == 200:
                    answer = response.json()['choices'][0]['message']['content']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.rerun() # Forza il refresh per attivare il pulsante download
                else:
                    st.error(f"Errore API {response.status_code}")
            except Exception as e:
                st.error(f"Errore: {e}")
