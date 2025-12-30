import streamlit as st
from groq import Groq
import io
from fpdf import FPDF
from PyPDF2 import PdfReader

# --- 1. CONFIGURAZIONE PAGINA (Obbligatoria come prima riga) ---
st.set_page_config(page_title="RE-WIRE Business Brain", layout="wide")

# Inizializzazione della memoria della sessione
if "current_template" not in st.session_state:
    st.session_state.current_template = None

# --- 2. FUNZIONE ESPORTAZIONE PDF ---
def crea_pdf_output(testo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, txt="RE-WIRE BUSINESS REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("helvetica", size=12)
    # Rimuove caratteri speciali per evitare crash del PDF
    testo_safe = testo.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=testo_safe)
    return pdf.output()

# --- 3. BARRA LATERALE (CONTROLLI) ---
with st.sidebar:
    st.header("⚙️ Pannello di Controllo")
    
    st.subheader("📁 Carica Documenti")
    uploaded_file = st.file_uploader(
        "Carica file .txt o .pdf dal PC", 
        type=["txt", "pdf"]
    )
    
    contenuto_file = ""
    if uploaded_file is not None:
        try:
            if uploaded_file.type == "application/pdf":
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    contenuto_file += page.extract_text() + "\n"
            else:
                contenuto_file = uploaded_file.getvalue().decode("utf-8")
            st.success(f"✅ {uploaded_file.name} caricato")
        except:
            st.error("Errore nella lettura del file")

    st.divider()

    # TASTI DOWNLOAD (appaiono solo se c'è un risultato)
    if st.session_state.current_template:
        st.subheader("💾 Esporta Risultato")
        st.download_button(
            label="📄 SCARICA TXT",
            data=st.session_state.current_template,
            file_name="strategia_rewire.txt",
            use_container_width=True
        )
        try:
            pdf_data = crea_pdf_output(st.session_state.current_template)
            st.download_button(
                label="📕 SCARICA PDF",
                data=bytes(pdf_data),
                file_name="report_rewire.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except:
            st.error("Errore creazione PDF")

    st.divider()
    if st.button("🗑️ CANCELLA TUTTO", use_container_width=True):
        st.session_state.current_template = None
        st.rerun()

# --- 4. AREA CENTRALE DI LAVORO ---
st.title("📈 RE-WIRE Business Brain")
st.markdown("Genera analisi professionali dai tuoi documenti e idee [2025-12-30].")

c_prompt = st.text_area(
    "Descrizione progetto o istruzioni aggiuntive:", 
    placeholder="Scrivi qui o chiedi di analizzare il file caricato...",
    height=200
)

# IL TASTO GENERATORE
if st.button("📝 GENERA ANALISI PROFESSIONALE", use_container_width=True):
    if c_prompt or contenuto_file:
        with st.spinner("RE-WIRE AI sta elaborando i dati..."):
            try:
                # Prompt di sistema per evitare risposte robotiche o "allucinazioni" finanziarie
                istruzioni_sistema = (
                    "Sei RE-WIRE Business AI. Se l'utente ti saluta, rispondi cordialmente. "
                    "Se ricevi dati o richieste business, agisci come un consulente senior "
                    "e crea una strategia dettagliata, realistica e professionale."
                )
                
                full_context = f"DATI DAL FILE:\n{contenuto_file}\n\nRICHIESTA UTENTE:\n{c_prompt}"
                
                # Connessione a Groq tramite i Secrets
                client = Groq(api_key=st.secrets["GROQ_
