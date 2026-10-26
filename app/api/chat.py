
from fastapi import APIRouter

from app.api.schemas import ChatRequest, ChatResponse
from app.knowledge.store import knowledge_registry

router = APIRouter(
    prefix="/api/v1",
    tags=["Chat"],
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


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Return matching content only from approved documents and sources."""

    documents = knowledge_registry.retrieve(
        query=request.message,
        language=request.language,
        limit=5,
    )

    # Defensive checks: only include documents whose source language
    # also matches the requested language and whose review is approved.
    approved_documents = [
        document
        for document in documents
        if (
            document.review_status == "approved"
            and document.source.review_status == "approved"
            and document.language == request.language
            and document.source.language == request.language
        )
    ]

    if not approved_documents:
        return _fallback_response(request.language)

    answer = "\n\n".join(
        document.content for document in approved_documents
    )

    sources = [
        {
            "title": document.source.title,
            "organization": document.source.organization,
            "url": str(document.source.url),
        }
        for document in approved_documents
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
