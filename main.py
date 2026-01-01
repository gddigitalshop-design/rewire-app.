import streamlit as st
import requests
import base64
import PyPDF2

# --- 1. CONFIGURAZIONE GRAFICA PREMIUM ---
st.set_page_config(page_title="REWIRE AI - Digital Factory", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    /* Sfondo scuro professionale */
    .stApp { background-color: #0b0e14; color: #e2e8f0; }
    
    /* Sidebar scura (Colonna Funzioni) */
    [data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    
    /* Titolo con Gradiente */
    .main-header {
        font-size: 2.8rem; font-weight: 800; text-align: center;
        background: linear-gradient(120deg, #a78bfa, #22d3ee);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 20px;
    }

    /* Stile messaggi Chat */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }

    /* Area Upload al centro della colonna */
    [data-testid="stFileUploadDropzone"] {
        background: rgba(34, 211, 238, 0.05) !important;
        border: 1px dashed #22d3ee !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. ACCESSO (LOGIN PRIMA DI TUTTO) ---
if "auth" not in st.session_state: st.session_state.auth = False
if "messages" not in st.session_state: st.session_state.messages = []

if not st.session_state.auth:
    _, col, _ = st.columns([1, 1.2, 1])
    with col:
        st.markdown("<p class='main-header'>⚡ REWIRE PRO</p>", unsafe_allow_html=True)
        pwd = st.text_input("Inserire Licenza Group 4.0 (2026):", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "rewire2026": #
                st.session_state.auth = True
                st.rerun()
            else: st.error("Codice non valido.")
    st.stop()

# --- 3. COLONNA SINISTRA (FUNZIONI E SALVATAGGIO) ---
with st.sidebar:
    st.markdown("## 🏭 STRUMENTI")
    st.info("Scegli il prodotto digitale da creare")
    
    # Template rapidi
    st.button("🥗 Foglio Dieta & Progressi")
    st.button("🌐 Traduzione & Correzione")
    st.button("📋 Analisi Contratti PDF")
    
    st.markdown("---")
    
    # TASTO SALVA LAVORO (Fondamentale per la vendita)
    if st.session_state.messages:
        full_work = "--- REPORT REWIRE AI ---\n\n"
        for m in st.session_state.messages:
            full_work += f"{m['role'].upper()}: {m['content']}\n\n"
        
        st.download_button(
            label="💾 SALVA FILE DI LAVORO",
            data=full_work,
            file_name="prodotto_digitale_rewire.txt",
            mime="text/plain"
        )
    
    if st.button("🗑️ Nuova Analisi"):
        st.session_state.messages = []
        st.rerun()

# --- 4. PAGINA CENTRALE (DUE COLONNE: PDF vs CHAT) ---
st.markdown("<p class='main-header'>REWIRE AI</p>", unsafe_allow_html=True)

col_file, col_chat = st.columns([1, 1.3])

with col_file:
    st.markdown("### 📄 Input Documento")
    uploaded_file = st.file_uploader("Trascina qui il file (PDF o Immagine)", type=["pdf", "png", "jpg", "jpeg"])
    
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            # Mostra il PDF direttamente nella pagina
            base64_pdf = base64.b64encode(uploaded_file.read()).decode('utf-8')
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        else:
            st.image(uploaded_file, use_column_width=True)

with col_chat:
    st.markdown("### 🛠️ Area di Produzione")
    
    # Visualizzazione messaggi esistenti
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    # Input della chat fluida
    if prompt := st.chat_input("Scrivi un comando o fai una domanda..."):
        # 1. Messaggio utente
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 2. Risposta Assistant
        with st.chat_message("assistant"):
            if prompt.lower() in ["ciao", "uè", "buongiorno"]:
                response = "Ciao! Sono Rewire. È un piacere vederti nell'area di produzione. Carica un documento a sinistra o dimmi cosa dobbiamo creare insieme oggi!"
            elif "dieta" in prompt.lower() or "tabella" in prompt.lower():
                response = """### 🥗 FOGLIO PROGRESSI DIETA
Ecco il tuo prodotto pronto da usare. Puoi copiarlo o scaricarlo:

| Data | Peso (kg) | Calorie | Note / Progressi |
| :--- | :--- | :--- | :--- |
| | | | |
| | | | |
| | | | |

*Consiglio: Usa il tasto 'Salva' a sinistra per tenere traccia di questo foglio.*"""
            else:
                response = f"Ricevuto. Sto elaborando la tua richiesta: **{prompt}**. Procedo con l'analisi del documento caricato e la creazione del risultato."

            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
