import streamlit as st
from groq import Groq
import io
from fpdf import FPDF
from PyPDF2 import PdfReader

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business Brain", layout="wide")

# --- SISTEMA DI AUTOSAVE (Session State) ---
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

# --- 3. BARRA LATERALE (CONTROLLI E STORAGE) ---
with st.sidebar:
    st.header("⚙️ Pannello di Controllo")
    
    # Stato del salvataggio
    if st.session_state.current_template:
        st.success("✔️ Lavoro salvato in automatico")
    
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
            st.info(f"File pronto per l'analisi")
        except:
            st.error("Errore lettura file")

    st.divider()

    # ESPORTAZIONE
    if st.session_state.current_template:
        st.subheader("💾 Esporta e Archivia")
        
        # Tasto per "fissare" manualmente (opzionale visto l'autosave)
        if st.button("📌 CONFERMA SALVATAGGIO"):
            st.toast("Lavoro archiviato con successo!")

        st.download_button("📄 SCARICA TXT", st.session_state.current_template, "strategia_rewire.txt", use_container_width=True)
        try:
            pdf_data = crea_pdf_output(st.session_state.current_template)
            st.download_button("📕 SCARICA PDF", bytes(pdf_data), "report_rewire.pdf", "application/pdf", use_container_width=True)
        except:
            st.error("Errore PDF")

    st.divider()
    # RESET (Unico modo per cancellare il salvataggio automatico)
    if st.button("🗑️ CANCELLA TUTTO (Reset)", use_container_width=True):
        st.session_state.current_template = None
        st.session_state.last_prompt = ""
        st.rerun()

# --- 4. AREA CENTRALE ---
st.title("📈 RE-WIRE Business Brain")

# Il testo inserito viene salvato nello stato per non perderlo
c_prompt = st.text_area("Istruzioni o descrizione progetto:", 
                        value=st.session_state.last_prompt, 
                        height=200,
                        on_change=lambda: st.session_state.update({"last_prompt": c_prompt}))

if st.button("📝 GENERA ANALISI PROFESSIONALE", use_container_width=True):
    if c_prompt or contenuto_file:
        with st.spinner("Analisi in corso..."):
            try:
                api_key_groq = st.secrets["GROQ_API_KEY"]
                client = Groq(api_key=api_key_groq)
                
                # Trimmer per evitare l'errore 413 (Token limit)
                testo_limitato = contenuto_file[:15000] if len(contenuto_file) > 15000 else contenuto_file
                
                context = f"DATA:\n{testo_limitato}\n\nPROMPT:\n{c_prompt}"
                
                res = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Sei RE-WIRE AI, esperto strategist. Salva sempre il risultato in modo strutturato."},
                        {"role": "user", "content": context}
                    ],
                    model="llama-3.3-70b-versatile"
                )
                # SALVATAGGIO AUTOMATICO NELLO STATO
                st.session_state.current_template = res.choices[0].message.content
                st.session_state.last_prompt = c_prompt
                st.rerun() # Ricarica per aggiornare i tasti nella sidebar
                
            except Exception as e:
                st.error(f"Errore: {e}")
    else:
        st.warning("Inserisci dati per iniziare.")

st.divider()

# VISUALIZZAZIONE DEL LAVORO SALVATO
if st.session_state.current_template:
    st.subheader("📄 Risultato dell'Analisi (Salvataggio Attivo)")
    st.info(st.session_state.current_template)
