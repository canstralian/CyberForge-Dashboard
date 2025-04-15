"""
Script to create subscription tables in the database.
"""
import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import text
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum, func
from sqlalchemy.schema import CreateTable

from src.models.subscription import SubscriptionTier, BillingPeriod, SubscriptionStatus, PaymentStatus
from src.models.subscription import SubscriptionPlan, UserSubscription, PaymentHistory

# Get database URL from environment
db_url = os.getenv("DATABASE_URL", "")
if db_url.startswith("postgresql://"):
    # Remove sslmode parameter if present which causes issues with asyncpg
    if "?" in db_url:
        base_url, params = db_url.split("?", 1)
        param_list = params.split("&")
        filtered_params = [p for p in param_list if not p.startswith("sslmode=")]
        if filtered_params:
            db_url = f"{base_url}?{'&'.join(filtered_params)}"
        else:
            db_url = base_url
    
    ASYNC_DATABASE_URL = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    ASYNC_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,
    future=True
)

async def create_tables():
    """Create subscription tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(create_subscription_plan_table)
        await conn.run_sync(create_user_subscription_table)
        await conn.run_sync(create_payment_history_table)
        
        # Initialize default plans
        await initialize_default_plans(conn)
        
    print("Subscription tables created successfully.")

def create_subscription_plan_table(conn):
    """Create subscription_plans table."""
    metadata = MetaData()
    
    # Create table
    subscription_plans = Table(
        'subscription_plans',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(100), nullable=False),
        Column('tier', Enum(SubscriptionTier), nullable=False),
        Column('description', String(500)),
        Column('price_monthly', Float, nullable=False),
        Column('price_annually', Float, nullable=False),
        Column('is_active', Boolean, default=True),
        
        # Features
        Column('max_alerts', Integer, default=10),
        Column('max_reports', Integer, default=5),
        Column('max_searches_per_day', Integer, default=20),
        Column('max_monitoring_keywords', Integer, default=10),
        Column('max_data_retention_days', Integer, default=30),
        Column('supports_api_access', Boolean, default=False),
        Column('supports_live_feed', Boolean, default=False),
        Column('supports_dark_web_monitoring', Boolean, default=False),
        Column('supports_export', Boolean, default=False),
        Column('supports_advanced_analytics', Boolean, default=False),
        
        # Stripe integration
        Column('stripe_product_id', String(100)),
        Column('stripe_monthly_price_id', String(100)),
        Column('stripe_annual_price_id', String(100)),
        
        # Timestamps
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    # Create table
    metadata.create_all(conn, tables=[subscription_plans])

def create_user_subscription_table(conn):
    """Create user_subscriptions table."""
    metadata = MetaData()
    
    # Create table
    user_subscriptions = Table(
        'user_subscriptions',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('plan_id', Integer, ForeignKey('subscription_plans.id'), nullable=False),
        Column('status', Enum(SubscriptionStatus), nullable=False, default=SubscriptionStatus.ACTIVE),
        
        # Billing details
        Column('billing_period', Enum(BillingPeriod), nullable=False, default=BillingPeriod.MONTHLY),
        Column('current_period_start', DateTime(timezone=True)),
        Column('current_period_end', DateTime(timezone=True)),
        
        # Stripe subscription ID
        Column('stripe_subscription_id', String(100)),
        Column('stripe_customer_id', String(100)),
        
        # Timestamps
        Column('created_at', DateTime(timezone=True), server_default=func.now()),
        Column('updated_at', DateTime(timezone=True), onupdate=func.now()),
        Column('canceled_at', DateTime(timezone=True))
    )
    
    # Create table
    metadata.create_all(conn, tables=[user_subscriptions])

def create_payment_history_table(conn):
    """Create payment_history table."""
    metadata = MetaData()
    
    # Create table
    payment_history = Table(
        'payment_history',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
        Column('subscription_id', Integer, ForeignKey('user_subscriptions.id'), nullable=False),
        
        Column('amount', Float, nullable=False),
        Column('currency', String(3), default="USD"),
        Column('status', Enum(PaymentStatus), nullable=False),
        
        # Stripe payment intent ID
        Column('stripe_payment_intent_id', String(100)),
        Column('stripe_invoice_id', String(100)),
        
        # Timestamps
        Column('payment_date', DateTime(timezone=True), server_default=func.now())
    )
    
    # Create table
    metadata.create_all(conn, tables=[payment_history])

async def initialize_default_plans(conn):
    """Initialize default subscription plans."""
    # Check if plans already exist
    result = await conn.execute(text("SELECT COUNT(*) FROM subscription_plans"))
    count = result.scalar()
    
    if count > 0:
        print("Subscription plans already exist. Skipping initialization.")
        return
    
    # Create default plans
    plans = [
        {
            "name": "Free",
            "tier": SubscriptionTier.FREE,
            "description": "Basic access to the platform with limited features. Perfect for individuals or small teams starting with OSINT.",
            "price_monthly": 0.0,
            "price_annually": 0.0,
            "max_alerts": 5,
            "max_reports": 2,
            "max_searches_per_day": 10,
            "max_monitoring_keywords": 5,
            "max_data_retention_days": 7,
            "supports_api_access": False,
            "supports_live_feed": False,
            "supports_dark_web_monitoring": False,
            "supports_export": False,
            "supports_advanced_analytics": False
        },
        {
            "name": "Basic",
            "tier": SubscriptionTier.BASIC,
            "description": "Enhanced access with more features. Ideal for small businesses and security teams requiring regular threat intelligence.",
            "price_monthly": 29.99,
            "price_annually": 299.99,
            "max_alerts": 20,
            "max_reports": 10,
            "max_searches_per_day": 50,
            "max_monitoring_keywords": 25,
            "max_data_retention_days": 30,
            "supports_api_access": False,
            "supports_live_feed": True,
            "supports_dark_web_monitoring": True,
            "supports_export": True,
            "supports_advanced_analytics": False
        },
        {
            "name": "Professional",
            "tier": SubscriptionTier.PROFESSIONAL,
            "description": "Comprehensive access for professional users. Perfect for medium-sized organizations requiring advanced threat intelligence capabilities.",
            "price_monthly": 99.99,
            "price_annually": 999.99,
            "max_alerts": 100,
            "max_reports": 50,
            "max_searches_per_day": 200,
            "max_monitoring_keywords": 100,
            "max_data_retention_days": 90,
            "supports_api_access": True,
            "supports_live_feed": True,
            "supports_dark_web_monitoring": True,
            "supports_export": True,
            "supports_advanced_analytics": True
        },
        {
            "name": "Enterprise",
            "tier": SubscriptionTier.ENTERPRISE,
            "description": "Full access to all features with unlimited usage. Designed for large organizations with sophisticated threat intelligence requirements.",
            "price_monthly": 249.99,
            "price_annually": 2499.99,
            "max_alerts": 0,  # Unlimited
            "max_reports": 0,  # Unlimited
            "max_searches_per_day": 0,  # Unlimited
            "max_monitoring_keywords": 0,  # Unlimited
            "max_data_retention_days": 365,
            "supports_api_access": True,
            "supports_live_feed": True,
            "supports_dark_web_monitoring": True,
            "supports_export": True,
            "supports_advanced_analytics": True
        }
    ]
    
    # Insert plans
    for plan in plans:
        await conn.execute(
            text("""
            INSERT INTO subscription_plans (
                name, tier, description, price_monthly, price_annually,
                max_alerts, max_reports, max_searches_per_day, max_monitoring_keywords, max_data_retention_days,
                supports_api_access, supports_live_feed, supports_dark_web_monitoring, supports_export, supports_advanced_analytics
            ) VALUES (
                :name, :tier, :description, :price_monthly, :price_annually,
                :max_alerts, :max_reports, :max_searches_per_day, :max_monitoring_keywords, :max_data_retention_days,
                :supports_api_access, :supports_live_feed, :supports_dark_web_monitoring, :supports_export, :supports_advanced_analytics
            )
            """),
            {
                "name": plan["name"],
                "tier": plan["tier"].value,
                "description": plan["description"],
                "price_monthly": plan["price_monthly"],
                "price_annually": plan["price_annually"],
                "max_alerts": plan["max_alerts"],
                "max_reports": plan["max_reports"],
                "max_searches_per_day": plan["max_searches_per_day"],
                "max_monitoring_keywords": plan["max_monitoring_keywords"],
                "max_data_retention_days": plan["max_data_retention_days"],
                "supports_api_access": plan["supports_api_access"],
                "supports_live_feed": plan["supports_live_feed"],
                "supports_dark_web_monitoring": plan["supports_dark_web_monitoring"],
                "supports_export": plan["supports_export"],
                "supports_advanced_analytics": plan["supports_advanced_analytics"]
            }
        )
    
    print("Default subscription plans created.")

if __name__ == "__main__":
    asyncio.run(create_tables())