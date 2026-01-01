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

# --- 2. ACCESSO & SESSIONE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "messages" not in st.session_state: st.session_state.messages = []

# Funzione per chiamare Groq
def call_rewire_brain(user_input, pdf_context=""):
    try:
        api_key = st.secrets["GROQ_API_KEY"] # Usa la chiave salvata ieri
        headers = {"Authorization": f"Bearer {api_key}"}
        
        full_prompt = f"Contesto Documento: {pdf_context}\n\nRichiesta: {user_input}"
        
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "Sei Rewire AI. Sei un assistente professionale, empatico e risolutivo. Crea tabelle, traduzioni e report pronti all'uso."},
                {"role": "user", "content": full_prompt}
            ],
            "temperature": 0.5
        }
        
        r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
        return r.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Errore di connessione al cervello Rewire: {e}"

# --- 3. LOGIN ---
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

# --- 4. COLONNA FUNZIONI (SIDEBAR) ---
with st.sidebar:
    st.markdown("### 🏭 FABBRICA DIGITALE")
    
    # Questi tasti ora generano un'azione reale
    if st.button("🥗 Crea Tabella Dieta"):
        st.session_state.active_prompt = "Crea un foglio organizzazione pasti e progressi dieta professionale in tabella."
        
    if st.button("🌐 Traduzione Pro"):
        st.session_state.active_prompt = "Traduci il testo o il documento caricato in modo professionale."
        
    if st.button("📋 Analisi Contratto"):
        st.session_state.active_prompt = "Analizza i punti critici di questo documento e riassumili."

    st.markdown("---")
    if st.session_state.messages:
        report = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        st.download_button("💾 SALVA LAVORO", report, file_name="prodotto_rewire.txt")
    
    if st.button("🗑️ Reset"):
        st.session_state.messages = []
        st.rerun()

# --- 5. PAGINA CENTRALE ---
st.markdown("<p class='main-header'>REWIRE AI</p>", unsafe_allow_html=True)
col_pdf, col_chat = st.columns([1, 1.5])

with col_pdf:
    st.markdown("#### 📁 File Input")
    uploaded_file = st.file_uploader("Carica PDF", type=["pdf", "png", "jpg", "jpeg"])
    pdf_text = ""
    if uploaded_file and uploaded_file.type == "application/pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        pdf_text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        st.success("Documento letto con successo.")

# Gestione Input Chat e Tasti Sidebar
user_query = st.chat_input("Chiedi a Rewire...")
final_query = user_query or st.session_state.get("active_prompt")

if final_query:
    # Resetta il prompt della sidebar dopo l'uso
    if "active_prompt" in st.session_state: del st.session_state["active_prompt"]
    
    # Messaggio utente
    st.session_state.messages.append({"role": "user", "content": final_query})
    
    # Risposta AI Reale
    with col_chat:
        with st.spinner("Rewire sta producendo..."):
            answer = call_rewire_brain(final_query, pdf_text)
            st.session_state.messages.append({"role": "assistant", "content": answer})

# Visualizzazione Chat
with col_chat:
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
