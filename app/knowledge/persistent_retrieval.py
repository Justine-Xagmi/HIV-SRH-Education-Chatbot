
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    ClinicalReviewRecord as DBReview,
    DocumentVersion,
    HealthSource as DBSource,
    KnowledgeDocument as DBDocument,
)
from app.knowledge.models import HealthSource, KnowledgeDocument
from app.knowledge.review_workflow import document_fingerprint


@dataclass(frozen=True)
class RetrievedHealthDocument:
    """A database document eligible for educational retrieval."""

    document_id: int
    version_number: int
    title: str
    content: str
    language: str
    source_title: str
    source_organization: str | None
    source_url: str
    score: int


class PersistentKnowledgeRetriever:
    """
    Retrieve only documents whose latest version has valid approval evidence.

    This class does not authenticate reviewers or verify their clinical
    qualifications. It validates the evidence stored in the database.
    """

    REQUIRED_SNAPSHOT_FIELDS = {
        "document_id",
        "title",
        "content_fingerprint",
        "language",
        "topics",
        "source_id",
        "source_title",
        "source_organization",
        "source_url",
        "source_language",
        "source_version",
        "source_publication_date",
        "source_last_verified_at",
        "source_permission_status",
    }

    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _score(query: str, title: str, content: str) -> int:
        """Match the existing registry's simple keyword-overlap ranking."""
        import re

        tokens = set(re.findall(r"\w+", query.lower()))
        searchable = set(
            re.findall(r"\w+", f"{title} {content}".lower())
        )
        return len(tokens & searchable)

    def _latest_version(
        self, document_id: int
    ) -> DocumentVersion | None:
        return self.db.scalar(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
            .limit(1)
        )

    def _latest_review(
        self, version_id: int
    ) -> DBReview | None:
        return self.db.scalar(
            select(DBReview)
            .where(DBReview.document_version_id == version_id)
            .order_by(
                DBReview.reviewed_at.desc(),
                DBReview.id.desc(),
            )
            .limit(1)
        )

    def _is_eligible(
        self,
        document: DBDocument,
        source: DBSource,
        version: DocumentVersion,
        review: DBReview,
        requested_language: str,
    ) -> bool:
        """Reject incomplete or inconsistent approval evidence."""
        snapshot = version.review_snapshot

        if not isinstance(snapshot, dict):
            return False

        if not self.REQUIRED_SNAPSHOT_FIELDS.issubset(snapshot):
            return False

        if document.status != "approved":
            return False

        if review.decision != "approved":
            return False

        if review.language != requested_language:
            return False

        if (
            document.language != requested_language
            or source.language != requested_language
        ):
            return False

        if not source.is_active:
            return False

        if source.permission_status != "permitted":
            return False

        if not version.content_fingerprint:
            return False

        if len(version.content_fingerprint) != 64:
            return False

        # Verify metadata that exists independently in the current database.
        if snapshot["title"] != document.title:
            return False

        if snapshot["language"] != document.language:
            return False

        topics = snapshot["topics"]
        if not isinstance(topics, list) or not topics:
            return False

        if document.topic not in topics:
            return False

        if snapshot["source_title"] != source.name:
            return False

        if snapshot["source_organization"] != source.organization:
            return False

        if snapshot["source_url"] != source.source_url:
            return False

        if snapshot["source_language"] != source.language:
            return False

        if snapshot["source_permission_status"] != source.permission_status:
            return False

        if snapshot["content_fingerprint"] != version.content_fingerprint:
            return False

        # Reconstruct the reviewed document and recalculate its fingerprint.
        # Review status is set to approved only to reconstruct the reviewed
        # snapshot; the actual decision was checked independently above.
        try:
            reviewed_source = HealthSource(
                source_id=snapshot["source_id"],
                title=snapshot["source_title"],
                organization=snapshot["source_organization"],
                url=snapshot["source_url"],
                language=snapshot["source_language"],
                review_status="approved",
                reviewed_by=review.reviewer_id,
                reviewed_at=review.reviewed_at,
                version=snapshot["source_version"],
                publication_date=snapshot["source_publication_date"],
                last_verified_at=snapshot["source_last_verified_at"],
                permission_status=snapshot["source_permission_status"],
            )

            reviewed_document = KnowledgeDocument(
                document_id=snapshot["document_id"],
                source=reviewed_source,
                title=snapshot["title"],
                content=version.content,
                language=snapshot["language"],
                topics=topics,
                ingestion_status="validated",
                review_status="approved",
                reviewed_by=review.reviewer_id,
                reviewed_at=review.reviewed_at,
            )
        except (ValueError, TypeError, KeyError):
            return False

        calculated_fingerprint = document_fingerprint(reviewed_document)

        if calculated_fingerprint != version.content_fingerprint:
            return False

        if snapshot["document_id"] == "":
            return False

        if snapshot["source_id"] == "":
            return False

        return True

    def retrieve(
        self,
        query: str,
        language: str,
        limit: int = 5,
    ) -> list[RetrievedHealthDocument]:
        """
        Return matching content only from currently eligible latest versions.

        A newer pending, rejected, or inconsistent version prevents fallback
        to an older approved version.
        """
        if language not in {"en", "sw"}:
            raise ValueError("Unsupported language.")

        if limit < 1:
            return []

        if not query.strip():
            return []

        documents = self.db.scalars(
            select(DBDocument).where(
                DBDocument.language == language
            )
        ).all()

        results: list[RetrievedHealthDocument] = []

        for document in documents:
            source = self.db.get(DBSource, document.source_id)

            if source is None:
                continue

            version = self._latest_version(document.id)

            if version is None:
                continue

            review = self._latest_review(version.id)

            if review is None:
                continue

            if not self._is_eligible(
                document,
                source,
                version,
                review,
                language,
            ):
                continue

            score = self._score(
                query,
                document.title,
                version.content,
            )

            if score == 0:
                continue

            results.append(
                RetrievedHealthDocument(
                    document_id=document.id,
                    version_number=version.version_number,
                    title=document.title,
                    content=version.content,
                    language=document.language,
                    source_title=source.name,
                    source_organization=source.organization,
                    source_url=source.source_url or "",
                    score=score,
                )
            )

        results.sort(
            key=lambda item: (
                -item.score,
                item.title.lower(),
                item.document_id,
            )
        )

        return results[:limit]
