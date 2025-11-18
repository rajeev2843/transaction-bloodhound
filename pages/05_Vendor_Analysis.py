import streamlit as st
from utils.styling import inject_custom_css

st.set_page_config(page_title="Vendor Analysis", page_icon="🔎", layout="wide")
inject_custom_css()

if not st.session_state.get('authenticated'):
    st.switch_page("pages/02_Login.py")

# CSS to hide Landing/Login from sidebar
st.markdown("""
<style>
    [data-testid="stSidebarNav"] ul li:nth-child(1) {display: none;}
    [data-testid="stSidebarNav"] ul li:nth-child(2) {display: none;}
</style>
""", unsafe_allow_html=True)

st.title("🔎 Deep Vendor Analysis")
st.write("This page is visible to both CAs and Clients.")

# ... Add your Analysis code here ...
