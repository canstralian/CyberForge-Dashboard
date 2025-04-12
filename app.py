import streamlit as st
from streamlit_extras.app_logo import add_logo
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
import streamlit.components.v1 as components

from components.dashboard import render_dashboard
from components.threats import render_threats
from components.monitoring import render_monitoring
from components.alerts import render_alerts
from components.reports import render_reports

# Page configuration
st.set_page_config(
    page_title="CyberForge | Dark Web OSINT Platform",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match design requirements
# Note: Minimal custom styling to enhance Streamlit's native appearance
st.markdown("""
<style>
    .main {
        background-color: #1A1A1A;
    }
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2C3E50;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        color: #ECF0F1;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2C3E50;
        border-bottom: 2px solid #E74C3C;
    }
    .css-1qg05tj {
        color: #ECF0F1;
    }
    div[data-testid="stHeader"] {
        background-color: #1A1A1A;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Logo and app title
    st.image("assets/cyberforge_logo.svg", width=250)
    
    st.markdown("### **CyberForge**")
    st.markdown("#### Dark Web OSINT Platform")
    st.markdown("---")
    
    # Navigation
    st.subheader("Navigation")
    selected_page = st.radio(
        "Select a page",
        ["Dashboard", "Threat Detection", "Monitoring", "Alerts", "Reports"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # User profile placeholder
    with st.container():
        cols = st.columns([1, 3])
        with cols[0]:
            st.image("https://images.unsplash.com/photo-1590494165264-1ebe3602eb80", width=60)
        with cols[1]:
            st.markdown("**Security Analyst**")
            st.markdown("Online")
    
    st.markdown("---")
    
    # System status
    st.subheader("System Status")
    system_status = {
        "API Connection": "✅ Connected",
        "Dark Web Crawler": "✅ Active",
        "Data Processing": "✅ Running",
        "Alert System": "✅ Operational"
    }
    
    for key, value in system_status.items():
        cols = st.columns([3, 2])
        cols[0].write(key)
        cols[1].write(value)
    
    st.markdown("---")
    
    # Version information
    st.caption("CyberForge OSINT Platform v1.0.0")
    st.caption("© 2025 Chemically Motivated Solutions")

# Main content based on selected page
if selected_page == "Dashboard":
    render_dashboard()
elif selected_page == "Threat Detection":
    render_threats()
elif selected_page == "Monitoring":
    render_monitoring()
elif selected_page == "Alerts":
    render_alerts()
elif selected_page == "Reports":
    render_reports()
