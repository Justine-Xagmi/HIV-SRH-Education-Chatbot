
from datetime import date, datetime, timezone

import pytest

from app.knowledge.models import HealthSource, KnowledgeDocument
from app.knowledge.registry import KnowledgeRegistry


REVIEWER = "authorized-reviewer"
PREPARER = "content-preparer"


def make_document(
    document_id: str,
    *,
    title: str = "HIV health information",
    content: str = "General information about HIV and health.",
    language: str = "en",
    review_status: str = "approved",
    source_language: str | None = None,
    source_review_status: str = "approved",
) -> KnowledgeDocument:
    actual_source_language = source_language or language

    source = HealthSource(
        source_id=f"source-{document_id}",
        title=f"Official health source for {document_id}",
        organization="Example Health Organization",
        url="https://example.org/health-information",
        language=actual_source_language,
        review_status=source_review_status,
        reviewed_by=(
            "test-reviewer"
            if source_review_status == "approved"
            else None
        ),
        reviewed_at=(
            datetime.now(timezone.utc)
            if source_review_status == "approved"
            else None
        ),
        version="1.0",
        publication_date=date(2025, 1, 1),
        last_verified_at=datetime(
            2026, 10, 1, tzinfo=timezone.utc
        ),
        permission_status="permitted",
        permission_basis=(
            "Synthetic permission evidence for automated testing."
        ),
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
        document_id=document_id,
        source=source,
        title=title,
        content=content,
        language=language,
        review_status=review_status,
        reviewed_by=(
            "test-reviewer" if review_status == "approved" else None
        ),
        reviewed_at=(
            datetime.now(timezone.utc)
            if review_status == "approved"
            else None
        ),
        topics=["hiv_prevention"],
    )


def make_registry() -> KnowledgeRegistry:
    return KnowledgeRegistry(authorized_reviewer_ids={REVIEWER})


def add_approved(
    registry: KnowledgeRegistry,
    document: KnowledgeDocument,
) -> KnowledgeDocument:
    """Register a document and approve it through the review workflow."""
    registry.add_document(document)
    return registry.review_document(
        document.document_id,
        reviewer_id=REVIEWER,
        preparer_id=PREPARER,
        decision="approved",
        rationale="Approved by the test workflow.",
        language_reviewed=document.language,
    )


def test_new_registry_is_empty():
    registry = make_registry()

    assert registry.count() == 0
    assert registry.retrieve("HIV", "en") == []


def test_add_document_increases_count():
    registry = make_registry()
    registry.add_document(make_document("doc-1"))

    assert registry.count() == 1


def test_duplicate_document_id_is_rejected():
    registry = make_registry()
    registry.add_document(make_document("doc-1"))

    with pytest.raises(ValueError, match="Document already exists"):
        registry.add_document(make_document("doc-1"))


def test_retrieve_returns_matching_reviewed_document():
    registry = make_registry()
    add_approved(
        registry,
        make_document(
            "doc-1",
            title="HIV prevention",
            content="HIV prevention and education information.",
        ),
    )

    results = registry.retrieve("HIV prevention", "en")

    assert [item.document_id for item in results] == ["doc-1"]


def test_retrieve_is_case_insensitive():
    registry = make_registry()
    add_approved(
        registry,
        make_document("doc-1", title="HIV Prevention"),
    )

    assert len(registry.retrieve("hiv PREVENTION", "en")) == 1


def test_retrieve_ignores_punctuation():
    registry = make_registry()
    add_approved(registry, make_document("doc-1", title="HIV prevention"))

    assert len(registry.retrieve("HIV, prevention!", "en")) == 1


def test_pending_document_is_not_retrievable():
    registry = make_registry()
    registry.add_document(
        make_document("doc-pending", review_status="pending_review")
    )

    assert registry.retrieve("HIV prevention", "en") == []


def test_approved_status_without_review_record_is_not_enough():
    registry = make_registry()
    registry.add_document(make_document("doc-forged-approved"))

    # add_document resets caller-supplied approval status and evidence.
    assert registry.retrieve("HIV health", "en") == []


def test_document_with_unapproved_source_is_not_retrievable():
    registry = make_registry()
    registry.add_document(
        make_document(
            "doc-unapproved-source",
            source_review_status="pending_review",
        )
    )

    assert registry.retrieve("HIV prevention", "en") == []


def test_documents_in_another_language_are_excluded():
    registry = make_registry()
    add_approved(
        registry,
        make_document(
            "doc-sw",
            title="Kinga dhidi ya VVU",
            content="Taarifa kuhusu kinga dhidi ya VVU.",
            language="sw",
        ),
    )

    assert registry.retrieve("VVU", "en") == []


def test_source_language_must_match_requested_language():
    registry = make_registry()
    registry.add_document(
        make_document(
            "doc-mismatched-language",
            language="en",
            source_language="sw",
        )
    )

    assert registry.retrieve("HIV prevention", "en") == []


def test_unmatched_query_returns_no_results():
    registry = make_registry()
    add_approved(registry, make_document("doc-1"))

    assert registry.retrieve("transportation infrastructure", "en") == []


def test_blank_query_returns_no_results():
    registry = make_registry()
    add_approved(registry, make_document("doc-1"))

    assert registry.retrieve("", "en") == []
    assert registry.retrieve("   ", "en") == []


def test_zero_or_negative_limit_returns_no_results():
    registry = make_registry()
    add_approved(registry, make_document("doc-1"))

    assert registry.retrieve("HIV", "en", limit=0) == []
    assert registry.retrieve("HIV", "en", limit=-1) == []


def test_result_limit_is_respected():
    registry = make_registry()
    for index in range(3):
        add_approved(registry, make_document(f"doc-{index}"))

    assert len(registry.retrieve("HIV health", "en", limit=2)) == 2


def test_more_relevant_document_ranks_first():
    registry = make_registry()
    add_approved(
        registry,
        make_document(
            "doc-general",
            title="General health",
            content="General health information about HIV.",
        ),
    )
    add_approved(
        registry,
        make_document(
            "doc-specific",
            title="HIV prevention",
            content="HIV prevention information and HIV education.",
        ),
    )

    results = registry.retrieve("HIV prevention", "en")

    assert [item.document_id for item in results] == [
        "doc-specific",
        "doc-general",
    ]


def test_only_requested_language_is_returned():
    registry = make_registry()
    add_approved(
        registry,
        make_document("doc-en", title="HIV prevention", language="en"),
    )
    add_approved(
        registry,
        make_document(
            "doc-sw",
            title="Kinga dhidi ya VVU",
            content="Taarifa kuhusu kinga dhidi ya VVU.",
            language="sw",
        ),
    )

    results = registry.retrieve("HIV prevention", "en")

    assert [item.document_id for item in results] == ["doc-en"]


def test_unauthorized_reviewer_cannot_make_document_retrievable():
    registry = make_registry()
    registry.add_document(make_document("doc-unauthorized"))

    with pytest.raises(PermissionError, match="not authorized"):
        registry.review_document(
            "doc-unauthorized",
            reviewer_id="unknown-reviewer",
            preparer_id=PREPARER,
            decision="approved",
            rationale="Attempted approval.",
            language_reviewed="en",
        )

    assert registry.retrieve("HIV health", "en") == []


def test_changed_document_requires_a_new_approval():
    registry = make_registry()
    original = make_document("doc-version")
    add_approved(registry, original)

    changed = original.model_copy(
        update={"content": "Updated HIV education content."}
    )
    registry.update_document(changed)

    assert registry.retrieve("HIV health", "en") == []

    registry.review_document(
        "doc-version",
        reviewer_id=REVIEWER,
        preparer_id=PREPARER,
        decision="approved",
        rationale="The updated version was reviewed.",
        language_reviewed="en",
    )

    assert registry.retrieve("updated HIV education", "en")


def test_review_history_preserves_multiple_decisions():
    registry = make_registry()
    registry.add_document(make_document("doc-history"))

    registry.review_document(
        "doc-history",
        reviewer_id=REVIEWER,
        preparer_id=PREPARER,
        decision="changes_requested",
        rationale="Please revise the wording.",
        language_reviewed="en",
    )
    registry.review_document(
        "doc-history",
        reviewer_id=REVIEWER,
        preparer_id=PREPARER,
        decision="approved",
        rationale="The revised content was reviewed.",
        language_reviewed="en",
    )

    records = registry.review_history("doc-history")

    assert len(records) == 2
    assert records[0].decision == "changes_requested"
    assert records[1].decision == "approved"


def test_changed_source_permission_requires_fresh_approval():
    registry = make_registry()
    original = make_document("doc-permission")
    add_approved(registry, original)

    changed_source = original.source.model_copy(
        update={"permission_status": "restricted"}
    )
    changed_document = original.model_copy(
        update={"source": changed_source}
    )
    registry.update_document(changed_document)

    assert registry.retrieve("HIV health", "en") == []

    with pytest.raises(ValueError):
        registry.review_document(
            "doc-permission",
            reviewer_id=REVIEWER,
            preparer_id=PREPARER,
            decision="approved",
            rationale="Attempted approval of restricted source.",
            language_reviewed="en",
        )

    assert registry.retrieve("HIV health", "en") == []


def test_changed_source_verification_timestamp_requires_fresh_approval():
    registry = make_registry()
    original = make_document("doc-verification")
    add_approved(registry, original)

    changed_source = original.source.model_copy(
        update={
            "last_verified_at": datetime(
                2026, 10, 2, tzinfo=timezone.utc
            )
        }
    )
    changed_document = original.model_copy(
        update={"source": changed_source}
    )
    registry.update_document(changed_document)

    assert registry.retrieve("HIV health", "en") == []


def test_rejected_document_cannot_be_reapproved_without_correction():
    registry = make_registry()
    original = make_document("doc-rejected")
    registry.add_document(original)

    registry.review_document(
        "doc-rejected",
        reviewer_id=REVIEWER,
        preparer_id=PREPARER,
        decision="rejected",
        rationale="The content is not acceptable for use.",
        language_reviewed="en",
    )

    assert registry.retrieve("HIV health", "en") == []

    with pytest.raises(ValueError):
        registry.review_document(
            "doc-rejected",
            reviewer_id=REVIEWER,
            preparer_id=PREPARER,
            decision="approved",
            rationale="Attempted approval without correction.",
            language_reviewed="en",
        )

    assert registry.retrieve("HIV health", "en") == []


def test_retired_source_cannot_be_approved():
    registry = make_registry()
    original = make_document("doc-retired-source")
    registry.add_document(original)

    retired_source = original.source.model_copy(
        update={"review_status": "retired"}
    )
    changed_document = original.model_copy(
        update={"source": retired_source}
    )
    registry.update_document(changed_document)

    with pytest.raises(ValueError):
        registry.review_document(
            "doc-retired-source",
            reviewer_id=REVIEWER,
            preparer_id=PREPARER,
            decision="approved",
            rationale="Attempted approval of retired source.",
            language_reviewed="en",
        )

    assert registry.retrieve("HIV health", "en") == []
