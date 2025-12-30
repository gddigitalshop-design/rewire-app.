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
    # Pulizia per codifica latin-1
    testo_safe = testo.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=testo_safe)
    
    return pdf.output()

# --- 3. BARRA LATERALE (Solo comandi di sistema) ---
with st.sidebar:
    st.header("⚙️ Pannello")
    if st.button("🗑️ CANCELLA E RESETTA", use_container_width=True):
        st.session_state.current_template = None
        st.rerun()

# --- 4. AREA DI LAVORO CENTRALE ---
st.title("📈 RE-WIRE Business Brain")
st.markdown("Genera la tua strategia e scaricala subito.")

c_prompt = st.text_area(
    "Descrivi il tuo progetto:", 
    placeholder="Scrivi qui i dettagli del business...",
    height=150
)

if st.button("📝 GENERA STRATEGIA PROFESSIONALE", use_container_width=True):
    if c_prompt:
        with st.spinner("L'AI sta scrivendo..."):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Agisci come consulente senior. Crea un template e strategia per: {c_prompt}"}],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.current_template = res.choices[0].message.content
            except:
                st.error("Errore di connessione. Controlla la chiave API.")
    else:
        st.warning("Inserisci una descrizione.")

st.divider()

# --- 5. VISUALIZZAZIONE E TASTI DOWNLOAD (Tutti vicini al lavoro) ---
if st.session_state.current_template:
    # Visualizzazione del testo
    st.subheader("Risultato")
    st.info(st.session_state.current_template)
    
    # Tasti posizionati subito sotto il testo
    st.write("### 💾 Esporta il tuo lavoro")
    col_txt, col_pdf = st.columns(2)
    
    with col_txt:
        st.download_button(
            label="📄 SCARICA TXT",
            data=st.session_state.current_template,
            file_name="strategia_rewire.txt",
            use_container_width=True
        )
        
    with col_pdf:
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
            st.error("Errore durante la creazione del PDF.")
