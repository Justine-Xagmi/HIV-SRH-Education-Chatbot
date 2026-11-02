
from datetime import date, datetime, timezone
from types import SimpleNamespace

from sqlalchemy.exc import SQLAlchemyError
from fastapi.testclient import TestClient

from app.api.chat import get_knowledge_retriever
from app.knowledge.models import HealthSource, KnowledgeDocument
from app.knowledge.registry import KnowledgeRegistry
from app.main import app


client = TestClient(app)

TEST_REVIEWER = "test-authorized-reviewer"
TEST_PREPARER = "test-content-preparer"


def make_document(
    *,
    document_id="hiv-en-001",
    language="en",
    document_status="approved",
    source_status="approved",
    source_language=None,
    content="HIV is a virus that affects the immune system.",
):
    """Create synthetic test content, not clinically verified material."""

    source = HealthSource(
        source_id=f"source-{document_id}",
        title="Test health information",
        organization="Test organization",
        url="https://example.org/health-information",
        language=source_language or language,
        review_status=source_status,
        reviewed_by=(
            "Test reviewer" if source_status == "approved" else None
        ),
        version="test-1",
        publication_date=date(2025, 1, 1),
        last_verified_at=datetime(
            2026, 10, 1, tzinfo=timezone.utc
        ),
        permission_status="permitted",
        permission_basis="Synthetic permission evidence for automated tests.",
        permission_reference="TEST-PERMISSION-001",
        permission_checked_at=datetime(
            2026, 10, 1, tzinfo=timezone.utc
        ),
        permission_checked_by="test-permission-reviewer",
        permission_notes="Test fixture only; not evidence of real-world permission.",
    )

    return KnowledgeDocument(
        document_id=document_id,
        source=source,
        title="HIV information",
        content=content,
        language=language,
        topics=["hiv_prevention"],
        ingestion_status="validated",
        review_status=document_status,
        reviewed_by=(
            "Test reviewer" if document_status == "approved" else None
        ),
    )


def make_registry():
    """Create an isolated registry with a test-only reviewer."""
    return KnowledgeRegistry(
        authorized_reviewer_ids={TEST_REVIEWER}
    )


def add_approved_document(registry, document):
    """
    Add and explicitly approve synthetic test content.

    This simulates a completed review in tests. It does not establish
    that the content is clinically correct or approved for real-world use.
    """
    registry.add_document(document)

    registry.review_document(
        document.document_id,
        reviewer_id=TEST_REVIEWER,
        preparer_id=TEST_PREPARER,
        decision="approved",
        rationale="Synthetic test fixture for automated testing only.",
        language_reviewed=document.language,
    )


class RegistryTestRetriever:
    """
    Adapt the in-memory registry to the persistent retriever's result shape.

    This adapter is only for API tests. Production requests use the
    PersistentKnowledgeRetriever dependency.
    """

    def __init__(self, registry):
        self.registry = registry

    def retrieve(self, query, language, limit=5):
        documents = self.registry.retrieve(
            query=query,
            language=language,
            limit=limit,
        )

        return [
            SimpleNamespace(
                content=document.content,
                source_title=document.source.title,
                source_organization=document.source.organization,
                source_url=str(document.source.url),
            )
            for document in documents
        ]


def use_registry(monkeypatch, registry):
    """Inject a test-only retriever without connecting to PostgreSQL."""
    monkeypatch.setitem(
        app.dependency_overrides,
        get_knowledge_retriever,
        lambda: RegistryTestRetriever(registry),
    )


def test_chat_returns_matching_approved_english_content(monkeypatch):
    registry = make_registry()
    add_approved_document(registry, make_document())
    use_registry(monkeypatch, registry)

    response = client.post(
        "/api/v1/chat",
        json={"message": "What is HIV?", "language": "en"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "en"
    assert "HIV is a virus" in data["answer"]
    assert len(data["sources"]) == 1
    assert data["sources"][0]["title"] == "Test health information"
    assert data["sources"][0]["organization"] == "Test organization"
    assert data["sources"][0]["url"] == (
        "https://example.org/health-information"
    )
    assert "not medical advice" in data["safety_notice"]


def test_chat_returns_matching_approved_kiswahili_content(monkeypatch):
    registry = make_registry()
    document = make_document(
        document_id="hiv-sw-001",
        language="sw",
        content="VVU ni virusi vinavyoathiri mfumo wa kinga ya mwili.",
    )
    add_approved_document(registry, document)
    use_registry(monkeypatch, registry)

    response = client.post(
        "/api/v1/chat",
        json={"message": "VVU ni nini?", "language": "sw"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "sw"
    assert "VVU ni virusi" in data["answer"]
    assert len(data["sources"]) == 1
    assert data["sources"][0]["title"] == "Test health information"
    assert data["sources"][0]["organization"] == "Test organization"
    assert "Huu si ushauri wa kitabibu" in data["safety_notice"]


def test_chat_uses_english_fallback_when_no_content_matches(monkeypatch):
    use_registry(monkeypatch, make_registry())

    response = client.post(
        "/api/v1/chat",
        json={"message": "What is HIV?", "language": "en"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "en"
    assert "no approved health information" in data["answer"]
    assert data["sources"] == []


def test_chat_uses_kiswahili_fallback_when_no_content_matches(monkeypatch):
    use_registry(monkeypatch, make_registry())

    response = client.post(
        "/api/v1/chat",
        json={"message": "VVU ni nini?", "language": "sw"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "sw"
    assert "hakuna taarifa za afya zilizoidhinishwa" in data["answer"]
    assert data["sources"] == []


def test_chat_never_returns_unapproved_document(monkeypatch):
    registry = make_registry()
    registry.add_document(
        make_document(
            document_status="pending_review",
            content="SECRET UNAPPROVED TEST CONTENT",
        )
    )
    use_registry(monkeypatch, registry)

    response = client.post(
        "/api/v1/chat",
        json={"message": "What is HIV?", "language": "en"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "SECRET UNAPPROVED TEST CONTENT" not in data["answer"]
    assert data["sources"] == []
    assert "no approved health information" in data["answer"]


def test_chat_never_returns_document_with_unapproved_source(monkeypatch):
    registry = make_registry()
    registry.add_document(
        make_document(
            source_status="pending_review",
            content="UNAPPROVED SOURCE TEST CONTENT",
        )
    )
    use_registry(monkeypatch, registry)

    response = client.post(
        "/api/v1/chat",
        json={"message": "What is HIV?", "language": "en"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "UNAPPROVED SOURCE TEST CONTENT" not in data["answer"]
    assert data["sources"] == []


def test_chat_excludes_documents_with_mismatched_source_language(
    monkeypatch,
):
    registry = make_registry()
    registry.add_document(
        make_document(
            language="en",
            source_language="sw",
            content="CONTENT WITH MISMATCHED SOURCE LANGUAGE",
        )
    )
    use_registry(monkeypatch, registry)

    response = client.post(
        "/api/v1/chat",
        json={"message": "What is HIV?", "language": "en"},
    )

    assert response.status_code == 200
    data = response.json()
    assert (
        "CONTENT WITH MISMATCHED SOURCE LANGUAGE" not in data["answer"]
    )
    assert data["sources"] == []


def test_chat_rejects_unsupported_language():
    response = client.post(
        "/api/v1/chat",
        json={"message": "Hello", "language": "fr"},
    )

    assert response.status_code == 422


def test_chat_rejects_blank_message():
    response = client.post(
        "/api/v1/chat",
        json={"message": "   ", "language": "en"},
    )

    assert response.status_code == 422


def test_chat_rejects_missing_language():
    response = client.post(
        "/api/v1/chat",
        json={"message": "Hello"},
    )

    assert response.status_code == 422


def test_chat_never_returns_rejected_document(monkeypatch):
    registry = make_registry()
    document = make_document(
        content="SECRET REJECTED HIV TEST CONTENT",
    )
    registry.add_document(document)

    registry.review_document(
        document.document_id,
        reviewer_id=TEST_REVIEWER,
        preparer_id=TEST_PREPARER,
        decision="rejected",
        rationale="Synthetic test rejection.",
        language_reviewed="en",
    )
    use_registry(monkeypatch, registry)

    response = client.post(
        "/api/v1/chat",
        json={"message": "HIV test content", "language": "en"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "SECRET REJECTED HIV TEST CONTENT" not in data["answer"]
    assert data["sources"] == []
    assert "no approved health information" in data["answer"]


def test_chat_never_returns_content_from_retired_source(monkeypatch):
    registry = make_registry()
    document = make_document(
        content="SECRET RETIRED SOURCE HIV TEST CONTENT",
    )
    retired_source = document.source.model_copy(
        update={"review_status": "retired"}
    )
    document = document.model_copy(
        update={"source": retired_source}
    )
    registry.add_document(document)
    use_registry(monkeypatch, registry)

    response = client.post(
        "/api/v1/chat",
        json={"message": "HIV test content", "language": "en"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "SECRET RETIRED SOURCE HIV TEST CONTENT" not in data["answer"]
    assert data["sources"] == []
    assert "no approved health information" in data["answer"]


def test_chat_never_returns_modified_content_without_new_approval(
    monkeypatch,
):
    registry = make_registry()
    document = make_document(
        content="Original approved HIV information for testing.",
    )
    add_approved_document(registry, document)

    modified_document = registry.get_document(
        document.document_id
    ).model_copy(
        update={
            "content": "SECRET MODIFIED HIV INFORMATION FOR TESTING."
        }
    )
    registry.update_document(modified_document)
    use_registry(monkeypatch, registry)

    response = client.post(
        "/api/v1/chat",
        json={"message": "HIV information testing", "language": "en"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "SECRET MODIFIED HIV INFORMATION FOR TESTING." not in data["answer"]
    assert data["sources"] == []
    assert "no approved health information" in data["answer"]


def test_chat_returns_503_when_database_configuration_is_missing(
    monkeypatch,
):
    from app.db import session as db_session

    app.dependency_overrides.pop(get_knowledge_retriever, None)
    monkeypatch.setattr(db_session, "SessionLocal", None)

    response = client.post(
        "/api/v1/chat",
        json={"message": "What is HIV?", "language": "en"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "The health information service is temporarily "
        "unavailable. Please try again later."
    )


def test_chat_returns_503_when_database_query_fails(monkeypatch):
    class FailingRetriever:
        def retrieve(self, query, language, limit=5):
            raise SQLAlchemyError("synthetic database failure")

    monkeypatch.setitem(
        app.dependency_overrides,
        get_knowledge_retriever,
        lambda: FailingRetriever(),
    )

    response = client.post(
        "/api/v1/chat",
        json={"message": "What is HIV?", "language": "en"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "The health information service is temporarily "
        "unavailable. Please try again later."
    )
    assert "synthetic database failure" not in response.text
