# HIV/SRH Education Chatbot — Knowledge Content Requirements

**Phase:** R04 — Knowledge Content Readiness  
**Checkpoint:** R04.2 — Knowledge Content Requirements  
**Status:** Draft for project-owner review  
**Version:** 1.0

## 1. Purpose

This document defines the content requirements for the HIV/SRH Education Chatbot knowledge base.

It establishes what information the knowledge base should contain, the quality conditions that content must satisfy, and the requirements for clinical review, language coverage, source traceability, retrieval eligibility and maintenance.

These requirements guide future content preparation and ingestion. They do not approve any source or medical content for chatbot use.

## 2. Scope

The initial knowledge base is intended to support general educational questions about HIV, sexual health and reproductive health.

The knowledge base must support:
- English.
- Kiswahili.
- Source-grounded educational responses.
- Traceable references to approved source material.
- Clinical review and approval before retrieval.
- Controlled updates and retirement of outdated content.

The knowledge base is not intended to independently diagnose conditions, prescribe medication or make individualized clinical decisions.

## 3. Initial Knowledge Topics

The initial knowledge collection must address the following nine topic areas.

### 3.1 HIV Prevention

Content requirements:
- General HIV transmission education.
- Evidence-based HIV prevention methods.
- Correct educational information about condoms.
- PrEP and PEP education based on applicable approved guidance.
- Common misconceptions about HIV transmission.
- Prevention-related stigma and discrimination.

Clinical recommendations must be consistent with current applicable national guidance and receive qualified clinical review.

### 3.2 HIV Testing

Content requirements:
- Reasons for HIV testing.
- General descriptions of available testing approaches.
- Window-period education based on approved guidance.
- Explanation of the meaning and limitations of test results.
- General guidance on seeking confirmatory testing and professional support.
- Confidentiality and respectful testing education.

Content must not interpret an individual's result as a definitive diagnosis or replace professional testing services.

### 3.3 HIV Treatment Education

Content requirements:
- General information about antiretroviral therapy.
- Educational explanation of treatment adherence.
- General information about viral load and viral suppression.
- U=U education when supported by applicable approved guidance.
- General information about treatment monitoring and professional follow-up.
- Stigma reduction and treatment support.

The chatbot must not initiate, discontinue or change an individual's medication or treatment plan.

### 3.4 Stigma and Discrimination

Content requirements:
- HIV-related stigma education.
- Discrimination awareness.
- Respectful and non-judgmental language.
- Myths and misconceptions.
- Privacy, dignity and confidentiality education.
- Supportive information about accessing appropriate services.

Content must avoid stigmatizing language or assumptions about an individual's HIV status, identity or behaviour.

### 3.5 Sexual Health

Content requirements:
- General sexual health education.
- Safer-sex information.
- Consent and respectful relationships.
- Sexual health communication.
- STI prevention education.
- Guidance on seeking appropriate professional support.

### 3.6 Contraception and Family Planning

Content requirements:
- General information about contraception methods.
- Educational descriptions of how methods are used.
- General benefits, limitations and possible side effects where supported by approved sources.
- Family planning education.
- Guidance on seeking qualified contraceptive counselling.

The chatbot must not select or prescribe a contraceptive method for an individual.

### 3.7 Pregnancy and Reproductive Health

Content requirements:
- General pregnancy education.
- Reproductive health information.
- Antenatal-care education.
- General maternal health information.
- Guidance on accessing qualified healthcare.
- Safety information about symptoms that may require urgent assessment, using approved clinical guidance.

The chatbot must not diagnose pregnancy complications or replace professional maternal healthcare.

### 3.8 Sexually Transmitted Infections Other Than HIV

Content requirements:
- General STI education.
- Common transmission routes.
- Prevention information.
- General symptoms and the limitations of symptom-based identification.
- Testing and treatment education.
- Encouragement to seek qualified healthcare.
- Stigma reduction.

The chatbot must not diagnose an STI or recommend individualized treatment.

### 3.9 Other Sexual and Reproductive Health Topics

Content requirements:
- Only topics within the approved project scope.
- A documented reason for adding each new topic.
- Appropriate source evidence.
- Qualified review when clinical recommendations are involved.
- Project-owner approval before expanding the knowledge scope.

Unreviewed or unrelated material must not be added merely because it is available.

## 4. Content Quality Requirements

Every knowledge document must satisfy the following requirements before clinical approval.

### 4.1 Accuracy

- Content must be supported by the identified source.
- Clinical recommendations must be consistent with applicable current guidance.
- Uncertain or conflicting recommendations must be flagged for review.
- Content must not contain invented statistics, clinical claims or references.
- Unsupported statements must be removed or clearly identified for further review.

### 4.2 Relevance

- Content must relate to an approved chatbot topic.
- Content must be appropriate for the intended general audience.
- Explanations should be understandable without unnecessary technical terminology.
- Technical terms should be explained when needed.

### 4.3 Clarity

- Content should use clear and direct language.
- Headings should identify the subject of each section.
- Complex explanations should be divided into understandable sections.
- Abbreviations should be defined when first introduced.
- Ambiguous wording should be corrected before approval.

### 4.4 Completeness

A document should contain enough context to preserve the meaning of the source material.

Extracted content must not remove qualifications, warnings, exceptions or limitations that materially affect a clinical statement.

### 4.5 Non-stigmatizing language

- Use respectful and inclusive wording.
- Avoid blame, shame and discrimination.
- Do not make assumptions about users.
- Preserve confidentiality and dignity in educational explanations.

## 5. Source and Traceability Requirements

Every knowledge document must be traceable to its original source.

Required source information:
- Unique source identifier.
- Source title.
- Publishing organization.
- Original source URL.
- Source language.
- Source version or edition where available.
- Publication date where available.
- Last verification date.
- Permission or licence status.
- Evidence supporting the recorded permission status.

A source must not be considered approved merely because it is published by a recognized organization.

The project must verify that:
- The source is authentic.
- The content is applicable to the intended audience.
- The information is sufficiently current.
- Any relevant national guidance has been considered.
- The intended extraction, storage and use are permitted.

## 6. Knowledge Document Requirements

Every knowledge document must have:
- A unique document identifier.
- A descriptive title.
- A source reference.
- A language.
- One or more approved topic categories.
- Non-empty content.
- A source version or publication reference.
- An ingestion status.
- A clinical review status.
- A review history linked to the exact content version.
- A content update timestamp.

The document must preserve enough source context to allow reviewers to compare extracted material with the original.

Changes to content must result in a new immutable version and require the applicable review process.

## 7. English and Kiswahili Requirements

The knowledge base must support English and Kiswahili content.

Requirements:
- Each document must identify its actual content language.
- A translation must preserve the meaning of the reviewed original.
- Machine translation alone must not qualify as clinical approval.
- Safety-critical instructions must receive appropriate language and clinical review.
- Medical terminology must be understandable and consistent.
- Where possible, translated documents should maintain a traceable relationship to their original source document.
- An unreviewed translation must not be represented as clinically validated.

The existence of an English document does not automatically authorize a Kiswahili version, or vice versa.

## 8. Clinical Review Requirements

Clinical content must undergo review by an appropriately qualified healthcare professional before approval.

The review process must:
- Identify the exact document version.
- Identify the reviewer.
- Record the review date.
- Record the review decision.
- Include a meaningful review rationale.
- Confirm the reviewed language.
- Preserve review history.
- Prevent a preparer from approving their own submission.
- Require a new review when content changes.

Supported decisions:
- `approved`
- `rejected`
- `changes_requested`

Only eligible approved content may be retrieved.

The development reviewer-ID allowlist must not be treated as proof of professional identity or qualification.

## 9. Safety-Sensitive Content Requirements

Safety-sensitive content requires particular attention.

Examples include:
- PEP timing and eligibility.
- HIV test interpretation.
- Antiretroviral treatment.
- Pregnancy complications.
- Sexual assault and coercion.
- Self-harm or severe emotional distress.
- STI symptoms and treatment.
- Urgent healthcare situations.

For these areas:
- Use current applicable approved guidance.
- Preserve clinical qualifications and limitations.
- Require qualified clinical review.
- Avoid diagnosis and individualized treatment decisions.
- Include appropriate professional-care guidance.
- Use approved safety responses where applicable.

The knowledge base must not invent emergency contacts, referral locations or healthcare-service availability.

## 10. Content Exclusion Requirements

The following content must not enter the approved retrieval collection:

- Documents without an identifiable source.
- Content with unverified or prohibited usage permissions.
- Retired or superseded material.
- Material with unresolved critical clinical concerns.
- Unreviewed medical recommendations.
- Unreviewed translations presented as validated.
- Content whose source and document languages conflict.
- Documents with incomplete or invalid required metadata.
- Content that has been modified after approval without the required new review.
- Material outside the approved chatbot scope.

## 11. Content Maintenance Requirements

The project must establish a maintenance process that:
- Records when each source was last checked.
- Identifies updated or withdrawn source documents.
- Flags affected knowledge documents.
- Prevents superseded content from remaining eligible for retrieval.
- Requires re-review of materially affected content.
- Preserves document versions and review history.
- Records retirement decisions and reasons.

The exact review interval must be established through clinical governance and source-specific requirements.

## 12. Retrieval Requirements

The retrieval system must:
- Return only content eligible under the approval workflow.
- Respect the requested language.
- Preserve source attribution.
- Use the approved document version.
- Exclude retired or ineligible sources.
- Avoid presenting unsupported information as established fact.
- Return no fabricated citations.
- Support a safe fallback when adequate approved content is unavailable.

Retrieval results must not be treated as a substitute for clinical assessment.

## 13. Acceptance Criteria

The knowledge-content foundation will be considered ready for the next implementation stages when:

1. The nine initial topic areas have documented content requirements.
2. Required source metadata is defined.
3. Knowledge document metadata is defined.
4. English and Kiswahili requirements are documented.
5. Clinical review requirements are documented.
6. Safety-sensitive content requirements are documented.
7. Content exclusion conditions are defined.
8. Content maintenance requirements are documented.
9. Retrieval eligibility requirements are documented.
10. The distinction between candidate, validated, reviewed and approved content is maintained.

Completion of these criteria does not mean that actual medical content has been approved.

## 14. Open Decisions

The following decisions remain subject to future checkpoints:
- Final source inventory for each topic.
- Confirmation of source currentness and applicability.
- Source-specific permission and licensing evidence.
- Named clinical reviewer and qualification verification.
- Final English/Kiswahili terminology and translation workflow.
- Source re-verification schedule.
- Referral-service verification process.
- Final ingestion integration design.
- Retrieval technology beyond the current keyword-based implementation.

## 15. Approval Record

**Checkpoint:** R04.2 — Knowledge Content Requirements  
**Status:** Draft for project-owner review  
**Project-owner approval:** Pending  
**Approval date:** Pending

Approval of this document confirms the content requirements. It does not approve any specific source, medical document, translation or clinical recommendation for chatbot retrieval.