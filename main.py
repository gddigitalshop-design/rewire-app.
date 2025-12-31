import streamlit as st
import requests
import base64
from PIL import Image
import io

# ---------------------------------------------------------
# 1. CONFIGURAZIONE (Deve essere SEMPRE la prima istruzione)
# ---------------------------------------------------------
st.set_page_config(
    page_title="REWIRE AI",
    page_icon="⚡",
    layout="wide"
)

# 2. INIZIALIZZAZIONE STATI (Evita il NameError)
if "auth" not in st.session_state:
    st.session_state.auth = False

# Recupero della chiave dai Secrets (impostata su Streamlit Cloud)
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# ---------------------------------------------------------
# 3. INTERFACCIA DI LOGIN
# ---------------------------------------------------------
if not st.session_state.auth:
    # Centriamo il login graficamente
    _, col2, _ = st.columns([1, 2, 1])
    
    with col2:
        st.title("🔐 REWIRE AI - Accesso Clienti")
        st.markdown("---")
        with st.form("login_panel"):
            pwd = st.text_input("Inserisci la Password di attivazione:", type="password")
            submit = st.form_submit_button("SBLOCCA APPLICAZIONE")
            
            if submit:
                if pwd == "rewire2026":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Password non valida. Contattare l'amministratore.")
    
    st.stop() # Blocca il resto del codice finché non sei loggato

# ---------------------------------------------------------
# 4. DASHBOARD APPLICATIVA (Eseguita solo post-login)
# ---------------------------------------------------------
st.sidebar.success("Accesso Autorizzato")
if st.sidebar.button("Log Out"):
    st.session_state.auth = False
    st.rerun()

st.title("⚡ Dashboard Rewire AI")
st.write("L'applicazione è pronta per l'uso.")

# Qui prosegui con la tua logica Groq...
