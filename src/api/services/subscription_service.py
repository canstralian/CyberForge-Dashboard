"""
Subscription service.

This module provides functions for managing subscriptions.
"""
import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union

import stripe
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload

from src.models.subscription import (
    SubscriptionPlan, UserSubscription, PaymentHistory,
    SubscriptionTier, BillingPeriod, SubscriptionStatus, PaymentStatus
)
from src.models.user import User

# Set up Stripe API key
stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")

# Set up logging
logger = logging.getLogger(__name__)


async def get_subscription_plans(
    db: AsyncSession,
    active_only: bool = True
) -> List[SubscriptionPlan]:
    """
    Get all subscription plans.
    
    Args:
        db: Database session
        active_only: If True, only return active plans
        
    Returns:
        List of subscription plans
    """
    query = select(SubscriptionPlan)
    
    if active_only:
        query = query.where(SubscriptionPlan.is_active == True)
    
    result = await db.execute(query)
    plans = result.scalars().all()
    
    return plans


async def get_subscription_plan_by_id(
    db: AsyncSession,
    plan_id: int
) -> Optional[SubscriptionPlan]:
    """
    Get a subscription plan by ID.
    
    Args:
        db: Database session
        plan_id: ID of the plan to get
        
    Returns:
        Subscription plan or None if not found
    """
    query = select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id)
    result = await db.execute(query)
    plan = result.scalars().first()
    
    return plan


async def get_subscription_plan_by_tier(
    db: AsyncSession,
    tier: SubscriptionTier
) -> Optional[SubscriptionPlan]:
    """
    Get a subscription plan by tier.
    
    Args:
        db: Database session
        tier: Tier of the plan to get
        
    Returns:
        Subscription plan or None if not found
    """
    query = select(SubscriptionPlan).where(SubscriptionPlan.tier == tier)
    result = await db.execute(query)
    plan = result.scalars().first()
    
    return plan


async def create_subscription_plan(
    db: AsyncSession,
    name: str,
    tier: SubscriptionTier,
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
) -> Optional[SubscriptionPlan]:
    """
    Create a new subscription plan.
    
    Args:
        db: Database session
        name: Name of the plan
        tier: Tier of the plan
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
        Created subscription plan or None if creation failed
    """
    # Check if plan with the same tier already exists
    existing_plan = await get_subscription_plan_by_tier(db, tier)
    
    if existing_plan:
        logger.warning(f"Subscription plan with tier {tier} already exists")
        return None
    
    # Create Stripe product if requested
    stripe_product_id = None
    stripe_monthly_price_id = None
    stripe_annual_price_id = None
    
    if create_stripe_product and stripe.api_key:
        try:
            # Create Stripe product
            product = stripe.Product.create(
                name=name,
                description=description,
                metadata={
                    "tier": tier.value,
                    "max_alerts": max_alerts,
                    "max_reports": max_reports,
                    "max_searches_per_day": max_searches_per_day,
                    "max_monitoring_keywords": max_monitoring_keywords,
                    "max_data_retention_days": max_data_retention_days,
                    "supports_api_access": "yes" if supports_api_access else "no",
                    "supports_live_feed": "yes" if supports_live_feed else "no",
                    "supports_dark_web_monitoring": "yes" if supports_dark_web_monitoring else "no",
                    "supports_export": "yes" if supports_export else "no",
                    "supports_advanced_analytics": "yes" if supports_advanced_analytics else "no"
                }
            )
            
            stripe_product_id = product.id
            
            # Create monthly price
            monthly_price = stripe.Price.create(
                product=product.id,
                unit_amount=int(price_monthly * 100),  # Stripe uses cents
                currency="usd",
                recurring={"interval": "month"},
                metadata={"billing_period": "monthly"}
            )
            
            stripe_monthly_price_id = monthly_price.id
            
            # Create annual price
            annual_price = stripe.Price.create(
                product=product.id,
                unit_amount=int(price_annually * 100),  # Stripe uses cents
                currency="usd",
                recurring={"interval": "year"},
                metadata={"billing_period": "annually"}
            )
            
            stripe_annual_price_id = annual_price.id
            
            logger.info(f"Created Stripe product {product.id} for plan {name}")
        except Exception as e:
            logger.error(f"Failed to create Stripe product for plan {name}: {e}")
    
    # Create plan in database
    plan = SubscriptionPlan(
        name=name,
        tier=tier,
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
        stripe_product_id=stripe_product_id,
        stripe_monthly_price_id=stripe_monthly_price_id,
        stripe_annual_price_id=stripe_annual_price_id
    )
    
    db.add(plan)
    await db.commit()
    await db.refresh(plan)
    
    return plan


async def update_subscription_plan(
    db: AsyncSession,
    plan_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    price_monthly: Optional[float] = None,
    price_annually: Optional[float] = None,
    is_active: Optional[bool] = None,
    max_alerts: Optional[int] = None,
    max_reports: Optional[int] = None,
    max_searches_per_day: Optional[int] = None,
    max_monitoring_keywords: Optional[int] = None,
    max_data_retention_days: Optional[int] = None,
    supports_api_access: Optional[bool] = None,
    supports_live_feed: Optional[bool] = None,
    supports_dark_web_monitoring: Optional[bool] = None,
    supports_export: Optional[bool] = None,
    supports_advanced_analytics: Optional[bool] = None,
    update_stripe_product: bool = True
) -> Optional[SubscriptionPlan]:
    """
    Update a subscription plan.
    
    Args:
        db: Database session
        plan_id: ID of the plan to update
        name: New name of the plan
        description: New description of the plan
        price_monthly: New monthly price of the plan
        price_annually: New annual price of the plan
        is_active: New active status of the plan
        max_alerts: New maximum number of alerts allowed
        max_reports: New maximum number of reports allowed
        max_searches_per_day: New maximum number of searches per day
        max_monitoring_keywords: New maximum number of monitoring keywords
        max_data_retention_days: New maximum number of days to retain data
        supports_api_access: New API access support status
        supports_live_feed: New live feed support status
        supports_dark_web_monitoring: New dark web monitoring support status
        supports_export: New data export support status
        supports_advanced_analytics: New advanced analytics support status
        update_stripe_product: Whether to update the Stripe product for this plan
        
    Returns:
        Updated subscription plan or None if update failed
    """
    # Get existing plan
    plan = await get_subscription_plan_by_id(db, plan_id)
    
    if not plan:
        logger.warning(f"Subscription plan with ID {plan_id} not found")
        return None
    
    # Prepare update data
    update_data = {}
    
    if name is not None:
        update_data["name"] = name
    
    if description is not None:
        update_data["description"] = description
    
    if price_monthly is not None:
        update_data["price_monthly"] = price_monthly
    
    if price_annually is not None:
        update_data["price_annually"] = price_annually
    
    if is_active is not None:
        update_data["is_active"] = is_active
    
    if max_alerts is not None:
        update_data["max_alerts"] = max_alerts
    
    if max_reports is not None:
        update_data["max_reports"] = max_reports
    
    if max_searches_per_day is not None:
        update_data["max_searches_per_day"] = max_searches_per_day
    
    if max_monitoring_keywords is not None:
        update_data["max_monitoring_keywords"] = max_monitoring_keywords
    
    if max_data_retention_days is not None:
        update_data["max_data_retention_days"] = max_data_retention_days
    
    if supports_api_access is not None:
        update_data["supports_api_access"] = supports_api_access
    
    if supports_live_feed is not None:
        update_data["supports_live_feed"] = supports_live_feed
    
    if supports_dark_web_monitoring is not None:
        update_data["supports_dark_web_monitoring"] = supports_dark_web_monitoring
    
    if supports_export is not None:
        update_data["supports_export"] = supports_export
    
    if supports_advanced_analytics is not None:
        update_data["supports_advanced_analytics"] = supports_advanced_analytics
    
    # Update Stripe product if requested
    if update_stripe_product and plan.stripe_product_id and stripe.api_key:
        try:
            # Update Stripe product
            product_update_data = {}
            
            if name is not None:
                product_update_data["name"] = name
            
            if description is not None:
                product_update_data["description"] = description
            
            metadata_update = {}
            
            if max_alerts is not None:
                metadata_update["max_alerts"] = max_alerts
            
            if max_reports is not None:
                metadata_update["max_reports"] = max_reports
            
            if max_searches_per_day is not None:
                metadata_update["max_searches_per_day"] = max_searches_per_day
            
            if max_monitoring_keywords is not None:
                metadata_update["max_monitoring_keywords"] = max_monitoring_keywords
            
            if max_data_retention_days is not None:
                metadata_update["max_data_retention_days"] = max_data_retention_days
            
            if supports_api_access is not None:
                metadata_update["supports_api_access"] = "yes" if supports_api_access else "no"
            
            if supports_live_feed is not None:
                metadata_update["supports_live_feed"] = "yes" if supports_live_feed else "no"
            
            if supports_dark_web_monitoring is not None:
                metadata_update["supports_dark_web_monitoring"] = "yes" if supports_dark_web_monitoring else "no"
            
            if supports_export is not None:
                metadata_update["supports_export"] = "yes" if supports_export else "no"
            
            if supports_advanced_analytics is not None:
                metadata_update["supports_advanced_analytics"] = "yes" if supports_advanced_analytics else "no"
            
            if metadata_update:
                product_update_data["metadata"] = metadata_update
            
            if product_update_data:
                stripe.Product.modify(plan.stripe_product_id, **product_update_data)
            
            # Update prices if needed
            if price_monthly is not None and plan.stripe_monthly_price_id:
                # Can't update existing price in Stripe, create a new one
                new_monthly_price = stripe.Price.create(
                    product=plan.stripe_product_id,
                    unit_amount=int(price_monthly * 100),  # Stripe uses cents
                    currency="usd",
                    recurring={"interval": "month"},
                    metadata={"billing_period": "monthly"}
                )
                
                update_data["stripe_monthly_price_id"] = new_monthly_price.id
            
            if price_annually is not None and plan.stripe_annual_price_id:
                # Can't update existing price in Stripe, create a new one
                new_annual_price = stripe.Price.create(
                    product=plan.stripe_product_id,
                    unit_amount=int(price_annually * 100),  # Stripe uses cents
                    currency="usd",
                    recurring={"interval": "year"},
                    metadata={"billing_period": "annually"}
                )
                
                update_data["stripe_annual_price_id"] = new_annual_price.id
            
            logger.info(f"Updated Stripe product {plan.stripe_product_id} for plan {plan.name}")
        except Exception as e:
            logger.error(f"Failed to update Stripe product for plan {plan.name}: {e}")
    
    # Update plan in database
    if update_data:
        await db.execute(
            update(SubscriptionPlan)
            .where(SubscriptionPlan.id == plan_id)
            .values(**update_data)
        )
        
        await db.commit()
        
        # Refresh plan
        plan = await get_subscription_plan_by_id(db, plan_id)
    
    return plan


async def get_user_subscription(
    db: AsyncSession,
    user_id: int
) -> Optional[UserSubscription]:
    """
    Get a user's active subscription.
    
    Args:
        db: Database session
        user_id: ID of the user
        
    Returns:
        User subscription or None if not found
    """
    query = (
        select(UserSubscription)
        .where(UserSubscription.user_id == user_id)
        .where(UserSubscription.status != SubscriptionStatus.CANCELED)
        .options(joinedload(UserSubscription.plan))
    )
    
    result = await db.execute(query)
    subscription = result.scalars().first()
    
    return subscription


async def get_user_subscription_by_id(
    db: AsyncSession,
    subscription_id: int
) -> Optional[UserSubscription]:
    """
    Get a user subscription by ID.
    
    Args:
        db: Database session
        subscription_id: ID of the subscription
        
    Returns:
        User subscription or None if not found
    """
    query = (
        select(UserSubscription)
        .where(UserSubscription.id == subscription_id)
        .options(joinedload(UserSubscription.plan))
    )
    
    result = await db.execute(query)
    subscription = result.scalars().first()
    
    return subscription


async def create_user_subscription(
    db: AsyncSession,
    user_id: int,
    plan_id: int,
    billing_period: BillingPeriod = BillingPeriod.MONTHLY,
    create_stripe_subscription: bool = True,
    payment_method_id: Optional[str] = None
) -> Optional[UserSubscription]:
    """
    Create a new user subscription.
    
    Args:
        db: Database session
        user_id: ID of the user
        plan_id: ID of the subscription plan
        billing_period: Billing period (monthly or annually)
        create_stripe_subscription: Whether to create a Stripe subscription
        payment_method_id: ID of the payment method to use (required if create_stripe_subscription is True)
        
    Returns:
        Created user subscription or None if creation failed
    """
    # Check if user exists
    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    
    if not user:
        logger.warning(f"User with ID {user_id} not found")
        return None
    
    # Check if plan exists
    plan = await get_subscription_plan_by_id(db, plan_id)
    
    if not plan:
        logger.warning(f"Subscription plan with ID {plan_id} not found")
        return None
    
    # Check if user already has an active subscription
    existing_subscription = await get_user_subscription(db, user_id)
    
    if existing_subscription:
        logger.warning(f"User with ID {user_id} already has an active subscription")
        return None
    
    # Calculate subscription period
    now = datetime.utcnow()
    
    if billing_period == BillingPeriod.MONTHLY:
        current_period_end = now + timedelta(days=30)
        price = plan.price_monthly
        stripe_price_id = plan.stripe_monthly_price_id
    elif billing_period == BillingPeriod.ANNUALLY:
        current_period_end = now + timedelta(days=365)
        price = plan.price_annually
        stripe_price_id = plan.stripe_annual_price_id
    else:
        logger.warning(f"Invalid billing period: {billing_period}")
        return None
    
    # Create Stripe subscription if requested
    stripe_subscription_id = None
    stripe_customer_id = None
    
    if create_stripe_subscription and stripe.api_key and plan.stripe_product_id:
        if not payment_method_id:
            logger.warning("Payment method ID is required to create a Stripe subscription")
            return None
        
        try:
            # Create or retrieve Stripe customer
            customers = stripe.Customer.list(email=user.email)
            
            if customers.data:
                customer = customers.data[0]
                stripe_customer_id = customer.id
            else:
                customer = stripe.Customer.create(
                    email=user.email,
                    name=user.full_name,
                    metadata={"user_id": user_id}
                )
                
                stripe_customer_id = customer.id
            
            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=stripe_customer_id
            )
            
            # Set as default payment method
            stripe.Customer.modify(
                stripe_customer_id,
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=stripe_customer_id,
                items=[
                    {"price": stripe_price_id}
                ],
                expand=["latest_invoice.payment_intent"]
            )
            
            stripe_subscription_id = subscription.id
            
            logger.info(f"Created Stripe subscription {subscription.id} for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to create Stripe subscription for user {user_id}: {e}")
            return None
    
    # Create subscription in database
    subscription = UserSubscription(
        user_id=user_id,
        plan_id=plan_id,
        status=SubscriptionStatus.ACTIVE,
        billing_period=billing_period,
        current_period_start=now,
        current_period_end=current_period_end,
        stripe_subscription_id=stripe_subscription_id,
        stripe_customer_id=stripe_customer_id
    )
    
    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)
    
    # Record payment
    if subscription.id:
        payment_status = PaymentStatus.SUCCEEDED if stripe_subscription_id else PaymentStatus.PENDING
        
        payment = PaymentHistory(
            user_id=user_id,
            subscription_id=subscription.id,
            amount=price,
            currency="USD",
            status=payment_status
        )
        
        db.add(payment)
        await db.commit()
    
    return subscription


async def cancel_user_subscription(
    db: AsyncSession,
    subscription_id: int,
    cancel_stripe_subscription: bool = True
) -> Optional[UserSubscription]:
    """
    Cancel a user subscription.
    
    Args:
        db: Database session
        subscription_id: ID of the subscription to cancel
        cancel_stripe_subscription: Whether to cancel the Stripe subscription
        
    Returns:
        Canceled user subscription or None if cancellation failed
    """
    # Get subscription
    subscription = await get_user_subscription_by_id(db, subscription_id)
    
    if not subscription:
        logger.warning(f"Subscription with ID {subscription_id} not found")
        return None
    
    # Cancel Stripe subscription if requested
    if cancel_stripe_subscription and subscription.stripe_subscription_id and stripe.api_key:
        try:
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
            
            logger.info(f"Canceled Stripe subscription {subscription.stripe_subscription_id} at period end")
        except Exception as e:
            logger.error(f"Failed to cancel Stripe subscription {subscription.stripe_subscription_id}: {e}")
    
    # Update subscription in database
    now = datetime.utcnow()
    
    await db.execute(
        update(UserSubscription)
        .where(UserSubscription.id == subscription_id)
        .values(
            status=SubscriptionStatus.CANCELED,
            canceled_at=now
        )
    )
    
    await db.commit()
    
    # Refresh subscription
    subscription = await get_user_subscription_by_id(db, subscription_id)
    
    return subscription