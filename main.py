import streamlit as st
import pandas as pd
import groq
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAZIONE PAGINA (Deve essere la prima istruzione)
st.set_page_config(page_title="REWIRE AI - Factory", layout="wide", page_icon="🧠")

# --- FUNZIONI DATABASE ---
def get_user_db():
    try:
        # ttl=0 assicura che l'app legga i dati nuovi ogni volta che fai il login
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0)
        # Pulizia dati: rimuoviamo spazi bianchi e convertiamo in stringhe
        df['username'] = df['username'].astype(str).str.strip()
        df['password'] = df['password'].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"Errore di connessione al database: {e}")
        return pd.DataFrame(columns=['username', 'password'])

# --- GESTIONE SESSIONE LOGIN ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_active"] = ""

# --- SCHERMATA DI LOGIN ---
if not st.session_state["logged_in"]:
    st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: #ff4b4b;">🧠 REWIRE AI</h1>
            <p>Accedi al Sistema Operativo Factory</p>
        </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Richiedi Accesso"])
    
    with tab1:
        u_input = st.text_input("Username").strip()
        p_input = st.text_input("Password", type="password").strip()
        
        if st.button("ENTRA"):
            if u_input and p_input:
                db = get_user_db()
                # Cerchiamo l'utente (senza distinguere tra maiuscole e minuscole per l'username)
                user_match = db[db['username'].str.lower() == u_input.lower()]
                
                if not user_match.empty:
                    stored_password = str(user_match['password'].values[0])
                    if stored_password == p_input:
                        st.session_state["logged_in"] = True
                        st.session_state["user_active"] = u_input
                        st.rerun()
                    else:
                        st.error("Password errata.")
                else:
                    st.error("Utente non trovato.")
            else:
                st.warning("Inserisci tutte le credenziali.")

    with tab2:
        st.info("Per affittare l'app o creare un account, contatta l'amministratore.")
        st.write("Email: support@rewire-ai.it") # Cambia con la tua email
    
    st.stop() # Blocca l'esecuzione qui se non sei loggato

# --- 2. INTERFACCIA APP (Visible solo dopo il Login) ---

# Sidebar professionale
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=100) # Logo esempio
    st.markdown(f"### 👤 Utente: **{st.session_state['user_active'].upper()}**")
    st.markdown("---")
    if st.button("LOGOUT"):
        st.session_state["logged_in"] = False
        st.rerun()

# Layout principale
st.title("🚀 REWIRE AI - Factory Control")
st.write(f"Benvenuto, {st.session_state['user_active']}. Il sistema è pronto.")

# Inizializzazione Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra i messaggi precedenti
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input Chat
if prompt := st.chat_input("Chiedi qualcosa all'AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            client = groq.Client(api_key=st.secrets["GROQ_API_KEY"])
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
            )
            response = completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Errore Groq: {e}")
