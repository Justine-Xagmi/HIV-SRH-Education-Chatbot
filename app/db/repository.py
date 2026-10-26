
import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    ClinicalReviewRecord,
    DocumentVersion,
    HealthSource,
    KnowledgeAuditEvent,
    KnowledgeDocument,
)


class KnowledgeRepository:
    """Database operations for health knowledge governance.

    This repository does not authorize clinical content or verify
    reviewer qualifications. Those checks remain separate requirements.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_source(
        self,
        *,
        name: str,
        source_type: str,
        language: str = "en",
        organization: str | None = None,
        source_url: str | None = None,
        permission_status: str = "pending",
        is_active: bool = True,
    ) -> HealthSource:
        source = HealthSource(
            name=name,
            source_type=source_type,
            language=language,
            organization=organization,
            source_url=source_url,
            permission_status=permission_status,
            is_active=is_active,
        )
        self.db.add(source)
        self.db.flush()
        return source

    def get_source(self, source_id: int) -> HealthSource | None:
        return self.db.get(HealthSource, source_id)

    def create_document(
        self,
        *,
        source_id: int,
        title: str,
        topic: str,
        language: str,
        status: str = "draft",
    ) -> KnowledgeDocument:
        if self.get_source(source_id) is None:
            raise ValueError(f"Health source {source_id} does not exist.")

        document = KnowledgeDocument(
            source_id=source_id,
            title=title,
            topic=topic,
            language=language,
            status=status,
        )
        self.db.add(document)
        self.db.flush()
        return document

    def get_document(self, document_id: int) -> KnowledgeDocument | None:
        return self.db.get(KnowledgeDocument, document_id)

    def create_document_version(
        self,
        *,
        document_id: int,
        version_number: int,
        content: str,
        content_fingerprint: str,
    ) -> DocumentVersion:
        if self.get_document(document_id) is None:
            raise ValueError(f"Knowledge document {document_id} does not exist.")

        if version_number < 1:
            raise ValueError("Version number must be at least 1.")

        if len(content_fingerprint) != 64:
            raise ValueError("Content fingerprint must contain 64 characters.")

        version = DocumentVersion(
            document_id=document_id,
            version_number=version_number,
            content=content,
            content_fingerprint=content_fingerprint,
        )
        self.db.add(version)
        self.db.flush()
        return version

    def get_document_version(
        self, version_id: int
    ) -> DocumentVersion | None:
        return self.db.get(DocumentVersion, version_id)

    def list_document_versions(
        self, document_id: int
    ) -> list[DocumentVersion]:
        statement = (
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number)
        )
        return list(self.db.scalars(statement).all())

    def create_review_record(
        self,
        *,
        document_version_id: int,
        reviewer_id: str,
        decision: str,
        rationale: str,
        language: str,
    ) -> ClinicalReviewRecord:
        if self.get_document_version(document_version_id) is None:
            raise ValueError(
                f"Document version {document_version_id} does not exist."
            )

        allowed_decisions = {"approved", "rejected", "changes_requested"}
        if decision not in allowed_decisions:
            raise ValueError("Invalid clinical review decision.")

        if not reviewer_id.strip():
            raise ValueError("Reviewer ID cannot be empty.")

        if not rationale.strip():
            raise ValueError("Review rationale cannot be empty.")

        review = ClinicalReviewRecord(
            document_version_id=document_version_id,
            reviewer_id=reviewer_id,
            decision=decision,
            rationale=rationale,
            language=language,
        )
        self.db.add(review)
        self.db.flush()
        return review

    def list_reviews_for_version(
        self, version_id: int
    ) -> list[ClinicalReviewRecord]:
        statement = (
            select(ClinicalReviewRecord)
            .where(ClinicalReviewRecord.document_version_id == version_id)
            .order_by(ClinicalReviewRecord.reviewed_at)
        )
        return list(self.db.scalars(statement).all())

    def create_audit_event(
        self,
        *,
        event_type: str,
        entity_type: str,
        entity_id: str,
        actor_id: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> KnowledgeAuditEvent:
        event = KnowledgeAuditEvent(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            details=(
                json.dumps(details, sort_keys=True)
                if details is not None
                else None
            ),
        )
        self.db.add(event)
        self.db.flush()
        return event

    def list_audit_events(
        self,
        *,
        entity_type: str | None = None,
        entity_id: str | None = None,
    ) -> list[KnowledgeAuditEvent]:
        statement = select(KnowledgeAuditEvent)

        if entity_type is not None:
            statement = statement.where(
                KnowledgeAuditEvent.entity_type == entity_type
            )

        if entity_id is not None:
            statement = statement.where(
                KnowledgeAuditEvent.entity_id == entity_id
            )

        statement = statement.order_by(KnowledgeAuditEvent.created_at)
        return list(self.db.scalars(statement).all())
