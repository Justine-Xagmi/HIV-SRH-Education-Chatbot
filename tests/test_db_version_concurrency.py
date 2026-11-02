
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError

from app.db.models import (
    DocumentVersion,
    HealthSource,
    KnowledgeDocument,
)
from app.db.session import SessionLocal


EXPECTED_CONSTRAINT = "uq_document_versions_document_version"


@pytest.fixture
def test_document():
    """Create a committed, test-only document for independent sessions."""
    if SessionLocal is None:
        pytest.fail("DATABASE_URL is not configured.")

    setup_session = SessionLocal()

    if setup_session.get_bind().dialect.name != "postgresql":
        pytest.skip("These tests require PostgreSQL.")

    suffix = uuid.uuid4().hex

    source = HealthSource(
        name=f"TEST-ONLY concurrency source {suffix}",
        source_type="test_only",
        language="en",
        permission_status="pending",
        is_active=False,
    )

    setup_session.add(source)
    setup_session.flush()

    document = KnowledgeDocument(
        source_id=source.id,
        title=f"TEST-ONLY concurrency document {suffix}",
        topic="test_only",
        language="en",
        status="draft",
    )

    setup_session.add(document)
    setup_session.commit()

    document_id = document.id
    source_id = source.id

    try:
        yield document_id
    finally:
        # Remove only this fixture's test records.
        setup_session.rollback()

        try:
            setup_session.execute(
                text(
                    """
                    DROP TRIGGER IF EXISTS
                    trg_document_versions_immutable
                    ON public.document_versions
                    """
                )
            )

            setup_session.execute(
                DocumentVersion.__table__.delete().where(
                    DocumentVersion.document_id == document_id
                )
            )

            setup_session.execute(
                KnowledgeDocument.__table__.delete().where(
                    KnowledgeDocument.id == document_id
                )
            )

            setup_session.execute(
                HealthSource.__table__.delete().where(
                    HealthSource.id == source_id
                )
            )

            # Restore the immutability trigger before committing cleanup.
            setup_session.execute(
                text(
                    """
                    CREATE TRIGGER trg_document_versions_immutable
                    BEFORE UPDATE OR DELETE
                    ON public.document_versions
                    FOR EACH ROW
                    EXECUTE FUNCTION prevent_document_version_mutation()
                    """
                )
            )

            setup_session.commit()

        except Exception:
            setup_session.rollback()
            raise

        finally:
            setup_session.close()


def create_version(session, document_id, version_number=1):
    """Create a test-only document version."""
    version = DocumentVersion(
        document_id=document_id,
        version_number=version_number,
        content="TEST-ONLY concurrency test; not health guidance.",
        content_fingerprint=uuid.uuid4().hex * 2,
    )

    session.add(version)
    return version


def get_constraint_name(error):
    """Return the PostgreSQL constraint responsible for an integrity error."""
    original_error = error.orig
    diagnostic = getattr(original_error, "diag", None)

    if diagnostic is None:
        return None

    return getattr(diagnostic, "constraint_name", None)


def test_duplicate_version_reports_exact_constraint(test_document):
    """Verify duplicate versions violate the expected unique constraint."""
    session = SessionLocal()

    try:
        create_version(session, test_document, version_number=1)
        session.commit()

        create_version(session, test_document, version_number=1)

        with pytest.raises(IntegrityError) as error:
            session.flush()

        assert get_constraint_name(error.value) == EXPECTED_CONSTRAINT

        session.rollback()

        saved_count = session.scalar(
            select(func.count())
            .select_from(DocumentVersion)
            .where(
                DocumentVersion.document_id == test_document,
                DocumentVersion.version_number == 1,
            )
        )

        assert saved_count == 1

    finally:
        session.rollback()
        session.close()


def test_concurrent_duplicate_version_insertions_allow_only_one(
    test_document,
):
    """
    Verify independent transactions cannot both create the same version.

    Both workers wait at a barrier before attempting their database insert.
    PostgreSQL's unique constraint must allow exactly one transaction to
    commit and reject the other.
    """
    barrier = Barrier(2)

    def insert_version():
        session = SessionLocal()

        try:
            barrier.wait(timeout=15)

            create_version(session, test_document, version_number=1)
            session.commit()

            return "success", None

        except IntegrityError as error:
            constraint_name = get_constraint_name(error)
            session.rollback()

            return "conflict", constraint_name

        finally:
            session.close()

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [
            executor.submit(insert_version),
            executor.submit(insert_version),
        ]

        results = [future.result(timeout=30) for future in futures]

    successes = [
        result for result in results if result[0] == "success"
    ]

    conflicts = [
        result for result in results if result[0] == "conflict"
    ]

    assert len(successes) == 1
    assert len(conflicts) == 1
    assert conflicts[0][1] == EXPECTED_CONSTRAINT

    # Verify exactly one version was committed.
    verification_session = SessionLocal()

    try:
        saved_count = verification_session.scalar(
            select(func.count())
            .select_from(DocumentVersion)
            .where(
                DocumentVersion.document_id == test_document,
                DocumentVersion.version_number == 1,
            )
        )

        assert saved_count == 1

    finally:
        verification_session.close()
