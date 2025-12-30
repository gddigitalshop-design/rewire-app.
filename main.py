import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURAZIONE ---
# Ho inserito la tua nuova chiave qui
genai.configure(api_key="AIzaSyAI6SNpjbh0nft9dlzxHADUiquQBXDC1pE")

st.set_page_config(page_title="RE-WIRE Vision", layout="centered")
st.title("🧠 RE-WIRE Business Vision")
st.write("Carica un'immagine e io la analizzerò per te.")

# --- CARICAMENTO ---
file_caricato = st.file_uploader("Scegli un'immagine dal tuo PC", type=["jpg", "png", "jpeg"])

if file_caricato:
    # Mostriamo la foto sullo schermo
    immagine = Image.open(file_caricato)
    st.image(immagine, caption="Immagine caricata con successo!", use_container_width=True)
    
    # Casella di testo per la tua richiesta
    istruzione = st.text_input("Cosa devo fare?", "Descrivi questa immagine per un bambino in modo breve")

    # TASTO PER FAR PARTIRE L'AI
    if st.button("🚀 ANALIZZA ORA"):
        with st.spinner("Sto leggendo l'immagine..."):
            try:
                # Usiamo il modello Flash (il più veloce e moderno)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                # Chiediamo all'AI di guardare e rispondere
                risposta = model.generate_content([istruzione, immagine])
                
                # Risultato finale
                st.subheader("Ecco il risultato:")
                st.success(risposta.text)
                
            except Exception as e:
                st.error(f"C'è ancora un problema tecnico: {e}")
                st.info("Se vedi ancora '404', vai su https://aistudio.google.com/ e accetta i contratti di Google.")
