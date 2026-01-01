import streamlit as st
import requests
import base64
import PyPDF2

# --- 1. CONFIGURAZIONE UI ---
st.set_page_config(page_title="REWIRE AI - Group 4.0", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp { background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 100%); color: #f8fafc; }
    .header-box { text-align: center; padding: 20px; border-bottom: 1px solid rgba(99, 102, 241, 0.3); }
    .main-logo { font-size: 3.5rem !important; font-weight: 800; background: linear-gradient(to right, #818cf8, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; }
    [data-testid="stChatMessage"] { background: rgba(255, 255, 255, 0.05) !important; border-radius: 15px !important; }
    /* Nasconde l'etichetta dell'uploader per un look più pulito */
    .stFileUploader label { display: none; }
</style>
""", unsafe_allow_html=True)

# --- 2. LOGICA DI ACCESSO ---
if "auth" not in st.session_state: st.session_state.auth = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>⚡ REWIRE PRO</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Licenza Group 4.0 (2026):", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Licenza non valida.")
    st.stop()

# --- 3. HEADER FISSO ---
st.markdown("<div class='header-box'><p class='main-logo'>REWIRE AI</p><p style='color:#94a3b8;'>Intelligence & Recovery System</p></div>", unsafe_allow_html=True)

# --- 4. SIDEBAR (Solo Reset e Download) ---
with st.sidebar:
    st.title("📂 Gestione Sessione")
    if st.button("🗑️ Reset Totale"):
        st.session_state.messages = []
        st.rerun()
    if st.session_state.messages:
        report = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        st.download_button("💾 Salva Analisi", report, file_name="report_rewire.txt")

# --- 5. UNICO CARICAMENTO FILE (CENTRALE) ---
# Questo è l'unico uploader dell'app. Appare sotto il logo.
st.markdown("<p style='text-align:center; margin-top:10px;'>Trascina qui il documento da analizzare (PDF o Immagine)</p>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    uploaded_file = st.file_uploader("Upload", type=["pdf", "png", "jpg", "jpeg"], key="single_uploader")

# --- 6. VISUALIZZAZIONE STORICO CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if "image" in m: st.image(m["image"], width=450)
        st.markdown(m["content"])

# --- 7. LOGICA CHAT ---
if prompt := st.chat_input("Chiedi a Rewire..."):
    # Messaggio Utente
    user_msg = {"role": "user", "content": prompt}
    
    # Processamento File (se presente al momento dell'invio)
    pdf_text = ""
    img_b64 = None
    
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            try:
                reader = PyPDF2.PdfReader(uploaded_file)
                pdf_text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
            except: st.error("Errore lettura PDF")
        else:
            img_bytes = uploaded_file.getvalue()
            user_msg["image"] = img_bytes
            img_b64 = base64.b64encode(img_bytes).decode()

    st.session_state.messages.append(user_msg)
    
    # Generazione Risposta AI
    with st.chat_message("assistant"):
        with st.spinner("Rewire sta elaborando..."):
            try:
                api_key = st.secrets["GROQ_API_KEY"]
                headers = {"Authorization": f"Bearer {api_key}"}
                model = "llama-3.2-11b-vision-preview" if img_b64 else "llama-3.3-70b-versatile"
                
                # Costruzione del contenuto
                if pdf_text:
                    content_ai = f"CONTESTO DOCUMENTO:\n{pdf_text}\n\nDOMANDA: {prompt}"
                elif img_b64:
                    content_ai = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}]
                else:
                    content_ai = prompt

                r = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "Sei Rewire AI Group 4.0. Rispondi in italiano professionale."},
                            {"role": "user", "content": content_ai}
                        ]
                    }
                )
                
                if r.status_code == 200:
                    ans = r.json()['choices'][0]['message']['content']
                    st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                    st.rerun()
                else:
                    st.error(f"Errore API: {r.status_code}")
            except Exception as e:
                st.error("Connessione ai circuiti fallita. Verifica la configurazione.")
