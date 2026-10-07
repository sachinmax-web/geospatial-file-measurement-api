"""initial_schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-07 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'files',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('storage_path', sa.String(length=512), nullable=False),
        sa.Column('crs', sa.String(length=100), nullable=True),
        sa.Column('feature_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PROCESSING'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'feature_measurements',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('file_id', sa.String(length=36), nullable=False),
        sa.Column('feature_index', sa.Integer(), nullable=False),
        sa.Column('geometry_type', sa.String(length=50), nullable=False),
        sa.Column('original_crs', sa.String(length=100), nullable=True),
        sa.Column('projected_crs', sa.String(length=100), nullable=True),
        sa.Column('measurement_type', sa.String(length=50), nullable=True),
        sa.Column('measurement_value', sa.Float(), nullable=True),
        sa.Column('properties', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='VALID'),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['file_id'], ['files.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_feature_measurements_file_id'), 'feature_measurements', ['file_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_feature_measurements_file_id'), table_name='feature_measurements')
    op.drop_table('feature_measurements')
    op.drop_table('files')
