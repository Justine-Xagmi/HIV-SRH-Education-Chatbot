
import uuid

import pytest
from sqlalchemy import delete, update
from sqlalchemy.exc import DBAPIError

from app.db.models import (
    DocumentVersion,
    HealthSource,
    KnowledgeDocument,
)
from app.db.repository import KnowledgeRepository
from app.db.session import SessionLocal


@pytest.fixture
def db_session():
    if SessionLocal is None:
        pytest.fail("DATABASE_URL is not configured.")

    session = SessionLocal()
    try:
        yield session
    finally:
        # Roll back test records instead of deleting immutable versions.
        session.rollback()
        session.close()


def create_test_version(session):
    """Create temporary test-only records without committing them."""
    repository = KnowledgeRepository(session)
    suffix = uuid.uuid4().hex

    source = repository.create_source(
        name=f"TEST-ONLY source {suffix}",
        source_type="test_only",
        language="en",
        permission_status="pending",
        is_active=False,
    )

    document = repository.create_document(
        source_id=source.id,
        title=f"TEST-ONLY document {suffix}",
        topic="test_only",
        language="en",
    )

    version = repository.create_document_version(
        document_id=document.id,
        version_number=1,
        content="TEST-ONLY content; not health guidance.",
        content_fingerprint=uuid.uuid4().hex * 2,
    )

    session.flush()
    return document, version


def test_existing_document_version_cannot_be_updated(db_session):
    _, version = create_test_version(db_session)

    with pytest.raises(DBAPIError):
        with db_session.begin_nested():
            db_session.execute(
                update(DocumentVersion)
                .where(DocumentVersion.id == version.id)
                .values(content="Modified test content")
            )


def test_existing_document_version_cannot_be_deleted(db_session):
    _, version = create_test_version(db_session)

    with pytest.raises(DBAPIError):
        with db_session.begin_nested():
            db_session.execute(
                delete(DocumentVersion).where(
                    DocumentVersion.id == version.id
                )
            )


def test_new_document_version_can_be_inserted(db_session):
    document, first_version = create_test_version(db_session)

    second_version = KnowledgeRepository(db_session).create_document_version(
        document_id=document.id,
        version_number=2,
        content="TEST-ONLY new version; not health guidance.",
        content_fingerprint=uuid.uuid4().hex * 2,
    )

    assert first_version.id != second_version.id
    assert second_version.version_number == 2
    assert second_version.document_id == document.id
