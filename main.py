


import streamlit as st
from groq import Groq

# Titolo semplice
st.title("🧠 RE-WIRE AI")

# Prendi la chiave dai Secrets e puliscila da eventuali spazi
api_key = st.secrets.get("GROQ_API_KEY", "").strip()

if api_key:
    client = Groq(api_key=api_key)
    
    # Campo per la domanda
    user_input = st.text_input("Scrivi la tua domanda:")
    
    if st.button("Invia"):
        if user_input:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": user_input}],
                    model="llama-3.3-70b-versatile",
                )
                st.success("Risposta:")
                st.write(chat_completion.choices[0].message.content)
            except Exception as e:
                st.error(f"Errore tecnico: {e}")
        else:
            st.warning("Scrivi qualcosa!")
else:
    st.error("Manca la chiave! Vai in Settings -> Secrets e inserisci GROQ_API_KEY")
