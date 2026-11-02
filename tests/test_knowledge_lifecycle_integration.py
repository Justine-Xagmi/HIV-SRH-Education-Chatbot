
import json
import uuid
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import select, text

from app.db.models import (
    ClinicalReviewRecord as DBReview,
    DocumentVersion,
    HealthSource as DBSource,
    KnowledgeAuditEvent,
    KnowledgeDocument as DBDocument,
)
from app.db.session import SessionLocal
from app.knowledge.ingestion import prepare_candidate_document
from app.knowledge.models import HealthSource, KnowledgeDocument
from app.knowledge.persistent_review_workflow import (
    PersistentClinicalReviewWorkflow,
)
from app.knowledge.persistent_retrieval import PersistentKnowledgeRetriever


IMMUTABILITY_TRIGGER = "trg_document_versions_immutable"


@pytest.fixture
def lifecycle_context():
    """Create isolated synthetic database records for lifecycle testing."""

    if SessionLocal is None:
        pytest.skip("DATABASE_URL is not configured.")

    db = SessionLocal()
    suffix = uuid.uuid4().hex[:12]

    db_source = None
    db_document = None
    trigger_was_dropped = False

    verified_at = datetime.now(timezone.utc)

    try:
        db_source = DBSource(
            name=f"Lifecycle source {suffix}",
            organization="Synthetic Test Organization",
            source_url=f"https://example.org/lifecycle-{suffix}",
            source_type="synthetic_test",
            language="en",
            permission_status="permitted",
            is_active=True,
            last_verified_at=verified_at,
        )
        db.add(db_source)
        db.flush()

        db_document = DBDocument(
            source_id=db_source.id,
            title=f"Lifecycle test document {suffix}",
            topic="hiv_prevention",
            language="en",
            status="pending_review",
        )
        db.add(db_document)
        db.commit()

        source = HealthSource(
            source_id=f"lifecycle-source-{suffix}",
            title=db_source.name,
            organization=db_source.organization,
            url=db_source.source_url,
            language="en",
            review_status="pending_review",
            version="1.0",
            publication_date=date(2025, 1, 1),
            last_verified_at=verified_at,
            permission_status="permitted",
            permission_basis=(
                "Synthetic permission evidence for automated testing."
            ),
            permission_reference="TEST-PERMISSION-001",
            permission_checked_at=verified_at,
            permission_checked_by="integration-test-reviewer",
            permission_notes=(
                "Test fixture only; not evidence of real-world permission."
            ),
        )

        candidate = KnowledgeDocument(
            document_id=f"lifecycle-document-{suffix}",
            source=source,
            title=db_document.title,
            content=(
                "Synthetic educational content for testing the "
                "knowledge lifecycle. This is not clinical guidance."
            ),
            language="en",
            topics=["hiv_prevention"],
            ingestion_status="pending_validation",
            review_status="pending_review",
        )

        yield {
            "db": db,
            "source_id": db_source.id,
            "document_id": db_document.id,
            "source": source,
            "candidate": candidate,
        }

    finally:
        try:
            db.rollback()

            if db_document is not None:
                # Test cleanup temporarily disables the immutability
                # trigger so isolated test records can be deleted.
                db.execute(
                    text(
                        f"DROP TRIGGER IF EXISTS {IMMUTABILITY_TRIGGER} "
                        "ON document_versions"
                    )
                )
                trigger_was_dropped = True

                version_ids = list(
                    db.scalars(
                        select(DocumentVersion.id).where(
                            DocumentVersion.document_id == db_document.id
                        )
                    )
                )

                if version_ids:
                    db.execute(
                        text(
                            """
                            DELETE FROM clinical_review_records
                            WHERE document_version_id = ANY(:version_ids)
                            """
                        ),
                        {"version_ids": version_ids},
                    )

                db.execute(
                    text(
                        """
                        DELETE FROM knowledge_audit_events
                        WHERE entity_type = 'knowledge_document'
                          AND entity_id = :document_id
                        """
                    ),
                    {"document_id": str(db_document.id)},
                )

                db.execute(
                    text(
                        """
                        DELETE FROM document_versions
                        WHERE document_id = :document_id
                        """
                    ),
                    {"document_id": db_document.id},
                )

                db.execute(
                    text(
                        """
                        DELETE FROM knowledge_documents
                        WHERE id = :document_id
                        """
                    ),
                    {"document_id": db_document.id},
                )

            if db_source is not None:
                db.execute(
                    text(
                        "DELETE FROM health_sources WHERE id = :source_id"
                    ),
                    {"source_id": db_source.id},
                )

            if trigger_was_dropped:
                db.execute(
                    text(
                        f"""
                        CREATE TRIGGER {IMMUTABILITY_TRIGGER}
                        BEFORE UPDATE OR DELETE ON document_versions
                        FOR EACH ROW
                        EXECUTE FUNCTION prevent_document_version_mutation()
                        """
                    )
                )

            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()


def test_complete_knowledge_lifecycle(lifecycle_context):
    """Verify ingestion, independent review, persistence, and retrieval."""

    context = lifecycle_context
    db = context["db"]

    # 1. Prepare the candidate through the real ingestion function.
    prepared = prepare_candidate_document(context["candidate"])

    assert prepared.ingestion_status == "validated"
    assert prepared.review_status == "pending_review"
    assert prepared.source.review_status == "pending_review"

    # 2. Confirm that preparation did not approve the database document.
    db_document = db.get(DBDocument, context["document_id"])

    assert db_document is not None
    assert db_document.status == "pending_review"

    # 3. Submit an independent authorized clinical review.
    workflow = PersistentClinicalReviewWorkflow(
        db,
        authorized_reviewer_ids={"integration-reviewer"},
    )

    review = workflow.record_review(
        prepared,
        database_document_id=context["document_id"],
        version_number=1,
        reviewer_id="integration-reviewer",
        preparer_id="integration-preparer",
        decision="approved",
        rationale="Synthetic integration-test review; not clinical approval.",
        language_reviewed="en",
    )

    db.commit()

    # 4. Verify the immutable version and its review snapshot.
    version = db.scalar(
        select(DocumentVersion).where(
            DocumentVersion.document_id == context["document_id"],
            DocumentVersion.version_number == 1,
        )
    )

    assert version is not None
    assert version.content == prepared.content
    assert version.review_snapshot is not None
    assert version.review_snapshot["source_last_verified_at"] is not None

    # 5. Verify the persistent clinical review.
    persisted_review = db.get(DBReview, review.id)

    assert persisted_review is not None
    assert persisted_review.reviewer_id == "integration-reviewer"
    assert persisted_review.decision == "approved"
    assert persisted_review.language == "en"

    # 6. Verify the audit event.
    audit = db.scalar(
        select(KnowledgeAuditEvent).where(
            KnowledgeAuditEvent.entity_type == "knowledge_document",
            KnowledgeAuditEvent.entity_id == str(context["document_id"]),
            KnowledgeAuditEvent.event_type == "clinical_review_recorded",
        )
    )

    assert audit is not None
    assert audit.actor_id == "integration-reviewer"

    audit_details = json.loads(audit.details)

    assert audit_details["decision"] == "approved"
    assert audit_details["version_number"] == 1

    # 7. Verify that the database document is approved.
    db.refresh(db_document)

    assert db_document.status == "approved"

    # 8. Retrieve the approved document through persistent retrieval.
    retriever = PersistentKnowledgeRetriever(db)

    results = retriever.retrieve(
        query="synthetic educational content",
        language="en",
        limit=10,
    )

    matching_results = [
        result
        for result in results
        if result.document_id == context["document_id"]
    ]

    assert len(matching_results) == 1
    assert matching_results[0].content == prepared.content
    assert matching_results[0].version_number == 1

    # 9. Change the source verification timestamp.
    db_source = db.get(DBSource, context["source_id"])

    assert db_source is not None

    db_source.last_verified_at = (
        datetime.now(timezone.utc) + timedelta(days=1)
    )
    db.commit()

    # 10. Previously approved content must now be excluded.
    results_after_change = retriever.retrieve(
        query="HIV prevention",
        language="en",
        limit=10,
    )

    matching_after_change = [
        result
        for result in results_after_change
        if result.document_id == context["document_id"]
    ]

    assert matching_after_change == []
