import streamlit as st
from groq import Groq
from PyPDF2 import PdfReader
import base64

# --- 1. SETTING ESTETICO ---
st.set_page_config(page_title="RE-WIRE | Business Vision Pro", layout="wide", page_icon="🧠")

st.markdown("""
    <style>
    .report-box { background-color: #1E1E1E; color: #FFFFFF; padding: 25px; border-radius: 12px; border-left: 5px solid #FF4B4B; margin-bottom: 20px; box-shadow: 0px 4px 10px rgba(0,0,0,0.3); }
    .stChatMessage { border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNZIONE PER ENCODE IMMAGINI ---
def encode_image(image_file):
    return base64.b64encode(image_file.read()).decode('utf-8')

# --- 3. GESTIONE MEMORIA ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "temp_file_data" not in st.session_state:
    st.session_state.temp_file_data = {"text": "", "image_b64": None, "file_name": None}

# --- 4. SIDEBAR ---
with st.sidebar:
    st.title("🚀 RE-WIRE Vision")
    st.divider()
    
    st.subheader("📁 Carica Allegato")
    uploaded_file = st.file_uploader("Scegli un'immagine (JPG/PNG)", type=["jpg", "png", "jpeg"])
    
    if uploaded_file:
        if uploaded_file.name != st.session_state.temp_file_data.get("file_name"):
            try:
                st.session_state.temp_file_data["image_b64"] = encode_image(uploaded_file)
                st.session_state.temp_file_data["file_name"] = uploaded_file.name
                st.image(uploaded_file, caption="Immagine caricata", use_container_width=True)
                st.success(f"✅ {uploaded_file.name} pronto!")
            except Exception as e:
                st.error(f"Errore caricamento: {e}")

    if st.button("🧹 PULISCI TUTTO", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.temp_file_data = {"text": "", "image_b64": None, "file_name": None}
        st.rerun()

# --- 5. AREA CHAT ---
st.title("🧠 RE-WIRE Business Brain")

# Mostra messaggi precedenti
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant":
            st.markdown(f'<div class="report-box">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(msg["content"])

# Input Utente
prompt = st.chat_input("Scrivi qui: es. 'Descrivi questa immagine per un bambino'")

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("RE-WIRE sta guardando e scrivendo per te..."):
            try:
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                
                # Usiamo il modello Llama 3.2 Vision aggiornato
                # Se il 90b dà ancora errore, il sistema proverà automaticamente l'11b
                try:
                    model_to_use = "llama-3.2-11b-vision-preview" 
                    
                    if st.session_state.temp_file_data["image_b64"]:
                        content_payload = [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.temp_file_data['image_b64']}"}
                            }
                        ]
                    else:
                        model_to_use = "llama-3.3-70b-versatile"
                        content_payload = prompt

                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": content_payload}],
                        model=model_to_use
                    )
                    risposta = res.choices[0].message.content
                except:
                    # Fallback estremo se Groq cambia nomi ai modelli all'improvviso
                    st.error("Il modello Vision è in manutenzione su Groq. Prova tra pochi minuti.")
                    risposta = "Spiacente, sto aggiornando i miei occhi digitali. Riprova tra un istante!"
                
                st.markdown(f'<div class="report-box">{risposta}</div>', unsafe_allow_html=True)
                st.session_state.chat_history.append({"role": "assistant", "content": risposta})
                
            except Exception as e:
                st.error(f"Errore di sistema: {e}")
