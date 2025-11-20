"""Authentication module for user sign-in and sign-up"""

import streamlit as st
import json
import bcrypt
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Tuple

# Path to users database
USERS_DB_PATH = Path(__file__).parent.parent / "data" / "users.json"


def init_users_db():
    """Initialize the users database file if it doesn't exist"""
    USERS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_DB_PATH.exists():
        with open(USERS_DB_PATH, 'w') as f:
            json.dump({}, f)


def load_users() -> Dict:
    """Load users from the database"""
    init_users_db()
    try:
        with open(USERS_DB_PATH, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_users(users: Dict):
    """Save users to the database"""
    init_users_db()
    with open(USERS_DB_PATH, 'w') as f:
        json.dump(users, f, indent=2)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against a hash"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def sign_up(username: str, email: str, password: str) -> Tuple[bool, str]:
    """
    Register a new user
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    users = load_users()
    
    # Validate input
    if not username or not username.strip():
        return False, "Username cannot be empty"
    
    if not email or not email.strip():
        return False, "Email cannot be empty"
    
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    username = username.strip().lower()
    email = email.strip().lower()
    
    # Check if username already exists
    if username in users:
        return False, "Username already exists. Please choose a different one."
    
    # Check if email already exists
    for user_data in users.values():
        if user_data.get('email', '').lower() == email:
            return False, "Email already registered. Please use a different email."
    
    # Create new user
    users[username] = {
        'email': email,
        'password_hash': hash_password(password),
        'created_at': datetime.now().isoformat(),
        'last_login': None
    }
    
    save_users(users)
    return True, "Account created successfully! You can now sign in."


def sign_in(username: str, password: str) -> Tuple[bool, str]:
    """
    Authenticate a user
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    users = load_users()
    username = username.strip().lower()
    
    if not username or not password:
        return False, "Please enter both username and password"
    
    if username not in users:
        return False, "Invalid username or password"
    
    user_data = users[username]
    
    if not verify_password(password, user_data['password_hash']):
        return False, "Invalid username or password"
    
    # Update last login
    user_data['last_login'] = datetime.now().isoformat()
    save_users(users)
    
    return True, "Sign in successful!"


def is_authenticated() -> bool:
    """Check if user is currently authenticated"""
    return st.session_state.get('authenticated', False)


def get_current_user() -> Optional[str]:
    """Get the current authenticated username"""
    if is_authenticated():
        return st.session_state.get('username')
    return None


def sign_out():
    """Sign out the current user"""
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()


def require_auth():
    """Decorator/function to require authentication - redirects to sign-in if not authenticated"""
    if not is_authenticated():
        st.session_state.page = 'signin'
        st.rerun()


