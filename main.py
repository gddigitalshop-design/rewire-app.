import streamlit as st
import pandas as pd
import groq
import PyPDF2
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="REWIRE AI - Factory", layout="wide")

# --- FUNZIONI DATABASE ---
def get_user_db():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read(ttl=0)
    except Exception as e:
        st.error(f"Errore database: {e}")
        return pd.DataFrame(columns=['username', 'password'])

# --- GESTIONE LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("🧠 REWIRE AI - Accesso")
    tab1, tab2 = st.tabs(["Login", "Registrati"])
    with tab1:
        u = st.text_input("Username", key="l_user")
        p = st.text_input("Password", type="password", key="l_pass")
        if st.button("Entra"):
            db = get_user_db()
            # Pulizia per evitare errori di spazi
            db['username'] = db['username'].astype(str).str.strip()
            db['password'] = db['password'].astype(str).str.strip()
            
            user_row = db[db['username'] == u.strip()]
            if not user_row.empty and str(user_row['password'].values[0]) == p.strip():
                st.session_state["logged_in"] = True
                st.session_state["user_active"] = u
                st.rerun()
            else:
                st.error("Credenziali errate")
    with tab2:
        st.info("Contatta l'amministratore per un nuovo account.")
    st.stop()

# --- 2. SE SEI QUI, SEI LOGGATO: CARICAMENTO INTERFACCIA ---

# CSS ESTETICO
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #ff4b4b33; }
    div.stButton > button { border-radius: 5px; height: 3em; width: 100%; transition: all 0.3s; }
    div.stButton > button:hover { border-color: #ff4b4b; color: #ff4b4b; }
    </style>
""", unsafe_allow_html=True)

# INIZIALIZZAZIONE MESSAGGI
if "messages" not in st.session_state:
    st.session_state.messages = []

# SIDEBAR
with st.sidebar:
    st.markdown(f"### 👤 UTENTE: {st.session_state.user_active.upper()}")
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()
    st.markdown("---")
    st.markdown("### 🛠️ STRUMENTI")
    uploaded_file = st.file_uploader("📁 CARICA DOCUMENTO", type=["pdf"])
    
    st.markdown("---")
    if st.button("🗑️ RESET CHAT"):
        st.session_state.messages = []
        st.rerun()

# AREA CENTRALE
if not st.session_state.messages:
    st.markdown("""
        <div style="text-align: center; margin-top: 100px;">
            <h1 style="color: #ff4b4b; font-size: 4rem;">🧠 REWIRE AI</h1>
            <p style="font-size: 1.2rem; letter-spacing: 5px;">FACTORY EDITION - PRONTA</p>
        </div>
    """, unsafe_allow_html=True)

# VISUALIZZAZIONE CHAT
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# LOGICA CHAT
user_query = st.chat_input("Invia un comando al cervello AI...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)
    
    with st.chat_message("assistant"):
        with st.spinner("Elaborazione..."):
            try:
                client = groq.Client(api_key=st.secrets["GROQ_API_KEY"])
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                )
                risposta = response.choices[0].message.content
                st.markdown(risposta)
                st.session_state.messages.append({"role": "assistant", "content": risposta})
            except Exception as e:
                st.error(f"Errore AI: {e}")
