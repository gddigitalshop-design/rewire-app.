import streamlit as st
import requests
import fitz
import io

# --- CONFIGURAZIONE ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.1-8b-instant"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI 2026", layout="wide", page_icon="✨")

# --- STILE GRAFICO (Rendiamola bella!) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { border-radius: 20px; border: 1px solid #4CAF50; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN DOLCE ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🌟 Benvenuto in RE-WIRE")
    st.subheader("Il tuo assistente intelligente è quasi pronto.")
    pwd = st.text_input("Inserisci la tua chiave d'accesso per iniziare:", type="password")
    if st.button("SBLOCCA LA MAGIA ✨"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Ops! La chiave sembra non essere corretta. Riprova! 😊")
    st.stop()

# --- INIZIALIZZAZIONE ---
if "messages" not in st.session_state: st.session_state.messages = []
if "doc_text" not in st.session_state: st.session_state.doc_text = ""
if "file_processed" not in st.session_state: st.session_state.file_processed = False

# --- INTERFACCIA PRINCIPALE ---
st.title("🧠 RE-WIRE: Analizziamo insieme!")
st.write("Ciao! Sono pronto ad aiutarti con i tuoi documenti e le tue foto. Cosa studiamo oggi?")

with st.sidebar:
    st.header("📁 Area Caricamento")
    file = st.file_uploader("Trascina qui un PDF o una Foto!", type=["pdf", "jpg", "jpeg", "png"])
    
    if file:
        if not st.session_state.file_processed:
            with st.spinner("Sto leggendo con attenzione... 📖"):
                if file.type == "application/pdf":
                    doc = fitz.open(stream=file.read(), filetype="pdf")
                    st.session_state.doc_text = "".join([p.get_text() for p in doc])[:4000]
                else:
                    st.session_state.doc_text = f"[Immagine: {file.name}]"
                
                # Messaggio di benvenuto automatico
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"Ho ricevuto il file **{file.name}**! ✨ Ho già dato un'occhiata veloce. Dimmi pure cosa vuoi sapere o chiedimi un riassunto!"
                })
                st.session_state.file_processed = True
                st.rerun()

    st.divider()
    if st.button("🧹 Ricomincia da zero"):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.session_state.file_processed = False
        st.rerun()

# --- AREA SALVATAGGIO ---
if st.session_state.messages:
    report = "📄 REPORT RE-WIRE AI\n" + "—"*20 + "\n\n"
    for m in st.session_state.messages:
        label = "TU" if m["role"] == "user" else "RE-WIRE"
        report += f"{label}: {m['content']}\n\n"
    
    st.download_button(
        label="📥 Salva questa conversazione sul tuo PC",
        data=report,
        file_name="Analisi_REWIRE.txt",
        mime="text/plain",
        key="save_btn"
    )

# --- CHAT AMICHEVOLE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Scrivimi pure qui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Ci sto pensando... 🤔"):
            payload = {
                "model": MODEL_ID,
                "messages": [
                    {"role": "system", "content": f"Sei un assistente business molto amichevole, gentile e utile. Usa queste info: {st.session_state.doc_text}"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7 # Un po' più creativo e umano
            }
            try:
                res = requests.post(API_URL, json=payload, headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
                ans = res.json()['choices'][0]['message']['content']
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
                st.rerun()
            except:
                st.error("Scusami, ho avuto un piccolo giramento di testa... puoi riprovare? 😅")
