import streamlit as st
import groq
import PyPDF2

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="REWIRE AI - Factory", layout="wide", initial_sidebar_state="expanded")

# --- CSS PER PERSONALIZZAZIONE ESTETICA (TITOLO ROSSO E SIDEBAR) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #ff4b4b33; }
    
    /* Bottoni Sidebar */
    div.stButton > button {
        border-radius: 5px;
        height: 3em;
        transition: all 0.3s;
        width: 100%;
    }
    
    /* Hover specifico per il tasto RESET */
    div.stButton > button:contains("RESET"):hover {
        border-color: #ff4b4b !important;
        color: #ff4b4b !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- INIZIALIZZAZIONE SESSIONE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "active_prompt" not in st.session_state:
    st.session_state.active_prompt = None

# --- FUNZIONE LOGICA AI (CON CONNESSIONE SICURA) ---
def call_rewire_brain(query, context=""):
    try:
        # Usa i Secrets di Streamlit per la sicurezza della licenza
        api_key = st.secrets["GROQ_API_KEY"]
        client = groq.Client(api_key=api_key) 
        
        full_prompt = f"Contesto documento: {context}\n\nDomanda utente: {query}" if context else query
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.5,
        )
        return completion.choices[0].message.content
    except KeyError:
        return "Errore: Chiave API non trovata nei Secrets del server."
    except Exception as e:
        return f"Errore di connessione: {str(e)}"

# --- SIDEBAR (PANNELLO DI CONTROLLO PULITO) ---
with st.sidebar:
    st.markdown("### 🛠️ STRUMENTI")
    
    # 1. CARICAMENTO FILE (NELLA SIDEBAR COME RICHIESTO)
    uploaded_file = st.file_uploader("📁 CARICA PDF O IMMAGINE", type=["pdf", "png", "jpg", "jpeg"])
    pdf_text = ""
    
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
            st.success("✅ PDF Letto")
        else:
            st.image(uploaded_file, caption="Immagine caricata", use_container_width=True)
            st.info("📸 Immagine Pronta")

    st.markdown("---")
    
    # 2. FUNZIONI RAPIDE
    st.markdown("### ⚡ PROMPT RAPIDI")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🥗 DIETA", use_container_width=True):
            st.session_state.active_prompt = "Crea una tabella dieta professionale basata sui dati forniti."
    with col_b:
        if st.button("🌐 TRADUCI", use_container_width=True):
            st.session_state.active_prompt = "Traduci il testo fornito in modo tecnico e professionale."

    st.markdown("---")

    # 3. GESTIONE LAVORO (SALVA E CANCELLA SEMPRE VISIBILI)
    st.markdown("### 💾 GESTIONE")
    
    ultimo_lavoro = ""
    if st.session_state.messages:
        for m in reversed(st.session_state.messages):
            if m['role'] == "assistant":
                ultimo_lavoro = m['content']
                break

    report_pulp = f"REWIRE AI - FACTORY REPORT\n{'='*30}\n\n" + (ultimo_lavoro if ultimo_lavoro else "Nessun dato.")

    st.download_button(
        label="💾 SALVA RISULTATO",
        data=report_pulp,
        file_name="risultato_rewire.txt",
        mime="text/plain",
        use_container_width=True
    )

    if st.button("🗑️ RESET SISTEMA", use_container_width=True):
        st.session_state.messages = []
        st.session_state.active_prompt = None
        st.rerun()

# --- AREA CENTRALE (DASHBOARD REWIRE AI) ---

if not st.session_state.messages:
    # IL CUORE DELL'APP: TITOLO GIGANTE ROSSO AL CENTRO
    st.markdown("""
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh;">
            <div style="text-align: center; border: 3px solid #ff4b4b; padding: 50px; border-radius: 30px; background-color: rgba(255, 75, 75, 0.03); box-shadow: 0px 0px 50px rgba(255, 75, 75, 0.1);">
                <h1 style="color: #ff4b4b; font-size: 6rem; font-weight: 900; margin-bottom: 0px; line-height: 1;">
                    🧠 REWIRE AI
                </h1>
                <p style="color: #ffffff; font-size: 1.8rem; letter-spacing: 8px; margin-top: 15px; font-weight: 300;">
                    FACTORY EDITION
                </p>
                <div style="margin-top: 30px; padding: 12px 25px; background-color: #0e1117; border: 1px solid #333; border-radius: 50px; display: inline-block;">
                    <span style="color: #00ff00; animation: pulse 2s infinite;">●</span> 
                    <span style="color: #888; font-family: monospace; font-size: 1.1rem; margin-left: 10px;">STATUS: SISTEMA PRONTO</span>
                </div>
            </div>
        </div>
        <style>
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
        </style>
    """, unsafe_allow_html=True)

else:
    # Mostra solo il lavoro quando attivo
    st.markdown("<h2 style='color: #ff4b4b;'>🧠 REWIRE AI <span style='font-size: 1rem; color: #444;'>WORKING...</span></h2>", unsafe_allow_html=True)
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

# --- INPUT UTENTE ---
user_query = st.chat_input("Chiedi a Rewire...")

# Logica di attivazione
prompt_to_send = user_query or st.session_state.active_prompt

if prompt_to_send:
    st.session_state.messages.append({"role": "user", "content": prompt_to_send})
    st.session_state.active_prompt = None # Pulisce il prompt dopo l'invio
    
    with st.spinner("⚡ Elaborazione..."):
        risposta = call_rewire_brain(prompt_to_send, pdf_text)
        st.session_state.messages.append({"role": "assistant", "content": risposta})
    st.rerun()
