# HIV/SRH Education Chatbot — Requirements Specification

**Project phase:** Phase 2 — Requirements and Design
**Step:** 1 — Define and Approve Project Requirements
**Status:** Draft for user review — approval pending
**Version:** 1.0
**Date:** 26 October 2026

## 1. Project Purpose

The HIV/SRH Education Chatbot will provide accessible, evidence-based educational information about HIV and sexual and reproductive health (SRH). It will help users understand health topics, prevention options, testing, treatment education, and available sources of support.

The chatbot will prioritize reliable health information, clear communication, privacy, and appropriate referral to qualified health professionals and services.

It is an educational information tool, not a replacement for professional healthcare.

## 2. Target Audience

**Initial audience: General public.**

The application will initially be designed for members of the general public seeking HIV and SRH educational information.

The requirements for age restrictions, age-appropriate responses, and access by minors remain subject to a safety and policy decision before public deployment.

## 3. Initial Scope and Topics

The initial educational scope includes:

1. HIV prevention.
2. HIV testing.
3. HIV treatment education.
4. HIV-related stigma and discrimination.
5. Sexual health.
6. Contraception.
7. Pregnancy and reproductive health.
8. Sexually transmitted infections (STIs) other than HIV.
9. Other relevant SRH educational topics, subject to review and approval.

The chatbot will explain approved topics in clear, understandable language and distinguish general educational information from advice requiring individual clinical assessment.

## 4. Language Requirements

- **English (`en`)** — supported initial language.
- **Kiswahili (`sw`)** — supported initial language.

The chatbot should accept questions and provide responses in the supported language selected or reasonably identified from the user's message.

Health-related translations must preserve medical meaning. Important safety instructions, referrals, and limitations must be understandable in both languages. Language quality should be evaluated before deployment.

## 5. Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | The system shall accept user questions about approved HIV and SRH topics. |
| FR-02 | The system shall provide clear, relevant educational responses within the approved scope. |
| FR-03 | Health-related answers shall be grounded in an approved, reviewed knowledge base once implemented. |
| FR-04 | The system shall identify or provide supporting sources when available and applicable. It must not invent references or imply that an unsupported answer is verified. |
| FR-05 | The system shall support English and Kiswahili interactions. |
| FR-06 | The system shall communicate uncertainty and abstain from giving unsupported or unsafe answers. |
| FR-07 | The system shall direct users to qualified health professionals or appropriate services when individual assessment, urgent care, or other human support is needed. |
| FR-08 | The application shall expose a health endpoint to check whether the API is running. |
| FR-09 | The system shall clearly communicate that it provides education and does not diagnose medical conditions or replace professional care. |
| FR-10 | The system shall handle unsupported topics and unclear questions safely, asking for clarification or providing an appropriate referral when necessary. |

## 6. Health-Safety Requirements

- The chatbot shall not diagnose HIV, another STI, pregnancy, or any other medical condition.
- It shall not claim that a user has or does not have HIV based on a conversation.
- It shall not prescribe medication, recommend an individualized treatment change, or advise a user to start or stop prescribed treatment.
- It shall not fabricate medical facts, citations, service locations, telephone numbers, or referral availability.
- Responses about testing, prevention, treatment, contraception, pregnancy, and STIs shall be based on approved and appropriately reviewed sources.
- The system shall communicate limitations and uncertainty where evidence is incomplete or a question requires individual clinical assessment.
- Users needing personal medical advice shall be directed to qualified health professionals or appropriate health services.
- Potentially urgent situations shall receive a suitable, reviewed referral response. The final rules for urgent situations and specific referral wording remain to be approved.
- The chatbot shall use respectful, non-stigmatizing, non-discriminatory language.
- The system shall not request unnecessary intimate, identifying, or medical information.
- Safety-critical responses and Kiswahili translations shall be included in testing before deployment.

## 7. Knowledge Base and Content Governance

The planned system will use an approved health knowledge base. A retrieval-augmented generation (RAG) approach is a proposed technical direction, not an implemented feature.

Before health content is made available to users:

1. Source organizations and documents must be identified and approved.
2. Content must be checked for relevance, accuracy, currency, and suitability for the intended audience.
3. A qualified health reviewer or designated content-review process must be identified.
4. Source attribution and review dates should be retained where applicable.
5. Outdated or superseded content must be reviewed and updated.
6. The system must be tested for unsupported claims, misleading summaries, and incorrect source attribution.

**Open decision:** The approved source list and responsibility for clinical content review must be confirmed before the knowledge base is treated as authoritative.

## 8. Privacy and Security Requirements

The final conversation-storage policy has not yet been decided.

Regardless of the final policy, the system shall:

- Minimize the collection of personal and sensitive information.
- Avoid requesting names, exact addresses, contact details, or other identifiers unless a clearly justified feature requires them.
- Protect application credentials and secrets using environment configuration rather than hard-coding them in source files.
- Restrict access to any stored information to authorized purposes.
- Avoid exposing sensitive conversation content in application logs, error messages, or analytics.
- Define applicable consent, access, retention, deletion, and security procedures before collecting or retaining conversations.
- Review applicable Tanzanian data-protection and other relevant legal requirements before deployment.

**Open decision:** Whether conversations will be processed without persistent storage by default, stored in a limited form, or handled under another explicitly approved policy.

No persistent conversation-storage feature is authorized by this draft alone.

## 9. Proposed Technical Direction

The following is the planned direction, not a claim that these features have already been built:

- **Backend:** Python and FastAPI, using the existing project baseline.
- **Knowledge retrieval:** An approved knowledge base, potentially implemented using RAG.
- **Language support:** English and Kiswahili.
- **Configuration:** Environment-based settings and protected secrets.
- **Testing:** Automated API and configuration tests, together with health-answer quality, source-grounding, language, and safety evaluations.
- **Data storage:** To be determined after the privacy and data-governance decisions.
- **Deployment:** To be determined after security, privacy, testing, and operational requirements have been reviewed.

Any additional model provider, database, hosting platform, or external service must be selected deliberately and evaluated for cost, privacy, security, and suitability.

## 10. Non-Functional Requirements

- **Accuracy:** Health answers must be supported by approved sources within the system's intended scope.
- **Safety:** The chatbot must abstain or refer appropriately when a safe, evidence-based response cannot be provided.
- **Reliability:** API endpoints and error handling must behave predictably.
- **Maintainability:** Code, configuration, documentation, and tests must be organized so that the application can be maintained.
- **Security:** Secrets and sensitive data must be protected, and unnecessary data collection avoided.
- **Accessibility:** Responses should use clear language and be suitable for users with different levels of health literacy.
- **Performance:** The system should respond within an acceptable time under its intended deployment conditions; measurable targets remain to be defined.
- **Bilingual quality:** English and Kiswahili responses must be evaluated for meaning, clarity, and safety.
- **Traceability:** Important health claims should be traceable to approved sources where applicable.
- **Testability:** Requirements must be translated into test cases and evaluated before deployment.

## 11. Out of Scope

The chatbot is not intended to:

- Diagnose HIV, STIs, pregnancy, or other conditions.
- Replace a clinician, counsellor, testing service, or other qualified healthcare provider.
- Prescribe treatment or make individualized treatment decisions.
- Guarantee that every answer is correct or that a particular service is available.
- Collect or retain personal health histories by default without an explicitly approved design.
- Provide unreviewed medical content as authoritative guidance.

## 12. Acceptance Criteria

The requirements will be considered ready for implementation planning when:

1. The intended audience and initial topic scope are approved.
2. English and Kiswahili requirements are approved.
3. The health-safety and referral approach is defined sufficiently for implementation.
4. Approved knowledge sources and the content-review process are identified, or their selection is assigned as an explicit prerequisite.
5. Conversation privacy and data-handling decisions are documented.
6. Security, evaluation, and deployment prerequisites are recorded.
7. The requirements are testable and do not imply that unimplemented features already exist.
8. The project owner explicitly approves this specification.

The existing nine Phase 1 tests remain the baseline for the current API. Passing them does not, by itself, demonstrate that future health answers are medically accurate or safe.

## 13. Decisions Register

| Decision | Current status |
|---|---|
| Initial audience | **Decided:** General public |
| Initial topics | **Decided:** All nine topics listed in Section 3 |
| Initial languages | English and Kiswahili |
| Conversation privacy | **Undecided** |
| Access by minors and age-related safeguards | Open |
| Approved health-information sources | Open |
| Clinical/content reviewer | Open |
| Urgent-situation response and referral wording | Open |
| Referral directory and service verification process | Open |
| Conversation logging and retention | Open |
| Consent, access, and deletion procedures | Open |
| Deployment location and hosting | Open |
| Measurable performance targets | Open |
| Final evaluation thresholds | Open |

## 14. Approval Record

**Specification status:** Draft for review.

**Project owner decision:** Pending.

**Approval date:** Pending.

This document must not be treated as the approved requirements baseline until the project owner explicitly approves the finalized version.