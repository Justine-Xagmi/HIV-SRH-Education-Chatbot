
import json
from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    ClinicalReviewRecord as DBClinicalReviewRecord,
    DocumentVersion,
    HealthSource as DBHealthSource,
    KnowledgeAuditEvent,
    KnowledgeDocument as DBDocument,
)
from app.knowledge.models import KnowledgeDocument
from app.knowledge.review_workflow import document_fingerprint


ReviewDecision = Literal["approved", "rejected", "changes_requested"]


def build_review_snapshot(document: KnowledgeDocument) -> dict:
    """Capture the document and source metadata used for a review."""

    return {
        "document_id": document.document_id,
        "title": document.title,
        "content_fingerprint": document_fingerprint(document),
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


class PersistentClinicalReviewWorkflow:
    """
    Database-backed review workflow.

    This service enforces configured reviewer IDs and persists review evidence.
    It does not authenticate users or verify clinical qualifications.

    The caller owns the outer database transaction and must commit or roll
    it back. Review and audit writes are grouped in a database savepoint.
    """

    def __init__(
        self,
        db: Session,
        authorized_reviewer_ids: set[str] | None = None,
    ) -> None:
        self.db = db
        self._authorized_reviewer_ids = set(
            authorized_reviewer_ids or set()
        )

    def record_review(
        self,
        document: KnowledgeDocument,
        *,
        database_document_id: int,
        version_number: int,
        reviewer_id: str,
        preparer_id: str,
        decision: ReviewDecision,
        rationale: str,
        language_reviewed: str,
    ) -> DBClinicalReviewRecord:
        """Persist a review against an exact, immutable document version."""

        if reviewer_id not in self._authorized_reviewer_ids:
            raise PermissionError("Reviewer is not authorized.")

        if reviewer_id == preparer_id:
            raise PermissionError(
                "Preparers cannot review their own submissions."
            )

        if decision not in {
            "approved",
            "rejected",
            "changes_requested",
        }:
            raise ValueError("Invalid review decision.")

        if language_reviewed != document.language:
            raise ValueError(
                "The reviewed language must match the document language."
            )

        if not rationale or not rationale.strip():
            raise ValueError("A review rationale is required.")

        if version_number < 1:
            raise ValueError("Version number must be at least 1.")

        fingerprint = document_fingerprint(document)
        snapshot = build_review_snapshot(document)

        db_document = self.db.get(DBDocument, database_document_id)
        if db_document is None:
            raise ValueError("Database document does not exist.")

        if db_document.language != document.language:
            raise ValueError(
                "Database document language does not match the submitted document."
            )

        source = self.db.get(DBHealthSource, db_document.source_id)
        if source is None:
            raise ValueError("Database source does not exist.")

        if not source.is_active:
            raise ValueError(
                "Inactive sources cannot be reviewed for approval."
            )

        if (
            decision == "approved"
            and source.permission_status != "permitted"
        ):
            raise ValueError(
                "A document cannot be approved while its source permission "
                "status is not 'permitted'."
            )

        # Keep the immutable version, review, and audit writes in one savepoint.
        # The caller remains responsible for committing or rolling back.
        with self.db.begin_nested():
            existing_version = self.db.scalar(
                select(DocumentVersion).where(
                    DocumentVersion.document_id == database_document_id,
                    DocumentVersion.version_number == version_number,
                )
            )

            if existing_version is not None:
                if (
                    existing_version.content_fingerprint != fingerprint
                    or existing_version.content != document.content
                ):
                    raise ValueError(
                        "This version number already belongs to different "
                        "content. Create a new version number."
                    )

                if existing_version.review_snapshot is None:
                    raise ValueError(
                        "This legacy version has no review snapshot. "
                        "Create a new version number before recording a review."
                    )

                if existing_version.review_snapshot != snapshot:
                    raise ValueError(
                        "The existing review snapshot differs from the "
                        "submitted document metadata. Create a new version number."
                    )

                db_version = existing_version
            else:
                db_version = DocumentVersion(
                    document_id=database_document_id,
                    version_number=version_number,
                    content=document.content,
                    content_fingerprint=fingerprint,
                    review_snapshot=snapshot,
                )
                self.db.add(db_version)
                self.db.flush()

            review = DBClinicalReviewRecord(
                document_version_id=db_version.id,
                reviewer_id=reviewer_id,
                decision=decision,
                rationale=rationale.strip(),
                language=language_reviewed,
                reviewed_at=datetime.now(timezone.utc),
            )
            self.db.add(review)

            if decision == "approved":
                db_document.status = "approved"
            elif decision == "rejected":
                db_document.status = "rejected"
            else:
                db_document.status = "pending_review"

            audit = KnowledgeAuditEvent(
                event_type="clinical_review_recorded",
                entity_type="knowledge_document",
                entity_id=str(database_document_id),
                actor_id=reviewer_id,
                details=json.dumps(
                    {
                        "version_id": db_version.id,
                        "version_number": version_number,
                        "content_fingerprint": fingerprint,
                        "decision": decision,
                        "language": language_reviewed,
                    },
                    sort_keys=True,
                ),
            )
            self.db.add(audit)
            self.db.flush()

        return review
