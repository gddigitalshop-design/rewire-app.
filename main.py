import streamlit as st
from groq import Groq
import random
import urllib.parse
import requests
import io
from PIL import Image
from fpdf import FPDF # Assicurati di aggiungere 'fpdf2' nel file requirements.txt

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="RE-WIRE Business Brain", layout="wide")

if "current_img_data" not in st.session_state:
    st.session_state.current_img_data = None
if "current_template" not in st.session_state:
    st.session_state.current_template = None

# --- 2. FUNZIONI TECNICHE ---
def genera_immagine(prompt):
    seed = random.randint(1, 1000000)
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
    try:
        r = requests.get(url, timeout=20)
        # Verifica se è un'immagine reale
        img = Image.open(io.BytesIO(r.content))
        return r.content
    except:
        return None

def crea_pdf(testo, immagine_data=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="RE-WIRE Business Report", ln=True, align='C')
    pdf.ln(10)
    
    # Testo del Template
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=testo)
    
    if immagine_data:
        pdf.ln(10)
        img_bin = io.BytesIO(immagine_data)
        pdf.image(img_bin, x=10, w=100)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 3. INTERFACCIA PRINCIPALE ---
st.title("📈 RE-WIRE Business Brain")
st.markdown("Genera strategie, template e immagini per il tuo business in un click.")

with st.sidebar:
    st.header("Comandi Rapidi")
    if st.button("🗑️ Svuota Tutto", use_container_width=True):
        st.session_state.current_img_data = None
        st.session_state.current_template = None
        st.rerun()

# --- 4. INPUT E GENERAZIONE ---
c_prompt = st.text_input("Descrivi la tua idea o il tuo progetto:")

col1, col2 = st.columns(2)

with col1:
    if st.button("🖼️ Genera Immagine HD", use_container_width=True):
        if c_prompt:
            with st.spinner("Creazione immagine..."):
                res = genera_immagine(c_prompt)
                if res:
                    st.session_state.current_img_data = res
                else:
                    st.error("Server temporaneamente occupato. Riprova.")
        else:
            st.warning("Inserisci una descrizione.")

with col2:
    if st.button("📝 Crea Template & Strategia", use_container_width=True):
        if c_prompt:
            with st.spinner("Scrittura strategia..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Crea un report business e un template per: {c_prompt}"}],
                        model="llama-3.3-70b-versatile"
                    )
                    st.session_state.current_template = res.choices[0].message.content
                except:
                    st.error("Errore API Groq.")

# --- 5. VISUALIZZAZIONE E DOWNLOAD ---
st.divider()

if st.session_state.current_template or st.session_state.current_img_data:
    c1, c2 = st.columns([2, 1])
    
    with c1:
        if st.session_state.current_template:
            st.subheader("📝 Strategia e Template")
            st.info(st.session_state.current_template)
            
        if st.session_state.current_img_data:
            st.subheader("🖼️ Concept Visuale")
            st.image(st.session_state.current_img_data, use_container_width=True)

    with c2:
        st.subheader("💾 Esportazione")
        
        # Download Immagine
        if st.session_state.current_img_data:
            st.download_button(
                "📥 Scarica Immagine (PNG)",
                st.session_state.current_img_data,
                "creazione_rewire.png",
                "image/png",
                use_container_width=True
            )
        
        # Download Template (Testo)
        if st.session_state.current_template:
            st.download_button(
                "📥 Scarica Template (TXT)",
                st.session_state.current_template,
                "template_rewire.txt",
                use_container_width=True
            )
            
            # Esportazione PDF (Bonus)
            try:
                pdf_bytes = crea_pdf(st.session_state.current_template, st.session_state.current_img_data)
                st.download_button(
                    "📄 Scarica Report Completo (PDF)",
                    pdf_bytes,
                    "report_rewire.pdf",
                    "application/pdf",
                    use_container_width=True
                )
            except:
                st.write("PDF in preparazione...")
