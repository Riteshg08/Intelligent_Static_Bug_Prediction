"""add pattern_severity

Revision ID: 7f8b9c0d1e2f
Revises: 52a1762c45ab
Create Date: 2026-10-05 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7f8b9c0d1e2f'
down_revision = '52a1762c45ab'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('predictions', sa.Column('pattern_severity', sa.String(), server_default='none', nullable=True))

def downgrade():
    op.drop_column('predictions', 'pattern_severity')
