import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURAZIONE API ---
# Usa la tua chiave: AIzaSyCBzOkGxO2qkJcNCqK1hcqHmaclY2_SWGA
genai.configure(api_key="AIzaSyCBzOkGxO2qkJcNCqK1hcqHmaclY2_SWGA")

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
st.title("🧠 RE-WIRE Business Vision")
st.markdown('<style>.report-box { background-color: #1E1E1E; color: white; padding: 20px; border-radius: 10px; border-left: 5px solid red; }</style>', unsafe_allow_html=True)

with st.sidebar:
    st.header("📁 Caricamento")
    file = st.file_uploader("Carica Immagine", type=["jpg", "png", "jpeg"])
    if st.button("Esci"):
        st.session_state.auth = False
        st.rerun()

if file:
    img = Image.open(file)
    st.image(img, width=400)
    
    domanda = st.text_input("Cosa vuoi che l'AI faccia con questa foto?", "Descrivi per un bambino")
    
    if st.button("🚀 ANALIZZA CON GEMINI"):
        with st.spinner("Inviando i dati ai server Google..."):
            try:
                # Usiamo il modello che abbiamo appena visto funzionare nel Code Assistant
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Generazione contenuto (Testo + Immagine)
                response = model.generate_content([domanda, img])
                
                st.markdown("### 📝 Risultato dell'Analisi")
                st.markdown(f'<div class="report-box">{response.text}</div>', unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"Errore: {e}")
                st.info("Nota: Se ricevi ancora 404, prova a cambiare il nome del modello in 'gemini-1.5-flash-latest'")
else:
    st.info("Benvenuto! Carica un'immagine per iniziare l'analisi strategica.")
