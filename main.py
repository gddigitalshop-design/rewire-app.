import streamlit as st
import requests
import base64
import PyPDF2

# --- 1. CONFIGURAZIONE UI ---
st.set_page_config(page_title="REWIRE AI - Group 4.0", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp { 
        background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 100%); 
        color: #f8fafc; 
    }
    .header-container { text-align: center; padding: 20px; }
    .main-logo { 
        font-size: 3.5rem !important; 
        font-weight: 800; 
        background: linear-gradient(to right, #818cf8, #6366f1); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
    }
    /* Centratura perfetta del caricamento */
    [data-testid="stFileUploadDropzone"] { 
        background: rgba(99, 102, 241, 0.05) !important; 
        border: 2px dashed #6366f1 !important; 
        border-radius: 20px !important;
        min-height: 200px;
    }
    .stFileUploader label { display: none; }
</style>
""", unsafe_allow_html=True)

# --- 2. ACCESSO ---
if "auth" not in st.session_state: st.session_state.auth = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<h1 style='text-align:center;'>⚡ REWIRE PRO</h1>", unsafe_allow_html=True)
        pwd = st.text_input("Licenza Group 4.0:", type="password")
        if st.button("SBLOCCA"):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
            else: st.error("Licenza non valida.")
    st.stop()

# --- 3. HEADER ---
st.markdown("<div class='header-container'><p class='main-logo'>REWIRE AI</p><p>Intelligence & Recovery System</p></div>", unsafe_allow_html=True)

# --- 4. SIDEBAR (GESTIONE E SALVATAGGIO) ---
with st.sidebar:
    st.title("📂 Gestione Lavoro")
    
    # TASTO SALVA FILE (Esporta la chat)
    if st.session_state.messages:
        chat_history = "--- REPORT REWIRE AI ---\n\n"
        for m in st.session_state.messages:
            chat_history += f"{m['role'].upper()}: {m['content']}\n\n"
        
        st.download_button(
            label="💾 SALVA FILE DI LAVORO",
            data=chat_history,
            file_name="lavoro_rewire.txt",
            mime="text/plain"
        )
    
    if st.button("🗑️ RESET SESSIONE"):
        st.session_state.messages = []
        st.rerun()

# --- 5. CARICAMENTO CENTRALE (UNICO) ---
# Usiamo le colonne per centrare l'area di upload
_, center_col, _ = st.columns([1, 2, 1])
with center_col:
    st.write("### Trascina qui il file da analizzare")
    uploaded_file = st.file_uploader("", type=["pdf", "png", "jpg", "jpeg"], key="solo_uploader")

# --- 6. VISUALIZZAZIONE CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if "image" in m: st.image(m["image"], width=400)
        st.markdown(m["content"])

# --- 7. LOGICA AI ---
if prompt := st.chat_input("Chiedi a Rewire..."):
    user_msg = {"role": "user", "content": prompt}
    
    # Estrazione testo o immagine
    pdf_text = ""
    img_b64 = None
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            pdf_text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
        else:
            img_bytes = uploaded_file.getvalue()
            user_msg["image"] = img_bytes
            img_b64 = base64.b64encode(img_bytes).decode()

    st.session_state.messages.append(user_msg)
    
    with st.chat_message("assistant"):
        with st.spinner("Rewire sta elaborando..."):
            try:
                headers = {"Authorization": f"Bearer {st.secrets['GROQ_API_KEY']}"}
                model = "llama-3.2-11b-vision-preview" if img_b64 else "llama-3.3-70b-versatile"
                
                if pdf_text:
                    content_ai = f"CONTESTO DOCUMENTO:\n{pdf_text}\n\nDOMANDA: {prompt}"
                elif img_b64:
                    content_ai = [{"type": "text", "text": prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}]
                else:
                    content_ai = prompt

                r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, 
                                 json={"model": model, "messages": [{"role": "system", "content": "Sei Rewire AI."}, {"role": "user", "content": content_ai}]})
                
                ans = r.json()['choices'][0]['message']['content']
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                st.rerun()
            except:
                st.error("Errore di connessione. Riprova.")
