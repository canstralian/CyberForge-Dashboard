"""
One-click Security Configuration Wizard

This component provides a streamlined interface for configuring security settings
based on threat profiles and organizational needs.
"""
import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from streamlit_extras.colored_header import colored_header
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.metric_cards import style_metric_cards

from src.streamlit_database import run_async
from components.deployment_recommendations import generate_threat_based_recommendation
from components.deployment_recommendations import record_deployment

# Predefined security configurations
SECURITY_CONFIGURATIONS = {
    "minimal": {
        "name": "Minimal Security",
        "description": "Basic security settings for low-risk environments",
        "firewall": "default",
        "encryption": "standard",
        "authentication": "email_password",
        "monitoring": "basic",
        "threat_level": "low",
        "patching": "manual",
        "backup": "weekly",
        "access_controls": "simple"
    },
    "standard": {
        "name": "Standard Security",
        "description": "Balanced security settings for most organizations",
        "firewall": "enhanced",
        "encryption": "aes_256",
        "authentication": "2fa",
        "monitoring": "24x7",
        "threat_level": "medium",
        "patching": "scheduled",
        "backup": "daily",
        "access_controls": "role_based"
    },
    "enhanced": {
        "name": "Enhanced Security",
        "description": "Strong security settings for sensitive data and high-value targets",
        "firewall": "advanced",
        "encryption": "aes_256_gcm",
        "authentication": "mfa",
        "monitoring": "24x7_extended",
        "threat_level": "high",
        "patching": "auto",
        "backup": "continuous",
        "access_controls": "zero_trust"
    },
    "maximum": {
        "name": "Maximum Security",
        "description": "Highest security settings for financial institutions, healthcare, and government",
        "firewall": "next_gen",
        "encryption": "military_grade",
        "authentication": "biometric_mfa",
        "monitoring": "24x7_ai_enhanced",
        "threat_level": "critical",
        "patching": "immediate",
        "backup": "geo_redundant",
        "access_controls": "zero_trust_verified"
    }
}

# Vulnerability database for risk scoring
VULNERABILITY_TYPES = {
    "sql_injection": {
        "name": "SQL Injection",
        "risk_score": 8.5,
        "description": "Code injection technique that exploits SQL queries",
        "mitigation": "Use parameterized queries, input sanitization, and ORM frameworks"
    },
    "xss": {
        "name": "Cross-Site Scripting (XSS)",
        "risk_score": 7.8,
        "description": "Client-side code injection attacks",
        "mitigation": "Implement Content Security Policy (CSP), escape output, validate input"
    },
    "csrf": {
        "name": "Cross-Site Request Forgery (CSRF)",
        "risk_score": 6.5,
        "description": "Forces users to execute unwanted actions on authenticated web applications",
        "mitigation": "Use anti-CSRF tokens, SameSite cookies, and proper authentication"
    },
    "broken_auth": {
        "name": "Broken Authentication",
        "risk_score": 8.0,
        "description": "Flaws in authentication mechanisms",
        "mitigation": "Implement MFA, session management, password policies, and secure reset flows"
    },
    "sensitive_data_exposure": {
        "name": "Sensitive Data Exposure",
        "risk_score": 7.5,
        "description": "Inadequate protection of sensitive data",
        "mitigation": "Encrypt data at rest and in transit, implement data classification"
    },
    "xxe": {
        "name": "XML External Entities (XXE)",
        "risk_score": 7.0,
        "description": "Attacks against XML parsers processing untrusted XML input",
        "mitigation": "Disable XML external entity processing, use SAST tools"
    },
    "broken_access_control": {
        "name": "Broken Access Control",
        "risk_score": 8.7,
        "description": "Restrictions on authenticated users are not properly enforced",
        "mitigation": "Implement least privilege, strong access controls, and RBAC"
    },
    "security_misconfiguration": {
        "name": "Security Misconfiguration",
        "risk_score": 6.8,
        "description": "Missing security hardening or misconfigured permissions",
        "mitigation": "Implement security baseline, regular patching, and configuration audits"
    },
    "insecure_deserial": {
        "name": "Insecure Deserialization",
        "risk_score": 7.2,
        "description": "Untrusted data is used to manipulate serialized objects",
        "mitigation": "Avoid serialized objects from untrusted sources, implement integrity checks"
    },
    "insufficient_logging": {
        "name": "Insufficient Logging & Monitoring",
        "risk_score": 5.5,
        "description": "Lack of proper logging to detect and respond to breaches",
        "mitigation": "Implement centralized logging, monitoring, and alerting systems"
    }
}

def calculate_risk_score(threat_data, organization_type, data_sensitivity, response_time=24):
    """
    Calculate the risk score based on threat data and organization profile.
    
    Args:
        threat_data (dict): Dictionary of active threats
        organization_type (str): Type of organization
        data_sensitivity (str): Level of data sensitivity
        response_time (int): Response time capability in hours
        
    Returns:
        float: Risk score between 0-100
    """
    # Base score from threats
    threat_score = sum(VULNERABILITY_TYPES[threat]["risk_score"] for threat in threat_data)
    
    # Organization type multiplier
    org_multiplier = {
        "small_business": 0.8,
        "medium_business": 1.0,
        "enterprise": 1.2,
        "government": 1.5,
        "healthcare": 1.6,
        "financial": 1.7,
        "critical_infrastructure": 1.8
    }.get(organization_type, 1.0)
    
    # Data sensitivity multiplier
    data_multiplier = {
        "public": 0.7,
        "internal": 1.0,
        "confidential": 1.3,
        "restricted": 1.6,
        "classified": 2.0
    }.get(data_sensitivity, 1.0)
    
    # Response time factor - faster response = lower risk
    response_factor = max(0.5, min(2.0, response_time / 24))
    
    # Calculate final score
    raw_score = threat_score * org_multiplier * data_multiplier * response_factor
    
    # Normalize to 0-100 scale
    return min(100, max(0, raw_score * 5))

def get_recommended_security_level(risk_score):
    """
    Determine recommended security level based on risk score.
    
    Args:
        risk_score (float): Risk score between 0-100
        
    Returns:
        str: Recommended security level
    """
    if risk_score < 30:
        return "minimal"
    elif risk_score < 60:
        return "standard"
    elif risk_score < 85:
        return "enhanced"
    else:
        return "maximum"

def get_active_threats(user_id=1):
    """
    Get active threats for the user from database.
    For demo, using simulated threats.
    
    Args:
        user_id (int): User ID
        
    Returns:
        dict: Dictionary of active threats with counts
    """
    # Simulate threats for demo
    import random
    threats = {}
    all_threats = list(VULNERABILITY_TYPES.keys())
    
    # Select 3-7 random threats
    num_threats = random.randint(3, 7)
    selected_threats = random.sample(all_threats, num_threats)
    
    for threat in selected_threats:
        # Random count of each threat instance
        threats[threat] = random.randint(1, 5)
    
    return threats

def generate_security_recommendation(
    user_id=1, 
    organization_type="medium_business", 
    data_sensitivity="confidential",
    response_time=24
):
    """
    Generate a security configuration recommendation.
    
    Args:
        user_id (int): User ID
        organization_type (str): Type of organization
        data_sensitivity (str): Level of data sensitivity
        response_time (int): Response time capability in hours
        
    Returns:
        dict: Recommended security configuration
    """
    # Get active threats
    active_threats = get_active_threats(user_id)
    
    # Calculate risk score
    risk_score = calculate_risk_score(
        active_threats, 
        organization_type, 
        data_sensitivity, 
        response_time
    )
    
    # Get recommended security level
    security_level = get_recommended_security_level(risk_score)
    
    # Get configuration from predefined templates
    config = SECURITY_CONFIGURATIONS[security_level].copy()
    
    # Add additional data
    config.update({
        "risk_score": risk_score,
        "active_threats": active_threats,
        "organization_type": organization_type,
        "data_sensitivity": data_sensitivity,
        "response_time": response_time,
        "generated_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
    })
    
    return config

def save_security_configuration(user_id, config, apply_now=False):
    """
    Save security configuration as a deployment recommendation.
    
    Args:
        user_id (int): User ID
        config (dict): Security configuration
        apply_now (bool): Whether to apply the configuration immediately
        
    Returns:
        bool: Success status
    """
    try:
        # Create a deployment recommendation
        security_level = config.get("name", "Standard Security")
        security_settings = json.dumps(config)
        
        # Calculate threat counts
        active_threats = config.get("active_threats", {})
        high_risk_threats = sum(1 for t in active_threats if VULNERABILITY_TYPES[t]["risk_score"] > 7.5)
        medium_risk_threats = sum(1 for t in active_threats if 5 <= VULNERABILITY_TYPES[t]["risk_score"] <= 7.5)
        low_risk_threats = sum(1 for t in active_threats if VULNERABILITY_TYPES[t]["risk_score"] < 5)
        
        # Prepare threat assessment summary
        threat_summary = "Identified vulnerabilities: "
        threat_summary += ", ".join([VULNERABILITY_TYPES[t]["name"] for t in active_threats])
        
        # Create deployment recommendation
        result = run_async(generate_threat_based_recommendation(
            user_id=user_id,
            title=f"Security Configuration: {security_level}",
            description=f"Automated security configuration based on threat analysis",
            security_level=security_level.split()[0].lower(),  # minimal, standard, enhanced, maximum
            security_settings=security_settings,
            threat_assessment_summary=threat_summary,
            high_risk_threats_count=high_risk_threats,
            medium_risk_threats_count=medium_risk_threats,
            low_risk_threats_count=low_risk_threats
        ))
        
        recommendation_id = getattr(result, 'id', None)
        
        # If apply_now is True, record it as an applied deployment
        if apply_now and recommendation_id:
            run_async(record_deployment(
                user_id=user_id,
                recommendation_id=recommendation_id,
                title=f"Applied {security_level}",
                was_successful=True
            ))
        
        return True
    except Exception as e:
        st.error(f"Failed to save security configuration: {str(e)}")
        return False

def render_security_level_comparison():
    """Render a comparison of different security levels."""
    st.markdown("### Security Level Comparison")
    
    # Convert security configurations to DataFrame for display
    configs = []
    for level, config in SECURITY_CONFIGURATIONS.items():
        data = {
            "Level": config["name"],
            "Description": config["description"],
            "Firewall": config["firewall"],
            "Encryption": config["encryption"],
            "Authentication": config["authentication"],
            "Monitoring": config["monitoring"],
            "Threat Level": config["threat_level"],
            "Patching": config["patching"],
            "Backup": config["backup"],
            "Access Controls": config["access_controls"],
        }
        configs.append(data)
    
    df = pd.DataFrame(configs)
    
    # Style the dataframe
    def highlight_cells(val):
        if "maximum" in val.lower() or "next_gen" in val.lower() or "military" in val.lower() or "biometric" in val.lower() or "geo_redundant" in val.lower():
            return "background-color: #9C27B0; color: white"
        elif "enhanced" in val.lower() or "advanced" in val.lower() or "mfa" in val.lower() or "continuous" in val.lower() or "zero_trust" in val.lower():
            return "background-color: #E74C3C; color: white"
        elif "standard" in val.lower() or "aes_256" in val.lower() or "2fa" in val.lower() or "daily" in val.lower() or "role_based" in val.lower():
            return "background-color: #3498DB; color: white"
        elif "minimal" in val.lower() or "basic" in val.lower() or "default" in val.lower() or "weekly" in val.lower() or "simple" in val.lower():
            return "background-color: #2ECC71; color: white"
        return ""
    
    # Apply styling
    styled_df = df.style.applymap(highlight_cells)
    
    # Show the table
    st.dataframe(styled_df, hide_index=True, use_container_width=True)

def render_security_scorecard(config):
    """
    Render a security scorecard for the configuration.
    
    Args:
        config (dict): Security configuration
    """
    st.markdown("### Security Scorecard")
    
    # Create metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_score = config.get("risk_score", 50)
        st.metric("Risk Score", f"{risk_score:.1f}/100")
        
    with col2:
        security_level = config.get("name", "Standard Security").split()[0]
        st.metric("Security Level", security_level)
        
    with col3:
        # Count active threats
        active_threats = len(config.get("active_threats", {}))
        st.metric("Active Threats", active_threats)
    
    style_metric_cards()
    
    # Create radar chart for security dimensions
    categories = ['Firewall', 'Encryption', 'Authentication', 'Monitoring', 
                  'Patching', 'Backup', 'Access Controls']
    
    # Map security settings to numerical values (1-4)
    security_values = {
        "minimal": 1,
        "standard": 2,
        "enhanced": 3,
        "maximum": 4
    }
    
    # Get level from config name
    level = config.get("name", "Standard Security").split()[0].lower()
    if "minimal" in level:
        level_key = "minimal"
    elif "standard" in level:
        level_key = "standard"
    elif "enhanced" in level:
        level_key = "enhanced"
    else:
        level_key = "maximum"
    
    # Map configuration values to numerical scores
    values = []
    
    # Firewall
    firewall_map = {"default": 1, "enhanced": 2, "advanced": 3, "next_gen": 4}
    values.append(firewall_map.get(config.get("firewall", "default"), 1))
    
    # Encryption
    encryption_map = {"standard": 1, "aes_256": 2, "aes_256_gcm": 3, "military_grade": 4}
    values.append(encryption_map.get(config.get("encryption", "standard"), 1))
    
    # Authentication
    auth_map = {"email_password": 1, "2fa": 2, "mfa": 3, "biometric_mfa": 4}
    values.append(auth_map.get(config.get("authentication", "email_password"), 1))
    
    # Monitoring
    monitoring_map = {"basic": 1, "24x7": 2, "24x7_extended": 3, "24x7_ai_enhanced": 4}
    values.append(monitoring_map.get(config.get("monitoring", "basic"), 1))
    
    # Patching
    patching_map = {"manual": 1, "scheduled": 2, "auto": 3, "immediate": 4}
    values.append(patching_map.get(config.get("patching", "manual"), 1))
    
    # Backup
    backup_map = {"weekly": 1, "daily": 2, "continuous": 3, "geo_redundant": 4}
    values.append(backup_map.get(config.get("backup", "weekly"), 1))
    
    # Access Controls
    access_map = {"simple": 1, "role_based": 2, "zero_trust": 3, "zero_trust_verified": 4}
    values.append(access_map.get(config.get("access_controls", "simple"), 1))
    
    # Create radar chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=config.get("name", "Security Configuration"),
        line_color='#E74C3C',
        fillcolor='rgba(231, 76, 60, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 4]
            )
        ),
        showlegend=True,
        title="Security Dimensions",
        height=400,
        margin=dict(l=80, r=80, t=40, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create bar chart for threat breakdown
    active_threats = config.get("active_threats", {})
    if active_threats:
        threat_names = [VULNERABILITY_TYPES[t]["name"] for t in active_threats.keys()]
        threat_scores = [VULNERABILITY_TYPES[t]["risk_score"] for t in active_threats.keys()]
        threat_counts = [active_threats[t] for t in active_threats.keys()]
        
        # Combine scores and counts
        df = pd.DataFrame({
            "Threat": threat_names,
            "Risk Score": threat_scores,
            "Count": threat_counts
        })
        
        # Sort by risk score
        df = df.sort_values("Risk Score", ascending=False)
        
        # Create combined bar and line chart
        fig = go.Figure()
        
        # Add bars for counts
        fig.add_trace(go.Bar(
            x=df["Threat"],
            y=df["Count"],
            name="Threat Count",
            marker_color='#3498DB'
        ))
        
        # Add line for risk scores
        fig.add_trace(go.Scatter(
            x=df["Threat"],
            y=df["Risk Score"],
            name="Risk Score",
            mode='lines+markers',
            yaxis='y2',
            line=dict(color='#E74C3C', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Active Threats Analysis",
            xaxis=dict(title="Threat Type"),
            yaxis=dict(title="Count", side="left", showgrid=False),
            yaxis2=dict(title="Risk Score", side="right", overlaying="y", range=[0, 10], showgrid=False),
            legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0)"),
            height=400,
            margin=dict(l=40, r=40, t=60, b=80),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white")
        )
        
        st.plotly_chart(fig, use_container_width=True)

def render_one_click_wizard():
    """
    Render the one-click security configuration wizard.
    """
    colored_header(
        label="Security Configuration Wizard",
        description="Quickly configure security settings based on your organization's needs",
        color_name="red-70"
    )
    
    # Check if we're in results mode
    if "security_wizard_result" in st.session_state:
        # Show results
        st.success("Security configuration generated successfully!")
        
        config = st.session_state.security_wizard_result
        
        # Display summary card
        st.markdown(f"""
        <div style="padding: 20px; border-radius: 10px; background-color: rgba(52, 152, 219, 0.1); margin-bottom: 20px; border-left: 4px solid #3498DB;">
            <h3 style="margin-top: 0;">{config.get('name', 'Security Configuration')}</h3>
            <p>{config.get('description', '')}</p>
            <p><strong>Risk Score:</strong> {config.get('risk_score', 0):.1f}/100</p>
            <p><strong>Organization:</strong> {config.get('organization_type', '').replace('_', ' ').title()}</p>
            <p><strong>Data Sensitivity:</strong> {config.get('data_sensitivity', '').replace('_', ' ').title()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show security scorecard
        render_security_scorecard(config)
        
        # Action buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button("Apply Configuration", key="apply_config", type="primary"):
                if save_security_configuration(user_id=1, config=config, apply_now=True):
                    st.success("Security configuration applied successfully!")
                    st.balloons()
                    # Clear the wizard result to restart if needed
                    if "security_wizard_result" in st.session_state:
                        del st.session_state.security_wizard_result
                    st.rerun()
        
        with col2:
            if st.button("Save as Recommendation", key="save_config"):
                if save_security_configuration(user_id=1, config=config, apply_now=False):
                    st.success("Security configuration saved as a recommendation!")
                    # Clear the wizard result to restart if needed
                    if "security_wizard_result" in st.session_state:
                        del st.session_state.security_wizard_result
                    st.rerun()
        
        with col3:
            if st.button("Start Over", key="start_over"):
                if "security_wizard_result" in st.session_state:
                    del st.session_state.security_wizard_result
                st.rerun()
        
        # Show detailed security settings
        with st.expander("View Detailed Security Settings", expanded=False):
            # Create a formatted display of all settings
            settings_md = "### Detailed Security Settings\n\n"
            for key, value in config.items():
                if key not in ["active_threats", "description", "organization_type", "data_sensitivity", "response_time"]:
                    if isinstance(value, (int, float)) and key == "risk_score":
                        settings_md += f"**{key.replace('_', ' ').title()}**: {value:.1f}\n\n"
                    elif not isinstance(value, (dict, list)):
                        settings_md += f"**{key.replace('_', ' ').title()}**: {str(value).replace('_', ' ').title()}\n\n"
            
            st.markdown(settings_md)
        
        # Show security level comparison
        with st.expander("View Security Level Comparison", expanded=False):
            render_security_level_comparison()
    
    else:
        # Show wizard form
        st.markdown("### Configure your security profile")
        
        wizard_form = st.form(key="security_wizard_form")
        
        with wizard_form:
            col1, col2 = st.columns(2)
            
            with col1:
                organization_type = st.selectbox(
                    "Organization Type",
                    options=[
                        "small_business", "medium_business", "enterprise",
                        "government", "healthcare", "financial", "critical_infrastructure"
                    ],
                    format_func=lambda x: x.replace("_", " ").title(),
                    help="Select the type of your organization"
                )
            
            with col2:
                data_sensitivity = st.selectbox(
                    "Data Sensitivity",
                    options=["public", "internal", "confidential", "restricted", "classified"],
                    format_func=lambda x: x.replace("_", " ").title(),
                    help="Select the sensitivity level of your data"
                )
            
            response_time = st.slider(
                "Security Response Time (hours)",
                min_value=1,
                max_value=72,
                value=24,
                help="How quickly can your organization respond to security incidents?"
            )
            
            submit_button = st.form_submit_button(label="Generate Security Configuration", type="primary")
        
        # Handle form submission
        if submit_button:
            with st.spinner("Analyzing security needs and generating configuration..."):
                # Generate security recommendation
                config = generate_security_recommendation(
                    user_id=1,
                    organization_type=organization_type,
                    data_sensitivity=data_sensitivity,
                    response_time=response_time
                )
                
                # Store in session state
                st.session_state.security_wizard_result = config
                
                # Rerun to show results
                st.rerun()
        
        # Show description and benefits
        st.markdown("""
        ### Benefits of the Security Configuration Wizard
        
        - **One-Click Security**: Quickly apply recommended security settings
        - **Risk-Based Approach**: Configurations aligned with your threat profile
        - **Continuous Improvement**: Re-run the wizard periodically to adapt to changing threats
        - **Compliance Alignment**: Security settings mapped to common compliance frameworks
        """)
        
        # Show security level comparison
        render_security_level_comparison()

def render_security_wizard():
    """Main function to render the security wizard component."""
    st.title("Security Configuration Wizard")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Configure Security", "View Applied Configurations"])
    
    with tab1:
        render_one_click_wizard()
    
    with tab2:
        st.markdown("### Applied Security Configurations")
        st.info("This section will show the history of applied security configurations.")
        # This would be implemented to show history from the deployment_history table
        # where the configurations were applied