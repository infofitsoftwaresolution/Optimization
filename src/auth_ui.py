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
            username_or_email = st.text_input(
                "Username or Email", 
                placeholder="Enter your username or email",
                autocomplete="username",
                label_visibility="visible"
            )
            password = st.text_input(
                "Password", 
                type="password", 
                placeholder="Enter your password",
                autocomplete="current-password",
                label_visibility="visible"
            )
            
            submit_button = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit_button:
                success, message, user_info = sign_in(username_or_email, password)
                if success and user_info:
                    st.session_state.authenticated = True
                    st.session_state.username = user_info['username']
                    st.session_state.user_id = user_info['id']
                    st.session_state.user_email = user_info['email']
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
        
        st.markdown("---")
        st.markdown('<p style="text-align: center; color: #666;">Don\'t have an account?</p>', unsafe_allow_html=True)
        
        # Sign Up button outside the form for better reliability
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("📝 Create New Account", use_container_width=True, type="primary"):
                st.session_state.page = 'signup'
                st.rerun()


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
            username = st.text_input(
                "Username", 
                placeholder="Choose a username",
                autocomplete="username",
                label_visibility="visible"
            )
            email = st.text_input(
                "Email", 
                placeholder="Enter your email address",
                autocomplete="email",
                label_visibility="visible"
            )
            password = st.text_input(
                "Password", 
                type="password", 
                placeholder="Create a password (min 6 characters)",
                autocomplete="new-password",
                label_visibility="visible"
            )
            confirm_password = st.text_input(
                "Confirm Password", 
                type="password", 
                placeholder="Confirm your password",
                autocomplete="new-password",
                label_visibility="visible"
            )
            
            submit_button = st.form_submit_button("Sign Up", use_container_width=True, type="primary")
            
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
        
        st.markdown("---")
        st.markdown('<p style="text-align: center; color: #666;">Already have an account?</p>', unsafe_allow_html=True)
        
        # Sign In button outside the form for better reliability
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🔐 Sign In", use_container_width=True):
                st.session_state.page = 'signin'
                st.rerun()

