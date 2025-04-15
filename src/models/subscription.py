"""
Subscription models for the application.

This module defines database models for subscription management.
"""
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.database import Base


class SubscriptionTier(str, Enum):
    """Subscription tier enum."""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class BillingPeriod(str, Enum):
    """Billing period enum."""
    MONTHLY = "monthly"
    ANNUALLY = "annually"
    CUSTOM = "custom"


class SubscriptionPlan(Base):
    """Subscription plan model."""
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    tier = Column(SQLAlchemyEnum(SubscriptionTier), nullable=False)
    description = Column(String(500))
    price_monthly = Column(Float, nullable=False)
    price_annually = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Features
    max_alerts = Column(Integer, default=10)
    max_reports = Column(Integer, default=5)
    max_searches_per_day = Column(Integer, default=20)
    max_monitoring_keywords = Column(Integer, default=10)
    max_data_retention_days = Column(Integer, default=30)
    supports_api_access = Column(Boolean, default=False)
    supports_live_feed = Column(Boolean, default=False)
    supports_dark_web_monitoring = Column(Boolean, default=False)
    supports_export = Column(Boolean, default=False)
    supports_advanced_analytics = Column(Boolean, default=False)
    
    # Stripe product ID (for integration with Stripe)
    stripe_product_id = Column(String(100))
    stripe_monthly_price_id = Column(String(100))
    stripe_annual_price_id = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="plan")
    
    def __repr__(self):
        return f"<SubscriptionPlan(id={self.id}, name={self.name}, tier={self.tier})>"


class SubscriptionStatus(str, Enum):
    """Subscription status enum."""
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"


class UserSubscription(Base):
    """User subscription model."""
    __tablename__ = "user_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    status = Column(SQLAlchemyEnum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE)
    
    # Billing details
    billing_period = Column(SQLAlchemyEnum(BillingPeriod), nullable=False, default=BillingPeriod.MONTHLY)
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    
    # Stripe subscription ID
    stripe_subscription_id = Column(String(100))
    stripe_customer_id = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    canceled_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan", back_populates="subscriptions")
    payment_history = relationship("PaymentHistory", back_populates="subscription")
    
    def __repr__(self):
        return f"<UserSubscription(id={self.id}, user_id={self.user_id}, plan_id={self.plan_id})>"


class PaymentStatus(str, Enum):
    """Payment status enum."""
    SUCCEEDED = "succeeded"
    PENDING = "pending"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentHistory(Base):
    """Payment history model."""
    __tablename__ = "payment_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"), nullable=False)
    
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    status = Column(SQLAlchemyEnum(PaymentStatus), nullable=False)
    
    # Stripe payment intent ID
    stripe_payment_intent_id = Column(String(100))
    stripe_invoice_id = Column(String(100))
    
    # Timestamps
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    subscription = relationship("UserSubscription", back_populates="payment_history")
    
    def __repr__(self):
        return f"<PaymentHistory(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status})>"