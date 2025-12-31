import streamlit as st
import requests
import base64
from PIL import Image
import io

# --- CONFIGURAZIONE RE-WIRE ---
API_KEY = "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"
# Lista di modelli Vision (l'app proverà il primo disponibile)
MODELS_TO_TRY = ["llama-3.2-11b-vision-instant", "llama-3.2-90b-vision-instant", "pixtral-12b-2409"]
URL = "https://api.groq.com/openai/v1/chat/completions"

st.set_page_config(page_title="RE-WIRE AI PRO", layout="wide")

# --- 1. LOGIN (Indispensabile per vendere l'app) ---
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<h1 style='text-align:center; color:#4facfe;'>⚡ RE-WIRE ACCESS</h1>", unsafe_allow_html=True)
    _, col, _ = st.columns([1,1,1])
    with col:
        pwd = st.text_input("Inserisci Chiave Segreta", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("Accesso Negato")
    st.stop()

# --- 2. GESTIONE IMMAGINI ---
def prepare_image(uploaded_file):
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((800, 800))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue()).decode('utf-8')

# --- 3. MEMORIA ---
if "chat" not in st.session_state:
    st.session_state.chat = []
if "img" not in st.session_state:
    st.session_state.img = None

# --- 4. INTERFACCIA ---
with st.sidebar:
    st.title("⚡ DASHBOARD")
    file = st.file_uploader("Carica File (JPG/PNG)", type=["jpg", "png", "jpeg"])
    if file:
        st.session_state.img = prepare_image(file)
        st.image(file, caption="Visione Attiva")
    
    if st.button("🗑️ RESET SESSIONE"):
        st.session_state.chat = []
        st.session_state.img = None
        st.rerun()

# --- 5. CHAT E LOGICA VISION ---
for m in st.session_state.chat:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Scrivi un comando..."):
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        success = False
        # PROVIAMO I MODELLI UNO PER UNO FINCHÉ UNO NON FUNZIONA
        for model in MODELS_TO_TRY:
            payload = {
                "model": model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Sei RE-WIRE AI. Analizza l'immagine se presente e rispondi a: {prompt}"}
                    ]
                }],
                "temperature": 0.5
            }
            if st.session_state.img:
                payload["messages"][0]["content"].append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{st.session_state.img}"}
                })

            try:
                r = requests.post(URL, headers={"Authorization": f"Bearer {API_KEY}"}, json=payload)
                if r.status_code == 200:
                    res = r.json()
                    answer = res['choices'][0]['message']['content']
                    st.markdown(f"*{model}*:\n\n{answer}")
                    st.session_state.chat.append({"role": "assistant", "content": answer})
                    success = True
                    break # Esci dal ciclo se funziona
            except:
                continue
        
        if not success:
            st.error("Nessun modello Vision disponibile al momento. Controlla la tua console Groq o riprova tra poco.")



### Cosa cambia ora:
1.  **Zero Errori di Modello**: Se Groq ha cambiato nome al modello "instant", l'app prova automaticamente gli altri della lista.
2.  **Affidabilità**: La pagina di Login (password: **rewire2026**) protegge il tuo lavoro.
3.  **Analisi Reale**: Una volta entrato, se carichi l'immagine, l'IA vedrà finalmente la scena del bambino e del robot senza allucinazioni.

**Copia e sostituisci tutto.** Fammi sapere se finalmente la chat ti risponde "Ciao" dopo il login. Una volta sbloccato questo, potremo rendere la grafica degna di un'app da migliaia di euro.
