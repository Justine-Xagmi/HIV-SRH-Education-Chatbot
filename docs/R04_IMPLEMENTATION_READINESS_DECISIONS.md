# R04 Implementation Readiness Decisions

**Project:** HIV/SRH Education Chatbot  
**Phase:** R04 — Knowledge Content Readiness  
**Checkpoint:** R04.7.5.1 — Open-Decision Register  
**Status:** Proposed decisions pending project-owner approval

## 1. Purpose

This document records the unresolved decisions from the R04 migration design and proposes implementation defaults.

The objective is to prevent developers from making undocumented assumptions during implementation.

No application code or database changes are authorized by this document.

## 2. Decision register

### D01 — Permission-status enumeration

**Problem:** Permission evidence needs a controlled status vocabulary.

**Proposed values:**

- `permitted`: Documented permission or applicable reuse basis has been verified.
- `restricted`: Reuse is subject to conditions that have not yet been satisfied.
- `prohibited`: Reuse is not permitted.
- `unknown`: Permission status has not been established.

**Proposed rule:** Only `permitted` may satisfy the permission-status requirement for new clinical approval. The evidence must also be sufficient and independently validated.

**Approval required:** Yes.

### D02 — Legacy topic mapping

**Problem:** Existing documents use a single topic field, while the new design supports multiple topics.

**Proposed approach:**

1. Inventory all existing topic values.
2. Compare them with the approved nine-topic vocabulary.
3. Create an explicit mapping table.
4. Manually resolve unknown values.
5. Preserve the original values during migration.
6. Validate migrated document and topic counts.

**Proposed rule:** Unknown values must block completion of the affected migration step until resolved. No automatic guessing.

**Approval required:** Yes.

### D03 — Topic representation authority

**Problem:** The legacy topic column and new association table could disagree.

**Proposed approach:**

- The association table becomes the authoritative representation.
- The legacy column remains temporarily for compatibility.
- Application writes must use one controlled service.
- Readers must transition through a tested compatibility layer.
- The legacy column must not be independently updated.
- Removing the legacy column requires a separate approved migration.

**Approval required:** Yes.

### D04 — Topic changes after clinical approval

**Problem:** Changing topics can change how content is retrieved and interpreted.

**Proposed rule:**

- A topic change that materially affects content classification or retrieval eligibility requires a new document version and clinical review.
- A purely administrative correction may follow a separately documented, auditable process.
- Existing approved versions must remain unchanged.
- Topic changes must never silently preserve approval when the clinical meaning or intended use has changed.

**Approval required:** Yes.

### D05 — Transaction ownership

**Problem:** The ingestion service must not commit prematurely or leave partial records.

**Proposed approach:**

- The calling application/service layer owns the outer transaction.
- The ingestion service performs database operations within that transaction.
- The caller commits after successful completion.
- The caller rolls back after failure.
- The ingestion service must not independently commit the caller's transaction.
- Nested transaction behavior must be explicitly tested.

**Approval required:** Yes.

### D06 — Idempotency identity

**Problem:** Repeated ingestion requests must not create duplicate versions or audit events unnecessarily.

**Proposed identity fields:**

- Document ID.
- Version number.
- Content fingerprint.
- Source identity.
- Language.
- Relevant immutable source and permission metadata.

**Proposed rule:**

- An exact matching request is treated as an idempotent duplicate.
- A conflicting request using the same document and version is rejected.
- A changed content fingerprint requires a new version.
- Audit behavior for duplicate requests must be deterministic and documented.

**Approval required:** Yes.

### D07 — Downgrade restrictions

**Problem:** A migration downgrade could destroy newly created topic assignments or evidence.

**Proposed rule:**

- Downgrades must be tested against disposable databases.
- Destructive downgrade operations must not run automatically.
- Data must be exported or preserved before a destructive operation.
- A downgrade must be blocked if data cannot be safely reconstructed.
- Recovery must be documented and tested.

**Approval required:** Yes.

### D08 — Legacy permission assessment

**Problem:** Existing immutable snapshots may lack structured permission evidence.

**Proposed approach:**

- Preserve historical snapshots unchanged.
- Mark missing evidence as legacy/unverified in the relevant assessment process.
- Do not infer permission from historical approval status.
- Do not automatically approve legacy records under the new permission policy.
- Require a separate permission-evidence assessment before new approval or reuse where required.
- Record the assessment and its responsible actor.

**Approval required:** Yes.

## 3. Decision summary

| ID | Decision | Proposed direction |
|---|---|---|
| D01 | Permission statuses | Four controlled values |
| D02 | Legacy topic mapping | Explicit mapping; no guessing |
| D03 | Topic authority | Association table |
| D04 | Approved-document topic changes | New version and review when material |
| D05 | Transactions | Caller owns outer transaction |
| D06 | Idempotency | Document/version plus content and metadata identity |
| D07 | Downgrade | Block unsafe destructive downgrade |
| D08 | Legacy permission evidence | Preserve and reassess; never infer |

## 4. Implementation readiness conditions

Before R04 implementation begins:

1. All eight decisions must be approved or revised.
2. Any revised decision must be recorded.
3. The implementation specification must be updated where necessary.
4. The migration plan must remain consistent with the decisions.
5. The implementation scope must be explicitly approved.
6. Backup and disposable-database testing requirements must be satisfied before database migration.

## 5. Scope exclusions

This checkpoint does not authorize:

- Python application changes.
- SQLAlchemy model changes.
- Alembic migration creation.
- Database schema modifications.
- Database migration execution.
- Production deployment.
- Clinical content approval.

## 6. Approval record

- D01–D08 proposals documented: Yes.
- Project-owner review: Pending.
- Implementation authorization: Not granted.
- Database migration authorization: Not granted.