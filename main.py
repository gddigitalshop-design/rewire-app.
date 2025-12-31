import streamlit as st
import requests
import fitz
from PIL import Image
import io

# --- CONFIGURAZIONE API ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE AI", layout="wide", page_icon="⚡")

# --- DESIGN "ANIMA E OCCHI" (CSS AVANZATO) ---
st.markdown("""
    <style>
    /* Sfondo animato e profondo */
    .stApp {
        background: radial-gradient(circle at top right, #1e2a4a, #0d1117);
        color: #e6edf3;
    }
    
    /* Header e Logo Animato */
    .main-title {
        font-size: 55px !important;
        font-weight: 900 !important;
        background: linear-gradient(90deg, #00f2fe, #4facfe, #00f2fe);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
        text-align: center;
        margin-bottom: 0px;
    }
    
    @keyframes shine {
        to { background-position: 200% center; }
    }

    /* Messaggio di Benvenuto Sprizzante */
    .welcome-text {
        text-align: center;
        font-size: 26px;
        color: #4facfe;
        font-weight: 300;
        margin-bottom: 30px;
    }

    /* Sidebar elegante con Glassmorphism */
    [data-testid="stSidebar"] {
        background-color: rgba(13, 17, 23, 0.85);
        border-right: 1px solid rgba(79, 172, 254, 0.3);
        backdrop-filter: blur(12px);
    }

    /* Chat Bubbles */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.04) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        backdrop-filter: blur(5px);
        margin-bottom: 15px;
    }

    /* Bottoni Premium */
    .stButton > button {
        border-radius: 30px !important;
        background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%) !important;
        color: #0d1117 !important;
        font-weight: bold !important;
        border: none !important;
        padding: 0.6rem 2.5rem !important;
        transition: 0.4s all !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stButton > button:hover {
        transform: scale(1.03);
        box-shadow: 0 10px 25px rgba(79, 172, 254, 0.5) !important;
    }

    /* Input Styling */
    .stChatInputContainer {
        padding-bottom: 20px !important;
    }
    
    /* Status box styling */
    div[data-testid="stStatusWidget"] {
        background-color: rgba(0, 242, 254, 0.1);
        border: 1px solid #00f2fe;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN (Protetto e Invisibile al Reset) ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.8, 1])
    with col:
        st.markdown("<br><br><br><h1 class='main-title'>⚡ RE-WIRE</h1>", unsafe_allow_html=True)
        st.markdown("<p class='welcome-text'>L'intelligenza al servizio della tua visione.</p>", unsafe_allow_html=True)
        with st.container(border=True):
            pwd = st.text_input("🔑 Chiave d'Accesso:", type="password", placeholder="Inserisci il codice...")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("SBLOCCA RE-WIRE"):
                if pwd == "rewire2026":
                    st.session_state.auth = True
                    st.rerun()
                else:
                    st.error("Accesso negato. Controlla la chiave.")
    st.stop()

# --- INIZIALIZZAZIONE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""
if "current_file" not in st.session_state: st.session_state.current_file = None

# --- SIDEBAR (GESTIONE DOCUMENTI) ---
with st.sidebar:
    st.markdown("<h1 style='font-size: 28px; color: #4facfe;'>⚡ RE-WIRE AI</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Caricatore file
    file = st.file_uploader("📂 Carica Risorsa (Ebook, PDF, Immagini)", type=["pdf", "jpg", "png", "jpeg"])
    
    if file:
        if "last_fn" not in st.session_state or st.session_state.last_fn != file.name:
            # Mostra lo stato di avanzamento durante il caricamento di file grossi
            with st.status("🧠 Elaborazione del documento in corso...", expanded=True) as status:
                st.session_state.messages = []
                st.session_state.last_fn = file.name
                
                if file.type == "application/pdf":
                    doc = fitz.open(stream=file.read(), filetype="pdf")
                    # Aumentato a 8000 per ebook più complessi
                    st.session_state.doc_text = "".join([p.get_text() for p in doc])[:8000]
                    st.session_state.current_file = {"type": "pdf", "name": file.name}
                else:
                    st.session_state.doc_text = f"Analisi immagine: {file.name}"
                    st.session_state.current_file = {"type": "img", "data": file.read(), "name": file.name}
                
                status.update(label="✅ Documento pronto!", state="complete", expanded=False)
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # PULSANTE RESET
    if st.button("🗑️ RESET WORKSPACE"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.current_file = None
        st.rerun()
    
    # DOWNLOAD REPORT
    if st.session_state.messages:
        chat_history = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        st.download_button("📩 SCARICA REPORT CHAT", chat_history, file_name=f"report_{file.name if file else 'chat'}.txt")

# --- AREA DI LAVORO CENTRALE ---
if not st.session_state.current_file:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 class='main-title'>⚡ RE-WIRE AI</h1>", unsafe_allow_html=True)
    st.markdown("<p class='welcome-text'>Buongiorno! Cosa posso fare per te oggi?</p>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; opacity: 0.5; font-style: italic;'>Carica un file dalla dashboard per iniziare un'analisi intelligente.</div>", unsafe_allow_html=True)
else:
    st.markdown(f"<h3 style='text-align: center; color: #4facfe;'>💎 RISORSA ATTIVA: {st.session_state.current_file['name']}</h3>", unsafe_allow_html=True)
    with st.expander("👁️ ISPEZIONA CONTENUTO"):
        if st.session_state.current_file['type'] == "img":
            st.image(st.session_state.current_file['data'], use_container_width=True)
        else:
            st.write(st.session_state.doc_text)

st.markdown("<hr style='opacity: 0.2;'>", unsafe_allow_html=True)

# --- INTERFACCIA CHAT ---
# Visualizza messaggi esistenti
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Nuovo input
if prompt := st.chat_input("Scrivi qui la tua domanda o comando..."):
    # Salva e visualizza input utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Genera risposta con l'AI
    with st.chat_message("assistant"):
        try:
            # Prompt di sistema raffinato per un tono amichevole e professionale
            system_prompt = (
                "Sei RE-WIRE AI, un assistente brillante, amichevole e molto preparato. "
                "Il tuo obiettivo è aiutare l'utente con competenza e un tono ispiratore. "
                "Se è presente un contesto, usalo per dare risposte precise."
            )
            
            payload = {
                "model": MODEL_ID, 
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Contesto: {st.session_state.doc_text}\n\nDomanda: {prompt}"}
                ]
            }
            
            r = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
            ans = r.json()['choices'][0]['message']['content']
        except:
            ans = "⚠️ Mi dispiace, ho avuto un piccolo calo di energia. Puoi ripetere la domanda?"
        
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
