
import json
import uuid
from datetime import date, datetime, timezone

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
from app.knowledge.models import HealthSource, KnowledgeDocument
from app.knowledge.persistent_review_workflow import (
    PersistentClinicalReviewWorkflow,
    build_review_snapshot,
)
from app.knowledge.persistent_retrieval import PersistentKnowledgeRetriever


IMMUTABILITY_TRIGGER = "trg_document_versions_immutable"


def drop_immutability_trigger(db):
    """Drop the version immutability trigger for isolated test setup/cleanup."""
    db.execute(
        text(
            f"DROP TRIGGER IF EXISTS {IMMUTABILITY_TRIGGER} "
            "ON document_versions"
        )
    )


def restore_immutability_trigger(db):
    """Create the immutability trigger only when it is missing."""
    trigger_exists = db.execute(
        text(
            """
            SELECT EXISTS (
                SELECT 1
                FROM pg_trigger
                WHERE tgname = :trigger_name
                  AND tgrelid = to_regclass('public.document_versions')
                  AND NOT tgisinternal
            )
            """
        ),
        {"trigger_name": IMMUTABILITY_TRIGGER},
    ).scalar_one()

    if not trigger_exists:
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


@pytest.fixture
def review_test_context():
    """Create isolated database records for persistent-review tests."""
    if SessionLocal is None:
        pytest.skip("DATABASE_URL is not configured.")

    db = SessionLocal()
    suffix = uuid.uuid4().hex[:12]

    source_name = f"Test source {suffix}"
    document_title = f"Test document {suffix}"
    verified_at = datetime.now(timezone.utc)

    try:
        db_source = DBSource(
            name=source_name,
            organization="Synthetic Test Organization",
            source_url=f"https://example.org/test-source-{suffix}",
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
            title=document_title,
            topic="sexual_health",
            language="en",
            status="pending_review",
        )
        db.add(db_document)
        db.commit()

        source = HealthSource(
            source_id=f"test-source-{suffix}",
            title=source_name,
            organization="Synthetic Test Organization",
            url=f"https://example.org/test-source-{suffix}",
            language="en",
            review_status="pending_review",
            reviewed_by=None,
            reviewed_at=None,
            version="1.0",
            publication_date=date(2025, 1, 1),
            last_verified_at=verified_at,
            permission_status="permitted",
            permission_basis=(
                "Synthetic permission evidence for automated testing."
            ),
            permission_reference="TEST-PERMISSION-001",
            permission_checked_at=verified_at,
            permission_checked_by="persistent-review-test-reviewer",
            permission_notes=(
                "Test fixture only; not evidence of real-world permission."
            ),
        )

        document = KnowledgeDocument(
            document_id=f"test-document-{suffix}",
            source=source,
            title=document_title,
            content=(
                "Synthetic test content for verifying the persistent "
                "review workflow. This is not clinical guidance."
            ),
            language="en",
            topics=["sexual_health", "hiv_testing"],
            ingestion_status="validated",
            review_status="pending_review",
            reviewed_by=None,
            reviewed_at=None,
            updated_at=datetime.now(timezone.utc),
        )

        context = {
            "db": db,
            "source_id": db_source.id,
            "document_id": db_document.id,
            "source": source,
            "document": document,
        }

        yield context

    finally:
        try:
            db.rollback()

            # Test-only cleanup: immutable versions must be removed to
            # delete the test document and its associated records.
            drop_immutability_trigger(db)

            db.execute(
                text(
                    """
                    DELETE FROM knowledge_audit_events
                    WHERE entity_type = 'knowledge_document'
                      AND entity_id = :document_id
                    """
                ),
                {"document_id": str(db_document.id)}
                if "db_document" in locals()
                else {"document_id": "-1"},
            )

            if "db_document" in locals():
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
                        "DELETE FROM document_versions "
                        "WHERE document_id = :document_id"
                    ),
                    {"document_id": db_document.id},
                )

                db.execute(
                    text(
                        "DELETE FROM knowledge_documents "
                        "WHERE id = :document_id"
                    ),
                    {"document_id": db_document.id},
                )

            if "db_source" in locals():
                db.execute(
                    text("DELETE FROM health_sources WHERE id = :source_id"),
                    {"source_id": db_source.id},
                )

            # Restore the trigger in the same transaction as cleanup.
            restore_immutability_trigger(db)
            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()


def make_workflow(context, authorized=None):
    """Create a workflow with an explicit reviewer allowlist."""
    if authorized is None:
        authorized = {"reviewer-test"}

    return PersistentClinicalReviewWorkflow(
        context["db"],
        authorized_reviewer_ids=authorized,
    )


def call_review(context, workflow, **overrides):
    """Submit a review using the fixture's document and database ID."""
    arguments = {
        "database_document_id": context["document_id"],
        "version_number": 1,
        "reviewer_id": "reviewer-test",
        "preparer_id": "preparer-test",
        "decision": "approved",
        "rationale": "Synthetic test rationale; not clinical approval.",
        "language_reviewed": context["document"].language,
    }
    arguments.update(overrides)

    return workflow.record_review(context["document"], **arguments)


def test_approved_review_persists_version_review_and_audit(
    review_test_context,
):
    context = review_test_context
    db = context["db"]
    workflow = make_workflow(context)

    review = call_review(context, workflow)
    db.commit()

    version = db.scalar(
        select(DocumentVersion).where(
            DocumentVersion.document_id == context["document_id"],
            DocumentVersion.version_number == 1,
        )
    )
    assert version is not None
    assert version.content == context["document"].content
    assert len(version.content_fingerprint) == 64

    assert version.review_snapshot is not None
    assert version.review_snapshot["document_id"] == context["document"].document_id
    assert version.review_snapshot["title"] == context["document"].title
    assert version.review_snapshot["content_fingerprint"] == version.content_fingerprint
    assert version.review_snapshot["language"] == context["document"].language
    assert version.review_snapshot["topics"] == sorted(context["document"].topics)
    assert version.review_snapshot["source_id"] == context["document"].source.source_id
    assert version.review_snapshot["source_url"] == str(context["document"].source.url)
    assert version.review_snapshot["source_version"] == context["document"].source.version

    stored_review = db.get(DBReview, review.id)
    assert stored_review is not None
    assert stored_review.decision == "approved"
    assert stored_review.reviewer_id == "reviewer-test"
    assert stored_review.document_version_id == version.id

    db_document = db.get(DBDocument, context["document_id"])
    assert db_document is not None
    assert db_document.status == "approved"

    audit = db.scalar(
        select(KnowledgeAuditEvent).where(
            KnowledgeAuditEvent.entity_id == str(context["document_id"]),
            KnowledgeAuditEvent.event_type == "clinical_review_recorded",
        )
    )
    assert audit is not None
    assert audit.actor_id == "reviewer-test"

    details = json.loads(audit.details)
    assert details["decision"] == "approved"
    assert details["version_number"] == 1
    assert details["content_fingerprint"] == version.content_fingerprint


def test_no_reviewer_is_authorized_by_default(review_test_context):
    context = review_test_context
    workflow = make_workflow(context, authorized=set())

    with pytest.raises(PermissionError, match="not authorized"):
        call_review(context, workflow)


def test_unauthorized_reviewer_is_rejected(review_test_context):
    context = review_test_context
    workflow = make_workflow(context, authorized={"another-reviewer"})

    with pytest.raises(PermissionError, match="not authorized"):
        call_review(context, workflow, reviewer_id="reviewer-test")


def test_preparer_cannot_review_own_submission(review_test_context):
    context = review_test_context

    workflow = make_workflow(
        context,
        authorized={"reviewer-test", "preparer-test"},
    )

    with pytest.raises(PermissionError, match="own submissions"):
        call_review(
            context,
            workflow,
            reviewer_id="preparer-test",
            preparer_id="preparer-test",
        )


def test_review_language_must_match_document(review_test_context):
    context = review_test_context
    workflow = make_workflow(context)

    with pytest.raises(ValueError, match="language"):
        call_review(context, workflow, language_reviewed="sw")


def test_source_permission_must_be_permitted_for_approval(
    review_test_context,
):
    context = review_test_context
    db = context["db"]
    db_source = db.get(DBSource, context["source_id"])
    assert db_source is not None

    db_source.permission_status = "pending"
    db.commit()

    workflow = make_workflow(context)

    with pytest.raises(ValueError, match="permission status"):
        call_review(context, workflow)


def test_inactive_source_cannot_be_approved(review_test_context):
    context = review_test_context
    db = context["db"]
    db_source = db.get(DBSource, context["source_id"])
    assert db_source is not None

    db_source.is_active = False
    db.commit()

    workflow = make_workflow(context)

    with pytest.raises(ValueError, match="Inactive sources"):
        call_review(context, workflow)


def test_existing_version_cannot_be_reused_for_different_content(
    review_test_context,
):
    context = review_test_context
    db = context["db"]
    workflow = make_workflow(context)

    call_review(context, workflow)
    db.commit()

    changed_document = context["document"].model_copy(
        update={"content": "Different synthetic content."}
    )

    with pytest.raises(ValueError, match="different content"):
        workflow.record_review(
            changed_document,
            database_document_id=context["document_id"],
            version_number=1,
            reviewer_id="reviewer-test",
            preparer_id="preparer-test",
            decision="approved",
            rationale="Synthetic test rationale.",
            language_reviewed=changed_document.language,
        )


def test_existing_version_rejects_changed_review_snapshot_metadata(
    review_test_context,
):
    context = review_test_context
    db = context["db"]
    workflow = make_workflow(context)

    call_review(context, workflow)
    db.commit()

    version = db.scalar(
        select(DocumentVersion).where(
            DocumentVersion.document_id == context["document_id"],
            DocumentVersion.version_number == 1,
        )
    )
    assert version is not None
    assert version.review_snapshot is not None

    # Simulate an inconsistent legacy database state for this test.
    savepoint = db.begin_nested()

    try:
        drop_immutability_trigger(db)

        altered_snapshot = dict(version.review_snapshot)
        altered_snapshot["source_title"] = "Unexpected source title"
        version.review_snapshot = altered_snapshot
        db.flush()

        with pytest.raises(ValueError, match="snapshot differs"):
            call_review(context, workflow)

    finally:
        if savepoint.is_active:
            savepoint.rollback()

        db.expire_all()

        # The savepoint rollback may already have restored the trigger.
        restore_immutability_trigger(db)
        db.commit()


def test_legacy_version_without_snapshot_is_rejected(review_test_context):
    context = review_test_context
    db = context["db"]
    workflow = make_workflow(context)

    call_review(context, workflow)
    db.commit()

    version = db.scalar(
        select(DocumentVersion).where(
            DocumentVersion.document_id == context["document_id"],
            DocumentVersion.version_number == 1,
        )
    )
    assert version is not None

    try:
        drop_immutability_trigger(db)
        version.review_snapshot = None
        db.flush()

        # Restore the trigger before committing the test mutation.
        restore_immutability_trigger(db)
        db.commit()

    except Exception:
        db.rollback()
        raise

    with pytest.raises(ValueError, match="no review snapshot"):
        call_review(context, workflow)


def test_outer_transaction_rollback_removes_review_and_audit(
    review_test_context,
):
    context = review_test_context
    db = context["db"]
    workflow = make_workflow(context)

    call_review(context, workflow)
    db.rollback()

    version = db.scalar(
        select(DocumentVersion).where(
            DocumentVersion.document_id == context["document_id"],
            DocumentVersion.version_number == 1,
        )
    )
    review = db.scalar(
        select(DBReview).where(
            DBReview.document_version_id == (
                version.id if version is not None else -1
            )
        )
    )
    audit = db.scalar(
        select(KnowledgeAuditEvent).where(
            KnowledgeAuditEvent.entity_id == str(context["document_id"]),
            KnowledgeAuditEvent.event_type == "clinical_review_recorded",
        )
    )

    assert version is None
    assert review is None
    assert audit is None


def test_build_review_snapshot_contains_source_metadata(
    review_test_context,
):
    document = review_test_context["document"]
    snapshot = build_review_snapshot(document)

    assert snapshot["document_id"] == document.document_id
    assert snapshot["title"] == document.title
    assert snapshot["content_fingerprint"]
    assert snapshot["source_id"] == document.source.source_id
    assert snapshot["source_title"] == document.source.title
    assert snapshot["source_organization"] == document.source.organization
    assert snapshot["source_url"] == str(document.source.url)
    assert snapshot["source_language"] == document.source.language
    assert snapshot["source_version"] == document.source.version
    assert snapshot["source_permission_status"] == (
        document.source.permission_status
    )


def test_retriever_returns_currently_approved_document(review_test_context):
    context = review_test_context
    db = context["db"]

    workflow = make_workflow(context)
    call_review(context, workflow)
    db.commit()

    retriever = PersistentKnowledgeRetriever(db)
    results = retriever.retrieve("synthetic test content", "en")

    assert len(results) == 1
    assert results[0].document_id == context["document_id"]
    assert results[0].version_number == 1
    assert results[0].content == context["document"].content


def test_retriever_excludes_document_when_latest_version_is_rejected(
    review_test_context,
):
    context = review_test_context
    db = context["db"]

    workflow = make_workflow(context)
    call_review(context, workflow)
    db.commit()

    changed_document = context["document"].model_copy(
        update={
            "content": (
                "Synthetic revised content about testing retrieval. "
                "This is not clinical guidance."
            )
        }
    )

    workflow.record_review(
        changed_document,
        database_document_id=context["document_id"],
        version_number=2,
        reviewer_id="reviewer-test",
        preparer_id="preparer-test",
        decision="rejected",
        rationale="Synthetic rejection for a retrieval test.",
        language_reviewed="en",
    )
    db.commit()

    retriever = PersistentKnowledgeRetriever(db)
    results = retriever.retrieve("synthetic content", "en")

    assert results == []


def test_retriever_excludes_document_without_review_snapshot(
    review_test_context,
):
    context = review_test_context
    db = context["db"]

    workflow = make_workflow(context)
    call_review(context, workflow)
    db.commit()

    db.add(
        DocumentVersion(
            document_id=context["document_id"],
            version_number=2,
            content=(
                "Synthetic newer content without approval evidence. "
                "This is not clinical guidance."
            ),
            content_fingerprint="a" * 64,
            review_snapshot=None,
        )
    )
    db.commit()

    retriever = PersistentKnowledgeRetriever(db)
    results = retriever.retrieve("synthetic content", "en")

    assert results == []


def test_retriever_excludes_document_when_source_metadata_changes(
    review_test_context,
):
    context = review_test_context
    db = context["db"]

    workflow = make_workflow(context)
    call_review(context, workflow)
    db.commit()

    source = db.get(DBSource, context["source_id"])
    assert source is not None

    source.organization = "Unexpected Synthetic Organization"
    db.commit()

    retriever = PersistentKnowledgeRetriever(db)
    results = retriever.retrieve("synthetic test content", "en")

    assert results == []


def test_retriever_excludes_document_when_source_verification_timestamp_changes(
    review_test_context,
):
    context = review_test_context
    db = context["db"]

    workflow = make_workflow(context)
    call_review(context, workflow)
    db.commit()

    source = db.get(DBSource, context["source_id"])
    assert source is not None

    # Simulate a source verification timestamp change after approval.
    source.last_verified_at = datetime(2020, 1, 1, tzinfo=timezone.utc)
    db.commit()

    retriever = PersistentKnowledgeRetriever(db)
    results = retriever.retrieve("synthetic test content", "en")

    assert results == []


def test_retriever_respects_requested_language(review_test_context):
    context = review_test_context
    db = context["db"]

    workflow = make_workflow(context)
    call_review(context, workflow)
    db.commit()

    retriever = PersistentKnowledgeRetriever(db)

    english_results = retriever.retrieve("synthetic test content", "en")
    swahili_results = retriever.retrieve("synthetic test content", "sw")

    assert len(english_results) == 1
    assert english_results[0].language == "en"
    assert swahili_results == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("is_active", False),
        ("permission_status", "restricted"),
    ],
)
def test_retriever_excludes_ineligible_source(
    review_test_context, field, value
):
    context = review_test_context
    db = context["db"]

    workflow = make_workflow(context)
    call_review(context, workflow)
    db.commit()

    source = db.get(DBSource, context["source_id"])
    assert source is not None

    setattr(source, field, value)
    db.commit()

    retriever = PersistentKnowledgeRetriever(db)
    results = retriever.retrieve("synthetic test content", "en")

    assert results == []


def test_retriever_respects_result_limit(review_test_context):
    context = review_test_context
    db = context["db"]

    workflow = make_workflow(context)
    call_review(context, workflow)
    db.commit()

    retriever = PersistentKnowledgeRetriever(db)

    one_result = retriever.retrieve(
        "synthetic test content",
        "en",
        limit=1,
    )
    no_results = retriever.retrieve(
        "synthetic test content",
        "en",
        limit=0,
    )

    assert len(one_result) == 1
    assert no_results == []


@pytest.mark.parametrize(
    "field",
    [
        "source_title",
        "source_organization",
        "source_url",
    ],
)
def test_retriever_excludes_document_when_required_snapshot_field_is_missing(
    review_test_context, field
):
    context = review_test_context
    db = context["db"]

    workflow = make_workflow(context)
    call_review(context, workflow)
    db.commit()

    version = db.scalar(
        select(DocumentVersion).where(
            DocumentVersion.document_id == context["document_id"],
            DocumentVersion.version_number == 1,
        )
    )
    assert version is not None
    assert isinstance(version.review_snapshot, dict)

    try:
        drop_immutability_trigger(db)

        altered_snapshot = dict(version.review_snapshot)
        altered_snapshot.pop(field)
        version.review_snapshot = altered_snapshot
        db.flush()

        restore_immutability_trigger(db)
        db.commit()

    except Exception:
        db.rollback()
        raise

    results = PersistentKnowledgeRetriever(db).retrieve(
        "synthetic test content", "en"
    )
    assert results == []


def test_retriever_excludes_document_with_non_dictionary_snapshot(
    review_test_context,
):
    context = review_test_context
    db = context["db"]

    workflow = make_workflow(context)
    call_review(context, workflow)
    db.commit()

    version = db.scalar(
        select(DocumentVersion).where(
            DocumentVersion.document_id == context["document_id"],
            DocumentVersion.version_number == 1,
        )
    )
    assert version is not None

    try:
        drop_immutability_trigger(db)
        version.review_snapshot = ["malformed", "snapshot"]
        db.flush()

        restore_immutability_trigger(db)
        db.commit()

    except Exception:
        db.rollback()
        raise

    results = PersistentKnowledgeRetriever(db).retrieve(
        "synthetic test content", "en"
    )
    assert results == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("document_id", ""),
        ("source_id", ""),
        ("document_id", "different-document-id"),
        ("source_id", "different-source-id"),
    ],
)
def test_retriever_excludes_document_with_invalid_snapshot_identifiers(
    review_test_context, field, value
):
    context = review_test_context
    db = context["db"]

    workflow = make_workflow(context)
    call_review(context, workflow)
    db.commit()

    version = db.scalar(
        select(DocumentVersion).where(
            DocumentVersion.document_id == context["document_id"],
            DocumentVersion.version_number == 1,
        )
    )
    assert version is not None
    assert isinstance(version.review_snapshot, dict)

    try:
        drop_immutability_trigger(db)

        altered_snapshot = dict(version.review_snapshot)
        altered_snapshot[field] = value
        version.review_snapshot = altered_snapshot
        db.flush()

        restore_immutability_trigger(db)
        db.commit()

    except Exception:
        db.rollback()
        raise

    results = PersistentKnowledgeRetriever(db).retrieve(
        "synthetic test content", "en"
    )
    assert results == []


@pytest.mark.parametrize(
    "timestamp_value",
    [
        None,
        "not-a-valid-timestamp",
        "2025-01-01T12:00:00",
    ],
)
def test_retriever_excludes_document_with_invalid_snapshot_timestamp(
    review_test_context, timestamp_value
):
    context = review_test_context
    db = context["db"]

    workflow = make_workflow(context)
    call_review(context, workflow)
    db.commit()

    version = db.scalar(
        select(DocumentVersion).where(
            DocumentVersion.document_id == context["document_id"],
            DocumentVersion.version_number == 1,
        )
    )
    assert version is not None
    assert isinstance(version.review_snapshot, dict)

    try:
        drop_immutability_trigger(db)

        altered_snapshot = dict(version.review_snapshot)
        altered_snapshot["source_last_verified_at"] = timestamp_value
        version.review_snapshot = altered_snapshot
        db.flush()

        restore_immutability_trigger(db)
        db.commit()

    except Exception:
        db.rollback()
        raise

    results = PersistentKnowledgeRetriever(db).retrieve(
        "synthetic test content", "en"
    )
    assert results == []


def test_retriever_excludes_document_when_stored_review_language_changes(
    review_test_context,
):
    context = review_test_context
    db = context["db"]

    workflow = make_workflow(context)
    review = call_review(context, workflow)
    db.commit()

    stored_review = db.get(DBReview, review.id)
    assert stored_review is not None

    stored_review.language = "sw"
    db.commit()

    results = PersistentKnowledgeRetriever(db).retrieve(
        "synthetic test content", "en"
    )
    assert results == []


@pytest.mark.parametrize(
    "latest_decision",
    ["rejected", "changes_requested"],
)
def test_latest_non_approval_on_same_version_blocks_retrieval(
    review_test_context,
    latest_decision,
):
    context = review_test_context
    db = context["db"]
    workflow = make_workflow(context)

    first_review = call_review(context, workflow, decision="approved")
    db.commit()

    second_review = call_review(
        context,
        workflow,
        decision=latest_decision,
        rationale=f"Synthetic follow-up decision: {latest_decision}.",
    )
    db.commit()

    assert first_review.document_version_id == second_review.document_version_id

    results = PersistentKnowledgeRetriever(db).retrieve(
        "synthetic test content", "en"
    )

    assert results == []


def test_latest_approval_on_same_version_restores_retrieval(
    review_test_context,
):
    context = review_test_context
    db = context["db"]
    workflow = make_workflow(context)

    first_review = call_review(context, workflow, decision="rejected")
    db.commit()

    second_review = call_review(
        context,
        workflow,
        decision="approved",
        rationale="Synthetic follow-up approval for testing.",
    )
    db.commit()

    assert first_review.document_version_id == second_review.document_version_id

    results = PersistentKnowledgeRetriever(db).retrieve(
        "synthetic test content", "en"
    )

    assert len(results) == 1
    assert results[0].version_number == 1
    assert results[0].content == context["document"].content


def test_multiple_reviews_preserve_complete_history_for_same_version(
    review_test_context,
):
    context = review_test_context
    db = context["db"]
    workflow = make_workflow(context)

    first_review = call_review(
        context,
        workflow,
        decision="approved",
        rationale="First synthetic review.",
    )
    db.commit()

    second_review = call_review(
        context,
        workflow,
        decision="changes_requested",
        rationale="Second synthetic review.",
    )
    db.commit()

    third_review = call_review(
        context,
        workflow,
        decision="approved",
        rationale="Third synthetic review.",
    )
    db.commit()

    assert (
        first_review.document_version_id
        == second_review.document_version_id
        == third_review.document_version_id
    )

    stored_reviews = db.scalars(
        select(DBReview)
        .where(
            DBReview.document_version_id
            == first_review.document_version_id
        )
        .order_by(DBReview.id.asc())
    ).all()

    assert len(stored_reviews) == 3
    assert [review.decision for review in stored_reviews] == [
        "approved",
        "changes_requested",
        "approved",
    ]
    assert [review.rationale for review in stored_reviews] == [
        "First synthetic review.",
        "Second synthetic review.",
        "Third synthetic review.",
    ]
    assert all(
        review.reviewer_id == "reviewer-test"
        for review in stored_reviews
    )
    assert all(
        review.language == "en"
        for review in stored_reviews
    )

    db_document = db.get(DBDocument, context["document_id"])
    assert db_document is not None
    assert db_document.status == "approved"


def test_equal_review_timestamps_use_highest_review_id_as_tiebreaker(
    review_test_context,
):
    context = review_test_context
    db = context["db"]
    workflow = make_workflow(context)

    first_review = call_review(
        context,
        workflow,
        decision="approved",
    )
    second_review = call_review(
        context,
        workflow,
        decision="rejected",
    )

    same_timestamp = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)

    first_review.reviewed_at = same_timestamp
    second_review.reviewed_at = same_timestamp
    db.commit()

    assert first_review.id < second_review.id
    assert (
        first_review.document_version_id
        == second_review.document_version_id
    )

    latest_review = PersistentKnowledgeRetriever(db)._latest_review(
        first_review.document_version_id
    )

    assert latest_review is not None
    assert latest_review.id == second_review.id
    assert latest_review.decision == "rejected"

    results = PersistentKnowledgeRetriever(db).retrieve(
        "synthetic test content", "en"
    )
    assert results == []


@pytest.mark.parametrize(
    ("latest_decision", "document_status"),
    [
        ("approved", "pending_review"),
        ("rejected", "approved"),
        ("changes_requested", "approved"),
    ],
)
def test_retriever_fails_closed_when_document_status_disagrees_with_latest_review(
    review_test_context,
    latest_decision,
    document_status,
):
    context = review_test_context
    db = context["db"]
    workflow = make_workflow(context)

    review = call_review(
        context,
        workflow,
        decision=latest_decision,
    )
    db.commit()

    db_document = db.get(DBDocument, context["document_id"])
    assert db_document is not None

    # Simulate inconsistent persisted state.
    db_document.status = document_status
    db.commit()

    latest_review = PersistentKnowledgeRetriever(db)._latest_review(
        review.document_version_id
    )

    assert latest_review is not None
    assert latest_review.decision == latest_decision

    results = PersistentKnowledgeRetriever(db).retrieve(
        "synthetic test content", "en"
    )

    assert results == []
