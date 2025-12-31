import streamlit as st
import requests
import base64

# --- CREDENZIALI ---
API_KEY = "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"
MODEL_VISION = "llama-3.2-11b-vision-preview"
URL = "https://api.groq.com/openai/v1/chat/completions"

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="RE-WIRE PRO", layout="wide")
st.markdown("<h1 style='text-align:center; color:#4facfe;'>⚡ RE-WIRE AI SYSTEM</h1>", unsafe_allow_html=True)

# --- STATO DELLA SESSIONE (MEMORIA) ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "img_b64" not in st.session_state:
    st.session_state.img_b64 = None

# --- SIDEBAR: CARICAMENTO E CONTROLLO ---
with st.sidebar:
    st.header("⚙️ Pannello Controllo")
    file = st.file_uploader("Carica Immagine", type=["jpg", "jpeg", "png"])
    if file:
        img_bytes = file.read()
        st.session_state.img_b64 = base64.b64encode(img_bytes).decode('utf-8')
        st.image(img_bytes, caption="File pronto")
    
    ambiente = st.radio("Seleziona Ambiente", ["Famiglia", "Business", "Specialista"])
    if st.button("Svuota Memoria"):
        st.session_state.chat_history = []
        st.session_state.img_b64 = None
        st.rerun()

# --- AREA CHAT ---
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Scrivi un comando (es: Ciao, Analizza per un bambino)..."):
    # Mostra messaggio utente
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generazione Risposta
    with st.chat_message("assistant"):
        # Costruzione del Messaggio per l'IA
        system_prompt = f"Sei RE-WIRE AI in modalità {ambiente}. Rispondi sempre in italiano. Se l'utente ti saluta, ricambia. Se c'è un'immagine, descrivila fedelmente (se vedi teschio/robot/bambino, parla di quelli, mai di cappelli)."
        
        # Struttura del contenuto (Testo + eventuale Immagine)
        payload_content = [{"type": "text", "text": f"{system_prompt}\n\nUtente: {prompt}"}]
        
        if st.session_state.img_b64:
            payload_content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.img_b64}"}
            })

        # Chiamata API
        try:
            response = requests.post(
                URL,
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={
                    "model": MODEL_VISION,
                    "messages": [{"role": "user", "content": payload_content}],
                    "temperature": 0.5
                }
            )
            
            # Controllo Risposta
            if response.status_code == 200:
                full_res = response.json()
                answer = full_res['choices'][0]['message']['content']
                st.markdown(answer)
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Errore API ({response.status_code}): {response.text}")
        
        except Exception as e:
            st.error(f"Errore di sistema: {e}")

    # Forza il refresh per pulire l'input
    st.rerun()
