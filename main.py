import streamlit as st
from groq import Groq

# Configurazione della pagina
st.set_page_config(page_title="RE-WIRE AI", page_icon="🚀")
st.title("🚀 RE-WIRE: Assistente Intelligente")

# Barra laterale per la chiave
with st.sidebar:
    st.header("Impostazioni")
    # Qui l'utente può inserire la sua chiave Groq
    api_key = st.text_input("Inserisci Groq API Key:", type="password")
    st.info("Prendi la tua chiave gratis su: https://console.groq.com/keys")

# Area di Chat
domanda = st.text_input("In cosa posso aiutarti oggi?")

if st.button("Chiedi all'IA"):
    if not api_key:
        st.warning("Inserisci la chiave API nella barra a sinistra!")
    elif not domanda:
        st.error("Scrivi una domanda!")
    else:
        try:
            client = Groq(api_key=api_key)
            with st.spinner("L'IA sta pensando..."):
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": domanda}],
                    model="llama-3.3-70b-versatile",
                )
                risposta = chat_completion.choices[0].message.content
                st.success("Risposta:")
                st.write(risposta)
        except Exception as e:
            st.error(f"Errore: {e}")