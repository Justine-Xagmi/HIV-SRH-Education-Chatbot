# R04 Final Migration Design

**Project:** HIV/SRH Education Chatbot  
**Phase:** R04 — Knowledge Content Readiness  
**Checkpoint:** R04.7.4.5 — Final Migration Design Consolidation  
**Status:** Consolidated design; implementation authorization pending

## 1. Purpose

This document consolidates the approved R04 database migration assessments, design decisions, implementation requirements, and risk controls into one reference.

It is intended to guide the later implementation of:

1. Multiple topics per knowledge document.
2. Structured source-permission evidence.
3. Persistent knowledge ingestion.
4. Immutable document-version preservation.
5. Transaction-safe ingestion and audit recording.
6. Migration testing, backup, rollback, and recovery.

This document does not authorize implementation or database migration.

## 2. Existing technical baseline

The project currently uses:

- Python 3.11.
- FastAPI.
- SQLAlchemy ORM.
- PostgreSQL.
- Alembic 1.20.1.
- SQLAlchemy declarative models.
- Persistent knowledge documents and sources.
- Immutable document versions.
- Clinical review history.
- Knowledge audit events.
- JSON review snapshots.

The verified current Alembic revision is:

`2833c9394364`

The existing database includes:

- A unique constraint on document ID and version number.
- A PostgreSQL document-version immutability trigger.
- The trigger function `prevent_document_version_mutation`.
- A JSON `review_snapshot` field on document versions.

These protections must remain intact.

## 3. Consolidated design decisions

### 3.1 Multiple topics per document

Introduce a new association table:

`knowledge_document_topics`

Proposed fields:

- `id`
- `document_id`
- `topic`
- `created_at`

Required database protections:

- Foreign key to `knowledge_documents`.
- Unique constraint on `(document_id, topic)`.
- Index on `document_id`.
- Index on `topic`.

The legacy `knowledge_documents.topic` column will remain temporarily for compatibility.

The new association table will become the authoritative representation after the application transition is completed and verified.

The implementation must not allow independent writes to the old and new representations.

### 3.2 Controlled topic vocabulary

Use the following stable identifiers:

| Identifier | Meaning |
|---|---|
| `hiv_prevention` | HIV prevention |
| `hiv_testing` | HIV testing |
| `hiv_treatment` | HIV treatment education |
| `stigma_discrimination` | Stigma and discrimination |
| `sexual_health` | Sexual health |
| `contraception` | Contraception and family planning |
| `pregnancy_reproductive_health` | Pregnancy and reproductive health |
| `other_stis` | STIs other than HIV |
| `other_srh` | Other sexual and reproductive health topics |

All topic identifiers must be validated before persistence.

Unknown or unmapped legacy values must be reported and resolved explicitly. They must not be silently discarded or converted into a guessed category.

### 3.3 Structured permission evidence

Store structured permission evidence in the immutable `DocumentVersion.review_snapshot` JSON field.

Proposed fields:

- `permission_status`
- `permission_basis`
- `permission_reference`
- `permission_checked_at`
- `permission_checked_by`
- `permission_notes`

Requirements:

- Evidence must be appropriate to the permission status.
- Verification timestamps must be valid and timezone-aware.
- Permission must not be inferred from a source URL.
- Confidential correspondence and unnecessary personal information must not be stored.
- Insufficient evidence must prevent new clinical approval under the updated policy.

Existing immutable snapshots must not be rewritten to add missing evidence.

### 3.4 Persistent knowledge ingestion service

Introduce:

`PersistentKnowledgeIngestionService`

The service will coordinate:

1. Candidate validation.
2. Registered source resolution.
3. Source metadata matching.
4. Permission evidence validation.
5. Topic validation.
6. Document persistence.
7. Topic association persistence.
8. Immutable version creation.
9. Review snapshot creation.
10. Audit event recording.

The service must not approve clinical content.

Newly ingested documents must remain pending clinical review.

### 3.5 Idempotency and version conflicts

The service must distinguish:

- Exact duplicate ingestion.
- Conflicting content under an existing version.
- Conflicting source or metadata.
- New document versions.

An exact duplicate may be handled idempotently.

Different content or metadata under an already-used version must be rejected rather than silently overwriting the existing version.

### 3.6 Transaction boundary

Document, topic, version, snapshot, and audit writes must form one logical transaction.

The implementation must explicitly define transaction ownership.

A failure during any stage must not leave partial ingestion records.

Nested transaction behavior must be tested, and the service must not commit prematurely when the caller owns the outer transaction.

## 4. Migration architecture

The planned migration sequence is:

1. Inspect the current database schema and migration revision.
2. Inventory existing documents and topic values.
3. Prepare and approve the legacy-topic mapping.
4. Back up the database.
5. Add the document-topic association table.
6. Add required constraints and indexes.
7. Preserve the legacy topic column.
8. Preserve existing document-version snapshots.
9. Preserve the immutability trigger and unique version constraint.
10. Validate migrated topic assignments.
11. Implement the persistent ingestion service.
12. Run integration and regression tests.
13. Verify retrieval and review behavior.
14. Document the migration result.

The new Alembic revision must have:

`down_revision = "2833c9394364"`

No migration file has been authorized or created by this design document.

## 5. Legacy data handling

Existing records require explicit treatment.

### 5.1 Existing topics

- Inventory all existing topic values.
- Map known values using an approved mapping.
- Report unknown values.
- Resolve unmapped values before completing the migration.
- Compare document and topic counts before and after migration.

### 5.2 Existing permission evidence

Existing immutable snapshots may not contain structured permission evidence.

Such records must not be treated as if their permission has been verified.

They must undergo a separate evidence assessment before new approval under the updated policy.

### 5.3 Existing document approvals

Existing clinical review history must be preserved.

The migration must not create new approval decisions or change existing review decisions.

Existing approval status and new permission-evidence requirements must be evaluated separately.

## 6. Compatibility strategy

During the transition:

- Preserve the legacy topic column.
- Establish the new association table as the intended authoritative topic representation.
- Define a single application write path.
- Avoid independent dual writes.
- Update readers through a controlled compatibility approach.
- Test all affected repository, retrieval, review, and ingestion operations.

Removal of the legacy column requires a separate assessment and explicit approval.

## 7. Immutability and audit protection

The implementation must preserve:

- Existing document-version records.
- Existing review snapshots.
- Existing unique document/version constraint.
- Existing PostgreSQL trigger.
- Existing trigger function.
- Clinical review history.
- Knowledge audit events.

The implementation must not bypass immutability protections to simplify migration.

New ingestion operations must produce traceable audit events.

## 8. Required implementation tests

### 8.1 Database migration tests

- Upgrade from the current migration head.
- Association table creation.
- Foreign-key enforcement.
- Unique topic assignment.
- Index creation.
- Legacy-topic mapping.
- Existing record preservation.
- Trigger preservation.
- Downgrade behavior.

### 8.2 Permission evidence tests

- Valid permission evidence.
- Missing permission evidence.
- Invalid permission status.
- Invalid timestamp.
- Insufficient permission reference.
- Historical snapshot preservation.
- Approval blocked when required evidence is missing.

### 8.3 Ingestion service tests

- Successful ingestion.
- Invalid candidate rejection.
- Unknown source rejection.
- Source metadata mismatch.
- Topic validation.
- Multiple topic persistence.
- Exact duplicate ingestion.
- Conflicting version rejection.
- Audit event creation.
- Pending-review status after ingestion.
- No automatic clinical approval.

### 8.4 Transaction tests

- Failure during document persistence.
- Failure during topic persistence.
- Failure during version creation.
- Failure during snapshot creation.
- Failure during audit recording.
- Complete rollback after failure.
- Caller-owned transaction behavior.

### 8.5 Regression tests

- Existing repository tests.
- Persistent retrieval tests.
- Clinical review workflow tests.
- Document-version immutability tests.
- Knowledge lifecycle integration tests.
- Full project test suite.

## 9. Backup, rollback, and recovery

Before migration:

1. Confirm the current migration revision.
2. Create a database backup.
3. Verify backup integrity.
4. Test restoration.
5. Record relevant row counts.
6. Record existing topic values.
7. Record trigger and constraint status.

Rollback must not silently destroy topic assignments or permission evidence.

If a downgrade cannot preserve data safely, it must be blocked until a verified recovery or export procedure exists.

## 10. Security and clinical governance boundaries

The migration does not:

- Verify clinical reviewer qualifications.
- Establish professional registration.
- Approve clinical content.
- Grant source publication permissions.
- Certify translation accuracy.
- Authorize diagnosis or treatment recommendations.

Clinical approval remains separate from technical ingestion.

English and Kiswahili versions require their own language-specific review and approval.

## 11. Unresolved implementation decisions

The following decisions must be resolved before implementation:

1. **Permission-status enumeration:** Final allowed values and their evidence requirements.
2. **Legacy topic mapping:** Complete inventory and explicit mapping of existing values.
3. **Topic authority:** Exact transition point at which the association table becomes the sole authoritative representation.
4. **Topic changes:** Whether changing topics on an already-reviewed document requires a new document version or another governed review event.
5. **Transaction ownership:** Exact service and caller responsibilities for commit and rollback.
6. **Idempotency identity:** Exact fields used to identify an identical ingestion request.
7. **Downgrade restrictions:** Conditions under which a downgrade must be blocked.
8. **Legacy permission assessment:** Workflow for reviewing historical records without structured permission evidence.

These decisions must not be silently assumed during implementation.

## 12. Implementation acceptance criteria

The implementation may be considered technically complete only when:

- Multiple topics persist correctly.
- Legacy topic data is preserved and mapped.
- Permission evidence is captured in new immutable snapshots.
- Existing immutable snapshots remain unchanged.
- Ingestion is transaction-safe.
- Duplicate ingestion is handled safely.
- Conflicting versions are rejected.
- Ingestion never automatically approves clinical content.
- Audit events are recorded.
- Existing retrieval and clinical review behavior remains correct.
- All required tests pass.
- Backup and recovery procedures are verified.

## 13. Scope exclusions

This document does not authorize:

- Application code modifications.
- SQLAlchemy model changes.
- Alembic migration creation.
- Database schema changes.
- Database migration execution.
- Production deployment.
- Clinical content approval.
- Removal of legacy database columns.

Each implementation activity remains subject to its own approved checkpoint.

## 14. Final design decision

The approved design direction is to introduce a normalized document-topic association table, preserve structured permission evidence in immutable version snapshots, and implement a transaction-safe persistent ingestion service that remains separate from clinical approval.

The existing migration history, document versions, review snapshots, clinical review history, audit events, and immutability protections must be preserved.

**Current status:** Final migration design consolidated. Implementation readiness remains conditional on resolving the open decisions and satisfying the documented migration safety requirements.

**Production migration authorization:** Not granted.

## 15. Approval record

- R04.7.4.1 Database migration assessment: Closed.
- R04.7.4.2 Database migration design: Closed.
- R04.7.4.3 Migration implementation specification: Closed.
- R04.7.4.4 Migration risk and readiness review: Closed.
- R04.7.4.5 Final migration design consolidation: Pending project-owner review.
- Application implementation: Not authorized.
- Database migration: Not authorized.
