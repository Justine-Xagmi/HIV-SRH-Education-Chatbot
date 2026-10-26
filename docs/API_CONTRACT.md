# HIV/SRH Education Chatbot — API Contract

**Phase:** 2 — Requirements and Design
**Step:** 3 — API Contract Design
**Status:** Final draft — approval pending
**Version:** 1.1

## 1. Purpose

This document defines the proposed HTTP API endpoints, request and response formats, validation rules, and error-handling conventions.

This is a design specification. Endpoints described as proposed are not implemented merely because they appear here.

## 2. API Conventions

- Framework: Python and FastAPI.
- Proposed API prefix: `/api/v1`.
- Request and response format: JSON, except where otherwise documented.
- Supported language codes: `en` (English) and `sw` (Kiswahili).
- Chat requests must explicitly specify a supported language.
- Input must be validated before processing.
- Health-related answers must be grounded in approved sources once the knowledge service is implemented.
- This contract does not authorize persistent conversation storage.

## 3. Existing Endpoints

### 3.1 GET /

Purpose: Confirm that the application is running.

The existing response structure must remain unchanged:

{
  "message": "HIV/SRH Education Chatbot API is running.",
  "docs": "/docs"
}

### 3.2 GET /health

Purpose: Check application availability.

The existing response structure must remain unchanged:

{
  "status": "ok",
  "application": "HIV_SRH_Education_Chatbot"
}

This endpoint does not, by itself, establish that an AI provider or knowledge base is available.

## 4. Proposed Endpoint: GET /api/v1/languages

Purpose: Return the languages supported by the application.

Proposed successful response:

{
  "languages": [
    {"code": "en", "name": "English"},
    {"code": "sw", "name": "Kiswahili"}
  ]
}

Proposed status code: 200 OK.

## 5. Proposed Endpoint: POST /api/v1/chat

Purpose: Accept an educational HIV/SRH question and return a response.

### 5.1 Request schema

Proposed JSON request:

{
  "message": "How can HIV be prevented?",
  "language": "en"
}

Fields:

- `message`: required string, trimmed value must not be empty, maximum 2,000 characters.
- `language`: required string, allowed values are `en` and `sw`. No default is permitted.

A request that omits `language`, provides an unsupported language code, or supplies an invalid field type must be rejected.

### 5.2 Successful response schema

Proposed JSON response:

{
  "answer": "Educational response text.",
  "language": "en",
  "sources": [],
  "safety_notice": "This chatbot provides educational information, not a medical diagnosis."
}

Fields:

- `answer`: educational response or an appropriate safe fallback.
- `language`: language used for the response.
- `sources`: array of verified sources actually used to support the answer.
- `safety_notice`: notice explaining the educational purpose and limitations of the service.

An empty `sources` array must not be interpreted as proof that an answer is evidence-based.

A source entry may contain:

- `title`: source document or page title.
- `organization`: publishing organization, when known.
- `url`: verified source URL, when available.
- `reviewed_at`: content-review date, when available.

The final source-entry schema must be confirmed before implementation. The application must not invent source details or imply that a source supports a claim when it does not.

Proposed successful status code: 200 OK.

### 5.3 Validation rules

- Reject missing, empty, or whitespace-only messages.
- Reject messages exceeding 2,000 characters.
- Reject requests that omit `language`.
- Reject unsupported language codes.
- Reject malformed JSON and invalid field types.
- Do not request unnecessary personal or identifying information.
- Do not treat user-provided text as verified medical evidence.
- Do not return fabricated medical answers or citations when reliable supporting evidence is unavailable.

The implementation must apply consistent validation and safe error responses.

## 6. Standardized Error Handling

Errors shall use the following response envelope:

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid fields."
  }
}

The fields are:

- `error.code`: stable machine-readable error identifier.
- `error.message`: safe, understandable description of the problem.

Proposed status-code mapping:

| HTTP status | Meaning |
|---|---|
| 400 | Invalid request that cannot be processed |
| 422 | Request fields fail validation |
| 429 | Rate limit exceeded, if rate limiting is implemented |
| 500 | Unexpected internal application error |
| 503 | Required service temporarily unavailable |

The final mapping of framework-generated validation errors to this envelope must be tested during implementation.

Error responses must not expose secrets, stack traces, sensitive user content, or internal implementation details.

## 7. Safety and Privacy Behavior

- The chat endpoint provides education, not diagnosis or individualized treatment decisions.
- Questions requiring professional assessment must receive an appropriate limitation or referral response.
- Unsupported health questions must not trigger fabricated answers or citations.
- Urgent-situation guidance must follow an approved safety policy.
- This API contract does not authorize persistent conversation storage.
- Logging, retention, consent, deletion, and external AI-provider data handling remain subject to privacy review.
- Any future storage or external-service integration must follow approved privacy and security requirements.

## 8. Compatibility and Versioning

- Existing `GET /` and `GET /health` responses must remain compatible with the Phase 1 baseline.
- New chatbot endpoints will use the `/api/v1` prefix.
- Breaking changes to public request or response schemas require deliberate versioning and tests.
- FastAPI's OpenAPI documentation should describe implemented endpoints and schemas.

## 9. Proposed API Acceptance Tests

Before the endpoints are considered implemented, tests should verify:

1. Existing root and health endpoints retain their current behavior.
2. The languages endpoint returns both supported languages.
3. A valid English request is accepted.
4. A valid Kiswahili request is accepted.
5. Missing language is rejected.
6. Unsupported language codes are rejected.
7. Empty and whitespace-only messages are rejected.
8. Messages exceeding 2,000 characters are rejected.
9. Invalid request bodies return the standardized error envelope.
10. Response language and source structure match the contract.
11. Safe fallback behavior is tested when supporting evidence is unavailable.
12. Errors do not reveal secrets or sensitive internal details.
13. Tests do not require real medical claims or unverified sources.

## 10. Decisions Register

| Decision | Status |
|---|---|
| Existing root and health endpoint compatibility | Required |
| API prefix | Proposed: `/api/v1` |
| Maximum message length | Decided: 2,000 characters |
| Language field | Required |
| Supported language values | `en`, `sw` |
| Default language | None |
| Error format | Standardized error envelope |
| Final source-entry fields | Open |
| Rate-limiting requirements | Open |
| Detailed safety and referral rules | Open |
| Conversation storage and logging policy | Open |

## 11. Approval Record

**Status:** Final draft for review.

**Project owner approval:** Pending.

**Approval date:** Pending.