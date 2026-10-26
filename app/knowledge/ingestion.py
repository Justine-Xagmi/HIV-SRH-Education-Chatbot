
from app.knowledge.models import KnowledgeDocument


def validate_candidate_document(
    document: KnowledgeDocument,
) -> list[str]:
    """Return metadata problems that block candidate ingestion.

    Passing validation does not mean that clinical review is complete.
    """

    issues: list[str] = []

    if document.language != document.source.language:
        issues.append("Document language must match source language.")

    if document.source.url.scheme != "https":
        issues.append("Source URL must use HTTPS.")

    if document.source.publication_date is None:
        issues.append("Source publication date is required.")

    if document.source.last_verified_at is None:
        issues.append("Source verification timestamp is required.")

    if document.source.permission_status != "permitted":
        issues.append(
            "Source permissions must be reviewed and marked permitted."
        )

    if not document.topics:
        issues.append("At least one knowledge topic is required.")

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
    approves a source or document, even if the input says it is approved.
    """

    issues = validate_candidate_document(document)

    if issues:
        raise ValueError(
            "Candidate document failed validation: " + " ".join(issues)
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
