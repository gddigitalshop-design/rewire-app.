import streamlit as st
from groq import Groq
import io
from fpdf import FPDF
from PyPDF2 import PdfReader

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business Brain", layout="wide", page_icon="📈")

# --- 2. SISTEMA DI LOGIN (Per vendita/affitto) ---
def check_login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align: center;'>🔐 RE-WIRE Business Access</h1>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            user = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("ACCEDI AL SISTEMA", use_container_width=True):
                # Cambia queste credenziali prima della consegna al cliente
                if user == "admin" and password == "rewire2025":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Credenziali non valide. Riprova.")
        return False
    return True

# --- ESECUZIONE APP SE LOGGATO ---
if check_login():
    
    # Inizializzazione Session State (Autosave)
    if "current_template" not in st.session_state:
        st.session_state.current_template = None
    if "last_prompt" not in st.session_state:
        st.session_state.last_prompt = ""

    # --- 3. FUNZIONE ESPORTAZIONE PDF ---
    def crea_pdf_output(testo):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, txt="RE-WIRE BUSINESS REPORT", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("helvetica", size=11)
        # Pulizia caratteri non compatibili
        testo_safe = testo.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 8, txt=testo_safe)
        return pdf.output()

    # --- 4. BARRA LATERALE (PANNELLO DI CONTROLLO) ---
    with st.sidebar:
        st.title("⚙️ RE-WIRE Hub")
        st.write(f"Stato: **Connesso** [2025-12-30]")
        
        st.subheader("📋 Modelli Strategici")
        tipo_lavoro = st.selectbox(
            "Scegli un'attività:",
            [
                "Analisi Libera", 
                "Business Plan Executive (Riunioni)", 
                "Analisi SWOT Professionale", 
                "Piano Marketing Strategico",
                "Analisi dei Rischi Aziendali"
            ]
        )
        
        st.divider()
        
        st.subheader("📁 Documenti Fonte")
        uploaded_file = st.file_uploader("Carica PDF o TXT dal PC", type=["txt", "pdf"])
        
        contenuto_file = ""
        if uploaded_file:
            try:
                if uploaded_file.type == "application/pdf":
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        contenuto_file += page.extract_text() + "\n"
                else:
                    contenuto_file = uploaded_file.getvalue().decode("utf-8")
                st.success(f"✅ {uploaded_file.name} analizzato")
            except:
                st.error("Errore lettura file")

        st.divider()

        # ESPORTAZIONE (Appare solo se c'è un risultato)
        if st.session_state.current_template:
            st.subheader("💾 Esporta Analisi")
            st.download_button("📄 SCARICA TXT", st.session_state.current_template, "strategia_rewire.txt", use_container_width=True)
            try:
                pdf_data = crea_pdf_output(st.session_state.current_template)
                st.download_button("📕 SCARICA PDF", bytes(pdf_data), "report_rewire.pdf", "application/pdf", use_container_width=True)
            except:
                st.error("Errore creazione PDF")

        if st.button("🗑️ RESET SESSIONE", use_container_width=True):
