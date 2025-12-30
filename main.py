import streamlit as st
from groq import Groq
import io
from fpdf import FPDF

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="RE-WIRE Business", layout="wide")

# Inizializzazione della sessione
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
    # Pulizia testo per codifica PDF
    testo_safe = testo.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=testo_safe)
    
    return pdf.output()

# --- 3. INTERFACCIA ---
st.title("📈 RE-WIRE Business Brain")
st.markdown("Generatore di strategie e template operativi.")

with st.sidebar:
    st.header("Comandi")
    # TASTO CANCELLA
    if st.button("🗑️ Svuota Tutto", use_container_width=True):
        st.session_state.current_template = None
        st.rerun()

# --- 4. INPUT E GENERAZIONE ---
c_prompt = st.text_area("Descrivi il tuo progetto o la sfida aziendale:", placeholder="Esempio: Strategia di marketing per un nuovo centro commerciale...")

if st.button("📝 CREA TEMPLATE & STRATEGIA", use_container_width=True):
    if c_prompt:
        with st.spinner("L'AI sta scrivendo la tua strategia..."):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": f"Agisci come un consulente business esperto. Crea un template e una strategia dettagliata per: {c_prompt}"}],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.current_template = res.choices[0].message.content
            except:
                st.error("Errore di connessione. Controlla la chiave API Groq nei Secrets.")
    else:
        st.warning("Inserisci una descrizione per procedere.")

# --- 5. VISUALIZZAZIONE E TASTI SALVA ---
st.divider()

if st.session_state.current_template:
    col_view, col_down = st.columns([3, 1])
    
    with col_view:
        st.subheader("Risultato Generato")
        st.info(st.session_state.current_template)
    
    with col_down:
        st.subheader("💾 Salva Lavoro")
        
        # SALVA TESTO
        st.download_button(
            label="📄 SCARICA TESTO (TXT)",
            data=st.session_state.current_template,
            file_name="strategia_rewire.txt",
            use_container_width=True
        )
        
        # SALVA PDF
        try:
            pdf_bytes = crea_pdf(st.session_state.current_template)
            st.download_button(
                label="📕 SCARICA REPORT (PDF)",
                data=bytes(pdf_bytes),
                file_name="report_rewire.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except:
            st.write("Generazione PDF...")
