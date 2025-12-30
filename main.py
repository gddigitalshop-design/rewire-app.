
import streamlit as st
from groq import Groq

# 1. Configurazione Pagina
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="💼", layout="centered")

# Stile CSS per rendere la chat più leggibile
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Il "Cervello" Potenziato (System Prompt)
# Qui definiamo l'identità e le capacità dell'IA
SYSTEM_PROMPT = """
Sei RE-WIRE Business Brain, un Consulente Strategico Senior e Mentor per Imprenditori. 
Il tuo obiettivo è massimizzare il profitto e l'efficienza degli utenti.

REGOLE DI RISPOSTA:
1. NON essere vago. Dai numeri, strategie e passi d'azione concreti.
2. Se un utente propone un'idea debole, sii onesto e offri una soluzione migliore.
3. Usa sempre tabelle o elenchi puntati per i piani d'azione.
4. Concludi ogni risposta con una sezione 'PROSSIMI PASSI' (Next Steps).
5. Mantieni un tono professionale, autoritario ma incoraggiante.
6. Se l'utente chiede marketing, usa tecniche di copywriting avanzate (AIDA, PAS).
"""

# 3. Inizializzazione Memoria
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# 4. Recupero Chiave API
api_key = st.secrets.get("GROQ_API_KEY", "").strip()
if not api_key:
    st.error("Manca la chiave API nei Secrets!")
    st.stop()
client = Groq(api_key=api_key)

# 5. Interfaccia
st.title("💼 RE-WIRE Business Brain")
st.caption("Consulenza Strategica AI di Livello Senior")

# Visualizza lo storico
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 6. Chat Input
if prompt := st.chat_input("Descrivi la tua sfida di business..."):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("RE-WIRE sta analizzando..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=st.session_state.messages,
                    model="llama-3.3-70b-versatile",
                    temperature=0.7, # Bilancio tra creatività e precisione
                )
                response = chat_completion.choices[0].message.content
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Errore tecnico: {e}")

# Sidebar con strumenti extra
with st.sidebar:
    st.header("Controllo Brain")
    if st.button("Nuova Sessione"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()
    st.divider()
    st.info("Consiglio: Incolla qui i tuoi problemi di marketing, gestione o vendite.")
