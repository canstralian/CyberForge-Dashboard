"""Create deployment recommendation tables.

Revision ID: 3a20f67c5ade
Revises: create_subscription_tables
Create Date: 2025-04-15 12:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3a20f67c5ade'
down_revision = 'create_subscription_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    security_config_level = sa.Enum('STANDARD', 'ENHANCED', 'STRICT', 'CUSTOM', name='securityconfiglevel')
    deployment_timing_recommendation = sa.Enum('SAFE_TO_DEPLOY', 'CAUTION', 'DELAY_RECOMMENDED', 'HIGH_RISK', name='deploymenttimingrecommendation')
    deployment_platform = sa.Enum('AWS', 'AZURE', 'GCP', 'HEROKU', 'DIGITAL_OCEAN', 'ON_PREMISE', 'HUGGING_FACE', 'OTHER', name='deploymentplatform')
    deployment_region = sa.Enum('US_EAST', 'US_WEST', 'EU_CENTRAL', 'EU_WEST', 'ASIA_PACIFIC', 'SOUTH_AMERICA', 'AFRICA', 'MIDDLE_EAST', 'CUSTOM', name='deploymentregion')
    security_config_category = sa.Enum('NETWORK', 'AUTHENTICATION', 'ENCRYPTION', 'MONITORING', 'COMPLIANCE', 'FIREWALL', 'WEB_APPLICATION_FIREWALL', 'DDOS_PROTECTION', 'IDENTITY_ACCESS_MANAGEMENT', 'SECRETS_MANAGEMENT', name='securityconfigcategory')
    
    # Create enums
    op.create_table('deployment_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('security_level', security_config_level, nullable=False),
        sa.Column('security_settings', sa.Text(), nullable=True),
        sa.Column('timing_recommendation', deployment_timing_recommendation, nullable=False),
        sa.Column('timing_justification', sa.Text(), nullable=True),
        sa.Column('recommended_window_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('recommended_window_end', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('cost_saving_potential', sa.Float(), nullable=True),
        sa.Column('cost_justification', sa.Text(), nullable=True),
        sa.Column('recommended_platform', deployment_platform, nullable=True),
        sa.Column('recommended_region', deployment_region, nullable=True),
        sa.Column('threat_assessment_summary', sa.Text(), nullable=True),
        sa.Column('high_risk_threats_count', sa.Integer(), nullable=True),
        sa.Column('medium_risk_threats_count', sa.Integer(), nullable=True),
        sa.Column('low_risk_threats_count', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_applied', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('deployment_security_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('recommendation_id', sa.Integer(), nullable=False),
        sa.Column('category', security_config_category, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('configuration_value', sa.Text(), nullable=True),
        sa.Column('related_threat_types', sa.String(length=255), nullable=True),
        sa.Column('is_critical', sa.Boolean(), nullable=True),
        sa.Column('is_applied', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['recommendation_id'], ['deployment_recommendations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('deployment_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('recommendation_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('platform', deployment_platform, nullable=True),
        sa.Column('region', deployment_region, nullable=True),
        sa.Column('security_level', security_config_level, nullable=True),
        sa.Column('security_config_summary', sa.Text(), nullable=True),
        sa.Column('was_successful', sa.Boolean(), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('actual_cost', sa.Float(), nullable=True),
        sa.Column('deployed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['recommendation_id'], ['deployment_recommendations.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_deployment_recommendations_id'), 'deployment_recommendations', ['id'], unique=False)
    op.create_index(op.f('ix_deployment_security_configs_id'), 'deployment_security_configs', ['id'], unique=False)
    op.create_index(op.f('ix_deployment_history_id'), 'deployment_history', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_deployment_history_id'), table_name='deployment_history')
    op.drop_index(op.f('ix_deployment_security_configs_id'), table_name='deployment_security_configs')
    op.drop_index(op.f('ix_deployment_recommendations_id'), table_name='deployment_recommendations')
    
    op.drop_table('deployment_history')
    op.drop_table('deployment_security_configs')
    op.drop_table('deployment_recommendations')
    
    # Drop enum types
    sa.Enum(name='securityconfiglevel').drop(op.get_bind())
    sa.Enum(name='deploymenttimingrecommendation').drop(op.get_bind())
    sa.Enum(name='deploymentplatform').drop(op.get_bind())
    sa.Enum(name='deploymentregion').drop(op.get_bind())
    sa.Enum(name='securityconfigcategory').drop(op.get_bind())