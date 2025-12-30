import streamlit as st
from groq import Groq
import random
import urllib.parse
import requests
import io
from PIL import Image
from fpdf import FPDF

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="RE-WIRE Business", layout="wide")

if "img_data" not in st.session_state: st.session_state.img_data = None
if "template_text" not in st.session_state: st.session_state.template_text = None

# --- FUNZIONE PDF ---
def genera_pdf(testo, immagine):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "RE-WIRE BUSINESS REPORT", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("helvetica", size=12)
    # Pulizia caratteri per il PDF
    t_safe = testo.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 10, t_safe)
    
    if immagine:
        pdf.ln(10)
        img_file = io.BytesIO(immagine)
        pdf.image(img_file, x=10, w=180)
    
    return pdf.output()

# --- INTERFACCIA ---
st.title("📈 RE-WIRE Business")
st.write("Generatore di strategie e concept visuali (Accesso Libero)")

with st.sidebar:
    if st.button("🗑️ Reset Totale", use_container_width=True):
        st.session_state.img_data = None
        st.session_state.template_text = None
        st.rerun()

prompt = st.text_input("Descrivi il tuo progetto (es. un topo, un ufficio, un piano marketing):")

c1, c2 = st.columns(2)

with c1:
    if st.button("🖼️ Genera Immagine HD", use_container_width=True):
        if prompt:
            with st.spinner("Creazione immagine..."):
                seed = random.randint(1, 999999)
                # Nuovo indirizzo per evitare il messaggio "We have moved"
                url = f"https://pollinations.ai/p/{urllib.parse.quote(prompt)}?width=1024&height=1024&seed={seed}&model=flux"
                try:
                    r = requests.get(url, timeout=20)
                    # Testiamo se è una vera immagine
                    Image.open(io.BytesIO(r.content))
                    st.session_state.img_data = r.content
                except:
                    st.error("Il server immagini è in manutenzione. Riprova tra poco.")

with c2:
    if st.button("📝 Crea Template & Strategia", use_container_width=True):
        if prompt:
            with st.spinner("Scrittura..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Crea una strategia business e un template operativo per: {prompt}"}],
                        model="llama-3.3-70b-versatile"
                    )
                    st.session_state.template_text = res.choices[0].message.content
                except:
                    st.error("Controlla la tua chiave Groq nei Secrets.")

# --- RISULTATI E DOWNLOAD ---
st.divider()

if st.session_state.template_text or st.session_state.img_data:
    col_v, col_d = st.columns([3, 1])
    
    with col_v:
        if st.session_state.template_text:
            st.info(st.session_state.template_text)
        if st.session_state.img_data:
            st.image(st.session_state.img_data, use_container_width=True)

    with col_d:
        st.subheader("💾 Esporta")
        if st.session_state.img_data:
            st.download_button("🖼️ Scarica Foto", st.session_state.img_data, "immagine.png", "image/png", use_container_width=True)
        
        if st.session_state.template_text:
            st.download_button("📄 Scarica Testo", st.session_state.template_text, "strategia.txt", use_container_width=True)
            
            # Tasto PDF
            try:
                report_pdf = genera_pdf(st.session_state.template_text, st.session_state.img_data)
                st.download_button(
                    "📕 SCARICA REPORT PDF",
                    data=bytes(report_pdf),
                    file_name="report_rewire.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except:
                st.write("Generazione PDF in corso...")
