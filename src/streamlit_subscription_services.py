"""
Streamlit integration for subscription services.
"""
import os
import asyncio
import pandas as pd
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

import stripe
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.subscription import (
    SubscriptionPlan, UserSubscription, PaymentHistory,
    SubscriptionTier, BillingPeriod, SubscriptionStatus, PaymentStatus
)
from src.api.services.subscription_service import (
    get_subscription_plans, get_subscription_plan_by_id, get_subscription_plan_by_tier,
    create_subscription_plan, update_subscription_plan,
    get_user_subscription, get_user_subscription_by_id,
    create_user_subscription, cancel_user_subscription
)

from src.streamlit_database import run_async, get_db_session

# Set up Stripe API keys for client-side usage
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")

def get_subscription_plans_df(active_only: bool = True) -> pd.DataFrame:
    """
    Get all subscription plans as a DataFrame.
    
    Args:
        active_only: If True, only return active plans
        
    Returns:
        DataFrame containing subscription plans
    """
    session = get_db_session()
    
    if not session:
        return pd.DataFrame()
    
    plans = run_async(get_subscription_plans(session, active_only))
    
    if not plans:
        return pd.DataFrame()
    
    data = []
    for plan in plans:
        data.append({
            "id": plan.id,
            "name": plan.name,
            "tier": plan.tier.value if plan.tier else None,
            "description": plan.description,
            "price_monthly": plan.price_monthly,
            "price_annually": plan.price_annually,
            "max_alerts": plan.max_alerts,
            "max_reports": plan.max_reports,
            "max_searches_per_day": plan.max_searches_per_day,
            "max_monitoring_keywords": plan.max_monitoring_keywords,
            "max_data_retention_days": plan.max_data_retention_days,
            "supports_api_access": plan.supports_api_access,
            "supports_live_feed": plan.supports_live_feed,
            "supports_dark_web_monitoring": plan.supports_dark_web_monitoring,
            "supports_export": plan.supports_export,
            "supports_advanced_analytics": plan.supports_advanced_analytics,
            "is_active": plan.is_active,
        })
    
    return pd.DataFrame(data)


def get_subscription_plan(plan_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a subscription plan by ID.
    
    Args:
        plan_id: ID of the plan to get
        
    Returns:
        Dictionary containing plan details or None if not found
    """
    session = get_db_session()
    
    if not session:
        return None
    
    plan = run_async(get_subscription_plan_by_id(session, plan_id))
    
    if not plan:
        return None
    
    return {
        "id": plan.id,
        "name": plan.name,
        "tier": plan.tier.value if plan.tier else None,
        "description": plan.description,
        "price_monthly": plan.price_monthly,
        "price_annually": plan.price_annually,
        "max_alerts": plan.max_alerts,
        "max_reports": plan.max_reports,
        "max_searches_per_day": plan.max_searches_per_day,
        "max_monitoring_keywords": plan.max_monitoring_keywords,
        "max_data_retention_days": plan.max_data_retention_days,
        "supports_api_access": plan.supports_api_access,
        "supports_live_feed": plan.supports_live_feed,
        "supports_dark_web_monitoring": plan.supports_dark_web_monitoring,
        "supports_export": plan.supports_export,
        "supports_advanced_analytics": plan.supports_advanced_analytics,
        "is_active": plan.is_active,
        "stripe_product_id": plan.stripe_product_id,
        "stripe_monthly_price_id": plan.stripe_monthly_price_id,
        "stripe_annual_price_id": plan.stripe_annual_price_id,
    }


def get_user_current_subscription(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a user's current subscription.
    
    Args:
        user_id: ID of the user
        
    Returns:
        Dictionary containing subscription details or None if not found
    """
    session = get_db_session()
    
    if not session:
        return None
    
    subscription = run_async(get_user_subscription(session, user_id))
    
    if not subscription:
        return None
    
    plan = subscription.plan
    
    return {
        "id": subscription.id,
        "user_id": subscription.user_id,
        "plan_id": subscription.plan_id,
        "plan_name": plan.name if plan else None,
        "plan_tier": plan.tier.value if plan and plan.tier else None,
        "status": subscription.status.value if subscription.status else None,
        "billing_period": subscription.billing_period.value if subscription.billing_period else None,
        "current_period_start": subscription.current_period_start,
        "current_period_end": subscription.current_period_end,
        "stripe_subscription_id": subscription.stripe_subscription_id,
        "stripe_customer_id": subscription.stripe_customer_id,
        "created_at": subscription.created_at,
        "canceled_at": subscription.canceled_at,
    }


def create_new_subscription_plan(
    name: str,
    tier: str,
    description: str,
    price_monthly: float,
    price_annually: float,
    max_alerts: int = 10,
    max_reports: int = 5,
    max_searches_per_day: int = 20,
    max_monitoring_keywords: int = 10,
    max_data_retention_days: int = 30,
    supports_api_access: bool = False,
    supports_live_feed: bool = False,
    supports_dark_web_monitoring: bool = False,
    supports_export: bool = False,
    supports_advanced_analytics: bool = False,
    create_stripe_product: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Create a new subscription plan.
    
    Args:
        name: Name of the plan
        tier: Tier of the plan (must be one of "free", "basic", "professional", "enterprise")
        description: Description of the plan
        price_monthly: Monthly price of the plan
        price_annually: Annual price of the plan
        max_alerts: Maximum number of alerts allowed
        max_reports: Maximum number of reports allowed
        max_searches_per_day: Maximum number of searches per day
        max_monitoring_keywords: Maximum number of monitoring keywords
        max_data_retention_days: Maximum number of days to retain data
        supports_api_access: Whether the plan supports API access
        supports_live_feed: Whether the plan supports live feed
        supports_dark_web_monitoring: Whether the plan supports dark web monitoring
        supports_export: Whether the plan supports data export
        supports_advanced_analytics: Whether the plan supports advanced analytics
        create_stripe_product: Whether to create a Stripe product for this plan
        
    Returns:
        Dictionary containing plan details or None if creation failed
    """
    session = get_db_session()
    
    if not session:
        return None
    
    try:
        # Convert tier string to enum
        tier_enum = SubscriptionTier(tier.lower())
    except ValueError:
        return None
    
    plan = run_async(create_subscription_plan(
        db=session,
        name=name,
        tier=tier_enum,
        description=description,
        price_monthly=price_monthly,
        price_annually=price_annually,
        max_alerts=max_alerts,
        max_reports=max_reports,
        max_searches_per_day=max_searches_per_day,
        max_monitoring_keywords=max_monitoring_keywords,
        max_data_retention_days=max_data_retention_days,
        supports_api_access=supports_api_access,
        supports_live_feed=supports_live_feed,
        supports_dark_web_monitoring=supports_dark_web_monitoring,
        supports_export=supports_export,
        supports_advanced_analytics=supports_advanced_analytics,
        create_stripe_product=create_stripe_product
    ))
    
    if not plan:
        return None
    
    return {
        "id": plan.id,
        "name": plan.name,
        "tier": plan.tier.value if plan.tier else None,
        "description": plan.description,
        "price_monthly": plan.price_monthly,
        "price_annually": plan.price_annually,
        "max_alerts": plan.max_alerts,
        "max_reports": plan.max_reports,
        "max_searches_per_day": plan.max_searches_per_day,
        "max_monitoring_keywords": plan.max_monitoring_keywords,
        "max_data_retention_days": plan.max_data_retention_days,
        "supports_api_access": plan.supports_api_access,
        "supports_live_feed": plan.supports_live_feed,
        "supports_dark_web_monitoring": plan.supports_dark_web_monitoring,
        "supports_export": plan.supports_export,
        "supports_advanced_analytics": plan.supports_advanced_analytics,
        "is_active": plan.is_active,
        "stripe_product_id": plan.stripe_product_id,
        "stripe_monthly_price_id": plan.stripe_monthly_price_id,
        "stripe_annual_price_id": plan.stripe_annual_price_id,
    }


def subscribe_user_to_plan(
    user_id: int,
    plan_id: int,
    billing_period: str = "monthly",
    create_stripe_subscription: bool = True,
    payment_method_id: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Subscribe a user to a plan.
    
    Args:
        user_id: ID of the user
        plan_id: ID of the plan
        billing_period: Billing period ("monthly" or "annually")
        create_stripe_subscription: Whether to create a Stripe subscription
        payment_method_id: ID of the payment method to use (required if create_stripe_subscription is True)
        
    Returns:
        Dictionary containing subscription details or None if creation failed
    """
    session = get_db_session()
    
    if not session:
        return None
    
    try:
        # Convert billing period string to enum
        billing_period_enum = BillingPeriod(billing_period.lower())
    except ValueError:
        return None
    
    subscription = run_async(create_user_subscription(
        db=session,
        user_id=user_id,
        plan_id=plan_id,
        billing_period=billing_period_enum,
        create_stripe_subscription=create_stripe_subscription,
        payment_method_id=payment_method_id
    ))
    
    if not subscription:
        return None
    
    plan = subscription.plan
    
    return {
        "id": subscription.id,
        "user_id": subscription.user_id,
        "plan_id": subscription.plan_id,
        "plan_name": plan.name if plan else None,
        "plan_tier": plan.tier.value if plan and plan.tier else None,
        "status": subscription.status.value if subscription.status else None,
        "billing_period": subscription.billing_period.value if subscription.billing_period else None,
        "current_period_start": subscription.current_period_start,
        "current_period_end": subscription.current_period_end,
        "stripe_subscription_id": subscription.stripe_subscription_id,
        "stripe_customer_id": subscription.stripe_customer_id,
        "created_at": subscription.created_at,
    }


def cancel_subscription(
    subscription_id: int,
    cancel_stripe_subscription: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Cancel a subscription.
    
    Args:
        subscription_id: ID of the subscription to cancel
        cancel_stripe_subscription: Whether to cancel the Stripe subscription
        
    Returns:
        Dictionary containing subscription details or None if cancellation failed
    """
    session = get_db_session()
    
    if not session:
        return None
    
    subscription = run_async(cancel_user_subscription(
        db=session,
        subscription_id=subscription_id,
        cancel_stripe_subscription=cancel_stripe_subscription
    ))
    
    if not subscription:
        return None
    
    plan = subscription.plan
    
    return {
        "id": subscription.id,
        "user_id": subscription.user_id,
        "plan_id": subscription.plan_id,
        "plan_name": plan.name if plan else None,
        "plan_tier": plan.tier.value if plan and plan.tier else None,
        "status": subscription.status.value if subscription.status else None,
        "billing_period": subscription.billing_period.value if subscription.billing_period else None,
        "current_period_start": subscription.current_period_start,
        "current_period_end": subscription.current_period_end,
        "stripe_subscription_id": subscription.stripe_subscription_id,
        "stripe_customer_id": subscription.stripe_customer_id,
        "created_at": subscription.created_at,
        "canceled_at": subscription.canceled_at,
    }


def initialize_default_plans():
    """Initialize default subscription plans if they don't exist."""
    # Get existing plans
    plans_df = get_subscription_plans_df(active_only=False)
    
    if not plans_df.empty:
        # Plans already exist
        return
    
    # Create default plans
    # Free tier
    create_new_subscription_plan(
        name="Free",
        tier="free",
        description="Basic access to the platform with limited features. Perfect for individuals or small teams starting with OSINT.",
        price_monthly=0.0,
        price_annually=0.0,
        max_alerts=5,
        max_reports=2,
        max_searches_per_day=10,
        max_monitoring_keywords=5,
        max_data_retention_days=7,
        supports_api_access=False,
        supports_live_feed=False,
        supports_dark_web_monitoring=False,
        supports_export=False,
        supports_advanced_analytics=False,
        create_stripe_product=False  # No need to create Stripe product for free tier
    )
    
    # Basic tier
    create_new_subscription_plan(
        name="Basic",
        tier="basic",
        description="Enhanced access with more features. Ideal for small businesses and security teams requiring regular threat intelligence.",
        price_monthly=29.99,
        price_annually=299.99,
        max_alerts=20,
        max_reports=10,
        max_searches_per_day=50,
        max_monitoring_keywords=25,
        max_data_retention_days=30,
        supports_api_access=False,
        supports_live_feed=True,
        supports_dark_web_monitoring=True,
        supports_export=True,
        supports_advanced_analytics=False
    )
    
    # Professional tier
    create_new_subscription_plan(
        name="Professional",
        tier="professional",
        description="Comprehensive access for professional users. Perfect for medium-sized organizations requiring advanced threat intelligence capabilities.",
        price_monthly=99.99,
        price_annually=999.99,
        max_alerts=100,
        max_reports=50,
        max_searches_per_day=200,
        max_monitoring_keywords=100,
        max_data_retention_days=90,
        supports_api_access=True,
        supports_live_feed=True,
        supports_dark_web_monitoring=True,
        supports_export=True,
        supports_advanced_analytics=True
    )
    
    # Enterprise tier
    create_new_subscription_plan(
        name="Enterprise",
        tier="enterprise",
        description="Full access to all features with unlimited usage. Designed for large organizations with sophisticated threat intelligence requirements.",
        price_monthly=249.99,
        price_annually=2499.99,
        max_alerts=0,  # Unlimited
        max_reports=0,  # Unlimited
        max_searches_per_day=0,  # Unlimited
        max_monitoring_keywords=0,  # Unlimited
        max_data_retention_days=365,
        supports_api_access=True,
        supports_live_feed=True,
        supports_dark_web_monitoring=True,
        supports_export=True,
        supports_advanced_analytics=True
    )