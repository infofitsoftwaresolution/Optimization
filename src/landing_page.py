"""Modern landing page for BellaTrix LLM Evaluation Framework"""

import streamlit as st
from src.auth import is_authenticated


def render_landing_page():
    """Render the modern landing page"""
    
    # Hide default Streamlit elements
    st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stApp {
            background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Main landing page CSS
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }
        
        .landing-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }
        
        /* Hero Section */
        .hero-section {
            min-height: 90vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 4rem 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 30px;
            margin: 2rem 0;
            position: relative;
            overflow: hidden;
        }
        
        .hero-section::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 8s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        
        .hero-content {
            position: relative;
            z-index: 1;
            color: white;
        }
        
        .hero-title {
            font-size: 4.5rem;
            font-weight: 800;
            margin: 0 0 1.5rem 0;
            line-height: 1.1;
            background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: fadeInUp 0.8s ease-out;
        }
        
        .hero-subtitle {
            font-size: 1.5rem;
            font-weight: 400;
            margin: 0 0 2.5rem 0;
            opacity: 0.95;
            max-width: 700px;
            margin-left: auto;
            margin-right: auto;
            animation: fadeInUp 1s ease-out;
        }
        
        .hero-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            flex-wrap: wrap;
            animation: fadeInUp 1.2s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .cta-button {
            padding: 1rem 2.5rem;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 12px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        
        .cta-primary {
            background: white;
            color: #667eea;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .cta-primary:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        
        .cta-secondary {
            background: rgba(255,255,255,0.2);
            color: white;
            border: 2px solid white;
            backdrop-filter: blur(10px);
        }
        
        .cta-secondary:hover {
            background: rgba(255,255,255,0.3);
            transform: translateY(-3px);
        }
        
        /* Features Section */
        .features-section {
            padding: 5rem 2rem;
            background: white;
        }
        
        .section-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: #1a1a1a;
        }
        
        .section-subtitle {
            text-align: center;
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 4rem;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }
        
        .feature-card {
            background: white;
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 5px 25px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
            border: 1px solid #f0f0f0;
        }
        
        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 15px 40px rgba(102, 126, 234, 0.15);
            border-color: #667eea;
        }
        
        .feature-icon {
            font-size: 3rem;
            margin-bottom: 1.5rem;
            display: block;
        }
        
        .feature-title {
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #1a1a1a;
        }
        
        .feature-description {
            font-size: 1rem;
            color: #666;
            line-height: 1.6;
        }
        
        /* Stats Section */
        .stats-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 4rem 2rem;
            border-radius: 30px;
            margin: 3rem 0;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
            text-align: center;
        }
        
        .stat-item {
            color: white;
        }
        
        .stat-number {
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }
        
        .stat-label {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        /* CTA Section */
        .cta-section {
            text-align: center;
            padding: 5rem 2rem;
            background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        }
        
        .cta-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: #1a1a1a;
        }
        
        .cta-description {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 2.5rem;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        
        /* Streamlit Button Styling */
        .stButton > button[kind="primary"] {
            background: white !important;
            color: #667eea !important;
            border: none !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            padding: 1rem 2rem !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2) !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 15px 40px rgba(0,0,0,0.3) !important;
        }
        
        .stButton > button:not([kind="primary"]) {
            background: rgba(255,255,255,0.2) !important;
            color: white !important;
            border: 2px solid white !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            padding: 1rem 2rem !important;
            border-radius: 12px !important;
            backdrop-filter: blur(10px) !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton > button:not([kind="primary"]):hover {
            background: rgba(255,255,255,0.3) !important;
            transform: translateY(-3px) !important;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .hero-title {
                font-size: 2.5rem;
            }
            
            .hero-subtitle {
                font-size: 1.2rem;
            }
            
            .features-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Section with embedded buttons
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <h1 class="hero-title">🚀 BellaTrix</h1>
            <p class="hero-subtitle">
                Enterprise-Grade LLM Performance & Cost Analytics Platform
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero buttons positioned below hero section
    st.markdown('<div style="margin-top: -80px; position: relative; z-index: 10;">', unsafe_allow_html=True)
    hero_col1, hero_col2, hero_col3, hero_col4, hero_col5 = st.columns([1, 1, 2, 1, 1])
    with hero_col3:
        hero_btn_col1, hero_btn_col2 = st.columns(2)
        with hero_btn_col1:
            if st.button("🚀 Get Started Free", use_container_width=True, key="hero_signup", type="primary"):
                st.session_state.page = 'signup'
                st.rerun()
        with hero_btn_col2:
            if st.button("🔐 Sign In", use_container_width=True, key="hero_signin"):
                st.session_state.page = 'signin'
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Features Section
    st.markdown("""
    <div class="features-section">
        <h2 class="section-title">Powerful Features</h2>
        <p class="section-subtitle">
            Everything you need to evaluate, compare, and optimize your LLM models
        </p>
        <div class="features-grid">
            <div class="feature-card">
                <span class="feature-icon">📊</span>
                <h3 class="feature-title">Multi-Model Evaluation</h3>
                <p class="feature-description">
                    Test multiple AWS Bedrock models simultaneously with the same prompts. 
                    Compare performance, latency, and costs side-by-side.
                </p>
            </div>
            <div class="feature-card">
                <span class="feature-icon">💰</span>
                <h3 class="feature-title">Cost Optimization</h3>
                <p class="feature-description">
                    Track token usage and costs in real-time. Identify the most 
                    cost-effective models for your use case.
                </p>
            </div>
            <div class="feature-card">
                <span class="feature-icon">⚡</span>
                <h3 class="feature-title">Performance Analytics</h3>
                <p class="feature-description">
                    Comprehensive latency metrics with percentile analysis. 
                    Understand response times and optimize for speed.
                </p>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🔍</span>
                <h3 class="feature-title">JSON Validation</h3>
                <p class="feature-description">
                    Automatic JSON validation and parsing. Ensure your model 
                    outputs meet your format requirements.
                </p>
            </div>
            <div class="feature-card">
                <span class="feature-icon">📈</span>
                <h3 class="feature-title">Interactive Dashboards</h3>
                <p class="feature-description">
                    Beautiful, interactive visualizations with Plotly. 
                    Export data as CSV for further analysis.
                </p>
            </div>
            <div class="feature-card">
                <span class="feature-icon">☁️</span>
                <h3 class="feature-title">CloudWatch Integration</h3>
                <p class="feature-description">
                    Upload and parse CloudWatch logs. Extract prompts and 
                    metrics from your production logs.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Section
    st.markdown("""
    <div class="stats-section">
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-number">100+</div>
                <div class="stat-label">Models Supported</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">99.9%</div>
                <div class="stat-label">Uptime</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">24/7</div>
                <div class="stat-label">Monitoring</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">Real-time</div>
                <div class="stat-label">Analytics</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Final CTA Section
    st.markdown("""
    <div class="cta-section">
        <h2 class="cta-title">Ready to Optimize Your LLM Performance?</h2>
        <p class="cta-description">
            Join teams using BellaTrix to make data-driven decisions about their LLM infrastructure.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Final CTA buttons using Streamlit
    cta_col1, cta_col2, cta_col3, cta_col4, cta_col5 = st.columns([1, 1, 2, 1, 1])
    with cta_col3:
        cta_btn_col1, cta_btn_col2 = st.columns(2)
        with cta_btn_col1:
            if st.button("🚀 Start Free Trial", use_container_width=True, key="cta_signup", type="primary"):
                st.session_state.page = 'signup'
                st.rerun()
        with cta_btn_col2:
            if st.button("🔐 Sign In", use_container_width=True, key="cta_signin"):
                st.session_state.page = 'signin'
                st.rerun()

