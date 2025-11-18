import streamlit as st
from database import init_database
from utils.styling import inject_custom_css

# Initialize DB
if 'db_initialized' not in st.session_state:
    init_database()
    st.session_state.db_initialized = True

st.set_page_config(page_title="Transaction Bloodhound", page_icon="🔍", layout="wide")

# Inject CSS to hide sidebar navigation by default (we will show it only when logged in)
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {display: none !important;}
</style>
""", unsafe_allow_html=True)

# Session Init
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'role' not in st.session_state:
    st.session_state.role = None

def main():
    # If not logged in, force them to Landing
    if not st.session_state.authenticated:
        st.switch_page("pages/01_Landing.py")
    
    # If logged in, redirect based on role
    if st.session_state.authenticated:
        if st.session_state.role == "client":
            st.switch_page("pages/03_Client_Dashboard.py")
        elif st.session_state.role == "ca":
            st.switch_page("pages/04_CA_Dashboard.py")

if __name__ == "__main__":
    main()
