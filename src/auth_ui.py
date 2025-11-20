"""Authentication UI components for sign-in and sign-up pages"""

import streamlit as st
from src.auth import sign_in, sign_up, is_authenticated, sign_out, get_current_user


def render_sign_in_page():
    """Render the sign-in page"""
    
    # Custom CSS for auth pages
    st.markdown("""
    <style>
        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
        }
        .auth-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .auth-header h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .stButton>button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem;
            border-radius: 8px;
            font-weight: 600;
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%);
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-header"><h1>🔐 Sign In</h1><p>Welcome back to BellaTrix</p></div>', unsafe_allow_html=True)
        
        with st.form("signin_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit_button = st.form_submit_button("Sign In", use_container_width=True)
            with col_btn2:
                switch_to_signup = st.form_submit_button("Sign Up", use_container_width=True)
            
            if submit_button:
                success, message = sign_in(username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.username = username.strip().lower()
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            
            if switch_to_signup:
                st.session_state.page = 'signup'
                st.rerun()
        
        st.markdown("---")
        st.markdown('<p style="text-align: center; color: #666;">Don\'t have an account? Click "Sign Up" above</p>', unsafe_allow_html=True)


def render_sign_up_page():
    """Render the sign-up page"""
    
    # Custom CSS for auth pages
    st.markdown("""
    <style>
        .auth-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
        }
        .auth-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .auth-header h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        .stButton>button {
            width: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem;
            border-radius: 8px;
            font-weight: 600;
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%);
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-header"><h1>📝 Sign Up</h1><p>Create your BellaTrix account</p></div>', unsafe_allow_html=True)
        
        with st.form("signup_form"):
            username = st.text_input("Username", placeholder="Choose a username")
            email = st.text_input("Email", placeholder="Enter your email address")
            password = st.text_input("Password", type="password", placeholder="Create a password (min 6 characters)")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit_button = st.form_submit_button("Sign Up", use_container_width=True)
            with col_btn2:
                switch_to_signin = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit_button:
                # Validate passwords match
                if password != confirm_password:
                    st.error("Passwords do not match. Please try again.")
                else:
                    success, message = sign_up(username, email, password)
                    if success:
                        st.success(message)
                        st.info("Redirecting to sign in page...")
                        st.session_state.page = 'signin'
                        st.rerun()
                    else:
                        st.error(message)
            
            if switch_to_signin:
                st.session_state.page = 'signin'
                st.rerun()
        
        st.markdown("---")
        st.markdown('<p style="text-align: center; color: #666;">Already have an account? Click "Sign In" above</p>', unsafe_allow_html=True)

