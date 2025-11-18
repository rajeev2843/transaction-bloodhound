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

# --- MAIN ROUTING LOGIC ---
def main():
    # 1. If NOT logged in, force them to the Landing Page
    if not st.session_state.authenticated:
        st.switch_page("pages/1_🏠_Landing.py")
        
    # 2. If LOGGED IN, force them to their specific Dashboard
    if st.session_state.authenticated:
        if st.session_state.role == "client":
            st.switch_page("pages/3_📊_Client_Dashboard.py")
        elif st.session_state.role == "ca":
            st.switch_page("pages/4_⚖️_CA_Dashboard.py")

if __name__ == "__main__":
    main()
    
