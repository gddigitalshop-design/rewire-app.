import streamlit as st
import requests
import base64

# --- CONFIGURAZIONE ---
API_KEY = "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"
MODEL_ID = "llama-3.2-11b-vision-preview" 
URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI", layout="wide")

# --- MEMORIA ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "img_b64" not in st.session_state:
    st.session_state.image_data = None

# --- SIDEBAR ---
with st.sidebar:
    st.title("⚡ RE-WIRE DASH")
    uploaded_file = st.file_uploader("Carica immagine", type=["jpg", "png", "jpeg"])
    if uploaded_file:
        data = uploaded_file.read()
        st.session_state.image_data = base64.b64encode(data).decode('utf-8')
        st.image(data, caption="Immagine caricata correttamente")
    
    if st.button("Pulisci Chat"):
        st.session_state.messages = []
        st.rerun()

# --- DISPLAY CHAT ---
# Mostriamo i messaggi precedenti prima dell'input
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# --- INPUT E RISPOSTA ---
if prompt := st.chat_input("Scrivi qui..."):
    # 1. Mostra e salva il messaggio utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Genera risposta
    with st.chat_message("assistant"):
        # Istruzioni fisse per evitare allucinazioni (niente cappelli!)
        system_content = "Sei RE-WIRE AI. Se c'è un'immagine, descrivila esattamente. Se vedi robot, teschi o bambini, parla di quelli. Rispondi sempre in italiano."
        
        # Prepariamo il payload per l'API
        payload_messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"{system_content}\n\nDomanda: {prompt}"}
                ]
            }
        ]

        # Se abbiamo un'immagine in memoria, la iniettiamo nel messaggio
        if st.session_state.image_data:
            payload_messages[0]["content"].append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.image_data}"}
            })

        try:
            response = requests.post(
                URL,
                headers={"Authorization": f"Bearer {API_KEY}"},
                json={"model": MODEL_ID, "messages": payload_messages, "temperature": 0.5},
                timeout=30
            )
            
            if response.status_code == 200:
                res_json = response.json()
                answer = res_json['choices'][0]['message']['content']
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                st.error(f"Errore API: {response.status_code}")
        except Exception as e:
            st.error(f"Errore connessione: {e}")
