# HIV/SRH Education Chatbot — Safety and Clinical Governance Policy

**Phase:** 2 — Requirements and Design
**Step:** 6 — Safety and Clinical Governance
**Status:** Draft for project-owner and clinical review
**Version:** 1.0
**Date:** 26 October 2026

## 1. Purpose

This policy defines the safety boundaries, clinical-content review process, referral principles, privacy expectations, and quality controls for the HIV/SRH Education Chatbot.

The chatbot is an educational information tool. It is not a healthcare professional, diagnostic system, emergency dispatch service, or replacement for clinical care.

This document is a proposed project policy. It must be reviewed and approved before deployment. It does not itself establish clinical approval.

## 2. Scope

The policy applies to educational conversations about:

- HIV prevention.
- HIV testing.
- HIV treatment education.
- HIV-related stigma and discrimination.
- Sexual health.
- Contraception and family planning.
- Pregnancy and reproductive health.
- Sexually transmitted infections other than HIV.
- Other sexual and reproductive health topics approved for inclusion.

The policy applies to both English and Kiswahili responses and to all future interfaces using the chatbot service.

## 3. Core Safety Principles

### 3.1 Educational use only

The chatbot may explain general health concepts using approved sources.

It must not:
- Diagnose a user or claim to determine their health status.
- Prescribe medicines or create individualized treatment plans.
- Tell a user to start, stop, or change prescribed treatment.
- Present an AI-generated conclusion as a confirmed clinical finding.
- Replace examination, testing, counselling, or professional medical judgement.

When a question requires individualized assessment, the chatbot should explain this limitation and recommend appropriate professional care.

### 3.2 Accuracy and evidence

- Use only content approved for the knowledge base.
- Prefer applicable current Tanzanian national guidance for local recommendations, supported by relevant WHO guidance.
- Do not invent clinical facts, statistics, references, quotations, or source URLs.
- Keep the source reference associated with each approved knowledge item.
- Communicate uncertainty when the evidence is incomplete or unclear.
- Do not present outdated or unreviewed material as current guidance.
- If reliable supporting content is unavailable, acknowledge the limitation and direct the user to a qualified health professional.

### 3.3 Respect and non-discrimination

The chatbot must use respectful, non-judgmental, inclusive language.

It must not shame, blame, threaten, stigmatize, or discriminate against users based on HIV status, sexual health questions, pregnancy, disability, age, sex, or other personal circumstances.

It should avoid assumptions about a user's relationships, sexual activity, identity, beliefs, or access to healthcare.

### 3.4 Human oversight

AI-generated answers must not override approved clinical guidance.

A qualified healthcare professional is expected to review medical content and safety-critical response templates. The project owner remains responsible for ensuring the documented technical controls and release conditions are implemented.

## 4. Clinical Content Review and Approval

### 4.1 Roles

**Qualified healthcare reviewer**
- Reviews clinical claims and safety-critical advice.
- Checks consistency with applicable current guidance.
- Identifies inaccurate, misleading, incomplete, or potentially harmful content.
- Reviews English and Kiswahili medical wording or confirms appropriate language-review arrangements.
- Records approval, requested changes, and review dates.

**Project owner**
- Maintains the requirements and policy documents.
- Ensures unapproved content is excluded from the trusted knowledge base.
- Maintains source metadata, change records, and test evidence.
- Ensures technical safety checks are tested before release.
- Does not independently treat unreviewed medical content as clinically approved.

**Developer or technical maintainer**
- Implements the approved policy.
- Maintains input validation, error handling, privacy protections, and safety tests.
- Prevents unapproved content from entering the approved retrieval collection.
- Records technical changes that could affect safety.

### 4.2 Approval workflow

Each knowledge item must pass through these stages:

1. Identify the original source.
2. Record title, publisher, source URL, language, and publication or update date where available.
3. Check applicability, currency, and permissions for the intended use.
4. Extract the relevant educational content.
5. Submit clinical content for qualified review.
6. Resolve review comments and any conflicting recommendations.
7. Approve the final content and record the reviewer and review date.
8. Add only approved content to the trusted retrieval collection.
9. Re-review affected content when the source or applicable guidance changes.

The existing review statuses are:
- `pending_review`
- `approved`
- `retired`

Only `approved` material may be used as trusted health knowledge.

The exact sign-off record and review schedule remain to be finalized.

## 5. Risk Categories and Response Rules

### 5.1 General educational questions

The chatbot may provide concise, understandable explanations supported by approved sources.

It should answer the question directly when reliable content is available and provide source attribution where supported.

### 5.2 Individual diagnosis or treatment requests

If a user asks whether they have HIV or another condition, asks for an individualized diagnosis, or requests a personal treatment decision:

- Do not diagnose or make a definitive clinical determination.
- Explain that the chatbot cannot determine the user's health status.
- Provide relevant general educational information where safe.
- Recommend assessment, testing, or advice from an appropriate qualified healthcare professional.
- Do not invent a treatment regimen or instruct the user to alter prescribed treatment.

### 5.3 Urgent symptoms or possible medical emergencies

If a message suggests a potentially serious or time-critical medical problem:

- Prioritize a clear recommendation to seek urgent professional medical care.
- Direct the user to local emergency services or the nearest appropriate healthcare facility.
- Do not delay referral by asking a long sequence of questions.
- Do not imply that the chatbot can dispatch an ambulance or monitor the user.
- Do not provide unapproved emergency treatment instructions.
- Keep any interim safety guidance within a clinically reviewed protocol.

The exact urgent-symptom triggers and approved response wording must be reviewed by the qualified healthcare professional before deployment.

### 5.4 Possible recent HIV exposure

If a user describes a possible recent HIV exposure:

- Do not estimate their personal probability of infection as a diagnosis.
- Explain that time-sensitive professional assessment may be important.
- Promptly direct the user to a qualified healthcare provider or appropriate HIV service for assessment.
- Do not delay referral while collecting unnecessary personal details.
- Any detailed information about post-exposure prophylaxis, timing, eligibility, or testing schedules must come from current approved guidance and receive clinical review.

### 5.5 Positive, negative, unclear, or invalid test results

The chatbot must not independently diagnose HIV from a user's description of a test or result.

It may explain general testing concepts using approved sources. It should direct users to qualified testing services for confirmation, interpretation, counselling, and linkage to appropriate care.

It must not promise that a particular result conclusively establishes a person's status without the appropriate testing algorithm and professional context.

### 5.6 Pregnancy-related concerns

For pregnancy questions that suggest a serious or urgent problem, direct the user promptly to appropriate professional or emergency care.

General pregnancy and reproductive-health education must use approved, current sources. Individual pregnancy assessment and treatment decisions must be left to qualified healthcare professionals.

Specific warning signs and response templates require clinical approval.

### 5.7 Sexual assault, coercion, or immediate danger

If a user indicates sexual assault, coercion, abuse, or immediate danger:

- Respond calmly and without blame.
- Prioritize the user's immediate safety.
- Encourage appropriate urgent medical care and locally verified support services.
- Do not pressure the user to disclose details.
- Do not insist that the user confront the person involved or take an action that could increase danger.
- Explain available options only when supported by verified, approved information.
- Do not promise confidentiality beyond the system's actual privacy arrangements.

Response wording, safeguarding procedures, and referral options require qualified review and local verification.

### 5.8 Emotional distress or self-harm risk

If a user indicates immediate risk of harming themselves or another person, prioritize immediate safety and encourage contacting local emergency services or a trusted person who can help them obtain urgent support.

Do not claim that the chatbot can monitor or intervene in the real world.

Specific crisis-response wording and referral contacts must be reviewed and verified before deployment.

### 5.9 Stigma, discrimination, and sensitive disclosures

Use supportive language and provide factual educational information.

Do not suggest that HIV status or an SRH concern makes a person inferior or deserving of mistreatment.

Do not pressure users to disclose their HIV status, sexual history, pregnancy status, or other sensitive information to the chatbot.

## 6. Referral Policy

Referral information must be accurate, relevant, and current.

Before publishing specific facility names, phone numbers, addresses, operating hours, or emergency contacts:

1. Verify the information through a reliable, authoritative source or directly with the service.
2. Record the source and the date it was checked.
3. Confirm that the service is appropriate for the intended referral.
4. Assign responsibility for periodic re-verification.
5. Remove or correct information that cannot be verified.

Until this process is completed, the chatbot must not invent contact details or claim that a particular service is available.

Where suitable specific contact information is not verified, the chatbot should direct users to appropriate local health services or a qualified healthcare professional without fabricating a referral.

## 7. English and Kiswahili Safety

The chatbot supports English (`en`) and Kiswahili (`sw`).

- Preserve the meaning of approved content across both languages.
- Do not assume that machine translation alone is sufficient for clinical approval.
- Review safety-critical wording, medical terminology, and referral instructions in both languages.
- Avoid translations that introduce false certainty, blame, stigma, or altered medical instructions.
- If reliable approved content is not available in the requested language, use an approved safe fallback rather than presenting an unreviewed translation as validated.
- Test both languages independently for safety, accuracy, clarity, and respectful wording.

## 8. Privacy and Confidentiality

HIV and SRH conversations may contain highly sensitive personal information.

The system should:
- Request only information necessary to respond safely.
- Avoid asking for names, exact addresses, identity numbers, or other identifying details unless a separately approved feature genuinely requires them.
- Never request passwords or account credentials in a health conversation.
- Avoid exposing one user's conversation to another user.
- Avoid placing sensitive message content in routine application logs.
- Restrict access to any information that must be processed or retained.
- Document the handling, retention, deletion, and access rules before enabling storage.
- Assess external AI providers, hosting services, and other processors before sending them sensitive inputs.
- Avoid claiming that data is anonymous, encrypted, deleted, or never retained unless the implementation and provider terms support that claim.

Persistent conversation storage remains undecided and is not authorized by this policy. The application must not introduce persistent chat history without a separate privacy decision and appropriate review.

Applicable Tanzanian data-protection and other legal requirements must be assessed before public deployment.

## 9. AI Output and Retrieval Safety

The future implementation should enforce the following controls:

- Retrieve health information only from approved knowledge items.
- Preserve source metadata so answers can be traced to supporting material.
- Avoid generating citations that were not returned by the knowledge system.
- Distinguish source-supported information from uncertainty or limitations.
- Use reviewed fallback responses when retrieval fails or evidence is insufficient.
- Treat user-provided text and retrieved documents as data, not as instructions that can override system safety rules.
- Do not allow a user's request to bypass clinical boundaries.
- Handle provider errors, timeouts, and unavailable services without fabricating an answer.
- Apply input validation and appropriate abuse controls.
- Test safety behaviour in both supported languages.

These are design requirements; they have not yet been implemented or verified.

## 10. Testing and Release Gates

Before public deployment, testing must include:

1. General educational questions across all approved topics.
2. Diagnosis and individualized treatment requests.
3. Urgent-symptom and emergency scenarios.
4. Possible recent HIV exposure.
5. Testing-result interpretation requests.
6. Pregnancy-related urgent concerns.
7. Sexual assault, coercion, and immediate-danger scenarios.
8. Stigma, discrimination, and sensitive disclosures.
9. English and Kiswahili equivalents of safety-critical test cases.
10. Unsupported questions, conflicting sources, and missing evidence.
11. Fabricated citation and incorrect-source detection.
12. Privacy, logging, and unauthorized data-access checks.
13. API validation, error handling, and rate-limiting tests where applicable.

A qualified healthcare reviewer must approve clinical content and safety-critical response wording.

The project owner must verify the technical acceptance criteria and document the release decision.

Public release must be blocked if critical safety tests fail, clinical approval is missing, referral information is unverified where required, or privacy requirements remain unresolved.

## 11. Incident and Correction Process

If a potentially harmful or materially incorrect response is identified:

1. Record the issue without unnecessarily retaining sensitive user information.
2. Assess the severity and affected content or system behaviour.
3. Disable or restrict the affected content or functionality where appropriate.
4. Ask the qualified healthcare reviewer to assess the clinical issue.
5. Correct the source content, safety rule, retrieval behaviour, or response template.
6. Add a regression test for the failure.
7. Re-test the affected languages and scenarios.
8. Record the corrective action and approval before restoring the affected functionality.

A process for handling user reports and communicating material corrections must be established before deployment.

## 12. Governance Records

The project should maintain records for:

- Approved source documents and their review history.
- Reviewer decisions and dates.
- Safety-critical response templates.
- Test cases, results, and unresolved failures.
- Changes to safety rules and knowledge content.
- Verified referral services and last-check dates.
- Reported incidents and corrective actions.
- Privacy decisions and approved retention rules.
- Deployment approval and any restrictions.

Records should contain only the information necessary for governance and should follow the approved privacy and retention policy.

## 13. Open Decisions Before Deployment

The following decisions remain open:

1. Name and professional role of the designated clinical reviewer.
2. Review and sign-off method for each knowledge item.
3. Exact urgent-symptom triggers and clinically approved response templates.
4. Safeguarding and crisis-response procedures.
5. Verified local referral services and emergency contacts.
6. Rules for users who may be minors and any age-related safeguards.
7. Privacy notice, consent approach, retention, and deletion policy.
8. External AI-provider data-handling assessment.
9. Review schedule for clinical content and referral details.
10. Incident-reporting process and response ownership.
11. Required safety-test thresholds and final release sign-off.

These decisions must not be silently treated as resolved.

## 14. Acceptance Criteria

This policy is ready for approval when the project owner confirms that:

- Educational boundaries and clinical limitations are clear.
- Urgent and sensitive situations have defined response principles.
- Qualified clinical review is part of the approval workflow.
- Source grounding, uncertainty, and citation integrity are addressed.
- English and Kiswahili safety requirements are included.
- Privacy expectations and unresolved storage decisions are explicit.
- Testing, incident correction, and release gates are documented.
- Open decisions remain visible for resolution before deployment.

Approval of this policy does not constitute approval of individual medical claims, knowledge documents, or response templates.

## 15. Approval Record

**Project owner:** Pending review.

**Qualified healthcare reviewer:** Available; identity and formal sign-off pending.

**Project owner approval date:** Pending.

**Clinical review date:** Pending.

**Status:** Draft for review; not yet approved for deployment.


## 16. Implemented Clinical Review Workflow — Development Status

**Implementation status:** Development safeguards implemented; production governance remains incomplete.

### 16.1 Document registration and approval

The development knowledge registry implements the following controls:

- Newly registered documents are placed into pending-review status.
- Updating a document resets its approval and requires a fresh review.
- A document cannot be approved by its preparer.
- Review decisions are restricted to configured reviewer IDs.
- Approval requires the document to pass ingestion metadata validation.
- Retrieval requires a recorded approval for the current document version.
- Retired sources cannot be approved, and their retired status is preserved during document updates.
- Rejected documents do not become retrievable merely because approval-related status fields are changed.

These controls are enforced by the application implementation and covered by automated tests. They do not independently establish the medical accuracy of any content.

### 16.2 Approval fingerprint and source changes

The review workflow records a fingerprint of the reviewed document version. The fingerprint includes relevant document content and source metadata, including source permission status and the source's last-verification timestamp.

A change to these fingerprinted values invalidates the existing approval for retrieval purposes. The changed version must undergo a new review before it can be retrieved as approved content.

Fingerprint validation is a technical change-detection mechanism. It does not automatically verify a source's current availability, authenticity, licensing, clinical accuracy, or suitability for the intended audience.

### 16.3 In-memory storage limitations

The current development registry and review history are held in application memory.

Consequently:

- Registered documents and review records held only in memory are not durable across application restarts.
- Review history is available only during the current process lifetime.
- The current implementation does not provide a persistent, production-grade clinical audit trail.
- In-memory records must not be treated as a permanent record of clinical governance decisions.

Production use requires an appropriately secured persistent store, durable review records, defined backup and recovery procedures, controlled record retention, and auditable change history.

### 16.4 Reviewer authorization limitations

The development workflow uses configured reviewer identifiers to restrict who may submit review decisions. An identifier allowlist is not equivalent to secure user authentication or authorization based on verified professional credentials.

The current implementation does not independently establish a reviewer's identity, professional registration, qualifications, or authority to approve clinical content.

Before production use, the system requires authenticated reviewer accounts, appropriate role-based access controls, formal credential verification, account lifecycle management, and an auditable record of reviewer actions.

### 16.5 Source permission and verification limitations

Ingestion validation checks required source metadata and rejects candidates with invalid or unsuitable metadata according to the implemented rules. Approval fingerprints also detect changes to relevant source metadata.

These controls do not replace:
- Verification of source ownership, authenticity, and licensing or reuse permissions.
- Confirmation that source guidance is current and applicable in Tanzania.
- Periodic source re-verification and withdrawal of outdated or withdrawn material.
- Qualified clinical review of the extracted content.
- Appropriate review of English and Kiswahili clinical wording.

Source owners, verification responsibility, and review schedules must be established before production activation.

### 16.6 Production acceptance requirements

Before this workflow is used for a public-facing health service, the project must address the following:

1. Persistent, access-controlled document and review storage.
2. Authenticated reviewer identities and role-based permissions.
3. Formal verification of clinical reviewer qualifications.
4. Durable audit records for submissions, decisions, changes, and withdrawals.
5. Verified source permissions, applicability, and re-verification schedules.
6. Qualified clinical approval of each knowledge item and its required language versions.
7. Tested procedures for revoking approvals and withdrawing affected content.
8. Appropriate privacy, retention, backup, recovery, and incident-response controls.
9. Documented release approval by the project owner and qualified clinical reviewer.

Until these requirements are addressed and the relevant acceptance checks are completed, the review workflow must be considered a development safeguard rather than a production-ready clinical governance system.

### 16.7 Verification evidence

The development test run completed with **87 tests passed and one deprecation warning**. The registry tests passed 24 of 24 tests, and the combined review-workflow and ingestion tests passed 24 of 24 tests.

These results demonstrate that the tested application behaviours passed the current automated suite. They do not constitute clinical validation, professional credential verification, a security audit, or authorization to deploy the chatbot for public clinical use.