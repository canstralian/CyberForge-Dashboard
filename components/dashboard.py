import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import altair as alt
from datetime import datetime, timedelta

def render_dashboard():
    st.title("Dark Web Intelligence Dashboard")
    
    # Date range selector
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("## Overview")
        st.markdown("Real-time monitoring of dark web activities, data breaches, and emerging threats.")
    
    with col2:
        date_range = st.selectbox(
            "Time Range",
            ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last Quarter", "Custom Range"],
            index=1
        )
    
    # Dashboard metrics row
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric(
            label="Active Threats",
            value="27",
            delta="4",
            delta_color="inverse"
        )
    
    with metric_col2:
        st.metric(
            label="Data Breaches",
            value="3",
            delta="-2",
            delta_color="normal"
        )
    
    with metric_col3:
        st.metric(
            label="Credential Leaks",
            value="1,247",
            delta="89",
            delta_color="inverse"
        )
    
    with metric_col4:
        st.metric(
            label="Threat Score",
            value="72/100",
            delta="12",
            delta_color="inverse"
        )
    
    # First row - Threat map and category distribution
    row1_col1, row1_col2 = st.columns([2, 1])
    
    with row1_col1:
        st.subheader("Global Threat Origin Map")
        
        # World map of threat origins
        fig = go.Figure(data=go.Choropleth(
            locations=['USA', 'RUS', 'CHN', 'IRN', 'PRK', 'UKR', 'DEU', 'GBR', 'CAN', 'BRA', 'IND'],
            z=[25, 42, 37, 30, 28, 18, 15, 20, 12, 14, 23],
            colorscale='Reds',
            autocolorscale=False,
            reversescale=False,
            marker_line_color='#2C3E50',
            marker_line_width=0.5,
            colorbar_title='Threat<br>Index',
        ))

        fig.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='equirectangular',
                bgcolor='rgba(26, 26, 26, 0)',
                coastlinecolor='#2C3E50',
                landcolor='#1A1A1A',
                oceancolor='#2C3E50',
            ),
            paper_bgcolor='rgba(26, 26, 26, 0)',
            plot_bgcolor='rgba(26, 26, 26, 0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=400,
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with row1_col2:
        st.subheader("Threat Categories")
        
        # Threat category distribution
        categories = ['Data Breach', 'Ransomware', 'Phishing', 'Malware', 'Identity Theft']
        values = [38, 24, 18, 14, 6]
        
        fig = px.pie(
            names=categories,
            values=values,
            hole=0.6,
            color_discrete_sequence=['#E74C3C', '#F1C40F', '#3498DB', '#2ECC71', '#9B59B6']
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(26, 26, 26, 0)',
            plot_bgcolor='rgba(26, 26, 26, 0)',
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            height=300,
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Second row - Trend and recent activities
    row2_col1, row2_col2 = st.columns([3, 2])
    
    with row2_col1:
        st.subheader("Threat Activity Trend")
        
        # Generate dates for the past 14 days
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(14, 0, -1)]
        
        # Sample data for threats over time
        threat_data = {
            'Date': dates,
            'High': [12, 10, 15, 11, 14, 16, 18, 20, 17, 12, 14, 13, 19, 22],
            'Medium': [23, 25, 22, 20, 24, 25, 26, 24, 22, 21, 23, 25, 28, 27],
            'Low': [32, 30, 35, 34, 36, 33, 30, 34, 38, 37, 35, 34, 32, 30]
        }
        
        df = pd.DataFrame(threat_data)
        
        # Create stacked area chart
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['High'],
            mode='lines',
            line=dict(width=0.5, color='#E74C3C'),
            stackgroup='one',
            name='High'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Medium'],
            mode='lines',
            line=dict(width=0.5, color='#F1C40F'),
            stackgroup='one',
            name='Medium'
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'], y=df['Low'],
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
                title=None,
                tickfont=dict(color='#ECF0F1')
            ),
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with row2_col2:
        st.subheader("Recent Intelligence Feeds")
        
        # Recent dark web activities
        activities = [
            {"time": "10 mins ago", "event": "New ransomware group identified", "severity": "High"},
            {"time": "43 mins ago", "event": "Database with 50K credentials for sale", "severity": "High"},
            {"time": "2 hours ago", "event": "Zero-day exploit being discussed", "severity": "Medium"},
            {"time": "3 hours ago", "event": "New phishing campaign detected", "severity": "Medium"},
            {"time": "5 hours ago", "event": "PII data from financial institution leaked", "severity": "High"}
        ]
        
        for activity in activities:
            severity_color = "#E74C3C" if activity["severity"] == "High" else "#F1C40F" if activity["severity"] == "Medium" else "#2ECC71"
            
            cols = st.columns([1, 4, 1])
            cols[0].caption(activity["time"])
            cols[1].markdown(activity["event"])
            cols[2].markdown(f"<span style='color:{severity_color}'>{activity['severity']}</span>", unsafe_allow_html=True)
            
            st.markdown("---")
    
    # Third row - Sectors at risk and trending keywords
    row3_col1, row3_col2 = st.columns(2)
    
    with row3_col1:
        st.subheader("Sectors at Risk")
        
        # Horizontal bar chart for sectors at risk
        sectors = ['Healthcare', 'Finance', 'Technology', 'Education', 'Government', 'Manufacturing']
        risk_scores = [87, 82, 75, 63, 78, 56]
        
        sector_data = pd.DataFrame({
            'Sector': sectors,
            'Risk Score': risk_scores
        })
        
        fig = px.bar(
            sector_data,
            x='Risk Score',
            y='Sector',
            orientation='h',
            color='Risk Score',
            color_continuous_scale=['#2ECC71', '#F1C40F', '#E74C3C'],
            range_color=[50, 100]
        )
        
        fig.update_layout(
            paper_bgcolor='rgba(26, 26, 26, 0)',
            plot_bgcolor='rgba(26, 26, 26, 0)',
            margin=dict(l=0, r=0, t=0, b=0),
            height=250,
            coloraxis_showscale=False,
            xaxis=dict(
                showgrid=False,
                title=None,
                tickfont=dict(color='#ECF0F1')
            ),
            yaxis=dict(
                showgrid=False,
                title=None,
                tickfont=dict(color='#ECF0F1')
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with row3_col2:
        st.subheader("Trending Keywords")
        
        # Word cloud alternative - trending keywords with frequency
        keywords = [
            {"word": "ransomware", "count": 42},
            {"word": "zero-day", "count": 37},
            {"word": "botnet", "count": 31},
            {"word": "credentials", "count": 28},
            {"word": "bitcoin", "count": 25},
            {"word": "exploit", "count": 23},
            {"word": "malware", "count": 21},
            {"word": "backdoor", "count": 18},
            {"word": "phishing", "count": 16},
            {"word": "darknet", "count": 15}
        ]
        
        keyword_data = pd.DataFrame(keywords)
        
        # Calculate sizes for visual representation
        max_count = max(keyword_data['count'])
        keyword_data['size'] = keyword_data['count'].apply(lambda x: int((x / max_count) * 100) + 70)
        
        # Create a simple horizontal bar to represent frequency
        chart = alt.Chart(keyword_data).mark_bar().encode(
            x=alt.X('count:Q', title=None),
            y=alt.Y('word:N', title=None, sort='-x'),
            color=alt.Color('count:Q', scale=alt.Scale(scheme='reds'), legend=None)
        ).properties(
            height=250
        )
        
        st.altair_chart(chart, use_container_width=True)
    
    # Fourth row - Latest intelligence reports
    st.subheader("Latest Intelligence Reports")
    
    reports = [
        {
            "title": "Major Healthcare Breach Analysis",
            "date": "2025-04-08",
            "summary": "Analysis of recent healthcare data breach affecting over 500,000 patient records.",
            "severity": "Critical"
        },
        {
            "title": "Emerging Ransomware Group Activities",
            "date": "2025-04-07",
            "summary": "New ransomware group targeting financial institutions with sophisticated techniques.",
            "severity": "High"
        },
        {
            "title": "Credential Harvesting Campaign",
            "date": "2025-04-05",
            "summary": "Widespread phishing campaign targeting corporate credentials across multiple sectors.",
            "severity": "Medium"
        }
    ]
    
    row4_cols = st.columns(3)
    
    for i, report in enumerate(reports):
        with row4_cols[i]:
            severity_color = "#E74C3C" if report["severity"] == "Critical" else "#F1C40F" if report["severity"] == "High" else "#2ECC71"
            
            st.markdown(f"#### {report['title']}")
            st.markdown(f"<span style='color:{severity_color}'>{report['severity']}</span> | {report['date']}", unsafe_allow_html=True)
            st.markdown(report["summary"])
            st.button("View Full Report", key=f"report_{i}")
