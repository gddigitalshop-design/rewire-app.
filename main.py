import streamlit as st
import requests
import base64
import PyPDF2
import io

# --- 1. SETUP UI: DESIGN PREMIUM & VIVO ---
st.set_page_config(page_title="REWIRE AI - Group 4.0", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.07) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
    }

    /* Immagini caricate: Centrate e Grandi */
    .stImage > img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        border-radius: 15px;
        border: 2px solid #6366f1;
    }

    [data-testid="stChatInput"] {
        border-radius: 20px !important;
        border: 1px solid #6366f1 !important;
    }
    
    h1, h2, h3 { color: #818cf8 !important; text-align: center; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGICA DI ACCESSO ---
if "auth" not in st.session_state: st.session_state.auth = False
if "messages" not in st.session_state: st.session_state.messages = []

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("Errore: Chiave API Groq non trovata nei Secrets.")
    st.stop()

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1>⚡ REWIRE PRO</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Licenza Group 4.0:", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Licenza non valida.")
    st.stop()

# --- 3. FUNZIONE LETTURA PDF ---
def get_pdf_text(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except:
        return ""

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("📂 Risorse")
    st.info("Group 4.0: Supporto PDF & Immagini")
    file = st.file_uploader("Carica File", type=["pdf", "png", "jpg", "jpeg"])
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 5. CHAT ENGINE ---
st.markdown("<h3>🚀 Analizzatore Intelligente</h3>", unsafe_allow_html=True)

# Mostra lo storico
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if "image" in m: st.image(m["image"], width=500)
        st.markdown(m["content"])

# Nuovo input
if prompt := st.chat_input("Scrivi qui..."):
    
    # 1. Prepariamo il messaggio dell'utente (quello che apparirà in chat)
    user_msg_for_ui = {"role": "user", "content": prompt}
    
    # 2. Prepariamo il contenuto extra (PDF o Immagine)
    img_b64 = None
    context_from_pdf = ""
    
    if file:
        if file.type == "application/pdf":
            context_from_pdf = get_pdf_text(file)
        else:
            img_bytes = file.getvalue()
            user_msg_for_ui["image"] = img_bytes
            img_b64 = base64.b64encode(img_bytes).decode()

    # Visualizziamo subito il messaggio utente
    with st.chat_message("user"):
        if "image" in user_msg_for_ui: st.image(user_msg_for_ui["image"], width=500)
        st.markdown(prompt)
    
    st.session_state.messages.append(user_msg_for_ui)

    # 3. Risposta AI
    with st.chat_message("assistant"):
        with st.spinner("Rewire sta pensando..."):
            try:
                # Scegliamo il modello
                model = "llama-3.2-11b-vision-preview" if img_b64 else "llama-3.3-70b-versatile"
                
                # Costruiamo il prompt finale per l'AI (con il PDF se esiste)
                final_prompt_ai = prompt
                if context_from_pdf:
                    final_prompt_ai = f"CONTESTO DOCUMENTO PDF:\n{context_from_pdf}\n\nDOMANDA UTENTE: {prompt}"

                headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
                
                # Messaggi per l'API (con memoria degli ultimi 4)
                msgs_for_api = [{"role": "system", "content": "Sei Rewire AI Group 4.0. Rispondi in modo professionale."}]
                for m in st.session_state.messages[-4:-1]:
                    msgs_for_api.append({"role": m["role"], "content": m["content"]})
                
                # Aggiungiamo l'ultimo messaggio (con immagine o testo+pdf)
                if img_b64:
                    content = [{"type": "text", "text": final_prompt_ai}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}]
                else:
                    content = final_prompt_ai
                
                msgs_for_api.append({"role": "user", "content": content})

                r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json={"model": model, "messages": msgs_for_api})
                
                ans = r.json()['choices'][0]['message']['content']
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                
            except Exception as e:
                st.error("Errore nella risposta dell'AI.")
