import streamlit as st
from groq import Groq

# Titolo e Configurazione Pagina
st.set_page_config(page_title="RE-WIRE AI", page_icon="🧠")
st.title("🧠 RE-WIRE AI")
st.subheader("La tua intelligenza artificiale personalizzata")

# Recupero automatico della chiave dai Secrets
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("Errore: Chiave API non configurata nei Secrets di Streamlit.")
    st.stop()

# Area di input
user_input = st.text_area("Cosa vuoi chiedermi oggi?", placeholder="Scrivi qui...")

if st.button("Chiedi all'IA"):
    if user_input:
        with st.spinner("Sto pensando..."):
            try:
                # Usiamo il modello nuovo che abbiamo testato prima
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": user_input}],
                    model="llama-3.3-70b-versatile",
                )
                risposta = chat_completion.choices[0].message.content
                st.markdown("### Risposta:")
                st.write(risposta)
            except Exception as e:
                st.error(f"Si è verificato un errore: {e}")
    else:
        st.warning("Per favore, inserisci una domanda.")
