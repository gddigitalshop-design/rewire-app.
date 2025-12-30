import streamlit as st
from groq import Groq
import base64
from PIL import Image
import io
import fitz  # PyMuPDF per i PDF

# --- 1. CONFIGURAZIONE ---
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="RE-WIRE AI Business", layout="wide", page_icon="🧠")

# --- 2. LOGIN (Protezione Business) ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Inserisci Password Licenza", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Password non valida.")
    st.stop()

# --- 3. GESTIONE MEMORIA E FILE ---
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
st.title("🧠 RE-WIRE Business Intelligence")

with st.sidebar:
    st.header("📁 Hub Documenti")
    file = st.file_uploader("Carica Foto o PDF", type=["jpg", "png", "jpeg", "pdf"])
    if st.button("🗑️ Reset Conversazione"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.info("Sistema multi-modello attivo")

img_base64 = None
if file:
    try:
        img_obj = process_file(file)
        st.image(img_obj, width=350, caption="Documento in analisi")
        img_base64 = encode_image(img_obj)
    except Exception as e:
        st.error(f"Errore caricamento file: {e}")

# --- 5. CHAT CON FALLBACK AUTOMATICO ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Fai una domanda strategica..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("L'intelligenza RE-WIRE sta elaborando..."):
            # Gerarchia di modelli: dal più recente al più stabile
            modelli_da_provare = [
                "llama-3.2-11b-vision-instant",
                "llama-3.2-90b-vision-instant",
                "llama-3.3-70b-versatile" # Modello testuale di emergenza (sempre attivo)
            ]
            
            final_res = None
            
            for model_name in modelli_da_provare:
                try:
                    # Se il modello supporta la visione e abbiamo un'immagine
                    if "vision" in model_name and img_base64:
                        content = [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                        ]
                    else:
                        # Fallback solo testo
                        content = [{"type": "text", "text": prompt}]

                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": content}],
                        timeout=10.0 # Evita attese infinite
                    )
                    final_res = response.choices[0].message.content
                    if "vision" not in model_name and img_base64:
                        final_res += "\n\n*(Nota: Analisi testuale di backup)*"
                    break
                except Exception:
                    continue # Passa al prossimo modello se questo fallisce
            
            if final_res:
                st.markdown(final_res)
                st.session_state.messages.append({"role": "assistant", "content": final_res})
            else:
                st.error("I sistemi sono temporaneamente occupati. Riprova tra 60 secondi.")
