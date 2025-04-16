"""
Script to create subscription tables in the database.
"""
import asyncio
import os
import json
from datetime import datetime, timedelta
import pandas as pd

import asyncpg
from sqlalchemy import text
from src.streamlit_database import get_db_session, get_db_connection


async def create_tables():
    """Create subscription tables in the database."""
    conn = await get_db_connection()
    
    try:
        # Create tables
        await create_subscription_plan_table(conn)
        await create_user_subscription_table(conn)
        await create_payment_history_table(conn)
        
        # Initialize default plans
        await initialize_default_plans(conn)
        
        print("Subscription tables created successfully!")
    except Exception as e:
        print(f"Error creating subscription tables: {str(e)}")
    finally:
        await conn.close()


async def create_subscription_plan_table(conn):
    """Create subscription_plans table."""
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS subscription_plans (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        description TEXT,
        tier VARCHAR(20) NOT NULL,
        price_monthly NUMERIC(10, 2) NOT NULL,
        price_annually NUMERIC(10, 2) NOT NULL,
        max_alerts INTEGER NOT NULL DEFAULT 0,
        max_reports INTEGER NOT NULL DEFAULT 0,
        max_searches_per_day INTEGER NOT NULL DEFAULT 0,
        max_monitoring_keywords INTEGER NOT NULL DEFAULT 0,
        max_data_retention_days INTEGER NOT NULL DEFAULT 30,
        supports_api_access BOOLEAN NOT NULL DEFAULT FALSE,
        supports_live_feed BOOLEAN NOT NULL DEFAULT FALSE,
        supports_dark_web_monitoring BOOLEAN NOT NULL DEFAULT FALSE,
        supports_export BOOLEAN NOT NULL DEFAULT FALSE,
        supports_advanced_analytics BOOLEAN NOT NULL DEFAULT FALSE,
        is_active BOOLEAN NOT NULL DEFAULT TRUE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    )
    """)


async def create_user_subscription_table(conn):
    """Create user_subscriptions table."""
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS user_subscriptions (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        plan_id INTEGER NOT NULL REFERENCES subscription_plans(id),
        billing_period VARCHAR(20) NOT NULL,
        status VARCHAR(20) NOT NULL,
        stripe_subscription_id VARCHAR(100),
        current_period_start TIMESTAMP WITH TIME ZONE,
        current_period_end TIMESTAMP WITH TIME ZONE,
        cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        CONSTRAINT unique_user_active_subscription UNIQUE (user_id, status)
    )
    """)


async def create_payment_history_table(conn):
    """Create payment_history table."""
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS payment_history (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        subscription_id INTEGER REFERENCES user_subscriptions(id),
        amount NUMERIC(10, 2) NOT NULL,
        currency VARCHAR(3) NOT NULL DEFAULT 'USD',
        status VARCHAR(20) NOT NULL,
        stripe_payment_id VARCHAR(100),
        payment_method VARCHAR(20) NOT NULL,
        payment_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    )
    """)


async def initialize_default_plans(conn):
    """Initialize default subscription plans."""
    # Check if plans already exist
    result = await conn.fetch("SELECT COUNT(*) FROM subscription_plans")
    count = result[0][0]
    
    if count > 0:
        print("Plans already exist, skipping initialization")
        return
    
    # Create default plans
    default_plans = [
        {
            "name": "Free",
            "description": "Basic access to dark web monitoring",
            "tier": "free",
            "price_monthly": 0.00,
            "price_annually": 0.00,
            "max_alerts": 5,
            "max_reports": 2,
            "max_searches_per_day": 10,
            "max_monitoring_keywords": 5,
            "max_data_retention_days": 30,
            "supports_api_access": False,
            "supports_live_feed": False,
            "supports_dark_web_monitoring": True,
            "supports_export": False,
            "supports_advanced_analytics": False,
        },
        {
            "name": "Basic",
            "description": "Essential dark web intelligence",
            "tier": "basic",
            "price_monthly": 29.99,
            "price_annually": 299.90,
            "max_alerts": 25,
            "max_reports": 10,
            "max_searches_per_day": 50,
            "max_monitoring_keywords": 25,
            "max_data_retention_days": 90,
            "supports_api_access": False,
            "supports_live_feed": True,
            "supports_dark_web_monitoring": True,
            "supports_export": True,
            "supports_advanced_analytics": False,
        },
        {
            "name": "Professional",
            "description": "Advanced dark web intelligence for professionals",
            "tier": "professional",
            "price_monthly": 99.99,
            "price_annually": 999.90,
            "max_alerts": 100,
            "max_reports": 50,
            "max_searches_per_day": 200,
            "max_monitoring_keywords": 100,
            "max_data_retention_days": 180,
            "supports_api_access": True,
            "supports_live_feed": True,
            "supports_dark_web_monitoring": True,
            "supports_export": True,
            "supports_advanced_analytics": True,
        },
        {
            "name": "Enterprise",
            "description": "Comprehensive dark web intelligence for organizations",
            "tier": "enterprise",
            "price_monthly": 299.99,
            "price_annually": 2999.90,
            "max_alerts": 0,  # Unlimited
            "max_reports": 0,  # Unlimited
            "max_searches_per_day": 0,  # Unlimited
            "max_monitoring_keywords": 0,  # Unlimited
            "max_data_retention_days": 365,
            "supports_api_access": True,
            "supports_live_feed": True,
            "supports_dark_web_monitoring": True,
            "supports_export": True,
            "supports_advanced_analytics": True,
        }
    ]
    
    for plan in default_plans:
        await conn.execute("""
        INSERT INTO subscription_plans (
            name, description, tier, price_monthly, price_annually,
            max_alerts, max_reports, max_searches_per_day, max_monitoring_keywords,
            max_data_retention_days, supports_api_access, supports_live_feed,
            supports_dark_web_monitoring, supports_export, supports_advanced_analytics
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15
        )
        """,
        plan["name"], plan["description"], plan["tier"],
        plan["price_monthly"], plan["price_annually"],
        plan["max_alerts"], plan["max_reports"], plan["max_searches_per_day"],
        plan["max_monitoring_keywords"], plan["max_data_retention_days"],
        plan["supports_api_access"], plan["supports_live_feed"],
        plan["supports_dark_web_monitoring"], plan["supports_export"],
        plan["supports_advanced_analytics"]
        )
    
    print(f"Inserted {len(default_plans)} default subscription plans")


if __name__ == "__main__":
    asyncio.run(create_tables())