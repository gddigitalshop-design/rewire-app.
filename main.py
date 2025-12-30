import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader

# --- 1. SETTING ESTETICO ---
st.set_page_config(page_title="RE-WIRE | Business Intelligence", layout="wide", page_icon="🧠")

st.markdown("""
    <style>
    .report-box { 
        background-color: #1E1E1E; color: #FFFFFF; padding: 20px; 
        border-radius: 10px; border-left: 5px solid #FF4B4B; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MEMORIA ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "file_content" not in st.session_state:
    st.session_state.file_content = ""

# --- 3. SIDEBAR ---
with st.sidebar:
    st.title("🚀 RE-WIRE Hub")
    st.divider()
    st.subheader("📁 Carica Documento")
    uploaded_file = st.file_uploader("Trascina qui il file da analizzare", type=["txt", "pdf"])
    
    # LOGICA DI APERTURA E VISUALIZZAZIONE FILE
    if uploaded_file:
        raw_text = ""
        try:
            if uploaded_file.type == "application/pdf":
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    raw_text += page.extract_text() + "\n"
            else:
                raw_text = uploaded_file.getvalue().decode("utf-8")
            
            # Salviamo il contenuto nella sessione
            if st.session_state.file_content != raw_text:
                st.session_state.file_content = raw_text
                # Notifica automatica in chat che il file è aperto
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": f"✅ **File '{uploaded_file.name}' aperto con successo!** Ho letto il contenuto e sono pronto ad analizzarlo con te. Cosa vuoi sapere?"
                })
            st.success("File caricato e letto!")
        except Exception as e:
            st.error(f"Errore nell'apertura del file: {e}")

    if st.button("🧹 Pulisci tutto"):
        st.session_state.chat_history = []
        st.session_state.file_content = ""
        st.rerun()

# --- 4. AREA CHAT ---
st.title("🧠 RE-WIRE Business Brain")

# Visualizzazione Cronologia
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(f'<div class="report-box">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# Input Chat
prompt = st.chat_input("Chiedimi qualsiasi cosa sul file o proponi un'idea...")

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analizzando..."):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                # Inseriamo il contenuto del file nel contesto se presente
                context = ""
                if st.session_state.file_content:
                    context = f"\n\nCONTENUTO DEL FILE CARICATO:\n{st.session_state.file_content[:10000]}"

                msgs = [
                    {"role": "system", "content": "Sei RE-WIRE AI. Sei esperto nell'analizzare documenti e rispondere in modo fluido e professionale."},
                    {"role": "user", "content": f"{prompt}{context}"}
                ]

                res = client.chat.completions.create(messages=msgs, model="llama-3.3-70b-versatile")
                risposta = res.choices[0].message.content
                
                st.markdown(f'<div class="report-box">{risposta}</div>', unsafe_allow_html=True)
                st.session_state.chat_history.append({"role": "assistant", "content": risposta})
                
            except Exception as e:
                st.error(f"Errore: {e}")

