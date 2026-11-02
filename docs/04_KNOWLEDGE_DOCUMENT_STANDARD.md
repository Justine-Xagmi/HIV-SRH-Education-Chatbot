# HIV/SRH Education Chatbot — Knowledge Document Standard

**Phase:** R04 — Knowledge Content Readiness  
**Checkpoint:** R04.4 — Knowledge Document Structure  
**Status:** Draft for project-owner review  
**Version:** 1.0

## 1. Purpose

This document defines the standard structure and metadata requirements for knowledge documents used by the HIV/SRH Education Chatbot.

It provides a consistent format for identifying, organizing, reviewing, versioning, translating and maintaining educational health content.

Every knowledge document must be traceable to its original source and must retain the review and approval information applicable to its exact content version.

This standard does not independently approve medical content.

## 2. Document Design Principles

Every knowledge document must be:

1. Traceable to an identifiable source.
2. Assigned a unique and stable identifier.
3. Classified under one or more approved topics.
4. Explicit about its content language.
5. Structured for clear educational retrieval.
6. Version-controlled.
7. Subject to clinical review where clinical content is involved.
8. Protected against unreviewed changes after approval.
9. Linked to its review and approval history.
10. Retirable without losing its historical records.

## 3. Knowledge Document Structure

A knowledge document consists of five logical sections:

1. Document identity.
2. Source information.
3. Content and classification.
4. Version and review information.
5. Translation and maintenance relationships.

These sections define the logical standard. The final database implementation may use multiple related database tables.

## 4. Document Identity Metadata

Each document must contain:

| Field | Requirement | Description |
|---|---|---|
| `document_id` | Required | Unique, stable document identifier |
| `title` | Required | Descriptive document title |
| `language` | Required | `en` or `sw` |
| `topics` | Required | One or more approved topic categories |
| `document_type` | Required | Type of educational knowledge document |
| `content` | Required | Actual extracted educational content |
| `created_at` | Required | Document creation timestamp |
| `updated_at` | Required | Last document update timestamp |

The document identifier must remain stable across versions of the same logical document.

A new logical document must receive a different identifier.

## 5. Source Metadata

Every knowledge document must reference its original source.

Required source information:

| Field | Requirement | Description |
|---|---|---|
| `source_id` | Required | Unique source identifier |
| `source_title` | Required | Original publication title |
| `source_organization` | Required | Publishing organization |
| `source_url` | Required | Original source URL |
| `source_language` | Required | Original publication language |
| `source_version` | Required where available | Edition, version or publication identifier |
| `source_publication_date` | Required where available | Original publication date |
| `source_last_verified_at` | Required before approval | Date the source was last verified |
| `source_permission_status` | Required | Permission assessment status |

The source record must distinguish the original publication from the extracted knowledge document.

A knowledge document must not invent missing source metadata.

## 6. Content Organization Standard

Knowledge content should be organized using the following logical structure:

### 6.1 Title

A concise heading identifying the educational subject.

### 6.2 Summary

A short description of what the document explains.

### 6.3 Main content

The educational explanation, organized into meaningful sections.

### 6.4 Important qualifications

Relevant limitations, exceptions, clinical qualifications or contextual details must be preserved.

### 6.5 Safety information

Where applicable, include approved warnings, limitations and instructions for seeking professional healthcare.

### 6.6 Source attribution

Identify the publication and organization supporting the material.

Content must not remove qualifications or warnings that materially change the meaning of the original source.

## 7. Topic Classification

Every document must belong to at least one approved topic.

The initial topic identifiers are:

| Topic identifier | Description |
|---|---|
| `hiv_prevention` | HIV prevention |
| `hiv_testing` | HIV testing |
| `hiv_treatment_education` | HIV treatment education |
| `stigma_discrimination` | Stigma and discrimination |
| `sexual_health` | Sexual health |
| `contraception_family_planning` | Contraception and family planning |
| `pregnancy_reproductive_health` | Pregnancy and reproductive health |
| `sexually_transmitted_infections` | STIs other than HIV |
| `other_srh` | Other approved SRH topics |

A document may have multiple relevant topics.

Topic classification must accurately represent the document's actual content.

Duplicate topic identifiers should not be stored within the same document.

New topics require scope review and project-owner approval.

## 8. Language and Translation Metadata

Each document must explicitly identify its language.

Supported language values:

- `en`: English.
- `sw`: Kiswahili.

For translated documents, the following additional metadata is required:

| Field | Requirement | Description |
|---|---|---|
| `translation_status` | Required for translated documents | Translation review status |
| `original_document_id` | Required for translations | Identifier of the original logical document |
| `original_language` | Required for translations | Language of the original |
| `translator_or_translation_team` | Required where available | Responsible translator or team |
| `translation_reviewed_at` | Required before approval | Translation review timestamp |
| `translation_reviewed_by` | Required before approval | Translation reviewer identifier |

Translations must preserve the meaning and clinical qualifications of the original.

Machine translation alone does not qualify as clinical approval.

An English approval must not automatically approve a Kiswahili translation.

Each language version must have its own content version and applicable review record.

## 9. Document Versioning

Every knowledge document must have a version number.

The version standard is:

- Initial document: version `1`.
- First approved content revision: version `2`.
- Subsequent revisions: increment the version number.

Each version must preserve:

- Document identifier.
- Version number.
- Exact content.
- Content fingerprint.
- Source reference.
- Relevant metadata snapshot.
- Creation timestamp.
- Applicable review history.

A content fingerprint must be calculated from a deterministic representation of the document content and relevant version metadata.

The fingerprint must be recalculated when the content changes.

An approved version must not be modified in place.

A revision must create a new version and undergo the required review process.

## 10. Clinical Review Metadata

Every clinical review must be linked to an exact document version.

Required review information:

| Field | Requirement | Description |
|---|---|---|
| `review_id` | Required | Unique review record identifier |
| `document_id` | Required | Logical document identifier |
| `version_number` | Required | Exact version reviewed |
| `reviewer_id` | Required | Reviewer identifier |
| `decision` | Required | Review decision |
| `rationale` | Required | Explanation of the decision |
| `language_reviewed` | Required | Language reviewed |
| `reviewed_at` | Required | Review timestamp |

Supported review decisions:

- `approved`
- `rejected`
- `changes_requested`

Multiple reviews may exist for the same document version.

Review history must be retained.

The latest applicable review decision determines eligibility under the approved review workflow.

Reviewer identity and qualifications must be verified through an appropriate governance process. A reviewer identifier alone is insufficient evidence of qualification.

## 11. Document and Ingestion Status

The document lifecycle must distinguish ingestion status from clinical review status.

### Ingestion status

- `pending_validation`
- `validated`
- `rejected`

### Clinical review status

- `pending_review`
- `approved`
- `retired`

The review workflow may also record individual decisions such as `rejected` and `changes_requested`.

Validation does not equal clinical approval.

Only content that has completed the applicable validation and clinical approval requirements may be eligible for retrieval.

## 12. Translation and Original Document Relationships

A translated document must retain a relationship to its original logical document.

For example:

- Original document: `HIV-PREV-001`, English.
- Translation: `HIV-PREV-001-SW`, Kiswahili.

The identifiers above are illustrative only.

The relationship must make it possible to determine:

- Which original document was translated.
- Which language version is being used.
- Which original version informed the translation.
- Whether the translation has been reviewed.
- Whether either version has been revised or retired.

The two language versions must not be assumed to contain identical wording or have identical review histories.

## 13. Audit and Maintenance Metadata

The system must preserve sufficient history to determine:

- Who prepared the document.
- When it was created.
- Which source was used.
- Which version was submitted for review.
- Who reviewed it.
- What decision was made.
- Why the decision was made.
- When the document was revised.
- When it was retired.
- Why it was retired.

Audit records must not be silently overwritten.

Source updates must trigger an assessment of affected knowledge documents.

## 14. Retrieval Eligibility

A document may be retrieved only when:

1. Its content has passed the required ingestion validation.
2. Its exact current version has the required approval.
3. Its latest applicable clinical review permits approval.
4. Its source is active and eligible.
5. Source permission status is acceptable.
6. Document and source language metadata are consistent.
7. The requested language matches the document language.
8. The content fingerprint and review snapshot remain valid.
9. The document has not been retired or superseded.

If any mandatory condition fails, the document must be excluded.

## 15. Data Minimization

Knowledge documents must contain educational source material and relevant metadata, not personal information about chatbot users.

The following must not be added unnecessarily:

- User names.
- Personal contact information.
- Individual HIV status.
- Personal medical histories.
- Identifiable patient records.
- Private reviewer information beyond what governance requires.

Reviewer identifiers should be handled according to the project's privacy and access-control requirements.

## 16. Illustrative Knowledge Document

The following is a structural example, not approved medical content.

```json
{
  "document_id": "HIV-PREV-001",
  "title": "HIV Prevention Educational Overview",
  "language": "en",
  "topics": [
    "hiv_prevention"
  ],
  "document_type": "educational_article",
  "content": "Placeholder content awaiting source extraction and clinical review.",
  "source": {
    "source_id": "SRC-001",
    "title": "Placeholder publication title",
    "organization": "Placeholder organization",
    "url": "https://example.org/publication",
    "language": "en",
    "version": "1",
    "publication_date": null,
    "last_verified_at": null,
    "permission_status": "unknown"
  },
  "version_number": 1,
  "ingestion_status": "pending_validation",
  "review_status": "pending_review",
  "translation": {
    "is_translation": false,
    "original_document_id": null,
    "original_language": null
  }
}
```

The example is illustrative. It must not be ingested as a real source or approved document.

## 17. Relationship to Existing Implementation

The existing application already contains several related structures:

- `HealthSource`
- `KnowledgeDocument`
- `DocumentVersion`
- `ClinicalReviewRecord`
- `KnowledgeAuditEvent`

Existing fields include document identifiers, source identifiers, content, language, topics, review status, content fingerprints and review snapshots.

The proposed standard extends the logical requirements to include document type, translation relationships, clearer source metadata, and additional maintenance and audit expectations.

These are requirements for assessment during later implementation planning. This document does not authorize immediate database changes.

## 18. Acceptance Criteria

The knowledge document standard is ready for approval when:

1. Document identity fields are defined.
2. Source metadata requirements are defined.
3. Content organization is defined.
4. The nine topic identifiers are documented.
5. English and Kiswahili requirements are documented.
6. Translation relationships are defined.
7. Immutable versioning requirements are documented.
8. Clinical review metadata is defined.
9. Ingestion and review statuses are distinguished.
10. Audit and maintenance requirements are defined.
11. Retrieval eligibility conditions are documented.
12. Data minimization requirements are included.
13. The illustrative structure is clearly identified as non-approved sample content.

## 19. Open Decisions

The following remain subject to later review:

- Final database representation of document type and translation relationships.
- Whether document identifiers use UUIDs or controlled human-readable identifiers.
- Exact fingerprint serialization and canonicalization rules.
- Required versus optional publication metadata for different source types.
- Final translation-review responsibilities.
- Source and document retirement procedures.
- Whether a document is divided into smaller independently retrievable sections.
- Any additional metadata required by the future retrieval architecture.

## 20. Approval Record

**Checkpoint:** R04.4 — Knowledge Document Structure  
**Status:** Draft for project-owner review  
**Project-owner approval:** Pending  
**Approval date:** Pending

Approval confirms the logical document standard. It does not approve any source publication, extracted content, translation or clinical recommendation for chatbot retrieval.