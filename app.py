import streamlit as st
from streamlit_extras.app_logo import add_logo
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
import streamlit.components.v1 as components
import time
from datetime import datetime

from components.dashboard import render_dashboard
from components.threats import render_threats
from components.monitoring import render_monitoring
from components.alerts import render_alerts
from components.reports import render_reports
from components.live_feed import render_live_feed, render_content_analysis
from components.web_scraper import render_web_scraper_ui

# Page configuration
st.set_page_config(
    page_title="CyberForge | Dark Web OSINT Platform",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to match design requirements and improve UI/UX
st.markdown("""
<style>
    /* Base styling */
    .main {
        background-color: #1A1A1A;
    }
    .stApp {
        font-family: 'JetBrains Mono', 'Inter', monospace, sans-serif;
    }
    
    /* Custom card styling */
    div.card {
        background-color: #2C3E50;
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border-left: 4px solid #E74C3C;
    }
    
    /* Button enhancements */
    .stButton button {
        border-radius: 4px;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 6px;
    }
    .status-active {
        background-color: #2ECC71;
        box-shadow: 0 0 8px #2ECC71;
    }
    .status-warning {
        background-color: #F1C40F;
        box-shadow: 0 0 8px #F1C40F;
    }
    .status-error {
        background-color: #E74C3C;
        box-shadow: 0 0 8px #E74C3C;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #2C3E50;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        color: #ECF0F1;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2C3E50;
        border-bottom: 2px solid #E74C3C;
        transform: translateY(-2px);
    }
    
    /* Header styling */
    div[data-testid="stHeader"] {
        background-color: #1A1A1A;
    }
    
    /* Metric styling */
    div[data-testid="metric-container"] {
        background-color: #2C3E5030;
        border-radius: 6px;
        padding: 10px;
        border-left: 3px solid #3498DB;
    }
    
    /* Text color */
    .css-1qg05tj, .css-10trblm, p, h1, h2, h3, .stMarkdown {
        color: #ECF0F1 !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        border-radius: 6px;
        overflow: hidden;
    }
    .dataframe th {
        background-color: #2C3E50 !important;
        color: #ECF0F1 !important;
    }
    
    /* Sidebar refinements */
    section[data-testid="stSidebar"] {
        background-color: #1A1A1A;
        border-right: 1px solid #2C3E50;
    }
    section[data-testid="stSidebar"] .stRadio label {
        background-color: #2C3E5030;
        padding: 10px;
        border-radius: 4px;
        margin-bottom: 5px;
        transition: all 0.2s ease;
    }
    section[data-testid="stSidebar"] .stRadio label:hover {
        background-color: #2C3E5050;
    }
    
    /* Custom loading animation */
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    .loading-pulse {
        animation: pulse 1.5s infinite ease-in-out;
    }
    
    /* Alert and notification styling */
    div.stAlert {
        border-radius: 6px;
        border-width: 1px;
    }
    
    /* Progress bar improvements */
    div[data-testid="stProgressBar"] > div {
        background-color: #E74C3C;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for notifications
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
    st.session_state.last_notification_time = datetime.now()
    st.session_state.notification_count = 0

# Add a new notification
def add_notification(title, message, severity="info", icon="🔔"):
    now = datetime.now()
    st.session_state.notifications.insert(0, {
        "id": len(st.session_state.notifications),
        "title": title,
        "message": message,
        "severity": severity,
        "icon": icon,
        "time": now,
        "read": False
    })
    st.session_state.last_notification_time = now
    st.session_state.notification_count += 1

# Add initial notifications if none exist
if len(st.session_state.notifications) == 0:
    add_notification(
        "Welcome to CyberForge OSINT Platform",
        "Your dark web intelligence dashboard is ready.",
        "info",
        "👋"
    )
    add_notification(
        "New Dark Web Mentions Detected",
        "3 mentions of your organization found on dark web forums.",
        "warning",
        "⚠️"
    )
    add_notification(
        "Credential Leak Detected",
        "Potential credential leak affecting your domain.",
        "danger",
        "🚨"
    )

# Sidebar with enhanced UI
with st.sidebar:
    # Logo and app title with animation effect on load
    st.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <img src='https://raw.githubusercontent.com/yourusername/cyberforge/main/assets/logo.svg' width='200'>
    </div>
    """, unsafe_allow_html=True)
    
    st.image("assets/cyberforge_logo.svg", width=250)
    
    st.markdown("<h3 style='text-align: center; margin-top: 0;'><strong>CyberForge</strong></h3>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; margin-top: -15px; opacity: 0.8;'>Dark Web OSINT Platform</h4>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Navigation with improved interactive elements
    st.subheader("Navigation")
    selected_page = st.radio(
        "Select a page",
        ["Dashboard", "Live Feed", "Threat Detection", "Monitoring", "Alerts", "Reports", "Content Analysis", "Web Scraper"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # User profile with enhanced styling
    with st.container():
        cols = st.columns([1, 3])
        with cols[0]:
            st.image("https://images.unsplash.com/photo-1590494165264-1ebe3602eb80", width=60)
        with cols[1]:
            st.markdown("<div style='line-height: 1.2;'><strong>Security Analyst</strong><br><span style='color: #2ECC71; font-size: 0.8em;'>● Online</span></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Notifications center
    notification_expander = st.expander(f"Notifications ({sum(1 for n in st.session_state.notifications if not n['read'])})")
    with notification_expander:
        if st.session_state.notifications:
            for i, notification in enumerate(st.session_state.notifications[:5]):  # Show only 5 most recent
                # Format time as relative (e.g., "2 mins ago")
                time_diff = datetime.now() - notification["time"]
                minutes_ago = time_diff.total_seconds() / 60
                
                if minutes_ago < 1:
                    time_str = "just now"
                elif minutes_ago < 60:
                    time_str = f"{int(minutes_ago)} min ago"
                else:
                    hours = int(minutes_ago / 60)
                    time_str = f"{hours} hrs ago"
                
                # Determine notification color
                if notification["severity"] == "danger":
                    color = "#E74C3C"
                elif notification["severity"] == "warning":
                    color = "#F1C40F"
                else:
                    color = "#3498DB"
                
                # Display notification with custom styling
                st.markdown(f"""
                <div style="margin-bottom: 10px; padding: 8px; border-left: 3px solid {color}; background-color: rgba(44, 62, 80, 0.3); border-radius: 4px;">
                    <div style="display: flex; justify-content: space-between;">
                        <div style="font-weight: bold; color: {color};">{notification["icon"]} {notification["title"]}</div>
                        <div style="font-size: 0.7em; opacity: 0.7;">{time_str}</div>
                    </div>
                    <div style="font-size: 0.9em; margin-top: 5px;">{notification["message"]}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Mark as read when clicked
                if not notification["read"]:
                    if st.button("Mark as read", key=f"read_{i}", help="Mark this notification as read"):
                        st.session_state.notifications[i]["read"] = True
                        st.experimental_rerun()
        else:
            st.info("No notifications")
    
    st.markdown("---")
    
    # System status with improved visual indicators
    st.subheader("System Status")
    
    # Simulated system metrics with visual indicators
    system_status = {
        "API Connection": {"status": "active", "value": "Connected", "details": "Latency: 42ms"},
        "Dark Web Crawler": {"status": "active", "value": "Active", "details": "12 sources"},
        "Data Processing": {"status": "active", "value": "Running", "details": "Load: 47%"},
        "Alert System": {"status": "active", "value": "Operational", "details": "No delays"}
    }
    
    for key, data in system_status.items():
        status_class = f"status-{data['status']}"
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px; padding: 8px; background-color: rgba(44, 62, 80, 0.2); border-radius: 4px;">
            <div>
                <span class="status-indicator {status_class}"></span>
                {key}
            </div>
            <div style="text-align: right; opacity: 0.9;">
                <div>{data['value']}</div>
                <div style="font-size: 0.7em; opacity: 0.7;">{data['details']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Version information
    current_time = datetime.now().strftime("%H:%M:%S")
    st.caption(f"CyberForge OSINT Platform v1.1.0")
    st.caption(f"Last scan: {current_time} | © 2025 CMS")

# Main content based on selected page with enhanced transitions
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
elif selected_page == "Live Feed":
    render_live_feed()
elif selected_page == "Content Analysis":
    render_content_analysis()
elif selected_page == "Web Scraper":
    render_web_scraper_ui()

# Add a floating action button for quick actions
st.markdown("""
<style>
.fab {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background-color: #E74C3C;
    color: white;
    text-align: center;
    line-height: 60px;
    font-size: 24px;
    cursor: pointer;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    z-index: 9999;
    transition: all 0.3s ease;
}
.fab:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 12px rgba(0,0,0,0.4);
}
</style>
<div class="fab" onclick="document.body.dispatchEvent(new Event('fab_click'))" title="Quick Actions">+</div>
""", unsafe_allow_html=True)

# Custom JavaScript to handle FAB click and open a modal
components.html("""
<script>
document.body.addEventListener('fab_click', function() {
    window.parent.postMessage({type: 'fab_click'}, '*');
});
</script>
""", height=0)

# Check for FAB click event
if st.session_state.get('fab_clicked', False):
    with st.form(key='quick_action_form'):
        st.subheader("Quick Actions")
        action = st.selectbox("Choose an action", [
            "Run Full Scan", 
            "Generate Threat Report", 
            "Create Alert Rule", 
            "Add Monitoring Keywords",
            "Export Dashboard"
        ])
        submitted = st.form_submit_button("Execute")
        if submitted:
            with st.spinner("Executing action..."):
                time.sleep(2)  # Simulate processing
                st.success(f"Action '{action}' executed successfully!")
                st.session_state.fab_clicked = False

# Easter egg - execute when a specific key combination is pressed
components.html("""
<script>
// Easter egg listener
let keys = [];
window.addEventListener('keydown', (e) => {
    keys.push(e.key);
    keys = keys.slice(-10);
    if (keys.join('').includes('darkweb')) {
        window.parent.postMessage({type: 'easter_egg'}, '*');
    }
});
</script>
""", height=0)
