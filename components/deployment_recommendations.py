"""
Deployment Recommendation Component

This component provides UI for viewing and applying deployment recommendations.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import asyncio

from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards

from src.streamlit_database import get_db_session
from src.api.services.deployment_recommendation_service import DeploymentRecommendationService
from src.models.deployment import (
    SecurityConfigLevel, DeploymentTimingRecommendation, 
    DeploymentPlatform, DeploymentRegion, SecurityConfigCategory
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
        
        # Convert to list of dicts for easier handling in Streamlit
        result = []
        for rec in recommendations:
            security_settings = json.loads(rec.security_settings) if rec.security_settings else {}
            
            rec_dict = {
                "id": rec.id,
                "title": rec.title,
                "description": rec.description,
                "security_level": rec.security_level.value,
                "timing_recommendation": rec.timing_recommendation.value,
                "timing_justification": rec.timing_justification,
                "estimated_cost": rec.estimated_cost,
                "cost_saving_potential": rec.cost_saving_potential,
                "cost_justification": rec.cost_justification,
                "recommended_platform": rec.recommended_platform.value if rec.recommended_platform else None,
                "recommended_region": rec.recommended_region.value if rec.recommended_region else None,
                "threat_assessment_summary": rec.threat_assessment_summary,
                "high_risk_threats_count": rec.high_risk_threats_count,
                "medium_risk_threats_count": rec.medium_risk_threats_count,
                "low_risk_threats_count": rec.low_risk_threats_count,
                "is_active": rec.is_active,
                "is_applied": rec.is_applied,
                "created_at": rec.created_at,
                "updated_at": rec.updated_at,
                "applied_at": rec.applied_at,
                "expires_at": rec.expires_at,
                "security_settings": security_settings,
                "security_configurations": []
            }
            
            # Add security configurations
            for config in rec.security_configurations:
                config_value = json.loads(config.configuration_value) if config.configuration_value else {}
                config_dict = {
                    "id": config.id,
                    "category": config.category.value,
                    "name": config.name,
                    "description": config.description,
                    "configuration_value": config_value,
                    "related_threat_types": config.related_threat_types.split(",") if config.related_threat_types else [],
                    "is_critical": config.is_critical,
                    "is_applied": config.is_applied
                }
                rec_dict["security_configurations"].append(config_dict)
            
            result.append(rec_dict)
        
        return result


async def generate_threat_based_recommendation(user_id=1, look_back_days=7):
    """Generate a new threat-based deployment recommendation."""
    async with get_db_session() as session:
        service = DeploymentRecommendationService(session)
        recommendation = await service.generate_threat_based_recommendations(
            user_id=user_id,
            look_back_days=look_back_days
        )
        return recommendation is not None


async def generate_cost_optimization_recommendation(user_id=1):
    """Generate a new cost optimization recommendation."""
    async with get_db_session() as session:
        service = DeploymentRecommendationService(session)
        recommendation = await service.generate_cost_optimization_recommendations(
            user_id=user_id
        )
        return recommendation is not None


async def mark_recommendation_applied(recommendation_id):
    """Mark a deployment recommendation as applied."""
    async with get_db_session() as session:
        service = DeploymentRecommendationService(session)
        recommendation = await service.mark_recommendation_applied(
            recommendation_id=recommendation_id
        )
        return recommendation is not None


async def record_deployment(user_id=1, recommendation_id=None, title=None, was_successful=True):
    """Record a deployment in the history."""
    if title is None:
        title = "Manual deployment" if recommendation_id is None else "Recommendation-based deployment"
        
    async with get_db_session() as session:
        service = DeploymentRecommendationService(session)
        
        # If we have a recommendation_id, get the details
        if recommendation_id is not None:
            recommendations = await service.get_recommendations_for_user(user_id=user_id)
            recommendation = next((r for r in recommendations if r.id == recommendation_id), None)
            
            if recommendation:
                platform = recommendation.recommended_platform
                region = recommendation.recommended_region
                security_level = recommendation.security_level
                security_summary = recommendation.threat_assessment_summary
                actual_cost = recommendation.estimated_cost
            else:
                platform = None
                region = None
                security_level = None
                security_summary = None
                actual_cost = None
        else:
            platform = None
            region = None
            security_level = None
            security_summary = None
            actual_cost = None
        
        deployment = await service.record_deployment(
            user_id=user_id,
            title=title,
            recommendation_id=recommendation_id,
            platform=platform,
            region=region,
            security_level=security_level,
            security_config_summary=security_summary,
            was_successful=was_successful,
            actual_cost=actual_cost
        )
        
        return deployment is not None


async def get_deployment_history(user_id=1, limit=10):
    """Get deployment history for a user."""
    async with get_db_session() as session:
        service = DeploymentRecommendationService(session)
        history = await service.get_deployment_history(
            user_id=user_id,
            limit=limit
        )
        
        # Convert to list of dicts for easier handling in Streamlit
        result = []
        for deployment in history:
            result.append({
                "id": deployment.id,
                "title": deployment.title,
                "description": deployment.description,
                "platform": deployment.platform.value if deployment.platform else None,
                "region": deployment.region.value if deployment.region else None,
                "security_level": deployment.security_level.value if deployment.security_level else None,
                "security_config_summary": deployment.security_config_summary,
                "was_successful": deployment.was_successful,
                "failure_reason": deployment.failure_reason,
                "actual_cost": deployment.actual_cost,
                "deployed_at": deployment.deployed_at
            })
            
        return result


def render_security_level_badge(level):
    """Render a security level badge."""
    if level == SecurityConfigLevel.STRICT.value:
        bg_color = "#E74C3C"  # Red
        text = "STRICT"
    elif level == SecurityConfigLevel.ENHANCED.value:
        bg_color = "#F1C40F"  # Yellow
        text = "ENHANCED"
    elif level == SecurityConfigLevel.CUSTOM.value:
        bg_color = "#9B59B6"  # Purple
        text = "CUSTOM"
    else:  # STANDARD
        bg_color = "#2ECC71"  # Green
        text = "STANDARD"
    
    return f"""
    <span style="
        background-color: {bg_color};
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
    ">{text}</span>
    """


def render_timing_badge(timing):
    """Render a timing recommendation badge."""
    if timing == DeploymentTimingRecommendation.HIGH_RISK.value:
        bg_color = "#E74C3C"  # Red
        text = "HIGH RISK"
    elif timing == DeploymentTimingRecommendation.DELAY_RECOMMENDED.value:
        bg_color = "#F1C40F"  # Yellow
        text = "DELAY RECOMMENDED"
    elif timing == DeploymentTimingRecommendation.CAUTION.value:
        bg_color = "#F39C12"  # Orange
        text = "CAUTION"
    else:  # SAFE_TO_DEPLOY
        bg_color = "#2ECC71"  # Green
        text = "SAFE TO DEPLOY"
    
    return f"""
    <span style="
        background-color: {bg_color};
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
    ">{text}</span>
    """


def render_recommendation_card(recommendation):
    """Render a deployment recommendation card."""
    # Determine color based on timing recommendation
    if recommendation["timing_recommendation"] == DeploymentTimingRecommendation.HIGH_RISK.value:
        border_color = "#E74C3C"  # Red
    elif recommendation["timing_recommendation"] == DeploymentTimingRecommendation.DELAY_RECOMMENDED.value:
        border_color = "#F1C40F"  # Yellow
    elif recommendation["timing_recommendation"] == DeploymentTimingRecommendation.CAUTION.value:
        border_color = "#F39C12"  # Orange
    else:  # SAFE_TO_DEPLOY
        border_color = "#2ECC71"  # Green
    
    # Format dates
    created_date = recommendation["created_at"].strftime("%b %d, %Y") if recommendation["created_at"] else "N/A"
    expires_date = recommendation["expires_at"].strftime("%b %d, %Y") if recommendation["expires_at"] else "No expiration"
    
    # Format status
    status_text = "Applied" if recommendation["is_applied"] else "Pending"
    status_color = "#2ECC71" if recommendation["is_applied"] else "#3498DB"
    
    # Card container
    st.markdown(f"""
    <div style="border: 2px solid {border_color}; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div>
                <h3 style="margin: 0;">{recommendation["title"]}</h3>
                <div style="font-size: 0.8em; color: #95A5A6;">Created: {created_date} | Expires: {expires_date}</div>
            </div>
            <div>
                <span style="
                    background-color: {status_color};
                    color: white;
                    padding: 3px 8px;
                    border-radius: 4px;
                    font-size: 0.8em;
                ">{status_text}</span>
            </div>
        </div>
        <p>{recommendation["description"]}</p>
        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
            {render_security_level_badge(recommendation["security_level"])}
            {render_timing_badge(recommendation["timing_recommendation"])}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_recommendation_details(recommendation):
    """Render detailed view of a deployment recommendation."""
    st.markdown(f"## {recommendation['title']}")
    
    # Status badge
    status_text = "Applied" if recommendation["is_applied"] else "Pending"
    st.markdown(f"Status: **{status_text}**")
    
    # Dates
    created_date = recommendation["created_at"].strftime("%B %d, %Y") if recommendation["created_at"] else "N/A"
    expires_date = recommendation["expires_at"].strftime("%B %d, %Y") if recommendation["expires_at"] else "No expiration"
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"Created: **{created_date}**")
    with col2:
        st.markdown(f"Expires: **{expires_date}**")
    
    # Key metrics in cards
    st.subheader("Recommendation Summary")
    
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    
    with metric_col1:
        st.metric(
            label="Security Level",
            value=recommendation["security_level"]
        )
    
    with metric_col2:
        st.metric(
            label="Deployment Timing",
            value=recommendation["timing_recommendation"].replace("_", " ")
        )
    
    with metric_col3:
        if recommendation["estimated_cost"] is not None:
            cost_value = f"${recommendation['estimated_cost']:.2f}"
            saving = recommendation["cost_saving_potential"]
            if saving:
                delta = f"Save ${saving:.2f}"
            else:
                delta = None
        else:
            cost_value = "N/A"
            delta = None
            
        st.metric(
            label="Estimated Cost",
            value=cost_value,
            delta=delta,
            delta_color="normal"
        )
    
    style_metric_cards()
    
    # Description
    st.markdown("### Description")
    st.markdown(recommendation["description"])
    
    # Timing justification
    st.markdown("### Deployment Timing Recommendation")
    st.markdown(recommendation["timing_justification"])
    
    # Platform and region if available
    if recommendation["recommended_platform"] or recommendation["recommended_region"]:
        st.markdown("### Recommended Infrastructure")
        
        if recommendation["recommended_platform"]:
            st.markdown(f"**Platform:** {recommendation['recommended_platform'].replace('_', ' ')}")
        
        if recommendation["recommended_region"]:
            st.markdown(f"**Region:** {recommendation['recommended_region'].replace('_', ' ')}")
    
    # Threat assessment if available
    if recommendation["threat_assessment_summary"]:
        st.markdown("### Threat Assessment")
        
        # Threat counts
        threat_col1, threat_col2, threat_col3 = st.columns(3)
        
        with threat_col1:
            st.metric(
                label="High Risk Threats",
                value=recommendation["high_risk_threats_count"],
                delta=None
            )
        
        with threat_col2:
            st.metric(
                label="Medium Risk Threats",
                value=recommendation["medium_risk_threats_count"],
                delta=None
            )
        
        with threat_col3:
            st.metric(
                label="Low Risk Threats",
                value=recommendation["low_risk_threats_count"],
                delta=None
            )
        
        # Threat summary as preformatted text
        st.text_area(
            "Threat Assessment Summary",
            value=recommendation["threat_assessment_summary"],
            height=200,
            disabled=True
        )
    
    # Cost justification if available
    if recommendation["cost_justification"]:
        st.markdown("### Cost Optimization")
        st.markdown(recommendation["cost_justification"])
    
    # Security configurations
    if recommendation["security_configurations"]:
        st.markdown("### Security Configurations")
        
        for i, config in enumerate(recommendation["security_configurations"]):
            with st.expander(f"{config['category'].replace('_', ' ')}: {config['name']}"):
                st.markdown(f"**Description:** {config['description']}")
                
                if config["is_critical"]:
                    st.markdown("**Priority:** <span style='color: #E74C3C; font-weight: bold;'>CRITICAL</span>", unsafe_allow_html=True)
                else:
                    st.markdown("**Priority:** Standard")
                
                if config["related_threat_types"]:
                    st.markdown(f"**Related Threats:** {', '.join(config['related_threat_types'])}")
                
                # Configuration values as JSON
                st.json(config["configuration_value"])
    
    # Actions
    st.markdown("### Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if not recommendation["is_applied"]:
            if st.button("Apply Recommendation", key=f"apply_{recommendation['id']}"):
                with st.spinner("Applying recommendation..."):
                    success = asyncio.run(mark_recommendation_applied(recommendation["id"]))
                    
                    if success:
                        # Record the deployment
                        deployment_success = asyncio.run(record_deployment(
                            user_id=1,  # Example user ID
                            recommendation_id=recommendation["id"],
                            title=f"Applied: {recommendation['title']}",
                            was_successful=True
                        ))
                        
                        st.success("Recommendation applied successfully!")
                        st.session_state.recommendation_applied = True
                        st.session_state.current_recommendation = None
                        st.rerun()
                    else:
                        st.error("Failed to apply recommendation. Please try again.")
        else:
            st.info("This recommendation has already been applied.")
    
    with col2:
        if st.button("Back to List", key="back_to_list"):
            st.session_state.current_recommendation = None
            st.rerun()


def render_deployment_history():
    """Render deployment history."""
    st.subheader("Deployment History")
    
    # Get deployment history
    deployments = asyncio.run(get_deployment_history(user_id=1, limit=10))
    
    if not deployments:
        st.info("No deployment history available.")
        return
    
    # Create a DataFrame for better display
    df = pd.DataFrame(deployments)
    
    # Format columns for display
    if not df.empty:
        df["deployed_at"] = df["deployed_at"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M") if x else "N/A")
        df["status"] = df["was_successful"].apply(lambda x: "✅ Success" if x else "❌ Failed")
        df["actual_cost"] = df["actual_cost"].apply(lambda x: f"${x:.2f}" if x is not None else "N/A")
        
        # Keep only relevant columns
        display_df = df[["deployed_at", "title", "platform", "region", "security_level", "actual_cost", "status"]]
        
        # Rename columns for better display
        display_df.columns = ["Date", "Deployment", "Platform", "Region", "Security", "Cost", "Status"]
        
        # Display the table
        st.dataframe(display_df, use_container_width=True)


def render_threat_analysis_chart(recommendation=None):
    """Render a chart of threat analysis."""
    if recommendation:
        # Use data from recommendation
        high_count = recommendation["high_risk_threats_count"]
        medium_count = recommendation["medium_risk_threats_count"]
        low_count = recommendation["low_risk_threats_count"]
    else:
        # Example data
        high_count = 5
        medium_count = 12
        low_count = 23
    
    # Create a DataFrame for the chart
    threat_data = pd.DataFrame({
        "Severity": ["High", "Medium", "Low"],
        "Count": [high_count, medium_count, low_count]
    })
    
    # Create a bar chart
    fig = px.bar(
        threat_data,
        x="Severity",
        y="Count",
        color="Severity",
        color_discrete_map={
            "High": "#E74C3C",
            "Medium": "#F1C40F",
            "Low": "#2ECC71"
        },
        text="Count"
    )
    
    fig.update_layout(
        title="Threat Severity Distribution",
        xaxis_title=None,
        yaxis_title="Number of Threats",
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_cost_chart(recommendations=None):
    """Render a cost comparison chart."""
    if recommendations and len(recommendations) > 0:
        # Use data from recommendations
        data = []
        for rec in recommendations:
            if rec["estimated_cost"] is not None:
                data.append({
                    "Date": rec["created_at"].strftime("%b %d") if rec["created_at"] else "N/A",
                    "Base Cost": rec["estimated_cost"] + (rec["cost_saving_potential"] or 0),
                    "Optimized Cost": rec["estimated_cost"],
                    "Savings": rec["cost_saving_potential"] or 0,
                    "id": rec["id"]
                })
    else:
        # Example data
        data = [
            {"Date": "Apr 10", "Base Cost": 130, "Optimized Cost": 100, "Savings": 30, "id": 1},
            {"Date": "Apr 5", "Base Cost": 145, "Optimized Cost": 110, "Savings": 35, "id": 2},
            {"Date": "Mar 28", "Base Cost": 160, "Optimized Cost": 120, "Savings": 40, "id": 3}
        ]
    
    if not data:
        st.info("No cost data available.")
        return
    
    # Create a DataFrame for the chart
    df = pd.DataFrame(data)
    
    # Create a bar chart for cost comparison
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df["Date"],
        y=df["Base Cost"],
        name="Base Cost",
        marker_color="#3498DB"
    ))
    
    fig.add_trace(go.Bar(
        x=df["Date"],
        y=df["Optimized Cost"],
        name="Optimized Cost",
        marker_color="#2ECC71"
    ))
    
    # Add a line for savings
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["Savings"],
        name="Savings",
        mode="lines+markers",
        marker_color="#E74C3C",
        line=dict(width=3)
    ))
    
    fig.update_layout(
        title="Cost Optimization Comparison",
        xaxis_title=None,
        yaxis_title="Cost ($)",
        barmode="group",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_deployment_recommendations():
    """Main function to render the deployment recommendations component."""
    colored_header(
        label="Smart Deployment Recommendations",
        description="Security configuration suggestions, cost optimization, and deployment timing based on threat intelligence",
        color_name="green-70"
    )
    
    # Initialize session state
    if "current_recommendation" not in st.session_state:
        st.session_state.current_recommendation = None
    
    if "recommendation_applied" not in st.session_state:
        st.session_state.recommendation_applied = False
    
    # If recommendation_applied is True, show success message
    if st.session_state.recommendation_applied:
        st.success("Recommendation applied successfully!")
        st.session_state.recommendation_applied = False
    
    # If a recommendation is selected, show the detailed view
    if st.session_state.current_recommendation is not None:
        render_recommendation_details(st.session_state.current_recommendation)
        return
    
    # Overview and metrics row
    st.subheader("Recommendation Overview")
    
    # Get current recommendations
    recommendations = asyncio.run(get_user_recommendations(user_id=1, limit=5))
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        active_count = sum(1 for r in recommendations if r["is_active"] and not r["is_applied"])
        st.metric(
            label="Active Recommendations",
            value=active_count
        )
    
    with metric_col2:
        applied_count = sum(1 for r in recommendations if r["is_applied"])
        st.metric(
            label="Applied Recommendations",
            value=applied_count
        )
    
    with metric_col3:
        # Count recommendations by timing
        safe_count = sum(1 for r in recommendations if r["timing_recommendation"] == DeploymentTimingRecommendation.SAFE_TO_DEPLOY.value)
        st.metric(
            label="Safe to Deploy",
            value=safe_count
        )
    
    with metric_col4:
        # Average cost savings if cost_saving_potential is available
        savings = [r["cost_saving_potential"] for r in recommendations if r["cost_saving_potential"] is not None]
        avg_savings = sum(savings) / len(savings) if savings else 0
        st.metric(
            label="Avg. Cost Savings",
            value=f"${avg_savings:.2f}" if savings else "N/A"
        )
    
    style_metric_cards()
    
    # Two-column layout for charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Show threat analysis chart
        render_threat_analysis_chart(recommendations[0] if recommendations else None)
    
    with chart_col2:
        # Show cost optimization chart
        render_cost_chart(recommendations)
    
    # Active recommendations
    st.subheader("Active Recommendations")
    
    active_recommendations = [r for r in recommendations if r["is_active"] and not r["is_applied"]]
    
    if not active_recommendations:
        st.info("No active recommendations available.")
    else:
        for recommendation in active_recommendations:
            render_recommendation_card(recommendation)
            
            # View details button
            if st.button("View Details", key=f"view_{recommendation['id']}"):
                st.session_state.current_recommendation = recommendation
                st.rerun()
    
    # Generate new recommendations
    st.subheader("Generate New Recommendations")
    
    generate_col1, generate_col2 = st.columns(2)
    
    with generate_col1:
        with st.expander("Threat-Based Recommendation"):
            look_back_days = st.slider(
                "Look Back Period (days)",
                min_value=1,
                max_value=30,
                value=7,
                help="Number of days to analyze threat data for recommendation"
            )
            
            if st.button("Generate Threat-Based Recommendation", key="generate_threat"):
                with st.spinner("Analyzing threat data..."):
                    success = asyncio.run(generate_threat_based_recommendation(user_id=1, look_back_days=look_back_days))
                    
                    if success:
                        st.success("New threat-based recommendation generated!")
                        st.session_state.recommendation_applied = False
                        st.rerun()
                    else:
                        st.warning("No significant threats found for recommendation.")
    
    with generate_col2:
        with st.expander("Cost Optimization Recommendation"):
            if st.button("Generate Cost Optimization Recommendation", key="generate_cost"):
                with st.spinner("Analyzing cost data..."):
                    success = asyncio.run(generate_cost_optimization_recommendation(user_id=1))
                    
                    if success:
                        st.success("New cost optimization recommendation generated!")
                        st.session_state.recommendation_applied = False
                        st.rerun()
                    else:
                        st.warning("No significant cost optimization opportunities found.")
    
    # Show deployment history
    render_deployment_history()