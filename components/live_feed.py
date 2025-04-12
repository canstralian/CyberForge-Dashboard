import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import random
import plotly.graph_objects as go
import trafilatura
import threading
import queue

# Global queue for storing live feed events
feed_queue = queue.Queue(maxsize=100)

# Sample dark web sources for simulation
DARK_WEB_SOURCES = [
    "AlphaBay Market", "BreachForums", "XSS Forum", "RaidForums", "DeepPaste", 
    "BlackHat Forum", "DarkLeak Site", "HackTown", "Exploit.in", "0day.today",
    "Telegram Channel: DarkLeaks", "Telegram Channel: DataBreach", "BitHunters IRC",
    "Genesis Market", "ASAP Market", "Tor Network: Hidden Services", "DarkNetLive"
]

# Sample event types and severities
EVENT_TYPES = {
    "Credential Leak": ["Critical", "High"],
    "Data Breach": ["Critical", "High", "Medium"],
    "Ransomware Activity": ["Critical", "High"],
    "Hacking Tool": ["Medium", "Low"],
    "Zero-day Exploit": ["Critical", "High"],
    "Phishing Campaign": ["High", "Medium"],
    "Dark Web Mention": ["Medium", "Low"],
    "PII Exposure": ["Critical", "High"],
    "New Marketplace Listing": ["Medium", "Low"],
    "Threat Actor Communication": ["High", "Medium"],
    "Malware Sample": ["High", "Medium", "Low"],
    "Source Code Leak": ["High", "Medium"]
}

# Keywords associated with your organization
MONITORED_KEYWORDS = [
    "company.com", "companyname", "company name", "CompanyX", "ServiceY", "ProductZ",
    "company database", "company credentials", "company breach", "company leak",
    "@company.com", "CEO Name", "CTO Name", "internal documents"
]

# Industries for sector-based alerts
INDUSTRIES = [
    "Healthcare", "Finance", "Technology", "Education", "Government", 
    "Manufacturing", "Retail", "Energy", "Telecommunications", "Transportation"
]

def generate_live_event():
    """Generate a simulated live dark web event for demonstration"""
    current_time = datetime.now()
    
    # Choose event type and severity
    event_type = random.choice(list(EVENT_TYPES.keys()))
    severity = random.choice(EVENT_TYPES[event_type])
    
    # Choose source
    source = random.choice(DARK_WEB_SOURCES)
    
    # Determine if it should mention a monitored keyword (higher chance for critical events)
    mention_keyword = random.random() < (0.8 if severity == "Critical" else 0.3)
    keyword = random.choice(MONITORED_KEYWORDS) if mention_keyword else None
    
    # Choose affected industry
    industry = random.choice(INDUSTRIES)
    
    # Generate description
    if keyword:
        descriptions = [
            f"Detected {event_type.lower()} involving {keyword}",
            f"{keyword} mentioned in context of {event_type.lower()}",
            f"Potential {event_type.lower()} related to {keyword}",
            f"New {severity.lower()} severity {event_type.lower()} containing {keyword}",
            f"Alert: {event_type} with reference to {keyword}"
        ]
    else:
        descriptions = [
            f"New {event_type} affecting {industry} sector",
            f"Detected {event_type.lower()} targeting {industry} organizations",
            f"Emerging {event_type.lower()} with {severity.lower()} impact",
            f"Potential {industry} sector {event_type.lower()} identified",
            f"{severity} {event_type} observed in {source}"
        ]
    
    description = random.choice(descriptions)
    
    # Generate event ID
    event_id = f"EVT-{current_time.strftime('%y%m%d')}-{random.randint(1000, 9999)}"
    
    # Create event dictionary
    event = {
        "id": event_id,
        "timestamp": current_time,
        "event_type": event_type,
        "severity": severity,
        "source": source,
        "description": description,
        "industry": industry,
        "relevant": mention_keyword
    }
    
    return event

def start_feed_generator():
    """Start background thread to generate feed events"""
    def generate_events():
        while True:
            # Generate a new event
            event = generate_live_event()
            
            # Add to queue, remove oldest if full
            if feed_queue.full():
                try:
                    feed_queue.get_nowait()
                except queue.Empty:
                    pass
            
            try:
                feed_queue.put_nowait(event)
            except queue.Full:
                pass
            
            # Sleep random interval (2-15 seconds)
            sleep_time = random.uniform(2, 15)
            time.sleep(sleep_time)
    
    # Start the background thread
    thread = threading.Thread(target=generate_events, daemon=True)
    thread.start()

def render_live_feed():
    st.title("Real-Time Dark Web Monitoring")
    
    # Initialize the feed generator if it's not already running
    if 'feed_initialized' not in st.session_state:
        start_feed_generator()
        st.session_state.feed_initialized = True
        st.session_state.feed_events = []
        st.session_state.last_update = datetime.now()
        
    # Dashboard layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown("### Monitoring Status")
        
        # Display monitoring metrics
        st.metric(
            label="Active Crawlers",
            value=str(random.randint(12, 18)),
            delta=str(random.randint(-2, 3))
        )
        
        st.metric(
            label="Sources Coverage",
            value=f"{random.randint(85, 98)}%",
            delta=f"{random.randint(-2, 3)}%"
        )
        
        st.metric(
            label="Scan Frequency",
            value=f"{random.randint(3, 7)} min",
            delta=f"{random.choice([-1, -0.5, 0, 0.5])} min",
            delta_color="inverse"
        )
        
        # Filters for live feed
        st.markdown("### Feed Filters")
        
        severity_filter = st.multiselect(
            "Severity",
            ["Critical", "High", "Medium", "Low"],
            default=["Critical", "High"]
        )
        
        source_type = st.multiselect(
            "Source Type",
            ["Market", "Forum", "Telegram", "IRC", "Paste Site", "Leak Site"],
            default=["Market", "Forum", "Leak Site"]
        )
        
        relevant_only = st.checkbox("Show Relevant Alerts Only", value=True)
        
        auto_refresh = st.checkbox("Auto-Refresh Feed", value=True)
        
        if st.button("Refresh Now"):
            st.session_state.last_update = datetime.now()
    
    with col2:
        st.markdown("### Live Intelligence Feed")
        
        # Get events from queue and merge with existing events
        new_events = []
        while not feed_queue.empty():
            try:
                new_events.append(feed_queue.get_nowait())
            except queue.Empty:
                break
        
        if new_events:
            st.session_state.feed_events = new_events + st.session_state.feed_events
            st.session_state.feed_events = st.session_state.feed_events[:100]  # Keep only 100 most recent
            st.session_state.last_update = datetime.now()
        
        # Filter events
        filtered_events = []
        for event in st.session_state.feed_events:
            if event["severity"] in severity_filter:
                if not relevant_only or event["relevant"]:
                    source_match = False
                    for s_type in source_type:
                        if s_type.lower() in event["source"].lower():
                            source_match = True
                            break
                    if source_match or not source_type:
                        filtered_events.append(event)
        
        # Display last updated time
        st.caption(f"Last updated: {st.session_state.last_update.strftime('%H:%M:%S')}")
        
        # Display events
        if not filtered_events:
            st.info("No events match your current filters. Adjust filters or wait for new events.")
        else:
            for i, event in enumerate(filtered_events[:20]):  # Show only 20 most recent
                # Determine the color based on severity
                if event["severity"] == "Critical":
                    severity_color = "#E74C3C"
                elif event["severity"] == "High":
                    severity_color = "#F1C40F"
                elif event["severity"] == "Medium":
                    severity_color = "#3498DB"
                else:
                    severity_color = "#2ECC71"
                
                # Event container with colored border based on severity
                with st.container():
                    cols = st.columns([3, 1])
                    
                    # Event details
                    with cols[0]:
                        st.markdown(f"""
                        <div style="border-left: 4px solid {severity_color}; padding-left: 10px;">
                            <span style="color: {severity_color}; font-weight: bold;">{event['severity']}</span> | {event['event_type']}
                            <br><span style="font-size: 0.9em;">{event['description']}</span>
                            <br><span style="font-size: 0.8em; color: #7F8C8D;">Source: {event['source']} | ID: {event['id']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Timestamp and actions
                    with cols[1]:
                        # Format time as relative (e.g., "2 mins ago")
                        time_diff = datetime.now() - event["timestamp"]
                        minutes_ago = time_diff.total_seconds() / 60
                        
                        if minutes_ago < 1:
                            time_str = "just now"
                        elif minutes_ago < 60:
                            time_str = f"{int(minutes_ago)} min ago"
                        else:
                            hours = int(minutes_ago / 60)
                            time_str = f"{hours} hrs ago"
                        
                        st.markdown(f"<span style='font-size: 0.8em;'>{time_str}</span>", unsafe_allow_html=True)
                        
                        # Action buttons
                        if st.button("Investigate", key=f"investigate_{i}"):
                            st.session_state.selected_event = event
                    
                    # Add a subtle divider
                    st.markdown("<hr style='margin: 5px 0; opacity: 0.2;'>", unsafe_allow_html=True)
    
    with col3:
        st.markdown("### Intelligence Summary")
        
        # Current severity distribution
        severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for event in st.session_state.feed_events:
            if event["severity"] in severity_counts:
                severity_counts[event["severity"]] += 1
        
        # Create donut chart for severity distribution
        fig = go.Figure(go.Pie(
            labels=list(severity_counts.keys()),
            values=list(severity_counts.values()),
            hole=.6,
            marker=dict(colors=['#E74C3C', '#F1C40F', '#3498DB', '#2ECC71'])
        ))
        
        fig.update_layout(
            showlegend=True,
            margin=dict(t=0, b=0, l=0, r=0),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=200
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top mentioned industries
        st.markdown("#### Top Targeted Industries")
        
        industry_counts = {}
        for event in st.session_state.feed_events:
            industry = event["industry"]
            industry_counts[industry] = industry_counts.get(industry, 0) + 1
        
        # Sort industries by count and take top 5
        top_industries = sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for industry, count in top_industries:
            st.markdown(f"• {industry}: **{count}** alerts")
        
        # Trending threats
        st.markdown("#### Trending Threats")
        
        event_type_counts = {}
        for event in st.session_state.feed_events:
            event_type = event["event_type"]
            event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1
        
        # Sort event types by count and take top 5
        top_threats = sorted(event_type_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        for threat, count in top_threats:
            st.markdown(f"• {threat}: **{count}** alerts")
        
        # Add a quick investigate button for the most recent critical event
        st.markdown("---")
        st.markdown("#### Urgent Action Required")
        
        critical_events = [e for e in st.session_state.feed_events if e["severity"] == "Critical"]
        if critical_events:
            latest_critical = critical_events[0]
            st.error(f"""
            **{latest_critical['event_type']}**  
            {latest_critical['description']}
            """)
            
            if st.button("Investigate Now", key="urgent_investigate"):
                st.session_state.selected_event = latest_critical
        else:
            st.success("No critical events requiring urgent attention")
    
    # If an event is selected for investigation, show details
    if 'selected_event' in st.session_state and st.session_state.selected_event:
        event = st.session_state.selected_event
        
        st.markdown("---")
        st.markdown("## Event Investigation")
        
        event_col1, event_col2 = st.columns([3, 1])
        
        with event_col1:
            st.markdown(f"### {event['event_type']}")
            st.markdown(f"**ID:** {event['id']}")
            st.markdown(f"**Description:** {event['description']}")
            st.markdown(f"**Source:** {event['source']}")
            st.markdown(f"**Industry:** {event['industry']}")
            st.markdown(f"**Detected:** {event['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
            st.markdown(f"**Severity:** {event['severity']}")
        
        with event_col2:
            severity_color = "#E74C3C" if event["severity"] == "Critical" else "#F1C40F" if event["severity"] == "High" else "#3498DB" if event["severity"] == "Medium" else "#2ECC71"
            
            st.markdown(f"""
            <div style="background-color: {severity_color}20; padding: 10px; border-radius: 5px; border-left: 4px solid {severity_color};">
                <h4 style="margin: 0; color: {severity_color};">Risk Assessment</h4>
                <p>Severity: <b>{event['severity']}</b></p>
                <p>Confidence: <b>{random.randint(70, 95)}%</b></p>
                <p>Impact: <b>{'High' if event['severity'] in ['Critical', 'High'] else 'Medium'}</b></p>
            </div>
            """, unsafe_allow_html=True)
        
        # Tabs for different investigation aspects
        inv_tab1, inv_tab2, inv_tab3 = st.tabs(["Analysis", "Similar Events", "Recommendations"])
        
        with inv_tab1:
            st.markdown("### Event Analysis")
            
            # Simulated content analysis
            st.markdown("#### Content Analysis")
            st.markdown("""
            This event represents a potential security incident that requires investigation. 
            The key indicators suggest this could be related to targeted activity against your organization 
            or the wider industry sector.
            
            **Key Indicators:**
            * Event type and severity level
            * Source credibility assessment
            * Contextual mentions and relationships
            * Temporal correlation with known threat activities
            """)
            
            # Simulated indicators of compromise
            st.markdown("#### Indicators of Compromise")
            ioc_data = {
                "IP Addresses": [f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}" for _ in range(3)],
                "Domains": [f"malicious{random.randint(100, 999)}.{random.choice(['com', 'net', 'org'])}" for _ in range(2)],
                "File Hashes": [f"{''.join(random.choices('0123456789abcdef', k=64))}" for _ in range(2)]
            }
            
            for ioc_type, items in ioc_data.items():
                st.markdown(f"**{ioc_type}:**")
                for item in items:
                    st.code(item)
        
        with inv_tab2:
            st.markdown("### Related Events")
            
            # Generate a few similar events
            similar_events = []
            for _ in range(3):
                similar_event = generate_live_event()
                similar_event["event_type"] = event["event_type"]
                similar_event["severity"] = random.choice(EVENT_TYPES[event["event_type"]])
                similar_event["timestamp"] = event["timestamp"] - timedelta(days=random.randint(1, 30))
                similar_events.append(similar_event)
            
            # Display similar events
            for i, similar in enumerate(similar_events):
                with st.container():
                    st.markdown(f"""
                    **{similar['event_type']} ({similar['severity']})**  
                    {similar['description']}  
                    *Detected: {similar['timestamp'].strftime('%Y-%m-%d')} | Source: {similar['source']}*
                    """)
                    
                    if i < len(similar_events) - 1:
                        st.markdown("---")
        
        with inv_tab3:
            st.markdown("### Recommended Actions")
            
            # Generic recommendations based on event type
            recommendations = {
                "Data Breach": [
                    "Verify if the leaked data belongs to your organization",
                    "Identify affected systems and users",
                    "Initiate your incident response plan",
                    "Prepare for potential notification requirements",
                    "Monitor for misuse of the compromised data"
                ],
                "Credential Leak": [
                    "Force password resets for affected accounts",
                    "Enable multi-factor authentication where possible",
                    "Monitor for unauthorized access attempts",
                    "Review privileged access controls",
                    "Scan for credentials used across multiple systems"
                ],
                "Ransomware Activity": [
                    "Verify backup integrity and availability",
                    "Isolate potentially affected systems",
                    "Review security controls for ransomware protection",
                    "Assess exposure to the specific ransomware variant",
                    "Prepare business continuity procedures"
                ],
                "Zero-day Exploit": [
                    "Assess if your systems use the affected software",
                    "Apply temporary mitigations or workarounds",
                    "Monitor vendor channels for patch availability",
                    "Increase monitoring for exploit attempts",
                    "Review defense-in-depth security controls"
                ],
                "Phishing Campaign": [
                    "Alert employees about the phishing campaign",
                    "Block identified phishing domains and URLs",
                    "Scan email systems for instances of the phishing message",
                    "Review security awareness training materials",
                    "Deploy additional email security controls"
                ],
                "Dark Web Mention": [
                    "Analyze context of the mention for potential threats",
                    "Review security for specifically mentioned assets",
                    "Increase monitoring for related activities",
                    "Brief relevant stakeholders on potential risks",
                    "Consider threat intelligence analysis for the mention"
                ]
            }
            
            # Get recommendations for the event type or use a default set
            event_recommendations = recommendations.get(
                event["event_type"], 
                ["Investigate the alert details", "Assess potential impact", "Verify if your organization is affected"]
            )
            
            # Display recommendations
            for rec in event_recommendations:
                st.markdown(f"- {rec}")
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                st.button("Add to Investigation Case", key="add_to_case")
            with col2:
                st.button("Mark as False Positive", key="mark_false_positive")
        
        # Close investigation button
        if st.button("Close Investigation", key="close_investigation"):
            del st.session_state.selected_event
    
    # Auto-refresh using a placeholder and empty to trigger rerun
    if auto_refresh:
        placeholder = st.empty()
        time.sleep(30)  # Refresh every 30 seconds
        placeholder.empty()
        st.rerun()

def fetch_dark_web_content(url):
    """
    Fetch content from a dark web site (simulated for demonstration).
    In a real application, this would connect to Tor network or similar.
    
    Args:
        url (str): The URL to fetch content from
        
    Returns:
        str: The extracted content
    """
    # In a real scenario, you would use specialized tools to access dark web
    # Here we'll simulate this with sample data
    
    if "forum" in url.lower():
        return """
        --------- Dark Web Forum Excerpt ---------
        
        User123: Looking for access to healthcare databases, paying premium
        
        DarkSeller: Have fresh dump from major hospital, 50K+ patient records with PII and insurance info
        
        User123: What's your price? Is it the Memorial Hospital data?
        
        DarkSeller: 45 BTC for the full database. Yes, it's from Memorial plus two smaller clinics.
        
        User456: I can vouch for DarkSeller, bought credentials last month, all valid.
        
        DarkSeller: Sample available for serious buyers. Payment via escrow only.
        """
    
    elif "market" in url.lower():
        return """
        --------- Dark Web Marketplace Listing ---------
        
        ITEM: Complete patient database from major US hospital
        SELLER: MedLeaks (Trusted Vendor ★★★★★)
        PRICE: 45 BTC
        
        DESCRIPTION:
        Fresh database dump containing 50,000+ complete patient records including:
        - Full names, DOB, SSN
        - Home addresses and contact information
        - Insurance policy details and ID numbers
        - Medical diagnoses and treatment codes
        - Billing information including payment methods
        
        Data verified and ready for immediate delivery. Suitable for identity theft, 
        insurance fraud, or targeted phishing campaigns.
        
        SHIPPING: Instant digital delivery via encrypted channel
        TERMS: No refunds, escrow available
        """
    
    else:
        return """
        --------- Dark Web Intelligence ---------
        
        Multiple sources reporting new ransomware operation targeting healthcare sector.
        Group appears to be using stolen credentials to access systems.
        
        Identified C2 infrastructure:
        - 185.212.x.x
        - 91.223.x.x
        - malware-delivery[.]xyz
        
        Ransom demands ranging from 20-50 BTC depending on organization size.
        Group is exfiltrating data before encryption and threatening publication.
        """

def render_content_analysis():
    """Display dark web content analysis tools"""
    st.markdown("### Dark Web Content Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("Enter a URL or paste content for analysis:")
        
        analysis_source = st.radio(
            "Content Source",
            ["URL", "Pasted Content"],
            horizontal=True
        )
        
        if analysis_source == "URL":
            url = st.text_input("Enter Dark Web URL", value="darkforum.onion/thread/healthcare-data")
            
            if st.button("Fetch Content", key="fetch_btn"):
                with st.spinner("Connecting to dark web. Please wait..."):
                    time.sleep(2)  # Simulate connection time
                    content = fetch_dark_web_content(url)
                    st.session_state.current_content = content
        else:
            content_input = st.text_area("Paste content for analysis", height=150)
            
            if st.button("Analyze Content", key="analyze_pasted"):
                st.session_state.current_content = content_input
    
    with col2:
        st.markdown("Analysis Options")
        
        analysis_type = st.selectbox(
            "Select Analysis Type",
            ["Entity Extraction", "Threat Detection", "Keyword Analysis", "IoC Extraction"]
        )
        
        st.markdown("---")
        
        st.markdown("Monitored Keywords")
        
        # Display monitored keywords
        keyword_columns = st.columns(2)
        
        for i, keyword in enumerate(MONITORED_KEYWORDS[:8]):  # Show only first 8
            with keyword_columns[i % 2]:
                st.markdown(f"• {keyword}")
        
        st.markdown("...")
        
        st.markdown("---")
        
        if st.button("Add Custom Keywords"):
            st.session_state.show_keyword_input = True
        
        if st.session_state.get("show_keyword_input", False):
            new_keyword = st.text_input("Enter new keyword")
            if st.button("Add Keyword"):
                if new_keyword and new_keyword not in MONITORED_KEYWORDS:
                    MONITORED_KEYWORDS.append(new_keyword)
                    st.success(f"Added keyword: {new_keyword}")
    
    # If we have content to analyze, show it and the analysis
    if hasattr(st.session_state, "current_content") and st.session_state.current_content:
        st.markdown("---")
        
        tabs = st.tabs(["Content", "Analysis", "Entities", "Indicators"])
        
        with tabs[0]:
            st.markdown("### Raw Content")
            st.text(st.session_state.current_content)
        
        with tabs[1]:
            st.markdown("### Content Analysis")
            
            # Identify any monitored keywords in content
            found_keywords = []
            for keyword in MONITORED_KEYWORDS:
                if keyword.lower() in st.session_state.current_content.lower():
                    found_keywords.append(keyword)
            
            if found_keywords:
                st.warning(f"Found {len(found_keywords)} monitored keywords in content:")
                for keyword in found_keywords:
                    st.markdown(f"• **{keyword}**")
            else:
                st.info("No monitored keywords found in content.")
            
            # Simple sentiment analysis
            text = st.session_state.current_content.lower()
            
            threat_terms = ["hack", "breach", "leak", "dump", "sell", "exploit", "vulnerability", 
                          "ransomware", "malware", "phishing", "attack", "threat"]
            
            threat_found = sum(term in text for term in threat_terms)
            
            if threat_found > 3:
                threat_level = "High"
                color = "#E74C3C"
            elif threat_found > 1:
                threat_level = "Medium"
                color = "#F1C40F"
            else:
                threat_level = "Low"
                color = "#2ECC71"
            
            st.markdown(f"**Threat Assessment: <span style='color:{color}'>{threat_level}</span>**", unsafe_allow_html=True)
            st.markdown(f"Identified {threat_found} threat indicators in the content.")
        
        with tabs[2]:
            st.markdown("### Entities Extracted")
            
            # Sample entity extraction
            entities = {
                "Organizations": ["Memorial Hospital", "MedLeaks"],
                "Monetary Values": ["45 BTC", "20-50 BTC"],
                "Quantities": ["50,000+ patient records", "50K+ patient records"],
                "Locations": [],
                "People": ["User123", "DarkSeller", "User456"]
            }
            
            for entity_type, items in entities.items():
                if items:
                    st.markdown(f"#### {entity_type}")
                    for item in items:
                        st.markdown(f"• {item}")
        
        with tabs[3]:
            st.markdown("### Indicators of Compromise")
            
            # Extract indicators from content
            iocs = {
                "IP Addresses": [],
                "Domains": [],
                "URLs": [],
                "Hashes": []
            }
            
            # Very simple regex patterns for demo - in real system use more robust methods
            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            domain_pattern = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
            url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
            hash_pattern = r'\b[a-fA-F0-9]{32,64}\b'
            
            import re
            
            text = st.session_state.current_content
            
            # Find IP addresses
            iocs["IP Addresses"] = re.findall(ip_pattern, text)
            
            # Find domains
            domains = re.findall(domain_pattern, text)
            iocs["Domains"] = [d for d in domains if ".onion" in d or ".xyz" in d]  # Filter for interesting domains
            
            # Find URLs
            iocs["URLs"] = re.findall(url_pattern, text)
            
            # Find hashes
            iocs["Hashes"] = re.findall(hash_pattern, text)
            
            # Display found IOCs
            has_iocs = False
            
            for ioc_type, items in iocs.items():
                if items:
                    has_iocs = True
                    st.markdown(f"#### {ioc_type}")
                    for item in items:
                        st.code(item)
            
            if not has_iocs:
                st.info("No indicators of compromise detected in the content.")
            
            # Actions
            col1, col2 = st.columns(2)
            
            with col1:
                st.button("Export Indicators", key="export_iocs")
            
            with col2:
                st.button("Add to Watchlist", key="add_to_watchlist")