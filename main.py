import streamlit as st
from groq import Groq
import base64
from PIL import Image
import io
import fitz  # PyMuPDF per leggere i PDF

# --- 1. CONFIGURAZIONE MOTORE ---
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="RE-WIRE AI Business", layout="wide", page_icon="🧠")

# --- 2. STILE CSS PERSONALIZZATO ---
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stChatInput { border-radius: 10px; }
    .report-box { background-color: #1E1E1E; color: white; padding: 20px; border-radius: 10px; border-left: 5px solid red; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIN SISTEMA ---
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 RE-WIRE AI | Accesso Licenza")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        pwd = st.text_input("Inserisci Password", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Accesso negato.")
    st.stop()

# --- 4. GESTIONE MEMORIA E FILE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

def get_image_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        page = doc.load_page(0) # Legge la prima pagina
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return img
    else:
        return Image.open(uploaded_file)

def encode_image(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- 5. INTERFACCIA PRINCIPALE ---
st.title("🧠 RE-WIRE Business Vision & Chat")

with st.sidebar:
    st.header("📁 File Center")
    uploaded_file = st.file_uploader("Carica Foto o PDF", type=["jpg", "png", "jpeg", "pdf"])
    if st.button("🗑️ Svuota Conversazione"):
        st.session_state.messages = []
        st.rerun()
    st.divider()
    st.caption("Versione Business 2026.1")

# Visualizzazione file e preparazione dati
img_base64 = None
if uploaded_file:
    try:
        image_obj = get_image_from_file(uploaded_file)
        st.image(image_obj, width=350, caption="Documento analizzato")
        img_base64 = encode_image(image_obj)
    except Exception as e:
        st.error(f"Errore caricamento: {e}")

# --- 6. CHAT INTERATTIVA ---
# Mostra cronologia
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Barra di input
if prompt := st.chat_input("Chiedi qualcosa sul documento..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("L'AI sta analizzando..."):
            # Lista di modelli Vision da provare se uno fallisce
            modelli_vision = [
                "llama-3.2-11b-vision-preview",
                "llama-3.2-90b-vision-preview",
                "llava-v1.5-7b-4096"
            ]
            
            final_response = None
            for model_name in modelli_vision:
                try:
                    # Costruzione messaggio (Testo + Immagine se presente)
                    content = [{"type": "text", "text": prompt}]
                    if img_base64:
                        content.append({
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                        })

                    response = client.chat.completions.create(
                        model=model_name,
                        messages=[{"role": "user", "content": content}],
                        temperature=0.5,
                        max_tokens=1024
                    )
                    final_response = response.choices[0].message.content
                    break # Esce se funziona
                except:
                    continue # Prova il prossimo modello se c'è un errore (es. 404 o decommissionato)

            if final_response:
                st.markdown(final_response)
                st.session_state.messages.append({"role": "assistant", "content": final_response})
            else:
                st.error("I server di visione sono saturi. Riprova tra un istante.")
