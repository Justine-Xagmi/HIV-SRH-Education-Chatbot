# HIV/SRH Education Chatbot — English/Kiswahili Content Policy

**Phase:** R04 — Knowledge Content Readiness  
**Checkpoint:** R04.5 — English/Kiswahili Content Policy  
**Status:** Draft for project-owner review  
**Version:** 1.0

## 1. Purpose

This policy establishes requirements for preparing, translating, reviewing and maintaining HIV and Sexual and Reproductive Health (SRH) educational content in English and Kiswahili.

The chatbot must provide educational information in both supported languages while preserving the accuracy, meaning, safety and clinical qualifications of the original content.

## 2. Scope

This policy applies to:

- Knowledge documents.
- Educational explanations.
- HIV and SRH terminology.
- Frequently asked questions and answers.
- Safety notices and disclaimers.
- Source descriptions and attribution.
- Translated knowledge documents.
- Clinical review of language-specific content.

Supported language identifiers:

| Language | Identifier |
|---|---|
| English | `en` |
| Kiswahili | `sw` |

This policy does not authorize automatic translation of clinical content without appropriate review.

## 3. Core Bilingual Principles

All bilingual content must follow these principles:

1. Accuracy: Preserve the meaning of the original information.
2. Clarity: Use language understandable to the intended audience.
3. Consistency: Use consistent terminology across documents.
4. Cultural appropriateness: Use respectful language suitable for the Tanzanian context.
5. Clinical safety: Preserve warnings, limitations and medical qualifications.
6. Traceability: Maintain a relationship between original and translated documents.
7. Independent review: Review each language version before approval.
8. Non-discrimination: Avoid stigmatizing or judgmental expressions.

## 4. Language Selection

The chatbot must use the language explicitly selected or supplied in the API request.

Supported values are:

- `en`
- `sw`

The application must not silently treat an unsupported language as English or Kiswahili.

If a language is unsupported, the application should return a standardized validation error.

The language of a retrieved knowledge document must match the requested response language.

The system must not return an English document as though it were a Kiswahili document, or vice versa.

## 5. English Content Requirements

English educational content must:

- Use clear and straightforward language.
- Prefer familiar terms where medically appropriate.
- Explain technical terms when first introduced.
- Avoid unnecessary abbreviations.
- Preserve relevant clinical terminology.
- Use respectful and non-stigmatizing expressions.
- Avoid unsupported promises or absolute claims.
- Clearly distinguish general education from individualized medical advice.

Content should be suitable for a general audience without unnecessarily simplifying medically important information.

## 6. Kiswahili Content Requirements

Kiswahili educational content must:

- Use clear and natural Kiswahili.
- Prefer commonly understood Tanzanian Kiswahili expressions.
- Explain technical medical terminology.
- Avoid direct translations that distort medical meaning.
- Preserve important medical qualifications and warnings.
- Use respectful, non-judgmental language.
- Avoid unnecessary English expressions when an accurate Kiswahili equivalent exists.
- Retain internationally recognized medical abbreviations where appropriate and explain them.

The content should be understandable to the general Tanzanian audience.

## 7. Translation Requirements

Every translated document must:

1. Reference its original logical document.
2. Identify the original language.
3. Identify the translated language.
4. Preserve the original educational meaning.
5. Preserve relevant medical terminology.
6. Preserve safety warnings and limitations.
7. Preserve source attribution.
8. Undergo language review.
9. Undergo applicable clinical review.
10. Receive an independent approval decision.

Translation must not introduce new medical recommendations that are absent from the original source without additional authoritative support and review.

A translation must not omit important qualifications simply to make the wording shorter or easier.

## 8. Translation Workflow

The proposed translation workflow is:

1. Select an eligible source document.
2. Prepare the original-language knowledge document.
3. Validate source metadata and content.
4. Create the translated version.
5. Link the translated document to its original.
6. Conduct language and terminology review.
7. Conduct clinical review of the translated content.
8. Record the review decision.
9. Approve the exact translated version if all requirements are satisfied.
10. Make the approved version eligible for retrieval.

The workflow must preserve the history of both language versions.

## 9. Clinical Meaning Equivalence

English and Kiswahili documents must communicate equivalent clinical meaning.

Reviewers must verify that translations preserve:

- Prevention information.
- Testing information.
- Treatment education.
- Important conditions and exceptions.
- Safety warnings.
- Referral and care-seeking guidance.
- Limitations of educational information.
- Relevant dates and numerical information.
- Dosage or measurement information when included in an approved source.

A translation must not make a recommendation appear more certain, more urgent or less restrictive than the original.

Where a direct translation could be misleading, reviewers should use a clear explanatory expression that preserves the intended meaning.

## 10. Terminology Management

The project should maintain a controlled English–Kiswahili terminology glossary.

The glossary should include:

| Field | Description |
|---|---|
| `term_id` | Unique terminology identifier |
| `english_term` | Approved English term |
| `kiswahili_term` | Approved Kiswahili equivalent |
| `definition` | Explanation of the term |
| `usage_context` | Context in which the term is used |
| `review_status` | Terminology review status |
| `reviewed_by` | Reviewer identifier |
| `reviewed_at` | Review timestamp |

The glossary should cover HIV, testing, prevention, treatment, contraception, pregnancy, reproductive health, sexual health and STIs.

Where no reliable direct equivalent exists, the terminology reviewer should recommend an explanatory translation rather than inventing an equivalent.

## 11. Abbreviations and Medical Expressions

Abbreviations must be handled consistently.

Requirements:

- Introduce the full expression before using an unfamiliar abbreviation.
- Explain important medical abbreviations in both languages.
- Preserve internationally recognized abbreviations when appropriate.
- Do not assume that all users understand medical terminology.
- Do not translate abbreviations in a way that changes their meaning.

For example, HIV and STI may be retained as internationally recognized abbreviations while their meanings are explained in the relevant language.

## 12. Safety Notices and Disclaimers

Safety notices must be available in both supported languages.

The English and Kiswahili versions must communicate the same limitations.

They must clearly explain that:

- The chatbot provides educational information.
- The chatbot does not replace qualified healthcare professionals.
- The chatbot does not diagnose medical conditions.
- Users should seek appropriate healthcare when professional assessment is necessary.
- Emergency or urgent health concerns require appropriate immediate assistance.

Safety notices must not be weakened or omitted during translation.

## 13. Language-Specific Clinical Review

Each language version must receive an appropriate review before approval.

Review must consider:

1. Clinical accuracy.
2. Translation accuracy.
3. Terminology consistency.
4. Readability.
5. Cultural appropriateness.
6. Preservation of warnings and qualifications.
7. Source consistency.

Clinical review and language review may involve different qualified reviewers.

The project must retain the identity and review history associated with each decision.

An approved English version does not automatically approve its Kiswahili translation.

A Kiswahili translation must not be made retrievable solely because its English original was approved.

## 14. Versioning and Synchronization

Each language version must have its own version history.

When the original document changes:

1. Identify linked translations.
2. Determine whether each translation is affected.
3. Mark affected translations for reassessment.
4. Prepare revised translations where necessary.
5. Submit revised content for review.
6. Approve the exact revised versions before retrieval.

An old translation must not silently represent a newly revised original document.

The system must preserve the relationship between original and translated versions.

## 15. Retrieval Rules

For every user request:

- Use the requested language.
- Retrieve only documents approved for that language.
- Ensure document and source metadata are valid.
- Exclude pending, rejected or retired content.
- Exclude translations that have not completed required review.
- Do not silently substitute another language.
- Do not invent translations of unsupported medical content.

If approved content is unavailable in the requested language, the chatbot should communicate the limitation honestly rather than present unreviewed clinical information.

## 16. Content Quality Assurance

Bilingual quality assurance must evaluate:

| Quality dimension | Requirement |
|---|---|
| Accuracy | Meaning matches the authoritative source |
| Completeness | Important information is not omitted |
| Readability | Understandable to the general audience |
| Terminology | Medical terms are used consistently |
| Safety | Warnings and limitations are preserved |
| Cultural appropriateness | Language is respectful and suitable |
| Consistency | Related documents communicate equivalent information |
| Traceability | Original and translated versions are linked |

Automated checks may identify missing fields, language mismatches and formatting problems.

Automated translation or linguistic checks must not replace qualified clinical review.

## 17. Prohibited Practices

The project must not:

- Automatically approve machine-generated translations.
- Treat English approval as Kiswahili approval.
- Mix English and Kiswahili content without a clear reason.
- Invent medical terminology.
- Remove important safety warnings.
- Change clinical recommendations during translation without review.
- Use stigmatizing or discriminatory language.
- Present unsupported translations as clinically reviewed.
- Retrieve unapproved language versions.

## 18. Acceptance Criteria

The bilingual policy is acceptable when:

1. English and Kiswahili are explicitly defined.
2. Language selection rules are documented.
3. English writing requirements are documented.
4. Kiswahili writing requirements are documented.
5. Translation requirements are documented.
6. Translation relationships are defined.
7. Clinical meaning equivalence is addressed.
8. Terminology management requirements are defined.
9. Safety notice requirements are documented.
10. Independent language-version approval is required.
11. Version synchronization requirements are defined.
12. Retrieval restrictions are documented.
13. Bilingual quality assurance requirements are documented.

## 19. Open Decisions

The following remain subject to future review:

- Final English–Kiswahili terminology glossary.
- Approved translation reviewer qualifications.
- Whether translation review and clinical review require separate individuals in every case.
- Translation quality measurement criteria.
- Preferred Kiswahili terminology for specialized clinical expressions.
- Handling of content with no approved translation.
- Whether additional local languages will be supported in future releases.

## 20. Approval Record

**Checkpoint:** R04.5 — English/Kiswahili Content Policy  
**Status:** Draft for project-owner review  
**Project-owner approval:** Pending  
**Approval date:** Pending

Approval confirms the bilingual content policy. It does not approve individual translations, medical publications or clinical knowledge documents for chatbot retrieval.