import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import base64

# --- 1. SETTING ESTETICO ---
st.set_page_config(page_title="RE-WIRE | Business Vision", layout="wide", page_icon="🧠")

st.markdown("""
    <style>
    .report-box { background-color: #1E1E1E; color: #FFFFFF; padding: 20px; border-radius: 10px; border-left: 5px solid #FF4B4B; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNZIONE PER GESTIRE LE IMMAGINI ---
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 3. MEMORIA ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "file_context" not in st.session_state:
    st.session_state.file_context = {"text": "", "image_base64": None}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🚀 RE-WIRE Vision")
    st.divider()
    st.subheader("📁 Carica File o Immagine")
    uploaded_file = st.file_uploader("PDF, TXT o Immagini (JPG/PNG)", type=["txt", "pdf", "jpg", "png"])
    
    if uploaded_file:
        try:
            if uploaded_file.type in ["image/jpeg", "image/png"]:
                st.session_state.file_context["image_base64"] = encode_image(uploaded_file)
                st.image(uploaded_file, caption="Immagine pronta", use_container_width=True)
                st.session_state.file_context["text"] = "L'utente ha caricato un'immagine."
            elif uploaded_file.type == "application/pdf":
                reader = PdfReader(uploaded_file)
                text = ""
                for page in reader.pages: text += page.extract_text() + "\n"
                st.session_state.file_context["text"] = text
                st.session_state.file_context["image_base64"] = None
                st.success("PDF letto!")
            else:
                st.session_state.file_context["text"] = uploaded_file.getvalue().decode("utf-8")
                st.session_state.file_context["image_base64"] = None
                st.success("Testo letto!")
        except Exception as e:
            st.error(f"Errore: {e}")

    if st.button("🧹 Pulisci tutto"):
        st.session_state.chat_history = []
        st.session_state.file_context = {"text": "", "image_base64": None}
        st.rerun()

# --- 5. AREA CHAT ---
st.title("🧠 RE-WIRE Business Brain")

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(f'<div class="report-box">{msg["content"]}</div>' if msg["role"] == "assistant" else msg["content"], unsafe_allow_html=True)

prompt = st.chat_input("Cosa vedi in questa immagine? / Analizza questo file...")

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("RE-WIRE sta guardando e analizzando..."):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                # Se c'è un'immagine, usiamo il modello VISION
                if st.session_state.file_context["image_base64"]:
                    model = "llama-3.2-11b-vision-preview"
                    content = [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.file_context['image_base64']}"}}
                    ]
                else:
                    model = "llama-3.3-70b-versatile"
                    content = f"{prompt}\n\nCONTESTO:\n{st.session_state.file_context['text'][:10000]}"

                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": content}],
                    model=model
                )
                
                risposta = res.choices[0].message.content
                st.markdown(f'<div class="report-box">{risposta}</div>', unsafe_allow_html=True)
                st.session_state.chat_history.append({"role": "assistant", "content": risposta})
                
            except Exception as e:
                st.error(f"Errore Visione: {e}")
