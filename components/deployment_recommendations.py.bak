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


async def generate_threat_based_recommendation(user_id=1, look_back_days=7):
    """Generate a new threat-based deployment recommendation."""
    async with get_db_session() as session:
        service = DeploymentRecommendationService(session)
        recommendation = await service.generate_threat_based_recommendations(
            user_id=user_id,
            look_back_days=look_back_days
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
        recommendation = await service.mark_recommendation_applied(
            recommendation_id=recommendation_id
        )
        return recommendation


async def record_deployment(user_id=1, recommendation_id=None, title=None, was_successful=True):
    """Record a deployment in the history."""
    async with get_db_session() as session:
        service = DeploymentRecommendationService(session)
        history = await service.record_deployment(
            user_id=user_id,
            title=title or "Manual Deployment",
            recommendation_id=recommendation_id,
            was_successful=was_successful
        )
        return history


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
    if level == SecurityConfigLevel.STANDARD:
        color = "blue"
        text = "STANDARD"
    elif level == SecurityConfigLevel.ENHANCED:
        color = "orange"
        text = "ENHANCED"
    elif level == SecurityConfigLevel.STRICT:
        color = "red"
        text = "STRICT"
    else:
        color = "gray"
        text = "CUSTOM"
    
    st.markdown(f"""
    <div style="display: inline-block; padding: 4px 8px; background-color: {color}30; 
    color: {color}; border: 1px solid {color}; border-radius: 4px; font-size: 0.8em; font-weight: bold;">
    {text}
    </div>
    """, unsafe_allow_html=True)


def render_timing_badge(timing):
    """Render a timing recommendation badge."""
    if timing == DeploymentTimingRecommendation.SAFE_TO_DEPLOY:
        color = "green"
        text = "SAFE TO DEPLOY"
    elif timing == DeploymentTimingRecommendation.CAUTION:
        color = "orange"
        text = "CAUTION"
    elif timing == DeploymentTimingRecommendation.DELAY_RECOMMENDED:
        color = "red"
        text = "DELAY RECOMMENDED"
    elif timing == DeploymentTimingRecommendation.HIGH_RISK:
        color = "darkred"
        text = "HIGH RISK"
    else:
        color = "gray"
        text = "UNKNOWN"
    
    st.markdown(f"""
    <div style="display: inline-block; padding: 4px 8px; background-color: {color}30; 
    color: {color}; border: 1px solid {color}; border-radius: 4px; font-size: 0.8em; font-weight: bold;">
    {text}
    </div>
    """, unsafe_allow_html=True)


def render_recommendation_card(recommendation):
    """Render a deployment recommendation card."""
    with st.container():
        st.markdown(f"""
        <div style="border-left: 4px solid #3498DB; padding-left: 10px; margin-bottom: 5px;">
            <h3 style="margin-bottom: 0;">{recommendation.title}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        cols = st.columns([3, 2])
        with cols[0]:
            st.markdown(f"**Description:** {recommendation.description[:100]}...")
            
            st.markdown("**Security Level:**")
            render_security_level_badge(recommendation.security_level)
            
            st.markdown("**Timing Recommendation:**")
            render_timing_badge(recommendation.timing_recommendation)
            
            if recommendation.recommended_window_start and recommendation.recommended_window_end:
                window_start = recommendation.recommended_window_start.strftime("%Y-%m-%d %H:%M")
                window_end = recommendation.recommended_window_end.strftime("%Y-%m-%d %H:%M")
                st.markdown(f"**Recommended Window:** {window_start} to {window_end}")
        
        with cols[1]:
            if recommendation.estimated_cost is not None:
                st.metric("Estimated Cost", f"${recommendation.estimated_cost:.2f}")
            
            if recommendation.cost_saving_potential is not None:
                st.metric("Potential Savings", f"${recommendation.cost_saving_potential:.2f}", delta="↓")
            
            # Threat counts if available
            if recommendation.high_risk_threats_count or recommendation.medium_risk_threats_count or recommendation.low_risk_threats_count:
                st.markdown("**Threat Assessment**")
                threat_cols = st.columns(3)
                with threat_cols[0]:
                    st.metric("High", recommendation.high_risk_threats_count or 0, delta_color="inverse")
                with threat_cols[1]:
                    st.metric("Medium", recommendation.medium_risk_threats_count or 0, delta_color="inverse")
                with threat_cols[2]:
                    st.metric("Low", recommendation.low_risk_threats_count or 0, delta_color="inverse")
        
        # Actions
        if not recommendation.is_applied:
            if st.button("View Details", key=f"view_{recommendation.id}"):
                st.session_state.selected_recommendation = recommendation.id
                st.rerun()
                
            if st.button("Apply Recommendation", key=f"apply_{recommendation.id}"):
                run_async(mark_recommendation_applied, recommendation.id)
                run_async(record_deployment, 1, recommendation.id, recommendation.title)
                st.success(f"Recommendation '{recommendation.title}' applied successfully!")
                st.rerun()
        else:
            st.success("This recommendation has been applied.")
        
        st.markdown("---")


def render_recommendation_details(recommendation):
    """Render detailed view of a deployment recommendation."""
    st.markdown(f"## {recommendation.title}")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Description:** {recommendation.description}")
        
        st.markdown("### Security Configuration")
        st.markdown(f"**Security Level:** {recommendation.security_level.name}")
        
        # Parse and display security settings
        if recommendation.security_settings:
            try:
                settings = json.loads(recommendation.security_settings)
                for category, configs in settings.items():
                    st.markdown(f"**{category}**")
                    for config in configs:
                        st.markdown(f"- {config['name']}: {config['value']}")
            except:
                st.markdown(recommendation.security_settings)
        
        st.markdown("### Deployment Timing")
        st.markdown(f"**Recommendation:** {recommendation.timing_recommendation.name}")
        st.markdown(f"**Justification:** {recommendation.timing_justification}")
        
        if recommendation.recommended_window_start and recommendation.recommended_window_end:
            window_start = recommendation.recommended_window_start.strftime("%Y-%m-%d %H:%M")
            window_end = recommendation.recommended_window_end.strftime("%Y-%m-%d %H:%M")
            st.markdown(f"**Recommended Window:** {window_start} to {window_end}")
        
        st.markdown("### Cost Analysis")
        if recommendation.estimated_cost is not None:
            st.metric("Estimated Cost", f"${recommendation.estimated_cost:.2f}")
        
        if recommendation.cost_saving_potential is not None:
            st.metric("Potential Savings", f"${recommendation.cost_saving_potential:.2f}")
            
        if recommendation.cost_justification:
            st.markdown(f"**Cost Justification:** {recommendation.cost_justification}")
    
    with col2:
        if recommendation.recommended_platform:
            st.markdown(f"**Platform:** {recommendation.recommended_platform.name}")
            
        if recommendation.recommended_region:
            st.markdown(f"**Region:** {recommendation.recommended_region.name}")
        
        # Expiration info
        if recommendation.expires_at:
            expires_at = recommendation.expires_at.strftime("%Y-%m-%d %H:%M")
            st.markdown(f"**Expires:** {expires_at}")
        
        # Timestamps
        created_at = recommendation.created_at.strftime("%Y-%m-%d %H:%M") if recommendation.created_at else "N/A"
        st.markdown(f"**Created:** {created_at}")
        
        if recommendation.applied_at:
            applied_at = recommendation.applied_at.strftime("%Y-%m-%d %H:%M")
            st.markdown(f"**Applied:** {applied_at}")
    
    # Threat analysis chart
    render_threat_analysis_chart(recommendation)
    
    # Cost comparison chart
    render_cost_chart(recommendation)
    
    # Actions
    st.markdown("### Actions")
    cols = st.columns([1, 1, 2])
    with cols[0]:
        if not recommendation.is_applied:
            if st.button("Apply Recommendation"):
                run_async(mark_recommendation_applied, recommendation.id)
                run_async(record_deployment, 1, recommendation.id, recommendation.title)
                st.success(f"Recommendation '{recommendation.title}' applied successfully!")
                st.rerun()
        else:
            st.success("This recommendation has been applied.")
    
    with cols[1]:
        if st.button("Back to List"):
            st.session_state.selected_recommendation = None
            st.rerun()


def render_deployment_history():
    """Render deployment history."""
    st.markdown("## Deployment History")
    
    history = run_async(get_deployment_history, 1)
    
    if not history:
        st.info("No deployment history found.")
        return
    
    # Convert to dataframe for display
    history_data = []
    for item in history:
        history_data.append({
            "ID": item.id,
            "Title": item.title,
            "Platform": item.platform.name if item.platform else "N/A",
            "Security Level": item.security_level.name if item.security_level else "N/A",
            "Status": "Success" if item.was_successful else "Failed",
            "Date": item.deployed_at.strftime("%Y-%m-%d %H:%M") if item.deployed_at else "N/A"
        })
    
    history_df = pd.DataFrame(history_data)
    st.dataframe(history_df, use_container_width=True)


def render_threat_analysis_chart(recommendation=None):
    """Render a chart of threat analysis."""
    st.markdown("### Threat Analysis")
    
    # If recommendation is provided, use its data
    if recommendation and (
        recommendation.high_risk_threats_count is not None or 
        recommendation.medium_risk_threats_count is not None or 
        recommendation.low_risk_threats_count is not None
    ):
        threat_data = {
            "Risk Level": ["High", "Medium", "Low"],
            "Count": [
                recommendation.high_risk_threats_count or 0,
                recommendation.medium_risk_threats_count or 0,
                recommendation.low_risk_threats_count or 0
            ]
        }
        colors = ["#E74C3C", "#F39C12", "#3498DB"]
    else:
        # Use sample data
        threat_data = {
            "Risk Level": ["High", "Medium", "Low"],
            "Count": [3, 7, 12]
        }
        colors = ["#E74C3C", "#F39C12", "#3498DB"]
    
    fig = px.bar(
        threat_data, 
        x="Risk Level", 
        y="Count", 
        color="Risk Level",
        color_discrete_sequence=colors,
        title="Threat Analysis by Risk Level"
    )
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#ECF0F1"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.1)")
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_cost_chart(recommendations=None):
    """Render a cost comparison chart."""
    st.markdown("### Cost Analysis")
    
    cost_data = {
        "Deployment Option": ["Current", "Recommended"],
        "Cost": [100, 75]  # Sample data
    }
    
    # If recommendation is provided with cost data, use it
    if recommendations and hasattr(recommendations, 'estimated_cost') and recommendations.estimated_cost is not None:
        # Assume current cost is higher than recommended
        current_cost = recommendations.estimated_cost + (recommendations.cost_saving_potential or 0)
        cost_data = {
            "Deployment Option": ["Current", "Recommended"],
            "Cost": [current_cost, recommendations.estimated_cost]
        }
    
    fig = px.bar(
        cost_data, 
        x="Deployment Option", 
        y="Cost", 
        color="Deployment Option",
        color_discrete_sequence=["#E74C3C", "#2ECC71"],
        title="Cost Comparison",
        text_auto=True
    )
    
    # Add $ to y-axis labels
    fig.update_layout(
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