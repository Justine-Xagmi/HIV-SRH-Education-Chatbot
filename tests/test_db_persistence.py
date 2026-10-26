
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.db.models import (
    ClinicalReviewRecord,
    DocumentVersion,
    HealthSource,
    KnowledgeAuditEvent,
    KnowledgeDocument,
)
from app.db.session import SessionLocal


@pytest.fixture
def db_session():
    """Provide a database session for persistence tests."""
    if SessionLocal is None:
        pytest.fail("DATABASE_URL is not configured.")

    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_governance_records_persist_and_relationships_work(db_session):
    """Verify persistence and relationships across all five tables."""
    suffix = uuid.uuid4().hex
    source_name = f"TEST-ONLY source {suffix}"
    document_title = f"TEST-ONLY document {suffix}"
    fingerprint = uuid.uuid4().hex * 2

    source_id = None
    document_id = None
    version_id = None
    review_id = None
    event_id = None

    try:
        # 1. Create a test-only health source.
        source = HealthSource(
            name=source_name,
            source_type="test_only",
            language="en",
            permission_status="pending",
            is_active=False,
        )
        db_session.add(source)
        db_session.flush()
        source_id = source.id

        # 2. Create a document linked to the source.
        document = KnowledgeDocument(
            source_id=source_id,
            title=document_title,
            topic="test_only",
            language="en",
            status="draft",
        )
        db_session.add(document)
        db_session.flush()
        document_id = document.id

        # 3. Create the first immutable document version.
        version = DocumentVersion(
            document_id=document_id,
            version_number=1,
            content="TEST-ONLY content; not health guidance.",
            content_fingerprint=fingerprint,
        )
        db_session.add(version)
        db_session.flush()
        version_id = version.id

        # 4. Create a review record for this exact version.
        review = ClinicalReviewRecord(
            document_version_id=version_id,
            reviewer_id=f"test-only-{suffix}",
            decision="changes_requested",
            rationale="TEST-ONLY persistence verification.",
            language="en",
        )
        db_session.add(review)
        db_session.flush()
        review_id = review.id

        # 5. Create an audit event.
        event = KnowledgeAuditEvent(
            event_type="test_persistence",
            entity_type="document_version",
            entity_id=str(version_id),
            actor_id=f"test-only-{suffix}",
            details="TEST-ONLY record; not clinical guidance.",
        )
        db_session.add(event)
        db_session.flush()
        event_id = event.id

        # Commit so persistence can be verified with fresh database reads.
        db_session.commit()
        db_session.expire_all()

        saved_source = db_session.get(HealthSource, source_id)
        saved_document = db_session.get(KnowledgeDocument, document_id)
        saved_version = db_session.get(DocumentVersion, version_id)
        saved_review = db_session.get(ClinicalReviewRecord, review_id)
        saved_event = db_session.get(KnowledgeAuditEvent, event_id)

        assert saved_source is not None
        assert saved_source.name == source_name

        assert saved_document is not None
        assert saved_document.source_id == source_id
        assert saved_document.title == document_title

        assert saved_version is not None
        assert saved_version.document_id == document_id
        assert saved_version.version_number == 1
        assert saved_version.content_fingerprint == fingerprint

        assert saved_review is not None
        assert saved_review.document_version_id == version_id
        assert saved_review.decision == "changes_requested"

        assert saved_event is not None
        assert saved_event.entity_id == str(version_id)
        assert saved_event.event_type == "test_persistence"

        # Verify duplicate version numbers are rejected.
        duplicate = DocumentVersion(
            document_id=document_id,
            version_number=1,
            content="TEST-ONLY duplicate version.",
            content_fingerprint=uuid.uuid4().hex * 2,
        )
        db_session.add(duplicate)

        with pytest.raises(IntegrityError):
            db_session.flush()

        # Recover from the expected integrity error.
        db_session.rollback()

    finally:
        # Clean up only the records created by this test.
        # Document versions cannot be deleted while the immutability
        # trigger is active, so use transactional DDL for local test cleanup.
        db_session.rollback()

        if version_id is not None:
            try:
                db_session.execute(
                    text(
                        """
                        DROP TRIGGER IF EXISTS
                        trg_document_versions_immutable
                        ON document_versions
                        """
                    )
                )

                if event_id is not None:
                    db_session.execute(
                        KnowledgeAuditEvent.__table__.delete().where(
                            KnowledgeAuditEvent.id == event_id
                        )
                    )

                if review_id is not None:
                    db_session.execute(
                        ClinicalReviewRecord.__table__.delete().where(
                            ClinicalReviewRecord.id == review_id
                        )
                    )

                db_session.execute(
                    DocumentVersion.__table__.delete().where(
                        DocumentVersion.id == version_id
                    )
                )

                if document_id is not None:
                    db_session.execute(
                        KnowledgeDocument.__table__.delete().where(
                            KnowledgeDocument.id == document_id
                        )
                    )

                if source_id is not None:
                    db_session.execute(
                        HealthSource.__table__.delete().where(
                            HealthSource.id == source_id
                        )
                    )

                # Restore the trigger before committing cleanup.
                db_session.execute(
                    text(
                        """
                        CREATE TRIGGER trg_document_versions_immutable
                        BEFORE UPDATE OR DELETE ON document_versions
                        FOR EACH ROW
                        EXECUTE FUNCTION prevent_document_version_mutation()
                        """
                    )
                )

                db_session.commit()

            except Exception:
                # PostgreSQL transactional DDL rolls back the trigger
                # changes and cleanup operations together.
                db_session.rollback()
                raise
