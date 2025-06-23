"""Initial migration

Revision ID: 2024_03_19_initial
Revises: 
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geography
import uuid

# revision identifiers, used by Alembic.
revision = '2024_03_19_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable PostGIS extension
    op.execute('CREATE EXTENSION IF NOT EXISTS postgis')
    
    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('bin', sa.String(12), unique=True),
        sa.Column('registration_date', sa.Date()),
        sa.Column('status', sa.String(50)),
        sa.Column('company_type', sa.String(50)),
        sa.Column('employee_count', sa.Integer()),
        sa.Column('revenue_range', sa.String(50)),
        sa.Column('industry', sa.String(100)),
        
        # Contact Information
        sa.Column('website', sa.String(255)),
        sa.Column('phone', sa.String(50)),
        sa.Column('email', sa.String(255)),
        sa.Column('description', sa.String(1000)),
        
        # Social Media and Contact Verification
        sa.Column('social_media', postgresql.JSONB, server_default='{}'),
        sa.Column('has_social_media', sa.Boolean(), server_default='false'),
        sa.Column('has_website', sa.Boolean(), server_default='false'),
        sa.Column('has_contact_info', sa.Boolean(), server_default='false'),
        
        # Tax Information
        sa.Column('annual_tax_paid', sa.Float()),
        sa.Column('tax_reporting_year', sa.Integer()),
        sa.Column('tax_compliance_score', sa.Float()),
        sa.Column('last_tax_update', sa.Date()),
        
        # Sponsorship Information
        sa.Column('past_donations', sa.Text()),
        sa.Column('sponsorship_interests', sa.Text()),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    
    # Create locations table
    op.create_table(
        'locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('company_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('region', sa.String(100), nullable=False),
        sa.Column('city', sa.String(100)),
        sa.Column('address', sa.String(500)),
        sa.Column('postal_code', sa.String(10)),
        sa.Column('coordinates', Geography(geometry_type='POINT', srid=4326)),
        sa.Column('is_primary', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
    )
    
    # Create indexes
    op.create_index('idx_company_tax_paid', 'companies', ['annual_tax_paid'])
    op.create_index('idx_company_tax_year', 'companies', ['tax_reporting_year'])
    op.create_index('idx_company_has_website', 'companies', ['has_website'])
    op.create_index('idx_company_has_social_media', 'companies', ['has_social_media'])
    op.create_index('idx_company_has_contact_info', 'companies', ['has_contact_info'])
    op.create_index('idx_company_bin', 'companies', ['bin'])
    op.create_index('idx_company_industry', 'companies', ['industry'])
    
    op.create_index('idx_location_region', 'locations', ['region'])
    op.create_index('idx_location_city', 'locations', ['city'])
    op.create_index('idx_location_company', 'locations', ['company_id'])
    # Create GiST index for spatial queries
    op.execute('CREATE INDEX idx_location_coordinates ON locations USING GIST(coordinates)')


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_location_coordinates', table_name='locations')
    op.drop_index('idx_location_company', table_name='locations')
    op.drop_index('idx_location_city', table_name='locations')
    op.drop_index('idx_location_region', table_name='locations')
    
    op.drop_index('idx_company_industry', table_name='companies')
    op.drop_index('idx_company_bin', table_name='companies')
    op.drop_index('idx_company_has_contact_info', table_name='companies')
    op.drop_index('idx_company_has_social_media', table_name='companies')
    op.drop_index('idx_company_has_website', table_name='companies')
    op.drop_index('idx_company_tax_year', table_name='companies')
    op.drop_index('idx_company_tax_paid', table_name='companies')
    
    # Drop tables
    op.drop_table('locations')
    op.drop_table('companies')
    
    # Drop PostGIS extension
    op.execute('DROP EXTENSION IF EXISTS postgis') 