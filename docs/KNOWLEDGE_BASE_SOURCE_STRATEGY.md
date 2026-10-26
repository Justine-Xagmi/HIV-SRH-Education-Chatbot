# HIV/SRH Education Chatbot — Knowledge-Base Source Strategy

**Phase:** 2 — Requirements and Design
**Step:** 5 — Knowledge-Base Source Strategy
**Status:** Draft for review
**Version:** 1.0
**Date:** 26 October 2026

## 1. Purpose

This document defines how the project will identify, evaluate, approve, maintain, and use health-information sources for the HIV/SRH Education Chatbot.

The sources listed here are candidates for review. Listing a source does not mean that its content has already been downloaded, clinically reviewed, or approved for use.

## 2. Source Selection Principles

Every candidate source should be evaluated for:

1. Authority and credibility of the publisher.
2. Relevance to Tanzania and the intended audience.
3. Accuracy and consistency with applicable national guidance.
4. Publication date, review date, and whether newer guidance exists.
5. Coverage of the chatbot's approved educational topics.
6. Suitability for clear explanations in English and Kiswahili.
7. Permission and conditions for downloading, storing, transforming, or redistributing content.
8. Availability of reliable source metadata and traceable references.

Clinical recommendations must not be accepted solely because they appear on a website. Conflicting or outdated recommendations require review before use.

## 3. Candidate Source Register

### Source S-01: Tanzania Ministry of Health — NASHCoP

Organization: Tanzania Ministry of Health, National AIDS, STIs and Hepatitis Control Programme.

Website:
https://www.nacp.go.tz/

Candidate document:
National Integrated HIV, Viral Hepatitis and STI Management Guidelines, September 2023.

Document:
https://www.nacp.go.tz/documents/download/90

Proposed use:
- HIV prevention and testing.
- HIV treatment education.
- Sexually transmitted infections.
- Relevant national clinical and programme guidance.

Priority: High for relevant Tanzania-specific HIV and STI content.

Review requirements:
- Confirm the document remains applicable and has not been superseded.
- Identify the sections appropriate for public education.
- Confirm consistency with current national guidance.
- Obtain qualified health-content review before approval.

Status: Candidate; review pending.

### Source S-02: World Health Organization

Organization: World Health Organization (WHO).

HIV and AIDS information:
https://www.who.int/en/news-room/fact-sheets/detail/hiv-aids

Consolidated HIV guidelines:
https://www.who.int/publications/i/item/9789240031593

Proposed use:
- HIV prevention.
- HIV testing.
- HIV treatment education.
- Supporting international technical context.

Priority: High as an international reference, subject to checking the latest applicable guidance and Tanzanian national recommendations.

Review requirements:
- Check for newer WHO guidance.
- Identify the publication or update date.
- Compare relevant recommendations with current national guidance.
- Do not silently resolve conflicting recommendations without qualified review.

Status: Candidate; review pending.

### Source S-03: UNFPA Tanzania

Organization: United Nations Population Fund, Tanzania.

Sexual and reproductive health:
https://tanzania.unfpa.org/en/topics/sexual-and-reproductive-health-11

Country programme overview:
https://tanzania.unfpa.org/en/unfpa-tanzania

Proposed use:
- Sexual health education.
- Contraception and family planning.
- Pregnancy and reproductive health.
- Relevant reproductive-health rights and service information.

Priority: High as a candidate SRH reference.

Review requirements:
- Identify specific pages or documents suitable for educational use.
- Check the currency and scope of the information.
- Obtain health-content review for clinical recommendations.
- Confirm content-use permissions.

Status: Candidate; review pending.

## 4. Topic Coverage Plan

The initial chatbot scope contains nine topic areas.

| Topic | Proposed source direction |
|---|---|
| HIV prevention | NASHCoP; WHO |
| HIV testing | NASHCoP; WHO |
| HIV treatment education | NASHCoP; WHO |
| Stigma and discrimination | Relevant national and recognized international health resources |
| Sexual health | UNFPA Tanzania; relevant national guidance |
| Contraception | UNFPA Tanzania; applicable national guidance |
| Pregnancy and reproductive health | UNFPA Tanzania; applicable national maternal-health guidance |
| STIs other than HIV | NASHCoP; applicable national guidance |
| Other SRH topics | Only after scope review and source approval |

The table identifies candidate directions, not proof that every topic is covered adequately by the listed sources.

Additional sources may be required after topic-by-topic review.

## 5. Content Approval Workflow

Each candidate document must follow this workflow:

1. Discover the original source and record its URL.
2. Record the title, publisher, language, publication date, and update or review date when available.
3. Check whether the document is current and applicable to Tanzania.
4. Check content-use permissions and any licence restrictions.
5. Extract only relevant material using a documented process.
6. Submit clinical material to the designated qualified reviewer.
7. Resolve conflicting or ambiguous recommendations through the approved review process.
8. Mark material as approved only after the required review is complete.
9. Keep the source reference and review history with the approved content.
10. Periodically check for new guidance, corrections, or withdrawn material.

Unreviewed material must remain excluded from the approved retrieval collection.

## 6. Knowledge Document Metadata

The proposed knowledge-document metadata includes:

- `document_id`: unique identifier.
- `title`: source document title.
- `organization`: publisher.
- `source_url`: verified original URL.
- `language`: source language.
- `topics`: relevant topic categories.
- `content`: approved extracted educational text.
- `review_status`: pending_review, approved, or retired.
- `reviewed_at`: last content-review date.
- `last_updated_at`: last known source update date.

The exact schema will be confirmed during implementation planning.

## 7. Source Attribution

When the chatbot uses approved source material, its answer should provide accurate attribution where applicable.

Source references must:
- Point to the actual source used.
- Identify the correct title and publisher when available.
- Avoid fabricated URLs, titles, dates, and organizations.
- Avoid implying that a source supports a claim when it does not.
- Preserve the distinction between source publication dates and project review dates.

If no adequate supporting evidence is found, the chatbot must use a suitable safe fallback rather than inventing an answer or citation.

## 8. English and Kiswahili

The project supports English and Kiswahili.

Content prepared or translated into Kiswahili must preserve the meaning of the approved source. Safety-critical instructions and clinical terminology require appropriate review.

Machine translation alone does not constitute approval of medical content.

Where no reviewed translation exists, the system must not pretend that an unreviewed translation has been clinically validated.

## 9. Content Maintenance

The project must define a maintenance process before public deployment.

The process should:
- Check official publishers for updated guidance.
- Record when a source was last checked.
- Identify content affected by updated recommendations.
- Remove or retire superseded material.
- Re-review affected answers and retrieval tests.
- Preserve sufficient history to understand why content was approved or retired.

The exact review interval remains undecided and should depend on source requirements, clinical risk, and available review capacity.

## 10. Safety and Privacy

- Only approved documents may be treated as trusted health knowledge.
- Source approval does not authorize the chatbot to diagnose or prescribe.
- Individual treatment decisions must be referred to qualified health professionals.
- Urgent-situation guidance must follow an approved safety policy.
- Personal or sensitive information must not be added to source metadata unnecessarily.
- Downloaded documents and extracted content must be handled according to applicable permissions and privacy requirements.
- External model providers must not be assumed to have permission to retain or reuse health-related inputs.
- Persistent conversation storage remains undecided and is not authorized by this document.

## 11. Open Decisions

1. Designated qualified health-content reviewer.
2. Confirmation that the candidate national guidelines remain current.
3. Final approved documents for each of the nine topic areas.
4. Content-use permissions and any licensing restrictions.
5. Approved English and Kiswahili review process.
6. Content-review and source-checking frequency.
7. Process for handling conflicting recommendations.
8. Process for verifying referral services and contact details.
9. Knowledge retrieval and indexing technology.
10. Final source metadata schema.

## 12. Acceptance Criteria

This strategy is ready for approval when the project owner confirms that:

- Candidate sources and their proposed uses are documented.
- Candidate sources are not misrepresented as already approved.
- The review and approval workflow is clear.
- The nine initial topic areas are represented.
- Source attribution and content maintenance are addressed.
- Open clinical, licensing, and governance decisions remain explicit.

Approval of this strategy does not automatically approve any specific medical content for use in the chatbot.

## 13. Approval Record

Status: Draft for review.

Project owner approval: Pending.

Approval date: Pending.
