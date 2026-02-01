"""Add synthesis cache column

Revision ID: 20260201_add_synthesis_cache
Revises: 20260201_add_analysis_cache
Create Date: 2026-02-01
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20260201_add_synthesis_cache'
down_revision = '20260201_add_analysis_cache'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('cases', sa.Column('synthesis_analysis_json', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('cases', 'synthesis_analysis_json')
