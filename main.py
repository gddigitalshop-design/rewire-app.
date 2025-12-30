import streamlit as st
from groq import Groq
import PyPDF2
import random
import urllib.parse
import requests
import io
from PIL import Image

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="📈", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_img_data" not in st.session_state:
    st.session_state.current_img_data = None
if "current_template" not in st.session_state:
    st.session_state.current_template = None

# --- 2. LOGIN (Persistente per la sessione) ---
USERS = {"admin": "tuapassword123", "cliente1": "rewire2025"}

def login_page():
    st.markdown("<h1 style='text-align: center; color: #007BFF;'>RE-WIRE SYSTEM</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("ACCEDI"):
            if u in USERS and USERS[u] == p:
                st.session_state.logged_in = True
                st.session_state.user_role = u
                st.rerun()
            else:
                st.error("Credenziali errate")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# --- 3. MOTORE IMMAGINI CON CONTROLLO ANTI-CRASH ---
def genera_immagine_sicura(prompt_utente):
    seed = random.randint(1, 1000000)
    prompt_encoded = urllib.parse.quote(f"{prompt_utente}, professional, 8k, highly detailed")
    
    # Proviamo l'endpoint alternativo che è meno soggetto a blocchi
    url = f"https://pollinations.ai/p/{prompt_encoded}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"
    
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            # CONTROLLO CRITICO: Verifichiamo se è davvero un'immagine
            try:
                img = Image.open(io.BytesIO(r.content))
                img.verify() # Se non è un'immagine, qui genera errore
                return r.content
            except:
                return "formato_errato"
        return "errore_server"
    except:
        return "timeout"

# --- 4. INTERFACCIA ---
with st.sidebar:
    st.title("RE-WIRE PANEL")
    if st.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

st.header("🚀 Business Hub")
c_prompt = st.text_input("Cosa vuoi creare oggi?")

col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🖼️ GENERA IMMAGINE HD"):
        if c_prompt:
            with st.spinner("L'AI sta disegnando..."):
                risultato = genera_immagine_sicura(c_prompt)
                if isinstance(risultato, bytes):
                    st.session_state.current_img_data = risultato
                elif risultato == "formato_errato":
                    st.error("⚠️ Il server ha inviato un errore (Rate Limit). Riprova tra 30 secondi.")
                else:
                    st.error("❌ Connessione persa. Riprova.")
        else:
            st.warning("Inserisci un testo!")

with col_btn2:
    if st.button("📝 CREA TEMPLATE"):
        if c_prompt:
            with st.spinner("Scrittura..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Crea un template business per: {c_prompt}"}],
                        model="llama-3.3-70b-versatile"
                    )
                    st.session_state.current_template = res.choices[0].message.content
                except:
                    st.error("Errore Groq API")

# --- VISUALIZZAZIONE RISULTATI ---
if st.session_state.current_img_data:
    st.markdown("### Anteprima Visual")
    st.image(st.session_state.current_img_data, use_container_width=True)
    st.download_button("💾 SCARICA", st.session_state.current_img_data, "file.png", "image/png")
    if st.button("🗑️ CHIUDI IMMAGINE"):
        st.session_state.current_img_data = None
        st.rerun()

if st.session_state.current_template:
    st.info("Template Generato:")
    st.markdown(st.session_state.current_template)
    if st.button("🗑️ CHIUDI TEMPLATE"):
        st.session_state.current_template = None
        st.rerun()

st.divider()

# --- CHAT ---
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]): st.markdown(m["content"])

if p := st.chat_input("Chiedi alla tua AI..."):
    st.session_state.messages.append({"role": "user", "content": p})
    with st.chat_message("user"): st.markdown(p)
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        compl = client.chat.completions.create(messages=st.session_state.messages, model="llama-3.3-70b-versatile")
        resp = compl.choices[0].message.content
        st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
