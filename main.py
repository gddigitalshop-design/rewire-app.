import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import base64

# --- 1. SETTING ESTETICO ---
st.set_page_config(page_title="RE-WIRE | Business Vision Pro", layout="wide", page_icon="🧠")

st.markdown("""
    <style>
    .report-box { background-color: #1E1E1E; color: #FFFFFF; padding: 25px; border-radius: 12px; border-left: 5px solid #FF4B4B; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3); }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNZIONE PER ENCODE IMMAGINI ---
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 3. GESTIONE MEMORIA ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "temp_file_data" not in st.session_state:
    st.session_state.temp_file_data = {"text": "", "image_b64": None, "file_name": None}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🚀 RE-WIRE Vision")
    st.write("Versione: **Premium 2026 Ready**")
    st.divider()
    
    st.subheader("📁 Carica Allegato")
    uploaded_file = st.file_uploader("Scegli un'immagine (JPG/PNG) o un PDF/TXT", type=["txt", "pdf", "jpg", "png"])
    
    if uploaded_file:
        if uploaded_file.name != st.session_state.temp_file_data.get("file_name"):
            try:
                if uploaded_file.type in ["image/jpeg", "image/png"]:
                    st.session_state.temp_file_data["image_b64"] = encode_image(uploaded_file)
                    st.session_state.temp_file_data["text"] = ""
                    st.image(uploaded_file, caption="Immagine caricata", use_container_width=True)
                elif uploaded_file.type == "application/pdf":
                    reader = PdfReader(uploaded_file)
                    text = ""
                    for page in reader.pages: text += page.extract_text() + "\n"
                    st.session_state.temp_file_data["text"] = text
                    st.session_state.temp_file_data["image_b64"] = None
                else:
                    st.session_state.temp_file_data["text"] = uploaded_file.getvalue().decode("utf-8")
                    st.session_state.temp_file_data["image_b64"] = None
                
                st.session_state.temp_file_data["file_name"] = uploaded_file.name
                st.success(f"✅ {uploaded_file.name} pronto!")
            except Exception as e:
                st.error(f"Errore caricamento: {e}")

    if st.button("🧹 PULISCI TUTTO", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.temp_file_data = {"text": "", "image_b64": None, "file_name": None}
        st.rerun()

# --- 5. AREA CHAT ---
st.title("🧠 RE-WIRE Business Brain")

# Mostra messaggi precedenti
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(f'<div class="report-box">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# Input Utente
prompt = st.chat_input("Scrivi qui il tuo messaggio... (analizzerò anche l'allegato se presente)")

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("RE-WIRE sta elaborando testo e visione..."):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                # Se c'è un'immagine, usiamo il modello VISION aggiornato (90b)
                if st.session_state.temp_file_data["image_b64"]:
                    model_to_use = "llama-3.2-90b-vision-preview" # Modello aggiornato 2025
                    content_payload = [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.temp_file_data['image_b64']}"}
                        }
                    ]
                else:
                    # Altrimenti usiamo il modello testuale standard
                    model_to_use = "llama-3.3-70b-versatile"
                    context_text = st.session_state.temp_file_data["text"]
                    content_payload = f"UTENTE DICE: {prompt}\n\nCONTESTO DOCUMENTO:\n{context_text[:10000]}"

                res = client.chat.completions.create(
                    messages=[{"role": "user", "content": content_payload}],
                    model=model_to_use
                )
                
                risposta = res.choices[0].message.content
                st.markdown(f'<div class="report-box">{risposta}</div>', unsafe_allow_html=True)
                st.session_state.chat_history.append({"role": "assistant", "content": risposta})
                
            except Exception as e:
                st.error(f"Errore di sistema: {e}")
