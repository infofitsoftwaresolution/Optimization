"""Authentication module for user sign-in and sign-up"""

import streamlit as st
import bcrypt
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.exc import IntegrityError
from database.connection import get_db_session
from database.models import User
import logging

logger = logging.getLogger(__name__)


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
    Register a new user in the database
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Validate input
    if not username or not username.strip():
        return False, "Username cannot be empty"
    
    if not email or not email.strip():
        return False, "Email cannot be empty"
    
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long"
    
    username = username.strip().lower()
    email = email.strip().lower()
    
    try:
        with get_db_session() as session:
            # Check if username already exists
            existing_user = session.query(User).filter(
                User.username == username
            ).first()
            if existing_user:
                return False, "Username already exists. Please choose a different one."
            
            # Check if email already exists
            existing_email = session.query(User).filter(
                User.email == email
            ).first()
            if existing_email:
                return False, "Email already registered. Please use a different email."
            
            # Create new user
            new_user = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                is_active=True,
                is_admin=False
            )
            
            session.add(new_user)
            session.commit()
            
            logger.info(f"New user registered: {username} ({email})")
            return True, "Account created successfully! You can now sign in."
            
    except IntegrityError as e:
        logger.error(f"Database integrity error during sign up: {e}")
        return False, "Registration failed. Username or email may already exist."
    except Exception as e:
        logger.error(f"Error during sign up: {e}", exc_info=True)
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Full traceback: {error_details}")
        return False, f"Registration failed: {str(e)}. Please check server logs."


def sign_in(username_or_email: str, password: str) -> Tuple[bool, str, Optional[dict]]:
    """
    Authenticate a user by username or email
    
    Args:
        username_or_email: Username or email address
        password: User password
    
    Returns:
        Tuple of (success: bool, message: str, user_info: dict or None)
        user_info contains: {'id': user_id, 'username': username, 'email': email}
    """
    if not username_or_email or not password:
        return False, "Please enter both username/email and password", None
    
    username_or_email = username_or_email.strip().lower()
    
    try:
        with get_db_session() as session:
            # Try to find user by username or email
            user = session.query(User).filter(
                (User.username == username_or_email) | (User.email == username_or_email)
            ).first()
            
            if not user:
                return False, "Invalid username/email or password", None
            
            # Check if user is active
            if not user.is_active:
                return False, "Account is inactive. Please contact administrator.", None
            
            # Verify password
            if not verify_password(password, user.password_hash):
                return False, "Invalid username/email or password", None
            
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            session.commit()
            
            user_info = {
                'id': str(user.id),
                'username': user.username,
                'email': user.email
            }
            
            logger.info(f"User signed in: {user.username} ({user.email})")
            return True, "Sign in successful!", user_info
            
    except Exception as e:
        logger.error(f"Error during sign in: {e}", exc_info=True)
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Full traceback: {error_details}")
        return False, f"Sign in failed: {str(e)}. Please check server logs.", None


def is_authenticated() -> bool:
    """Check if user is currently authenticated"""
    return st.session_state.get('authenticated', False)


def get_current_user() -> Optional[str]:
    """Get the current authenticated username"""
    if is_authenticated():
        return st.session_state.get('username')
    return None


def get_current_user_id() -> Optional[str]:
    """Get the current authenticated user ID (UUID)"""
    if is_authenticated():
        return st.session_state.get('user_id')
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


