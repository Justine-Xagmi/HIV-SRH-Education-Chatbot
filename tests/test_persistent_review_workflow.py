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
    """Ensure the normal document-version immutability trigger exists."""
    # Avoid CREATE TRIGGER failing when the trigger already exists.
    drop_immutability_trigger(db)
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

    try:
        db_source = DBSource(
            name=source_name,
            organization="Synthetic Test Organization",
            source_url=f"https://example.org/test-source-{suffix}",
            source_type="synthetic_test",
            language="en",
            permission_status="permitted",
            is_active=True,
            last_verified_at=datetime.now(timezone.utc),
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
            last_verified_at=datetime.now(timezone.utc),
            permission_status="permitted",
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
                {"document_id": str(locals().get("db_document").id)}
                if locals().get("db_document") is not None
                else {"document_id": "-1"},
            )

            if locals().get("db_document") is not None:
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
                        "DELETE FROM knowledge_documents WHERE id = :document_id"
                    ),
                    {"document_id": db_document.id},
                )

            if locals().get("db_source") is not None:
                db.execute(
                    text("DELETE FROM health_sources WHERE id = :source_id"),
                    {"source_id": db_source.id},
                )

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

    # Authorize the reviewer so the self-review safeguard is reached.
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

    # This test deliberately simulates an inconsistent legacy database
    # state. Use a savepoint so the altered snapshot is rolled back.
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

        # Restore the normal trigger after rolling back the simulated state.
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

    # Simulate a legacy version without a snapshot. This mutation is
    # test-only; the immutability trigger is restored immediately after.
    try:
        drop_immutability_trigger(db)
        version.review_snapshot = None
        db.commit()
    finally:
        restore_immutability_trigger(db)
        db.commit()

    with pytest.raises(ValueError, match="no review snapshot"):
        call_review(context, workflow)


def test_outer_transaction_rollback_removes_review_and_audit(
    review_test_context,
):
    context = review_test_context
    db = context["db"]
    workflow = make_workflow(context)

    call_review(context, workflow)

    # The workflow must not commit the caller's outer transaction.
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


from app.knowledge.persistent_retrieval import PersistentKnowledgeRetriever


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

    # Create a newer version with synthetic content and reject it.
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

    version = db.scalar(
        select(DocumentVersion).where(
            DocumentVersion.document_id == context["document_id"],
            DocumentVersion.version_number == 1,
        )
    )
    assert version is not None

    # Create a newer legacy-style version without a review snapshot or review.
    # The database permits inserts; existing versions remain immutable.
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

    # Simulate a source metadata change after review.
    source.organization = "Unexpected Synthetic Organization"
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

    # The fixture supplies one approved document. A limit of one should
    # return that document, while a limit of zero should return no results.
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
