import streamlit as st
from groq import Groq
import base64
from PIL import Image
import io
import fitz  # PyMuPDF

# --- 1. CONFIGURAZIONE MOTORE (Nuova Chiave) ---
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="RE-WIRE AI Business", layout="wide", page_icon="🧠")

# --- 2. LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso RE-WIRE")
    pwd = st.text_input("Password Licenza", type="password")
    if st.button("ENTRA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. GESTIONE FILE E MEMORIA ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_image_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        page = doc.load_page(0)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img
    else:
        return Image.open(uploaded_file)

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- 4. INTERFACCIA ---
st.title("🧠 RE-WIRE Business Vision")

with st.sidebar:
    st.header("📁 Caricamento")
    uploaded_file = st.file_uploader("Foto o PDF", type=["jpg", "png", "jpeg", "pdf"])
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

img_base64 = None
if uploaded_file:
    image_obj = get_image_from_file(uploaded_file)
    st.image(image_obj, width=300)
    img_base64 = encode_image(image_obj)

# --- 5. CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Chiedi all'AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            # Modelli aggiornati per fine 2025
            modelli_vision = [
                "llama-3.2-11b-vision-preview",
                "llama-3.2-90b-vision-preview"
            ]
            
            final_response = None
            error_log = ""
            
            for model_name in modelli_vision:
                try:
                    content = [{"type": "text", "text": prompt}]
                    if img_base64:
                        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}})

                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": content}]
                    )
                    final_response = response.choices[0].message.content
                    break
                except Exception as e:
                    error_log += f"\n- {model_name}: {str(e)}"
                    continue

            if final_response:
                st.markdown(final_response)
                st.session_state.messages.append({"role": "assistant", "content": final_response})
            else:
                st.error("Errore di connessione ai modelli Vision.")
                with st.expander("Vedi dettagli tecnici"):
                    st.code(error_log)
