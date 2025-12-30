import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURAZIONE API ---
API_KEY = "AIzaSyCBzOkGxO2qkJcNCqK1hcqHmaclY2_SWGA"
genai.configure(api_key=API_KEY)

st.set_page_config(page_title="RE-WIRE Vision Pro", layout="wide")

# --- 2. LOGIN ---
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 RE-WIRE Login")
    pwd = st.text_input("Password Licenza", type="password")
    if st.button("ACCEDI"):
        if pwd == "rewire2026":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# --- 3. INTERFACCIA ---
st.title("🧠 RE-WIRE Business Brain")

with st.sidebar:
    st.header("⚙️ Strumenti")
    file = st.file_uploader("Carica Immagine", type=["jpg", "png", "jpeg"])
    if st.button("Esci"):
        st.session_state.auth = False
        st.rerun()

if file:
    img = Image.open(file)
    st.image(img, width=400)
    istruzione = st.text_area("Cosa deve fare l'AI?", "Descrivi per un bambino")

    if st.button("🚀 ANALIZZA"):
        with st.spinner("Ricerca motore compatibile..."):
            # PROVIAMO 3 MODELLI DIVERSI IN SEQUENZA
            modelli = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro-vision"]
            successo = False
            
            for m in modelli:
                if successo: break
                try:
                    model = genai.GenerativeModel(m)
                    # Se il modello è gemini-pro (solo testo), togliamo l'immagine
                    payload = [istruzione, img] if "vision" in m or "1.5" in m else [istruzione]
                    
                    response = model.generate_content(payload)
                    st.success(f"Analisi completata con successo (Motore: {m})")
                    st.markdown(f"**Risultato:** {response.text}")
                    successo = True
                except Exception as e:
                    continue # Prova il prossimo modello se questo fallisce
            
            if not successo:
                st.error("Nessun modello disponibile per questa chiave API.")
                st.info("⚠️ ULTIMO PASSO NECESSARIO: Vai su https://aistudio.google.com/, clicca sulla rotellina in basso a sinistra (Impostazioni) e verifica che il tuo Paese sia supportato e che i Termini di Servizio siano accettati.")
