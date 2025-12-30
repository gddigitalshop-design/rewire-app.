


import streamlit as st
from groq import Groq

# 1. Configurazione Pagina
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="💼", layout="centered")

# Design Professionale migliorato
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("💼 RE-WIRE Business Brain")
st.caption("Dialogo continuo abilitato - L'IA ricorda la conversazione.")

# 2. Inizializzazione Memoria (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Sei RE-WIRE Business Brain, un assistente esperto in business e marketing. Rispondi in modo professionale e tieni a mente il contesto della conversazione."}
    ]

# 3. Recupero Chiave API
api_key = st.secrets.get("GROQ_API_KEY", "").strip()
if not api_key:
    st.error("Configura la chiave API nei Secrets!")
    st.stop()
client = Groq(api_key=api_key)

# 4. Visualizza lo storico dei messaggi (tranne il messaggio di sistema)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. Area di Input (Chat Input è molto più fluido del text_area)
if prompt := st.chat_input("Scrivi qui il tuo messaggio..."):
    
    # Aggiungi il messaggio dell'utente alla memoria
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Mostra il messaggio dell'utente a schermo
    with st.chat_message("user"):
        st.markdown(prompt)

    # Genera la risposta dell'IA
    with st.chat_message("assistant"):
        with st.spinner("RE-WIRE sta elaborando..."):
            try:
                # Inviamo TUTTA la cronologia a Groq, così ha memoria
                chat_completion = client.chat.completions.create(
                    messages=st.session_state.messages,
                    model="llama-3.3-70b-versatile",
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                
                # Aggiungi la risposta dell'IA alla memoria
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Errore: {e}")

# Bottone per resettare la conversazione
if st.sidebar.button("Cancella Conversazione"):
    st.session_state.messages = [st.session_state.messages[0]]
    st.rerun()
