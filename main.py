import streamlit as st
from groq import Groq
import io
from fpdf import FPDF

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business", layout="wide")

# Inizializzazione sessione
if "current_template" not in st.session_state:
    st.session_state.current_template = None

# --- 2. FUNZIONE PDF ---
def crea_pdf(testo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, txt="RE-WIRE BUSINESS REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("helvetica", size=12)
    testo_safe = testo.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=testo_safe)
    return pdf.output()

# --- 3. BARRA LATERALE (TUTTI I COMANDI) ---
with st.sidebar:
    st.header("⚙️ Pannello di Controllo")
    
    # SEZIONE CARICAMENTO
    st.subheader("📁 Carica Documenti")
    uploaded_file = st.file_uploader("Carica file dal PC per l'analisi", type=["txt", "pdf", "docx"])
    if uploaded_file is not None:
        st.success(f"File '{uploaded_file.name}' caricato!")

    st.divider()

    # SEZIONE ESPORTAZIONE (Visibile solo se c'è un risultato)
    if st.session_state.current_template:
        st.subheader("💾 Esporta Risultato")
        
        # Download TXT
        st.download_button(
            label="📄 SCARICA TXT",
            data=st.session_state.current_template,
            file_name="strategia_rewire.txt",
            use_container_width=True
        )
        
        # Download PDF
        try:
            pdf_data = crea_pdf(st.session_state.current_template)
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

    # TASTO RESET
    if st.button("🗑️ CANCELLA TUTTO", use_container_width=True):
        st.session_state.current_template = None
        st.rerun()

# --- 4. AREA DI LAVORO CENTRALE ---
st.title("📈 RE-WIRE Business Brain")
st.markdown("Inserisci i dati o usa i file caricati per generare la tua strategia.")

c_prompt = st.text_area(
    "Descrizione progetto o istruzioni aggiuntive:", 
    placeholder="Scrivi qui i dettagli del business o cosa vuoi analizzare...",
    height=200
)

if st.button("📝 GENERA STRATEGIA PROFESSIONALE", use_container_width=True):
    if c_prompt:
        with st.spinner("L'AI sta analizzando i dati e scrivendo..."):
            try:
                # Nota: In una versione avanzata potremmo leggere il contenuto di 'uploaded_file' 
                # e aggiungerlo al prompt inviato a Groq.
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Agisci come consulente senior. Crea un report e strategia per: {c_prompt}"}],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.current_template = res.choices[0].message.content
            except:
                st.error("Errore di connessione API.")
    else:
        st.warning("Inserisci una descrizione.")

st.divider()

if st.session_state.current_template:
    st.subheader("📄 Risultato dell'Analisi")
    st.info(st.session_state.current_template)
