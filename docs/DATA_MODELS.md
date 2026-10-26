# HIV/SRH Education Chatbot — Data Models and Schema Design

**Phase:** 2 — Requirements and Design
**Step:** 4 — Data Models and Schema Design
**Status:** Draft for review
**Version:** 1.0

## 1. Purpose

This document defines the proposed data structures for chatbot requests, responses, verified health sources, and knowledge documents.

These are design definitions, not implemented application models or database tables.

## 2. Design Principles

- Validate incoming data before processing.
- Require an explicit supported language for every chat request.
- Limit messages to 2,000 characters.
- Return a consistent error structure.
- Distinguish approved health information from unreviewed content.
- Preserve source attribution where available.
- Avoid unnecessary collection of personal and sensitive information.
- Do not assume persistent conversation storage is authorized.
- Keep future database and retrieval technology decisions separate from these logical models.

## 3. Chat Request Model

Proposed model name: `ChatRequest`

| Field | Type | Required | Validation |
|---|---|---|---|
| `message` | String | Yes | Must not be empty or whitespace-only; maximum 2,000 characters |
| `language` | String | Yes | Must be `en` or `sw` |

Example:

{
  "message": "How can HIV be prevented?",
  "language": "en"
}

Example in Kiswahili:

{
  "message": "HIV inaweza kuzuiwaje?",
  "language": "sw"
}

The API must reject a missing language, an unsupported language code, an invalid field type, or a message that exceeds the maximum length.

The system must not silently choose a default language.

## 4. Chat Response Model

Proposed model name: `ChatResponse`

| Field | Type | Required | Description |
|---|---|---|---|
| `answer` | String | Yes | Educational response or safe fallback |
| `language` | String | Yes | Language used in the response: `en` or `sw` |
| `sources` | Array | Yes | Sources actually used to support the response |
| `safety_notice` | String | Yes | Notice explaining the educational purpose and limitations |

Illustrative response:

{
  "answer": "Educational information will appear here.",
  "language": "en",
  "sources": [],
  "safety_notice": "This chatbot provides educational information, not a medical diagnosis."
}

This example is a structural illustration, not medical guidance.

An empty source array must not be presented as evidence that an answer is verified. The application must not fabricate citations.

## 5. Health Source Model

Proposed model name: `HealthSource`

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | String | Yes | Title of the source document or page |
| `organization` | String | Recommended | Publishing organization, when known |
| `url` | String | Recommended | Verified source URL, when available |
| `reviewed_at` | Date or null | No | Date the content was last reviewed |
| `language` | String | Recommended | Language of the source, when known |

A source should only be represented as supporting an answer when it actually supports the relevant information.

The exact source identifier and source-entry schema remain subject to review before implementation.

## 6. Knowledge Document Model

Proposed logical model name: `KnowledgeDocument`

This model describes material considered for inclusion in the educational knowledge base.

| Field | Type | Description |
|---|---|---|
| `document_id` | String | Unique identifier assigned to the document |
| `title` | String | Document title |
| `organization` | String | Publishing organization, when known |
| `source_url` | String or null | Verified location of the original material |
| `language` | String | Language of the document |
| `topics` | Array of strings | Relevant approved topic categories |
| `content` | String | Extracted or prepared educational text |
| `review_status` | String | Content review and approval state |
| `reviewed_at` | Date or null | Most recent review date |
| `last_updated_at` | Date or null | Last known content update date |

Proposed review states:

- `pending_review`: not yet approved for use.
- `approved`: reviewed and approved for the intended use.
- `retired`: no longer approved for retrieval.

Only approved material may be treated as approved health knowledge.

The rules for review ownership, review frequency, and content updates remain open.

## 7. Proposed Source Entry in a Chat Response

A source entry may eventually use this structure:

{
  "title": "Verified source title",
  "organization": "Publishing organization",
  "url": "https://example.org/verified-resource",
  "reviewed_at": null
}

The values above are illustrative placeholders, not a real health source.

A final implementation must validate source URLs and metadata and must not invent source details. The system should distinguish a source's publication or update date from the date on which the project reviewed it.

## 8. Standardized Error Model

Proposed model name: `ErrorResponse`

Structure:

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid fields."
  }
}

| Field | Type | Description |
|---|---|---|
| `error.code` | String | Stable machine-readable error code |
| `error.message` | String | Safe, understandable error description |

Potential error codes include:

- `VALIDATION_ERROR`
- `UNSUPPORTED_LANGUAGE`
- `INVALID_REQUEST`
- `SERVICE_UNAVAILABLE`
- `INTERNAL_ERROR`

The final mapping between validation failures and HTTP status codes must follow the approved API contract.

Error responses must not expose stack traces, credentials, or sensitive information.

## 9. Privacy and Conversation Data

This design does not define a persistent conversation model.

Conversation storage, user accounts for chat history, retention periods, deletion procedures, and analytics storage remain subject to a separate privacy decision.

No persistent conversation database table or model should be created solely on the basis of this document.

## 10. Proposed Logical Relationships

The proposed relationship between the main structures is:

1. A `ChatRequest` contains a user question and an explicit language.
2. The future retrieval service identifies relevant approved `KnowledgeDocument` records.
3. Each selected document may provide metadata represented by a `HealthSource` entry.
4. A `ChatResponse` returns the educational answer, language, applicable sources, and safety notice.
5. If a request fails validation or a required service is unavailable, the API returns an `ErrorResponse`.

These are logical relationships. No database relationships or foreign keys have been implemented.

## 11. Proposed Validation Tests

Before implementing these models, tests should verify:

1. Valid English requests are accepted.
2. Valid Kiswahili requests are accepted.
3. Missing language is rejected.
4. Unsupported language values are rejected.
5. Empty and whitespace-only messages are rejected.
6. Messages up to 2,000 characters are accepted when all other fields are valid.
7. Messages longer than 2,000 characters are rejected.
8. Response objects follow the approved API contract.
9. Source metadata is not fabricated.
10. Only approved knowledge documents are eligible for health-answer retrieval.
11. Error objects follow the standardized error envelope.
12. No persistent conversation storage is introduced without explicit approval.

## 12. Open Decisions

- Final health-source identifier and source-entry schema.
- Approved source organizations and content-review owner.
- Rules for approving, updating, and retiring knowledge documents.
- Knowledge retrieval and indexing technology.
- Whether a separate content-management database is required.
- Conversation logging and storage policy.
- Final API error-code and status-code mapping.

## 13. Approval Record

**Status:** Draft for review.

**Project owner approval:** Pending.

**Approval date:** Pending.
