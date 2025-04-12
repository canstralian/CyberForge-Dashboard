import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
import altair as alt

def render_threats():
    st.title("Threat Detection & Analysis")
    
    # Filters section
    with st.container():
        st.subheader("Threat Filters")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            severity_filter = st.multiselect(
                "Severity Level",
                ["Critical", "High", "Medium", "Low"],
                default=["Critical", "High"]
            )
        
        with col2:
            threat_type = st.multiselect(
                "Threat Type",
                ["Data Breach", "Ransomware", "Phishing", "Malware", "Identity Theft", "Zero-day Exploit"],
                default=["Data Breach", "Ransomware"]
            )
        
        with col3:
            date_range = st.selectbox(
                "Time Range",
                ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last Quarter", "Custom Range"],
                index=1
            )
        
        with col4:
            st.text_input("Search Keywords", placeholder="e.g. healthcare, banking")
            
        st.button("Apply Filters", type="primary")
    
    # Threat overview metrics
    st.markdown("### Threat Overview")
    
    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
    
    with metric_col1:
        st.metric(
            label="Critical Threats",
            value="8",
            delta="2",
            delta_color="inverse"
        )
    
    with metric_col2:
        st.metric(
            label="High Threats",
            value="19",
            delta="4",
            delta_color="inverse"
        )
    
    with metric_col3:
        st.metric(
            label="Medium Threats",
            value="35",
            delta="0",
            delta_color="normal"
        )
    
    with metric_col4:
        st.metric(
            label="Low Threats",
            value="52",
            delta="-5",
            delta_color="normal"
        )
    
    with metric_col5:
        st.metric(
            label="Avg. Response Time",
            value="47m",
            delta="-13m",
            delta_color="normal"
        )
    
    # Threat detection visualization
    tab1, tab2, tab3 = st.tabs(["Threat Timeline", "Category Analysis", "Threat Details"])
    
    with tab1:
        st.subheader("Threat Detection Timeline")
        
        # Generate dates and times for the past 14 days with hourly granularity
        now = datetime.now()
        timeline_data = []
        
        for day in range(14, 0, -1):
            base_date = now - timedelta(days=day)
            for hour in range(0, 24, 2):  # Every 2 hours
                timestamp = base_date + timedelta(hours=hour)
                
                # Random threat count for each severity level
                if np.random.random() > 0.7:  # 30% chance of critical
                    severity = "Critical"
                    count = np.random.randint(1, 4)
                elif np.random.random() > 0.5:  # 20% chance of high
                    severity = "High"
                    count = np.random.randint(1, 6)
                elif np.random.random() > 0.3:  # 20% chance of medium
                    severity = "Medium"
                    count = np.random.randint(1, 8)
                else:  # 30% chance of low
                    severity = "Low"
                    count = np.random.randint(1, 10)
                
                timeline_data.append({
                    "timestamp": timestamp,
                    "severity": severity,
                    "count": count
                })
        
        timeline_df = pd.DataFrame(timeline_data)
        
        # Convert to a format suitable for visualization
        # Group by date and severity to get counts
        timeline_df['date'] = timeline_df['timestamp'].dt.strftime('%Y-%m-%d')
        
        # Create a scatter plot for the timeline with varying dot sizes based on count
        fig = px.scatter(
            timeline_df,
            x='timestamp',
            y='severity',
            size='count',
            color='severity',
            color_discrete_map={
                'Critical': '#E74C3C',
                'High': '#F1C40F',
                'Medium': '#3498DB',
                'Low': '#2ECC71'
            },
            hover_data=['count'],
            height=400
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(26, 26, 26, 0)',
            plot_bgcolor='rgba(26, 26, 26, 0)',
            xaxis=dict(
                showgrid=False,
                title=None,
                tickfont=dict(color='#ECF0F1')
            ),
            yaxis=dict(
                showgrid=False,
                title=None,
                tickfont=dict(color='#ECF0F1'),
                categoryorder='array',
                categoryarray=['Low', 'Medium', 'High', 'Critical']
            ),
            margin=dict(l=10, r=10, t=10, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Threat Categories")
            
            # Threat category distribution
            categories = ['Data Breach', 'Ransomware', 'Phishing', 'Malware', 'Identity Theft', 'Zero-day Exploit']
            values = [38, 24, 18, 14, 6, 8]
            
            category_data = pd.DataFrame({
                'Category': categories,
                'Count': values
            })
            
            fig = px.bar(
                category_data,
                x='Category',
                y='Count',
                color='Count',
                color_continuous_scale=['#2ECC71', '#3498DB', '#F1C40F', '#E74C3C'],
                height=350
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(26, 26, 26, 0)',
                plot_bgcolor='rgba(26, 26, 26, 0)',
                coloraxis_showscale=False,
                xaxis=dict(
                    title=None,
                    tickfont=dict(color='#ECF0F1')
                ),
                yaxis=dict(
                    title=None,
                    showgrid=True,
                    gridcolor='rgba(44, 62, 80, 0.3)',
                    tickfont=dict(color='#ECF0F1')
                ),
                margin=dict(l=10, r=10, t=10, b=10)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Threat Severity Distribution")
            
            # Severity distribution
            severity_labels = ['Critical', 'High', 'Medium', 'Low']
            severity_values = [8, 19, 35, 52]
            
            fig = px.pie(
                names=severity_labels,
                values=severity_values,
                color=severity_labels,
                color_discrete_map={
                    'Critical': '#E74C3C',
                    'High': '#F1C40F',
                    'Medium': '#3498DB',
                    'Low': '#2ECC71'
                },
                hole=0.4,
                height=350
            )
            
            fig.update_layout(
                paper_bgcolor='rgba(26, 26, 26, 0)',
                plot_bgcolor='rgba(26, 26, 26, 0)',
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5
                ),
                margin=dict(l=10, r=10, t=10, b=10),
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Active Threat Details")
        
        # Create data for the threat details table
        threat_details = [
            {
                "id": "T-2025-0428",
                "detected": "2025-04-08 14:32:21",
                "type": "Data Breach",
                "target": "Healthcare",
                "severity": "Critical",
                "status": "Active",
                "details": "Patient data exposed on dark web marketplace."
            },
            {
                "id": "T-2025-0427",
                "detected": "2025-04-08 09:17:45",
                "type": "Ransomware",
                "target": "Finance",
                "severity": "Critical",
                "status": "Active",
                "details": "New ransomware variant targeting financial institutions."
            },
            {
                "id": "T-2025-0426",
                "detected": "2025-04-07 22:03:12",
                "type": "Zero-day Exploit",
                "target": "Technology",
                "severity": "High",
                "status": "Active",
                "details": "Critical vulnerability in enterprise software being exploited."
            },
            {
                "id": "T-2025-0425",
                "detected": "2025-04-07 15:45:39",
                "type": "Phishing",
                "target": "Government",
                "severity": "High",
                "status": "Active",
                "details": "Sophisticated phishing campaign targeting government employees."
            },
            {
                "id": "T-2025-0424",
                "detected": "2025-04-07 11:27:03",
                "type": "Malware",
                "target": "Multiple",
                "severity": "Medium",
                "status": "Active",
                "details": "New strain of data-stealing malware distributed via email attachments."
            }
        ]
        
        # Create a dataframe for the table
        threat_df = pd.DataFrame(threat_details)
        
        # Apply colors to severity column
        def color_severity(val):
            color_map = {
                'Critical': '#E74C3C',
                'High': '#F1C40F',
                'Medium': '#3498DB',
                'Low': '#2ECC71'
            }
            return f'background-color: {color_map.get(val, "#ECF0F1")}'
        
        # Style the dataframe
        styled_df = threat_df.style.applymap(color_severity, subset=['severity'])
        
        # Display the table
        st.dataframe(styled_df, use_container_width=True, height=300)
        
        # Add action buttons below the table
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.button("Investigate Selected", key="investigate_btn")
        
        with col2:
            st.button("Mark as Resolved", key="resolve_btn")
        
        with col3:
            st.button("Export Report", key="export_btn")
        
        with col4:
            st.button("Assign to Analyst", key="assign_btn")
    
    # Threat intelligence section
    st.markdown("### Threat Intelligence Analysis")
    
    # Tabs for different intelligence views
    intel_tab1, intel_tab2, intel_tab3 = st.tabs(["Actor Analysis", "Attack Vectors", "Indicators of Compromise"])
    
    with intel_tab1:
        st.subheader("Threat Actor Analysis")
        
        # Actor table
        actor_data = [
            {
                "actor": "BlackCat Group",
                "type": "Ransomware",
                "activity": "High",
                "targets": "Healthcare, Finance",
                "ttps": "Double extortion, DDoS threats",
                "attribution": "Likely Eastern Europe"
            },
            {
                "actor": "CryptoLock",
                "type": "Ransomware",
                "activity": "Medium",
                "targets": "Manufacturing, Energy",
                "ttps": "Supply chain attacks",
                "attribution": "Unknown"
            },
            {
                "actor": "DarkLeaks",
                "type": "Data Broker",
                "activity": "High",
                "targets": "All sectors",
                "ttps": "Data aggregation, auction site",
                "attribution": "Multiple affiliates"
            }
        ]
        
        actor_df = pd.DataFrame(actor_data)
        st.dataframe(actor_df, use_container_width=True)
        
        # Relationship graph placeholder
        st.subheader("Threat Actor Relationships")
        st.image("https://images.unsplash.com/photo-1510987836583-e3fb9586c7b3", 
                 caption="Network analysis of threat actor relationships and infrastructure", 
                 use_column_width=True)
        
    with intel_tab2:
        st.subheader("Common Attack Vectors")
        
        # Attack vector distribution
        vectors = ['Phishing Email', 'Compromised Credentials', 'Malware Infection', 
                   'Supply Chain', 'Unpatched Vulnerability', 'Social Engineering']
        percentages = [35, 28, 15, 10, 8, 4]
        
        vector_data = pd.DataFrame({
            'Vector': vectors,
            'Percentage': percentages
        })
        
        # Horizontal bar chart for attack vectors
        fig = px.bar(
            vector_data,
            x='Percentage',
            y='Vector',
            orientation='h',
            color='Percentage',
            color_continuous_scale=['#2ECC71', '#3498DB', '#F1C40F', '#E74C3C'],
            height=300
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(26, 26, 26, 0)',
            plot_bgcolor='rgba(26, 26, 26, 0)',
            coloraxis_showscale=False,
            xaxis=dict(
                title='Percentage of Attacks',
                showgrid=True,
                gridcolor='rgba(44, 62, 80, 0.3)',
                tickfont=dict(color='#ECF0F1')
            ),
            yaxis=dict(
                title=None,
                showgrid=False,
                tickfont=dict(color='#ECF0F1')
            ),
            margin=dict(l=10, r=10, t=10, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Technical details section
        st.subheader("Technical Analysis")
        
        vector_tabs = st.tabs(["Phishing", "Malware", "Vulnerabilities"])
        
        with vector_tabs[0]:
            st.markdown("#### Phishing Campaign Analysis")
            st.markdown("""
            Recent phishing campaigns observed in dark web forums targeting:
            - Financial institutions (spoofed login pages)
            - Healthcare providers (fake patient portals)
            - Government employees (document sharing lures)
            
            **Tactics include:**
            - Lookalike domains with valid SSL certificates
            - Evasion of email security through legitimate hosting services
            - Use of shortened URLs to disguise destinations
            """)
            
        with vector_tabs[1]:
            st.markdown("#### Malware Analysis")
            st.markdown("""
            Prevalent malware families being distributed:
            - TrickBot (banking trojan with evolving capabilities)
            - Emotet (modular malware with spam capabilities)
            - Conti (ransomware with data exfiltration)
            
            **Distribution channels:**
            - Malicious email attachments (Excel files with macros)
            - Compromised software updates
            - Drive-by downloads from compromised websites
            """)
            
        with vector_tabs[2]:
            st.markdown("#### Vulnerability Exploitation")
            st.markdown("""
            Critical vulnerabilities being actively exploited:
            - CVE-2024-1234: Remote code execution in web servers
            - CVE-2024-5678: Authentication bypass in VPN appliances
            - CVE-2024-9101: Privilege escalation in enterprise software
            
            **Exploitation timeline:**
            - Average time from disclosure to exploitation: 72 hours
            - Peak exploitation activity occurs within 2 weeks
            - Persistence mechanisms often installed for long-term access
            """)
    
    with intel_tab3:
        st.subheader("Indicators of Compromise (IoCs)")
        
        # IoC tabs
        ioc_tabs = st.tabs(["IP Addresses", "Domains", "File Hashes", "URLs"])
        
        with ioc_tabs[0]:
            ip_data = pd.DataFrame({
                'IP Address': ['198.51.100.123', '203.0.113.45', '198.51.100.67', '203.0.113.89', '198.51.100.213'],
                'ASN': ['AS12345', 'AS67890', 'AS12345', 'AS23456', 'AS34567'],
                'Country': ['Russia', 'China', 'Russia', 'Ukraine', 'Brazil'],
                'First Seen': ['2025-04-01', '2025-04-03', '2025-04-04', '2025-04-05', '2025-04-07'],
                'Last Seen': ['2025-04-08', '2025-04-08', '2025-04-08', '2025-04-07', '2025-04-08'],
                'Associated Malware': ['TrickBot', 'Emotet', 'TrickBot', 'BlackCat', 'Conti']
            })
            
            st.dataframe(ip_data, use_container_width=True)
            
        with ioc_tabs[1]:
            domain_data = pd.DataFrame({
                'Domain': ['secure-banklogin.com', 'microsoft-update.xyz', 'docusign-view.net', 'healthcare-portal.org', 'service-login.co'],
                'IP Address': ['198.51.100.123', '203.0.113.45', '198.51.100.67', '203.0.113.89', '198.51.100.213'],
                'Registrar': ['NameCheap', 'GoDaddy', 'Namecheap', 'Hostinger', 'GoDaddy'],
                'Created Date': ['2025-03-30', '2025-04-01', '2025-04-02', '2025-04-03', '2025-04-05'],
                'Classification': ['Phishing', 'Malware C2', 'Phishing', 'Phishing', 'Phishing']
            })
            
            st.dataframe(domain_data, use_container_width=True)
            
        with ioc_tabs[2]:
            hash_data = pd.DataFrame({
                'File Hash (SHA-256)': [
                    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
                    'a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a',
                    '3f39d5c348e5b79d06e842c114e6cc571583bbf44e4b0ebfda1a01ec05745d43',
                    'ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb',
                    '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae'
                ],
                'File Name': ['invoice.doc', 'setup.exe', 'update.exe', 'report.xlsx', 'attachment.pdf'],
                'File Type': ['DOC', 'EXE', 'EXE', 'XLSX', 'PDF'],
                'Detection Ratio': ['37/58', '42/58', '29/58', '35/58', '23/58'],
                'Malware Family': ['Emotet', 'TrickBot', 'Conti', 'Emotet', 'AgentTesla']
            })
            
            st.dataframe(hash_data, use_container_width=True)
            
        with ioc_tabs[3]:
            url_data = pd.DataFrame({
                'URL': [
                    'https://secure-banklogin.com/auth/login.php',
                    'https://microsoft-update.xyz/download/patch.exe',
                    'https://docusign-view.net/document/invoice.doc',
                    'https://healthcare-portal.org/patient/login',
                    'https://service-login.co/auth/reset'
                ],
                'Status': ['Active', 'Active', 'Inactive', 'Active', 'Active'],
                'Classification': ['Phishing', 'Malware Distribution', 'Phishing', 'Phishing', 'Phishing'],
                'Target': ['Banking Customers', 'General', 'Business', 'Healthcare', 'General'],
                'First Reported': ['2025-04-02', '2025-04-03', '2025-04-04', '2025-04-06', '2025-04-07']
            })
            
            st.dataframe(url_data, use_container_width=True)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.button("Export IoCs", key="export_ioc_btn")
        
        with col2:
            st.button("Add to Blocklist", key="blocklist_btn")
        
        with col3:
            st.button("Share Intelligence", key="share_intel_btn")
