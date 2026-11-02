
from datetime import date, datetime, timezone

import pytest

from app.knowledge.models import HealthSource, KnowledgeDocument
from app.knowledge.review_workflow import (
    ClinicalReviewWorkflow,
    document_fingerprint,
)


def make_document() -> KnowledgeDocument:
    source = HealthSource(
        source_id="source-review-test",
        title="Example educational source",
        organization="Example Organization",
        url="https://example.org/health",
        language="en",
        version="1.0",
        publication_date=date(2025, 1, 1),
        last_verified_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
        permission_status="permitted",
        permission_basis="Synthetic permission evidence for automated tests.",
        permission_reference="TEST-PERMISSION-001",
        permission_checked_at=datetime(
            2026, 10, 1, tzinfo=timezone.utc
        ),
        permission_checked_by="test-permission-reviewer",
        permission_notes=(
            "Test fixture only; not evidence of real-world permission."
        ),
    )

    return KnowledgeDocument(
        document_id="document-review-test",
        source=source,
        title="Educational HIV information",
        content="Sample educational content awaiting review.",
        language="en",
        topics=["hiv_prevention"],
    )


def test_no_reviewer_is_authorized_by_default():
    workflow = ClinicalReviewWorkflow()

    with pytest.raises(PermissionError, match="not authorized"):
        workflow.review(
            make_document(),
            reviewer_id="reviewer-1",
            preparer_id="preparer-1",
            decision="approved",
            rationale="Reviewed.",
            language_reviewed="en",
        )


def test_unauthorized_reviewer_cannot_approve():
    workflow = ClinicalReviewWorkflow(
        authorized_reviewer_ids={"authorized-reviewer"}
    )

    with pytest.raises(PermissionError, match="not authorized"):
        workflow.review(
            make_document(),
            reviewer_id="other-reviewer",
            preparer_id="preparer-1",
            decision="approved",
            rationale="Reviewed.",
            language_reviewed="en",
        )


def test_preparer_cannot_approve_own_submission():
    workflow = ClinicalReviewWorkflow(
        authorized_reviewer_ids={"reviewer-1"}
    )

    with pytest.raises(PermissionError, match="own submissions"):
        workflow.review(
            make_document(),
            reviewer_id="reviewer-1",
            preparer_id="reviewer-1",
            decision="approved",
            rationale="Reviewed.",
            language_reviewed="en",
        )


def test_approval_records_evidence_and_version():
    workflow = ClinicalReviewWorkflow(
        authorized_reviewer_ids={"reviewer-1"}
    )
    document = make_document()

    approved = workflow.review(
        document,
        reviewer_id="reviewer-1",
        preparer_id="preparer-1",
        decision="approved",
        rationale="Content reviewed against the cited source.",
        language_reviewed="en",
    )

    records = workflow.records_for(document.document_id)

    assert approved.review_status == "approved"
    assert approved.source.review_status == "approved"
    assert approved.reviewed_by == "reviewer-1"
    assert len(records) == 1
    assert records[0].decision == "approved"
    assert records[0].content_fingerprint == document_fingerprint(document)
    assert records[0].rationale == "Content reviewed against the cited source."
    assert workflow.is_approval_current(document)


def test_changed_content_invalidates_version_approval():
    workflow = ClinicalReviewWorkflow(
        authorized_reviewer_ids={"reviewer-1"}
    )
    document = make_document()

    workflow.review(
        document,
        reviewer_id="reviewer-1",
        preparer_id="preparer-1",
        decision="approved",
        rationale="Reviewed.",
        language_reviewed="en",
    )

    changed_document = document.model_copy(
        update={"content": "Changed content requiring a new review."}
    )

    assert not workflow.is_approval_current(changed_document)


def test_changes_requested_does_not_create_current_approval():
    workflow = ClinicalReviewWorkflow(
        authorized_reviewer_ids={"reviewer-1"}
    )
    document = make_document()

    result = workflow.review(
        document,
        reviewer_id="reviewer-1",
        preparer_id="preparer-1",
        decision="changes_requested",
        rationale="Update the source reference and clarify wording.",
        language_reviewed="en",
    )

    assert result.review_status == "pending_review"
    assert result.source.review_status == "pending_review"
    assert not workflow.is_approval_current(document)
    assert workflow.records_for(document.document_id)[0].decision == (
        "changes_requested"
    )


def test_rejection_is_recorded_and_not_approved():
    workflow = ClinicalReviewWorkflow(
        authorized_reviewer_ids={"reviewer-1"}
    )
    document = make_document()

    result = workflow.review(
        document,
        reviewer_id="reviewer-1",
        preparer_id="preparer-1",
        decision="rejected",
        rationale="The evidence is insufficient.",
        language_reviewed="en",
    )

    assert result.review_status != "approved"
    assert result.source.review_status != "approved"
    assert not workflow.is_approval_current(document)
    assert workflow.records_for(document.document_id)[0].decision == "rejected"


def test_review_language_must_match_document_language():
    workflow = ClinicalReviewWorkflow(
        authorized_reviewer_ids={"reviewer-1"}
    )

    with pytest.raises(ValueError, match="must match"):
        workflow.review(
            make_document(),
            reviewer_id="reviewer-1",
            preparer_id="preparer-1",
            decision="approved",
            rationale="Reviewed.",
            language_reviewed="sw",
        )


def test_review_requires_nonblank_rationale():
    workflow = ClinicalReviewWorkflow(
        authorized_reviewer_ids={"reviewer-1"}
    )

    with pytest.raises(ValueError, match="rationale is required"):
        workflow.review(
            make_document(),
            reviewer_id="reviewer-1",
            preparer_id="preparer-1",
            decision="approved",
            rationale="   ",
            language_reviewed="en",
        )


def test_multiple_decisions_are_preserved_in_history():
    workflow = ClinicalReviewWorkflow(
        authorized_reviewer_ids={"reviewer-1"}
    )
    document = make_document()

    workflow.review(
        document,
        reviewer_id="reviewer-1",
        preparer_id="preparer-1",
        decision="changes_requested",
        rationale="Please revise the explanation.",
        language_reviewed="en",
    )

    workflow.review(
        document,
        reviewer_id="reviewer-1",
        preparer_id="preparer-1",
        decision="approved",
        rationale="The revised version has been reviewed.",
        language_reviewed="en",
    )

    records = workflow.records_for(document.document_id)

    assert len(records) == 2
    assert records[0].decision == "changes_requested"
    assert records[1].decision == "approved"


def test_source_permission_change_invalidates_approval():
    document = make_document()
    changed_source = document.source.model_copy(
        update={"permission_status": "restricted"}
    )
    changed_document = document.model_copy(
        update={"source": changed_source}
    )

    assert document_fingerprint(changed_document) != document_fingerprint(
        document
    )


def test_source_verification_timestamp_change_invalidates_approval():
    document = make_document()
    changed_source = document.source.model_copy(
        update={
            "last_verified_at": datetime(
                2026, 10, 2, tzinfo=timezone.utc
            )
        }
    )
    changed_document = document.model_copy(
        update={"source": changed_source}
    )

    assert document_fingerprint(changed_document) != document_fingerprint(
        document
    )


def test_missing_source_verification_timestamp_changes_fingerprint():
    document = make_document()
    changed_source = document.source.model_copy(
        update={"last_verified_at": None}
    )
    changed_document = document.model_copy(
        update={"source": changed_source}
    )

    assert document_fingerprint(changed_document) != document_fingerprint(
        document
    )
