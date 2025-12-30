import streamlit as st
from groq import Groq

# Configurazione Pagina
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="💼", layout="wide")

# Design Professionale
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    .stButton>button {
        background-color: #007BFF;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: bold;
        width: 100%;
    }
    .stTextArea>div>div>textarea {
        background-color: #161B22;
        color: white;
        border: 1px solid #30363D;
    }
    </style>
    """, unsafe_allow_html=True)

# Recupero Chiave API
api_key = st.secrets.get("GROQ_API_KEY", "").strip()

if not api_key:
    st.error("Configura la chiave API nei Secrets!")
    st.stop()

client = Groq(api_key=api_key)

# Sidebar - Menu Business
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png")
    st.title("RE-WIRE AI")
    st.subheader("Business Brain")
    st.divider()
    opzione = st.selectbox("Cosa vuoi creare?", 
                          ["Chat Libera", "Post per i Social", "Email Professionale", "Analisi Business Idea"])
    st.info("Questa IA è ottimizzata per la produttività aziendale.")

# Header principale
st.title("💼 RE-WIRE Business Brain")
st.caption("L'assistente intelligente per scalare il tuo business.")

# Logica delle istruzioni (System Prompt) basata sulla scelta
istruzioni = "Sei RE-WIRE Business Brain, un assistente esperto in economia, marketing e gestione aziendale. Rispondi in modo professionale, schematico e orientato ai risultati."

if opzione == "Post per i Social":
    istruzioni += " Crea post accattivanti con emoji e call to action."
    prompt_predefinito = "Scrivi un post per LinkedIn che parla di..."
elif opzione == "Email Professionale":
    istruzioni += " Scrivi email chiare, gentili e professionali."
    prompt_predefinito = "Scrivi una email per richiedere un appuntamento a..."
elif opzione == "Analisi Business Idea":
    istruzioni += " Analizza l'idea fornita evidenziando punti di forza e rischi."
    prompt_predefinito = "Analizza questa idea di business: "
else:
    prompt_predefinito = ""

# Area di Input
user_input = st.text_area("Inserisci i dettagli qui sotto:", value=prompt_predefinito, height=150)

if st.button("ELABORA STRATEGIA"):
    if user_input:
        with st.spinner("Analisi in corso..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": istruzioni},
                        {"role": "user", "content": user_input}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                risposta = chat_completion.choices[0].message.content
                st.markdown("### 🚀 Soluzione Proposta:")
                st.write(risposta)
            except Exception as e:
                st.error(f"Errore: {e}")
    else:
        st.warning("Inserisci una richiesta per continuare.")

st.divider()
st.caption("© 2024 RE-WIRE AI - Business Edition")

