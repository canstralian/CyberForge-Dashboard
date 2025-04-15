"""create subscription tables

Revision ID: 0002
Revises: 0001
Create Date: 2025-04-15 10:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from enum import Enum as PyEnum

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


class SubscriptionTier(str, PyEnum):
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class BillingPeriod(str, PyEnum):
    MONTHLY = "monthly"
    ANNUALLY = "annually"
    CUSTOM = "custom"


class SubscriptionStatus(str, PyEnum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    TRIALING = "trialing"
    INCOMPLETE = "incomplete"
    INCOMPLETE_EXPIRED = "incomplete_expired"


class PaymentStatus(str, PyEnum):
    SUCCEEDED = "succeeded"
    PENDING = "pending"
    FAILED = "failed"
    REFUNDED = "refunded"


def upgrade() -> None:
    # Create enum types
    op.create_table(
        'subscription_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('tier', sa.Enum(SubscriptionTier), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('price_monthly', sa.Float(), nullable=False),
        sa.Column('price_annually', sa.Float(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('max_alerts', sa.Integer(), nullable=True, default=10),
        sa.Column('max_reports', sa.Integer(), nullable=True, default=5),
        sa.Column('max_searches_per_day', sa.Integer(), nullable=True, default=20),
        sa.Column('max_monitoring_keywords', sa.Integer(), nullable=True, default=10),
        sa.Column('max_data_retention_days', sa.Integer(), nullable=True, default=30),
        sa.Column('supports_api_access', sa.Boolean(), nullable=True, default=False),
        sa.Column('supports_live_feed', sa.Boolean(), nullable=True, default=False),
        sa.Column('supports_dark_web_monitoring', sa.Boolean(), nullable=True, default=False),
        sa.Column('supports_export', sa.Boolean(), nullable=True, default=False),
        sa.Column('supports_advanced_analytics', sa.Boolean(), nullable=True, default=False),
        sa.Column('stripe_product_id', sa.String(length=100), nullable=True),
        sa.Column('stripe_monthly_price_id', sa.String(length=100), nullable=True),
        sa.Column('stripe_annual_price_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'user_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum(SubscriptionStatus), nullable=False, default='active'),
        sa.Column('billing_period', sa.Enum(BillingPeriod), nullable=False, default='monthly'),
        sa.Column('current_period_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('current_period_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(length=100), nullable=True),
        sa.Column('stripe_customer_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, onupdate=sa.text('now()')),
        sa.Column('canceled_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'payment_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=True, default='USD'),
        sa.Column('status', sa.Enum(PaymentStatus), nullable=False),
        sa.Column('stripe_payment_intent_id', sa.String(length=100), nullable=True),
        sa.Column('stripe_invoice_id', sa.String(length=100), nullable=True),
        sa.Column('payment_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['subscription_id'], ['user_subscriptions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('payment_history')
    op.drop_table('user_subscriptions')
    op.drop_table('subscription_plans')