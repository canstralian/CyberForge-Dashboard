"""
Deployment Recommendation Component

This component provides UI for viewing and applying deployment recommendations.
"""
import asyncio
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from typing import List, Dict, Any, Optional, Tuple, Union

# Import UI components
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards

# Import services and models
from src.streamlit_database import get_db_session, run_async
from src.api.services.deployment_recommendation_service import DeploymentRecommendationService
from src.models.deployment import (
    DeploymentRecommendation, DeploymentSecurityConfig,
    DeploymentHistory, SecurityConfigLevel,
    DeploymentTimingRecommendation, DeploymentPlatform,
    DeploymentRegion, SecurityConfigCategory
)
from src.models.subscription import SubscriptionTier


async def get_user_recommendations(user_id=1, active_only=True, expired=False, limit=5):
    """Get deployment recommendations for a user."""
    async with get_db_session() as session:
        service = DeploymentRecommendationService(session)
        recommendations = await service.get_recommendations_for_user(
            user_id=user_id,
            active_only=active_only,
            expired=expired,
            limit=limit
        )
        return recommendations


async def generate_threat_based_recommendation(user_id=1, look_back_days=7, 
                                              override_title=None, override_description=None):
    """Generate a new threat-based deployment recommendation."""
    async with get_db_session() as session:
        service = DeploymentRecommendationService(session)
        recommendation = await service.generate_threat_based_recommendations(
            user_id=user_id,
            look_back_days=look_back_days,
            override_title=override_title,
            override_description=override_description
        )
        return recommendation


async def generate_cost_optimization_recommendation(user_id=1):
    """Generate a new cost optimization recommendation."""
    async with get_db_session() as session:
        service = DeploymentRecommendationService(session)
        recommendation = await service.generate_cost_optimization_recommendations(
            user_id=user_id
        )
        return recommendation


async def mark_recommendation_applied(recommendation_id):
    """Mark a deployment recommendation as applied."""
    async with get_db_session() as session:
        service = DeploymentRecommendationService(session)
        success = await service.mark_recommendation_applied(recommendation_id)
        return success


async def record_deployment(user_id=1, recommendation_id=None, title=None, was_successful=True):
    """Record a deployment in the history."""
    async with get_db_session() as session:
        service = DeploymentRecommendationService(session)
        deployment = await service.record_deployment(
            user_id=user_id,
            recommendation_id=recommendation_id,
            title=title or "Manual Deployment",
            description="User initiated deployment",
            was_successful=was_successful
        )
        return deployment


async def get_deployment_history(user_id=1, limit=10):
    """Get deployment history for a user."""
    async with get_db_session() as session:
        service = DeploymentRecommendationService(session)
        history = await service.get_deployment_history(
            user_id=user_id,
            limit=limit
        )
        return history


def render_security_level_badge(level):
    """Render a security level badge."""
    if level == "STRICT":
        color = "#E74C3C"  # Red
        label = "Strict"
    elif level == "ENHANCED":
        color = "#F39C12"  # Orange
        label = "Enhanced"
    elif level == "STANDARD":
        color = "#3498DB"  # Blue
        label = "Standard"
    else:
        color = "#7F8C8D"  # Gray
        label = "Basic"
    
    return f"""
    <span style="
        background-color: {color}; 
        color: white; 
        padding: 2px 8px; 
        border-radius: 4px; 
        font-size: 0.8em; 
        font-weight: bold;
    ">
        {label}
    </span>
    """


def render_timing_badge(timing):
    """Render a timing recommendation badge."""
    if timing == "HIGH_RISK":
        color = "#E74C3C"  # Red
        icon = "🚨"
        label = "High Risk"
    elif timing == "DELAY_RECOMMENDED":
        color = "#F39C12"  # Orange
        icon = "⚠️"
        label = "Delay Recommended"
    elif timing == "CAUTION":
        color = "#F1C40F"  # Yellow
        icon = "⚠️"
        label = "Caution"
    else:  # SAFE_TO_DEPLOY
        color = "#2ECC71"  # Green
        icon = "✅"
        label = "Safe to Deploy"
    
    return f"""
    <span style="
        background-color: {color}; 
        color: white; 
        padding: 2px 8px; 
        border-radius: 4px; 
        font-size: 0.8em; 
        font-weight: bold;
    ">
        {icon} {label}
    </span>
    """


def render_recommendation_card(recommendation):
    """Render a deployment recommendation card."""
    # Format date
    created_at = recommendation.created_at.strftime("%B %d, %Y")
    expires_at = recommendation.expires_at.strftime("%B %d, %Y") if recommendation.expires_at else "Never"
    
    # Security level badge
    security_level_html = render_security_level_badge(recommendation.security_level)
    
    # Timing badge
    timing_html = render_timing_badge(recommendation.timing_recommendation)
    
    # Card with key details
    st.markdown(f"""
    <div style="
        border: 1px solid rgba(44, 62, 80, 0.4); 
        border-radius: 6px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: rgba(44, 62, 80, 0.1);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <div>
                <h3 style="margin: 0; color: #ECF0F1;">{recommendation.title}</h3>
                <p style="margin: 5px 0; color: #7F8C8D;">Created on {created_at}</p>
            </div>
            <div>
                {security_level_html}
                &nbsp;&nbsp;
                {timing_html}
            </div>
        </div>
        <p style="margin-bottom: 15px;">{recommendation.description}</p>
        <div style="display: flex; gap: 10px;">
            <button class="view-details-{recommendation.id}" style="
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
            ">View Details</button>
        </div>
    </div>
    
    <script>
        // JavaScript to handle button click
        document.querySelector('.view-details-{recommendation.id}').addEventListener('click', function() {{
            // Use Streamlit's postMessage API to communicate with Python
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: {recommendation.id},
                dataType: 'interactionData'
            }}, '*');
        }});
    </script>
    """, unsafe_allow_html=True)
    
    # Add a button with the same functionality that works with Streamlit's click handling
    if st.button(f"View Details", key=f"details_{recommendation.id}"):
        st.session_state.selected_recommendation = recommendation.id
        st.rerun()


def render_recommendation_details(recommendation):
    """Render detailed view of a deployment recommendation."""
    st.markdown(f"## {recommendation.title}")
    
    # Back button
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("← Back"):
            st.session_state.selected_recommendation = None
            st.rerun()
    
    # Main details in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Security Level", recommendation.security_level.replace("_", " ").title())
    
    with col2:
        st.metric("Recommendation Type", "Threat-Based" if recommendation.is_threat_based else "Cost Optimization")
    
    with col3:
        # Calculate days until expiry
        if recommendation.expires_at:
            days_left = (recommendation.expires_at - datetime.now()).days
            days_left = max(0, days_left)  # Ensure non-negative
            st.metric("Days Until Expiry", days_left)
        else:
            st.metric("Days Until Expiry", "Never")
    
    style_metric_cards()
    
    # Deployment timing
    st.markdown("### Deployment Timing")
    
    # Create timing status with colored badge and justification
    timing_html = render_timing_badge(recommendation.timing_recommendation)
    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        {timing_html}
        <p style="margin-top: 10px;">{recommendation.timing_justification}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # If recommendation specifies a window, show it
    if recommendation.recommended_window_start and recommendation.recommended_window_end:
        start_date = recommendation.recommended_window_start.strftime("%B %d, %Y")
        end_date = recommendation.recommended_window_end.strftime("%B %d, %Y")
        
        st.markdown(f"""
        <div style="
            padding: 10px 15px;
            background-color: rgba(44, 62, 80, 0.2);
            border-radius: 6px;
            margin-bottom: 20px;
        ">
            <p><strong>Recommended Deployment Window:</strong> {start_date} to {end_date}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Show threat assessment if it's a threat-based recommendation
    if recommendation.is_threat_based:
        st.markdown("### Threat Assessment")
        
        # Threat counts
        counts = st.columns(3)
        with counts[0]:
            st.metric("High Risk Threats", recommendation.high_risk_threats_count, delta=None, delta_color="inverse")
        with counts[1]:
            st.metric("Medium Risk Threats", recommendation.medium_risk_threats_count, delta=None, delta_color="inverse")
        with counts[2]:
            st.metric("Low Risk Threats", recommendation.low_risk_threats_count, delta=None, delta_color="inverse")
        
        style_metric_cards()
        
        # Threat assessment summary
        st.markdown(f"""
        <div style="
            padding: 15px;
            background-color: rgba(44, 62, 80, 0.2);
            border-radius: 6px;
            margin-top: 15px;
            margin-bottom: 20px;
        ">
            <h4 style="margin-top: 0;">Threat Assessment Summary</h4>
            <p>{recommendation.threat_assessment_summary}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Render threat analysis visualization
        render_threat_analysis_chart(recommendation)
    
    # Show cost assessment if it's a cost optimization recommendation
    if not recommendation.is_threat_based:
        st.markdown("### Cost Optimization")
        
        # Render cost visualization
        render_cost_chart([recommendation])
    
    # Security settings if available
    if recommendation.security_settings:
        st.markdown("### Security Settings")
        
        try:
            settings = recommendation.security_settings
            if isinstance(settings, str):
                settings = json.loads(settings)
                
            # Create a DataFrame for display
            settings_data = []
            for category, options in settings.items():
                for option, value in options.items():
                    settings_data.append({
                        "Category": category.replace("_", " ").title(),
                        "Setting": option.replace("_", " ").title(),
                        "Value": str(value).replace("_", " ").title() if isinstance(value, str) else str(value)
                    })
            
            settings_df = pd.DataFrame(settings_data)
            
            # Use Streamlit's experimental_allows_module to import AgGrid if available
            st.dataframe(settings_df)
        except Exception as e:
            st.warning(f"Could not parse security settings: {str(e)}")
    
    # Apply recommendation button
    st.markdown("### Apply This Recommendation")
    
    if st.button("Apply Now", key="apply_recommendation"):
        with st.spinner("Applying recommendation..."):
            # Mark as applied in the database
            success = run_async(mark_recommendation_applied, recommendation.id)
            
            # Record the deployment
            if success:
                deployment = run_async(
                    record_deployment,
                    user_id=1,
                    recommendation_id=recommendation.id,
                    title=f"Applied: {recommendation.title}",
                    was_successful=True
                )
                
                st.success("Recommendation applied successfully!")
                st.session_state.selected_recommendation = None
                st.rerun()
            else:
                st.error("Failed to apply recommendation. Please try again.")


def render_deployment_history():
    """Render deployment history."""
    st.markdown("## Deployment History")
    
    # Get deployment history
    history = run_async(get_deployment_history, 1)
    
    if not history:
        st.info("No deployment history found.")
        return
    
    # Create a DataFrame for display
    history_data = []
    for deployment in history:
        history_data.append({
            "ID": deployment.id,
            "Date": deployment.created_at,
            "Title": deployment.title,
            "Status": "Successful" if deployment.was_successful else "Failed",
            "Based On": deployment.recommendation_id if deployment.recommendation_id else "Manual"
        })
    
    history_df = pd.DataFrame(history_data)
    
    # Format the columns
    history_df["Date"] = history_df["Date"].dt.strftime("%Y-%m-%d %H:%M")
    
    # Apply custom styling
    def highlight_status(val):
        if val == "Successful":
            return "background-color: rgba(46, 204, 113, 0.2); color: #2ECC71"
        else:
            return "background-color: rgba(231, 76, 60, 0.2); color: #E74C3C"
    
    # Display the styled DataFrame
    st.dataframe(
        history_df.style.applymap(highlight_status, subset=["Status"]),
        use_container_width=True
    )


def render_threat_analysis_chart(recommendation=None):
    """Render a chart of threat analysis."""
    # Create sample data if no recommendation provided
    if not recommendation or not recommendation.is_threat_based:
        threat_data = {
            "SQL Injection": 3,
            "XSS": 2,
            "CSRF": 1,
            "Session Hijacking": 2,
            "Broken Authentication": 4
        }
        high_risk = 3
        medium_risk = 5
        low_risk = 4
    else:
        # Extract actual data
        high_risk = recommendation.high_risk_threats_count
        medium_risk = recommendation.medium_risk_threats_count
        low_risk = recommendation.low_risk_threats_count
        
        # Sample distribution of threats for visualization
        # In production, this would come from the actual threat assessment
        threat_data = {
            "SQL Injection": high_risk > 0,
            "XSS": high_risk > 1 or medium_risk > 0,
            "CSRF": medium_risk > 1 or low_risk > 0,
            "Session Hijacking": medium_risk > 2,
            "Broken Authentication": high_risk > 0 or medium_risk > 0,
            "Insecure File Upload": low_risk > 1,
            "Unpatched Vulnerabilities": high_risk > 2 or medium_risk > 3,
            "Insecure API": medium_risk > 1 or low_risk > 2
        }
        # Convert booleans to counts
        threat_data = {k: (1 if v else 0) * (
            3 if k in ["SQL Injection", "Broken Authentication", "Unpatched Vulnerabilities"] else
            2 if k in ["XSS", "Session Hijacking", "Insecure API"] else 1
        ) for k, v in threat_data.items()}
    
    # Create data for chart
    df = pd.DataFrame({
        "Threat": list(threat_data.keys()),
        "Count": list(threat_data.values())
    })
    
    # Create color map based on count (higher = more red)
    colors = ["#2ECC71", "#F1C40F", "#E67E22", "#E74C3C"]
    max_count = max(threat_data.values()) if threat_data else 1
    
    color_scale = []
    for i, (threat, count) in enumerate(threat_data.items()):
        color_idx = min(int((count / max_count) * (len(colors) - 1)), len(colors) - 1)
        color_scale.append(colors[color_idx])
    
    # Create the bar chart
    fig = px.bar(
        df, 
        x="Count", 
        y="Threat",
        orientation="h",
        title="Threat Distribution",
        labels={"Count": "Occurrences", "Threat": ""},
        color="Count",
        color_continuous_scale=["#2ECC71", "#F1C40F", "#E67E22", "#E74C3C"]
    )
    
    # Update layout for Streamlit dark theme
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ECF0F1"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create a pie chart of risk levels
    risk_df = pd.DataFrame({
        "Risk Level": ["High Risk", "Medium Risk", "Low Risk"],
        "Count": [high_risk, medium_risk, low_risk]
    })
    
    risk_colors = ["#E74C3C", "#F39C12", "#2ECC71"]
    
    fig = px.pie(
        risk_df,
        values="Count",
        names="Risk Level",
        title="Threat Risk Distribution",
        color="Risk Level",
        color_discrete_map={
            "High Risk": "#E74C3C",
            "Medium Risk": "#F39C12",
            "Low Risk": "#2ECC71"
        }
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ECF0F1")
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_cost_chart(recommendations=None):
    """Render a cost comparison chart."""
    # Create sample data if no recommendations provided
    if not recommendations:
        cost_data = {
            "Current": 850,
            "Optimized": 520
        }
        
        savings_pct = 38.8
    else:
        # Use data from the first recommendation
        # In production, this would be extracted from the recommendation
        cost_data = {
            "Current": 850,
            "Optimized": 520
        }
        
        savings_pct = ((cost_data["Current"] - cost_data["Optimized"]) / cost_data["Current"]) * 100
    
    # Show savings metric
    st.metric(
        "Estimated Monthly Savings", 
        f"${cost_data['Current'] - cost_data['Optimized']}", 
        f"{savings_pct:.1f}%"
    )
    style_metric_cards()
    
    # Create data for chart
    df = pd.DataFrame({
        "Scenario": list(cost_data.keys()),
        "Cost": list(cost_data.values())
    })
    
    # Create the bar chart
    fig = go.Figure()
    
    # Add bars
    fig.add_trace(go.Bar(
        x=df["Scenario"],
        y=df["Cost"],
        marker_color=["#E74C3C", "#2ECC71"],
        text=df["Cost"].apply(lambda x: f"${x}"),
        textposition="auto"
    ))
    
    # Update layout for Streamlit dark theme
    fig.update_layout(
        title="Cost Comparison",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ECF0F1"),
        yaxis=dict(
            title="Cost ($)",
            gridcolor="rgba(255,255,255,0.1)"
        ),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)")
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_deployment_recommendations():
    """Main function to render the deployment recommendations component."""
    colored_header(
        label="Deployment Recommendations",
        description="Intelligent deployment recommendations based on threat analysis and cost optimization",
        color_name="blue-90"
    )
    
    # Initialize session state
    if 'selected_recommendation' not in st.session_state:
        st.session_state.selected_recommendation = None
    
    # Create tabs for different sections
    tabs = st.tabs(["Recommendations", "Generate New", "Deployment History"])
    
    # Recommendations tab
    with tabs[0]:
        if st.session_state.selected_recommendation is not None:
            # Get the selected recommendation
            recommendations = run_async(get_user_recommendations, 1)
            selected = next((r for r in recommendations if r.id == st.session_state.selected_recommendation), None)
            
            if selected:
                render_recommendation_details(selected)
            else:
                st.error("Selected recommendation not found.")
                st.session_state.selected_recommendation = None
                st.rerun()
        else:
            st.markdown("## Active Recommendations")
            
            # Get active recommendations
            recommendations = run_async(get_user_recommendations, 1)
            
            if not recommendations:
                st.info("No active recommendations found. Generate new recommendations or check deployment history.")
            else:
                for recommendation in recommendations:
                    render_recommendation_card(recommendation)
    
    # Generate New tab
    with tabs[1]:
        st.markdown("## Generate New Recommendations")
        
        st.markdown("""
        Generate new deployment recommendations based on different analysis types.
        Each type focuses on specific aspects of your environment to provide tailored recommendations.
        """)
        
        # Analysis type selection
        analysis_type = st.radio(
            "Select Analysis Type",
            ["Threat-Based Analysis", "Cost Optimization Analysis"]
        )
        
        if analysis_type == "Threat-Based Analysis":
            st.markdown("""
            **Threat-Based Analysis** examines current threat intelligence to recommend:
            
            - Optimal security configurations
            - Best timing for deployment
            - Platform-specific security settings
            """)
            
            look_back_days = st.slider("Look Back Period (days)", 1, 30, 7)
            
            if st.button("Generate Threat-Based Recommendation"):
                with st.spinner("Analyzing threat intelligence..."):
                    recommendation = run_async(generate_threat_based_recommendation, 1, look_back_days)
                    
                    if recommendation:
                        st.success("Threat-based recommendation generated successfully!")
                        st.session_state.selected_recommendation = recommendation.id
                        st.rerun()
                    else:
                        st.warning("No significant threats detected to generate recommendations.")
        
        elif analysis_type == "Cost Optimization Analysis":
            st.markdown("""
            **Cost Optimization Analysis** examines your usage patterns to recommend:
            
            - Cost-effective deployment options
            - Right-sizing for resources
            - Optimal region/platform selection
            """)
            
            if st.button("Generate Cost Optimization Recommendation"):
                with st.spinner("Analyzing cost optimization opportunities..."):
                    recommendation = run_async(generate_cost_optimization_recommendation, 1)
                    
                    if recommendation:
                        st.success("Cost optimization recommendation generated successfully!")
                        st.session_state.selected_recommendation = recommendation.id
                        st.rerun()
                    else:
                        st.warning("No significant cost optimization opportunities detected.")
    
    # Deployment History tab
    with tabs[2]:
        render_deployment_history()