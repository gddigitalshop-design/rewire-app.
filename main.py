import streamlit as st
from groq import Groq
import io
from fpdf import FPDF
from PyPDF2 import PdfReader

# --- 1. CONFIGURAZIONE ESTETICA E TITOLO ---
st.set_page_config(page_title="RE-WIRE | Business Intelligence", layout="wide", page_icon="🧠")

st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; }
    .report-box { 
        background-color: #1E1E1E; 
        color: #FFFFFF; 
        padding: 25px; 
        border-radius: 15px; 
        border-left: 5px solid #FF4B4B; 
        line-height: 1.6;
        margin-bottom: 20px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.3);
    }
    .save-status { color: #00FF00; font-size: 0.8rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MEMORIA PERSISTENTE (Salvataggio Automatico) ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = None  # Qui salviamo l'ultimo lavoro "fisso"

def crea_pdf_output(testo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, txt="RE-WIRE STRATEGIC REPORT", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("helvetica", size=11)
    # Pulizia caratteri per PDF
    testo_safe = testo.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 8, txt=testo_safe)
    return pdf.output()

# --- 3. BARRA LATERALE (La tua Cassaforte) ---
with st.sidebar:
    st.title("🚀 RE-WIRE Hub")
    
    # Indicatore di Salvataggio
    if st.session_state.last_analysis:
        st.markdown('<p class="save-status">● LAVORO SALVATO IN AUTOMATICO</p>', unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📁 Analisi Documenti")
    uploaded_file = st.file_uploader("Carica PDF o TXT", type=["txt", "pdf"])
    
    file_text = ""
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages: file_text += page.extract_text() + "\n"
        else:
            file_text = uploaded_file.getvalue().decode("utf-8")
        st.success("File pronto!")

    st.divider()
    
    # TASTI DI SALVATAGGIO (appaiono solo se c'è un lavoro)
    if st.session_state.last_analysis:
        st.subheader("💾 Esporta Analisi")
        st.download_button(
            label="📄 SCARICA TXT",
            data=st.session_state.last_analysis,
            file_name="strategia_rewire.txt",
            use_container_width=True
        )
        
        pdf_bytes = crea_pdf_output(st.session_state.last_analysis)
        st.download_button(
            label="📕 SCARICA PDF",
            data=bytes(pdf_bytes),
            file_name="report_rewire.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        if st.button("🗑️ CANCELLA E RICOMINCIA", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.last_analysis = None
            st.rerun()

# --- 4. AREA CHAT ---
st.title("🧠 RE-WIRE Business Brain")
st.write("Ogni risposta viene salvata automaticamente nella tua barra laterale.")

# Mostra i messaggi precedenti
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(f'<div class="report-box">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# Input Chat
prompt = st.chat_input("Di cosa abbiamo bisogno per il progetto?")

if prompt:
    # Salva input utente
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Generando strategia e salvando i dati..."):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                # System Prompt: Umano + Professionale
                sys_msg = (
                    "Sei RE-WIRE AI. Rispondi in modo fluido ed empatico. "
                    "Organizza il contenuto con titoli, icone e liste. "
                    "Ogni tua risposta deve essere un documento pronto all'uso."
                )
                
                msgs = [{"role": "system", "content": sys_msg}]
                # Memoria degli ultimi 5 scambi
                msgs.extend(st.session_state.chat_history[-5:])
                
                if file_text:
                    msgs[-1]["content"] += f"\n\n[Analizza anche questo file: {file_text[:7000]}]"

                res = client.chat.completions.create(messages=msgs, model="llama-3.3-70b-versatile")
                risposta = res.choices[0].message.content
                
                # Visualizzazione Premium
                st.markdown(f'<div class="report-box">{risposta}</div>', unsafe_allow_html=True)
                
                # --- IL PUNTO CHIAVE: SALVATAGGIO AUTOMATICO ---
                st.session_state.chat_history.append({"role": "assistant", "content": risposta})
                st.session_state.last_analysis = risposta  # Sovrascrive e salva l'ultima versione
                st.rerun() # Ricarica per aggiornare i tasti download nella sidebar
                
            except Exception as e:
                st.error(f"Errore: {e}")
