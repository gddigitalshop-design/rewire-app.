import streamlit as st
from groq import Groq

# 1. Configurazione della pagina
st.set_page_config(page_title="RE-WIRE AI", page_icon="🧠", layout="centered")

# Stile CSS per renderla più bella
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🧠 RE-WIRE AI")
st.write("Benvenuto! Scrivi la tua domanda qui sotto e l'intelligenza artificiale ti risponderà.")

# 2. Gestione Chiave API (Automatica dai Secrets)
if "GROQ_API_KEY" in st.secrets:
    # Se la chiave è nei Secrets, la usa direttamente
    api_key = st.secrets["GROQ_API_KEY"]
else:
    # Se manca, mostra un avviso (utile per il primo setup)
    st.warning("Configurazione in corso... Se sei l'amministratore, inserisci la chiave nei Secrets di Streamlit.")
    api_key = st.sidebar.text_input("Inserisci Groq API Key per test:", type="password")

# 3. Logica dell'App
if api_key:
    client = Groq(api_key=api_key)
    
    user_input = st.text_area("Cosa vuoi sapere?", placeholder="Scrivi qui il tuo messaggio...", height=150)

    if st.button("Genera Risposta"):
        if user_input:
            with st.spinner("🤖 Sto elaborando la risposta..."):
                try:
                    # Usiamo il modello più recente
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": "Sei un assistente utile e professionale."},
                            {"role": "user", "content": user_input}
                        ],
                        model="llama-3.3-70b-versatile",
                    )
                    
                    risposta = chat_completion.choices[0].message.content
                    
                    st.markdown("---")
                    st.markdown("### ✨ Risposta dell'IA:")
                    st.write(risposta)
                    
                except Exception as e:
                    st.error(f"Si è verificato un errore tecnico: {e}")
        else:
            st.info("Per favore, scrivi qualcosa prima di cliccare il tasto.")
else:
    st.error("Chiave API non trovata. Vai nelle impostazioni di Streamlit e aggiungi GROQ_API_KEY nei Secrets.")

# Footer
st.markdown("---")
st.caption("Powered by RE-WIRE AI & Groq Cloud")

