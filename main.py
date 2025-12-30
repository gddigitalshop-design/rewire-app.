import streamlit as st
from groq import Groq
import random
import urllib.parse
import requests
import io
from PIL import Image
from fpdf import FPDF 

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="RE-WIRE Business Brain", layout="wide")

# Inizializzazione sessione
if "current_img_data" not in st.session_state:
    st.session_state.current_img_data = None
if "current_template" not in st.session_state:
    st.session_state.current_template = None

# --- 2. FUNZIONI TECNICHE ---
def genera_immagine(prompt):
    seed = random.randint(1, 1000000)
    # Usiamo un parametro casuale per il modello per tentare di aggirare il rate limit
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&seed={seed}&nologo=true"
    try:
        r = requests.get(url, timeout=20)
        img = Image.open(io.BytesIO(r.content))
        return r.content
    except:
        return None

def crea_pdf(testo, immagine_data=None):
    pdf = FPDF()
    pdf.add_page()
    
    # Titolo
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt="RE-WIRE Business Report", ln=True, align='C')
    pdf.ln(10)
    
    # Testo Strategia (Gestione caratteri speciali)
    pdf.set_font("Arial", size=12)
    # Pulizia testo per evitare errori di codifica latin-1 nel PDF
    testo_pulito = testo.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=testo_pulito)
    
    # Immagine (se presente)
    if immagine_data:
        try:
            pdf.ln(10)
            img_bin = io.BytesIO(immagine_data)
            # Salvataggio temporaneo per FPDF
            pdf.image(img_bin, x=10, w=180)
        except:
            pass
            
    return pdf.output()

# --- 3. INTERFACCIA ---
st.title("📈 RE-WIRE Business Brain")
st.markdown("Generatore di strategie e concept visuali - **Versione Libera**")

with st.sidebar:
    st.header("Comandi")
    if st.button("🗑️ Svuota Tutto", use_container_width=True):
        st.session_state.current_img_data = None
        st.session_state.current_template = None
        st.rerun()

c_prompt = st.text_input("Descrivi il tuo progetto business:")

col1, col2 = st.columns(2)

with col1:
    if st.button("🖼️ Genera Immagine HD", use_container_width=True):
        if c_prompt:
            with st.spinner("Creazione immagine..."):
                res = genera_immagine(c_prompt)
                if res:
                    st.session_state.current_img_data = res
                    st.success("Immagine creata!")
                else:
                    st.error("Server occupato (Rate Limit). Riprova tra poco.")
        else:
            st.warning("Inserisci una descrizione.")

with col2:
    if st.button("📝 Crea Strategia", use_container_width=True):
        if c_prompt:
            with st.spinner("Scrittura..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Crea una strategia business e un template operativo per: {c_prompt}"}],
                        model="llama-3.3-70b-versatile"
                    )
                    st.session_state.current_template = res.choices[0].message.content
                except:
                    st.error("Errore Groq. Controlla la tua API Key.")

# --- 4. VISUALIZZAZIONE E DOWNLOAD ---
st.divider()

if st.session_state.current_template or st.session_state.current_img_data:
    v_col, d_col = st.columns([3, 1])
    
    with v_col:
        if st.session_state.current_template:
            st.info("### Strategia Generata")
            st.markdown(st.session_state.current_template)
        
        if st.session_state.current_img_data:
            st.image(st.session_state.current_img_data, caption="Concept Visuale", use_container_width=True)

    with d_col:
        st.subheader("💾 Download")
        
        if st.session_state.current_img_data:
            st.download_button("🖼️ Scarica Foto", st.session_state.current_img_data, "immagine.png", "image/png", use_container_width=True)
        
        if st.session_state.current_template:
            st.download_button("📄 Scarica Testo (TXT)", st.session_state.current_template, "strategia.txt", use_container_width=True)
            
            # Generazione PDF al volo
            try:
                pdf_output = crea_pdf(st.session_state.current_template, st.session_state.current_img_data)
                st.download_button(
                    label="📕 Scarica Report PDF",
                    data=bytes(pdf_output),
                    file_name="report_rewire.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.write("Errore creazione PDF. Prova a scaricare il TXT.")
