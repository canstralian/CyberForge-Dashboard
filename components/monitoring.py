import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

def render_monitoring():
    st.title("Monitoring Configuration")
    
    # Dashboard layout for monitoring configuration
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("Monitoring Settings")
        
        with st.form("monitoring_settings"):
            st.markdown("### General Settings")
            
            scan_frequency = st.select_slider(
                "Scan Frequency",
                options=["1 hour", "2 hours", "4 hours", "6 hours", "12 hours", "24 hours"],
                value="4 hours"
            )
            
            intelligence_sources = st.multiselect(
                "Intelligence Sources",
                ["Dark Web Forums", "Paste Sites", "Marketplaces", "Telegram Channels", "IRC Channels", "Ransomware Blogs", "Breach Databases", "Hacker Forums", "Social Media"],
                default=["Dark Web Forums", "Paste Sites", "Marketplaces", "Ransomware Blogs"]
            )
            
            st.markdown("### Alert Thresholds")
            
            col1a, col1b = st.columns(2)
            
            with col1a:
                critical_threshold = st.number_input("Critical Alert Threshold", min_value=1, max_value=100, value=80)
            
            with col1b:
                high_threshold = st.number_input("High Alert Threshold", min_value=1, max_value=100, value=60)
            
            col1c, col1d = st.columns(2)
            
            with col1c:
                medium_threshold = st.number_input("Medium Alert Threshold", min_value=1, max_value=100, value=40)
            
            with col1d:
                low_threshold = st.number_input("Low Alert Threshold", min_value=1, max_value=100, value=20)
            
            st.markdown("### Notification Channels")
            
            email_notify = st.checkbox("Email Notifications", value=True)
            if email_notify:
                email_recipients = st.text_input("Email Recipients", value="security@company.com, analyst@company.com")
            
            slack_notify = st.checkbox("Slack Notifications", value=True)
            if slack_notify:
                slack_channel = st.text_input("Slack Channel", value="#security-alerts")
            
            api_notify = st.checkbox("API Webhook", value=False)
            if api_notify:
                webhook_url = st.text_input("Webhook URL", placeholder="https://api.example.com/webhook")
            
            sms_notify = st.checkbox("SMS Notifications", value=False)
            if sms_notify:
                phone_numbers = st.text_input("Phone Numbers", placeholder="+1234567890, +0987654321")
            
            submit = st.form_submit_button("Save Configuration", type="primary")
            
            if submit:
                st.success("Monitoring configuration saved successfully!")
    
    with col2:
        st.subheader("Monitored Keywords & Entities")
        
        # Tabs for different monitoring categories
        tab1, tab2, tab3, tab4 = st.tabs(["Company Assets", "Credentials", "PII", "Custom Keywords"])
        
        with tab1:
            st.markdown("### Company Assets Monitoring")
            
            # Sample company assets to monitor
            company_assets = pd.DataFrame({
                "Asset Type": ["Domain", "Domain", "IP Range", "Brand", "Brand", "Product", "Technology"],
                "Value": ["company.com", "company-services.net", "198.51.100.0/24", "CompanyName", "ProductX", "ServiceY", "TechnologyZ"],
                "Priority": ["High", "Medium", "High", "Critical", "High", "Medium", "Low"],
                "Status": ["Active", "Active", "Active", "Active", "Active", "Active", "Active"]
            })
            
            # Editable dataframe
            edited_assets = st.data_editor(
                company_assets,
                num_rows="dynamic",
                column_config={
                    "Asset Type": st.column_config.SelectboxColumn(
                        "Asset Type",
                        options=["Domain", "IP Range", "Brand", "Product", "Technology", "Other"],
                    ),
                    "Priority": st.column_config.SelectboxColumn(
                        "Priority",
                        options=["Critical", "High", "Medium", "Low"],
                    ),
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Active", "Paused"],
                    ),
                },
                use_container_width=True
            )
        
        with tab2:
            st.markdown("### Credentials Monitoring")
            
            # Sample credential monitoring settings
            credential_monitoring = pd.DataFrame({
                "Email Domain": ["@company.com", "@company-services.net", "@product-x.com"],
                "Include Subdomains": [True, True, False],
                "Monitor Password Breach": [True, True, True],
                "Alert Level": ["Critical", "High", "High"],
                "Status": ["Active", "Active", "Active"]
            })
            
            edited_credentials = st.data_editor(
                credential_monitoring,
                num_rows="dynamic",
                column_config={
                    "Include Subdomains": st.column_config.CheckboxColumn(
                        "Include Subdomains",
                        help="Monitor all subdomains",
                    ),
                    "Monitor Password Breach": st.column_config.CheckboxColumn(
                        "Monitor Password Breach",
                    ),
                    "Alert Level": st.column_config.SelectboxColumn(
                        "Alert Level",
                        options=["Critical", "High", "Medium", "Low"],
                    ),
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Active", "Paused"],
                    ),
                },
                use_container_width=True
            )
        
        with tab3:
            st.markdown("### PII Monitoring")
            
            # Sample PII monitoring settings
            pii_monitoring = pd.DataFrame({
                "PII Type": ["SSN", "Credit Card", "Bank Account", "Passport Number", "Driver License"],
                "Monitor": [True, True, True, False, False],
                "Alert Level": ["Critical", "Critical", "High", "High", "Medium"],
                "Status": ["Active", "Active", "Active", "Paused", "Paused"]
            })
            
            edited_pii = st.data_editor(
                pii_monitoring,
                num_rows="dynamic",
                column_config={
                    "PII Type": st.column_config.SelectboxColumn(
                        "PII Type",
                        options=["SSN", "Credit Card", "Bank Account", "Passport Number", "Driver License", "Health Information", "Other"],
                    ),
                    "Monitor": st.column_config.CheckboxColumn(
                        "Monitor",
                    ),
                    "Alert Level": st.column_config.SelectboxColumn(
                        "Alert Level",
                        options=["Critical", "High", "Medium", "Low"],
                    ),
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Active", "Paused"],
                    ),
                },
                use_container_width=True
            )
        
        with tab4:
            st.markdown("### Custom Keywords")
            
            # Sample custom keywords
            custom_keywords = pd.DataFrame({
                "Keyword": ["confidential memo", "project phoenix", "merger", "acquisition", "layoff", "security breach"],
                "Category": ["Internal Document", "Project", "Financial", "Financial", "HR", "Security"],
                "Alert Level": ["Critical", "High", "Critical", "Critical", "High", "Critical"],
                "Status": ["Active", "Active", "Active", "Active", "Active", "Active"]
            })
            
            edited_keywords = st.data_editor(
                custom_keywords,
                num_rows="dynamic",
                column_config={
                    "Category": st.column_config.SelectboxColumn(
                        "Category",
                        options=["Internal Document", "Project", "Financial", "HR", "Security", "Product", "Other"],
                    ),
                    "Alert Level": st.column_config.SelectboxColumn(
                        "Alert Level",
                        options=["Critical", "High", "Medium", "Low"],
                    ),
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Active", "Paused"],
                    ),
                },
                use_container_width=True
            )
    
    # Monitoring sources and coverage
    st.markdown("---")
    st.subheader("Monitoring Sources & Coverage")
    
    # Create tabs for different monitoring source categories
    source_tab1, source_tab2, source_tab3 = st.tabs(["Dark Web Coverage", "Source Categories", "Geographic Coverage"])
    
    with source_tab1:
        # Dark web monitoring sources
        st.markdown("### Dark Web Monitoring Sources")
        
        # Sample data for dark web sources
        dark_web_sources = pd.DataFrame({
            "Source Type": ["Market", "Forum", "Forum", "Market", "Paste Site", "Leak Site", "Chat", "Market"],
            "Name": ["AlphaBay", "XSS Forum", "Exploit.in", "ASAP Market", "DeepPaste", "DarkLeak", "Telegram", "White House"],
            "Focus": ["General", "Hacking", "Credentials", "Drugs/Fraud", "Text sharing", "Data leaks", "Communication", "General"],
            "Coverage": [95, 90, 85, 80, 75, 70, 65, 60],
            "Status": ["Active", "Active", "Active", "Active", "Active", "Active", "Active", "Active"]
        })
        
        fig = px.bar(
            dark_web_sources,
            x="Name",
            y="Coverage",
            color="Coverage",
            color_continuous_scale=["#2ECC71", "#F1C40F", "#E74C3C"],
            text="Coverage",
            height=400
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(26, 26, 26, 0)',
            plot_bgcolor='rgba(26, 26, 26, 0)',
            xaxis=dict(
                title=None,
                tickfont=dict(color='#ECF0F1')
            ),
            yaxis=dict(
                title="Coverage Percentage",
                showgrid=True,
                gridcolor='rgba(44, 62, 80, 0.3)',
                tickfont=dict(color='#ECF0F1')
            ),
            coloraxis_showscale=False
        )
        
        fig.update_traces(texttemplate='%{text}%', textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Source details table
        st.dataframe(dark_web_sources, use_container_width=True)
    
    with source_tab2:
        # Source category distribution
        st.markdown("### Monitoring by Source Category")
        
        # Sample data for source categories
        source_categories = {
            "Category": ["Dark Web Markets", "Hacking Forums", "Paste Sites", "Telegram Channels", "IRC Channels", "Leak Sites", "Ransomware Blogs", "Social Media"],
            "Sources Count": [12, 15, 5, 18, 8, 7, 6, 10],
            "Coverage Score": [90, 85, 75, 70, 60, 95, 80, 65]
        }
        
        source_df = pd.DataFrame(source_categories)
        
        fig = px.scatter(
            source_df,
            x="Sources Count",
            y="Coverage Score",
            color="Coverage Score",
            color_continuous_scale=["#E74C3C", "#F1C40F", "#2ECC71"],
            size="Sources Count",
            hover_name="Category",
            height=400
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(26, 26, 26, 0)',
            plot_bgcolor='rgba(26, 26, 26, 0)',
            xaxis=dict(
                title="Number of Sources",
                showgrid=True,
                gridcolor='rgba(44, 62, 80, 0.3)',
                tickfont=dict(color='#ECF0F1')
            ),
            yaxis=dict(
                title="Coverage Score (%)",
                showgrid=True,
                gridcolor='rgba(44, 62, 80, 0.3)',
                tickfont=dict(color='#ECF0F1')
            ),
            coloraxis_showscale=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Category details
        st.dataframe(source_df, use_container_width=True)
    
    with source_tab3:
        # Geographic coverage
        st.markdown("### Geographic Monitoring Coverage")
        
        # World map showing coverage
        st.image("https://images.unsplash.com/photo-1451187580459-43490279c0fa", 
                 caption="Global monitoring coverage across dark web sources", 
                 use_column_width=True)
        
        # Regional coverage metrics
        col_geo1, col_geo2, col_geo3, col_geo4 = st.columns(4)
        
        with col_geo1:
            st.metric(
                label="North America",
                value="92%",
                delta="3%",
                delta_color="normal"
            )
        
        with col_geo2:
            st.metric(
                label="Europe",
                value="88%",
                delta="5%",
                delta_color="normal"
            )
        
        with col_geo3:
            st.metric(
                label="Asia Pacific",
                value="76%",
                delta="8%",
                delta_color="normal"
            )
        
        with col_geo4:
            st.metric(
                label="Rest of World",
                value="65%",
                delta="12%",
                delta_color="normal"
            )
    
    # Monitoring performance metrics
    st.markdown("---")
    st.subheader("Monitoring Performance")
    
    # Performance metrics
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    
    with perf_col1:
        st.metric(
            label="Scan Completion Rate",
            value="98.7%",
            delta="0.5%",
            delta_color="normal"
        )
    
    with perf_col2:
        st.metric(
            label="Avg. Scan Duration",
            value="43 min",
            delta="-7 min",
            delta_color="normal"
        )
    
    with perf_col3:
        st.metric(
            label="Monitored Keywords",
            value="1,247",
            delta="23",
            delta_color="normal"
        )
    
    with perf_col4:
        st.metric(
            label="Coverage Index",
            value="87/100",
            delta="5",
            delta_color="normal"
        )
    
    # Performance charts
    st.markdown("### Performance Trends")
    
    perf_tab1, perf_tab2 = st.tabs(["Scan Performance", "Detection Accuracy"])
    
    with perf_tab1:
        # Generate dates for the past 30 days
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
        
        # Sample data for scan performance
        scan_times = np.random.normal(45, 5, 30).astype(int)  # Mean 45 minutes, std 5 minutes
        success_rates = np.random.normal(98, 1, 30)  # Mean 98%, std 1%
        success_rates = [min(100, max(90, rate)) for rate in success_rates]  # Clamp between 90-100%
        
        scan_data = pd.DataFrame({
            'Date': dates,
            'Scan Time (min)': scan_times,
            'Success Rate (%)': success_rates
        })
        
        # Create a figure with two y-axes
        fig = go.Figure()
        
        # Add scan time line
        fig.add_trace(go.Scatter(
            x=scan_data['Date'],
            y=scan_data['Scan Time (min)'],
            name='Scan Time (min)',
            line=dict(color='#3498DB', width=2)
        ))
        
        # Add success rate line on secondary y-axis
        fig.add_trace(go.Scatter(
            x=scan_data['Date'],
            y=scan_data['Success Rate (%)'],
            name='Success Rate (%)',
            line=dict(color='#2ECC71', width=2),
            yaxis='y2'
        ))
        
        # Configure the layout with two y-axes
        fig.update_layout(
            paper_bgcolor='rgba(26, 26, 26, 0)',
            plot_bgcolor='rgba(26, 26, 26, 0)',
            xaxis=dict(
                title="Date",
                showgrid=False,
                tickfont=dict(color='#ECF0F1')
            ),
            yaxis=dict(
                title="Scan Time (min)",
                showgrid=True,
                gridcolor='rgba(44, 62, 80, 0.3)',
                tickfont=dict(color='#ECF0F1'),
                range=[0, 60]
            ),
            yaxis2=dict(
                title="Success Rate (%)",
                showgrid=False,
                tickfont=dict(color='#ECF0F1'),
                overlaying='y',
                side='right',
                range=[90, 100]
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color='#ECF0F1')
            ),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with perf_tab2:
        # Sample data for detection accuracy
        accuracy_data = pd.DataFrame({
            'Date': dates,
            'True Positives': np.random.randint(80, 100, 30),
            'False Positives': np.random.randint(5, 15, 30),
            'Precision': np.random.normal(92, 2, 30),
            'Recall': np.random.normal(90, 3, 30)
        })
        
        # Ensure precision and recall are within reasonable bounds
        accuracy_data['Precision'] = accuracy_data['Precision'].apply(lambda x: min(100, max(80, x)))
        accuracy_data['Recall'] = accuracy_data['Recall'].apply(lambda x: min(100, max(80, x)))
        
        # Create a figure with stacked bars and lines
        fig = go.Figure()
        
        # Add stacked bars for true and false positives
        fig.add_trace(go.Bar(
            x=accuracy_data['Date'],
            y=accuracy_data['True Positives'],
            name='True Positives',
            marker_color='#2ECC71'
        ))
        
        fig.add_trace(go.Bar(
            x=accuracy_data['Date'],
            y=accuracy_data['False Positives'],
            name='False Positives',
            marker_color='#E74C3C'
        ))
        
        # Add lines for precision and recall
        fig.add_trace(go.Scatter(
            x=accuracy_data['Date'],
            y=accuracy_data['Precision'],
            name='Precision (%)',
            line=dict(color='#3498DB', width=2),
            yaxis='y2'
        ))
        
        fig.add_trace(go.Scatter(
            x=accuracy_data['Date'],
            y=accuracy_data['Recall'],
            name='Recall (%)',
            line=dict(color='#F1C40F', width=2),
            yaxis='y2'
        ))
        
        # Configure the layout
        fig.update_layout(
            paper_bgcolor='rgba(26, 26, 26, 0)',
            plot_bgcolor='rgba(26, 26, 26, 0)',
            barmode='stack',
            xaxis=dict(
                title="Date",
                showgrid=False,
                tickfont=dict(color='#ECF0F1')
            ),
            yaxis=dict(
                title="Alert Count",
                showgrid=True,
                gridcolor='rgba(44, 62, 80, 0.3)',
                tickfont=dict(color='#ECF0F1')
            ),
            yaxis2=dict(
                title="Percentage (%)",
                showgrid=False,
                tickfont=dict(color='#ECF0F1'),
                overlaying='y',
                side='right',
                range=[80, 100]
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color='#ECF0F1')
            ),
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
