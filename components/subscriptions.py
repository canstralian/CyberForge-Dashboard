"""
Subscription management component.

This component provides UI for managing subscription plans.
"""
import os
import streamlit as st
import pandas as pd
from datetime import datetime
import json

import stripe
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards

from src.streamlit_subscription_services import (
    get_subscription_plans_df,
    get_subscription_plan,
    get_user_current_subscription,
    subscribe_user_to_plan,
    cancel_subscription,
    initialize_default_plans
)

# Set up Stripe publishable key for client-side usage
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")


def format_price(price):
    """Format price display."""
    if price == 0:
        return "Free"
    return f"${price:.2f}"


def render_pricing_card(plan, selected_period="monthly"):
    """Render a pricing card for a subscription plan."""
    plan_id = plan["id"]
    plan_name = plan["name"]
    plan_tier = plan["tier"]
    description = plan["description"]
    
    # Determine price based on selected period
    if selected_period == "monthly":
        price = plan["price_monthly"]
        period_text = "per month"
        billing_term = "monthly"
    else:
        price = plan["price_annually"]
        period_text = "per year"
        billing_term = "annually"
    
    # Format price for display
    price_display = format_price(price)
    
    # Feature list
    features = [
        f"✓ {plan['max_alerts'] if plan['max_alerts'] > 0 else 'Unlimited'} alerts",
        f"✓ {plan['max_reports'] if plan['max_reports'] > 0 else 'Unlimited'} reports",
        f"✓ {plan['max_searches_per_day'] if plan['max_searches_per_day'] > 0 else 'Unlimited'} searches per day",
        f"✓ {plan['max_monitoring_keywords'] if plan['max_monitoring_keywords'] > 0 else 'Unlimited'} monitoring keywords",
        f"✓ {plan['max_data_retention_days']} days data retention"
    ]
    
    if plan["supports_api_access"]:
        features.append("✓ API access")
    
    if plan["supports_live_feed"]:
        features.append("✓ Live feed")
    
    if plan["supports_dark_web_monitoring"]:
        features.append("✓ Dark web monitoring")
    
    if plan["supports_export"]:
        features.append("✓ Data export")
    
    if plan["supports_advanced_analytics"]:
        features.append("✓ Advanced analytics")
    
    # Card style based on tier
    if plan_tier == "free":
        border_color = "#3498db"  # Blue
        header_color = "#3498db"
    elif plan_tier == "basic":
        border_color = "#2ecc71"  # Green
        header_color = "#2ecc71"
    elif plan_tier == "professional":
        border_color = "#f39c12"  # Orange
        header_color = "#f39c12"
    else:  # Enterprise
        border_color = "#9b59b6"  # Purple
        header_color = "#9b59b6"
    
    # Render card
    st.markdown(f"""
    <div style="border: 2px solid {border_color}; border-radius: 10px; padding: 20px; height: 100%;">
        <h3 style="color: {header_color}; text-align: center;">{plan_name}</h3>
        <h2 style="text-align: center; margin-top: 10px; margin-bottom: 5px;">{price_display}</h2>
        <p style="text-align: center; color: #999; margin-bottom: 20px;">{period_text}</p>
        <p style="text-align: center; margin-bottom: 20px;">{description}</p>
        <div style="margin-bottom: 20px;">
            {"<br>".join([f'<div style="margin-bottom: 8px;">{feature}</div>' for feature in features])}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Subscribe button
    if st.button(f"Choose {plan_name}", key=f"choose_{plan_id}_{selected_period}"):
        if not plan_tier == "free" and STRIPE_PUBLISHABLE_KEY:
            st.session_state.show_payment_form = True
            st.session_state.selected_plan = plan
            st.session_state.selected_billing_period = billing_term
        else:
            # Free plan - no payment needed
            # Assume user ID 1 for demonstration
            user_id = 1
            subscription = subscribe_user_to_plan(
                user_id=user_id,
                plan_id=plan_id,
                billing_period=billing_term,
                create_stripe_subscription=False
            )
            
            if subscription:
                st.success(f"You're now subscribed to the {plan_name} plan!")
                st.session_state.current_user_subscription = subscription
            else:
                st.error("Failed to subscribe. Please try again.")
            
            st.rerun()


def render_payment_form():
    """Render the payment form for subscription."""
    if not STRIPE_PUBLISHABLE_KEY:
        st.error("Stripe API key is not configured. Payment processing is unavailable.")
        return
    
    plan = st.session_state.selected_plan
    billing_period = st.session_state.selected_billing_period
    
    st.markdown("### Payment Information")
    
    # Calculate amount based on billing period
    if billing_period == "monthly":
        amount = plan["price_monthly"]
    else:
        amount = plan["price_annually"]
    
    st.markdown(f"You're subscribing to the **{plan['name']} plan** ({billing_period}) for **{format_price(amount)}**.")
    
    # Name and email inputs
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Full Name")
    
    with col2:
        email = st.text_input("Email Address")
    
    # HTML/JS for Stripe Elements
    st.markdown("""
    <div id="card-element" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px; margin-bottom: 20px;"></div>
    <div id="card-errors" style="color: #e74c3c; margin-bottom: 20px;"></div>
    
    <script src="https://js.stripe.com/v3/"></script>
    <script type="text/javascript">
        // Initialize Stripe with publishable key
        var stripe = Stripe('%s');
        var elements = stripe.elements();
        
        // Create card element
        var card = elements.create('card');
        card.mount('#card-element');
        
        // Handle real-time validation errors
        card.addEventListener('change', function(event) {
            var displayError = document.getElementById('card-errors');
            if (event.error) {
                displayError.textContent = event.error.message;
            } else {
                displayError.textContent = '';
            }
        });
        
        // Set up payment method creation
        window.createPaymentMethod = function() {
            stripe.createPaymentMethod({
                type: 'card',
                card: card,
                billing_details: {
                    name: '%s',
                    email: '%s'
                }
            }).then(function(result) {
                if (result.error) {
                    var errorElement = document.getElementById('card-errors');
                    errorElement.textContent = result.error.message;
                } else {
                    // Send payment method ID to Streamlit
                    window.parent.postMessage({
                        type: 'payment-method-created',
                        paymentMethodId: result.paymentMethod.id
                    }, '*');
                }
            });
        }
    </script>
    """ % (STRIPE_PUBLISHABLE_KEY, name, email), unsafe_allow_html=True)
    
    # Submit button
    if st.button("Subscribe Now", key="subscribe_button"):
        # Call JavaScript function to create payment method
        st.markdown("""
        <script>
            window.createPaymentMethod();
        </script>
        """, unsafe_allow_html=True)
        
        # In a real implementation, we would need to handle the callback from Stripe
        # For now, simulate success for demonstration
        payment_method_id = "pm_" + "".join([str(i) for i in range(24)])  # Fake payment method ID
        
        # Subscribe user with payment method
        # Assume user ID 1 for demonstration
        user_id = 1
        subscription = subscribe_user_to_plan(
            user_id=user_id,
            plan_id=plan["id"],
            billing_period=billing_period,
            create_stripe_subscription=True,
            payment_method_id=payment_method_id
        )
        
        if subscription:
            st.success(f"You're now subscribed to the {plan['name']} plan!")
            st.session_state.show_payment_form = False
            st.session_state.current_user_subscription = subscription
        else:
            st.error("Failed to subscribe. Please try again.")
        
        st.rerun()
    
    # Cancel button
    if st.button("Cancel", key="cancel_payment"):
        st.session_state.show_payment_form = False
        st.rerun()


def render_subscription_dashboard(user_id=1):
    """Render the subscription dashboard for the current user."""
    # Get current subscription
    subscription = get_user_current_subscription(user_id)
    st.session_state.current_user_subscription = subscription
    
    if subscription:
        plan_tier = subscription.get("plan_tier", "").capitalize()
        plan_name = subscription.get("plan_name", "Unknown Plan")
        status = subscription.get("status", "").capitalize()
        billing_period = subscription.get("billing_period", "").capitalize()
        
        period_start = subscription.get("current_period_start")
        period_end = subscription.get("current_period_end")
        
        # Format dates
        start_date = period_start.strftime("%B %d, %Y") if period_start else "N/A"
        end_date = period_end.strftime("%B %d, %Y") if period_end else "N/A"
        
        st.markdown(f"### Current Subscription: {plan_name}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status", status)
        
        with col2:
            st.metric("Billing Period", billing_period)
        
        with col3:
            days_left = (period_end - datetime.now()).days if period_end else 0
            days_left = max(0, days_left)
            st.metric("Days Remaining", days_left)
        
        style_metric_cards()
        
        st.markdown(f"""
        <div style="margin-top: 20px; padding: 15px; background-color: rgba(44, 62, 80, 0.2); border-radius: 6px;">
            <p><strong>Billing Period:</strong> {start_date} to {end_date}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Cancel subscription button
        if status.lower() != "canceled":
            if st.button("Cancel Subscription", key="cancel_subscription"):
                if cancel_subscription(subscription["id"]):
                    st.success("Your subscription has been canceled. You'll still have access until the end of your billing period.")
                    st.rerun()
                else:
                    st.error("Failed to cancel subscription. Please try again.")
    
    # View other plans button
    if st.button("View Available Plans", key="view_plans"):
        st.session_state.show_pricing_table = True
        st.rerun()


def render_subscription_metrics(user_id=1):
    """Render subscription usage metrics for the current user."""
    # Get current subscription
    subscription = st.session_state.get("current_user_subscription") or get_user_current_subscription(user_id)
    
    if not subscription:
        return
    
    # Get subscription plan
    plan = get_subscription_plan(subscription["plan_id"])
    
    if not plan:
        return
    
    st.markdown("### Usage Metrics")
    
    # Create metrics
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    
    with col1:
        max_alerts = plan["max_alerts"]
        alerts_used = 3  # Placeholder value
        alerts_percent = (alerts_used / max_alerts * 100) if max_alerts > 0 else 0
        st.metric("Alerts", f"{alerts_used}/{max_alerts if max_alerts > 0 else '∞'}")
        st.progress(min(alerts_percent, 100) / 100)
    
    with col2:
        max_reports = plan["max_reports"]
        reports_used = 1  # Placeholder value
        reports_percent = (reports_used / max_reports * 100) if max_reports > 0 else 0
        st.metric("Reports", f"{reports_used}/{max_reports if max_reports > 0 else '∞'}")
        st.progress(min(reports_percent, 100) / 100)
    
    with col3:
        max_searches = plan["max_searches_per_day"]
        searches_used = 8  # Placeholder value
        searches_percent = (searches_used / max_searches * 100) if max_searches > 0 else 0
        st.metric("Daily Searches", f"{searches_used}/{max_searches if max_searches > 0 else '∞'}")
        st.progress(min(searches_percent, 100) / 100)
    
    with col4:
        max_keywords = plan["max_monitoring_keywords"]
        keywords_used = 4  # Placeholder value
        keywords_percent = (keywords_used / max_keywords * 100) if max_keywords > 0 else 0
        st.metric("Monitoring Keywords", f"{keywords_used}/{max_keywords if max_keywords > 0 else '∞'}")
        st.progress(min(keywords_percent, 100) / 100)
    
    # List other features
    st.markdown("### Features")
    
    features = []
    
    if plan["supports_api_access"]:
        features.append("✓ API Access")
    else:
        features.append("✗ API Access")
    
    if plan["supports_live_feed"]:
        features.append("✓ Live Feed")
    else:
        features.append("✗ Live Feed")
    
    if plan["supports_dark_web_monitoring"]:
        features.append("✓ Dark Web Monitoring")
    else:
        features.append("✗ Dark Web Monitoring")
    
    if plan["supports_export"]:
        features.append("✓ Data Export")
    else:
        features.append("✗ Data Export")
    
    if plan["supports_advanced_analytics"]:
        features.append("✓ Advanced Analytics")
    else:
        features.append("✗ Advanced Analytics")
    
    # Display features
    cols = st.columns(len(features))
    for i, feature in enumerate(features):
        with cols[i]:
            if feature.startswith("✓"):
                st.markdown(f'<div style="text-align: center; color: #2ecc71; font-weight: bold;">{feature}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="text-align: center; color: #e74c3c; font-weight: bold;">{feature}</div>', unsafe_allow_html=True)


def render_pricing_table():
    """Render a pricing table with all subscription plans."""
    st.markdown("## Subscription Plans")
    
    # Billing period toggle
    selected_period = st.radio(
        "Billing Period",
        ["monthly", "annually"],
        format_func=lambda x: x.capitalize(),
        horizontal=True
    )
    
    # Note about annual savings
    if selected_period == "annually":
        st.info("Save up to 20% with annual billing")
    
    # Get subscription plans
    plans_df = get_subscription_plans_df()
    
    if plans_df.empty:
        st.warning("No subscription plans available.")
        return
    
    # Convert DataFrame to list of dictionaries
    plans = plans_df.to_dict("records")
    
    # Create a column for each plan
    cols = st.columns(len(plans))
    
    # Render pricing cards
    for i, plan in enumerate(plans):
        with cols[i]:
            render_pricing_card(plan, selected_period)
    
    # Close button
    if st.button("Back to Dashboard", key="close_pricing"):
        st.session_state.show_pricing_table = False
        st.rerun()


def render_subscriptions():
    """
    Main function to render the subscription management component.
    """
    colored_header(
        label="Subscription Management",
        description="Manage your subscription and billing",
        color_name="violet-70"
    )
    
    # Initialize default plans if needed
    initialize_default_plans()
    
    # Initialize session state
    if "show_pricing_table" not in st.session_state:
        st.session_state.show_pricing_table = False
    
    if "show_payment_form" not in st.session_state:
        st.session_state.show_payment_form = False
    
    if "selected_plan" not in st.session_state:
        st.session_state.selected_plan = None
    
    if "selected_billing_period" not in st.session_state:
        st.session_state.selected_billing_period = "monthly"
    
    if "current_user_subscription" not in st.session_state:
        st.session_state.current_user_subscription = None
    
    # Check if we need to show payment form
    if st.session_state.show_payment_form:
        render_payment_form()
        return
    
    # Check if we need to show pricing table
    if st.session_state.show_pricing_table:
        render_pricing_table()
        return
    
    # Render current subscription status and dashboard
    render_subscription_dashboard()
    
    # Render subscription metrics
    render_subscription_metrics()