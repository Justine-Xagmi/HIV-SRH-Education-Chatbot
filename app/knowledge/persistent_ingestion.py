
from dataclasses import dataclass
from datetime import datetime, timezone
import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import (
    DocumentVersion,
    HealthSource as DBHealthSource,
    KnowledgeAuditEvent,
    KnowledgeDocument as DBDocument,
    KnowledgeDocumentTopic,
)
from app.knowledge.models import KnowledgeDocument
from app.knowledge.persistent_review_workflow import build_review_snapshot
from app.knowledge.review_workflow import document_fingerprint


@dataclass(frozen=True)
class PersistentIngestionResult:
    """Result returned after persisting a validated knowledge document."""

    database_document_id: int
    version_id: int
    version_number: int
    document_id: str
    status: str
    created: bool


class PersistentKnowledgeIngestion:
    """
    Persist validated knowledge documents for subsequent clinical review.

    This service does not approve clinical content, create clinical review
    records, authenticate users, or verify reviewer qualifications.

    The caller owns the outer database transaction and must commit or roll
    it back. A database savepoint groups the ingestion writes.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    @staticmethod
    def _parse_aware_timestamp(value: object) -> datetime | None:
        """Parse a datetime or ISO-8601 string and normalize it to UTC."""
        if isinstance(value, datetime):
            parsed = value
        elif isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None
        else:
            return None

        if parsed.tzinfo is None or parsed.utcoffset() is None:
            return None

        return parsed.astimezone(timezone.utc)

    def _resolve_source(
        self,
        document: KnowledgeDocument,
    ) -> DBHealthSource:
        """
        Resolve exactly one registered database source.

        Identity is matched using title, organization, URL, and language.
        No source is automatically created.
        """
        candidate = document.source
        candidate_url = str(candidate.url)

        statement = select(DBHealthSource).where(
            DBHealthSource.name == candidate.title,
            DBHealthSource.organization == candidate.organization,
            DBHealthSource.source_url == candidate_url,
            DBHealthSource.language == candidate.language,
        )

        matches = list(self.db.scalars(statement).all())

        if not matches:
            raise ValueError(
                "No registered database source matches the submitted "
                "source title, organization, URL, and language."
            )

        if len(matches) != 1:
            raise ValueError(
                "Multiple registered database sources match the submitted "
                "source identity. Resolve the ambiguity before ingestion."
            )

        source = matches[0]

        if not source.is_active:
            raise ValueError("Inactive sources cannot be ingested.")

        if source.permission_status != "permitted":
            raise ValueError(
                "The registered database source must have permission "
                "status 'permitted'."
            )

        submitted_verified_at = self._parse_aware_timestamp(
            candidate.last_verified_at
        )
        registered_verified_at = self._parse_aware_timestamp(
            source.last_verified_at
        )

        if (
            submitted_verified_at is None
            or registered_verified_at is None
        ):
            raise ValueError(
                "A valid timezone-aware source verification timestamp "
                "is required."
            )

        if submitted_verified_at != registered_verified_at:
            raise ValueError(
                "The submitted source verification timestamp does not "
                "match the registered database source."
            )

        if candidate.permission_status != "permitted":
            raise ValueError(
                "The submitted source permission status must be 'permitted'."
            )

        # The Pydantic HealthSource model validates the required permission
        # evidence for a source whose permission status is 'permitted'.
        if (
            not candidate.permission_basis
            or not candidate.permission_basis.strip()
            or not candidate.permission_reference
            or not candidate.permission_reference.strip()
            or not candidate.permission_checked_by
            or not candidate.permission_checked_by.strip()
            or candidate.permission_checked_at is None
        ):
            raise ValueError(
                "Complete permission evidence is required for ingestion."
            )

        return source

    def _find_existing_document(
        self,
        external_document_id: str,
    ) -> list[tuple[DBDocument, DocumentVersion]]:
        """Find all persisted versions carrying the candidate external ID."""
        statement = (
            select(DBDocument, DocumentVersion)
            .join(
                DocumentVersion,
                DocumentVersion.document_id == DBDocument.id,
            )
            .order_by(
                DBDocument.id,
                DocumentVersion.version_number,
            )
        )

        matches: list[tuple[DBDocument, DocumentVersion]] = []

        for db_document, version in self.db.execute(statement).all():
            snapshot = version.review_snapshot

            if (
                isinstance(snapshot, dict)
                and snapshot.get("document_id") == external_document_id
            ):
                matches.append((db_document, version))

        return matches

    def ingest(
        self,
        document: KnowledgeDocument,
        *,
        actor_id: str | None = None,
    ) -> PersistentIngestionResult:
        """
        Persist a validated candidate as a pending-review database document.

        An identical retry returns the original version 1 result without
        creating duplicate records, even if later versions exist.

        A conflicting retry is rejected. Later versions and review decisions
        are not modified by this method.
        """
        if document.ingestion_status != "validated":
            raise ValueError(
                "Only documents with ingestion_status 'validated' "
                "can be persisted."
            )

        if document.review_status != "pending_review":
            raise ValueError(
                "Newly ingested documents must have review_status "
                "'pending_review'."
            )

        if not document.topics:
            raise ValueError(
                "At least one topic is required for persistent ingestion."
            )

        if len(document.topics) != len(set(document.topics)):
            raise ValueError("Duplicate document topics are not allowed.")

        source = self._resolve_source(document)
        fingerprint = document_fingerprint(document)
        snapshot = build_review_snapshot(document)

        existing = self._find_existing_document(document.document_id)

        if existing:
            # Multiple database documents with the same external ID are
            # ambiguous and must never be silently reconciled.
            existing_document_ids = {
                db_document.id for db_document, _ in existing
            }

            if len(existing_document_ids) != 1:
                raise ValueError(
                    "The external document ID is associated with multiple "
                    "database documents. Manual reconciliation is required."
                )

            existing_document = existing[0][0]

            # The original ingestion is always version 1. Later versions may
            # have been created by clinical review and must remain untouched.
            original_versions = [
                version
                for db_document, version in existing
                if (
                    db_document.id == existing_document.id
                    and version.version_number == 1
                )
            ]

            if len(original_versions) != 1:
                raise ValueError(
                    "The original version 1 for this external document ID "
                    "could not be identified uniquely. Manual reconciliation "
                    "is required."
                )

            existing_version = original_versions[0]

            if (
                existing_document.source_id != source.id
                or existing_document.title != document.title
                or existing_document.language != document.language
                or existing_document.topic != document.topics[0]
                or existing_version.content != document.content
                or existing_version.content_fingerprint != fingerprint
                or existing_version.review_snapshot != snapshot
            ):
                raise ValueError(
                    "This external document ID already exists with "
                    "different content or metadata. Use a new document ID "
                    "or resolve the existing record."
                )

            existing_topics = set(
                self.db.scalars(
                    select(KnowledgeDocumentTopic.topic).where(
                        KnowledgeDocumentTopic.document_id
                        == existing_document.id
                    )
                ).all()
            )

            if existing_topics != set(document.topics):
                raise ValueError(
                    "The existing document has different topic assignments. "
                    "Manual reconciliation is required."
                )

            return PersistentIngestionResult(
                database_document_id=existing_document.id,
                version_id=existing_version.id,
                version_number=existing_version.version_number,
                document_id=document.document_id,
                status=existing_document.status,
                created=False,
            )

        with self.db.begin_nested():
            db_document = DBDocument(
                source_id=source.id,
                title=document.title,
                topic=document.topics[0],
                language=document.language,
                status="pending_review",
            )
            self.db.add(db_document)
            self.db.flush()

            topic_records = [
                KnowledgeDocumentTopic(
                    document_id=db_document.id,
                    topic=topic,
                )
                for topic in document.topics
            ]
            self.db.add_all(topic_records)
            self.db.flush()

            db_version = DocumentVersion(
                document_id=db_document.id,
                version_number=1,
                content=document.content,
                content_fingerprint=fingerprint,
                review_snapshot=snapshot,
            )
            self.db.add(db_version)
            self.db.flush()

            audit_event = KnowledgeAuditEvent(
                event_type="knowledge_document_ingested",
                entity_type="knowledge_document",
                entity_id=str(db_document.id),
                actor_id=actor_id,
                details=json.dumps(
                    {
                        "external_document_id": document.document_id,
                        "version_id": db_version.id,
                        "version_number": 1,
                        "content_fingerprint": fingerprint,
                        "language": document.language,
                        "topics": sorted(document.topics),
                        "source_id": source.id,
                        "status": "pending_review",
                    },
                    sort_keys=True,
                ),
            )
            self.db.add(audit_event)
            self.db.flush()

        return PersistentIngestionResult(
            database_document_id=db_document.id,
            version_id=db_version.id,
            version_number=1,
            document_id=document.document_id,
            status=db_document.status,
            created=True,
        )
