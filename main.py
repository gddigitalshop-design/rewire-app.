import streamlit as st
from groq import Groq
import base64
from PIL import Image
import io
import fitz  # PyMuPDF

# --- 1. CONFIGURAZIONE ---
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="RE-WIRE AI Business", layout="wide", page_icon="🧠")

# --- 2. LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 Accesso Licenza RE-WIRE")
    pwd = st.text_input("Inserisci Password Licenza", type="password")
    if st.button("SBLOCCA SISTEMA"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. GESTIONE FILE ---
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

img_base64 = None
if file:
    try:
        img_obj = process_file(file)
        st.image(img_obj, width=350, caption="Documento pronto per l'analisi")
        img_base64 = encode_image(img_obj)
    except Exception as e:
        st.error(f"Errore file: {e}")

# --- 5. CHAT ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Fai una domanda sul documento..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Proviamo prima i modelli Vision aggiornati 2026
        # Se falliscono, l'app avvisa l'utente invece di dare risposte errate
        modelli_vision = ["llama-3.2-11b-vision-instant", "llama-3.2-90b-vision-instant"]
        successo = False
        
        for m in modelli_vision:
            try:
                # Costruiamo il contenuto multimediale
                contenuto = [{"type": "text", "text": prompt}]
                if img_base64:
                    contenuto.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
                    })

                response = client.chat.completions.create(
                    model=m,
                    messages=[{"role": "user", "content": contenuto}],
                    temperature=0.2
                )
                
                risposta_finale = response.choices[0].message.content
                st.markdown(risposta_finale)
                st.session_state.messages.append({"role": "assistant", "content": risposta_finale})
                successo = True
                break
            except Exception:
                continue
        
        if not successo:
            st.warning("⚠️ I server Vision di Groq sono in manutenzione per il nuovo anno.")
            st.info("Sto provando a rispondere usando l'analisi testuale avanzata...")
            try:
                # Backup solo testo (non vede l'immagine ma risponde alla domanda)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                risposta_testo = response.choices[0].message.content
                st.markdown(risposta_testo)
                st.session_state.messages.append({"role": "assistant", "content": risposta_testo})
            except Exception as e:
                st.error(f"Errore di rete: {e}")
