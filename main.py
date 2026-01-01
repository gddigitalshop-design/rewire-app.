import streamlit as st
import requests
import base64
import PyPDF2
import io

# --- 1. SETUP UI: DESIGN PREMIUM ---
st.set_page_config(page_title="REWIRE AI - Group 4.0", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    .main-logo {
        font-size: 3rem !important;
        font-weight: 800;
        background: -webkit-linear-gradient(#818cf8, #6366f1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
    }
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.07) !important;
        backdrop-filter: blur(15px);
        border-radius: 15px !important;
    }
    [data-testid="stFileUploadDropzone"] {
        border: 2px dashed #6366f1 !important;
        background: rgba(99, 102, 241, 0.05) !important;
        border-radius: 20px !important;
    }
    h3 { color: #818cf8 !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGICA DI ACCESSO ---
if "auth" not in st.session_state: st.session_state.auth = False
if "messages" not in st.session_state: st.session_state.messages = []

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("Errore: Chiave API Groq non trovata.")
    st.stop()

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<p class='main-logo'>⚡ REWIRE PRO</p>", unsafe_allow_html=True)
        pwd = st.text_input("Licenza Group 4.0 (2026):", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "rewire2026": #
                st.session_state.auth = True
                st.rerun()
            else: st.error("Licenza non valida.")
    st.stop()

# --- 3. FUNZIONI UTILI ---
def get_pdf_text(file):
    try:
        reader = PyPDF2.PdfReader(file)
        return "\n".join([page.extract_text() for page in reader.pages])
    except: return ""

def prepare_download_text(messages):
    report = "--- REWIRE AI - REPORT SESSIONE ---\n\n"
    for m in messages:
        role = "UTENTE" if m["role"] == "user" else "REWIRE AI"
        report += f"{role}: {m['content']}\n\n"
    return report

# --- 4. SIDEBAR FISSA ---
with st.sidebar:
    st.markdown("<h2 style='text-align:left;'>📂 Pannello</h2>", unsafe_allow_html=True)
    # Se la chat è già avviata, l'uploader rimane qui
    sidebar_file = st.file_uploader("Carica nuovo documento", type=["pdf", "png", "jpg", "jpeg"], key="side_up")
    
    st.markdown("---")
    if st.session_state.messages:
        st.download_button("💾 SALVA REPORT", data=prepare_download_text(st.session_state.messages), file_name="report_rewire.txt")
    
    if st.button("🗑️ RESET"):
        st.session_state.messages = []
        st.rerun()

# --- 5. LAYOUT CENTRALE ---
st.markdown("<p class='main-logo'>REWIRE AI</p>", unsafe_allow_html=True)
st.markdown("<h3>Analizzatore Intelligente Group 4.0</h3>", unsafe_allow_html=True)

# AREA DI BENVENUTO E UPLOAD CENTRALE (solo se chat vuota)
main_file = None
if not st.session_state.messages:
    _, center_col, _ = st.columns([1, 2, 1])
    with center_col:
        st.write("### Benvenuto. Carica un file per iniziare l'analisi.")
        main_file = st.file_uploader("Trascina qui il tuo file (PDF o Immagine)", type=["pdf", "png", "jpg", "jpeg"], key="main_up")

# Unifichiamo il file caricato (o dalla sidebar o dal centro)
active_file = main_file if main_file else sidebar_file

# Visualizzazione Chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if "image" in m: st.image(m["image"], width=500)
        st.markdown(m["content"])

# --- 6. BARRA DI CHAT (SEMPRE PRESENTE) ---
if prompt := st.chat_input("Chiedi a Rewire..."):
    user_msg = {"role": "user", "content": prompt}
    img_b64 = None
    pdf_context = ""
    
    if active_file:
        if active_file.type == "application/pdf":
            pdf_context = get_pdf_text(active_file)
        else:
            img_bytes = active_file.getvalue()
            user_msg["image"] = img_bytes
            img_b64 = base64.b64encode(img_bytes).decode()

    st.session_state.messages.append(user_msg)
    st.rerun() # Aggiorna la UI per mostrare il messaggio dell'utente

# Logica Risposta AI (se l'ultimo messaggio è dell'utente)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    last_msg = st.session_state.messages[-1]
    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            try:
                model = "llama-3.2-11b-vision-preview" if "image" in last_msg else "llama-3.3-70b-versatile"
                
                # Recuperiamo il contesto PDF se presente nel file attivo
                final_prompt = last_msg["content"]
                if active_file and active_file.type == "application/pdf":
                    pdf_context = get_pdf_text(active_file)
                    final_prompt = f"CONTESTO PDF:\n{pdf_context}\n\nDOMANDA: {last_msg['content']}"

                headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
                msgs_api = [{"role": "system", "content": "Sei Rewire AI. Rispondi in modo professionale."}]
                
                # Payload per immagine o testo
                if "image" in last_msg:
                    b64 = base64.b64encode(last_msg["image"]).decode()
                    content = [{"type": "text", "text": last_msg["content"]}, 
                               {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}]
                else:
                    content = final_prompt

                msgs_api.append({"role": "user", "content": content})
                r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": model, "messages": msgs_api})
                ans = r.json()['choices'][0]['message']['content']
                
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                st.rerun()
            except:
                st.error("Connessione ai circuiti fallita.")
