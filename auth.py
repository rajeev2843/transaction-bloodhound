import streamlit as st
import bcrypt
import secrets
from datetime import datetime
from database import get_session, User, CAProfile, EntityProfile, UserRole
from sqlalchemy.exc import IntegrityError

# Password hashing
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Generate unique CA invite code
def generate_invite_code():
    return f"CA-{secrets.token_hex(4).upper()}"

# Session management
def login_user(user_id: int, role: str, entity_id: int = None):
    st.session_state.user_id = user_id
    st.session_state.role = role
    st.session_state.entity_id = entity_id
    st.session_state.authenticated = True
    
    # Update last login
    db = get_session()
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        user.last_login = datetime.utcnow()
        db.commit()
    db.close()

def logout_user():
    for key in ['user_id', 'role', 'entity_id', 'authenticated', 'setup_complete']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# Sign Up Logic
def signup_user(email: str, password: str, full_name: str, role: str, firm_name: str = None, membership_no: str = None):
    db = get_session()
    try:
        # Create User
        new_user = User(
            email=email.lower().strip(),
            password_hash=hash_password(password),
            full_name=full_name.strip(),
            role=UserRole(role)
        )
        db.add(new_user)
        db.flush()
        
        # If CA, create CA Profile
        if role == "ca" and firm_name and membership_no:
            ca_profile = CAProfile(
                user_id=new_user.user_id,
                firm_name=firm_name.strip(),
                membership_no=membership_no.strip(),
                invite_code=generate_invite_code()
            )
            db.add(ca_profile)
        
        db.commit()
        return True, new_user.user_id, "Account created successfully!"
    
    except IntegrityError as e:
        db.rollback()
        if "email" in str(e.orig):
            return False, None, "Email already registered. Please login."
        elif "membership_no" in str(e.orig):
            return False, None, "CA Membership number already registered."
        else:
            return False, None, f"Registration error: {str(e)}"
    except Exception as e:
        db.rollback()
        return False, None, f"Unexpected error: {str(e)}"
    finally:
        db.close()

# Sign In Logic
def signin_user(email: str, password: str):
    db = get_session()
    try:
        user = db.query(User).filter(User.email == email.lower().strip()).first()
        
        if not user:
            return False, None, None, None, "Email not found. Please sign up first."
        
        if not user.is_active:
            return False, None, None, None, "Account is deactivated. Contact support."
        
        if not user.password_hash:
            return False, None, None, None, "Please use Google Sign In for this account."
        
        if not verify_password(password, user.password_hash):
            return False, None, None, None, "Incorrect password."
        
        # Check if entity setup is complete (for clients)
        entity_id = None
        if user.role == UserRole.CLIENT:
            entity = db.query(EntityProfile).filter(EntityProfile.user_id == user.user_id).first()
            if entity:
                entity_id = entity.entity_id
                if not entity.is_setup_complete:
                    st.session_state.setup_complete = False
                else:
                    st.session_state.setup_complete = True
            else:
                st.session_state.setup_complete = False
        
        # RETURN 5 VALUES: Success, UserID, Role, EntityID, Message
        return True, user.user_id, user.role.value, entity_id, "Login Successful"
    
    except Exception as e:
        return False, None, None, None, f"Login error: {str(e)}"
    finally:
        db.close()

# Google OAuth Placeholder
def google_signin():
    st.info("🚧 Google Sign-In integration coming soon! For now, use email/password.")
    return False, None, None, None
    
