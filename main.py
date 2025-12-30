import streamlit as st
from groq import Groq
import base64
from PIL import Image
import io
import fitz  # PyMuPDF

# --- 1. CONFIGURAZIONE MOTORE ---
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="RE-WIRE Business Vision", layout="wide", page_icon="🧠")

# --- 2. LOGIN (Password: rewire2026) ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso RE-WIRE")
    pwd = st.text_input("Password Licenza", type="password")
    if st.button("ENTRA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. FUNZIONI TECNICHE ---
@st.cache_data
def get_available_vision_model():
    """Chiede a Groq quali modelli Vision sono attivi ORA"""
    try:
        models = client.models.list()
        # Cerca modelli che contengono 'vision' nel nome
        vision_models = [m.id for m in models.data if "vision" in m.id]
        return vision_models[0] if vision_models else "llama-3.2-11b-vision-preview"
    except:
        return "llama-3.2-11b-vision-preview"

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
active_model = get_available_vision_model()
st.caption(f"Motore AI attivo: **{active_model}**")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("📁 Documenti")
    file = st.file_uploader("Foto o PDF", type=["jpg", "png", "jpeg", "pdf"])
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

if prompt := st.chat_input("Chiedi all'AI..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            content = [{"type": "text", "text": prompt}]
            if img_base64:
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}})
            
            response = client.chat.completions.create(
                model=active_model, 
                messages=[{"role": "user", "content": content}]
            )
            full_res = response.choices[0].message.content
            st.markdown(full_res)
            st.session_state.messages.append({"role": "assistant", "content": full_res})
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
