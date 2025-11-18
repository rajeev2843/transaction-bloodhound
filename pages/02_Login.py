import streamlit as st
from auth import signin_user, signup_user, login_user
from utils.styling import inject_custom_css

st.set_page_config(page_title="Login", page_icon="🔐", layout="centered", initial_sidebar_state="collapsed")
inject_custom_css()

# HIDE SIDEBAR CSS
st.markdown("""
<style>
    [data-testid="stSidebar"] {display: none;}
</style>
""", unsafe_allow_html=True)

# If already logged in, redirect
if st.session_state.get('authenticated', False):
    if st.session_state.role == 'client':
        st.switch_page("pages/03_Client_Dashboard.py")
    else:
        st.switch_page("pages/04_CA_Dashboard.py")

st.title("🔐 Authentication")

tab1, tab2 = st.tabs(["Login", "Sign Up"])

# --- LOGIN TAB ---
with tab1:
    st.subheader("Welcome Back")
    login_email = st.text_input("Email Address", key="l_email")
    login_pass = st.text_input("Password", type="password", key="l_pass")
    
    if st.button("Login", use_container_width=True):
        if not login_email or not login_pass:
            st.error("Please fill in all fields")
        else:
            # Call auth function
            success, uid, role, eid, msg = signin_user(login_email, login_pass)
            
            if success:
                login_user(uid, role, eid)
                st.success("Login successful! Redirecting...")
                
                # Redirect based on role
                if role == 'client':
                    st.switch_page("pages/03_Client_Dashboard.py")
                else:
                    st.switch_page("pages/04_CA_Dashboard.py")
            else:
                st.error(msg)

# --- SIGN UP TAB (The Missing Part) ---
with tab2:
    st.subheader("Create New Account")
    
    # Role Selection
    role_choice = st.radio("I am a:", ["Client (Entity)", "Chartered Accountant (CA)"], horizontal=True)
    role_db = "client" if "Client" in role_choice else "ca"
    
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("Full Name")
    with col2:
        new_email = st.text_input("Email Address", key="signup_email")
    
    new_pass = st.text_input("Password", type="password", key="signup_pass")
    
    # Extra fields for CAs
    firm_name = None
    mem_no = None
    
    if role_db == "ca":
        st.info("👨‍⚖️ CA Verification Details")
        c1, c2 = st.columns(2)
        with c1:
            firm_name = st.text_input("Firm Name")
        with c2:
            mem_no = st.text_input("Membership Number")
    
    if st.button("Create Account", use_container_width=True):
        if not new_email or not new_pass or not new_name:
            st.error("Please fill in all required fields")
        elif role_db == "ca" and (not firm_name or not mem_no):
            st.error("CA Registration requires Firm Name and Membership Number")
        else:
            # Call signup function
            success, uid, msg = signup_user(new_email, new_pass, new_name, role_db, firm_name, mem_no)
            
            if success:
                st.success(f"{msg} Please switch to the Login tab to sign in.")
                st.balloons()
            else:
                st.error(msg)
                
