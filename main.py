import streamlit as st
from groq import Groq
import base64
from PIL import Image
import io
import fitz  # PyMuPDF

# --- 1. CONFIGURAZIONE MOTORE ---
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

def process_file(uploaded_file):
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
    st.header("📁 Documenti")
    file = st.file_uploader("Carica Foto o PDF", type=["jpg", "png", "jpeg", "pdf"])
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

img_base64 = None
if file:
    img_obj = process_file(file)
    st.image(img_obj, width=300)
    img_base64 = encode_image(img_obj)

# --- 5. CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Fai una domanda..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisi in corso..."):
            # Modelli Vision 2026 (nomi corretti)
            modelli_vision = ["llama-3.2-11b-vision-instant", "llama-3.2-90b-vision-instant"]
            
            final_resp = None
            logs = ""
            
            for m in modelli_vision:
                try:
                    content = [{"type": "text", "text": prompt}]
                    if img_base64:
                        content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}})
                    
                    resp = client.chat.completions.create(model=m, messages=[{"role": "user", "content": content}])
                    final_resp = resp.choices[0].message.content
                    break
                except Exception as e:
                    logs += f"{m}: {str(e)}\n"
            
            if final_resp:
                st.markdown(final_resp)
                st.session_state.messages.append({"role": "assistant", "content": final_resp})
            else:
                st.error("Errore critico nei modelli.")
                st.info(f"Dettagli: {logs}")
