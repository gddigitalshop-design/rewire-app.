import streamlit as st
import requests
import base64
from PIL import Image
import io

# ---------------------
# 1. CONFIGURAZIONE E STILE (UI PREMIUM)
# ---------------------
st.set_page_config(page_title="REWIRE AI - Pro", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    /* Sfondo e font */
    .stApp { background-color: #f8f9fc; }
    
    /* Sidebar stilizzata */
    [data-testid="stSidebar"] { background-color: #1e1e2f; color: white; }
    
    /* Messaggi Chat */
    .user-msg { 
        background-color: #6c63ff; color: white; padding: 15px; 
        border-radius: 15px 15px 0px 15px; margin: 10px 0; text-align: right;
    }
    .ai-msg { 
        background-color: white; color: #333; padding: 15px; 
        border-radius: 15px 15px 15px 0px; margin: 10px 0;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    
    /* Bottoni e input */
    .stButton>button {
        width: 100%; border-radius: 8px; background-color: #6c63ff; color: white;
        border: none; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { background-color: #554ed1; transform: translateY(-2px); }
</style>
""", unsafe_allow_html=True)

# ---------------------
# 2. INIZIALIZZAZIONE
# ---------------------
if "auth" not in st.session_state: st.session_state.auth = False
if "messages" not in st.session_state: st.session_state.messages = []

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# ---------------------
# 3. LOGICA DI LOGIN (Full Screen)
# ---------------------
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.markdown("<h1 style='text-align: center;'>⚡ REWIRE AI</h1>", unsafe_allow_html=True)
        with st.container():
            st.info("Inserisci le credenziali fornite per accedere alla licenza.")
            pwd = st.text_input("Password Licenza", type="password")
            if st.button("SBLOCCA SOFTWARE"):
                if pwd == "rewire2026":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Accesso negato.")
    st.stop()

# ---------------------
# 4. SIDEBAR (Template e File)
# ---------------------
with st.sidebar:
    st.title("⚙️ Pannello Controllo")
    
    st.subheader("📁 Carica Documenti/Immagini")
    uploaded_file = st.file_uploader("Analizza file dal PC", type=['png', 'jpg', 'jpeg', 'pdf', 'txt'])
    
    st.markdown("---")
    st.subheader("📝 Template Pronti")
    template = st.selectbox("Scegli un'azione rapida:", [
        "Nessuno",
        "Analisi Tecnica Immagine",
        "Riassunto Documento",
        "Generazione Codice",
        "Correzione Testo"
    ])
    
    if st.button("Svuota Chat"):
        st.session_state.messages = []
        st.rerun()
        
    if st.button("🔴 Logout"):
        st.session_state.auth = False
        st.rerun()

# ---------------------
# 5. AREA CHAT (Stile Moderno)
# ---------------------
st.title("🚀 REWIRE Intelligent Assistant")

# Visualizzazione messaggi salvati
for msg in st.session_state.messages:
    div_class = "user-msg" if msg["role"] == "user" else "ai-msg"
    st.markdown(f'<div class="{div_class}">{msg["content"]}</div>', unsafe_allow_html=True)

# Barra di input fissa in basso
prompt = st.chat_input("Chiedi qualcosa o descrivi il file caricato...")

if prompt:
    # Aggiungi messaggio utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(f'<div class="user-msg">{prompt}</div>', unsafe_allow_html=True)

    # Logica API Groq
    with st.spinner("Rewire sta elaborando..."):
        try:
            # Qui andrebbe la chiamata API reale a Groq
            # Esempio semplificato di risposta
            response_text = "Questa è una risposta simulata. Collega la funzione Groq qui."
            
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            st.markdown(f'<div class="ai-msg">{response_text}</div>', unsafe_allow_html=True)
            st.rerun()
        except Exception as e:
            st.error(f"Errore API: {e}")

# ---------------------
# 6. FUNZIONE SALVATAGGIO
# ---------------------
if st.session_state.messages:
    chat_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    st.download_button("💾 Salva Conversazione (TXT)", chat_text, file_name="chat_rewire.txt")
