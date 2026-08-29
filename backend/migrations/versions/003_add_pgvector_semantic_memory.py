"""Add embedding column to messages and enable pgvector

Revision ID: 003
Revises: 002
Create Date: 2026-08-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Add embedding column (384-dim for all-MiniLM-L6-v2)
    op.add_column("messages", sa.Column(
        "embedding", sa.Text(), nullable=True
    ))
    # We store as text-serialized vector and cast in queries.
    # For production pgvector, use: sa.Column("embedding", Vector(384))
    # This requires pgvector to be installed on PostgreSQL.

    # Add detected_mood and mood_confidence to messages table
    op.add_column("messages", sa.Column(
        "detected_mood", sa.String(50), nullable=True
    ))
    op.add_column("messages", sa.Column(
        "mood_confidence", sa.Float(), nullable=True
    ))

    # Add user_id to messages for direct user-scoped semantic search
    op.add_column("messages", sa.Column(
        "user_id", postgresql.UUID(as_uuid=True), nullable=True
    ))
    op.create_foreign_key(
        "fk_messages_user_id",
        "messages", "users",
        ["user_id"], ["id"],
        ondelete="CASCADE"
    )


def downgrade() -> None:
    op.drop_constraint("fk_messages_user_id", "messages", type_="foreignkey")
    op.drop_column("messages", "user_id")
    op.drop_column("messages", "mood_confidence")
    op.drop_column("messages", "detected_mood")
    op.drop_column("messages", "embedding")
    op.execute('DROP EXTENSION IF EXISTS vector')
