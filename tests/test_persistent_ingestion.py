
import json
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.models import (
    ClinicalReviewRecord,
    DocumentVersion,
    HealthSource as DBHealthSource,
    KnowledgeAuditEvent,
    KnowledgeDocument as DBDocument,
    KnowledgeDocumentTopic,
)
from app.knowledge.models import HealthSource, KnowledgeDocument
from app.knowledge.persistent_ingestion import (
    PersistentKnowledgeIngestion,
)
from app.knowledge.review_workflow import document_fingerprint


@pytest.fixture
def db_session():
    """Create an isolated in-memory database for each test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def source_metadata():
    """Build source metadata with synthetic permission evidence."""
    verified_at = datetime(2026, 10, 1, tzinfo=timezone.utc)
    checked_at = datetime(2026, 10, 1, tzinfo=timezone.utc)

    return {
        "source_id": "TEST-SOURCE-001",
        "title": "Synthetic HIV Education Source",
        "organization": "Test Health Organization",
        "url": "https://example.org/hiv-education",
        "language": "en",
        "review_status": "pending_review",
        "version": "1.0",
        "publication_date": None,
        "last_verified_at": verified_at,
        "permission_status": "permitted",
        "permission_basis": "Synthetic permission evidence for testing.",
        "permission_reference": "TEST-PERMISSION-001",
        "permission_checked_at": checked_at,
        "permission_checked_by": "test-permission-reviewer",
        "permission_notes": (
            "Test fixture only; not evidence of real-world permission."
        ),
    }


@pytest.fixture
def registered_source(db_session, source_metadata):
    """Register the matching source in the test database."""
    source = DBHealthSource(
        name=source_metadata["title"],
        organization=source_metadata["organization"],
        source_url=str(source_metadata["url"]),
        source_type="guideline",
        language=source_metadata["language"],
        permission_status="permitted",
        is_active=True,
        last_verified_at=source_metadata["last_verified_at"],
    )

    db_session.add(source)
    db_session.flush()

    return source


@pytest.fixture
def candidate_document(source_metadata):
    """Build a validated, pending-review candidate document."""
    source = HealthSource(**source_metadata)

    return KnowledgeDocument(
        document_id="TEST-DOCUMENT-001",
        source=source,
        title="Understanding HIV Prevention",
        content=(
            "HIV prevention education includes information about "
            "prevention methods, testing, and accessing health services."
        ),
        language="en",
        topics=["hiv_prevention", "hiv_testing"],
        ingestion_status="validated",
        review_status="pending_review",
    )


def test_ingest_creates_pending_review_document(
    db_session,
    registered_source,
    candidate_document,
):
    service = PersistentKnowledgeIngestion(db_session)

    result = service.ingest(
        candidate_document,
        actor_id="test-ingestion-user",
    )

    db_document = db_session.get(
        DBDocument,
        result.database_document_id,
    )

    assert result.created is True
    assert result.document_id == candidate_document.document_id
    assert result.version_number == 1
    assert result.status == "pending_review"

    assert db_document is not None
    assert db_document.status == "pending_review"
    assert db_document.topic == "hiv_prevention"
    assert db_document.source_id == registered_source.id

    assert db_session.scalar(
        select(ClinicalReviewRecord).where(
            ClinicalReviewRecord.document_version_id == result.version_id
        )
    ) is None


def test_ingest_persists_all_topics(
    db_session,
    registered_source,
    candidate_document,
):
    service = PersistentKnowledgeIngestion(db_session)

    result = service.ingest(candidate_document)

    topics = set(
        db_session.scalars(
            select(KnowledgeDocumentTopic.topic).where(
                KnowledgeDocumentTopic.document_id
                == result.database_document_id
            )
        ).all()
    )

    assert topics == {
        "hiv_prevention",
        "hiv_testing",
    }


def test_ingest_persists_immutable_version_snapshot(
    db_session,
    registered_source,
    candidate_document,
):
    service = PersistentKnowledgeIngestion(db_session)

    result = service.ingest(candidate_document)

    version = db_session.get(DocumentVersion, result.version_id)

    assert version is not None
    assert version.version_number == 1
    assert version.content == candidate_document.content
    assert version.content_fingerprint == document_fingerprint(
        candidate_document
    )

    snapshot = version.review_snapshot

    assert snapshot["document_id"] == candidate_document.document_id
    assert snapshot["topics"] == sorted(candidate_document.topics)
    assert snapshot["source_permission_status"] == "permitted"
    assert snapshot["source_permission_basis"]
    assert snapshot["source_permission_reference"]
    assert snapshot["source_permission_checked_at"]
    assert snapshot["source_permission_checked_by"]
    assert snapshot["source_permission_notes"]


def test_ingest_records_audit_event_with_actor(
    db_session,
    registered_source,
    candidate_document,
):
    service = PersistentKnowledgeIngestion(db_session)

    result = service.ingest(
        candidate_document,
        actor_id="test-ingestion-user",
    )

    audit = db_session.scalar(
        select(KnowledgeAuditEvent).where(
            KnowledgeAuditEvent.entity_id
            == str(result.database_document_id)
        )
    )

    assert audit is not None
    assert audit.event_type == "knowledge_document_ingested"
    assert audit.actor_id == "test-ingestion-user"

    details = json.loads(audit.details)

    assert details["external_document_id"] == candidate_document.document_id
    assert details["status"] == "pending_review"
    assert details["version_number"] == 1


def test_ingest_allows_missing_optional_actor(
    db_session,
    registered_source,
    candidate_document,
):
    service = PersistentKnowledgeIngestion(db_session)

    result = service.ingest(candidate_document)

    audit = db_session.scalar(
        select(KnowledgeAuditEvent).where(
            KnowledgeAuditEvent.entity_id
            == str(result.database_document_id)
        )
    )

    assert audit is not None
    assert audit.actor_id is None


def test_identical_retry_is_idempotent(
    db_session,
    registered_source,
    candidate_document,
):
    service = PersistentKnowledgeIngestion(db_session)

    first = service.ingest(candidate_document)
    second = service.ingest(candidate_document)

    assert first.created is True
    assert second.created is False
    assert second.database_document_id == first.database_document_id
    assert second.version_id == first.version_id

    documents = db_session.scalars(
        select(DBDocument)
    ).all()

    versions = db_session.scalars(
        select(DocumentVersion)
    ).all()

    assert len(documents) == 1
    assert len(versions) == 1


def test_conflicting_retry_is_rejected(
    db_session,
    registered_source,
    candidate_document,
):
    service = PersistentKnowledgeIngestion(db_session)

    service.ingest(candidate_document)

    conflicting_document = candidate_document.model_copy(
        update={
            "content": (
                candidate_document.content
                + " Additional conflicting content."
            )
        }
    )

    with pytest.raises(ValueError, match="already exists"):
        service.ingest(conflicting_document)


def test_unregistered_source_is_rejected(
    db_session,
    candidate_document,
):
    service = PersistentKnowledgeIngestion(db_session)

    with pytest.raises(ValueError, match="No registered database source"):
        service.ingest(candidate_document)


def test_inactive_source_is_rejected(
    db_session,
    registered_source,
    candidate_document,
):
    registered_source.is_active = False
    db_session.flush()

    service = PersistentKnowledgeIngestion(db_session)

    with pytest.raises(ValueError, match="Inactive sources"):
        service.ingest(candidate_document)


def test_source_without_permission_is_rejected(
    db_session,
    registered_source,
    candidate_document,
):
    registered_source.permission_status = "pending"
    db_session.flush()

    service = PersistentKnowledgeIngestion(db_session)

    with pytest.raises(ValueError, match="permission status"):
        service.ingest(candidate_document)


def test_unvalidated_document_is_rejected(
    db_session,
    registered_source,
    candidate_document,
):
    unvalidated = candidate_document.model_copy(
        update={"ingestion_status": "pending_validation"}
    )

    service = PersistentKnowledgeIngestion(db_session)

    with pytest.raises(ValueError, match="ingestion_status"):
        service.ingest(unvalidated)


def test_document_not_pending_review_is_rejected(
    db_session,
    registered_source,
    candidate_document,
):
    approved_candidate = candidate_document.model_copy(
        update={"review_status": "approved"}
    )

    service = PersistentKnowledgeIngestion(db_session)

    with pytest.raises(ValueError, match="pending_review"):
        service.ingest(approved_candidate)


def test_empty_topics_are_rejected(
    db_session,
    registered_source,
    candidate_document,
):
    document_without_topics = candidate_document.model_copy(
        update={"topics": []}
    )

    service = PersistentKnowledgeIngestion(db_session)

    with pytest.raises(ValueError, match="At least one topic"):
        service.ingest(document_without_topics)


def test_duplicate_topics_are_rejected(
    db_session,
    registered_source,
    candidate_document,
):
    document_with_duplicate_topics = candidate_document.model_copy(
        update={
            "topics": [
                "hiv_prevention",
                "hiv_prevention",
            ]
        }
    )

    service = PersistentKnowledgeIngestion(db_session)

    with pytest.raises(ValueError, match="Duplicate document topics"):
        service.ingest(document_with_duplicate_topics)


def test_ingestion_does_not_commit_caller_transaction(
    db_session,
    registered_source,
    candidate_document,
):
    service = PersistentKnowledgeIngestion(db_session)

    result = service.ingest(candidate_document)

    # The service flushes its writes but leaves the transaction open.
    assert db_session.in_transaction()

    # Roll back the caller-owned transaction.
    db_session.rollback()

    assert db_session.get(DBDocument, result.database_document_id) is None





def test_original_ingestion_retry_succeeds_after_later_review_version(
    db_session,
    registered_source,
    candidate_document,
):
    """An original ingestion retry must preserve later clinical-review versions."""
    from sqlalchemy import select

    from app.knowledge.persistent_review_workflow import (
        PersistentClinicalReviewWorkflow,
    )

    ingestion = PersistentKnowledgeIngestion(db_session)

    # Step 1: Create the original persisted document and version 1.
    original_result = ingestion.ingest(candidate_document)

    assert original_result.created is True
    assert original_result.version_number == 1

    # Step 2: Create a revised candidate for clinical review.
    revised_document = candidate_document.model_copy(
        update={
            "content": (
                "Synthetic revised content for testing a later version. "
                "This is not clinical guidance."
            )
        }
    )

    # Step 3: Create version 2 and record a clinical review decision.
    workflow = PersistentClinicalReviewWorkflow(
        db_session,
        authorized_reviewer_ids={"reviewer-test"},
    )

    review = workflow.record_review(
        revised_document,
        database_document_id=original_result.database_document_id,
        version_number=2,
        reviewer_id="reviewer-test",
        preparer_id="preparer-test",
        decision="rejected",
        rationale="Synthetic rejection for the ingestion retry test.",
        language_reviewed="en",
    )

    db_session.flush()

    version_two = db_session.scalar(
        select(DocumentVersion).where(
            DocumentVersion.document_id == original_result.database_document_id,
            DocumentVersion.version_number == 2,
        )
    )
    assert version_two is not None

    original_version_two_id = version_two.id
    original_version_two_content = version_two.content
    original_review_id = review.id

    # Step 4: Retry the exact original candidate.
    retry_result = ingestion.ingest(candidate_document)

    # The retry must return the original version 1.
    assert retry_result.created is False
    assert retry_result.database_document_id == original_result.database_document_id
    assert retry_result.version_id == original_result.version_id
    assert retry_result.version_number == 1
    assert retry_result.document_id == original_result.document_id

    # Step 5: Verify that no duplicate version was created.
    versions = list(
        db_session.scalars(
            select(DocumentVersion)
            .where(
                DocumentVersion.document_id
                == original_result.database_document_id
            )
            .order_by(DocumentVersion.version_number)
        ).all()
    )

    assert len(versions) == 2
    assert [version.version_number for version in versions] == [1, 2]

    # Step 6: Verify that version 2 and its review remain unchanged.
    unchanged_version_two = db_session.get(
        DocumentVersion,
        original_version_two_id,
    )
    assert unchanged_version_two is not None
    assert unchanged_version_two.content == original_version_two_content

    unchanged_review = db_session.get(
        ClinicalReviewRecord,
        original_review_id,
    )
    assert unchanged_review is not None
    assert unchanged_review.decision == "rejected"
    assert unchanged_review.document_version_id == original_version_two_id

    # Verify that the document's review status was not changed by the retry.
    db_document = db_session.get(
        DBDocument,
        original_result.database_document_id,
    )
    assert db_document is not None
    assert db_document.status == "rejected"
