# ---------------------
# LOGIN
# ---------------------
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔐 ACCESSO REWIRE AI")
        st.info("Applicazione protetta. Inserisci la password per continuare.")
        
        pwd = st.text_input("Password:", type="password", placeholder="Digitare qui...")
        
        if st.button("ACCEDI", use_container_width=True):
            if pwd == "rewire2026":
                st.session_state.auth = True
                st.rerun()  # Aggiornato rispetto a experimental_rerun
            else:
                st.error("Password errata. Riprova.")
    
    # Ferma l'esecuzione del resto della pagina se non autenticato
    st.stop()

# ---------------------
# LOGICA APP (Solo se auth = True)
# ---------------------
st.title("⚡ Dashboard REWIRE AI")
# Qui continua il resto del tuo codice...
