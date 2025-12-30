import streamlit as st
from groq import Groq
import random
import urllib.parse
import requests
import io
from PIL import Image
from fpdf import FPDF 

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="RE-WIRE Business Brain", layout="wide")

if "current_img_data" not in st.session_state:
    st.session_state.current_img_data = None
if "current_template" not in st.session_state:
    st.session_state.current_template = None

# --- FUNZIONI ---
def genera_immagine(prompt):
    seed = random.randint(1, 1000000)
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
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, txt="RE-WIRE BUSINESS REPORT", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("helvetica", size=12)
    # Pulizia testo per evitare errori di codifica
    testo_safe = testo.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, txt=testo_safe)
    
    if immagine_data:
        try:
            pdf.ln(10)
            img_io = io.BytesIO(immagine_data)
            pdf.image(img_io, x=10, w=180)
        except:
            pass
    return pdf.output()

# --- INTERFACCIA ---
st.title("📈 RE-WIRE Business Brain")
st.markdown("Genera strategie e concept visuali - **Accesso Libero**")

with st.sidebar:
    if st.button("🗑️ Svuota Sessione", use_container_width=True):
        st.session_state.current_img_data = None
        st.session_state.current_template = None
        st.rerun()

c_prompt = st.text_input("Descrivi il tuo progetto business:", placeholder="Esempio: Centro commerciale ecosostenibile")

col1, col2 = st.columns(2)

with col1:
    if st.button("🖼️ Genera Immagine HD", use_container_width=True):
        if c_prompt:
            with st.spinner("Creazione concept..."):
                res = genera_immagine(c_prompt)
                if res:
                    st.session_state.current_img_data = res
                else:
                    st.error("Server occupato. Riprova tra 30 secondi.")

with col2:
    if st.button("📝 Crea Strategia", use_container_width=True):
        if c_prompt:
            with st.spinner("Scrittura report..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Crea una strategia business per: {c_prompt}"}],
                        model="llama-3.3-70b-versatile"
                    )
                    st.session_state.current_template = res.choices[0].message.content
                except:
                    st.error("Controlla la tua chiave Groq nei Secrets.")

# --- RISULTATI ---
st.divider()

if st.session_state.current_template or st.session_state.current_img_data:
    v_col, d_col = st.columns([3, 1])
    
    with v_col:
        if st.session_state.current_template:
            st.info(st.session_state.current_template)
        if st.session_state.current_img_data:
            st.image(st.session_state.current_img_data, use_container_width=True)

    with d_col:
        st.subheader("💾 Esporta")
        if st.session_state.current_img_data:
            st.download_button("🖼️ Immagine PNG", st.session_state.current_img_data, "concept.png", "image/png", use_container_width=True)
        
        if st.session_state.current_template:
            st.download_button("📄 Testo TXT", st.session_state.current_template, "strategia.txt", use_container_width=True)
            
            # Generazione PDF
            try:
                pdf_bytes = crea_pdf(st.session_state.current_template, st.session_state.current_img_data)
                st.download_button(
                    label="📕 Report PDF",
                    data=pdf_bytes,
                    file_name="report_rewire.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error("Errore PDF. Scarica il file TXT.")
