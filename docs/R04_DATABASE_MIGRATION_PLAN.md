# R04 Database Migration Plan

**Project:** HIV/SRH Education Chatbot  
**Phase:** R04 — Knowledge Content Readiness  
**Checkpoint:** R04.7.4.2 — Migration Design  
**Status:** Proposed design — pending project-owner approval

## 1. Purpose

This document defines the proposed database migration design for:

1. Supporting multiple topics per knowledge document.
2. Preserving structured source-permission evidence.
3. Maintaining immutable document versions and review snapshots.
4. Preserving existing database records.
5. Providing safe migration, rollback, and recovery procedures.

This is a design document only. It does not authorize database or application changes.

## 2. Existing database baseline

The current project uses:

- PostgreSQL.
- SQLAlchemy ORM.
- Alembic 1.20.1.
- A shared SQLAlchemy declarative base.
- A single Alembic migration chain.

The current migration head is:

`2833c9394364`

Existing database entities include:

- `health_sources`
- `knowledge_documents`
- `document_versions`
- `clinical_review_records`
- `knowledge_audit_events`

The current `knowledge_documents` table stores one topic in a single `topic` column.

The `document_versions` table includes a JSON `review_snapshot` column and an immutability trigger.

## 3. Design principles

All changes must follow these principles:

1. Preserve existing knowledge and review records.
2. Avoid destructive schema changes during the initial migration.
3. Maintain referential integrity.
4. Preserve immutable document-version history.
5. Keep source permission evidence traceable.
6. Prevent automatic clinical approval during ingestion.
7. Maintain compatibility with existing retrieval and review workflows.
8. Use transactional migrations where supported.
9. Test migrations independently before production use.
10. Make rollback and recovery procedures explicit.

## 4. Multiple-topic data model

### 4.1 Proposed association table

Introduce:

`knowledge_document_topics`

Proposed columns:

| Column | Proposed type | Purpose |
|---|---|---|
| id | Integer | Primary key |
| document_id | Integer | Foreign key to knowledge_documents.id |
| topic | String(100) | Validated topic identifier |
| created_at | DateTime with timezone | Assignment timestamp |

### 4.2 Constraints

The table should have:

- A primary key on `id`.
- A foreign key from `document_id` to `knowledge_documents.id`.
- A uniqueness constraint on `(document_id, topic)`.
- An index on `document_id`.
- An index on `topic`.

The foreign-key deletion policy must be selected deliberately. Cascading deletion should not be introduced without considering document retention and audit requirements.

### 4.3 Topic identifiers

Topic values must come from a controlled vocabulary.

The initial topic vocabulary is:

- `hiv_prevention`
- `hiv_testing`
- `hiv_treatment`
- `stigma_discrimination`
- `sexual_health`
- `contraception`
- `pregnancy_reproductive_health`
- `other_stis`
- `other_srh`

Identifiers must be stable, validated, and independent of display language.

English and Kiswahili documents should use the same topic identifiers where they cover the same subject.

### 4.4 Existing-topic migration

The existing `knowledge_documents.topic` column must initially remain in place.

The migration should:

1. Create the association table.
2. Read existing document IDs and topic values.
3. Validate and normalize existing topic values using an approved mapping.
4. Insert one association record for each valid existing topic.
5. Prevent duplicate assignments.
6. Verify that every existing document has its expected topic assignment.
7. Report unmapped or invalid topic values for manual resolution.

Existing topic values must not be silently discarded or guessed.

If an existing value cannot be mapped safely, the migration must preserve it for review and must not claim successful topic migration for that record.

### 4.5 Compatibility period

During the initial compatibility period:

- Existing code may continue reading the original `topic` column.
- New code may read the association table.
- Writes must use a controlled approach that prevents the two representations from becoming inconsistent.
- A later migration may remove the old column only after all dependent code and data have been verified.

Removal of the original column is outside this migration checkpoint.

## 5. Structured permission evidence

### 5.1 Proposed storage location

Use the existing `document_versions.review_snapshot` JSON column to preserve permission evidence with the immutable document version.

This avoids introducing multiple relational columns before the workflow demonstrates that they are necessary.

### 5.2 Proposed permission evidence structure

The snapshot should contain a structured permission evidence object with:

| Field | Purpose |
|---|---|
| permission_status | Permission state, such as permitted, restricted, prohibited, or unknown |
| permission_basis | Reason or legal/licensing basis for use |
| permission_reference | URL, licence identifier, or approved internal reference |
| permission_checked_at | Time permission was checked |
| permission_checked_by | Responsible actor identifier |
| permission_notes | Non-confidential explanation or restrictions |

The exact accepted values and validation rules must be defined in the application implementation specification.

### 5.3 Evidence integrity

Permission evidence must:

- Be associated with the exact source and document version.
- Be captured before a document is approved for retrieval.
- Be validated during candidate ingestion and review.
- Preserve restrictions and attribution requirements.
- Avoid storing confidential correspondence or unnecessary personal information.
- Remain part of the immutable version snapshot.

### 5.4 Existing snapshots

Existing snapshots must not be rewritten merely to make them conform to the new structure.

Where historical permission evidence is unavailable:

- Preserve the existing snapshot.
- Do not invent missing permission details.
- Treat missing evidence as an unresolved governance requirement.
- Require verification before the affected document can qualify for new approval or retrieval under the updated policy.

A legacy source's existing `permission_status` must not automatically be treated as complete permission evidence.

## 6. Immutable version compatibility

The existing database trigger protects document versions from updates and deletes.

The migration must preserve:

- The trigger `trg_document_versions_immutable`.
- The function `prevent_document_version_mutation()`.
- The existing unique constraint on `(document_id, version_number)`.
- Existing document fingerprints.
- Existing review snapshots.
- Existing clinical review records.

No migration should update existing immutable version records to add permission evidence.

New evidence must be captured when a new version is created.

The review workflow must continue to create a review snapshot before a version can be approved.

## 7. Proposed migration sequence

### Migration A — Multiple-topic support

1. Create `knowledge_document_topics`.
2. Add its primary key, foreign key, uniqueness constraint, and indexes.
3. Populate it from existing document topic values using an explicit mapping.
4. Validate the migrated assignments.
5. Retain the original `knowledge_documents.topic` column.

### Migration B — Permission evidence compatibility

1. Define the structured permission evidence schema.
2. Confirm that the JSON snapshot can preserve the proposed structure.
3. Update the application workflow in a separately approved implementation stage.
4. Ensure new snapshots capture permission evidence.
5. Preserve existing snapshots without fabricating missing evidence.

A database-only migration may not be necessary for this step if the existing JSON column is sufficient.

The decision to create a separate migration must be based on actual schema requirements.

### Migration C — Future compatibility cleanup

Only after a separately approved compatibility and data-integrity review:

- Remove obsolete single-topic dependencies.
- Consider removing the original topic column.
- Confirm that all application components use the association table.

This migration is not authorized by the current design.

## 8. Transaction and data integrity requirements

Migration operations must be designed to:

- Use transactions where supported.
- Avoid partially populated topic associations.
- Enforce foreign-key integrity.
- Prevent duplicate topic assignments.
- Preserve version immutability.
- Detect invalid legacy data.
- Fail safely when required data cannot be mapped.

The migration must not silently skip records and report success.

## 9. Rollback and recovery plan

### 9.1 Before migration

- Verify the current Alembic revision.
- Create a database backup.
- Verify backup integrity and restoration procedures.
- Record relevant row counts.
- Inspect existing constraints and triggers.
- Test the migration against a disposable database.

### 9.2 Topic migration rollback

A rollback must account for topic assignments created after the migration.

The new association table must not be dropped if doing so would destroy topic assignments that cannot be reconstructed from the original single-topic column.

Where necessary, rollback should be blocked until data has been exported or safely reconciled.

### 9.3 Permission evidence rollback

Existing immutable review snapshots must not be rewritten or deleted during rollback.

If the new application workflow is reverted, historical evidence must remain available.

### 9.4 Recovery

If migration fails:

1. Stop further migration operations.
2. Inspect the database revision and transaction outcome.
3. Check table, constraint, and trigger state.
4. Compare relevant row counts and data.
5. Restore from the verified backup if necessary.
6. Re-run tests before resuming implementation.

## 10. Testing strategy

The migration implementation must include tests for:

### Topic association

- Association table creation.
- Valid topic insertion.
- Multiple topics for one document.
- Duplicate topic rejection.
- Foreign-key enforcement.
- Existing topic migration.
- Invalid or unmapped legacy topics.
- Preservation of existing documents.
- Topic retrieval through the new structure.

### Permission evidence

- Valid permission evidence acceptance.
- Missing evidence rejection where required.
- Invalid permission status rejection.
- Permission reference validation.
- Timezone-aware verification timestamps.
- Source/document association integrity.
- Preservation of existing review snapshots.
- No fabricated legacy evidence.

### Version integrity

- Existing immutability trigger remains active.
- Existing versions cannot be updated or deleted.
- New versions can be created through the approved workflow.
- Version uniqueness remains enforced.
- Review history remains intact.

### Regression

- Existing ingestion tests.
- Existing review workflow tests.
- Existing persistent retrieval tests.
- Existing lifecycle integration tests.
- Full project test suite.

## 11. Acceptance criteria

The migration design can be considered implementation-ready when:

1. The topic association model is fully specified.
2. The controlled topic vocabulary is approved.
3. Existing topic values have an explicit mapping strategy.
4. Permission evidence fields and validation rules are approved.
5. Existing snapshots have a non-destructive compatibility strategy.
6. Version immutability is preserved.
7. Upgrade and downgrade behavior is documented.
8. Backup and recovery requirements are defined.
9. Migration and regression tests are specified.
10. No unresolved data-loss risk is hidden by the migration process.

## 12. Scope exclusions

This design does not authorize:

- Application code modifications.
- SQLAlchemy model modifications.
- Alembic revision creation.
- Database migration execution.
- Database table alteration.
- Existing version mutation.
- Automatic clinical approval.
- LLM or vector database integration.
- Authentication redesign.
- Persistent conversation-history implementation.

## 13. Open decisions

The following items require explicit resolution before implementation:

1. Final topic vocabulary and normalization mapping.
2. Treatment of legacy topic values that do not match the controlled vocabulary.
3. Whether permission evidence needs additional relational storage in the future.
4. Exact permission status enumeration and validation rules.
5. Compatibility approach for old and new topic reads/writes.
6. Conditions under which the legacy `topic` column may eventually be removed.
7. Downgrade restrictions where new topic assignments would otherwise be lost.

## 14. Approval record

- Migration design prepared: Yes.
- Existing database baseline considered: Yes.
- Data preservation requirements documented: Yes.
- Rollback and recovery requirements documented: Yes.
- Implementation authorized: No.
- Project-owner approval: Pending.