# R04 Migration Risk and Readiness Review

**Project:** HIV/SRH Education Chatbot  
**Phase:** R04 — Knowledge Content Readiness  
**Checkpoint:** R04.7.4.4 — Migration Risk and Readiness Review  
**Status:** Risk assessment complete; implementation readiness conditional

## 1. Purpose

This document evaluates the technical, data-integrity, clinical-governance, and operational risks associated with the proposed R04 database changes.

The assessment covers:

- Multiple-topic database support.
- Structured source-permission evidence.
- Persistent knowledge ingestion.
- Existing document-version immutability.
- Database migration safety.
- Application compatibility.
- Testing, backup, rollback, and recovery.

This is a risk assessment, not authorization to modify the application or database.

## 2. Existing baseline

The project currently uses:

- Python 3.11.
- SQLAlchemy ORM.
- PostgreSQL.
- Alembic 1.20.1.
- A shared SQLAlchemy declarative base.
- Persistent knowledge source and document models.
- Immutable document-version records.
- Clinical review history.
- Knowledge audit events.
- Review snapshots stored as JSON.

The current migration revision is:

`2833c9394364`

The existing database includes a document-version immutability trigger and a unique constraint on document/version number.

## 3. Risk assessment method

Risks are classified using:

- **High:** Could cause significant data loss, clinical-safety failure, or integrity compromise.
- **Medium:** Could cause application errors, inconsistent records, or operational disruption.
- **Low:** Limited impact, generally manageable through normal testing and review.

Risk ratings are preliminary engineering assessments and must be reassessed after implementation details and database conditions are verified.

## 4. Risk register

### R01 — Loss of existing topic data

**Risk:** Existing document topic values may be lost or incorrectly transformed during migration.

**Likelihood:** Medium  
**Impact:** High  
**Rating:** High

**Mitigation:**

- Preserve the original `topic` column initially.
- Use an explicit legacy-topic mapping.
- Validate every existing document.
- Record unmapped values for manual review.
- Compare pre-migration and post-migration topic counts.
- Do not silently skip invalid records.

**Acceptance condition:** Every existing topic is either correctly migrated or explicitly reported as unresolved without data loss.

### R02 — Topic representation inconsistency

**Risk:** The legacy `knowledge_documents.topic` column and the new association table may contain different topic assignments.

**Likelihood:** High  
**Impact:** High  
**Rating:** High

**Mitigation:**

- Define one authoritative write path.
- Define a temporary compatibility strategy for existing readers.
- Avoid independent writes to both representations.
- Add tests for topic consistency.
- Define reconciliation procedures.
- Remove legacy dependencies only through a separately approved migration.

**Acceptance condition:** Application components cannot silently create conflicting topic representations.

### R03 — Duplicate topic assignments

**Risk:** Repeated ingestion or concurrent writes may create duplicate topic associations.

**Likelihood:** Medium  
**Impact:** Medium  
**Rating:** Medium

**Mitigation:**

- Enforce uniqueness on `(document_id, topic)`.
- Validate duplicate topics before persistence.
- Test concurrent insertion behavior.
- Make ingestion idempotent.

**Acceptance condition:** Duplicate assignments are rejected or handled idempotently.

### R04 — Invalid topic vocabulary

**Risk:** Unknown, inconsistent, or incorrectly normalized topic identifiers may enter the database.

**Likelihood:** Medium  
**Impact:** High  
**Rating:** High

**Mitigation:**

- Use a controlled topic vocabulary.
- Validate identifiers at the application boundary.
- Define explicit mappings for legacy values.
- Test English and Kiswahili topic consistency.

**Acceptance condition:** Every accepted topic uses an approved stable identifier.

### R05 — Incomplete permission evidence

**Risk:** A document may be treated as permitted without sufficient evidence.

**Likelihood:** Medium  
**Impact:** High  
**Rating:** High

**Mitigation:**

- Define permission status values.
- Require evidence appropriate to the selected status.
- Validate permission references and verification timestamps.
- Distinguish source authority from permission to reuse content.
- Require permission evidence before approval under the updated policy.
- Never infer permission from a source URL alone.

**Acceptance condition:** Documents without sufficient evidence cannot receive new approval or become eligible for retrieval under the updated policy.

### R06 — Historical snapshot modification

**Risk:** Updating existing review snapshots may violate document-version immutability or create misleading historical evidence.

**Likelihood:** Medium  
**Impact:** High  
**Rating:** High

**Mitigation:**

- Do not rewrite existing immutable snapshots.
- Preserve historical metadata exactly.
- Capture new permission evidence in newly created versions.
- Use a separately governed process for legacy content review.

**Acceptance condition:** Existing immutable version snapshots remain unchanged.

### R07 — Accidental bypass of clinical review

**Risk:** The new persistent ingestion service may accidentally approve content or bypass the existing clinical review workflow.

**Likelihood:** Medium  
**Impact:** Critical  
**Rating:** High

**Mitigation:**

- Keep ingestion separate from clinical approval.
- Leave newly ingested documents pending review.
- Do not create approval records during ingestion.
- Preserve reviewer decision controls.
- Test explicitly that ingestion never results in clinical approval.

**Acceptance condition:** Only the authorized clinical review workflow can approve clinical content.

### R08 — Partial database writes

**Risk:** A failure during ingestion may leave a document without its topics, version, snapshot, or audit event.

**Likelihood:** Medium  
**Impact:** High  
**Rating:** High

**Mitigation:**

- Define one clear transaction boundary.
- Include related writes in the same transaction.
- Avoid premature nested commits.
- Test rollback after failures at different stages.
- Verify that no partial ingestion records remain.

**Acceptance condition:** Ingestion succeeds completely or rolls back completely.

### R09 — Immutable trigger damage

**Risk:** A migration or schema operation may disable, remove, or bypass the document-version immutability trigger.

**Likelihood:** Low  
**Impact:** Critical  
**Rating:** High

**Mitigation:**

- Preserve the trigger and its function.
- Inspect trigger state before and after migration.
- Test update and delete rejection.
- Verify the PostgreSQL error code remains `55000`.

**Acceptance condition:** Existing immutable-version protection remains operational.

### R10 — Unsafe migration downgrade

**Risk:** Downgrading the schema may destroy topic assignments or permission evidence that cannot be reconstructed.

**Likelihood:** Medium  
**Impact:** High  
**Rating:** High

**Mitigation:**

- Define downgrade restrictions.
- Export data before destructive rollback.
- Preserve evidence in immutable snapshots.
- Test upgrade and downgrade on disposable databases.
- Block rollback when data cannot be preserved safely.

**Acceptance condition:** No downgrade is executed if it would silently destroy unrecoverable data.

### R11 — Existing application regression

**Risk:** Existing review, retrieval, repository, and ingestion workflows may fail after introducing topic associations.

**Likelihood:** Medium  
**Impact:** High  
**Rating:** High

**Mitigation:**

- Maintain compatibility during the transition.
- Test existing repository operations.
- Test persistent retrieval.
- Test review and lifecycle workflows.
- Run the complete regression suite.

**Acceptance condition:** Existing approved functionality continues working without weakened tests.

### R12 — Incomplete backup or recovery

**Risk:** A failed migration may leave the database in an unexpected state without a verified recovery path.

**Likelihood:** Medium  
**Impact:** High  
**Rating:** High

**Mitigation:**

- Create a backup before migration.
- Verify backup integrity.
- Test restoration.
- Record the current migration revision.
- Define recovery ownership and procedures.

**Acceptance condition:** A verified recovery procedure exists before migration execution.

### R13 — Inaccurate audit records

**Risk:** Ingestion or permission evidence changes may not be sufficiently traceable.

**Likelihood:** Medium  
**Impact:** Medium  
**Rating:** Medium

**Mitigation:**

- Record ingestion events.
- Record relevant document and version identifiers.
- Record responsible actors where available.
- Keep audit events within the transaction.
- Avoid sensitive or confidential information in audit details.

**Acceptance condition:** Important ingestion operations are traceable through audit records.

### R14 — Deployment incompatibility

**Risk:** Application deployment may occur before the database migration or after an incompatible migration.

**Likelihood:** Medium  
**Impact:** High  
**Rating:** High

**Mitigation:**

- Define migration and application deployment order.
- Use a compatibility period for old and new topic structures.
- Test the intended deployment sequence.
- Verify the database revision before enabling new functionality.

**Acceptance condition:** The deployed application and database schema are compatible at every deployment stage.

## 5. Clinical and governance readiness risks

The following are governance requirements, not merely technical migration requirements:

1. Actual clinical reviewer appointments must be documented.
2. Reviewer qualifications and applicable professional registration must be verified.
3. Source permission must be assessed for each publication and intended use.
4. English and Kiswahili content must receive their respective reviews.
5. Historical documents without adequate permission evidence must not be treated as automatically approved.
6. Clinical content must remain subject to the established review and retirement procedures.

Approval of the migration design does not satisfy these governance requirements.

## 6. Migration readiness checklist

### 6.1 Technical preparation

- [ ] Existing migration head confirmed.
- [ ] Existing schema inspected.
- [ ] Existing topic values inventoried.
- [ ] Legacy-topic mapping approved.
- [ ] Association-table constraints specified.
- [ ] Permission evidence structure specified.
- [ ] Transaction ownership defined.
- [ ] Idempotency behavior defined.
- [ ] Upgrade and downgrade procedures specified.

### 6.2 Data protection

- [ ] Database backup created.
- [ ] Backup integrity verified.
- [ ] Restore procedure tested.
- [ ] Existing document counts recorded.
- [ ] Existing version counts recorded.
- [ ] Existing topic values recorded.
- [ ] Review snapshots preserved.
- [ ] Immutability trigger state recorded.

### 6.3 Testing

- [ ] Migration upgrade tests prepared.
- [ ] Legacy-topic migration tests prepared.
- [ ] Invalid-topic tests prepared.
- [ ] Permission evidence tests prepared.
- [ ] Transaction rollback tests prepared.
- [ ] Duplicate-ingestion tests prepared.
- [ ] Immutability tests prepared.
- [ ] Existing retrieval and review regression tests prepared.
- [ ] Full test suite planned.

### 6.4 Governance

- [ ] Clinical reviewer appointment documented.
- [ ] Reviewer qualification verification completed.
- [ ] Source permission evidence reviewed.
- [ ] Bilingual clinical review process available.
- [ ] Legacy content handling approved.

## 7. Readiness decision

The proposed R04 changes are suitable for controlled implementation planning.

However, the project is not yet authorized for production migration.

The following conditions remain mandatory before applying migrations to a persistent or production database:

1. Resolve high-risk design decisions.
2. Complete implementation and code review.
3. Test migrations against a disposable database.
4. Verify backup and recovery.
5. Verify existing records and constraints.
6. Confirm that the immutability trigger remains active.
7. Pass integration and regression tests.
8. Obtain explicit project-owner authorization.
9. Satisfy relevant clinical governance requirements before clinical content is approved.

## 8. Scope exclusions

This review does not authorize:

- Python code modifications.
- SQLAlchemy model modifications.
- Alembic revision creation.
- Database schema changes.
- Database migration execution.
- Production deployment.
- Clinical content approval.
- Automatic permission certification.

## 9. Conclusion

The proposed multiple-topic and structured permission-evidence changes can be implemented using the existing PostgreSQL and Alembic infrastructure, subject to the risks and conditions documented in this review.

The most important implementation risks are topic representation inconsistency, incomplete permission evidence, immutable snapshot protection, transaction safety, and destructive rollback.

These risks must be addressed and verified before migration execution.

**Current decision:** Implementation readiness is conditional. Production migration is not authorized.

## 10. Approval record

- Risk register prepared: Yes.
- Technical risks documented: Yes.
- Clinical governance risks documented: Yes.
- Data protection requirements documented: Yes.
- Migration readiness assessed: Conditional.
- Production migration authorized: No.
- Project-owner approval: Pending.