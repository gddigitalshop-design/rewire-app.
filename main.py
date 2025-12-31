import streamlit as st
import requests
import fitz
import json
import base64

# --- CONFIGURAZIONE API ---
GROQ_API_KEY = "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"
MODEL_ID = "llama-3.2-11b-vision-preview" 
API_URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI PRO", layout="wide", page_icon="⚡")

# --- CSS PREMIUM ---
st.markdown("""
    <style>
    .stApp { background: #0d1117; color: #e6edf3; }
    .main-title { font-size: 45px !important; font-weight: 800; background: linear-gradient(90deg, #00f2fe, #4facfe); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; }
    .img-container { border: 2px solid #4facfe; border-radius: 15px; overflow: hidden; background: black; margin-bottom: 20px; }
    .stChatMessage { background: rgba(255, 255, 255, 0.05) !important; border-radius: 15px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNZIONE ENCODE ---
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# --- INIT SESSION ---
if "messages" not in st.session_state: st.session_state.messages = []
if "current_file" not in st.session_state: st.session_state.current_file = None

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#4facfe; font-size:24px; text-align:center;'>⚡ DASHBOARD</h1>", unsafe_allow_html=True)
    uploaded = st.file_uploader("Upload", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
    
    if uploaded:
        if "last_fn" not in st.session_state or st.session_state.last_fn != uploaded.name:
            st.session_state.last_fn = uploaded.name
            file_bytes = uploaded.read()
            if uploaded.type != "application/pdf":
                st.session_state.current_file = {"type": "img", "data": file_bytes, "base64": encode_image(file_bytes)}
            st.rerun()

    mode = st.radio("🎯 AMBIENTE", ["🏠 Famiglia", "💼 Business", "🔬 Specialista"])
    if st.button("🗑️ RESET"):
        st.session_state.clear()
        st.rerun()

# --- AREA DI LAVORO ---
if st.session_state.current_file:
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown('<div class="img-container">', unsafe_allow_html=True)
        st.image(st.session_state.current_file["data"])
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        st.success(f"Modalità {mode} - VISIONE ATTIVA")

# --- CHAT ---
for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Analizza l'immagine..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        # Preparazione contenuto
        content_list = [{"type": "text", "text": f"Sei RE-WIRE AI ({mode}). Descrivi la scena reale: teschio, robot, bambino. Ignora nomi file fuorvianti come 'CAP'."}]
        
        if st.session_state.current_file and st.session_state.current_file["type"] == "img":
            content_list.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.current_file['base64']}"}
            })
        
        content_list.append({"type": "text", "text": prompt})

        try:
            response = requests.post(API_URL, 
                json={"model": MODEL_ID, "messages": [{"role": "user", "content": content_list}]}, 
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"})
            
            res_json = response.json()
            
            # CONTROLLO SICUREZZA PER EVITARE KEYERROR
            if 'choices' in res_json:
                ans = res_json['choices'][0]['message']['content']
                st.markdown(ans)
                st.session_state.messages.append({"role": "assistant", "content": ans})
            else:
                st.error("L'IA è momentaneamente sovraccarica o la chiave API ha raggiunto il limite. Riprova tra un istante.")
                st.write(res_json) # Debug per te, poi lo toglieremo
        except Exception as e:
            st.error(f"Errore di sistema: {e}")
        
        st.rerun()
