import streamlit as st
from groq import Groq
import io
from fpdf import FPDF
from PyPDF2 import PdfReader

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business Brain", layout="wide", page_icon="📈")

# --- 2. LOGICA DI LOGIN ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_login():
    if not st.session_state.authenticated:
        st.markdown("<h1 style='text-align: center;'>🔐 RE-WIRE Business Access</h1>", unsafe_allow_html=True)
        
        # Centriamo il modulo di login
        col1, col2, col3 = st.columns([1,1,1])
        with col2:
            input_user = st.text_input("Username", key="user")
            input_pass = st.text_input("Password", type="password", key="pass")
            
            if st.button("ACCEDI AL SISTEMA", use_container_width=True):
                # CONTROLLO CREDENZIALI (Modifica qui per il cliente)
                if input_user == "admin" and input_pass == "12345":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Credenziali non valide. Riprova.")
        return False
    return True

# --- ESECUZIONE APP (Solo se autenticato) ---
if check_login():
    
    # Inizializzazione Session State per i dati
    if "current_template" not in st.session_state:
        st.session_state.current_template = None
    if "last_prompt" not in st.session_state:
        st.session_state.last_prompt = ""

    # Funzione per creare il PDF
    def crea_pdf_output(testo):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", "B", 16)
        pdf.cell(0, 10, txt="RE-WIRE BUSINESS REPORT", ln=True, align='C')
        pdf.ln(10)
        pdf.set_font("helvetica", size=11)
        testo_safe = testo.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 8, txt=testo_safe)
        return pdf.output()

    # --- 3. BARRA LATERALE ---
    with st.sidebar:
        st.title("⚙️ RE-WIRE Hub")
        st.write("Utente: **Amministratore**")
        
        tipo_lavoro = st.selectbox(
            "Modelli Strategici:",
            ["Analisi Libera", "Business Plan Executive (Riunioni)", "Analisi SWOT", "Piano Marketing"]
        )
        
        st.divider()
        uploaded_file = st.file_uploader("Carica PDF o TXT", type=["txt", "pdf"])
        
        contenuto_file = ""
        if uploaded_file:
            try:
                if uploaded_file.type == "application/pdf":
                    reader = PdfReader(uploaded_file)
                    for page in reader.pages:
                        contenuto_file += page.extract_text() + "\n"
                else:
                    contenuto_file = uploaded_file.getvalue().decode("utf-8")
                st.success("File caricato")
            except:
                st.error("Errore lettura file")

        st.divider()

        if st.session_state.current_template:
            st.download_button("📄 TXT", st.session_state.current_template, "report.txt", use_container_width=True)
            try:
                pdf_data = crea_pdf_output(st.session_state.current_template)
                st.download_button("📕 PDF", bytes(pdf_data), "report.pdf", "application/pdf", use_container_width=True)
            except:
                st.error("Errore PDF")

        if st.button("🗑️ RESET SESSIONE", use_container_width=True):
            st.session_state.current_template = None
            st.session_state.last_prompt = ""
            st.rerun()
            
        if st.button("🚪 LOGOUT", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    # --- 4. AREA CENTRALE ---
    st.title("📈 RE-WIRE Business Brain")
    
    c_prompt = st.text_area("Descrizione o Istruzioni:", value=st.session_state.last_prompt, height=150)

    if st.button("🚀 AVVIA ELABORAZIONE", use_container_width=True):
        if c_prompt or contenuto_file:
            with st.spinner("Analisi in corso..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    context = f"Tipo: {tipo_lavoro}\nFile: {contenuto_file[:10000]}\nInput: {c_prompt}"
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": context}],
                        model="llama-3.3-70b-versatile"
                    )
                    st.session_state.current_template = res.choices[0].message.content
                    st.session_state.last_prompt = c_prompt
                    st.rerun()
                except Exception as e:
                    st.error(f"Errore API: {e}")
        else:
            st.warning("Inserisci dati per procedere.")

    if st.session_state.current_template:
        st.markdown(
            f"""
            <div style="background-color: #1E1E1E; color: #FFFFFF; padding: 25px; border-radius: 12px; border: 1px solid #444444; white-space: pre-wrap; max-height: 500px; overflow-y: auto;">
            {st.session_state.current_template}
            </div>
            """, 
            unsafe_allow_html=True
        )
