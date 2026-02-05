"""Add sample case fields to cases table

Revision ID: add_sample_case_fields
Revises: 20260201_add_synthesis_cache
Create Date: 2026-02-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_sample_case_fields'
down_revision = '20260201_add_synthesis_cache'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_sample_case column to cases table
    op.add_column('cases', sa.Column('is_sample_case', sa.Boolean(), nullable=True, server_default='false'))
    
    # Add thumbnail_path column to cases table
    op.add_column('cases', sa.Column('thumbnail_path', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('cases', 'thumbnail_path')
    op.drop_column('cases', 'is_sample_case')
