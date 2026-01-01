import streamlit as st
import groq
from streamlit_gsheets import GSheetsConnection

# 1. SETUP ESTETICO
st.set_page_config(page_title="REWIRE AI - Factory", layout="wide", page_icon="🚀")

# CSS per rendere l'app "Premium"
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0e1117 0%, #161b22 100%); color: #ffffff; }
    .stChatMessage { border-radius: 15px; border: 1px solid #ff4b4b33; margin-bottom: 10px; }
    .stButton > button { background-color: #ff4b4b; color: white; border-radius: 8px; width: 100%; border: none; }
    .stButton > button:hover { background-color: #ff3333; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- FUNZIONI CORE ---
def check_login(user, pwd):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0)
        for index, row in df.iterrows():
            if str(row['username']).strip() == user and str(row['password']).strip() == pwd:
                return True
        return False
    except: return False

# --- GESTIONE SESSIONE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SCHERMATA LOGIN ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #ff4b4b;'>🧠 REWIRE AI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Inserisci le tue credenziali per accedere alla Factory</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        with st.container(border=True):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("ACCEDI AL SISTEMA"):
                if check_login(u, p):
                    st.session_state.logged_in = True
                    st.session_state.user_active = u
                    st.rerun()
                else: st.error("Accesso negato")
    st.stop()

# --- INTERFACCIA OPERATIVA (Dopo Login) ---
with st.sidebar:
    st.markdown("<h2 style='color: #ff4b4b;'>🚀 REWIRE AI</h2>", unsafe_allow_html=True)
    st.write(f"Operatore: **{st.session_state.user_active.upper()}**")
    st.markdown("---")
    st.info("Sistema Operativo Factory v1.0 attivo.")
    if st.button("🗑️ SVUOTA CHAT"):
        st.session_state.messages = []
        st.rerun()
    if st.button("🔴 ESCI"):
        st.session_state.logged_in = False
        st.rerun()

# TITOLO CENTRALE
st.markdown(f"### ⚙️ Factory Dashboard - Sessione di {st.session_state.user_active}")

# VISUALIZZAZIONE CHAT STILE "MODERNO"
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# INPUT CHAT
if prompt := st.chat_input("Digita un comando per l'AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            client = groq.Client(api_key=st.secrets["GROQ_API_KEY"])
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            risposta = resp.choices[0].message.content
            st.markdown(risposta)
            st.session_state.messages.append({"role": "assistant", "content": risposta})
        except Exception as e:
            st.error("Connessione AI momentaneamente interrotta.")
