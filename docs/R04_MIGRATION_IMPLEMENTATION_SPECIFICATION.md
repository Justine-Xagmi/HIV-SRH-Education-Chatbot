# R04 Migration Implementation Specification

**Project:** HIV/SRH Education Chatbot  
**Phase:** R04 — Knowledge Content Readiness  
**Checkpoint:** R04.7.4.3 — Migration Implementation Specification  
**Status:** Proposed implementation specification — pending approval

## 1. Purpose

This specification translates the approved R04 database migration design into implementation requirements.

It defines the expected SQLAlchemy model changes, Alembic migration structure, ingestion integration, validation rules, transaction handling, and testing requirements.

This document does not authorize implementation or database migration execution.

## 2. Existing technical baseline

The implementation must remain compatible with:

- Python 3.11.
- SQLAlchemy ORM.
- PostgreSQL.
- Alembic 1.20.1.
- The existing shared declarative base.
- The current database repository.
- The existing persistent review workflow.
- The current persistent retrieval implementation.

Current migration head:

`2833c9394364`

Existing database entities:

- `HealthSource`
- `KnowledgeDocument`
- `DocumentVersion`
- `ClinicalReviewRecord`
- `KnowledgeAuditEvent`

Existing integrity protections:

- Unique document/version constraint.
- Immutable document-version trigger.
- Review snapshot storage.
- Clinical review history.
- Knowledge audit events.

Existing functionality must remain operational after implementation.

## 3. Implementation architecture

The proposed implementation will involve four main areas:

1. SQLAlchemy database models.
2. Alembic database migrations.
3. Persistent knowledge ingestion service.
4. Integration and regression tests.

The ingestion service will remain separate from the clinical review workflow.

Proposed processing flow:

Candidate document  
→ Candidate validation  
→ Registered source resolution  
→ Source metadata verification  
→ Permission evidence validation  
→ Document and topic persistence  
→ Immutable document-version creation  
→ Review snapshot creation  
→ Audit event recording  
→ Pending clinical review

The ingestion service must never automatically approve clinical content.

## 4. SQLAlchemy model requirements

### 4.1 KnowledgeDocumentTopic

Introduce a SQLAlchemy model named:

`KnowledgeDocumentTopic`

Proposed table:

`knowledge_document_topics`

Required fields:

| Field | Type | Requirement |
|---|---|---|
| id | Integer | Primary key |
| document_id | Integer | Foreign key to knowledge_documents.id |
| topic | String(100) | Validated topic identifier |
| created_at | DateTime(timezone=True) | Creation timestamp |

Required constraints:

- Primary key on `id`.
- Foreign key on `document_id`.
- Unique constraint on `(document_id, topic)`.
- Index on `document_id`.
- Index on `topic`.

The foreign-key deletion policy must preserve document retention and audit requirements.

### 4.2 Relationships

The `KnowledgeDocument` model should expose a relationship to its topic assignments.

The relationship must:

- Support retrieving all assigned topics.
- Prevent duplicate topic assignments.
- Preserve referential integrity.
- Avoid unintended deletion of knowledge documents.
- Work with existing repository operations.

### 4.3 Legacy topic compatibility

The existing `KnowledgeDocument.topic` field must remain during the initial implementation.

New topic assignments should be written to the association table.

The implementation must define a compatibility strategy for reads and writes so the old and new representations cannot silently diverge.

Removal of the old field is not part of this implementation specification.

## 5. Controlled topic vocabulary

The initial topic identifiers are:

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

Validation requirements:

- Reject unknown identifiers.
- Reject empty or whitespace-only identifiers.
- Reject duplicate topic assignments.
- Require at least one topic for a knowledge document.
- Preserve consistent identifiers across English and Kiswahili documents.

Topic identifiers must be independent of translated display labels.

## 6. Permission evidence implementation

### 6.1 Storage model

Permission evidence should be included in the immutable `DocumentVersion.review_snapshot` JSON structure.

The application must validate the structure before creating a document version.

### 6.2 Required fields

Proposed structure:

- `permission_status`
- `permission_basis`
- `permission_reference`
- `permission_checked_at`
- `permission_checked_by`
- `permission_notes`

The implementation must define accepted values for `permission_status`.

Unknown or unsupported values must not be interpreted as permission to use content.

### 6.3 Validation rules

The implementation must:

1. Require an explicitly supported permission status.
2. Reject blank permission basis where the selected status requires a basis.
3. Validate permission references.
4. Require a timezone-aware verification timestamp when evidence is marked verified.
5. Reject future verification timestamps.
6. Validate the responsible actor identifier.
7. Preserve restrictions and attribution conditions.
8. Avoid storing confidential correspondence or unnecessary personal information.

A URL alone must not be considered proof of permission.

### 6.4 Source and version consistency

Permission evidence must correspond to the exact source and document version being ingested.

The review snapshot must preserve source identity and publication metadata alongside permission evidence.

The application must not replace missing historical permission evidence with fabricated values.

## 7. Immutable document-version requirements

The existing immutable version model and database trigger must remain intact.

The implementation must:

- Create new document versions through the established repository/workflow.
- Preserve version uniqueness.
- Preserve content fingerprints.
- Create review snapshots before clinical review.
- Include permission evidence in new snapshots.
- Avoid updating existing version snapshots.
- Avoid deleting existing versions.

Historical records without complete permission evidence must remain unchanged.

They must not qualify for new approval or retrieval under the updated evidence requirements until the missing evidence has been independently verified through an approved workflow.

## 8. Alembic migration requirements

### 8.1 Migration revision

Create a new Alembic revision whose `down_revision` is:

`2833c9394364`

The migration must be added to the existing linear migration chain.

Existing migration scripts must not be rewritten.

### 8.2 Migration operations

The initial migration should:

1. Create `knowledge_document_topics`.
2. Add the required primary key.
3. Add the foreign key to `knowledge_documents`.
4. Add the uniqueness constraint.
5. Add the required indexes.
6. Populate topic associations from existing document topic values using an explicit mapping.
7. Preserve the original topic column.
8. Verify the migration outcome.

If permission evidence requires only an application-level JSON structure, do not create unnecessary database columns or a separate migration solely for that reason.

### 8.3 Migration failure behavior

The migration must fail safely when:

- An existing topic cannot be mapped.
- A duplicate assignment violates the uniqueness constraint.
- A required table or column is missing.
- Referential integrity cannot be maintained.
- An unexpected schema state is detected.

The migration must not silently skip invalid records.

### 8.4 Trigger protection

The migration must not:

- Drop the document-version immutability trigger.
- Drop its PostgreSQL function.
- Update or delete existing document versions.
- Remove the existing unique version constraint.

Post-migration verification must confirm that the trigger remains enabled.

## 9. PersistentKnowledgeIngestionService requirements

Introduce a service named:

`PersistentKnowledgeIngestionService`

Its responsibility is to coordinate candidate validation and persistent storage.

### 9.1 Required operations

The service must:

1. Accept a validated candidate document.
2. Resolve its registered source.
3. Verify source identity and metadata.
4. Verify language consistency.
5. Validate permission evidence.
6. Validate topic identifiers.
7. Create or resolve the knowledge document.
8. Persist topic associations.
9. Create the immutable document version.
10. Create the review snapshot.
11. Record the ingestion audit event.
12. Leave the document pending clinical review.

### 9.2 Separation of responsibilities

The service must not:

- Approve clinical content.
- Create a clinical approval record.
- Bypass the clinical review workflow.
- Mark an unverified source as permitted.
- Modify an existing immutable document version.
- Invent source metadata.
- Treat a successful database write as clinical approval.

### 9.3 Transaction management

The ingestion service must use a clearly defined transaction boundary.

All related writes should succeed or fail together:

- Document creation.
- Topic association creation.
- Version creation.
- Review snapshot creation.
- Audit event creation.

The service must not commit partial ingestion state.

Transaction ownership must be explicit and compatible with the existing repository and review workflow.

The implementation must avoid nested commits that make rollback incomplete.

## 10. Idempotency and version conflict handling

The implementation must distinguish:

### Exact duplicate

If the same document version and identical validated content and metadata are submitted again, the service must handle the request idempotently.

It must not create duplicate versions or duplicate topic assignments.

### Conflicting duplicate

If the same document/version identifier is submitted with different content or review metadata, reject the operation.

The caller must create an appropriate new document version rather than overwrite an existing one.

### Topic updates

Changes to topic assignments must be audited and must not silently alter immutable version snapshots.

Any topic changes affecting previously approved content must be evaluated against the established review policy.

## 11. Audit requirements

The ingestion workflow must record enough information to establish:

- The ingestion event.
- The affected document.
- The document version.
- The source identity.
- The responsible actor, where available.
- The operation outcome.
- Relevant validation or failure details.

Audit records must not contain passwords, confidential permission correspondence, or unnecessary personal information.

Audit event creation must participate in the ingestion transaction.

## 12. Rollback requirements

### 12.1 Schema rollback

The migration downgrade must account for topic assignments created after the migration.

The downgrade must not silently destroy assignments that cannot be reconstructed from the original `topic` column.

If a safe downgrade is not possible, the migration must include a documented data export or recovery procedure and must block unsafe rollback.

### 12.2 Application rollback

Application rollback must preserve:

- Existing topic data.
- Permission evidence in version snapshots.
- Existing clinical review history.
- Existing audit events.
- Immutable document-version records.

Application rollback must not rewrite historical snapshots.

### 12.3 Recovery

A failed migration or ingestion operation must have a documented recovery path.

Database backups must be verified before migration execution.

## 13. Required tests

### 13.1 Model tests

- Multiple topics can be associated with one document.
- Duplicate topics are rejected.
- Unknown topics are rejected.
- Invalid document references are rejected.
- Existing document relationships remain functional.

### 13.2 Migration tests

- Upgrade from the current head.
- Existing topics are migrated correctly.
- Invalid legacy topics cause safe failure.
- Existing documents remain intact.
- Existing document versions remain intact.
- Existing review snapshots remain intact.
- Existing constraints and triggers remain present.
- Downgrade behavior is tested.

### 13.3 Permission evidence tests

- Valid permission evidence is accepted.
- Missing required evidence is rejected.
- Invalid permission statuses are rejected.
- Invalid timestamps are rejected.
- Future timestamps are rejected.
- Evidence is preserved in the version snapshot.
- Existing snapshots are not rewritten.

### 13.4 Ingestion service tests

- Successful persistent ingestion.
- Source not found.
- Source metadata mismatch.
- Permission evidence failure.
- Language mismatch.
- Invalid topic.
- Duplicate topic.
- Exact duplicate submission.
- Conflicting version submission.
- Database rollback on failure.
- Audit event creation.
- Pending-review status after ingestion.
- No automatic clinical approval.

### 13.5 Regression tests

Run the existing knowledge ingestion, lifecycle integration, persistent review workflow, persistent retrieval, and full project test suites.

The implementation must not reduce existing test coverage or weaken existing assertions.

## 14. Implementation sequence

The future implementation should follow this sequence:

1. Review and approve this specification.
2. Inspect the current model and repository interfaces again.
3. Define exact model changes.
4. Implement the association model and relationships.
5. Implement the Alembic migration.
6. Test the migration against a disposable database.
7. Implement permission evidence validation.
8. Implement persistent ingestion coordination.
9. Add transaction and audit tests.
10. Run integration and regression tests.
11. Verify the database schema and trigger.
12. Prepare the implementation completion report.

Each implementation stage must have its own verification checkpoint.

## 15. Acceptance criteria

Implementation is acceptable only when:

- Multiple topics are persisted correctly.
- Existing topic values are preserved.
- Permission evidence is validated and traceable.
- Immutable versions remain protected.
- Ingestion is transactional.
- Duplicate submissions are handled safely.
- No automatic clinical approval occurs.
- Audit records are created.
- Existing review and retrieval workflows remain functional.
- Migration upgrade and recovery behavior are verified.
- All relevant tests pass.
- No broken Python dependencies remain.

## 16. Scope exclusions

This specification does not authorize:

- Actual code modifications.
- SQLAlchemy model changes.
- Alembic revision creation.
- Migration execution.
- Production database changes.
- Vector database integration.
- LLM integration.
- Frontend development.
- Authentication redesign.
- Conversation-history implementation.

## 17. Open decisions

The following decisions require explicit approval before implementation:

1. Final permission-status enumeration.
2. Final topic normalization mapping for legacy records.
3. Whether topic changes require re-review of previously approved documents.
4. Exact transaction ownership between the ingestion service and repository.
5. Idempotency key and duplicate-submission strategy.
6. Downgrade restrictions where data loss is possible.
7. Whether historical documents without permission evidence should be excluded from retrieval immediately or handled through a controlled legacy review process.

## 18. Approval record

- Implementation specification prepared: Yes.
- Existing migration design incorporated: Yes.
- Data integrity requirements documented: Yes.
- Test strategy documented: Yes.
- Implementation authorized: No.
- Project-owner approval: Pending.