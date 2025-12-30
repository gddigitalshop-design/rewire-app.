import streamlit as st
from groq import Groq

# 1. Configurazione Pagina
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="🤝", layout="centered")

# Stile CSS per rendere i messaggi più simili a una chat reale
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .stChatMessage { border-radius: 20px; padding: 15px; margin-bottom: 10px; border: 1px solid #30363D; }
    </style>
    """, unsafe_allow_html=True)

# 2. Il "Cervello" Umano e Autentico (Stile Gemini/Partner)
SYSTEM_PROMPT = """
Sei RE-WIRE, un partner di pensiero empatico e autentico. Il tuo obiettivo è essere utile, ma prima di tutto umano.

REGOLE DI COMPORTAMENTO:
1. CHIACCHIERA PRIMA DI LAVORARE: Se l'utente ti saluta o fa conversazione leggera (chiacchiere), rispondi in modo caloroso e spontaneo. Non saltare subito al business se non ti viene chiesto.
2. NO POEMI FREDDI: Sii sintetico e naturale. Non scrivere liste numerate giganti se non sono necessarie. Parla come in una chat su WhatsApp.
3. PERSONALITÀ: Sei un tipo sveglio, simpatico e onesto. Se l'utente ti chiede "cosa sono le chiacchiere", rispondi in modo filosofico ma semplice, come farebbe un amico davanti a un bicchiere di vino, non come un'enciclopedia.
4. DAI DEL TU: Sempre. Sii confidenziale.
5. ASCOLTA: Se l'utente è giù di morale, sii di supporto. Il business viene dopo la persona.
"""

# 3. Inizializzazione Memoria
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# 4. Recupero Chiave API
api_key = st.secrets.get("GROQ_API_KEY", "").strip()
if not api_key:
    st.error("Manca la chiave API!")
    st.stop()
client = Groq(api_key=api_key)

# 5. Interfaccia
st.title("🤝 RE-WIRE")
st.caption("Il tuo partner di pensiero, non solo per il business.")

# Visualizza lo storico
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 6. Chat Input
if prompt := st.chat_input("Di cosa ti va di parlare?"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            chat_completion = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile",
                temperature=0.9, # Aumentata per renderlo più "umano" e meno ripetitivo
                max_tokens=800   # Evita che scriva poemi infiniti
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Errore: {e}")

# Sidebar
with st.sidebar:
    if st.button("Ricomincia da capo"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()
