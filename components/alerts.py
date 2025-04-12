import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

def render_alerts():
    st.title("Alert Management")
    
    # Alert Overview
    st.subheader("Alert Overview")
    
    # Alert metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            label="Active Alerts",
            value="27",
            delta="4",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            label="Critical",
            value="8",
            delta="2",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="High",
            value="12",
            delta="3",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="Medium",
            value="5",
            delta="-1",
            delta_color="normal"
        )
    
    with col5:
        st.metric(
            label="Low",
            value="2",
            delta="0",
            delta_color="normal"
        )
    
    # Filters for alerts
    with st.container():
        st.markdown("### Alert Filters")
        
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        
        with filter_col1:
            severity_filter = st.multiselect(
                "Severity",
                ["Critical", "High", "Medium", "Low"],
                default=["Critical", "High", "Medium", "Low"]
            )
        
        with filter_col2:
            status_filter = st.multiselect(
                "Status",
                ["New", "In Progress", "Resolved", "False Positive"],
                default=["New", "In Progress"]
            )
        
        with filter_col3:
            date_range = st.selectbox(
                "Time Range",
                ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Custom Range"],
                index=1
            )
        
        with filter_col4:
            category_filter = st.multiselect(
                "Category",
                ["Data Breach", "Ransomware", "Credentials", "PII", "Brand Abuse", "Source Code", "Other"],
                default=["Data Breach", "Credentials", "PII"]
            )
    
    # Alert list
    st.markdown("### Active Alerts")
    
    # Sample alert data
    alerts = [
        {
            "id": "ALERT-2025-04081",
            "timestamp": "2025-04-08 14:32:21",
            "severity": "Critical",
            "category": "Data Breach",
            "description": "Patient records from Memorial Hospital found on dark web marketplace.",
            "status": "New",
            "source": "AlphaBay Market"
        },
        {
            "id": "ALERT-2025-04082",
            "timestamp": "2025-04-08 10:15:43",
            "severity": "Critical",
            "category": "Ransomware",
            "description": "Company mentioned in ransomware group's leak site as new victim.",
            "status": "New",
            "source": "BlackCat Leak Site"
        },
        {
            "id": "ALERT-2025-04083",
            "timestamp": "2025-04-08 08:42:19",
            "severity": "High",
            "category": "Credentials",
            "description": "123 employee credentials found in new breach compilation.",
            "status": "In Progress",
            "source": "BreachForums"
        },
        {
            "id": "ALERT-2025-04071",
            "timestamp": "2025-04-07 22:03:12",
            "severity": "High",
            "category": "PII",
            "description": "Customer PII being offered for sale on hacking forum.",
            "status": "In Progress",
            "source": "XSS Forum"
        },
        {
            "id": "ALERT-2025-04072",
            "timestamp": "2025-04-07 18:37:56",
            "severity": "Medium",
            "category": "Brand Abuse",
            "description": "Phishing campaign using company brand assets detected.",
            "status": "New",
            "source": "Telegram Channel"
        },
        {
            "id": "ALERT-2025-04073",
            "timestamp": "2025-04-07 14:21:08",
            "severity": "Medium",
            "category": "Source Code",
            "description": "Fragments of internal source code shared in paste site.",
            "status": "In Progress",
            "source": "DeepPaste"
        },
        {
            "id": "ALERT-2025-04063",
            "timestamp": "2025-04-06 20:15:37",
            "severity": "Low",
            "category": "Credentials",
            "description": "Legacy system credentials posted in hacking forum.",
            "status": "New",
            "source": "RaidForums"
        }
    ]
    
    # Create a dataframe for the alerts
    alert_df = pd.DataFrame(alerts)
    
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
    styled_df = alert_df.style.applymap(color_severity, subset=['severity'])
    
    # Display the table
    st.dataframe(styled_df, use_container_width=True, height=300)
    
    # Action buttons for alerts
    action_col1, action_col2, action_col3, action_col4, action_col5 = st.columns(5)
    
    with action_col1:
        st.button("Investigate", key="investigate_alert")
    
    with action_col2:
        st.button("Mark as Resolved", key="resolve_alert")
    
    with action_col3:
        st.button("Assign to Analyst", key="assign_alert")
    
    with action_col4:
        st.button("Mark as False Positive", key="false_positive")
    
    with action_col5:
        st.button("Generate Report", key="generate_report")
    
    # Alert visualization
    st.markdown("### Alert Analytics")
    
    # Tabs for different alert visualizations
    tab1, tab2, tab3 = st.tabs(["Alert Trend", "Category Distribution", "Source Analysis"])
    
    with tab1:
        # Alert trend over time
        st.subheader("Alert Trend (Last 30 Days)")
        
        # Generate dates for the past 30 days
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
        
        # Sample data for alert trends
        critical_alerts = np.random.randint(5, 12, 30)
        high_alerts = np.random.randint(8, 20, 30)
        medium_alerts = np.random.randint(12, 25, 30)
        low_alerts = np.random.randint(15, 30, 30)
        
        trend_data = pd.DataFrame({
            'Date': dates,
            'Critical': critical_alerts,
            'High': high_alerts,
            'Medium': medium_alerts,
            'Low': low_alerts
        })
        
        # Create a stacked area chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=trend_data['Date'], y=trend_data['Critical'],
            mode='lines',
            line=dict(width=0.5, color='#E74C3C'),
            stackgroup='one',
            name='Critical'
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_data['Date'], y=trend_data['High'],
            mode='lines',
            line=dict(width=0.5, color='#F1C40F'),
            stackgroup='one',
            name='High'
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_data['Date'], y=trend_data['Medium'],
            mode='lines',
            line=dict(width=0.5, color='#3498DB'),
            stackgroup='one',
            name='Medium'
        ))
        
        fig.add_trace(go.Scatter(
            x=trend_data['Date'], y=trend_data['Low'],
            mode='lines',
            line=dict(width=0.5, color='#2ECC71'),
            stackgroup='one',
            name='Low'
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(26, 26, 26, 0)',
            plot_bgcolor='rgba(26, 26, 26, 0)',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(
                showgrid=False,
                title=None,
                tickfont=dict(color='#ECF0F1')
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(44, 62, 80, 0.3)',
                title="Alert Count",
                tickfont=dict(color='#ECF0F1')
            ),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Alert distribution by category
        st.subheader("Alert Category Distribution")
        
        # Sample data for categories
        categories = ['Data Breach', 'Credentials', 'PII', 'Ransomware', 'Brand Abuse', 'Source Code', 'Infrastructure', 'Other']
        counts = [35, 28, 18, 12, 8, 6, 4, 2]
        
        category_data = pd.DataFrame({
            'Category': categories,
            'Count': counts
        })
        
        # Create a horizontal bar chart
        fig = px.bar(
            category_data,
            y='Category',
            x='Count',
            orientation='h',
            color='Count',
            color_continuous_scale=['#2ECC71', '#3498DB', '#F1C40F', '#E74C3C'],
            height=400
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(26, 26, 26, 0)',
            plot_bgcolor='rgba(26, 26, 26, 0)',
            coloraxis_showscale=False,
            xaxis=dict(
                title="Number of Alerts",
                showgrid=True,
                gridcolor='rgba(44, 62, 80, 0.3)',
                tickfont=dict(color='#ECF0F1')
            ),
            yaxis=dict(
                title=None,
                showgrid=False,
                tickfont=dict(color='#ECF0F1')
            ),
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Alert sources analysis
        st.subheader("Alert Sources")
        
        # Sample data for sources
        sources = ['Dark Web Markets', 'Hacking Forums', 'Paste Sites', 'Telegram Channels', 'Ransomware Blogs', 'IRC Channels', 'Social Media']
        source_counts = [32, 27, 18, 15, 10, 7, 4]
        
        source_data = pd.DataFrame({
            'Source': sources,
            'Count': source_counts
        })
        
        # Create a pie chart
        fig = px.pie(
            source_data,
            values='Count',
            names='Source',
            hole=0.4,
            color_discrete_sequence=['#E74C3C', '#F1C40F', '#3498DB', '#2ECC71', '#9B59B6', '#E67E22', '#1ABC9C']
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
                x=0.5,
                font=dict(color='#ECF0F1')
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Alert rules configuration
    st.markdown("---")
    st.subheader("Alert Rules Configuration")
    
    # Tabs for different rule categories
    rule_tab1, rule_tab2 = st.tabs(["Active Rules", "Rule Editor"])
    
    with rule_tab1:
        # Sample data for alert rules
        alert_rules = pd.DataFrame({
            "Rule Name": [
                "Critical Data Breach Detection",
                "Ransomware Victim Monitoring",
                "Employee Credential Exposure",
                "Source Code Leak Detection",
                "Brand Impersonation Alert",
                "Executive PII Monitoring",
                "Infrastructure Exposure"
            ],
            "Category": ["Data Breach", "Ransomware", "Credentials", "Source Code", "Brand Abuse", "PII", "Infrastructure"],
            "Severity": ["Critical", "Critical", "High", "High", "Medium", "Critical", "Medium"],
            "Sources": ["All", "Leak Sites", "Paste Sites, Forums", "Paste Sites, Forums", "All", "All", "Forums, Markets"],
            "Status": ["Active", "Active", "Active", "Active", "Active", "Active", "Active"]
        })
        
        # Display rules table
        st.dataframe(alert_rules, use_container_width=True)
        
        # Rule action buttons
        rule_col1, rule_col2, rule_col3, rule_col4 = st.columns(4)
        
        with rule_col1:
            st.button("Create New Rule", key="new_rule")
        
        with rule_col2:
            st.button("Edit Selected", key="edit_rule")
        
        with rule_col3:
            st.button("Duplicate", key="duplicate_rule")
        
        with rule_col4:
            st.button("Disable", key="disable_rule")
    
    with rule_tab2:
        # Rule editor form
        with st.form("rule_editor"):
            st.markdown("### Rule Editor")
            
            rule_name = st.text_input("Rule Name", value="New Alert Rule")
            
            editor_col1, editor_col2 = st.columns(2)
            
            with editor_col1:
                rule_category = st.selectbox(
                    "Category",
                    ["Data Breach", "Ransomware", "Credentials", "PII", "Brand Abuse", "Source Code", "Infrastructure", "Other"]
                )
                
                rule_severity = st.selectbox(
                    "Severity",
                    ["Critical", "High", "Medium", "Low"]
                )
            
            with editor_col2:
                rule_sources = st.multiselect(
                    "Monitoring Sources",
                    ["Dark Web Markets", "Hacking Forums", "Paste Sites", "Leak Sites", "Telegram Channels", "IRC Channels", "Social Media", "All"],
                    default=["All"]
                )
                
                rule_status = st.selectbox(
                    "Status",
                    ["Active", "Disabled"]
                )
            
            st.markdown("### Rule Conditions")
            
            condition_type = st.selectbox(
                "Condition Type",
                ["Keyword Match", "Regular Expression", "Data Pattern", "Complex Query"]
            )
            
            if condition_type == "Keyword Match":
                keywords = st.text_area("Keywords (one per line)", height=100)
                
                keyword_options = st.columns(3)
                with keyword_options[0]:
                    case_sensitive = st.checkbox("Case Sensitive", value=False)
                with keyword_options[1]:
                    whole_word = st.checkbox("Whole Word Only", value=False)
                with keyword_options[2]:
                    proximity = st.checkbox("Proximity Search", value=False)
            
            elif condition_type == "Regular Expression":
                regex_pattern = st.text_area("Regular Expression Pattern", height=100)
                
                regex_options = st.columns(2)
                with regex_options[0]:
                    test_regex = st.button("Test RegEx")
                with regex_options[1]:
                    validate_regex = st.button("Validate Pattern")
            
            elif condition_type == "Data Pattern":
                data_patterns = st.multiselect(
                    "Data Patterns to Detect",
                    ["Email Addresses", "Credit Card Numbers", "Social Security Numbers", "Phone Numbers", "IP Addresses", "API Keys", "Passwords"]
                )
            
            elif condition_type == "Complex Query":
                complex_query = st.text_area("Complex Query", height=100, 
                                            placeholder="Example: (keyword1 OR keyword2) AND (keyword3) NOT (keyword4)")
            
            st.markdown("### Response Actions")
            
            notification_channels = st.multiselect(
                "Notification Channels",
                ["Email", "Slack", "API Webhook", "SMS"],
                default=["Email", "Slack"]
            )
            
            auto_actions = st.multiselect(
                "Automated Actions",
                ["Create Incident Ticket", "Add to Watchlist", "Block in Firewall", "None"],
                default=["Create Incident Ticket"]
            )
            
            submit_rule = st.form_submit_button("Save Rule")
            
            if submit_rule:
                st.success("Alert rule saved successfully!")
    
    # Alert notification settings
    st.markdown("---")
    st.subheader("Alert Notification Settings")
    
    # Notification channels
    notif_col1, notif_col2 = st.columns(2)
    
    with notif_col1:
        st.markdown("### Notification Channels")
        
        with st.container():
            st.checkbox("Email Notifications", value=True)
            st.text_input("Email Recipients", value="security@company.com, analyst@company.com")
            
            st.checkbox("Slack Notifications", value=True)
            st.text_input("Slack Channel", value="#security-alerts")
            
            st.checkbox("SMS Notifications", value=False)
            st.text_input("Phone Numbers", placeholder="+1234567890, +0987654321")
            
            st.checkbox("API Webhook", value=False)
            st.text_input("Webhook URL", placeholder="https://api.example.com/webhook")
    
    with notif_col2:
        st.markdown("### Notification Schedule")
        
        with st.container():
            notify_critical = st.radio(
                "Critical Alerts",
                ["Immediate", "Hourly Digest", "Daily Digest"],
                index=0
            )
            
            notify_high = st.radio(
                "High Alerts",
                ["Immediate", "Hourly Digest", "Daily Digest"],
                index=1
            )
            
            notify_medium = st.radio(
                "Medium Alerts",
                ["Immediate", "Hourly Digest", "Daily Digest"],
                index=2
            )
            
            notify_low = st.radio(
                "Low Alerts",
                ["Immediate", "Hourly Digest", "Daily Digest"],
                index=2
            )
    
    # Save alert settings button
    st.button("Save Notification Settings", type="primary", key="save_notif")
