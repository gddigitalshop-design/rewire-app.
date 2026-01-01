import streamlit as st
import requests
import base64
from PIL import Image
import io
import PyPDF2

# --- CONFIGURAZIONE E STILE AVANZATO ---
st.set_page_config(page_title="REWIRE AI - Group 4.0", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    /* Sfondo con gradiente per dare vita alla pagina */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1e2f 100%);
        color: #e2e8f0;
    }
    
    /* Sidebar elegante */
    [data-testid="stSidebar"] { background-color: rgba(0,0,0,0.5) !important; }

    /* Bolle della chat stilizzate */
    .stChatMessage {
        border-radius: 20px !important;
        padding: 15px !important;
        margin-bottom: 10px !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    /* Centratura automatica immagini */
    .stImage > img {
        border-radius: 15px;
        display: block;
        margin-left: auto;
        margin-right: auto;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.5);
    }

    /* Barra chat evidenziata */
    [data-testid="stChatInput"] {
        border: 2px solid #6366f1 !important;
        border-radius: 25px !important;
        background-color: #1e293b !important;
    }
</style>
""", unsafe_allow_html=True)

# --- INIZIALIZZAZIONE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "messages" not in st.session_state: st.session_state.messages = []

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("Configura la chiave API.")
    st.stop()

# --- LOGIN ---
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h1 style='text-align: center; color: #6366f1;'>⚡ REWIRE PRO</h1>", unsafe_allow_html=True)
        with st.form("login"):
            pwd = st.text_input("Licenza Group 4.0:", type="password")
            if st.form_submit_button("SBLOCCA"):
                if pwd == "rewire2026":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Password errata.")
    st.stop()

# --- FUNZIONE LETTURA PDF ---
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# --- SIDEBAR ---
with st.sidebar:
    st.title("📂 Area File")
    st.info("Versione: Group 4.0 (Active)")
    uploaded_file = st.file_uploader("Carica PDF o Immagine", type=["pdf", "png", "jpg", "jpeg"])
    
    if st.button("🗑️ Svuota Chat"):
        st.session_state.messages = []
        st.rerun()

# --- AREA CHAT ---
st.markdown("<h2 style='text-align: center;'>🚀 Smart Workspace</h2>", unsafe_allow_html=True)

# Visualizzazione cronologia
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if "image" in m: st.image(m["image"], use_container_width=True)
        st.markdown(m["content"])

# --- LOGICA INPUT ---
if prompt := st.chat_input("Scrivi qui o descrivi il file caricato..."):
    
    user_payload = {"role": "user", "content": prompt}
    img_b64 = None
    context_text = ""

    # Gestione automatica del file caricato
    if uploaded_file:
        file_type = uploaded_file.type
        
        # Se è un'immagine
        if "image" in file_type:
            img_data = uploaded_file.getvalue()
            user_payload["image"] = img_data # La salva per mostrarla
            img_b64 = base64.b64encode(img_data).decode()
        
        # Se è un PDF
        elif "pdf" in file_type:
            with st.spinner("Lettura PDF..."):
                context_text = read_pdf(uploaded_file)
                prompt = f"Analizza questo documento: {context_text}\n\nDomanda utente: {prompt}"

    # Visualizzazione immediata
    with st.chat_message("user"):
        if "image" in user_payload:
            st.image(user_payload["image"], caption="File caricato", use_container_width=True)
        st.markdown(prompt if not context_text else "📄 Documento PDF inviato con successo.")
    
    st.session_state.messages.append(user_payload)

    # RISPOSTA AI
    with st.chat_message("assistant"):
        with st.spinner("Elaborazione..."):
            try:
                model = "llama-3.2-11b-vision-preview" if img_b64 else "llama-3.3-70b-versatile"
                headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
                
                api_msgs = [{"role": "system", "content": "Sei Rewire AI Group 4.0. Sei professionale e preciso."}]
                for m in st.session_state.messages[-3:-1]:
                    api_msgs.append({"role": m["role"], "content": m["content"]})
                
                if img_b64:
                    content = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}]
                else:
                    content = prompt
                
                api_msgs.append({"role": "user", "content": content})

                r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": model, "messages": api_msgs})
                ans = r.json()['choices'][0]['message']['content']
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            except:
                st.error("Errore di connessione al cervello AI.")
