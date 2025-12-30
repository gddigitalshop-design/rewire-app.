import streamlit as st
from groq import Groq
import io
from fpdf import FPDF
from PyPDF2 import PdfReader

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business", layout="wide")

if "current_template" not in st.session_state:
    st.session_state.current_template = None

# --- 2. FUNZIONE PDF (PER ESPORTARE) ---
def crea_pdf_output(testo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, txt="RE-WIRE BUSINESS REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("helvetica", size=12)
    testo_safe = testo.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=testo_safe)
    return pdf.output()

# --- 3. BARRA LATERALE (CONTROLLI E CARICAMENTO) ---
with st.sidebar:
    st.header("⚙️ Pannello di Controllo")
    
    st.subheader("📁 Carica Documenti")
    # Ora accettiamo sia TXT che PDF
    uploaded_file = st.file_uploader("Carica file .txt o .pdf dal PC", type=["txt", "pdf"])
    
    contenuto_file = ""
    if uploaded_file is not None:
        try:
            if uploaded_file.type == "application/pdf":
                # Legge il testo dal PDF caricato
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    contenuto_file += page.extract_text() + "\n"
            else:
                # Legge il file TXT
                contenuto_file = uploaded_file.getvalue().decode("utf-8")
            
            st.success(f"'{uploaded_file.name}' analizzato!")
        except Exception as e:
            st.error("Errore nella lettura del file.")

    st.divider()

    if st.session_state.current_template:
        st.subheader("💾 Esporta Risultato")
        st.download_button("📄 SCARICA TXT", st.session_state.current_template, "strategia.txt", use_container_width=True)
        try:
            pdf_data = crea_pdf_output(st.session_state.current_template)
            st.download_button("📕 SCARICA PDF", bytes(pdf_data), "report.pdf", "application/pdf", use_container_width=True)
        except:
            st.error("Errore PDF")

    st.divider()
    if st.button("🗑️ CANCELLA TUTTO", use_container_width=True):
        st.session_state.current_template = None
        st.rerun()

# --- 4. AREA DI LAVORO CENTRALE ---
st.title("📈 RE-WIRE Business Brain")
st.markdown("Analisi strategica basata sui tuoi file e prompt [2025-12-30].")

c_prompt = st.text_area(
    "Domande o istruzioni per l'AI:", 
    placeholder="Esempio: Riassumi questo bilancio e crea una strategia di crescita...",
    height=150
)

if st.button("📝 GENERA ANALISI PROFESSIONALE", use_container_width=True):
    if c_prompt or contenuto_file:
        with st.spinner("Analisi in corso..."):
            try:
                # Uniamo il testo estratto dal file alle istruzioni dell'utente
                testo_da_inviare = f"DATI DAL FILE:\n{contenuto_file}\n\nISTRUZIONI:\n{c_prompt}"
                
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(
                    messages=[{
                        "role": "user", 
                        "content": f"Sei un esperto business strategist. Usa questi dati per generare un report completo: {testo_da_inviare}"
                    }],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.current_template = res.choices[0].message.content
            except:
                st.error("Errore API Groq.")
    else:
        st.warning("Carica un file o scrivi qualcosa.")

st.divider()

if st.session_state.current_template:
    st.subheader("📄 Report Generato")
    st.info(st.session_state.current_template)
