import streamlit as st
from groq import Groq
import io
from fpdf import FPDF
from PyPDF2 import PdfReader

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business Brain", layout="wide")

if "current_template" not in st.session_state:
    st.session_state.current_template = None

# --- 2. FUNZIONE PDF ---
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

# --- 3. BARRA LATERALE ---
with st.sidebar:
    st.header("⚙️ Pannello di Controllo")
    
    st.subheader("📁 Carica Documenti")
    uploaded_file = st.file_uploader("Carica file .txt o .pdf", type=["txt", "pdf"])
    
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
            st.error("Errore lettura file")

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

# --- 4. AREA CENTRALE ---
st.title("📈 RE-WIRE Business Brain")

c_prompt = st.text_area("Istruzioni o descrizione progetto:", height=200)

if st.button("📝 GENERA ANALISI PROFESSIONALE", use_container_width=True):
    if c_prompt or contenuto_file:
        with st.spinner("Analisi in corso..."):
            try:
                # Recupero sicuro della chiave dai Secrets
                api_key_groq = st.secrets["GROQ_API_KEY"]
                client = Groq(api_key=api_key_groq)
                
                context = f"FILE DATA:\n{contenuto_file}\n\nUSER PROMPT:\n{c_prompt}"
                
                res = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Sei RE-WIRE AI, un consulente business senior."},
                        {"role": "user", "content": context}
                    ],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.current_template = res.choices[0].message.content
            except Exception as e:
                st.error(f"Errore: {e}")
    else:
        st.warning("Inserisci del testo o carica un file.")

st.divider()

if st.session_state.current_template:
    st.subheader("📄 Risultato dell'Analisi")
    st.info(st.session_state.current_template)
