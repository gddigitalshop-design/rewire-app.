import streamlit as st
import requests
import fitz  # PyMuPDF

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

# --- FUNZIONE LETTURA PDF (OTTIMIZZATA) ---
def get_content(uploaded_file):
    try:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        # Estraiamo solo i primi 5000 caratteri (circa 1200 token) per stare larghi nel limite
        return "".join([page.get_text() for page in doc])[:5000]
    except Exception as e:
        return f"Errore lettura: {e}"

# --- INTERFACCIA ---
st.title("🧠 RE-WIRE Business Intelligence")

with st.sidebar:
    st.header("📁 Documento")
    file = st.file_uploader("Carica PDF", type=["pdf"])
    if file:
        st.session_state.doc_text = get_content(file)
        st.success("Documento pronto.")
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
        with st.spinner("Analisi..."):
            # Costruiamo il payload con gestione errori avanzata
            messages_payload = [
                {"role": "system", "content": f"Sei un assistente business. Usa queste info: {st.session_state.doc_text}"},
            ]
            # Aggiungiamo solo gli ultimi 4 messaggi per risparmiare spazio
            for m in st.session_state.messages[-4:]:
                messages_payload.append(m)

            try:
                response = requests.post(
                    API_URL, 
                    json={"model": MODEL_ID, "messages": messages_payload, "temperature": 0.2},
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                    timeout=10 # Evita che l'app resti appesa
                )
                
                if response.status_code == 200:
                    answer = response.json()['choices'][0]['message']['content']
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                else:
                    # QUI LEGGERAI IL VERO ERRORE
                    st.error(f"Errore API {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Errore di rete: {e}")
