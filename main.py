import streamlit as st
import pandas as pd
import groq
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="REWIRE AI - Factory", layout="wide", page_icon="🧠")

# --- STILE CSS PERSONALIZZATO (Il tuo design) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #ff4b4b33; }
    .main-logo { text-align: center; padding: 50px; }
    .main-logo h1 { color: #ff4b4b; font-size: 4rem; letter-spacing: 2px; margin-bottom: 0; }
    .main-logo p { font-size: 1.2rem; letter-spacing: 8px; color: #888; }
    div.stButton > button { border-radius: 5px; height: 3em; width: 100%; transition: all 0.3s; }
    div.stButton > button:hover { border-color: #ff4b4b; color: #ff4b4b; background-color: #ff4b4b1a; }
    </style>
""", unsafe_allow_html=True)

# --- FUNZIONI DATABASE ---
def get_user_db():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0)
        df.columns = df.columns.str.strip().str.lower() # Normalizza colonne
        return df
    except Exception as e:
        return pd.DataFrame(columns=['username', 'password'])

# --- GESTIONE SESSIONE ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- LOGICA DI ACCESSO ---
if not st.session_state["logged_in"]:
    st.markdown('<div class="main-logo"><h1>🧠 REWIRE AI</h1><p>FACTORY ACCESS</p></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container(border=True):
            u = st.text_input("Username").strip()
            p = st.text_input("Password", type="password").strip()
            if st.button("ENTRA NEL SISTEMA"):
                db = get_user_db()
                user_match = db[db['username'].astype(str).str.lower() == u.lower()]
                if not user_match.empty and str(user_match['password'].values[0]) == p:
                    st.session_state["logged_in"] = True
                    st.session_state["user_active"] = u
                    st.rerun()
                else:
                    st.error("Credenziali non valide")
    st.stop()

# --- 2. INTERFACCIA APP DOPO LOGIN (Tutto quello che mancava) ---

# SIDEBAR CON LOGO E PULSANTI
with st.sidebar:
    st.markdown("<h2 style='color: #ff4b4b;'>FACTORY MENU</h2>", unsafe_allow_html=True)
    st.write(f"👤 Operatore: **{st.session_state['user_active'].upper()}**")
    st.markdown("---")
    
    # Pulsanti che avevamo messo
    st.button("📁 ARCHIVIO PROGETTI")
    st.button("📊 ANALISI DATI")
    st.button("⚙️ IMPOSTAZIONI")
    
    st.markdown("---")
    if st.button("🔴 LOGOUT"):
        st.session_state["logged_in"] = False
        st.rerun()

# LOGO CENTRALE (Scompare quando inizia la chat)
if "messages" not in st.session_state or not st.session_state.messages:
    st.markdown('<div class="main-logo"><h1>🧠 REWIRE AI</h1><p>FACTORY EDITION</p></div>', unsafe_allow_html=True)
else:
    st.markdown("<h3 style='color: #ff4b4b;'>REWIRE AI Chat</h3>", unsafe_allow_html=True)

# GESTIONE CHAT
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Inserisci comando..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            client = groq.Client(api_key=st.secrets["GROQ_API_KEY"])
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            risposta = resp.choices[0].message.content
            st.markdown(risposta)
            st.session_state.messages.append({"role": "assistant", "content": risposta})
        except Exception as e:
            st.error("Errore di connessione al cervello AI.")
