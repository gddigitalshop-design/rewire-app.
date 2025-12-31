import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configurazione API
API_KEY = "AIzaSyA8UTodWbYVU3Kzvc4Cg2brAoPinj5ciZc"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="RE-WIRE AI Business", page_icon="🧠")
st.title("🧠 RE-WIRE Business AI")

# 2. Login di sicurezza (fondamentale per affittare l'app)
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("Inserisci Password Licenza", type="password")
    if st.button("ACCEDI"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Password errata.")
    st.stop()

# 3. Interfaccia Caricamento
file = st.file_uploader("Carica un documento (Immagine)", type=["jpg", "png", "jpeg"])

if file:
    img = Image.open(file)
    st.image(img, caption="Documento caricato", use_container_width=True)
    
    prompt = st.text_input("Cosa vuoi sapere da questo documento?", "Riassumi i dati principali")
    
    if st.button("Analizza con AI"):
        with st.spinner("Analisi professionale in corso..."):
            try:
                # Modifica fondamentale: usiamo il nome semplice del modello
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Invio all'AI
                response = model.generate_content([prompt, img])
                
                st.subheader("Risultato Analisi:")
                st.write(response.text)
                
            except Exception as e:
                # Se dà ancora 404, mostriamo un messaggio utile
                if "404" in str(e):
                    st.error("Errore di configurazione Google (404).")
                    st.info("Stiamo forzando il sistema. Riprova tra un istante o contatta l'assistenza.")
                else:
                    st.error(f"Errore: {e}")

# 4. Sidebar per gestione clienti
with st.sidebar:
    st.write(f"Utente: Amministratore")
    if st.button("Svuota Sessione"):
        st.session_state.auth = False
        st.rerun()
