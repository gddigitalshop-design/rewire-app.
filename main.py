import streamlit as st
import requests
import base64
from PIL import Image
import io

# 1. SETUP UI
st.set_page_config(page_title="REWIRE AI PRO", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    [data-testid="stSidebar"] { background-color: #000000 !important; }
    [data-testid="stChatMessage"] { background-color: #1e293b !important; border-radius: 12px !important; }
    [data-testid="stChatInput"] { border: 2px solid #6366f1 !important; }
    .stButton>button { background-color: #6366f1; color: white; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# 2. INIZIALIZZAZIONE
if "auth" not in st.session_state: st.session_state.auth = False
if "messages" not in st.session_state: st.session_state.messages = []

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    st.error("Errore: Chiave API mancante nei Secrets.")
    st.stop()

# 3. LOGIN
if not st.session_state.auth:
    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown("<h1 style='text-align: center;'>⚡ REWIRE AI</h1>", unsafe_allow_html=True)
        with st.form("login"):
            pwd = st.text_input("Password Licenza:", type="password")
            if st.form_submit_button("ACCEDI"):
                if pwd == "rewire2026":
                    st.session_state.auth = True
                    st.rerun()
                else: st.error("Password errata.")
    st.stop()

# 4. SIDEBAR
with st.sidebar:
    st.title("⚙️ Pannello")
    # Abbiamo aggiornato i modelli ai nomi più recenti e stabili
    st.info("Modello Vision: Llama 3.2 Vision\nModello Testo: Llama 3.3 70B")
    uploaded_file = st.file_uploader("Allega immagine", type=["png", "jpg", "jpeg"])
    if st.button("🗑️ Reset Chat"):
        st.session_state.messages = []
        st.rerun()

# 5. STORICO CHAT
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        if "image" in m: st.image(m["image"], width=300)
        st.markdown(m["content"])

# 6. LOGICA DI RISPOSTA (MODELLI STABILI 2026)
if prompt := st.chat_input("Chiedi a Rewire..."):
    user_msg = {"role": "user", "content": prompt}
    img_b64 = None
    
    if uploaded_file:
        img_data = uploaded_file.getvalue()
        user_msg["image"] = img_data
        img_b64 = base64.b64encode(img_data).decode()

    with st.chat_message("user"):
        if uploaded_file: st.image(uploaded_file, width=300)
        st.markdown(prompt)
    
    st.session_state.messages.append(user_msg)

    with st.chat_message("assistant"):
        with st.spinner("Rewire sta elaborando..."):
            try:
                # MODELLI AGGIORNATI: Usiamo i nomi corretti per il 2026
                # Se l'immagine è presente, usiamo il modello vision stabile
                model = "llama-3.2-11b-vision-preview" if img_b64 else "llama-3.3-70b-versatile"
                
                api_msgs = [{"role": "system", "content": "Sei Rewire AI, rispondi in italiano."}]
                for m in st.session_state.messages[-5:-1]:
                    api_msgs.append({"role": m["role"], "content": m["content"]})
                
                if img_b64:
                    content = [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                    ]
                else:
                    content = prompt
                    
                api_msgs.append({"role": "user", "content": content})

                resp = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    json={"model": model, "messages": api_msgs},
                    timeout=20
                )
                
                data = resp.json()

                if "choices" in data:
                    ans = data['choices'][0]['message']['content']
                    st.markdown(ans)
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                else:
                    # GESTIONE DEPRECATION: Se il modello vision dà errore, l'app tenta il fallback sul testo
                    error_msg = data.get("error", {}).get("message", "")
                    if "decommissioned" in error_msg:
                        st.warning("Il modello Vision è in manutenzione. Provo con l'analisi testuale...")
                        # Fallback automatico
                        resp = requests.post(
                            "https://api.groq.com/openai/v1/chat/completions",
                            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]},
                            timeout=20
                        )
                        ans = resp.json()['choices'][0]['message']['content']
                        st.markdown(ans)
                        st.session_state.messages.append({"role": "assistant", "content": ans})
                    else:
                        st.error(f"Errore API: {error_msg}")
                    
            except Exception as e:
                st.error(f"Errore di connessione: {e}")
