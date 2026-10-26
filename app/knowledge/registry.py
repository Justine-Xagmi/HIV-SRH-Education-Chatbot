
import re
from typing import Literal

from app.knowledge.ingestion import validate_candidate_document
from app.knowledge.models import KnowledgeDocument
from app.knowledge.review_workflow import (
    ClinicalReviewRecord,
    ClinicalReviewWorkflow,
)


ReviewDecision = Literal[
    "approved",
    "rejected",
    "changes_requested",
]


def _tokenize(text: str) -> set[str]:
    """Extract case-insensitive word tokens, ignoring punctuation."""
    return set(re.findall(r"\w+", text.casefold()))


class KnowledgeRegistry:
    """
    In-memory development registry with clinical-review safeguards.

    Safeguards:
    - New and updated documents require fresh clinical review.
    - Retired sources remain retired and cannot be approved.
    - A preparer cannot approve their own submission.
    - Only configured reviewer IDs can submit review decisions.
    - Approval requires valid ingestion metadata.
    - Retrieval requires approval for the exact current document version.
    - Review history is retained during the current process only.

    This is a development implementation, not a production clinical
    governance system. Reviewer IDs do not prove identity or qualifications.
    """

    def __init__(
        self,
        authorized_reviewer_ids: set[str] | None = None,
    ) -> None:
        self._documents: dict[str, KnowledgeDocument] = {}
        self._review_workflow = ClinicalReviewWorkflow(
            authorized_reviewer_ids=authorized_reviewer_ids
        )

    @staticmethod
    def _reset_review_status(
        document: KnowledgeDocument,
    ) -> KnowledgeDocument:
        """
        Reset document approval after registration or modification.

        Preserve a retired source's status. Reset non-retired source status
        to pending review so an old source approval cannot be reused
        automatically after a document change.
        """
        source_status = (
            "retired"
            if document.source.review_status == "retired"
            else "pending_review"
        )

        pending_source = document.source.model_copy(
            update={
                "review_status": source_status,
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
            }
        )

    def add_document(self, document: KnowledgeDocument) -> None:
        """Register a new document in pending-review status."""
        document_id = document.document_id

        if document_id in self._documents:
            raise ValueError(f"Document already exists: {document_id}")

        self._documents[document_id] = self._reset_review_status(document)

    def update_document(self, document: KnowledgeDocument) -> None:
        """
        Replace an existing document and require fresh approval.

        Caller-supplied document approval is removed. A retired source
        remains retired, including when the document is updated.
        """
        document_id = document.document_id

        if document_id not in self._documents:
            raise KeyError(f"Document not found: {document_id}")

        self._documents[document_id] = self._reset_review_status(document)

    def get_document(self, document_id: str) -> KnowledgeDocument:
        """Return a registered document or raise KeyError."""
        if document_id not in self._documents:
            raise KeyError(f"Document not found: {document_id}")

        return self._documents[document_id]

    def review_document(
        self,
        document_id: str,
        *,
        reviewer_id: str,
        preparer_id: str,
        decision: ReviewDecision,
        rationale: str,
        language_reviewed: Literal["en", "sw"],
    ) -> KnowledgeDocument:
        """Record a review, enforcing source and ingestion safeguards."""
        if document_id not in self._documents:
            raise KeyError(f"Document not found: {document_id}")

        if decision not in {
            "approved",
            "rejected",
            "changes_requested",
        }:
            raise ValueError(f"Unsupported review decision: {decision}")

        current_document = self._documents[document_id]

        if decision == "approved":
            if current_document.source.review_status == "retired":
                raise ValueError(
                    "Document cannot be approved: source is retired."
                )

            issues = validate_candidate_document(current_document)

            if issues:
                raise ValueError(
                    "Document cannot be approved: " + " ".join(issues)
                )

        reviewed_document = self._review_workflow.review(
            current_document,
            reviewer_id=reviewer_id,
            preparer_id=preparer_id,
            decision=decision,
            rationale=rationale,
            language_reviewed=language_reviewed,
        )

        self._documents[document_id] = reviewed_document
        return reviewed_document

    def review_history(
        self,
        document_id: str,
    ) -> list[ClinicalReviewRecord]:
        """Return review records for this document in the current session."""
        if document_id not in self._documents:
            raise KeyError(f"Document not found: {document_id}")

        return self._review_workflow.records_for(document_id)

    def retrieve(
        self,
        query: str,
        language: str,
        limit: int = 5,
    ) -> list[KnowledgeDocument]:
        """
        Retrieve matching documents only when their current versions
        have valid approval and their sources are approved and not retired.
        """
        if not query.strip() or limit <= 0:
            return []

        query_terms = _tokenize(query)

        if not query_terms:
            return []

        matches: list[tuple[int, KnowledgeDocument]] = []

        for document in self._documents.values():
            if document.language != language:
                continue

            if document.source.language != language:
                continue

            # Document and source must both be approved.
            if document.review_status != "approved":
                continue

            if document.source.review_status != "approved":
                continue

            # Explicitly exclude retired sources.
            if document.source.review_status == "retired":
                continue

            # Approval must still match this exact document version.
            if not self._review_workflow.is_approval_current(document):
                continue

            searchable_text = f"{document.title} {document.content}"
            document_terms = _tokenize(searchable_text)
            score = len(query_terms & document_terms)

            if score > 0:
                matches.append((score, document))

        # Stable sorting preserves registration order for tied scores.
        matches.sort(key=lambda item: item[0], reverse=True)

        return [
            document
            for _, document in matches[:limit]
        ]

    def count(self) -> int:
        """Return the number of registered documents."""
        return len(self._documents)
