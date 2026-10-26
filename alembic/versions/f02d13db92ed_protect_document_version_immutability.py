
"""Protect document version immutability.

Revision ID: f02d13db92ed
Revises: 03903e1ec021
"""

from typing import Sequence, Union

from alembic import op


revision: str = "f02d13db92ed"
down_revision: Union[str, Sequence[str], None] = "03903e1ec021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Prevent updates and deletes of existing document versions."""
    op.execute(
        """
        CREATE FUNCTION prevent_document_version_mutation()
        RETURNS TRIGGER AS $$
        BEGIN
            RAISE EXCEPTION
                'Document versions are immutable; create a new version instead.'
                USING ERRCODE = '55000';
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    op.execute(
        """
        CREATE TRIGGER trg_document_versions_immutable
        BEFORE UPDATE OR DELETE ON document_versions
        FOR EACH ROW
        EXECUTE FUNCTION prevent_document_version_mutation();
        """
    )


def downgrade() -> None:
    """Remove the immutability trigger and its function."""
    op.execute(
        """
        DROP TRIGGER IF EXISTS trg_document_versions_immutable
        ON document_versions;
        """
    )

    op.execute(
        """
        DROP FUNCTION IF EXISTS prevent_document_version_mutation();
        """
    )
