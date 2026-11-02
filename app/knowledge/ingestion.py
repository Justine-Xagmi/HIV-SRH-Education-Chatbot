
from datetime import datetime, timezone

from app.knowledge.models import KnowledgeDocument


def _valid_source_verification_timestamp(
    value: datetime | None,
) -> bool:
    """Return True when the timestamp is aware and not in the future."""
    if value is None:
        return False

    if value.tzinfo is None or value.utcoffset() is None:
        return False

    return value.astimezone(timezone.utc) <= datetime.now(timezone.utc)


def validate_candidate_document(
    document: KnowledgeDocument,
) -> list[str]:
    """Return validation problems that block candidate ingestion.

    Passing validation does not mean clinical review is complete.
    """

    issues: list[str] = []

    # Document identity and content.
    if not document.document_id.strip():
        issues.append("Document ID cannot be blank.")

    if not document.title.strip():
        issues.append("Document title cannot be blank.")

    if not document.content.strip():
        issues.append("Document content cannot be blank.")

    # Source metadata.
    if not document.source.source_id.strip():
        issues.append("Source ID cannot be blank.")

    if not document.source.title.strip():
        issues.append("Source title cannot be blank.")

    if not document.source.organization.strip():
        issues.append("Source organization cannot be blank.")

    if not document.source.version.strip():
        issues.append("Source version cannot be blank.")

    if document.language != document.source.language:
        issues.append("Document language must match source language.")

    if document.source.url.scheme != "https":
        issues.append("Source URL must use HTTPS.")

    if document.source.publication_date is None:
        issues.append("Source publication date is required.")

    if document.source.last_verified_at is None:
        issues.append("Source verification timestamp is required.")
    elif not _valid_source_verification_timestamp(
        document.source.last_verified_at
    ):
        issues.append(
            "Source verification timestamp must be timezone-aware "
            "and cannot be in the future."
        )

    if document.source.permission_status != "permitted":
        issues.append(
            "Source permissions must be reviewed and marked permitted."
        )

    # Topic validation.
    if not document.topics:
        issues.append("At least one knowledge topic is required.")

    if len(document.topics) != len(set(document.topics)):
        issues.append("Duplicate knowledge topics are not allowed.")

    # Retired records cannot enter the candidate workflow.
    if document.review_status == "retired":
        issues.append("Retired documents cannot be ingested as candidates.")

    if document.source.review_status == "retired":
        issues.append("Retired sources cannot be used for ingestion.")

    return issues


def prepare_candidate_document(
    document: KnowledgeDocument,
) -> KnowledgeDocument:
    """Validate metadata and return a candidate awaiting review.

    This function deliberately resets approval information. It never
    approves a source or document.
    """

    issues = validate_candidate_document(document)

    if issues:
        raise ValueError(
            "Candidate document failed validation: "
            + "; ".join(issues)
        )

    pending_source = document.source.model_copy(
        update={
            "review_status": "pending_review",
            "reviewed_by": None,
            "reviewed_at": None,
        }
    )

    return document.model_copy(
        update={
            "source": pending_source,
            "review_status": "pending_review",
            "reviewed_by": None,
            "reviewed_at": None,
            "ingestion_status": "validated",
        }
    )
