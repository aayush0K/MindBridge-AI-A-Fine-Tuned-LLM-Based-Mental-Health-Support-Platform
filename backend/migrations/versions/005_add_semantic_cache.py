"""Create semantic_cache table with vector support

Revision ID: 005
Revises: 004
Create Date: 2026-09-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

try:
    from pgvector.sqlalchemy import Vector
    vector_type = Vector(384)
except ImportError:
    vector_type = sa.Text()

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure vector extension exists in PostgreSQL
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "semantic_cache",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("query_text", sa.Text(), nullable=False),
        sa.Column("response_text", sa.Text(), nullable=False),
        sa.Column("embedding", vector_type, nullable=False),
        sa.Column("detected_mood", sa.String(50), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),
        sa.Column("similarity_threshold", sa.Float(), server_default="0.90", nullable=False),
        sa.Column("hit_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
    )

    op.create_index("ix_semantic_cache_expires_at", "semantic_cache", ["expires_at"])
    op.create_index("ix_semantic_cache_is_active", "semantic_cache", ["is_active"])

    # Attempt HNSW vector index creation
    try:
        op.execute(
            "CREATE INDEX IF NOT EXISTS ix_semantic_cache_embedding_hnsw "
            "ON semantic_cache USING hnsw (embedding vector_cosine_ops);"
        )
    except Exception:
        pass


def downgrade() -> None:
    op.drop_index("ix_semantic_cache_is_active", table_name="semantic_cache")
    op.drop_index("ix_semantic_cache_expires_at", table_name="semantic_cache")
    op.drop_table("semantic_cache")
