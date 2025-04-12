import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta

def render_reports():
    st.title("Intelligence Reports")
    
    # Report filters
    with st.container():
        st.subheader("Report Filters")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            report_type = st.multiselect(
                "Report Type",
                ["Threat Intelligence", "Data Breach", "Executive", "Technical", "Custom"],
                default=["Threat Intelligence", "Data Breach"]
            )
        
        with col2:
            time_period = st.selectbox(
                "Time Period",
                ["Last 7 Days", "Last 30 Days", "Last Quarter", "Year to Date", "Custom Range"],
                index=1
            )
        
        with col3:
            severity = st.multiselect(
                "Severity",
                ["Critical", "High", "Medium", "Low"],
                default=["Critical", "High"]
            )
        
        with col4:
            keywords = st.text_input("Keywords", placeholder="e.g. healthcare, ransomware")
    
    # Recent reports
    st.markdown("### Recent Reports")
    
    # Sample report data
    reports = [
        {
            "id": "RPT-2025-04083",
            "title": "Healthcare Data Breach Intelligence Report",
            "date": "2025-04-08",
            "type": "Data Breach",
            "severity": "Critical",
            "status": "Final"
        },
        {
            "id": "RPT-2025-04082",
            "title": "Weekly Threat Intelligence Summary",
            "date": "2025-04-08",
            "type": "Threat Intelligence",
            "severity": "High",
            "status": "Final"
        },
        {
            "id": "RPT-2025-04073",
            "title": "Emerging Ransomware Group Analysis",
            "date": "2025-04-07",
            "type": "Technical",
            "severity": "High",
            "status": "Final"
        },
        {
            "id": "RPT-2025-04072",
            "title": "Executive Threat Landscape Overview",
            "date": "2025-04-07",
            "type": "Executive",
            "severity": "Medium",
            "status": "Final"
        },
        {
            "id": "RPT-2025-04063",
            "title": "Financial Sector Threat Assessment",
            "date": "2025-04-06",
            "type": "Threat Intelligence",
            "severity": "High",
            "status": "Final"
        },
        {
            "id": "RPT-2025-04053",
            "title": "Technical Analysis: PII Exposure in Dark Web",
            "date": "2025-04-05",
            "type": "Technical",
            "severity": "Medium",
            "status": "Final"
        }
    ]
    
    # Create a DataFrame
    report_df = pd.DataFrame(reports)
    
    # Report display
    for i, report in enumerate(reports):
        severity_color = "#E74C3C" if report["severity"] == "Critical" else "#F1C40F" if report["severity"] == "High" else "#3498DB" if report["severity"] == "Medium" else "#2ECC71"
        
        with st.container():
            cols = st.columns([4, 1, 1, 1])
            
            with cols[0]:
                st.markdown(f"#### {report['title']}")
                st.caption(f"ID: {report['id']} | Date: {report['date']}")
            
            with cols[1]:
                st.markdown(f"**Type:** {report['type']}")
            
            with cols[2]:
                st.markdown(f"**<span style='color:{severity_color}'>{report['severity']}</span>**", unsafe_allow_html=True)
            
            with cols[3]:
                st.button("View", key=f"view_report_{i}")
            
            st.markdown("---")
    
    # Generate a report
    st.markdown("### Generate New Report")
    
    with st.form("report_generator"):
        st.markdown("#### Report Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            report_title = st.text_input("Report Title", placeholder="e.g. Monthly Threat Intelligence Summary")
            
            report_type_selection = st.selectbox(
                "Report Type",
                ["Threat Intelligence", "Data Breach", "Executive", "Technical", "Custom"]
            )
        
        with col2:
            report_period = st.selectbox(
                "Report Period",
                ["Last 7 Days", "Last 30 Days", "Last Quarter", "Year to Date", "Custom Range"]
            )
            
            if report_period == "Custom Range":
                start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
                end_date = st.date_input("End Date", datetime.now())
        
        st.markdown("#### Report Content")
        
        include_options = st.columns(3)
        
        with include_options[0]:
            include_summary = st.checkbox("Executive Summary", value=True)
            include_threats = st.checkbox("Threat Overview", value=True)
            include_breaches = st.checkbox("Data Breaches", value=True)
        
        with include_options[1]:
            include_credentials = st.checkbox("Exposed Credentials", value=True)
            include_ioc = st.checkbox("Indicators of Compromise", value=True)
            include_actors = st.checkbox("Threat Actor Analysis", value=True)
        
        with include_options[2]:
            include_trends = st.checkbox("Trend Analysis", value=True)
            include_mitigation = st.checkbox("Mitigation Recommendations", value=True)
            include_references = st.checkbox("References", value=True)
        
        st.markdown("#### Distribution")
        
        distribution = st.multiselect(
            "Distribute To",
            ["Security Team", "Executive Team", "IT Department", "Legal Department", "Custom Recipients"],
            default=["Security Team"]
        )
        
        if "Custom Recipients" in distribution:
            custom_recipients = st.text_input("Custom Recipients (separated by commas)")
        
        generate_button = st.form_submit_button("Generate Report")
        
        if generate_button:
            st.success("Report generation initiated! Your report will be available shortly.")
    
    # Report analytics
    st.markdown("---")
    st.subheader("Report Analytics")
    
    # Report metrics
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric(
            label="Reports Generated",
            value="87",
            delta="12",
            delta_color="normal"
        )
    
    with metric_col2:
        st.metric(
            label="Critical Reports",
            value="23",
            delta="5",
            delta_color="normal"
        )
    
    with metric_col3:
        st.metric(
            label="Avg. Generation Time",
            value="3.5 min",
            delta="-0.8 min",
            delta_color="normal"
        )
    
    with metric_col4:
        st.metric(
            label="Distribution Rate",
            value="97%",
            delta="2%",
            delta_color="normal"
        )
    
    # Report analytics charts
    analytics_tab1, analytics_tab2 = st.tabs(["Report Generation Trends", "Report Distribution"])
    
    with analytics_tab1:
        # Generate dates for the past 30 days
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30, 0, -1)]
        
        # Sample data for report generation
        report_data = {
            'Date': dates,
            'Executive': np.random.randint(0, 2, 30),
            'Threat Intelligence': np.random.randint(1, 4, 30),
            'Data Breach': np.random.randint(0, 3, 30),
            'Technical': np.random.randint(1, 5, 30)
        }
        
        report_df = pd.DataFrame(report_data)
        
        # Create stacked bar chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=report_df['Date'],
            y=report_df['Executive'],
            name='Executive',
            marker_color='#9B59B6'
        ))
        
        fig.add_trace(go.Bar(
            x=report_df['Date'],
            y=report_df['Threat Intelligence'],
            name='Threat Intelligence',
            marker_color='#3498DB'
        ))
        
        fig.add_trace(go.Bar(
            x=report_df['Date'],
            y=report_df['Data Breach'],
            name='Data Breach',
            marker_color='#E74C3C'
        ))
        
        fig.add_trace(go.Bar(
            x=report_df['Date'],
            y=report_df['Technical'],
            name='Technical',
            marker_color='#2ECC71'
        ))
        
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
                title="Number of Reports",
                showgrid=True,
                gridcolor='rgba(44, 62, 80, 0.3)',
                tickfont=dict(color='#ECF0F1')
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
    
    with analytics_tab2:
        # Report distribution pie chart
        st.subheader("Report Distribution by Recipient")
        
        distribution_data = {
            'Recipient': ['Security Team', 'Executive Team', 'IT Department', 'Legal Department', 'Other'],
            'Count': [45, 23, 31, 15, 8]
        }
        
        dist_df = pd.DataFrame(distribution_data)
        
        fig = px.pie(
            dist_df,
            values='Count',
            names='Recipient',
            hole=0.4,
            color_discrete_sequence=['#3498DB', '#9B59B6', '#2ECC71', '#F1C40F', '#E74C3C']
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
            margin=dict(l=0, r=0, t=0, b=10),
            height=350
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Sample report view
    st.markdown("---")
    st.subheader("Sample Report Preview")
    
    # Report header
    st.markdown("# Healthcare Data Breach Intelligence Report")
    st.markdown("**Report ID:** RPT-2025-04083")
    st.markdown("**Date:** April 8, 2025")
    st.markdown("**Classification:** Confidential")
    st.markdown("**Severity:** Critical")
    
    # Table of contents
    st.markdown("## Table of Contents")
    st.markdown("""
    1. Executive Summary
    2. Breach Details
    3. Affected Data
    4. Threat Actor Analysis
    5. Timeline of Events
    6. Technical Indicators
    7. Recommendations
    8. References
    """)
    
    # Executive Summary
    st.markdown("## 1. Executive Summary")
    st.markdown("""
    On April 7, 2025, CyberForge OSINT Platform detected evidence of a significant data breach affecting Memorial Hospital. 
    Patient records containing personally identifiable information (PII) and protected health information (PHI) were 
    discovered for sale on a prominent dark web marketplace. Initial analysis indicates approximately 50,000 patient 
    records may be affected. This report provides detailed analysis of the breach, indicators of compromise, and 
    recommended actions.
    """)
    
    # Key findings
    st.info("""
    **Key Findings:**
    
    * Patient data including names, addresses, social security numbers, and medical records are being offered for sale
    * The threat actor appears to be affiliated with the BlackCat ransomware group
    * Initial access likely occurred between March 15-20, 2025
    * The breach has not yet been publicly disclosed by the healthcare provider
    * Similar tactics have been observed in other healthcare breaches in the past 60 days
    """)
    
    # Breach details
    st.markdown("## 2. Breach Details")
    st.markdown("""
    The data breach was detected on April 7, 2025, at 22:03 UTC when our monitoring system identified a new listing 
    on AlphaBay marketplace offering "Complete patient database from major US hospital" for sale. The listing specifically 
    mentioned Memorial Hospital by name and included sample data as proof of the breach. The seller, operating under the 
    username "MedLeaks", is requesting 45 BTC (approximately $1.8 million USD) for the complete dataset.
    """)
    
    # Sample chart
    affected_data = {
        'Data Type': ['Medical Records', 'Personally Identifiable Information', 'Insurance Information', 'Billing Information', 'Staff Credentials'],
        'Records': [42000, 50000, 38000, 35000, 1200]
    }
    
    affected_df = pd.DataFrame(affected_data)
    
    fig = px.bar(
        affected_df,
        x='Records',
        y='Data Type',
        orientation='h',
        color='Records',
        color_continuous_scale=['#3498DB', '#F1C40F', '#E74C3C'],
        height=300
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(26, 26, 26, 0)',
        plot_bgcolor='rgba(26, 26, 26, 0)',
        coloraxis_showscale=False,
        xaxis=dict(
            title="Number of Records",
            showgrid=True,
            gridcolor='rgba(44, 62, 80, 0.3)',
            tickfont=dict(color='#ECF0F1')
        ),
        yaxis=dict(
            title=None,
            showgrid=False,
            tickfont=dict(color='#ECF0F1')
        ),
        margin=dict(l=0, r=0, t=10, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Report actions
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        st.download_button(
            label="Download Full Report",
            data="This is a placeholder for the full report download",
            file_name="Healthcare_Data_Breach_Report.pdf",
            mime="application/pdf"
        )
    
    with action_col2:
        st.button("Share Report", key="share_report")
    
    with action_col3:
        st.button("Print Report", key="print_report")
