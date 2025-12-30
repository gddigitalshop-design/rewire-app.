import streamlit as st
from groq import Groq
import base64
from PIL import Image
import io
import fitz  # PyMuPDF per i PDF

# --- 1. CONFIGURAZIONE ---
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="RE-WIRE Business Vision", layout="wide", page_icon="🧠")

# --- 2. LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso RE-WIRE")
    pwd = st.text_input("Password Licenza", type="password")
    if st.button("SBLOCCA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. GESTIONE MEMORIA CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 4. FUNZIONI TECNICHE ---
def process_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        # Estrai la prima pagina del PDF come immagine
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

# --- 5. INTERFACCIA ---
st.title("🧠 RE-WIRE Business Vision & Chat")

with st.sidebar:
    st.header("📁 Documenti e Foto")
    file = st.file_uploader("Carica Immagine o PDF", type=["jpg", "png", "jpeg", "pdf"])
    if st.button("Svuota Chat"):
        st.session_state.messages = []
        st.rerun()

# Visualizzazione file caricato
current_img_base64 = None
if file:
    img = process_file(file)
    st.image(img, width=300, caption="Documento/Immagine pronti")
    current_img_base64 = encode_image(img)

# --- 6. BARRA DELLA CHAT ---
# Visualizza messaggi precedenti
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input nuova domanda
if prompt := st.chat_input("Fai una domanda sul file caricato..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            content = [{"type": "text", "text": prompt}]
            if current_img_base64:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{current_img_base64}"}
                })

            response = client.chat.completions.create(
                model="llama-3.2-90b-vision-preview",
                messages=[{"role": "user", "content": content}]
            )
            full_response = response.choices[0].message.content
            st.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Errore: {e}")
