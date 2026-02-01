"""add analysis cache columns

Revision ID: 20260201_add_analysis_cache
Revises: bfddc2a69577
Create Date: 2026-02-01 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260201_add_analysis_cache'
down_revision: Union[str, None] = 'bfddc2a69577'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns for caching analysis results
    op.add_column('cases', sa.Column('narrative_analysis_json', sa.Text(), nullable=True))
    op.add_column('cases', sa.Column('vision_analysis_json', sa.Text(), nullable=True))
    op.add_column('cases', sa.Column('analysis_status', sa.String(), nullable=True, server_default='PENDING'))


def downgrade() -> None:
    op.drop_column('cases', 'analysis_status')
    op.drop_column('cases', 'vision_analysis_json')
    op.drop_column('cases', 'narrative_analysis_json')
