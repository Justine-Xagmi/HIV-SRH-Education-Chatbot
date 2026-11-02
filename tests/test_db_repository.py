
import uuid

import pytest

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
def valid_document(repository_session):
    """Create a test-only source and document."""

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

    db.flush()
    return document


@pytest.fixture
def valid_version(valid_document, repository_session):
    """Create a test-only document version."""

    repo = KnowledgeRepository(repository_session)

    version = repo.create_document_version(
        document_id=valid_document.id,
        version_number=1,
        content="TEST-ONLY content; not health guidance.",
        content_fingerprint=uuid.uuid4().hex * 2,
    )

    repository_session.flush()
    return version


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
    repository_session,
    valid_version,
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
    repository_session,
    valid_version,
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
    repository_session,
    valid_version,
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
    repository_session,
    valid_version,
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


# ---------------------------------------------------------
# Multi-topic repository tests
# ---------------------------------------------------------


def test_repository_adds_multiple_document_topics(
    repository_session,
    valid_document,
):
    repo = KnowledgeRepository(repository_session)

    records = repo.add_document_topics(
        document_id=valid_document.id,
        topics=["sexual_health", "hiv_prevention", "hiv_testing"],
    )

    assert len(records) == 3
    assert repo.list_document_topics(valid_document.id) == [
        "hiv_prevention",
        "hiv_testing",
        "sexual_health",
    ]


def test_repository_adds_single_document_topic(
    repository_session,
    valid_document,
):
    repo = KnowledgeRepository(repository_session)

    record = repo.add_document_topic(
        document_id=valid_document.id,
        topic="hiv_prevention",
    )

    assert record.topic == "hiv_prevention"
    assert record.document_id == valid_document.id
    assert repo.list_document_topics(valid_document.id) == [
        "hiv_prevention"
    ]


def test_repository_rejects_duplicate_single_topic(
    repository_session,
    valid_document,
):
    repo = KnowledgeRepository(repository_session)

    repo.add_document_topic(
        document_id=valid_document.id,
        topic="hiv_prevention",
    )

    with pytest.raises(ValueError, match="already assigned"):
        repo.add_document_topic(
            document_id=valid_document.id,
            topic="hiv_prevention",
        )


def test_repository_rejects_duplicate_topics_in_same_request(
    repository_session,
    valid_document,
):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="Duplicate topics"):
        repo.add_document_topics(
            document_id=valid_document.id,
            topics=["hiv_prevention", "hiv_prevention"],
        )


def test_repository_rejects_empty_topic(
    repository_session,
    valid_document,
):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="Topic cannot be empty"):
        repo.add_document_topic(
            document_id=valid_document.id,
            topic="   ",
        )


def test_repository_rejects_empty_values_in_topic_list(
    repository_session,
    valid_document,
):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="empty values"):
        repo.add_document_topics(
            document_id=valid_document.id,
            topics=["hiv_prevention", " "],
        )


def test_repository_rejects_topic_longer_than_100_characters(
    repository_session,
    valid_document,
):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="100 characters"):
        repo.add_document_topic(
            document_id=valid_document.id,
            topic="x" * 101,
        )


def test_repository_rejects_topic_list_longer_than_100_characters(
    repository_session,
    valid_document,
):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="100 characters"):
        repo.add_document_topics(
            document_id=valid_document.id,
            topics=["x" * 101],
        )


def test_repository_rejects_topics_for_missing_document(
    repository_session,
):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="does not exist"):
        repo.add_document_topic(
            document_id=-999999,
            topic="hiv_prevention",
        )


def test_repository_rejects_multiple_topics_for_missing_document(
    repository_session,
):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="does not exist"):
        repo.add_document_topics(
            document_id=-999999,
            topics=["hiv_prevention", "hiv_testing"],
        )


def test_repository_rejects_existing_topic_in_multiple_topic_request(
    repository_session,
    valid_document,
):
    repo = KnowledgeRepository(repository_session)

    repo.add_document_topic(
        document_id=valid_document.id,
        topic="hiv_prevention",
    )

    with pytest.raises(ValueError, match="already assigned"):
        repo.add_document_topics(
            document_id=valid_document.id,
            topics=["hiv_prevention", "hiv_testing"],
        )


def test_repository_replaces_document_topics(
    repository_session,
    valid_document,
):
    repo = KnowledgeRepository(repository_session)

    repo.add_document_topics(
        document_id=valid_document.id,
        topics=["hiv_prevention", "hiv_testing"],
    )

    replacement_records = repo.replace_document_topics(
        document_id=valid_document.id,
        topics=["sexual_health", "contraception"],
    )

    assert len(replacement_records) == 2
    assert repo.list_document_topics(valid_document.id) == [
        "contraception",
        "sexual_health",
    ]


def test_repository_rejects_empty_replacement_topics(
    repository_session,
    valid_document,
):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="At least one topic"):
        repo.replace_document_topics(
            document_id=valid_document.id,
            topics=[],
        )


def test_repository_rejects_duplicate_replacement_topics(
    repository_session,
    valid_document,
):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="Duplicate topics"):
        repo.replace_document_topics(
            document_id=valid_document.id,
            topics=["hiv_testing", "hiv_testing"],
        )


def test_repository_rejects_replacement_for_missing_document(
    repository_session,
):
    repo = KnowledgeRepository(repository_session)

    with pytest.raises(ValueError, match="does not exist"):
        repo.replace_document_topics(
            document_id=-999999,
            topics=["hiv_prevention"],
        )
