import streamlit as st
from auth import signin_user, signup_user, login_user
from utils.styling import inject_custom_css

st.set_page_config(page_title="Login - Transaction Bloodhound", page_icon="🔐", layout="centered")
inject_custom_css()

# If already logged in, redirect
if st.session_state.get('authenticated', False):
    if st.session_state.role == 'client':
        st.switch_page("pages/3_📊_Client_Dashboard.py")
    else:
        st.switch_page("pages/4_⚖️_CA_Dashboard.py")

st.title("🔐 Authentication")

tab1, tab2 = st.tabs(["Login", "Sign Up"])

with tab1:
    st.subheader("Welcome Back")
    login_email = st.text_input("Email Address", key="login_email")
    login_pass = st.text_input("Password", type="password", key="login_pass")
    
    if st.button("Login", use_container_width=True):
        if not login_email or not login_pass:
            st.error("Please fill in all fields")
        else:
            success, uid, role, eid, msg = signin_user(login_email, login_pass) # Note: auth.py might need slight adjustment to match return values
            # Adjusted logic based on your auth.py:
            # It returns: True, user.user_id, user.role.value, entity_id
            # OR: False, None, None, "Error message"
            
            if success:
                login_user(uid, role, eid)
                st.success("Login successful!")
                st.rerun()
            else:
                st.error(msg)

with tab2:
    st.subheader("Create New Account")
    role_choice = st.radio("I am a:", ["Client (Entity)", "Chartered Accountant (CA)"])
    role_db = "client" if "Client" in role_choice else "ca"
    
    new_name = st.text_input("Full Name")
    new_email = st.text_input("Email Address", key="signup_email")
    new_pass = st.text_input("Password", type="password", key="signup_pass")
    
    firm_name = None
    mem_no = None
    
    if role_db == "ca":
        firm_name = st.text_input("Firm Name")
        mem_no = st.text_input("Membership Number")
    
    if st.button("Sign Up", use_container_width=True):
        if not new_email or not new_pass or not new_name:
            st.error("Please fill in all required fields")
        else:
            success, uid, msg = signup_user(new_email, new_pass, new_name, role_db, firm_name, mem_no)
            if success:
                st.success(msg)
                st.info("Please switch to the Login tab to sign in.")
            else:
                st.error(msg)
              
