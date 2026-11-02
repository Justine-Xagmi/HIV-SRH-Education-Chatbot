
"""add knowledge document topics

Revision ID: 7c91e4a2b6d3
Revises: 2833c9394364
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision: str = "7c91e4a2b6d3"
down_revision: Union[str, Sequence[str], None] = "2833c9394364"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the knowledge document topics association table."""

    op.create_table(
        "knowledge_document_topics",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "document_id",
            sa.Integer(),
            sa.ForeignKey(
                "knowledge_documents.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "topic",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "document_id",
            "topic",
            name="uq_knowledge_document_topics_document_topic",
        ),
    )

    op.create_index(
        "ix_knowledge_document_topics_document_id",
        "knowledge_document_topics",
        ["document_id"],
        unique=False,
    )


def downgrade() -> None:
    """Prevent destructive removal of knowledge document topics."""

    raise RuntimeError(
        "Downgrade is blocked because knowledge document topics "
        "may contain important knowledge-base data. "
        "Use an explicitly reviewed recovery procedure instead."
    )

    op.drop_table("knowledge_document_topics")
