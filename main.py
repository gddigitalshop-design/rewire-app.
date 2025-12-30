import streamlit as st
from groq import Groq
import io
from fpdf import FPDF

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business", layout="wide")

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
    uploaded_file = st.file_uploader("Carica file .txt per l'analisi", type=["txt"])
    
    contenuto_file = ""
    if uploaded_file is not None:
        # Legge il contenuto del file caricato
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        contenuto_file = stringio.read()
        st.success(f"File '{uploaded_file.name}' pronto!")

    st.divider()

    # SEZIONE ESPORTAZIONE
    if st.session_state.current_template:
        st.subheader("💾 Esporta Risultato")
        
        st.download_button(
            label="📄 SCARICA TXT",
            data=st.session_state.current_template,
            file_name="strategia_rewire.txt",
            use_container_width=True
        )
        
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

    if st.button("🗑️ CANCELLA TUTTO", use_container_width=True):
        st.session_state.current_template = None
        st.rerun()

# --- 4. AREA DI LAVORO CENTRALE ---
st.title("📈 RE-WIRE Business Brain")
st.markdown("Analisi strategica integrata con i tuoi documenti.")

c_prompt = st.text_area(
    "Istruzioni aggiuntive o prompt:", 
    placeholder="Inserisci qui gli obiettivi o chiedi di analizzare il file caricato...",
    height=150
)

if st.button("📝 GENERA ANALISI PROFESSIONALE", use_container_width=True):
    if c_prompt or contenuto_file:
        with st.spinner("Analisi in corso..."):
            try:
                # Unisce le istruzioni dell'utente al contenuto del file
                prompt_completo = f"Contenuto del file caricato:\n{contenuto_file}\n\nIstruzioni utente:\n{c_prompt}"
                
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(
                    messages=[{
                        "role": "user", 
                        "content": f"Agisci come consulente senior. Usa queste informazioni per creare una strategia business: {prompt_completo}"
                    }],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.current_template = res.choices[0].message.content
            except:
                st.error("Errore di connessione API.")
    else:
        st.warning("Carica un file o scrivi qualcosa per iniziare.")

st.divider()

if st.session_state.current_template:
    st.subheader("📄 Risultato dell'Analisi")
    st.info(st.session_state.current_template)
