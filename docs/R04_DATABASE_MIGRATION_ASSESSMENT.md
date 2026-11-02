# R04 Database Migration Assessment

**Project:** HIV/SRH Education Chatbot  
**Phase:** R04 — Knowledge Content Readiness  
**Checkpoint:** R04.7.4.1 — Database Migration Assessment  
**Status:** Assessment complete; implementation not yet authorized

## 1. Purpose

This assessment reviews the existing database migration setup before introducing changes to support multiple knowledge-document topics and structured source-permission evidence.

The assessment is based on the existing application configuration, SQLAlchemy models, Alembic environment, migration scripts, and reported database revision.

## 2. Existing migration infrastructure

The project uses:

- SQLAlchemy ORM for database models.
- Alembic 1.20.1 for schema migrations.
- PostgreSQL as the database engine.
- A shared declarative model base at `app/db/base.py`.
- Database connection configuration through `DATABASE_URL`.
- Migration configuration in `alembic.ini`.
- Migration environment in `alembic/env.py`.

Alembic imports the application's database models and uses `Base.metadata` as its target metadata. Schema comparison includes column types through `compare_type=True`.

The application database URL overrides the placeholder URL in `alembic.ini`.

## 3. Existing migration history

The inspected migration chain is:

1. `778ff1495041` — Create knowledge governance tables.
2. `03903e1ec021` — Prevent duplicate document version numbers.
3. `f02d13db92ed` — Protect document-version immutability.
4. `2833c9394364` — Add document review snapshot.

The reported database revision is:

`2833c9394364` (head).

The database connection reports PostgreSQL transactional DDL.

## 4. Existing schema considerations

The current knowledge-document table stores one topic in a single `topic` column.

Candidate ingestion supports multiple topics. A normalized document-topic association table is therefore a proposed solution to preserve all candidate topics without silently discarding information.

The document-version table contains a JSON `review_snapshot` column. The existing review workflow uses this snapshot to preserve review-relevant metadata.

This JSON structure may support structured permission evidence, subject to a detailed schema and compatibility assessment.

## 5. Proposed migration direction

### 5.1 Multiple topics

Assess introducing a document-topic association table with:

- A document foreign key.
- A topic identifier.
- A uniqueness rule preventing duplicate topic assignments for the same document.
- Appropriate indexes and referential integrity.

Existing single-topic values must be preserved and migrated into the association structure.

### 5.2 Permission evidence

Extend the version-level review snapshot design to preserve structured permission evidence, including:

- Permission status.
- Permission basis.
- Permission reference.
- Permission verification timestamp.
- Verifying actor identifier.
- Non-confidential permission notes.

The implementation must avoid storing confidential correspondence or unnecessary personal information.

### 5.3 Immutable version protection

Any migration must preserve the existing document-version immutability trigger and function.

New version snapshots must continue to be created through the established review workflow.

### 5.4 Existing data preservation

The migration must preserve:

- Health sources.
- Knowledge documents.
- Existing document topics.
- Document versions and fingerprints.
- Review snapshots.
- Clinical review records.
- Knowledge audit events.
- Existing foreign-key relationships and constraints.

## 6. Migration safety requirements

Before applying a migration:

1. Confirm the current database revision.
2. Create and verify a recoverable database backup.
3. Inspect existing records and constraints.
4. Check for duplicate or invalid topic values.
5. Define the mapping from existing topics to the new association structure.
6. Prepare explicit upgrade and downgrade operations.
7. Test the migration against a disposable database or verified test database.
8. Confirm existing records remain accessible.
9. Verify the immutability trigger after migration.
10. Run the complete application test suite.

A downgrade must not silently destroy newly assigned topic data. Where data loss cannot be avoided, the downgrade must be documented as unsafe or require an explicit recovery procedure.

## 7. Migration implementation exclusions

This assessment does not authorize:

- Applying database migrations.
- Changing application models.
- Changing repository or ingestion code.
- Modifying existing migration scripts.
- Dropping or recreating database tables.
- Changing database credentials.
- Introducing a vector database.
- Implementing LLM retrieval.
- Redesigning authentication.

## 8. Outstanding technical decisions

The following decisions must be resolved in the migration plan:

1. Whether the topic association table uses controlled topic identifiers or another validated representation.
2. How existing topic values are normalized and migrated.
3. Whether permission evidence remains entirely within the version-level JSON snapshot or requires additional relational fields.
4. How exact duplicate ingestion is handled.
5. How conflicting version metadata is rejected.
6. How rollback and recovery protect existing and newly created data.
7. How migrations are tested independently of the developer's working database.

## 9. Assessment conclusion

The project has an existing PostgreSQL and Alembic migration infrastructure with a linear migration history and a reported database revision at the current head.

The existing setup is suitable for planning the proposed R04 schema changes. The next step is to define the migration design, data-preservation strategy, testing requirements, and rollback procedure.

**No migration has been created or applied as part of this assessment.**

## 10. Approval record

- Database migration assessment: Complete.
- Existing migration chain inspected: Complete.
- Existing database revision checked: Complete.
- Migration implementation: Not authorized by this assessment.
- Project-owner approval: Pending.