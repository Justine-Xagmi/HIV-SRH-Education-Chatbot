
import uuid

import pytest

from app.db.models import (
    ClinicalReviewRecord,
    DocumentVersion,
    HealthSource,
    KnowledgeAuditEvent,
    KnowledgeDocument,
)
from app.db.repository import KnowledgeRepository
from app.db.session import SessionLocal


@pytest.fixture
def repository_session():
    if SessionLocal is None:
        pytest.fail("DATABASE_URL is not configured.")

    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def valid_version(repository_session):
    """Create test-only source, document, and version for validation tests."""
    db = repository_session
    repo = KnowledgeRepository(db)
    suffix = uuid.uuid4().hex

    source = repo.create_source(
        name=f"TEST-ONLY source {suffix}",
        source_type="test_only",
        language="en",
        permission_status="pending",
        is_active=False,
    )
    document = repo.create_document(
        source_id=source.id,
        title=f"TEST-ONLY document {suffix}",
        topic="test_only",
        language="en",
    )
    version = repo.create_document_version(
        document_id=document.id,
        version_number=1,
        content="TEST-ONLY content; not health guidance.",
        content_fingerprint=uuid.uuid4().hex * 2,
    )

    db.flush()
    yield version

    # Roll back these fixture records; no commit is performed here.
    db.rollback()


def test_repository_creates_and_retrieves_governance_records(
    repository_session,
):
    db = repository_session
    repo = KnowledgeRepository(db)
    suffix = uuid.uuid4().hex

    source = repo.create_source(
        name=f"TEST-ONLY source {suffix}",
        source_type="test_only",
        language="en",
        permission_status="pending",
        is_active=False,
    )
    document = repo.create_document(
        source_id=source.id,
        title=f"TEST-ONLY document {suffix}",
        topic="test_only",
        language="en",
    )
    version = repo.create_document_version(
        document_id=document.id,
        version_number=1,
        content="TEST-ONLY content; not health guidance.",
        content_fingerprint=uuid.uuid4().hex * 2,
    )
    review = repo.create_review_record(
        document_version_id=version.id,
        reviewer_id=f"test-only-{suffix}",
        decision="changes_requested",
        rationale="TEST-ONLY repository verification.",
        language="en",
    )
    event = repo.create_audit_event(
        event_type="test_repository",
        entity_type="document_version",
        entity_id=str(version.id),
        actor_id=f"test-only-{suffix}",
        details={"purpose": "automated test only"},
    )

    db.flush()

    assert repo.get_source(source.id).name == f"TEST-ONLY source {suffix}"
    assert repo.get_document(document.id).source_id == source.id
    assert repo.get_document_version(version.id).document_id == document.id
    assert len(repo.list_document_versions(document.id)) == 1
    assert len(repo.list_reviews_for_version(version.id)) == 1

    events = repo.list_audit_events(
        entity_type="document_version",
        entity_id=str(version.id),
    )
    assert any(item.id == event.id for item in events)
    assert repo.get_source(source.id).permission_status == "pending"
    assert review.decision == "changes_requested"


def test_repository_rejects_missing_source(repository_session):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="does not exist"):
        repo.create_document(
            source_id=-999999,
            title="TEST-ONLY",
            topic="test_only",
            language="en",
        )


def test_repository_rejects_missing_document_version(repository_session):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="does not exist"):
        repo.create_review_record(
            document_version_id=-999999,
            reviewer_id="test-only",
            decision="changes_requested",
            rationale="TEST-ONLY",
            language="en",
        )


def test_repository_rejects_invalid_review_decision(
    repository_session, valid_version
):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="Invalid clinical review decision"):
        repo.create_review_record(
            document_version_id=valid_version.id,
            reviewer_id="test-only",
            decision="publish_immediately",
            rationale="TEST-ONLY",
            language="en",
        )


def test_repository_rejects_invalid_version_number(
    repository_session, valid_version
):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="Version number"):
        repo.create_document_version(
            document_id=valid_version.document_id,
            version_number=0,
            content="TEST-ONLY",
            content_fingerprint=uuid.uuid4().hex * 2,
        )


def test_repository_rejects_invalid_fingerprint_length(
    repository_session, valid_version
):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="64 characters"):
        repo.create_document_version(
            document_id=valid_version.document_id,
            version_number=2,
            content="TEST-ONLY",
            content_fingerprint="too-short",
        )


def test_repository_rejects_empty_review_fields(
    repository_session, valid_version
):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="Reviewer ID"):
        repo.create_review_record(
            document_version_id=valid_version.id,
            reviewer_id=" ",
            decision="approved",
            rationale="TEST-ONLY",
            language="en",
        )
