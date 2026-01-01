import streamlit as st
import requests
import base64
import PyPDF2

# --- 1. CONFIGURAZIONE UI ---
st.set_page_config(page_title="REWIRE AI - Group 4.0", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0b0e14; color: #e2e8f0; }
    [data-testid="stSidebar"] { background-color: #161b22 !important; border-right: 1px solid #30363d; }
    .main-header {
        font-size: 2.5rem; font-weight: 800; text-align: center;
        background: linear-gradient(120deg, #a78bfa, #22d3ee);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. FUNZIONI DI SISTEMA ---

def test_connection():
    """Verifica se la chiave API inserita nei Secrets funziona"""
    api_key = st.secrets.get("GROQ_API_KEY")
    if not api_key:
        return "🔴 Chiave Mancante"
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        r = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=5)
        if r.status_code == 200:
            return "🟢 Sistema Pronto"
        else:
            return f"🔴 Errore Chiave ({r.status_code})"
    except:
        return "🔴 Errore di Rete"

def call_rewire_brain(user_input, pdf_context=""):
    try:
        if "GROQ_API_KEY" not in st.secrets:
            return "ERRORE: Chiave API non trovata!"
        
        api_key = st.secrets["GROQ_API_KEY"]
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "Sei Rewire AI, un assistente accogliente e professionale."},
                {"role": "user", "content": f"CONTESTO: {pdf_context}\n\nDOMANDA: {user_input}"}
            ]
        }
        
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        response_json = r.json()

        if 'choices' in response_json:
            return response_json['choices'][0]['message']['content']
        else:
            messaggio_errore = response_json.get('error', {}).get('message', 'Errore sconosciuto')
            return f"⚠️ IL CERVELLO DICE: {messaggio_errore}"
            
    except Exception as e:
        return f"❌ ERRORE: {str(e)}"

# --- 3. ACCESSO & SESSIONE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<p class='main-header'>⚡ REWIRE PRO</p>", unsafe_allow_html=True)
        pwd = st.text_input("Inserisci Licenza:", type="password")
        if st.button("SBLOCCA"):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
    st.stop()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🏭 FABBRICA DIGITALE")
    
    # Mostra lo stato della connessione sotto il titolo
    st.caption(f"Status: {test_connection()}")
    
    st.markdown("---")
    if st.button("🥗 Crea Tabella Dieta"):
        st.session_state.active_prompt = "Crea un foglio organizzazione pasti e progressi dieta professionale in tabella."
    if st.button("🌐 Traduzione Pro"):
        st.session_state.active_prompt = "Traduci il testo o il documento caricato in modo professionale."
    if st.button("📋 Analisi Contratto"):
        st.session_state.active_prompt = "Analizza i punti critici di questo documento e riassumili."

# --- 5. PAGINA CENTRALE ---
# (Il resto del tuo codice per la visualizzazione della chat...)
st.markdown("<p class='main-header'>REWIRE AI</p>", unsafe_allow_html=True)
col_pdf, col_chat = st.columns([1, 1.5])

with col_pdf:
    st.markdown("#### 📁 File Input")
    uploaded_file = st.file_uploader("Carica PDF", type=["pdf"])
    pdf_text = ""
    # Cerca questa parte nel tuo codice e sostituiscila
if uploaded_file and uploaded_file.type == "application/pdf":
    reader = PyPDF2.PdfReader(uploaded_file)
    testo_estratto = []
    for p in reader.pages:
        testo_estratto.append(p.extract_text())
    
    pdf_text = "\n".join(testo_estratto)
    
    # --- AGGIUNGI QUESTO TAGLIO DI SICUREZZA ---
    # Limita il testo a circa 30.000 caratteri (circa 8.000 token) 
    # per stare dentro i limiti di Groq
    if len(pdf_text) > 30000:
        pdf_text = pdf_text[:30000] + "\n... (testo troncato per limiti di dimensione) ..."
        st.warning("⚠️ Il PDF è molto lungo. Ho analizzato solo le prime pagine per garantire la risposta.")
    else:
        st.success("Documento letto con successo.")

user_query = st.chat_input("Chiedi a Rewire...")
final_query = user_query or st.session_state.get("active_prompt")

if final_query:
    if "active_prompt" in st.session_state: del st.session_state["active_prompt"]
    st.session_state.messages.append({"role": "user", "content": final_query})
    with col_chat:
        with st.spinner("Rewire sta producendo..."):
            answer = call_rewire_brain(final_query, pdf_text)
            st.session_state.messages.append({"role": "assistant", "content": answer})

with col_chat:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

