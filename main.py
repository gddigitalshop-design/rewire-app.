# --- 2. ACCESSO UTENTI ---
USERS = {
    "admin": "tuapassword123",
    "cliente1": "rewire2025"
}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.messages = []

# --- LOGICA LINK MAGICO (Controlla l'URL all'avvio) ---
query_params = st.query_params
url_user = query_params.get("user")
url_pass = query_params.get("pass")

if not st.session_state.logged_in:
    # Se i dati nell'URL sono corretti, logga l'utente automaticamente
    if url_user in USERS and USERS[url_user] == url_pass:
        st.session_state.logged_in = True
        st.session_state.user_role = url_user

def login_page():
    st.markdown('<p style="font-size:3rem; font-weight:800; color:#007BFF; text-align:center;">RE-WIRE</p>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#8B949E;">Business Intelligence & Strategic Partner</p>', unsafe_allow_html=True)
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Accedi", use_container_width=True):
        if u in USERS and USERS[u] == p:
            st.session_state.logged_in = True
            st.session_state.user_role = u
            st.rerun()
        else:
            st.error("Credenziali errate")

if not st.session_state.logged_in:
    login_page()
    st.stop()
