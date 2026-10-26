# HIV/SRH Education Chatbot — System Architecture

**Phase:** 2 — Requirements and Design
**Step:** 2 — System Architecture Design
**Status:** Draft for review
**Version:** 1.0

## 1. Purpose

This document describes the proposed architecture for the HIV/SRH Education Chatbot. It defines the main components, their responsibilities, and how information will flow through the application.

The design builds on the existing Python and FastAPI project baseline. It does not claim that the proposed components have already been implemented.

## 2. Architecture Principles

- Use modular components with clear responsibilities.
- Ground health-related answers in approved and reviewed sources.
- Support English and Kiswahili.
- Validate user requests and handle errors safely.
- Avoid unsupported medical claims and fabricated citations.
- Minimize collection and retention of personal information.
- Keep application secrets outside source code.
- Test individual components and the complete request flow.
- Do not implement unresolved privacy or clinical-policy decisions without approval.

## 3. Proposed Components

### 3.1 User Interface

The interface will allow users to submit questions and read responses in English or Kiswahili.

The interface technology has not yet been selected.

### 3.2 API Layer

The existing FastAPI application will expose endpoints for chatbot interactions and service health checks.

Responsibilities:
- Validate incoming requests.
- Return structured responses.
- Handle invalid input and application errors.
- Provide API documentation during development.

### 3.3 Configuration Layer

The existing configuration module will manage environment-specific settings, supported languages, and application configuration.

Secrets must not be committed to source control.

### 3.4 Safety and Language Layer

This component will apply approved safety rules, handle unsupported requests, and support appropriate English and Kiswahili responses.

It must not diagnose conditions, prescribe treatment, or replace professional healthcare.

Clinical safety rules and referral responses must be reviewed before deployment.

### 3.5 Knowledge Base

The knowledge base will contain approved educational material covering the nine topics in the requirements specification.

Each source should be assessed for authority, relevance, currency, and suitability. A content-review process must be established before material is treated as approved.

### 3.6 Retrieval Service

The proposed retrieval service will search the approved knowledge base for information relevant to a user's question.

Retrieval-augmented generation (RAG) is a proposed approach. The retrieval technology and indexing strategy have not yet been selected.

### 3.7 Answer Generation and Validation

A future answer-generation component may use retrieved material to draft responses.

Before a response is returned, the system should apply appropriate validation for:
- Relevance to the question.
- Support from approved sources.
- Source attribution.
- Language quality.
- Safety and uncertainty.
- Appropriate referral when needed.

The model provider and generation technology remain undecided.

### 3.8 Data and Privacy Layer

Persistent conversation storage is not authorized by this draft.

The design must not assume that conversations will be saved. Any future storage, logging, analytics, consent, retention, or deletion feature requires an approved privacy design.

### 3.9 Testing and Evaluation

The project will use automated tests and dedicated evaluations to assess API behavior, retrieval quality, source grounding, language quality, and health safety.

Passing API tests alone does not establish medical accuracy.

## 4. Proposed Request Flow

1. A user submits an HIV/SRH question in English or Kiswahili.
2. The API validates the request.
3. The safety layer checks whether the request can be handled within the approved scope.
4. The retrieval service searches approved material when retrieval is available.
5. The answer-generation component drafts a response from relevant evidence, if that component has been approved and implemented.
6. The validation layer checks the response and source attribution.
7. The API returns the response or an appropriate safe fallback or referral.

If adequate evidence cannot be found, the chatbot should not invent an answer or citation.

## 5. Proposed Component Boundaries

The application should keep these responsibilities separate as implementation progresses:

- API routes: HTTP requests and responses.
- Request and response schemas: input validation and output structure.
- Safety services: approved safety rules and fallback behavior.
- Knowledge services: approved source management and retrieval.
- Answer services: response generation and validation.
- Configuration: environment settings.
- Tests: verification of expected behavior.

The exact directory structure and interfaces will be confirmed before implementation.

## 6. Security and Privacy Considerations

- Keep secrets in environment configuration.
- Validate all incoming requests.
- Avoid unnecessary collection of identifying or sensitive information.
- Avoid exposing sensitive information in logs or error responses.
- Review any external model or hosting provider for data-handling implications.
- Decide conversation retention and deletion policies before implementing persistent storage.
- Review applicable Tanzanian data-protection obligations before deployment.

## 7. Dependencies and External Services

The current FastAPI baseline will be retained.

No additional database, vector store, model provider, or external service is selected by this document. Any proposed dependency must be justified, reviewed for compatibility with the existing environment, and approved before installation.

## 8. Open Architecture Decisions

1. User interface technology.
2. Approved health sources and content-review responsibility.
3. Retrieval and indexing technology.
4. Model provider and answer-generation approach.
5. Conversation storage and logging policy.
6. Referral information and service-verification process.
7. Deployment platform and operational requirements.
8. Performance, security, and evaluation thresholds.

These decisions must be resolved at the appropriate design checkpoints before affected features are implemented or deployed.

## 9. Architecture Acceptance Criteria

The architecture draft is ready for review when:

- Each major component has a clear responsibility.
- The proposed request flow is documented.
- The design reflects the approved requirements.
- Unresolved health-safety and privacy decisions remain explicitly identified.
- No unapproved technology or feature is represented as already implemented.
- The project owner explicitly approves the architecture.

## 10. Approval Record

**Status:** Draft for review.

**Project owner approval:** Pending.

**Approval date:** Pending.
