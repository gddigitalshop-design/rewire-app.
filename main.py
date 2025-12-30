
import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURAZIONE CHIAVE ---
# Ho inserito la tua nuova chiave qui
API_KEY = "AIzaSyCBzOkGxO2qkJcNCqK1hcqHmaclY2_SWGA"
genai.configure(api_key=API_KEY)

# --- 2. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="RE-WIRE Business Vision", layout="wide", page_icon="🧠")

# Stile CSS per un look professionale (Nero e Rosso)
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .report-box { 
        background-color: #1E1E1E; color: #FFFFFF; padding: 25px; 
        border-radius: 15px; border-left: 5px solid #FF4B4B; 
        line-height: 1.6; margin-bottom: 20px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. SISTEMA DI LOGIN (Per vendere l'app) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 RE-WIRE AI | Accesso Riservato")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        password = st.text_input("Inserisci Password Licenza", type="password")
        if st.button("SBLOCCA SISTEMA"):
            if password == "rewire2026": # Password per i tuoi clienti
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Password non valida. Contatta l'amministratore.")
    st.stop()

# --- 4. INTERFACCIA APP ---
st.title("🧠 RE-WIRE Business Vision")
st.write("Analisi Multimodale Strategica - Attiva")

with st.sidebar:
    st.header("⚙️ Pannello Strumenti")
    st.write("Stato API: **Connesso**")
    st.divider()
    
    file_caricato = st.file_uploader("Carica Immagine (JPG/PNG)", type=["jpg", "png", "jpeg"])
    
    if st.button("🔴 LOGOUT"):
        st.session_state.authenticated = False
        st.rerun()

# --- 5. LOGICA DI ANALISI ---
if file_caricato:
    col_img, col_txt = st.columns([1, 1])
    
    img = Image.open(file_caricato)
    with col_img:
        st.image(img, caption="Immagine in elaborazione", use_container_width=True)
    
    with col_txt:
        istruzione = st.text_area("Cosa desideri che l'AI analizzi?", 
                                 "Descrivi questa immagine in modo semplice per un bambino, evidenziando i colori e le forme.")
        
        if st.button("🚀 ESEGUI ANALISI AI"):
            with st.spinner("L'intelligenza artificiale sta osservando..."):
                try:
                    # Chiamata al modello stabile
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content([istruzione, img])
                    
                    st.markdown("### 📝 Risultato dell'Analisi")
                    st.markdown(f'<div class="report-box">{response.text}</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Errore tecnico: {e}")
                    st.info("Consiglio: Se l'errore persiste, verifica i permessi della chiave su AI Studio.")
else:
    st.info("👋 Benvenuto nel sistema RE-WIRE. Per iniziare, carica un'immagine dal pannello laterale.")

st.divider()
st.caption("© 2025 RE-WIRE Technology - Tutti i diritti riservati.")
