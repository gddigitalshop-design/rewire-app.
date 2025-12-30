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

# Stato della sessione per non perdere i dati al refresh
if "img_data" not in st.session_state: st.session_state.img_data = None
if "template_text" not in st.session_state: st.session_state.template_text = None

# --- FUNZIONE GENERAZIONE PDF ---
def genera_pdf(testo, immagine_bin):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, "RE-WIRE BUSINESS REPORT", ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("helvetica", size=11)
    # Pulizia caratteri per evitare errori nel PDF
    t_safe = testo.encode('latin-1', 'ignore').decode('latin-1')
    pdf.multi_cell(0, 8, t_safe)
    
    if immagine_bin:
        try:
            pdf.ln(10)
            img_file = io.BytesIO(immagine_bin)
            # Inserisce l'immagine nel PDF
            pdf.image(img_file, x=10, w=180)
        except:
            pass
    return pdf.output()

# --- INTERFACCIA ---
st.title("📈 RE-WIRE Business")
st.write("Generatore Strategico - Accesso Libero")

# Barra laterale per pulire la sessione
with st.sidebar:
    if st.button("🗑️ Reset Totale", use_container_width=True):
        st.session_state.img_data = None
        st.session_state.template_text = None
        st.rerun()

prompt = st.text_input("Inserisci la tua idea (es: un topo, un ufficio moderno, piano marketing):")

col1, col2 = st.columns(2)

with col1:
    if st.button("🖼️ Genera Immagine HD", use_container_width=True):
        if prompt:
            with st.spinner("L'AI sta creando l'immagine..."):
                seed = random.randint(1, 999999)
                # Endpoint aggiornato per tentare di bypassare il blocco
                url = f"https://pollinations.ai/p/{urllib.parse.quote(prompt)}?width=1024&height=1024&seed={seed}&nologo=true&model=flux"
                try:
                    r = requests.get(url, timeout=25)
                    # Verifica se è un'immagine reale o il messaggio di errore/manutenzione
                    test_img = Image.open(io.BytesIO(r.content))
                    st.session_state.img_data = r.content
                except:
                    st.error("⚠️ Il server immagini gratuito è saturo. Riprova tra 30 secondi o cambia prompt.")

with col2:
    if st.button("📝 Crea Template & Strategia", use_container_width=True):
        if prompt:
            with st.spinner("Scrittura strategia in corso..."):
                try:
                    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                    res = client.chat.completions.create(
                        messages=[{"role": "user", "content": f"Crea una strategia business e un template operativo per: {prompt}"}],
                        model="llama-3.3-70b-versatile"
                    )
                    st.session_state.template_text = res.choices[0].message.content
                except:
                    st.error("Errore Groq: controlla la tua API Key nei Secrets.")

# --- RISULTATI ---
st.divider()

if st.session_state.template_text or st.session_state.img_data:
    col_view, col_down = st.columns([3, 1])
    
    with col_view:
        if st.session_state.template_text:
            st.info(st.session_state.template_text)
        if st.session_state.img_data:
            st.image(st.session_state.img_data, caption="Risultato AI", use_container_width=True)

    with col_down:
        st.subheader("💾 Esporta")
        if st.session_state.img_data:
            st.download_button("🖼️ Scarica Foto", st.session_state.img_data, "immagine.png", "image/png", use_container_width=True)
        
        if st.session_state.template_text:
            st.download_button("📄 Scarica Testo", st.session_state.template_text, "strategia.txt", use_container_width=True)
            
            # Generazione PDF
            try:
                pdf_res = genera_pdf(st.session_state.template_text, st.session_state.img_data)
                st.download_button(
                    "📕 SCARICA PDF COMPLETO",
                    data=bytes(pdf_res),
                    file_name="report_rewire.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.write("Preparazione PDF...")
