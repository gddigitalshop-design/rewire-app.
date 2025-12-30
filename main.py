import streamlit as st
from groq import Groq
from openai import OpenAI # Importa la libreria OpenAI
import PyPDF2
import base64 # Per visualizzare le immagini DALL-E

# --- 1. CONFIGURAZIONE PAGINA (Look & Feel) ---
st.set_page_config(page_title="RE-WIRE Business Brain", page_icon="📈", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #0B0E11; color: #E9ECEF; }
    .stButton>button { border-radius: 10px; background-color: #007BFF; color: white; width: 100%; border: none; padding: 10px; }
    .stButton>button:hover { background-color: #0056b3; border: none; }
    .stChatMessage { background-color: #161B22; border-radius: 15px; border: 1px solid #30363D; margin-bottom: 10px; }
    /* Nasconde il menu Streamlit per un look più pulito */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* Stili per i nuovi bottoni Generatore */
    .stDownloadButton>button { background-color: #28a745 !important; }
    .image-generator-button { background-color: #6f42c1 !important; }
    .template-generator-button { background-color: #fd7e14 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIONE ACCESSO ---
USERS = {
    "admin": "tuapassword123", # <--- Ricorda di cambiare questa password!
    "cliente1": "rewire2025"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.messages = []
    st.session_state.generated_image_b64 = None # Nuova variabile per l'immagine

# Logica Link Magico
query_params = st.query_params
if not st.session_state.logged_in:
    u_url = query_params.get("user")
    p_url = query_params.get("pass")
    if u_url in USERS and USERS[u_url] == p_url:
        st.session_state.logged_in = True
        st.session_state.user_role = u_url

def login_page():
    st.markdown('<p style="font-size:3.5rem; font-weight:800; color:#007BFF; text-align:center; margin-bottom:0;">RE-WIRE</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#8B949E; margin-bottom:2rem;">L\'Intelligenza Artificiale per il tuo Business</p>', unsafe_allow_html=True)
    with st.container():
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Accedi al Sistema"):
            if u in USERS and USERS[u] == p:
                st.session_state.logged_in = True
                st.session_state.user_role = u
                st.rerun()
            else:
                st.error("Credenziali non valide")

if not st.session_state.logged_in:
    login_page()
    st.stop()

# --- 3. LOGICA DI BUSINESS (PDF & REPORT) ---
def genera_report():
    testo = f"--- REPORT CONSULENZA RE-WIRE ---\nUtente: {st.session_state.user_role}\n\n"
    for m in st.session_state.messages:
        if m["role"] != "system":
            testo += f"{m['role'].upper()}: {m['content']}\n\n"
    return testo

# --- FUNZIONI DI GENERAZIONE (NUOVE) ---
def genera_immagine(prompt_immagine):
    try:
        openai_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt_immagine,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        # Converti l'URL in base64 per visualizzarla direttamente (o usa l'URL se preferisci)
        # Per semplicità, useremo l'URL temporaneo, ma puoi scaricarla e convertirla se serve persistenza
        st.success("Immagine generata con successo!")
        return image_url
    except Exception as e:
        st.error(f"Errore nella generazione dell'immagine: {e}")
        return None

def genera_template(prompt_template):
    try:
        groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Sei un esperto di organizzazione aziendale e creazione di template. Genera template chiari, strutturati e funzionali in formato Markdown o testo semplice."},
                {"role": "user", "content": f"Genera un template per: {prompt_template}"}
            ],
            model="llama-3.3-70b-versatile"
        )
        st.success("Template generato con successo!")
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Errore nella generazione del template: {e}")
        return None

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/brainstorming.png", width=80) # Puoi mettere un tuo logo qui
    st.title("Area Riservata")
    st.write(f"Connesso come: **{st.session_state.user_role}**")
    
    if st.button("Esci"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    st.subheader("🛠️ Pannello Operativo")
    
    if len(st.session_state.messages) == 0:
        st.info("Inizia a chattare per attivare le funzioni di download.")
    else:
        st.download_button(
            label="💾 Scarica il Lavoro (TXT)",
            data=genera_report(),
            file_name=f"report_{st.session_state.user_role}.txt",
            use_container_width=True
        )

    st.divider()
    st.markdown("### 📂 Carica Documenti")
    file = st.file_uploader("Carica bilanci o PDF", type="pdf")
    
    if file:
        reader = PyPDF2.PdfReader(file)
        testo_pdf = "".join([p.extract_text() for p in reader.pages])
        if "ultimo_file" not in st.session_state or st.session_state.ultimo_file != file.name:
            st.session_state.messages.append({"role": "assistant", "content": f"✅ **Documento '{file.name}' caricato con successo.**\n\nHo analizzato il contenuto. Come posso aiutarti con questi dati?"})
            st.session_state.messages.append({"role": "system", "content": f"Agisci come un esperto Business Consultant. Usa queste info dal PDF per rispondere: {testo_pdf[:4000]}"})
            st.session_state.ultimo_file = file.name
            st.rerun()

# --- 5. CHAT PRINCIPALE & GENERATORE CREATIVO ---
st.markdown(f"### Benvenuto in RE-WIRE, {st.session_state.user_role}")

if not [m for m in st.session_state.messages if m["role"] != "system"]:
    st.markdown("""
    Ciao! Sono il tuo Business Brain. Ecco cosa posso fare per te oggi:
    * **Analisi PDF:** Carica un documento a sinistra e chiedimi riassunti o analisi.
    * **Strategia:** Chiedimi di creare un piano d'azione per il tuo business.
    * **Copywriting:** Posso scrivere email, post social o capitoli di ebook.
    * **Generatore Creativo:** Crea immagini o template organizzativi su richiesta.
    """)

# Sezione per il Generatore Creativo
st.divider()
st.markdown("### ✨ Generatore Creativo")
creative_prompt = st.text_input("Descrivi l'immagine o il template che desideri...", key="creative_input")

col_img, col_temp = st.columns(2)
with col_img:
    if st.button("🖼️ Genera Immagine (DALL-E)", use_container_width=True, help="Genera un'immagine basata sulla tua descrizione", key="gen_img_btn"):
        if creative_prompt:
            with st.spinner("Generazione immagine in corso..."):
                image_output_url = genera_immagine(creative_prompt)
                if image_output_url:
                    st.session_state.messages.append({"role": "assistant", "content": f"Ecco l'immagine che hai richiesto: ![]({image_output_url})"}) # Visualizza l'immagine nella chat
                    st.session_state.generated_image_b64 = image_output_url # Salva l'URL per display persistente
                st.rerun()
        else:
            st.warning("Inserisci una descrizione per l'immagine.")
with col_temp:
    if st.button("📝 Crea Template (AI)", use_container_width=True, help="Genera un template organizzativo o un formato di testo", key="gen_temp_btn"):
        if creative_prompt:
            with st.spinner("Generazione template in corso..."):
                template_output = genera_template(creative_prompt)
                if template_output:
                    st.session_state.messages.append({"role": "assistant", "content": f"Ecco il template che hai richiesto:\n\n{template_output}"})
                st.rerun()
        else:
            st.warning("Inserisci una descrizione per il template.")

# Visualizza l'immagine generata se presente nello session_state
if st.session_state.generated_image_b64:
    st.image(st.session_state.generated_image_b64, caption=f"Immagine generata: {creative_prompt}")
    
st.divider() # Rimetto il divider per separare la chat dal generatore

# 6. CHAT PRINCIPALE
for m in st.session_state.messages:
    if m["role"] != "system":
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

if prompt := st.chat_input("Scrivi qui la tua richiesta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        compl = client.chat.completions.create(
            messages=st.session_state.messages,
            model="llama-3.3-70b-versatile"
        )
        resp = compl.choices[0].message.content
        st.markdown(resp)
        st.session_state.messages.append({"role": "assistant", "content": resp})
