
from datetime import date, datetime, timezone

import pytest

from app.knowledge.ingestion import (
    prepare_candidate_document,
    validate_candidate_document,
)
from app.knowledge.models import HealthSource, KnowledgeDocument


def make_candidate(
    *,
    language: str = "en",
    source_language: str = "en",
    topics: list[str] | None = None,
    permission_status: str = "permitted",
    publication_date: date | None = date(2025, 1, 1),
    last_verified_at: datetime | None = datetime(
        2026, 10, 1, tzinfo=timezone.utc
    ),
) -> KnowledgeDocument:
    source = HealthSource(
        source_id="source-test-001",
        title="Example health information",
        organization="Example Health Organization",
        url="https://example.org/health",
        language=source_language,
        version="1.0",
        publication_date=publication_date,
        last_verified_at=last_verified_at,
        permission_status=permission_status,
    )

    return KnowledgeDocument(
        document_id="document-test-001",
        source=source,
        title="HIV prevention education",
        content="Educational content awaiting qualified review.",
        language=language,
        topics=topics or ["hiv_prevention"],
    )


def test_valid_candidate_passes_metadata_validation():
    document = make_candidate()

    assert validate_candidate_document(document) == []


def test_missing_source_metadata_is_reported():
    document = make_candidate(
        publication_date=None,
        last_verified_at=None,
    )

    issues = validate_candidate_document(document)

    assert "Source publication date is required." in issues
    assert "Source verification timestamp is required." in issues


def test_unknown_permission_status_blocks_validation():
    document = make_candidate(permission_status="unknown")

    issues = validate_candidate_document(document)

    assert (
        "Source permissions must be reviewed and marked permitted."
        in issues
    )


def test_restricted_permission_status_blocks_validation():
    document = make_candidate(permission_status="restricted")

    issues = validate_candidate_document(document)

    assert (
        "Source permissions must be reviewed and marked permitted."
        in issues
    )


def test_document_and_source_languages_must_match():
    document = make_candidate(
        language="en",
        source_language="sw",
    )

    issues = validate_candidate_document(document)

    assert "Document language must match source language." in issues


def test_candidate_requires_at_least_one_topic():
    document = make_candidate(topics=[])

    # Explicitly set an empty list after construction because the helper
    # uses a default topic list when topics is None.
    document = document.model_copy(update={"topics": []})

    issues = validate_candidate_document(document)

    assert "At least one knowledge topic is required." in issues


def test_retired_document_cannot_be_ingested():
    document = make_candidate().model_copy(
        update={"review_status": "retired"}
    )

    issues = validate_candidate_document(document)

    assert "Retired documents cannot be ingested as candidates." in issues


def test_retired_source_cannot_be_ingested():
    document = make_candidate()
    retired_source = document.source.model_copy(
        update={"review_status": "retired"}
    )
    document = document.model_copy(update={"source": retired_source})

    issues = validate_candidate_document(document)

    assert "Retired sources cannot be used for ingestion." in issues


def test_invalid_candidate_raises_value_error():
    document = make_candidate(permission_status="unknown")

    with pytest.raises(ValueError, match="failed validation"):
        prepare_candidate_document(document)


def test_preparation_never_automatically_approves_content():
    document = make_candidate()

    approved_source = document.source.model_copy(
        update={
            "review_status": "approved",
            "reviewed_by": "example-reviewer",
            "reviewed_at": datetime.now(timezone.utc),
        }
    )
    document = document.model_copy(
        update={
            "source": approved_source,
            "review_status": "approved",
            "reviewed_by": "example-reviewer",
            "reviewed_at": datetime.now(timezone.utc),
        }
    )

    prepared = prepare_candidate_document(document)

    assert prepared.ingestion_status == "validated"
    assert prepared.review_status == "pending_review"
    assert prepared.source.review_status == "pending_review"
    assert prepared.reviewed_by is None
    assert prepared.reviewed_at is None
    assert prepared.source.reviewed_by is None
    assert prepared.source.reviewed_at is None


def test_preparation_preserves_valid_metadata():
    document = make_candidate()

    prepared = prepare_candidate_document(document)

    assert prepared.document_id == document.document_id
    assert prepared.source.source_id == document.source.source_id
    assert prepared.topics == ["hiv_prevention"]
    assert prepared.source.permission_status == "permitted"
    assert prepared.review_status == "pending_review"
    assert prepared.source.review_status == "pending_review"
