# R04.7 — Persistent Knowledge Ingestion Service Design

**Project:** HIV/SRH Education Chatbot  
**Phase:** R04 — Knowledge Content Readiness  
**Checkpoint:** R04.7.3 — Persistent Ingestion Service Design  
**Status:** Project-owner approved design  
**Implementation status:** Not yet implemented

---

## 1. Purpose

This document defines the design for a controlled persistent knowledge ingestion service.

The service will connect validated knowledge candidates to the existing database-backed knowledge lifecycle while preserving clinical review separation, immutable document versions, source traceability, transaction integrity and auditability.

This design does not authorize automatic clinical approval or the use of unreviewed health content.

## 2. Design Principles

The ingestion service shall:

1. Validate candidates before persistence.
2. Preserve source provenance and publication metadata.
3. Require documented permission status and evidence.
4. Preserve English and Kiswahili as independently reviewable language versions.
5. Support multiple knowledge topics per document.
6. Create immutable document versions.
7. Preserve metadata snapshots associated with each version.
8. Record ingestion audit events.
9. Use database transactions to prevent partial ingestion.
10. Never automatically approve clinical content.
11. Preserve the existing clinical review and retrieval safeguards.
12. Avoid unnecessary personal or confidential information.

## 3. Existing Implementation

The current implementation provides:

- Pydantic knowledge source and document models.
- Candidate validation and preparation.
- Persistent source and document database models.
- Immutable document versions.
- Content fingerprints.
- Review metadata snapshots.
- Clinical review history.
- Persistent audit events.
- A database-backed clinical review workflow.
- Approval-aware persistent retrieval.
- A database trigger preventing document-version mutation.

The existing lifecycle integration test coordinates candidate preparation, database records, clinical review and retrieval.

A unified production ingestion service has not yet been established.

## 4. Source Metadata Strategy

### 4.1 Source identity

The existing `health_sources` table remains responsible for source identity and operational metadata, including:

- Source name.
- Publishing organization.
- Source URL.
- Source type.
- Language.
- Permission status.
- Active status.
- Last verification timestamp.

### 4.2 Publication metadata

Publication-specific metadata shall be preserved in the immutable document-version review snapshot.

This includes:

- Publication title.
- Publication version or edition.
- Publication date.
- Source URL.
- Source identity.
- Source language.
- Source verification timestamp.

Publication metadata must represent the exact publication used to prepare the knowledge document.

### 4.3 Permission evidence

A permission status alone is insufficient to demonstrate why a source may be used.

The version snapshot shall support the following structured evidence:

| Field | Purpose |
|---|---|
| `permission_status` | Permission decision, such as permitted, restricted or unknown |
| `permission_basis` | Documented basis for use, such as an open licence or written permission |
| `permission_reference` | Licence URL or controlled evidence reference |
| `permission_checked_at` | Date and time permission was checked |
| `permission_checked_by` | Responsible permission-checking actor |
| `permission_notes` | Relevant non-confidential notes |

Confidential correspondence and unnecessary personal information shall not be copied into the snapshot.

Permission must be established before a candidate can proceed to clinical approval.

## 5. Multiple Topic Persistence

The candidate model supports multiple topics, while the current database document model stores one topic.

The persistent design must support multiple topics without silently discarding information.

A document-topic association table is the proposed approach.

The final migration design shall define:

- Association between document IDs and topic identifiers.
- Valid topic identifiers.
- Duplicate prevention.
- Referential integrity.
- Migration and compatibility with existing records.

The implementation must preserve the nine approved project topic categories.

## 6. Persistent Ingestion Service Contract

Proposed service:

`PersistentKnowledgeIngestionService`

Proposed interface:

```python
class PersistentKnowledgeIngestionService:
    def ingest_candidate(
        self,
        document: KnowledgeDocument,
        *,
        preparer_id: str,
        version_number: int,
    ) -> IngestionResult:
        ...
```

The service shall return a structured result identifying:

- Persistent document ID.
- Persistent document version ID.
- Version number.
- Ingestion outcome.
- Relevant audit event identifier, where available.

The result must not imply clinical approval.

## 7. Ingestion Workflow

The service shall perform these operations in order:

1. Validate preparer identity and required metadata.
2. Validate the candidate using the approved candidate validation function.
3. Resolve the registered persistent source.
4. Verify that submitted source metadata matches the registered source.
5. Verify source activity and permission eligibility.
6. Identify or create the persistent knowledge document.
7. Persist the document's topic associations.
8. Calculate the document content fingerprint.
9. Build a complete immutable review metadata snapshot.
10. Create the immutable document version.
11. Set the document status to pending review.
12. Record a candidate-ingestion audit event.
13. Return the ingestion result.

No clinical review decision shall be created during ingestion.

## 8. Transaction Management

All database writes associated with one ingestion operation shall be performed within a controlled database transaction.

The transaction shall include:

- New document creation, when applicable.
- Topic association creation.
- Document version creation.
- Review snapshot persistence.
- Document status update.
- Ingestion audit event creation.

If an operation fails, all writes made by that ingestion operation must be rolled back.

The service must not commit a transaction owned by an external caller unless the final transaction contract explicitly assigns that responsibility to the service.

The implementation shall define and test transaction ownership consistently.

## 9. Duplicate and Idempotency Policy

The service shall distinguish identical submissions from conflicting submissions.

| Scenario | Expected behavior |
|---|---|
| New document and new version | Create pending-review candidate |
| Existing version with identical content and metadata | Apply documented idempotency behavior without creating duplicate records |
| Existing version with different content | Reject and require a new version number |
| Existing version with different review snapshot | Reject and require a new version number |
| Existing document with mismatched language or source | Reject |
| Duplicate topic association | Prevent duplicate association |
| Database uniqueness conflict | Roll back and return a controlled error |

An identical retry must never generate a new clinical approval decision.

## 10. Clinical Approval Separation

Ingestion and clinical approval are separate operations.

The ingestion service shall:

- Create candidates in pending-review status.
- Preserve preparer identity.
- Never create an approved clinical review record.
- Never mark a document approved.
- Never bypass the persistent clinical review workflow.

The existing `PersistentClinicalReviewWorkflow` remains responsible for recording clinical review decisions.

Clinical reviewer authentication and professional qualification verification remain separate governance requirements and are not satisfied by this ingestion service.

## 11. Bilingual Integrity

English and Kiswahili versions shall remain independently reviewable.

The service shall:

- Validate document and source language consistency.
- Preserve the exact language identifier.
- Preserve translation relationships where supported by the data model.
- Avoid treating approval of one language as approval of another.
- Ensure each language version has its own immutable version and review history.

## 12. Audit Events

The service shall record relevant ingestion events, including:

- Candidate ingestion requested.
- Candidate validation successful.
- Candidate validation rejected.
- Persistent candidate created.
- Existing candidate/version reused under the idempotency policy.
- Ingestion transaction failure, where safely recordable.

Audit records should include relevant identifiers and outcomes without copying unnecessary sensitive content.

Clinical review audit events remain the responsibility of the clinical review workflow.

## 13. Error Handling

The service shall provide controlled failures for:

- Invalid candidate metadata.
- Unknown source.
- Inactive source.
- Restricted or unknown source permission.
- Source metadata mismatch.
- Duplicate version conflict.
- Invalid language or topic association.
- Database transaction failure.
- Unexpected persistence errors.

Failed ingestion must not leave partially created documents, versions or topic associations.

## 14. Retrieval Eligibility

A successfully ingested candidate is not automatically retrievable.

Retrieval must continue to require:

- A valid immutable document version.
- A complete review snapshot.
- An eligible source.
- Permitted source status.
- A matching source metadata snapshot.
- A valid clinical approval decision.
- A matching requested language.
- All existing persistent retrieval integrity checks.

Pending-review candidates must remain unavailable to chatbot retrieval.

## 15. Database Schema and Migration Strategy

Potential database changes include:

1. A document-topic association table.
2. Additional structured permission-evidence fields, if required after implementation-level review.
3. Any necessary constraints and indexes.

Publication date and publication version shall remain in the immutable version snapshot unless a demonstrated operational requirement justifies dedicated database fields.

Database changes must be delivered through controlled migrations.

Existing data must be preserved, and migration rollback or recovery considerations must be documented.

## 16. Required Automated Tests

The implementation shall test:

- Successful candidate ingestion.
- Rejection of invalid candidates.
- Source identity matching.
- Source permission validation.
- Source verification timestamp consistency.
- Multiple topic persistence.
- Duplicate topic prevention.
- English and Kiswahili separation.
- Translation relationship integrity.
- Immutable version creation.
- Snapshot completeness.
- Permission evidence preservation.
- Duplicate submission handling.
- Conflicting version rejection.
- Transaction rollback.
- No automatic clinical approval.
- Audit event creation.
- Compatibility with the existing review workflow.
- Compatibility with approval-aware retrieval.
- Regression of all existing knowledge lifecycle tests.

## 17. Scope Exclusions

This checkpoint does not include:

- Vector database integration.
- Semantic search implementation.
- LLM-generated medical content.
- Frontend ingestion interfaces.
- Authentication redesign.
- Conversation-history storage.
- Automatic medical content approval.
- Automatic verification of professional clinical qualifications.

## 18. Acceptance Criteria

The persistent ingestion implementation will be acceptable when:

1. Valid candidates can be persisted through one controlled service.
2. Invalid candidates are rejected before persistence.
3. Source metadata and permission evidence are traceable.
4. Multiple topics are preserved.
5. Versions and review snapshots are immutable.
6. Failed operations do not leave partial records.
7. Duplicate submissions are handled consistently.
8. Ingestion does not approve clinical content.
9. Audit events are recorded.
10. Existing review and retrieval safeguards remain intact.
11. All relevant automated tests pass.
12. Database migrations are verified and existing records remain intact.

## 19. Outstanding Governance Requirements

The following remain outside the technical completion of this design:

- Appointment of an appropriately qualified clinical lead.
- Verification of clinical reviewer qualifications.
- Formal permission evidence for each publication or document.
- Clinical review and approval of actual knowledge content.
- Language review and approval of Kiswahili translations.
- Production authentication and authorization controls.

## 20. Approval Record

**R04.7.3 design decision:** Approved by project owner.

**Implementation authorization:** Subject to the next checkpoint's implementation plan and approval.

**Clinical governance approval:** Pending.

**Actual knowledge content approval:** Pending.

**Important:** Approval of this design does not approve any medical content, source publication, clinical reviewer qualification or production deployment.
```

## 2. Verify the document

After saving it, run:

```powershell
Test-Path docs/R04_INGESTION_SERVICE_DESIGN.md
```

Then:

```powershell
(Get-Item docs/R04_INGESTION_SERVICE_DESIGN.md).Length
```

And verify the section headings:

```powershell
Select-String -Path docs/R04_INGESTION_SERVICE_DESIGN.md -Pattern "^## "
```

## 3. R04.7.3 verification checkpoint

<box border radius="lg" padding={3} gap={2}>
  <badge color="warning">Awaiting document verification</badge>
  - [ ] Design document saved.
  - [ ] All 20 sections present.
  - [ ] Service contract documented.
  - [ ] Permission evidence strategy documented.
  - [ ] Multiple-topic persistence strategy documented.
  - [ ] Transaction and rollback strategy documented.
  - [ ] Clinical approval remains separate.
</box>

Please send the verification outputs. We will close R04.7.3 only after confirming the document exists and its sections are present. Then we can prepare the next implementation checkpoint, including a migration plan, before changing the database or application code.