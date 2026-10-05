"""add model drift

Revision ID: 52a1762c45ab
Revises: deec6eff8274
Create Date: 2026-10-05 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52a1762c45ab'
down_revision: Union[str, None] = 'deec6eff8274'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # AnalysisRun fields
    op.add_column('analysis_runs', sa.Column('files_total', sa.Integer(), nullable=True))
    op.add_column('analysis_runs', sa.Column('files_done', sa.Integer(), nullable=True))
    op.add_column('analysis_runs', sa.Column('files_skipped', sa.Integer(), nullable=True))
    op.add_column('analysis_runs', sa.Column('skipped_reasons', sa.String(), nullable=True))
    op.add_column('analysis_runs', sa.Column('functions_found', sa.Integer(), nullable=True))
    op.add_column('analysis_runs', sa.Column('error_message', sa.String(), nullable=True))

    # Feedback fields
    op.add_column('feedback', sa.Column('comment', sa.String(), nullable=True))
    op.add_column('feedback', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('feedback', sa.Column('updated_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('feedback', 'updated_at')
    op.drop_column('feedback', 'created_at')
    op.drop_column('feedback', 'comment')
    op.drop_column('analysis_runs', 'error_message')
    op.drop_column('analysis_runs', 'functions_found')
    op.drop_column('analysis_runs', 'skipped_reasons')
    op.drop_column('analysis_runs', 'files_skipped')
    op.drop_column('analysis_runs', 'files_done')
    op.drop_column('analysis_runs', 'files_total')
