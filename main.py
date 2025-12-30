if st.button("📝 GENERA ANALISI PROFESSIONALE", use_container_width=True):
    if c_prompt or contenuto_file:
        with st.spinner("L'AI sta elaborando..."):
            try:
                # Prompt di sistema per dare personalità e coerenza
                istruzioni_sistema = (
                    "Sei RE-WIRE Business AI. Se l'utente ti saluta o fa domande generiche, "
                    "rispondi cordialmente e spiega che sei pronto ad analizzare i suoi file o progetti. "
                    "Se invece ricevi dati aziendali o file, agisci come un consulente senior e crea una strategia."
                )
                
                full_context = f"DATI DAL FILE:\n{contenuto_file}\n\nRICHIESTA:\n{c_prompt}"
                
                client = Groq(api_key=st.secrets["GROQ_API_KEY"])
                res = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": istruzioni_sistema},
                        {"role": "user", "content": full_context}
                    ],
                    model="llama-3.3-70b-versatile"
                )
                st.session_state.current_template = res.choices[0].message.content
            except Exception as e:
                st.error(f"Errore API: {str(e)}")
    else:
        st.warning("Inserisci un prompt o carica un file.")
