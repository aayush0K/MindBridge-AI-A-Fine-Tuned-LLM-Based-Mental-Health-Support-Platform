"""Add automated mood detection columns to mood_logs

Revision ID: 002
Revises: 001
Create Date: 2026-08-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── mood_logs: add automated detection columns ────────────────────────────
    op.add_column("mood_logs", sa.Column(
        "auto_detected", sa.Boolean(), server_default=sa.text("false"), nullable=False
    ))
    op.add_column("mood_logs", sa.Column(
        "confidence", sa.Float(), nullable=True
    ))
    op.add_column("mood_logs", sa.Column(
        "message_id", postgresql.UUID(as_uuid=True), nullable=True
    ))
    op.add_column("mood_logs", sa.Column(
        "raw_label", sa.String(50), nullable=True
    ))
    op.create_foreign_key(
        "fk_mood_logs_message_id",
        "mood_logs", "messages",
        ["message_id"], ["id"],
        ondelete="SET NULL"
    )


def downgrade() -> None:
    op.drop_constraint("fk_mood_logs_message_id", "mood_logs", type_="foreignkey")
    op.drop_column("mood_logs", "raw_label")
    op.drop_column("mood_logs", "message_id")
    op.drop_column("mood_logs", "confidence")
    op.drop_column("mood_logs", "auto_detected")
