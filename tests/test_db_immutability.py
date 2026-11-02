
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


EXPECTED_SQLSTATE = "55000"
EXPECTED_ERROR_MESSAGE = (
    "Document versions are immutable; create a new version instead."
)


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


def assert_immutability_error(error):
    """Verify that PostgreSQL returned the expected immutability error."""
    original_error = error.value.orig

    # psycopg 3 exposes sqlstate; psycopg2 exposes pgcode.
    actual_sqlstate = (
        getattr(original_error, "sqlstate", None)
        or getattr(original_error, "pgcode", None)
    )

    assert actual_sqlstate == EXPECTED_SQLSTATE, (
        f"Expected PostgreSQL SQLSTATE {EXPECTED_SQLSTATE}, "
        f"but received {actual_sqlstate!r}. "
        f"Original error: {original_error}"
    )

    # PostgreSQL drivers expose the primary message through diag when
    # available. Fall back to the original exception text.
    diagnostic = getattr(original_error, "diag", None)
    actual_message = (
        getattr(diagnostic, "message_primary", None)
        if diagnostic is not None
        else None
    )

    if actual_message is None:
        actual_message = str(original_error)

    assert actual_message == EXPECTED_ERROR_MESSAGE, (
        f"Expected immutability message {EXPECTED_ERROR_MESSAGE!r}, "
        f"but received {actual_message!r}"
    )


def test_existing_document_version_cannot_be_updated(db_session):
    _, version = create_test_version(db_session)

    with pytest.raises(DBAPIError) as error:
        with db_session.begin_nested():
            db_session.execute(
                update(DocumentVersion)
                .where(DocumentVersion.id == version.id)
                .values(content="Modified test content")
            )

    assert_immutability_error(error)


def test_existing_document_version_cannot_be_deleted(db_session):
    _, version = create_test_version(db_session)

    with pytest.raises(DBAPIError) as error:
        with db_session.begin_nested():
            db_session.execute(
                delete(DocumentVersion).where(
                    DocumentVersion.id == version.id
                )
            )

    assert_immutability_error(error)


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
