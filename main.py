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

# --- 4. COLONNA FUNZIONI (SIDEBAR) ---
with st.sidebar:
    # LOGO E TITOLO GRANDE
    # Ho scelto l'icona "🧠" abbinata a un effetto neon rosso
    st.markdown("""
        <div style="text-align: center; padding-bottom: 20px;">
            <h1 style="color: #ff4b4b; font-size: 3.5rem; font-weight: 900; margin-bottom: 0px;">
                🧠 REWIRE AI
            </h1>
            <p style="color: #888; font-size: 0.9rem; letter-spacing: 2px;">FACTORY EDITION</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Stato del sistema
    st.caption(f"Status: {test_connection()}")
    st.markdown("---")

    # --- SEZIONE 1: CARICAMENTO FILE (ORA NELLA SIDEBAR) ---
    st.markdown("### 📁 INPUT DOCUMENTI")
    uploaded_file = st.file_uploader("Trascina qui PDF o Immagini", type=["pdf", "png", "jpg", "jpeg"])
    pdf_text = ""
    
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            testo_completo = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
            # Taglio di sicurezza per Groq
            pdf_text = testo_completo[:25000] if len(testo_completo) > 25000 else testo_completo
            st.success("✅ Documento caricato")
        else:
            st.image(uploaded_file, use_container_width=True)
            st.info("📸 Immagine pronta")

    st.markdown("---")

    # --- SEZIONE 2: AZIONI RAPIDE ---
    st.markdown("### ⚡ FUNZIONI RAPIDE")
    col1, col2 = st.columns(2) # Mettiamo i tasti su due colonne per risparmiare spazio
    with col1:
        if st.button("🥗 DIETA", use_container_width=True):
            st.session_state.active_prompt = "Crea una tabella dieta professionale."
    with col2:
        if st.button("🌐 TRADUCI", use_container_width=True):
            st.session_state.active_prompt = "Traduci il testo in modo professionale."
    
    if st.button("📋 ANALISI CONTRATTO", use_container_width=True):
        st.session_state.active_prompt = "Analizza i punti critici del documento."

    st.markdown("---")

    # --- SEZIONE 3: GESTIONE LAVORO (SEMPRE VISIBILI) ---
    st.markdown("### 💾 GESTIONE")

    ultimo_lavoro = ""
    if st.session_state.messages:
        for m in reversed(st.session_state.messages):
            if m['role'] == "assistant":
                ultimo_lavoro = m['content']
                break

    report_pulp = f"REWIRE AI - REPORT PROFESSIONALE\n{'='*30}\n\n" + (ultimo_lavoro if ultimo_lavoro else "Nessun dato.")

    st.download_button(
        label="💾 SALVA RISULTATO",
        data=report_pulp,
        file_name="risultato_rewire.txt",
        mime="text/plain",
        use_container_width=True
    )

    if st.button("🗑️ CANCELLA TUTTO", use_container_width=True):
        st.session_state.messages = []
        if "active_prompt" in st.session_state: del st.session_state["active_prompt"]
        st.rerun()

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





