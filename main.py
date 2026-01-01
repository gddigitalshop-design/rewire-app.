import streamlit as st
import groq

# TEST VELOCE SENZA DATABASE PER VEDERE SE IL MOTORE GIRA
st.title("🧠 REWIRE AI - Factory")

# Inserisci la tua chiave direttamente qui tra le virgolette per sbloccare subito
# Esempio: client = groq.Client(api_key="gsk_xxxx")
api_key_test = st.text_input("Inserisci qui la tua chiave Groq per sbloccare l'app:", type="password")

if api_key_test:
    client = groq.Client(api_key=api_key_test)
    prompt = st.chat_input("Chiedi qualcosa...")
    
    if prompt:
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            try:
                chat_completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.write(chat_completion.choices[0].message.content)
            except Exception as e:
                st.error(f"Errore: {e}")
