import streamlit as st
from groq import Groq
import io
from fpdf import FPDF
from PyPDF2 import PdfReader

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business Brain", layout="wide")

if "current_template" not in st.session_state:
    st.session_state.current_template = None
if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

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

# --- 3. BARRA LATERALE (TEMPLATE E CONTROLLI) ---
with st.sidebar:
    st.header("⚙️ Pannello di Controllo")
    
    # SEZIONE TEMPLATE
    st.subheader("📋 Modelli di Lavoro")
    tipo_lavoro = st.selectbox(
        "Scegli un Template:",
        [
            "Analisi Libera", 
            "Analisi SWOT Professionale", 
            "Business Plan Executive", 
            "Piano Marketing Strategico",
            "Analisi dei Rischi Aziendali"
        ]
    )
    
    # Descrizione automatica in base al template
    dict_template = {
        "Analisi SWOT Professionale": "Analizza il progetto evidenziando Punti di Forza, Debolezze, Opportunità e Minacce.",
        "Business Plan Executive": "Crea una sintesi del modello di business, target clienti e strategia di monetizzazione.",
        "Piano Marketing Strategico": "Definisci canali di vendita, posizionamento brand e strategia contenuti.",
        "Analisi dei Rischi Aziendali": "Identifica potenziali criticità operative, finanziarie e di mercato."
    }
    
    st.divider()
    
    st.subheader("📁 Carica Documenti")
    uploaded_file = st.file_uploader("Carica TXT o PDF", type=["txt", "pdf"])
    
    contenuto_file = ""
    if uploaded_file is not None:
        try:
            if uploaded_file.type == "application/pdf":
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    contenuto_file += page.extract_text() + "\n"
            else:
                contenuto_file = uploaded_file.getvalue().decode("utf-8")
            st.success("File caricato correttamente")
        except:
            st.error("Errore lettura file")

    st.divider()

    if st.session_state.current_template:
        st.subheader("💾 Esporta")
        st.download_button("📄 SCARICA TXT", st.session_state.current_template, "strategia.txt", use_container_width=True)
        try:
            pdf_data = crea_pdf_output(st.session_state.current_template)
            st.download_button("📕 SCARICA PDF", bytes(pdf_data), "report.pdf", "application/pdf", use_container_width=True)
        except:
            st.error("Errore PDF")

    if st.button("🗑️ RESET TOTALE", use_container_width=True):
        st.session_state.current_template = None
        st.session_state.last_prompt = ""
        st.rerun()

# --- 4. AREA CENTRALE ---
st.title("📈 RE-WIRE Business Brain")

# Se l'utente sceglie un template, lo suggeriamo nel testo
placeholder_text = dict_template.get(tipo_lavoro, "Descrivi qui il tuo progetto...")

c_prompt = st.text_area("Dettagli del Progetto:", value=st.session_state.last_prompt, placeholder=placeholder_text, height=150)

if st.button("📝 AVVIA ANALISI CON TEMPLATE", use_container_width=True):
    if c_prompt or contenuto_file:
        with st.spinner(f"Generazione {tipo_lavoro} in corso..."):
            try:
                api_key_groq = st.secrets["GROQ_API_KEY"]
                client = Groq(api_key=api_key_groq)
                
                # Trimmer per token
                testo_limitato = contenuto_file[:15000] if len(contenuto_file) > 15000 else contenuto_file
                
                # Istruzione specifica in base al Template scelto
                istruzioni_template = f"Agisci come consulente senior. Esegui un: {tipo_lavoro}."
                context = f"DATI FILE:\n{testo_limitato}\n\nINPUT UTENTE:\n{c_prompt}"
                
                res = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": istruzioni_template},
                        {"role": "user", "content": context}
                    ],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.current_template = res.choices[0].message.content
                st.session_state.last_prompt = c_prompt
                st.rerun()
            except Exception as e:
                st.error(f"Errore: {e}")

st.divider()

# --- 5. RISULTATO CON SFONDO NERO E SCRITTA BIANCA ---
if st.session_state.current_template:
    st.subheader(f"📄 Risultato: {tipo_lavoro}")
    st.markdown(
        f"""
        <div style="
            background-color: #1E1E1E; 
            color: #FFFFFF; 
            padding: 25px; 
            border-radius: 12px; 
            border: 1px solid #444444;
            line-height: 1.6;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            white-space: pre-wrap;
            box-shadow: 2px 2px 15px rgba(0,0,0,0.5);
        ">
        {st.session_state.current_template}
        </div>
        """, 
        unsafe_allow_html=True
    )
