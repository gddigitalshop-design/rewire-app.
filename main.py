import streamlit as st
import google.generativeai as genai
from PIL import Image
import google.ai.generativelanguage as gapic

# --- CONFIGURAZIONE API ---
API_KEY = "AIzaSyCBzOkGxO2qkJcNCqK1hcqHmaclY2_SWGA"

# TRUCCO TECNICO: Forziamo la configurazione sulla versione v1 (stabile)
genai.configure(api_key=API_KEY, transport='rest') # Usiamo il trasporto REST per evitare bug gRPC

st.set_page_config(page_title="RE-WIRE Business Vision", layout="wide")

# --- LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 RE-WIRE AI Login")
    pwd = st.text_input("Password Licenza", type="password")
    if st.button("ACCEDI"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- INTERFACCIA ---
st.title("🧠 RE-WIRE Business Brain")

with st.sidebar:
    st.header("📁 Caricamento")
    file = st.file_uploader("Carica Immagine", type=["jpg", "png", "jpeg"])

if file:
    img = Image.open(file)
    st.image(img, width=400)
    domanda = st.text_input("Cosa vuoi che l'AI faccia?", "Descrivi per un bambino")
    
    if st.button("🚀 ANALIZZA CON GEMINI"):
        with st.spinner("Connessione ai server stabili di Google..."):
            try:
                # Usiamo il nome del modello con il prefisso 'models/' che è più preciso
                model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
                
                # Generazione contenuto
                response = model.generate_content([domanda, img])
                
                st.markdown("### 📝 Risultato dell'Analisi")
                st.info(response.text)
                
            except Exception as e:
                st.error(f"Errore: {e}")
                st.warning("Proviamo il modello alternativo...")
                try:
                    # Fallback estremo se il flash fallisce
                    model_alt = genai.GenerativeModel('models/gemini-pro-vision')
                    response = model_alt.generate_content([domanda, img])
                    st.success(response.text)
                except:
                    st.error("Nessun modello risponde. Probabile problema di configurazione regionale del tuo account.")
