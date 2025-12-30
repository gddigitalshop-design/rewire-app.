import streamlit as st
from groq import Groq
import io
from fpdf import FPDF
from PyPDF2 import PdfReader

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="RE-WIRE Business", layout="wide")

if "current_template" not in st.session_state:
    st.session_state.current_template = None

# --- 2. FUNZIONE PDF (ESPORTAZIONE) ---
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

# --- 3. BARRA LATERALE (PANNELLO DI CONTROLLO) ---
with st.sidebar:
    st.header("⚙️ Pannello di Controllo")
    
    # CARICAMENTO DOCUMENTI
    st.subheader("📁 Carica Documenti")
    uploaded_file = st.file_uploader(
        "Trascina qui i tuoi file (TXT o PDF)", 
        type=["txt", "pdf"],
        help="Limite 200MB per file"
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

    # TASTI DI ESPORTAZIONE (SPOSTATI QUI)
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

    # RESET
    if st.button("🗑️ CANCELLA TUTTO", use_container_width=True):
        st.session_state.current_template = None
        st.rerun()

# --- 4. AREA CENTRALE ---
st.title("📈 RE-WIRE Business Brain")
st.markdown("Genera analisi professionali dai tuoi documenti [2025-12-30].")

c_prompt = st.text_area(
    "Descrizione progetto o istruzioni aggiuntive:", 
    placeholder="Inserisci qui i dettagli o chiedi un'analisi del file caricato...",
    height=200
)

if st.button("📝 GENERA ANALISI PROFESSIONALE", use_container_width=True):
    if c_prompt or contenuto_file:
        with st.spinner("Analisi in corso..."):
            try:
                # Combinazione dati file + prompt utente
                full_context = f"DATI DOCUMENTO:\n{contenuto_file}\n\nRICHIESTA UTENTE:\n{c_prompt}"
                
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Agisci come consulente senior. Crea una strategia basata su: {full_context}"}],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.current_template = res.choices[0].message.content
            except:
                st.error("Errore API Groq. Verifica i Secrets.")
    else:
        st.warning("Carica un documento o scrivi un prompt per iniziare.")

st.divider()

if st.session_state.current_template:
    st.subheader("📄 Risultato dell'Analisi")
    st.info(st.session_state.current_template)
