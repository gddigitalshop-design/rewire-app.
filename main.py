import streamlit as st
import requests
import base64
from PIL import Image
import io

# --- CONFIGURAZIONE ---
API_KEY = "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"
MODEL_ID = "llama-3.2-11b-vision-preview" 
URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI PRO", layout="wide")

# --- FUNZIONE PER OTTIMIZZARE L'IMMAGINE (Evita Errore 400) ---
def process_image(uploaded_file):
    img = Image.open(uploaded_file)
    # Converti in RGB se necessario (per PNG/RGBA)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    # Ridimensiona se troppo grande (max 1024px)
    img.thumbnail((1024, 1024))
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- MEMORIA ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "image_data" not in st.session_state:
    st.session_state.image_data = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ DASHBOARD")
    file = st.file_uploader("Carica immagine", type=["jpg", "png", "jpeg"])
    if file:
        st.session_state.image_data = process_image(file)
        st.image(file, caption="Immagine Ottimizzata")
    
    if st.button("Pulisci Chat"):
        st.session_state.messages = []
        st.session_state.image_data = None
        st.rerun()

# --- DISPLAY CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- INPUT E RISPOSTA ---
if prompt := st.chat_input("Scrivi qui..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Costruiamo il messaggio in modo ultra-pulito
        msg_body = {
            "role": "user",
            "content": [
                {"type": "text", "text": f"Sei RE-WIRE AI. Rispondi a questo: {prompt}. Se vedi un'immagine, descrivila fedelmente (robot, teschio, bambini)."}
            ]
        }
        
        # Aggiungiamo l'immagine solo se esiste
        if st.session_state.image_data:
            msg_body["content"].append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.image_data}"}
            })

        try:
            response = requests.post(
                URL,
                headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
                json={"model": MODEL_ID, "messages": [msg_body], "temperature": 0.5}
            )
            
            res_json = response.json()
            
            if response.status_code == 200:
                answer = res_json['choices'][0]['message']['content']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                # Se c'è ancora un errore, stampiamo il motivo esatto
                error_msg = res_json.get('error', {}).get('message', 'Errore sconosciuto')
                st.error(f"Errore API {response.status_code}: {error_msg}")
        
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
