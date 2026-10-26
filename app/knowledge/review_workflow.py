
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.knowledge.models import KnowledgeDocument


ReviewDecision = Literal[
    "approved",
    "rejected",
    "changes_requested",
]


class ClinicalReviewRecord(BaseModel):
    """A review decision tied to a specific version of a document."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    review_id: str = Field(min_length=1, max_length=100)
    document_id: str = Field(min_length=1, max_length=100)
    content_fingerprint: str = Field(min_length=64, max_length=64)
    reviewer_id: str = Field(min_length=1, max_length=100)
    decision: ReviewDecision
    rationale: str = Field(min_length=1, max_length=4000)
    reviewed_at: datetime
    language_reviewed: Literal["en", "sw"]


def document_fingerprint(document: KnowledgeDocument) -> str:
    """Create a stable fingerprint of the document and its source metadata.

    Review fields and timestamps that do not define the content are excluded.
    Changing the content, language, topic, source URL, or source version
    changes the fingerprint and requires a new review.
    """

    payload = {
        "document_id": document.document_id,
        "title": document.title,
        "content": document.content,
        "language": document.language,
        "topics": sorted(document.topics),
        "source_id": document.source.source_id,
        "source_title": document.source.title,
        "source_organization": document.source.organization,
        "source_url": str(document.source.url),
        "source_language": document.source.language,
        "source_version": document.source.version,
        "source_publication_date": (
            document.source.publication_date.isoformat()
            if document.source.publication_date
            else None
        ),
        "source_last_verified_at": (
            document.source.last_verified_at.isoformat()
            if document.source.last_verified_at
            else None
        ),
        "source_permission_status": document.source.permission_status,
    }

    serialized = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return sha256(serialized.encode("utf-8")).hexdigest()


class ClinicalReviewWorkflow:
    """Development-only review workflow with session-only history.

    The caller must supply the set of authorized reviewer IDs. The default
    is empty, so no reviewer can approve content by default.

    This class is not an authentication system and does not verify clinical
    qualifications. Production authorization and persistent audit storage
    must be implemented separately.
    """

    def __init__(
        self,
        authorized_reviewer_ids: set[str] | None = None,
    ) -> None:
        self._authorized_reviewer_ids = set(
            authorized_reviewer_ids or set()
        )
        self._records: list[ClinicalReviewRecord] = []
        self._latest_approval: dict[str, str] = {}

    def records_for(self, document_id: str) -> list[ClinicalReviewRecord]:
        """Return the session's review records for a document."""
        return [
            record
            for record in self._records
            if record.document_id == document_id
        ]

    def is_approval_current(self, document: KnowledgeDocument) -> bool:
        """Check whether this exact document version has a recorded approval."""
        fingerprint = document_fingerprint(document)
        return self._latest_approval.get(document.document_id) == fingerprint

    def review(
        self,
        document: KnowledgeDocument,
        *,
        reviewer_id: str,
        preparer_id: str,
        decision: ReviewDecision,
        rationale: str,
        language_reviewed: Literal["en", "sw"],
    ) -> KnowledgeDocument:
        """Record a review and return a copy with the corresponding status."""

        if reviewer_id not in self._authorized_reviewer_ids:
            raise PermissionError("Reviewer is not authorized.")

        if reviewer_id == preparer_id:
            raise PermissionError("Preparers cannot approve their own submissions.")

        if language_reviewed != document.language:
            raise ValueError(
                "The reviewed language must match the document language."
            )

        if not rationale.strip():
            raise ValueError("A review rationale is required.")

        fingerprint = document_fingerprint(document)

        # A previous approval for another version must not remain current.
        self._latest_approval.pop(document.document_id, None)

        record = ClinicalReviewRecord(
            review_id=f"review-{len(self._records) + 1:06d}",
            document_id=document.document_id,
            content_fingerprint=fingerprint,
            reviewer_id=reviewer_id,
            decision=decision,
            rationale=rationale.strip(),
            reviewed_at=datetime.now(timezone.utc),
            language_reviewed=language_reviewed,
        )
        self._records.append(record)

        if decision == "approved":
            self._latest_approval[document.document_id] = fingerprint
            return document.model_copy(
                update={
                    "review_status": "approved",
                    "reviewed_by": reviewer_id,
                    "reviewed_at": record.reviewed_at,
                    "source": document.source.model_copy(
                        update={
                            "review_status": "approved",
                            "reviewed_by": reviewer_id,
                            "reviewed_at": record.reviewed_at,
                        }
                    ),
                }
            )

        if decision == "rejected":
            return document.model_copy(
                update={
                    "review_status": "retired",
                    "reviewed_by": reviewer_id,
                    "reviewed_at": record.reviewed_at,
                    "source": document.source.model_copy(
                        update={
                            "review_status": "pending_review",
                            "reviewed_by": reviewer_id,
                            "reviewed_at": record.reviewed_at,
                        }
                    ),
                }
            )

        return document.model_copy(
            update={
                "review_status": "pending_review",
                "reviewed_by": reviewer_id,
                "reviewed_at": record.reviewed_at,
                "source": document.source.model_copy(
                    update={
                        "review_status": "pending_review",
                        "reviewed_by": reviewer_id,
                        "reviewed_at": record.reviewed_at,
                    }
                ),
            }
        )
