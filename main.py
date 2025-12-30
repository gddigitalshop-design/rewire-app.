import streamlit as st
from groq import Groq
import io
from fpdf import FPDF

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business", layout="wide")

# Inizializzazione sessione per mantenere i risultati a video
if "current_template" not in st.session_state:
    st.session_state.current_template = None

# --- 2. FUNZIONE GENERAZIONE PDF ---
def crea_pdf(testo):
    pdf = FPDF()
    pdf.add_page()
    # Intestazione
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, txt="RE-WIRE BUSINESS REPORT", ln=True, align='C')
    pdf.ln(10)
    
    # Corpo del testo
    pdf.set_font("helvetica", size=12)
    # Pulizia caratteri non compatibili con PDF standard
    testo_safe = testo.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=testo_safe)
    
    return pdf.output()

# --- 3. INTERFACCIA UTENTE ---
st.title("📈 RE-WIRE Business Brain")
st.markdown("Generatore professionale di strategie aziendali e template operativi.")

# Sidebar per la gestione della sessione
with st.sidebar:
    st.header("⚙️ Gestione")
    if st.button("🗑️ Svuota Tutto", use_container_width=True):
        st.session_state.current_template = None
        st.rerun()

# --- 4. INPUT E MOTORE AI ---
c_prompt = st.text_area(
    "Descrivi l'idea di business o il problema da risolvere:", 
    placeholder="Esempio: Sviluppare un piano di marketing per un'app di consulenza...",
    height=150
)

if st.button("📝 CREA STRATEGIA & TEMPLATE", use_container_width=True):
    if c_prompt:
        with st.spinner("L'AI sta elaborando la tua strategia..."):
            try:
                # Recupera la chiave dai Secrets di Streamlit
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(
                    messages=[{
                        "role": "user", 
                        "content": f"Agisci come un consulente business senior. Crea un template operativo e una strategia dettagliata per: {c_prompt}"
                    }],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.current_template = res.choices[0].message.content
            except Exception as e:
                st.error("Errore di connessione con il motore AI. Verifica la chiave API.")
    else:
        st.warning("Per favore, inserisci una descrizione prima di generare.")

# --- 5. VISUALIZZAZIONE E ESPORTAZIONE ---
st.divider()

if st.session_state.current_template:
    col_visual, col_actions = st.columns([3, 1])
    
    with col_visual:
        st.subheader("Risultato Strategico")
        st.info(st.session_state.current_template)
    
    with col_actions:
        st.subheader("💾 Esporta")
        
        # Download in formato TXT
        st.download_button(
            label="📄 Scarica Testo (TXT)",
            data=st.session_state.current_template,
            file_name="strategia_rewire.txt",
            use_container_width=True
        )
        
        # Download in formato PDF
        try:
            pdf_data = crea_pdf(st.session_state.current_template)
            st.download_button(
                label="📕 Scarica Report (PDF)",
                data=bytes(pdf_data),
                file_name="report_rewire.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except:
            st.write("Generazione PDF in corso...")
