"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create components table
    op.create_table(
        'components',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('component_type', sa.Enum('CPU', 'GPU', 'MOTHERBOARD', 'RAM', 'STORAGE', 'PSU', 'CASE', 'COOLING', name='componenttype'), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('manufacturer', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=200), nullable=True),
        sa.Column('price_dzd', sa.Float(), nullable=False),
        sa.Column('original_price', sa.String(length=100), nullable=True),
        sa.Column('condition', sa.Enum('NEW', 'USED', 'REFURBISHED', name='condition'), nullable=True),
        sa.Column('in_stock', sa.Boolean(), nullable=True),
        sa.Column('stock_quantity', sa.Integer(), nullable=True),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('source_platform', sa.String(length=100), nullable=True),
        sa.Column('seller_name', sa.String(length=200), nullable=True),
        sa.Column('seller_location', sa.String(length=200), nullable=True),
        sa.Column('specs', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('benchmark_score', sa.Float(), nullable=True),
        sa.Column('gaming_score', sa.Float(), nullable=True),
        sa.Column('productivity_score', sa.Float(), nullable=True),
        sa.Column('ai_score', sa.Float(), nullable=True),
        sa.Column('socket_type', sa.String(length=50), nullable=True),
        sa.Column('chipset', sa.String(length=50), nullable=True),
        sa.Column('ram_type', sa.String(length=20), nullable=True),
        sa.Column('ram_speed', sa.Integer(), nullable=True),
        sa.Column('tdp_watts', sa.Integer(), nullable=True),
        sa.Column('pcie_slots', sa.String(length=100), nullable=True),
        sa.Column('form_factor', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_scraped_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_components_component_type'), 'components', ['component_type'], unique=False)
    op.create_index(op.f('ix_components_name'), 'components', ['name'], unique=False)
    op.create_index(op.f('ix_components_manufacturer'), 'components', ['manufacturer'], unique=False)
    op.create_index(op.f('ix_components_price_dzd'), 'components', ['price_dzd'], unique=False)
    op.create_index(op.f('ix_components_condition'), 'components', ['condition'], unique=False)
    op.create_index(op.f('ix_components_in_stock'), 'components', ['in_stock'], unique=False)
    op.create_index(op.f('ix_components_source_platform'), 'components', ['source_platform'], unique=False)

    # Create component_translations table
    op.create_table(
        'component_translations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('component_id', sa.Integer(), nullable=False),
        sa.Column('locale', sa.String(length=5), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('features', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['component_id'], ['components.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_component_translations_locale'), 'component_translations', ['locale'], unique=False)

    # Create compatibility_rules table
    op.create_table(
        'compatibility_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('component_type_1', sa.Enum('CPU', 'GPU', 'MOTHERBOARD', 'RAM', 'STORAGE', 'PSU', 'CASE', 'COOLING', name='componenttype'), nullable=False),
        sa.Column('component_type_2', sa.Enum('CPU', 'GPU', 'MOTHERBOARD', 'RAM', 'STORAGE', 'PSU', 'CASE', 'COOLING', name='componenttype'), nullable=False),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('rule_logic', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create build_configurations table
    op.create_table(
        'build_configurations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=True),
        sa.Column('use_case', sa.String(length=100), nullable=True),
        sa.Column('budget_dzd', sa.Float(), nullable=False),
        sa.Column('total_price_dzd', sa.Float(), nullable=True),
        sa.Column('components', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('compatibility_score', sa.Float(), nullable=True),
        sa.Column('value_score', sa.Float(), nullable=True),
        sa.Column('locale', sa.String(length=5), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_build_configurations_use_case'), 'build_configurations', ['use_case'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_build_configurations_use_case'), table_name='build_configurations')
    op.drop_table('build_configurations')
    op.drop_table('compatibility_rules')
    op.drop_index(op.f('ix_component_translations_locale'), table_name='component_translations')
    op.drop_table('component_translations')
    op.drop_index(op.f('ix_components_source_platform'), table_name='components')
    op.drop_index(op.f('ix_components_in_stock'), table_name='components')
    op.drop_index(op.f('ix_components_condition'), table_name='components')
    op.drop_index(op.f('ix_components_price_dzd'), table_name='components')
    op.drop_index(op.f('ix_components_manufacturer'), table_name='components')
    op.drop_index(op.f('ix_components_name'), table_name='components')
    op.drop_index(op.f('ix_components_component_type'), table_name='components')
    op.drop_table('components')

