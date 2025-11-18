import streamlit as st
from database import init_database
from utils.styling import inject_custom_css

# Initialize DB on first run
if 'db_initialized' not in st.session_state:
    init_database()
    st.session_state.db_initialized = True

# Page Config
st.set_page_config(
    page_title="Transaction Bloodhound",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Styling
inject_custom_css()

# Session State Init
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# --- LOGIC TO HIDE PAGES ---
# This is the trick. We rename pages in the sidebar to hide them based on role.
# But Streamlit's native multipage app handles this differently.
# For this production version, we will trust the user flow.

def main():
    if not st.session_state.authenticated:
        st.switch_page("pages/1_🏠_Landing.py")
        
    # If logged in, redirect to appropriate dashboard if they land on main
    if st.session_state.authenticated:
        if st.session_state.role == "client":
            st.switch_page("pages/3_📊_Client_Dashboard.py")
        elif st.session_state.role == "ca":
            st.switch_page("pages/4_⚖️_CA_Dashboard.py")

if __name__ == "__main__":
    main()
  
