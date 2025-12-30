import streamlit as st
from groq import Groq

# 1. Configurazione Pagina e Titolo nel Browser
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="🤝", layout="centered")

# 2. DESIGN DARK MODERNO (CSS Personalizzato)
st.markdown("""
    <style>
    /* Sfondo generale */
    .stApp {
        background-color: #0B0E11;
        color: #E9ECEF;
    }
    
    /* Stile delle bolle dei messaggi */
    .stChatMessage {
        background-color: #161B22;
        border-radius: 20px;
        padding: 15px;
        margin-bottom: 15px;
        border: 1px solid #30363D;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Messaggio dell'utente (leggermente diverso) */
    [data-testid="stChatMessageUser"] {
        background-color: #1F2937;
        border: 1px solid #007BFF;
    }

    /* Titolo principale con effetto gradiente */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(#007BFF, #00D4FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }

    /* Nasconde il menu standard di Streamlit per un look più pulito */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# 3. Identità di RE-WIRE (Il tuo socio digitale)
SYSTEM_PROMPT = """
Sei RE-WIRE, il partner di pensiero dell'utente. 
Sei un tipo sveglio, simpatico, empatico e molto pratico. 
Non sei un robot: se l'utente scherza, scherza con lui. Se l'utente chiede aiuto per il business, diventa il suo socio più fidato.
Parla sempre in modo naturale, dai del TU e non scrivere mai testi troppo lunghi se non è strettamente necessario.
"""

# 4. Inizializzazione Sessione
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# 5. Connessione API
api_key = st.secrets.get("GROQ_API_KEY", "").strip()
if not api_key:
    st.error("Configura la chiave API!")
    st.stop()
client = Groq(api_key=api_key)

# 6. Interfaccia Grafica
st.markdown('<p class="main-title">RE-WIRE</p>', unsafe_allow_html=True)
st.markdown('<p style="color: #8B949E; margin-bottom: 30px;">Il tuo socio digitale per pensare in grande.</p>', unsafe_allow_html=True)

# Visualizzazione Chat
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 7. Input Chat
if prompt := st.chat_input("Ehi socio, di cosa parliamo oggi?"):
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            chat_completion = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile",
                temperature=0.9,
                max_tokens=1000
            )
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"Piccolo intoppo tecnico: {e}")

# Sidebar
with st.sidebar:
    st.markdown("### Centro di Controllo")
    if st.button("Reset Conversazione"):
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        st.rerun()
    st.divider()
    st.caption("RE-WIRE Business Brain v2.0")
