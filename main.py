import streamlit as st
from groq import Groq
import io
from fpdf import FPDF
from PyPDF2 import PdfReader

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business Brain", layout="wide")

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
    # Rimuove caratteri che fpdf non supporta
    testo_safe = testo.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=testo_safe)
    return pdf.output()

# --- 3. BARRA LATERALE (PANNELLO DI CONTROLLO) ---
with st.sidebar:
    st.header("⚙️ Pannello di Controllo")
    
    st.subheader("📁 Carica Documenti")
    uploaded_file = st.file_uploader(
        "Trascina qui TXT o PDF dal PC", 
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
            st.success(f"✅ {uploaded_file.name} pronto")
        except:
            st.error("Errore lettura file")

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

# --- 4. AREA CENTRALE ---
st.title("📈 RE-WIRE Business Brain")
st.markdown("Genera analisi professionali dai tuoi documenti.")

c_prompt = st.text_area(
    "Descrizione progetto o istruzioni aggiuntive:", 
    placeholder="Cosa vuoi analizzare o creare oggi?",
    height=200
)

if st.button("📝 GENERA ANALISI PROFESSIONALE", use_container_width=True):
    if c_prompt or contenuto_file:
        with st.spinner("L'AI sta elaborando i dati..."):
            try:
                # Verifica presenza chiave
                if "GROQ_API_KEY" not in st.secrets:
                    st.error("Manca la chiave GROQ_API_KEY nei Secrets di Streamlit!")
                    st.stop()
                
                full_context = f"DATI DAL FILE:\n{contenuto_file}\n\nRICHIESTA:\n{c_prompt}"
                
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Sei un consulente business senior. Crea un report strategico basato su: {full_context}"}],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.current_template = res.choices[0].message.content
            except Exception as e:
                st.error(f"Errore API: {str(e)}")
    else:
        st.warning("Inserisci un prompt o carica un file.")

st.divider()

if st.session_state.current_template:
    st.subheader("📄 Risultato dell'Analisi")
    st.info(st.session_state.current_template)
