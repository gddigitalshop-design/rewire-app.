import streamlit as st
from groq import Groq
import PyPDF2

# --- 1. CONFIGURAZIONE PAGINA (Look & Feel) ---
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0B0E11; color: #E9ECEF; }
    .stButton>button { border-radius: 10px; background-color: #007BFF; color: white; width: 100%; border: none; padding: 10px; }
    .stButton>button:hover { background-color: #0056b3; border: none; }
    .stChatMessage { background-color: #161B22; border-radius: 15px; border: 1px solid #30363D; margin-bottom: 10px; }
    /* Nasconde il menu Streamlit per un look più pulito */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIONE ACCESSO ---
USERS = {
    "admin": "tuapassword123",
    "cliente1": "rewire2025"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.messages = []

# Logica Link Magico
query_params = st.query_params
if not st.session_state.logged_in:
    u_url = query_params.get("user")
    p_url = query_params.get("pass")
    if u_url in USERS and USERS[u_url] == p_url:
        st.session_state.logged_in = True
        st.session_state.user_role = u_url

def login_page():
    st.markdown('<p style="font-size:3.5rem; font-weight:800; color:#007BFF; text-align:center; margin-bottom:0;">RE-WIRE</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#8B949E; margin-bottom:2rem;">L\'Intelligenza Artificiale per il tuo Business</p>', unsafe_allow_html=True)
    with st.container():
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

# --- 3. LOGICA DI BUSINESS (PDF & REPORT) ---
def genera_report():
    testo = f"--- REPORT CONSULENZA RE-WIRE ---\nUtente: {st.session_state.user_role}\n\n"
    for m in st.session_state.messages:
        if m["role"] != "system":
            testo += f"{m['role'].upper()}: {m['content']}\n\n"
    return testo

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/brainstorming.png", width=80)
    st.title("Area Riservata")
    st.write(f"Connesso come: **{st.session_state.user_role}**")
    
    if st.button("Esci"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    st.markdown("### 📊 Strumenti")
    
    if len(st.session_state.messages) > 0:
        st.download_button("💾 Scarica Risultati", genera_report(), f"analisi_{st.session_state.user_role}.txt")

    st.divider()
    st.markdown("### 📂 Analizzatore Documenti")
    file = st.file_uploader("Carica bilanci o PDF", type="pdf")
    
    if file:
        reader = PyPDF2.PdfReader(file)
        testo_pdf = "".join([p.extract_text() for p in reader.pages])
        if "ultimo_file" not in st.session_state or st.session_state.ultimo_file != file.name:
            st.session_state.messages.append({"role": "assistant", "content": f"✅ **Documento '{file.name}' caricato con successo.**\n\nHo analizzato il contenuto. Come posso aiutarti con questi dati?"})
            # Istruzione di sistema per l'IA
            st.session_state.messages.append({"role": "system", "content": f"Agisci come un esperto Business Consultant. Usa queste info dal PDF per rispondere: {testo_pdf[:4000]}"})
            st.session_state.ultimo_file = file.name
            st.rerun()

# --- 5. CHAT PRINCIPALE ---
st.markdown(f"### Benvenuto in RE-WIRE, {st.session_state.user_role}")

if not [m for m in st.session_state.messages if m["role"] != "system"]:
    st.markdown("""
    Ciao! Sono il tuo Business Brain. Ecco cosa posso fare per te oggi:
    * **Analisi PDF:** Carica un documento a sinistra e chiedimi riassunti o analisi.
    * **Strategia:** Chiedimi di creare un piano d'azione per il tuo business.
    * **Copywriting:** Posso scrivere email, post social o capitoli di ebook.
    """)

for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

if prompt := st.chat_input("Scrivi qui la tua richiesta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        compl = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        resp = compl.choices[0].message.content
        st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
