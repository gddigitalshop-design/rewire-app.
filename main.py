import streamlit as st
import pandas as pd
import groq
import PyPDF2
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="REWIRE AI - Factory", layout="wide", page_icon="🧠")

# --- CSS: IL TUO DESIGN ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #ff4b4b33; }
    .main-logo { text-align: center; padding: 30px; }
    .main-logo h1 { color: #ff4b4b; font-size: 3.5rem; margin-bottom: 0; }
    div.stButton > button { border-radius: 5px; height: 3em; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- FUNZIONI CORE ---
def get_user_db():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(ttl=0)
    except:
        return pd.DataFrame(columns=['username', 'password'])

def extract_pdf_text(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# --- LOGICA ACCESSO ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.markdown('<div class="main-logo"><h1>🧠 REWIRE AI</h1><p>FACTORY ACCESS</p></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("ENTRA"):
            db = get_user_db()
            if u in db['username'].values and str(db[db['username']==u]['password'].values[0]) == p:
                st.session_state["logged_in"] = True
                st.session_state["user_active"] = u
                st.rerun()
            else:
                st.error("Credenziali errate")
    st.stop()

# --- INTERFACCIA DOPO LOGIN ---

# Inizializzazione variabili di stato
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_context" not in st.session_state:
    st.session_state.pdf_context = ""

# SIDEBAR (Pulsanti e Caricamento)
with st.sidebar:
    st.markdown("<h2 style='color: #ff4b4b;'>FACTORY MENU</h2>", unsafe_allow_html=True)
    st.write(f"👤: {st.session_state.user_active.upper()}")
    
    st.markdown("---")
    # CARICAMENTO FILE (Ripristinato)
    uploaded_file = st.file_uploader("📁 CARICA DOCUMENTO PDF", type=["pdf"])
    if uploaded_file:
        with st.spinner("Analisi documento..."):
            st.session_state.pdf_context = extract_pdf_text(uploaded_file)
            st.success("Documento pronto per l'analisi!")

    st.markdown("---")
    # PULSANTI (Ora funzionanti come azioni)
    if st.button("📊 ANALISI DATI"):
        st.session_state.messages.append({"role": "user", "content": "Esegui un'analisi dei dati correnti."})
    
    if st.button("🗑️ CANCELLA CHAT"):
        st.session_state.messages = []
        st.rerun()

    if st.button("🔴 LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

# AREA CHAT CENTRALE
if not st.session_state.messages:
    st.markdown('<div class="main-logo"><h1>🧠 REWIRE AI</h1><p>FACTORY EDITION</p></div>', unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Chiedi all'AI o carica un PDF..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            client = groq.Client(api_key=st.secrets["GROQ_API_KEY"])
            
            # Uniamo il testo del PDF alla domanda se presente
            full_prompt = prompt
            if st.session_state.pdf_context:
                full_prompt = f"Contesto del documento: {st.session_state.pdf_context}\n\nDomanda: {prompt}"

            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": full_prompt}]
            )
            risposta = resp.choices[0].message.content
            st.markdown(risposta)
            st.session_state.messages.append({"role": "assistant", "content": risposta})
        except Exception as e:
            st.error("Errore AI. Controlla la tua GROQ_API_KEY nei Secrets.")
