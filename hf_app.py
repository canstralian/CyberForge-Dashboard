"""
CyberForge Dashboard - Hugging Face Spaces Version
"""
import os
import sys
import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.colored_header import colored_header

# Check if we're running on Hugging Face Spaces
is_huggingface = os.environ.get('SPACE_ID') is not None

# Set the page config
st.set_page_config(
    page_title="CyberForge Dashboard",
    page_icon="🕵️‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
    }
    .sidebar .sidebar-content {
        background-color: #262730;
    }
    h1, h2, h3 {
        color: #f8f9fa;
    }
    .cybertext {
        color: #00ff8d;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

# Choose between HF demo mode or regular mode
if is_huggingface:
    # Initialize in-memory database for Hugging Face
    import hf_database
    st.session_state.is_demo = True
    
    # Show demo mode banner
    st.warning("⚠️ Running in Hugging Face Spaces DEMO MODE. Data is stored in-memory and will be reset when the space restarts.")
else:
    # Regular database initialization
    import src.database_init
    
# Import components
from components.dashboard import render_dashboard
from components.threats import render_threats
from components.monitoring import render_monitoring
from components.alerts import render_alerts
from components.reports import render_reports
from components.live_feed import render_live_feed, render_content_analysis
from components.web_scraper import render_web_scraper_ui

# Custom notification function
def add_notification(title, message, severity="info", icon="🔔"):
    """Add a notification to the session state"""
    if "notifications" not in st.session_state:
        st.session_state.notifications = []
    
    # Add notification with timestamp
    import time
    notification = {
        "id": int(time.time() * 1000),
        "title": title,
        "message": message,
        "severity": severity,
        "icon": icon,
        "read": False,
        "timestamp": time.time()
    }
    st.session_state.notifications.insert(0, notification)

# Initialize notifications if needed
if "notifications" not in st.session_state:
    st.session_state.notifications = []

# Sidebar navigation
with st.sidebar:
    st.image("assets/cyberforge_logo.svg", width=200)
    st.title("CyberForge")
    
    # Demo badge
    if st.session_state.get("is_demo", False):
        st.markdown("#### 🔍 Demo Mode")
    
    st.markdown("---")
    
    # Navigation
    nav_selection = st.radio(
        "Navigation",
        ["Dashboard", "Threats", "Monitoring", "Alerts", "Reports", "Live Feed", "Content Analysis", "Web Scraper"]
    )
    
    # User information
    st.markdown("---")
    st.markdown("### User Info")
    if st.session_state.get("is_demo", False):
        st.markdown("👤 **Admin User** (Demo)")
        st.markdown("🔑 Role: Administrator")
    else:
        st.markdown("👤 **Analyst**")
        st.markdown("🔑 Role: Security Analyst")
    
    # Notification count
    unread_count = sum(1 for n in st.session_state.notifications if not n["read"])
    if unread_count > 0:
        st.markdown(f"🔔 **{unread_count}** unread notifications")
    
    # Credits
    st.markdown("---")
    st.markdown("### CyberForge v1.0")
    st.markdown("© 2025 Chemically Motivated Solutions")
    
    # HF badge if on Hugging Face
    if is_huggingface:
        st.markdown("---")
        st.markdown("""
        <a href="https://huggingface.co/spaces" target="_blank">
        <img src="https://img.shields.io/badge/Hosted%20on-HF%20Spaces-blue" alt="HuggingFace Spaces"/>
        </a>
        """, unsafe_allow_html=True)

# Main content area
if nav_selection == "Dashboard":
    render_dashboard()
elif nav_selection == "Threats":
    render_threats()
elif nav_selection == "Monitoring":
    render_monitoring()
elif nav_selection == "Alerts":
    render_alerts()
elif nav_selection == "Reports":
    render_reports()
elif nav_selection == "Live Feed":
    render_live_feed()
elif nav_selection == "Content Analysis":
    render_content_analysis()
elif nav_selection == "Web Scraper":
    render_web_scraper_ui()