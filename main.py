import streamlit as st
from groq import Groq
import io
from fpdf import FPDF
from PyPDF2 import PdfReader

# --- 1. CONFIGURAZIONE ESTETICA ---
st.set_page_config(page_title="RE-WIRE Business Brain", layout="wide", page_icon="🧠")

# CSS per rendere l'interfaccia meno "fredda"
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .stTextArea textarea { background-color: #161B22; color: white; border-radius: 10px; }
    .stButton button { border-radius: 20px; transition: 0.3s; }
    .stButton button:hover { background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIONE MEMORIA (Session State) ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_template" not in st.session_state:
    st.session_state.current_template = None

# Funzione per esportare in PDF
def crea_pdf_output(testo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, txt="RE-WIRE BUSINESS STRATEGY", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("helvetica", size=11)
    pdf.multi_cell(0, 8, txt=testo.encode('latin-1', 'ignore').decode('latin-1'))
    return pdf.output()

# --- 3. BARRA LATERALE (Minimalista e Utile) ---
with st.sidebar:
    st.title("🚀 RE-WIRE Hub")
    st.markdown("---")
    
    st.subheader("📁 I tuoi documenti")
    uploaded_file = st.file_uploader("Trascina un PDF o un TXT", type=["txt", "pdf"])
    
    contenuto_file = ""
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            reader = PdfReader(uploaded_file)
            for page in reader.pages: contenuto_file += page.extract_text() + "\n"
        else:
            contenuto_file = uploaded_file.getvalue().decode("utf-8")
        st.success("Documento pronto!")

    st.markdown("---")
    if st.session_state.current_template:
        st.subheader("💾 Esporta lavoro")
        pdf_data = crea_pdf_output(st.session_state.current_template)
        st.download_button("📕 SCARICA REPORT PDF", bytes(pdf_data), "strategia_rewire.pdf", "application/pdf", use_container_width=True)

    if st.button("🧹 PULISCI CONVERSAZIONE", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.current_template = None
        st.rerun()

# --- 4. AREA CENTRALE (Il cuore dell'AI) ---
st.title("🧠 Benvenuto in RE-WIRE Business")
st.write("Ciao! Sono il tuo braccio destro strategico. Come posso aiutarti a far crescere il tuo progetto oggi?")

# Visualizziamo la cronologia dei messaggi per renderla una "Chat" vera
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input dell'utente
prompt = st.chat_input("Scrivi qui la tua idea o chiedi un'analisi...")

if prompt:
    # Aggiungiamo il messaggio dell'utente alla storia
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Sto elaborando una visione per te..."):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                # Istruzioni "Umane"
                system_prompt = (
                    "Sei RE-WIRE AI, un partner strategico brillante, carismatico e pratico. "
                    "Non rispondere come un modulo burocratico. Parla in modo fluido, dai consigli "
                    "azionabili e sii creativo. Usa grassetti e liste per rendere il testo leggibile."
                )
                
                # Costruiamo il contesto con la storia della chat
                messages = [{"role": "system", "content": system_prompt}]
                messages.extend(st.session_state.chat_history[-5:]) # Ricorda gli ultimi 5 messaggi
                
                # Se c'è un file, lo iniettiamo nell'ultimo messaggio
                if contenuto_file:
                    messages[-1]["content"] += f"\n\n[Analizza anche questi dati dal file: {contenuto_file[:5000]}]"

                res = client.chat.completions.create(
                    messages=messages,
                    model="llama-3.3-70b-versatile"
                )
                
                risposta = res.choices[0].message.content
                st.markdown(risposta)
                
                # Salviamo la risposta e il template
                st.session_state.chat_history.append({"role": "assistant", "content": risposta})
                st.session_state.current_template = risposta
                
            except Exception as e:
                st.error(f"Ehi, qualcosa è andato storto: {e}")
