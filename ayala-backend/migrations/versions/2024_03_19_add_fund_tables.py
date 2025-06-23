"""add fund tables

Revision ID: 2024_03_19_add_fund_tables
Revises: 2024_03_19_add_users
Create Date: 2024-03-19 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2024_03_19_add_fund_tables'
down_revision: Union[str, None] = '2024_03_19_add_users'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create fund_profiles table
    op.create_table(
        'fund_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('fund_name', sa.String(255), nullable=False),
        sa.Column('fund_description', sa.Text, nullable=False),
        sa.Column('fund_email', sa.String(255), nullable=False),
        sa.Column('conversation_state', postgresql.JSONB, nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', name='uq_fund_profile_user_id')
    )
    
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('fund_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('target_region', sa.String(100), nullable=False),
        sa.Column('investment_amount', sa.Float, nullable=False),
        sa.Column('status', sa.String(50), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['fund_id'], ['fund_profiles.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('idx_fund_profiles_user_id', 'fund_profiles', ['user_id'])
    op.create_index('idx_projects_fund_id', 'projects', ['fund_id'])
    op.create_index('idx_projects_target_region', 'projects', ['target_region'])
    op.create_index('idx_projects_status', 'projects', ['status'])


def downgrade() -> None:
    op.drop_table('projects')
    op.drop_table('fund_profiles') 