import streamlit as st
import pandas as pd
import groq
import PyPDF2
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURAZIONE PAGINA (Deve essere SEMPRE la prima istruzione)
st.set_page_config(page_title="REWIRE AI - Factory", layout="wide")

# --- FUNZIONI DATABASE ---
def get_user_db():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        return conn.read()
    except Exception as e:
        st.error(f"Errore connessione: {e}")
        return pd.DataFrame(columns=['username', 'password'])

def save_new_user(username, password):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = get_user_db()
        if username in df['username'].values:
            return False 
        new_data = pd.DataFrame([{"username": username, "password": password}])
        updated_df = pd.concat([df, new_data], ignore_index=True)
        conn.update(data=updated_df)
        return True
    except:
        return False

# --- GESTIONE SESSIONE LOGIN ---
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
            user_row = db[db['username'].astype(str) == str(u)]
            if not user_row.empty and str(user_row['password'].values[0]) == str(p):
                st.session_state["logged_in"] = True
                st.session_state["user_active"] = u
                st.rerun()
            else:
                st.error("Credenziali errate")

    with tab2:
        st.subheader("Crea il tuo account")
        new_u = st.text_input("Scegli Username", key="r_user")
        new_p = st.text_input("Scegli Password", type="password", key="r_pass")
        if st.button("Registrati ora"):
            if new_u and new_p:
                if save_new_user(new_u, new_p):
                    st.success("Account creato! Ora puoi fare il Login.")
                else:
                    st.warning("Errore o username già occupato.")
            else:
                st.error("Compila tutti i campi.")
    st.stop()

# --- DA QUI IN POI L'APP DOPO IL LOGIN ---
st.sidebar.write(f"Connesso come: **{st.session_state['user_active']}**")
if st.sidebar.button("Log out"):
    st.session_state["logged_in"] = False
    st.rerun()

st.title("🧠 REWIRE AI - Factory")
st.write("Benvenuto nel sistema operativo.")

# Aggiungi qui il resto del tuo codice per la chat e Groq...
