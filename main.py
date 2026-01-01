import streamlit as st
import groq
import PyPDF2

# --- 1. LOGIN E SICUREZZA ---
def check_password():
    def password_entered():
        # Verifica se l'utente e la password esistono nei Secrets
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<div style='text-align:center;margin-top:100px;'><h1 style='color:#ff4b4b;font-size:4rem;'>🧠 REWIRE AI</h1><p style='color:#888;letter-spacing:5px;'>FACTORY EDITION</p></div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.text_input("Username", on_change=password_entered, key="username")
            st.text_input("Password", type="password", on_change=password_entered, key="password")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("❌ Credenziali errate")
        return False
    return True

if check_password():
    # --- 2. CONFIGURAZIONE PAGINA (Solo dopo il login) ---
    st.set_page_config(page_title="REWIRE AI - Factory", layout="wide")

    # --- CSS ESTETICO ---
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: #ffffff; }
        [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #ff4b4b33; }
        div.stButton > button { border-radius: 5px; height: 3em; width: 100%; transition: all 0.3s; }
        div.stButton > button:hover { border-color: #ff4b4b; color: #ff4b4b; }
        </style>
    """, unsafe_allow_html=True)

    # --- INIZIALIZZAZIONE ---
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "active_prompt" not in st.session_state:
        st.session_state.active_prompt = None

    # --- FUNZIONE CERVELLO AI (CON MEMORIA) ---
    def call_rewire_brain(query, context=""):
        try:
            client = groq.Client(api_key=st.secrets["GROQ_API_KEY"])
            history = []
            if context:
                history.append({"role": "system", "content": f"Usa questo documento: {context}"})
            for m in st.session_state.messages:
                history.append({"role": m["role"], "content": m["content"]})
            history.append({"role": "user", "content": query})
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=history,
                temperature=0.5,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Errore: {str(e)}"

    # --- SIDEBAR OPERATIVA ---
    with st.sidebar:
        st.markdown("### 🛠️ STRUMENTI")
        uploaded_file = st.file_uploader("📁 CARICA DOCUMENTO", type=["pdf", "png", "jpg", "jpeg"])
        pdf_text = ""
        if uploaded_file:
            if uploaded_file.type == "application/pdf":
                reader = PyPDF2.PdfReader(uploaded_file)
                pdf_text = "\n".join([p.extract_text() for p in reader.pages if p.extract_text()])
                st.success("✅ PDF Caricato")
            else:
                st.image(uploaded_file, use_container_width=True)

        st.markdown("---")
        st.markdown("### ⚡ PROMPT RAPIDI")
        if st.button("🥗 CREA DIETA"):
            st.session_state.active_prompt = "Crea una tabella dieta basata sui miei dati."
        if st.button("🌐 TRADUZIONE"):
            st.session_state.active_prompt = "Traduci professionalmente il testo."

        st.markdown("---")
        st.markdown("### 💾 GESTIONE")
        ultimo_lavoro = next((m['content'] for m in reversed(st.session_state.messages) if m['role'] == "assistant"), "Nessun dato.")
        st.download_button("💾 SALVA RISULTATO", data=ultimo_lavoro, file_name="rewire_output.txt", use_container_width=True)
        
        if st.button("🗑️ RESET SISTEMA"):
            st.session_state.messages = []
            st.rerun()

    # --- AREA CENTRALE ---
    if not st.session_state.messages:
        st.markdown("""
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh;">
                <div style="text-align: center; border: 3px solid #ff4b4b; padding: 50px; border-radius: 30px; background-color: rgba(255, 75, 75, 0.03);">
                    <h1 style="color: #ff4b4b; font-size: 5.5rem; font-weight: 900; margin-bottom: 0px;">🧠 REWIRE AI</h1>
                    <p style="color: #ffffff; font-size: 1.5rem; letter-spacing: 10px;">FACTORY EDITION</p>
                    <div style="margin-top: 20px;"><span style="color: #00ff00;">●</span> <span style="color: #888;">SISTEMA PRONTO</span></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='color:#ff4b4b;'>🧠 REWIRE AI</h2>", unsafe_allow_html=True)
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])

    # --- LOGICA CHAT ---
    user_query = st.chat_input("Invia un comando...")
    prompt_to_send = user_query or st.session_state.active_prompt

    if prompt_to_send:
        st.session_state.messages.append({"role": "user", "content": prompt_to_send})
        st.session_state.active_prompt = None
        with st.spinner("⚡ Elaborazione..."):
            risposta = call_rewire_brain(prompt_to_send, pdf_text)
            st.session_state.messages.append({"role": "assistant", "content": risposta})
        st.rerun()
