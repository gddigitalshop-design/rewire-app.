import streamlit as st
import groq
from streamlit_gsheets import GSheetsConnection

# CONFIGURAZIONE
st.set_page_config(page_title="REWIRE AI - Factory", layout="wide")

# FUNZIONE DATABASE (Google Sheets)
def check_login(user, pwd):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(ttl=0)
        # Controlla se le credenziali esistono nel foglio
        for index, row in df.iterrows():
            if str(row['username']).strip() == user and str(row['password']).strip() == pwd:
                return True
        return False
    except:
        return False

# SESSIONE
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# SCHERMATA LOGIN (Quella che vedrà il tuo cliente)
if not st.session_state.logged_in:
    st.title("🧠 REWIRE AI - Factory")
    st.subheader("Accesso Riservato")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    
    if st.button("ACCEDI"):
        if check_login(u, p):
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Credenziali non valide. Contatta l'amministratore.")
    st.stop()

# --- SE SEI QUI, IL LOGIN HA FUNZIONATO ---
st.title("🚀 REWIRE AI - Operativo")
st.success(f"Benvenuto nel sistema, sessione attiva.")

# CHAT AI
if prompt := st.chat_input("Invia un comando all'AI..."):
    with st.chat_message("user"):
        st.write(prompt)
    
    with st.chat_message("assistant"):
        try:
            # Qui usiamo la chiave che hai messo nei Secrets
            client = groq.Client(api_key=st.secrets["GROQ_API_KEY"])
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )
            st.write(resp.choices[0].message.content)
        except Exception as e:
            st.error("Errore di connessione. Verifica la GROQ_API_KEY nei Secrets di Streamlit.")
