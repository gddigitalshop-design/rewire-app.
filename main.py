import streamlit as st
from groq import Groq
import PyPDF2
import random
import urllib.parse

# --- 1. LOOK & FEEL (L'estetica che avevamo scelto) ---
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="📈", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0B0E11; color: #E9ECEF; }
    .stButton>button { border-radius: 10px; background-color: #007BFF; color: white; width: 100%; border: none; padding: 10px; font-weight: bold; }
    .stButton>button:hover { background-color: #0056b3; }
    .stChatMessage { background-color: #161B22; border-radius: 15px; border: 1px solid #30363D; margin-bottom: 10px; }
    /* Titolo RE-WIRE */
    .main-title { font-size: 3.5rem; font-weight: 800; color: #007BFF; text-align: center; margin-bottom: 0; }
    .subtitle { text-align: center; color: #8B949E; margin-bottom: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LOGICA DI ACCESSO (Per affittare l'app) ---
USERS = {
    "admin": "tuapassword123",
    "cliente1": "rewire2025",
    "test": "test2025"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.messages = []

def login_page():
    st.markdown('<p class="main-title">RE-WIRE</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">L\'Intelligenza Artificiale per il tuo Business</p>', unsafe_allow_html=True)
    with st.container():
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Accedi al Sistema"):
                if u in USERS and USERS[u] == p:
                    st.session_state.logged_in = True
                    st.session_state.user_role = u
                    st.rerun()
                else:
                    st.error("Credenziali non valide")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# --- 3. FUNZIONI TECNICHE ---
def genera_immagine(prompt_immagine):
    # Il trucco del seed casuale per forzare il cambio immagine (Uva vs Fico)
    seed = random.randint(0, 999999)
    prompt_pulito = urllib.parse.quote(prompt_immagine)
    # Usiamo il modello Flux per dettagli botanici precisi
    url = f"https://image.pollinations.ai/prompt/{prompt_pulito}?width=1024&height=1024&nologo=true&seed={seed}&model=flux"
    return url

# --- 4. SIDEBAR (Pannello Operativo) ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/brainstorming.png", width=80)
    st.title("Area Riservata")
    st.write(f"Utente: **{st.session_state.user_role.upper()}**")
    
    if st.button("Esci"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    st.subheader("📂 Analisi Documenti")
    file = st.file_uploader("Carica PDF aziendali", type="pdf")
    
    if file:
        reader = PyPDF2.PdfReader(file)
        testo_pdf = "".join([p.extract_text() for p in reader.pages])
        st.session_state.messages.append({"role": "system", "content": f"CONTESTO PDF: {testo_pdf[:4000]}"})
        st.success(f"File '{file.name}' analizzato!")
        st.divider()
    if  st.button("🗑️ Svuota Sessione", help="Cancella cronologia e immagini"):
        st.session_state.messages = []
        st.session_state.generated_image = None
        st.rerun()
# --- 5. AREA PRINCIPALE (Generatore e Chat) ---
st.markdown(f"### Benvenuto, {st.session_state.user_role.capitalize()}")

# Sezione ✨ Generatore Creativo
with st.expander("✨ GENERATORE DI IMMAGINI E TEMPLATE", expanded=True):
    creative_input = st.text_input("Cosa vuoi creare oggi?")
    col_img, col_temp = st.columns(2)
    
    with col_img:
        if st.button("🖼️ Genera Immagine"):
            if creative_input:  # <-- Questa riga deve avere uno spazio extra a sinistra rispetto a 'if st.button'
                with st.spinner("Creazione immagine..."):
                    img_url = genera_immagine(creative_input)
                    st.image(img_url, caption=f"Risultato per: {creative_input}")
                    st.session_state.messages.append({"role": "assistant", "content": f"Immagine: {img_url}"})
            else:
                st.warning("Scrivi qualcosa prima!")

    with col_temp:
        if st.button("📝 Crea Template"):
            if creative_input:
                with st.spinner("Elaborazione template..."):
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    resp = client.chat.completions.create(
                        messages=[{"role": "system", "content": "Sei un esperto di organizzazione aziendale. Crea template in formato tabella o lista Markdown."},
                                  {"role": "user", "content": f"Crea un template per: {creative_input}"}],
                        model="llama-3.3-70b-versatile"
                    )
                    template = resp.choices[0].message.content
                    st.markdown(template)
                    st.session_state.messages.append({"role": "assistant", "content": f"Ecco il template per '{creative_input}':\n\n{template}"})
            else: st.warning("Scrivi qualcosa prima!")

st.divider()

# 6. CHAT STORICA
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# INPUT CHAT
if prompt := st.chat_input("Chiedi un'analisi o una strategia..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        compl = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        response = compl.choices[0].message.content
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})




