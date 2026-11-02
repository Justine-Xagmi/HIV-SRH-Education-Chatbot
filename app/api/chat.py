
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.schemas import ChatRequest, ChatResponse
from app.db import session as db_session
from app.knowledge.persistent_retrieval import (
    PersistentKnowledgeRetriever,
)

router = APIRouter(
    prefix="/api/v1",
    tags=["Chat"],
)


def _service_unavailable() -> HTTPException:
    """Create a generic error without exposing internal details."""
    return HTTPException(
        status_code=503,
        detail=(
            "The health information service is temporarily "
            "unavailable. Please try again later."
        ),
    )


def _fallback_response(language: str) -> ChatResponse:
    """Return a safe response when approved information is unavailable."""

    if language == "sw":
        return ChatResponse(
            answer=(
                "Samahani, hakuna taarifa za afya zilizoidhinishwa "
                "zinazolingana na swali lako katika mfumo kwa sasa. "
                "Tafadhali wasiliana na mtaalamu wa afya kwa taarifa "
                "zinazofaa."
            ),
            language="sw",
            sources=[],
            safety_notice=(
                "Kwa elimu ya jumla pekee. Huu si ushauri wa kitabibu."
            ),
        )

    return ChatResponse(
        answer=(
            "Sorry, no approved health information matching your "
            "question is currently available in this system. Please "
            "consult a qualified healthcare professional for "
            "appropriate information."
        ),
        language="en",
        sources=[],
        safety_notice=(
            "For general education only. This is not medical advice."
        ),
    )


def get_knowledge_retriever(
) -> Generator[PersistentKnowledgeRetriever, None, None]:
    """Provide a database-backed retriever and manage its session."""

    if db_session.SessionLocal is None:
        raise _service_unavailable()

    db: Session | None = None

    try:
        db = db_session.SessionLocal()
        yield PersistentKnowledgeRetriever(db)
    except SQLAlchemyError as exc:
        raise _service_unavailable() from exc
    finally:
        if db is not None:
            db.close()


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    retriever: PersistentKnowledgeRetriever = Depends(
        get_knowledge_retriever
    ),
) -> ChatResponse:
    """Return information only from eligible, approved database documents."""

    try:
        documents = retriever.retrieve(
            query=request.message,
            language=request.language,
            limit=5,
        )
    except SQLAlchemyError as exc:
        raise _service_unavailable() from exc

    if not documents:
        return _fallback_response(request.language)

    answer = "\n\n".join(document.content for document in documents)

    sources = [
        {
            "title": document.source_title,
            "organization": document.source_organization or "",
            "url": document.source_url,
        }
        for document in documents
    ]

    if request.language == "sw":
        safety_notice = (
            "Kwa elimu ya jumla pekee. Huu si ushauri wa kitabibu. "
            "Tafadhali wasiliana na mtaalamu wa afya kwa ushauri "
            "unaokufaa."
        )
    else:
        safety_notice = (
            "For general education only. This is not medical advice. "
            "Consult a qualified healthcare professional for advice "
            "specific to your situation."
        )

    return ChatResponse(
        answer=answer,
        language=request.language,
        sources=sources,
        safety_notice=safety_notice,
    )
