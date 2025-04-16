"""Create deployment recommendation tables

Revision ID: create_deployment_tables
Revises: 
Create Date: 2025-04-16 09:22:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'create_deployment_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create deployment_recommendations table
    op.create_table(
        'deployment_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Security related fields
        sa.Column('security_level', sa.String(length=50), nullable=False),
        sa.Column('security_settings', sa.JSON(), nullable=True),
        
        # Timing related fields
        sa.Column('timing_recommendation', sa.String(length=50), nullable=True),
        sa.Column('timing_justification', sa.Text(), nullable=True),
        sa.Column('recommended_window_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('recommended_window_end', sa.DateTime(timezone=True), nullable=True),
        
        # Cost related fields
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('cost_saving_potential', sa.Float(), nullable=True),
        sa.Column('cost_justification', sa.Text(), nullable=True),
        
        # Deployment targets
        sa.Column('recommended_platform', sa.String(length=100), nullable=True),
        sa.Column('recommended_region', sa.String(length=100), nullable=True),
        
        # Threat assessment
        sa.Column('threat_assessment_summary', sa.Text(), nullable=True),
        sa.Column('high_risk_threats_count', sa.Integer(), nullable=True),
        sa.Column('medium_risk_threats_count', sa.Integer(), nullable=True),
        sa.Column('low_risk_threats_count', sa.Integer(), nullable=True),
        
        # Status fields
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('is_applied', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        
        # Primary key
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create deployment_history table
    op.create_table(
        'deployment_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('recommendation_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('was_successful', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('deployed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('platform', sa.String(length=100), nullable=True),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('error_details', sa.Text(), nullable=True),
        
        # Primary key
        sa.PrimaryKeyConstraint('id'),
        
        # Foreign key to recommendation if applicable
        sa.ForeignKeyConstraint(['recommendation_id'], ['deployment_recommendations.id'], ),
    )
    
    # Create indexes
    op.create_index(op.f('ix_deployment_recommendations_user_id'), 'deployment_recommendations', ['user_id'], unique=False)
    op.create_index(op.f('ix_deployment_recommendations_created_at'), 'deployment_recommendations', ['created_at'], unique=False)
    op.create_index(op.f('ix_deployment_history_user_id'), 'deployment_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_deployment_history_deployed_at'), 'deployment_history', ['deployed_at'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_table('deployment_history')
    op.drop_table('deployment_recommendations')