# R04 Implementation Scope and Execution Plan

**Project:** HIV/SRH Education Chatbot  
**Phase:** R04 — Knowledge Content Readiness  
**Checkpoint:** R04.7.5.3 — Implementation Scope and Execution Plan  
**Status:** Proposed implementation plan; authorization pending

## 1. Purpose

This document defines the proposed implementation scope for the approved R04 database and persistent knowledge-ingestion changes.

It identifies expected application files, database models, migration work, tests, implementation sequence, and verification requirements.

This is an implementation plan only. It does not authorize code modifications or database migration.

## 2. Approved design baseline

Implementation must follow:

- `docs/R04_KNOWLEDGE_BASE_AUDIT.md`
- `docs/R04_KNOWLEDGE_CONTENT_REQUIREMENTS.md`
- `docs/R04_SOURCE_STRATEGY.md`
- `docs/R04_KNOWLEDGE_DOCUMENT_STANDARD.md`
- `docs/R04_BILINGUAL_CONTENT_POLICY.md`
- `docs/R04_CLINICAL_KNOWLEDGE_GOVERNANCE.md`
- `docs/R04_INGESTION_SERVICE_DESIGN.md`
- `docs/R04_DATABASE_MIGRATION_ASSESSMENT.md`
- `docs/R04_DATABASE_MIGRATION_PLAN.md`
- `docs/R04_MIGRATION_IMPLEMENTATION_SPECIFICATION.md`
- `docs/R04_MIGRATION_RISK_AND_READINESS_REVIEW.md`
- `docs/R04_FINAL_MIGRATION_DESIGN.md`
- `docs/R04_APPROVED_IMPLEMENTATION_DECISIONS.md`

The approved decisions D01–D08 are binding unless formally revised.

## 3. Implementation objectives

The implementation is intended to deliver:

1. Multiple topics per knowledge document.
2. Structured permission evidence in immutable version snapshots.
3. A persistent candidate-ingestion service.
4. Explicit source and metadata validation.
5. Safe idempotency and version-conflict handling.
6. Transaction-safe document, topic, version, and audit persistence.
7. Preservation of clinical review separation.
8. Preservation of existing retrieval and immutability protections.

## 4. Proposed application files

The following files are expected to require inspection and potentially modification.

| File | Proposed change |
|---|---|
| `app/db/models.py` | Add document-topic association model and relationships |
| `app/db/repository.py` | Add topic persistence and lookup operations |
| `app/knowledge/ingestion.py` | Retain and, if needed, extend candidate validation |
| `app/knowledge/persistent_review_workflow.py` | Integrate permission evidence into new version snapshots without weakening review safeguards |
| `app/knowledge/persistent_retrieval.py` | Update topic access if required by the new authoritative representation |
| New `app/knowledge/persistent_ingestion.py` | Implement persistent candidate-ingestion service |

The exact file scope must be confirmed by inspecting the current repository immediately before implementation.

No unrelated files should be modified.

## 5. Proposed database migration

Create one new Alembic revision after:

`2833c9394364`

The migration is expected to:

1. Create `knowledge_document_topics`.
2. Add the document foreign key.
3. Add unique `(document_id, topic)` constraint.
4. Add required indexes.
5. Preserve the legacy `knowledge_documents.topic` column.
6. Preserve existing document and version records.
7. Preserve existing review snapshots.
8. Preserve the unique document-version constraint.
9. Preserve the PostgreSQL immutability trigger and function.

The migration must not rewrite immutable historical snapshots.

The migration must use an explicit legacy-topic mapping.

Unknown topic values must be reported and resolved rather than guessed.

## 6. Permission evidence implementation

Permission evidence will be stored in new immutable document-version snapshots.

The approved permission statuses are:

- `permitted`
- `restricted`
- `prohibited`
- `unknown`

Required evidence fields:

- `permission_status`
- `permission_basis`
- `permission_reference`
- `permission_checked_at`
- `permission_checked_by`
- `permission_notes`

Validation must ensure:

- Status is from the approved vocabulary.
- Evidence is sufficient for the selected status.
- Verification timestamp is valid and timezone-aware.
- Permission is not inferred from a URL.
- Insufficient evidence cannot satisfy new approval requirements.

Historical snapshots must remain unchanged.

## 7. Persistent ingestion service

Proposed module:

`app/knowledge/persistent_ingestion.py`

Proposed class:

`PersistentKnowledgeIngestionService`

Responsibilities:

1. Accept a validated candidate.
2. Resolve the registered source.
3. Verify source metadata consistency.
4. Validate permission evidence.
5. Validate all topic identifiers.
6. Resolve document identity.
7. Detect duplicate and conflicting versions.
8. Persist the document.
9. Persist topic associations.
10. Create the immutable version and review snapshot.
11. Record an audit event.
12. Leave the document pending clinical review.

The service must not create clinical approval decisions.

## 8. Transaction and idempotency behavior

The caller owns the outer transaction.

The ingestion service must:

- Operate within the caller's transaction.
- Avoid independent commits.
- Raise clear errors for invalid or conflicting operations.
- Allow the caller to roll back the complete operation.
- Avoid partial persistence.

Exact duplicate ingestion must be handled idempotently.

A conflicting request under an existing document/version must be rejected.

Duplicate-request audit behavior must be deterministic.

## 9. Proposed test files

Existing test files to inspect and potentially extend:

- `tests/test_knowledge_ingestion.py`
- `tests/test_knowledge_lifecycle_integration.py`
- `tests/test_persistent_review_workflow.py`

Additional tests may be introduced where needed, including:

- Persistent ingestion service tests.
- Topic association model and repository tests.
- Alembic migration tests.
- Permission evidence validation tests.
- Transaction rollback and idempotency tests.

The exact test file names must follow the existing repository conventions.

## 10. Required test scenarios

### 10.1 Topic persistence

- One document with one topic.
- One document with multiple topics.
- Duplicate topic rejection.
- Unknown topic rejection.
- Foreign-key enforcement.
- Legacy-topic mapping.
- Existing topic preservation.

### 10.2 Permission evidence

- All approved status values.
- Missing evidence.
- Invalid status.
- Invalid timestamp.
- Insufficient evidence.
- Historical snapshot preservation.
- Approval blocked when required evidence is missing.

### 10.3 Persistent ingestion

- Successful candidate ingestion.
- Unknown source.
- Source metadata mismatch.
- Invalid language.
- Invalid topic.
- Retired source or document.
- Exact duplicate request.
- Conflicting version.
- Audit event creation.
- Pending-review state.
- No automatic approval.

### 10.4 Transaction safety

- Failure during document persistence.
- Failure during topic persistence.
- Failure during version creation.
- Failure during snapshot creation.
- Failure during audit recording.
- Full rollback.
- Caller-owned transaction behavior.

### 10.5 Regression

- Existing clinical review tests.
- Persistent retrieval tests.
- Document-version immutability tests.
- Knowledge lifecycle integration tests.
- Existing API and schema tests.
- Full project test suite.

## 11. Implementation sequence

Implementation will be divided into separately approved checkpoints.

| Step | Work | Authorization |
|---|---|---|
| R04.7.6.1 | Final repository inspection | Pending |
| R04.7.6.2 | Confirm exact code and test file scope | Pending |
| R04.7.6.3 | Implement topic association model and repository | Pending |
| R04.7.6.4 | Create and test Alembic migration on disposable database | Separate approval required |
| R04.7.6.5 | Implement permission evidence validation | Pending |
| R04.7.6.6 | Implement persistent ingestion service | Pending |
| R04.7.6.7 | Add transaction and idempotency tests | Pending |
| R04.7.6.8 | Run regression and integration tests | Pending |
| R04.7.6.9 | Final implementation review | Pending |

No step automatically authorizes the next.

## 12. Database safety requirements

Before applying any migration:

1. Confirm the actual database environment.
2. Confirm the current Alembic revision.
3. Use a disposable database for migration development.
4. Create and verify a backup of any database containing valuable data.
5. Test restoration.
6. Record existing document, version, and topic counts.
7. Verify existing constraints and trigger state.
8. Test migration upgrade.
9. Test rollback restrictions.
10. Obtain explicit authorization for any persistent or production migration.

Never execute an unreviewed migration against the production database.

## 13. Verification gates

Each implementation checkpoint must provide:

- Files changed.
- Reason for every change.
- Complete relevant code or patch.
- Tests added or updated.
- Exact PowerShell verification commands.
- Actual test results.
- Any warnings or failures.
- Confirmation that unrelated behavior was not modified.

The full regression suite must pass before implementation closure.

## 14. Out-of-scope work

The following are not included in this implementation plan:

- User authentication redesign.
- Conversation-history implementation.
- Frontend redesign.
- Vector database or semantic search introduction.
- New clinical content authoring.
- Automatic clinical approval.
- Production deployment.
- Removal of the legacy topic column.
- Changes to unrelated application modules.

These require separate planning and approval.

## 15. Implementation completion criteria

The planned implementation will be considered technically complete when:

- Multiple topics are stored and retrieved correctly.
- Legacy topic data is preserved.
- Permission evidence is validated and stored in new immutable snapshots.
- Historical snapshots remain unchanged.
- Persistent ingestion is transaction-safe.
- Idempotency and version conflicts work correctly.
- Audit events are traceable.
- Clinical approval remains separate.
- Existing immutability protections remain active.
- Migration and integration tests pass.
- Full regression tests pass.
- Recovery procedures are documented.

## 16. Current authorization status

- R04 design decisions D01–D08: Approved.
- Implementation scope: Proposed.
- Repository implementation: Not authorized.
- Alembic revision creation: Not authorized.
- Database migration: Not authorized.
- Production deployment: Not authorized.

Each implementation checkpoint requires explicit project-owner approval.

## 17. Approval record

- Document prepared: Yes.
- Project-owner review: Pending.
- Implementation scope approval: Pending.
- Code modification authorization: Not granted.
- Database migration authorization: Not granted.