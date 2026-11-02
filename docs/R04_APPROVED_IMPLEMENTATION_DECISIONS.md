# R04 Approved Implementation Decisions

**Project:** HIV/SRH Education Chatbot  
**Phase:** R04 — Knowledge Content Readiness  
**Checkpoint:** R04.7.5.2 — Approved Decision Record  
**Status:** Project-owner decisions approved

## 1. Purpose

This document records the project owner's decisions on all eight open implementation questions identified in R04.7.5.1.

These decisions are authoritative for subsequent R04 implementation planning unless formally revised.

## 2. Approval summary

All eight proposed decisions were approved without changes.

| Decision | Subject | Result |
|---|---|---|
| D01 | Permission-status enumeration | Approved |
| D02 | Legacy topic mapping | Approved |
| D03 | Topic representation authority | Approved |
| D04 | Topic changes after clinical approval | Approved |
| D05 | Transaction ownership | Approved |
| D06 | Idempotency identity | Approved |
| D07 | Downgrade restrictions | Approved |
| D08 | Legacy permission assessment | Approved |

## 3. Approved decisions

### D01 — Permission-status enumeration

Approved values:

- `permitted`
- `restricted`
- `prohibited`
- `unknown`

Only `permitted` may satisfy the permission-status requirement for new clinical approval, and sufficient supporting evidence must also be verified.

### D02 — Legacy topic mapping

Approved approach:

- Inventory all existing topic values.
- Create an explicit mapping to the controlled topic vocabulary.
- Manually resolve unknown values.
- Preserve original values during migration.
- Validate migrated records and topic counts.
- Never silently guess or discard unmapped topics.

### D03 — Topic representation authority

Approved approach:

- `knowledge_document_topics` becomes the authoritative topic representation.
- The legacy `knowledge_documents.topic` column remains temporarily for compatibility.
- Application writes use one controlled service.
- Independent writes to both representations are prohibited.
- Legacy-column removal requires separate assessment and approval.

### D04 — Topic changes after clinical approval

Approved approach:

- Material topic changes require a new document version and clinical review.
- Administrative corrections require a documented and auditable process.
- Previously approved versions remain unchanged.
- Approval must not silently carry over when classification or retrieval meaning changes.

### D05 — Transaction ownership

Approved approach:

- The calling application/service layer owns the outer transaction.
- The ingestion service operates within that transaction.
- The caller commits after successful completion.
- The caller rolls back after failure.
- The ingestion service must not independently commit the caller's transaction.
- Nested transaction behavior must be tested.

### D06 — Idempotency identity

Approved identity fields:

- Document ID.
- Version number.
- Content fingerprint.
- Source identity.
- Language.
- Relevant immutable source and permission metadata.

Approved behavior:

- Exact matching requests are idempotent.
- Conflicting requests under the same document/version are rejected.
- Changed content requires a new version.
- Duplicate-request audit behavior must be deterministic.

### D07 — Downgrade restrictions

Approved approach:

- Test downgrades against disposable databases.
- Do not automatically execute destructive downgrade operations.
- Preserve or export data before destructive operations.
- Block downgrades that cannot safely preserve or reconstruct data.
- Document and test recovery procedures.

### D08 — Legacy permission assessment

Approved approach:

- Preserve historical immutable snapshots unchanged.
- Treat missing permission evidence as legacy/unverified.
- Do not infer permission from historical clinical approval.
- Do not automatically approve legacy records under the updated permission policy.
- Require separate evidence assessment where needed.
- Record the assessment and responsible actor.

## 4. Implementation implications

The approved decisions must be reflected in:

1. SQLAlchemy model design.
2. Alembic migration design.
3. Persistent ingestion service.
4. Permission evidence validation.
5. Topic migration and compatibility handling.
6. Transaction and idempotency tests.
7. Downgrade and recovery procedures.
8. Clinical review and audit workflows.

## 5. Approval boundaries

Approval of these decisions does not authorize:

- Application code modifications.
- Database schema changes.
- Alembic revision creation.
- Database migration execution.
- Production deployment.
- Clinical content approval.

Those activities require their own implementation scope and explicit authorization.

## 6. Approval record

- D01–D08: Approved.
- Revision requests: None.
- Project-owner decision review: Approved.
- Implementation plan: Pending.
- Application implementation authorization: Not granted.
- Database migration authorization: Not granted.