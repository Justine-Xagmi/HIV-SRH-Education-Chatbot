# HIV/SRH Education Chatbot — Testing and Quality Assurance Strategy

**Phase:** 2 — Requirements and Design
**Step:** 8 — Testing and Quality Assurance
**Status:** Draft for review
**Version:** 1.0
**Date:** 26 October 2026

## 1. Purpose

This document defines the proposed testing strategy for the HIV/SRH Education Chatbot.

The goal is to verify that the application behaves correctly, provides evidence-grounded educational information, follows approved safety rules, protects sensitive information, and meets the project's functional and non-functional requirements.

This document defines the planned tests and release criteria. It does not mean that the future chatbot has been implemented or that the proposed tests have already passed.

## 2. Testing Principles

Testing must follow these principles:

1. Test requirements before relying on the application in practice.
2. Automate repeatable checks wherever appropriate.
3. Test normal behaviour, invalid inputs, failures, and security boundaries.
4. Test English and Kiswahili independently.
5. Treat clinical safety and privacy failures as release-blocking issues.
6. Use approved medical content and qualified clinical review for clinical assertions.
7. Never use real, identifiable health conversations as routine test fixtures.
8. Use synthetic test data unless a separately approved and justified process permits otherwise.
9. Record test results, defects, corrections, and unresolved risks.
10. Do not describe an untested feature as verified or production-ready.

## 3. Testing Scope

The testing strategy covers:

- Existing application baseline and compatibility.
- API contract and input validation.
- Authentication and authorization.
- Conversation creation, history, continuation, and deletion.
- Health-source retrieval and citation integrity.
- Educational answer quality.
- Clinical safety and referral behaviour.
- English and Kiswahili support.
- Privacy and sensitive-data handling.
- Error handling and service availability.
- Performance and basic resilience.
- Deployment readiness.

## 4. Testing Levels

### 4.1 Unit testing

Test individual functions and components in isolation.

Examples:
- Request validation.
- Language validation.
- Source eligibility checks.
- Safety-rule classification.
- Conversation ownership checks.
- Deletion-related business rules.
- Error-response formatting.

Unit tests should be deterministic and should not require a live external AI provider or production database unless a specific test is designed for that purpose.

### 4.2 Integration testing

Test how application components work together.

Examples:
- API routes and request models.
- API and database interactions.
- Authentication and protected endpoints.
- Retrieval and approved source metadata.
- Conversation and message persistence.
- Deletion of a conversation and its associated messages.
- External AI-provider error handling.

Use an isolated test database and controlled test services rather than production data.

### 4.3 API contract testing

Verify that the implemented API follows the approved API contract.

The existing `GET /` and `GET /health` endpoints must remain compatible.

The proposed endpoints are:
- `GET /api/v1/languages`
- `POST /api/v1/chat`

Tests must verify request fields, response fields, validation rules, status codes, and the standardized error envelope.

The final implemented contract must match the approved `docs/API_CONTRACT.md`.

### 4.4 End-to-end testing

Test complete user journeys through the application.

Examples:
- Register or sign in.
- Ask an educational question.
- Receive an answer in the selected language.
- View the supporting sources.
- Save and reopen a conversation.
- Continue an existing conversation.
- Delete a conversation and verify it is no longer accessible.
- Attempt unauthorized access and verify it is denied.

### 4.5 Clinical-content review

Automated tests alone cannot establish that health advice is clinically accurate.

A qualified healthcare professional must review:
- Clinical claims.
- Safety-critical answer templates.
- Urgent-situation responses.
- HIV testing and treatment education.
- Possible recent HIV exposure responses.
- Pregnancy-related safety guidance.
- Referral wording.
- Safety-critical English and Kiswahili translations.

Review outcomes must be recorded. Content that has not passed the required review must not be treated as approved knowledge.

### 4.6 Security and privacy testing

Test whether the application protects sensitive information and enforces access restrictions.

Examples:
- Unauthorized conversation access.
- Cross-user access attempts.
- Token and session handling.
- Sensitive information in application logs.
- Deletion behaviour.
- Database and secret configuration.
- External-provider data flows.
- Backup and restoration behaviour, where implemented.

### 4.7 Performance and resilience testing

Test whether the service responds acceptably under expected usage and handles failures safely.

Examples:
- Concurrent requests within the agreed test load.
- Slow or unavailable AI providers.
- Database connection failures.
- Request timeouts.
- Rate limits, if implemented.
- Large but valid messages.
- Recovery after temporary service failures.

Performance targets must be defined before release testing. No performance threshold is assumed by this draft.

## 5. API Validation Test Plan

### 5.1 Language endpoint

For `GET /api/v1/languages`, verify that:
- The endpoint responds successfully.
- English (`en`) and Kiswahili (`sw`) are listed.
- The response follows the documented contract.
- An internal error does not expose secrets or sensitive details.

### 5.2 Chat request validation

For `POST /api/v1/chat`, verify that:
- A valid message and supported language are accepted.
- The language field is required.
- Unsupported language codes are rejected.
- Missing messages are rejected.
- Empty or whitespace-only messages are rejected.
- Messages exceeding the 2,000-character limit are rejected.
- Malformed JSON is handled appropriately.
- Invalid fields produce the documented error response.
- Error messages do not expose stack traces, secrets, or internal configuration.

The exact status codes must match the approved API contract.

### 5.3 Chat response validation

Verify that a successful response contains:
- `answer`
- `language`
- `sources`
- `safety_notice`

Also verify that:
- The returned language matches the selected language.
- Source entries contain only supported metadata.
- Citations correspond to actual retrieved sources.
- The answer does not invent source details.
- Safety notices are present when required by the approved policy.
- Provider failures do not produce fabricated answers.

### 5.4 Rate limiting

If rate limiting is implemented, verify that:
- Excessive requests are handled according to the configured policy.
- The documented error response and status code are returned.
- Legitimate users can continue after the limit window ends.
- Rate-limit responses do not disclose sensitive account information.

## 6. Clinical Safety Test Plan

All scenarios below are test categories, not clinical instructions. The expected answer wording must be reviewed by the qualified healthcare professional.

### 6.1 General educational questions

Test questions about:
- HIV prevention.
- HIV testing.
- HIV treatment education.
- Stigma and discrimination.
- Sexual health.
- Contraception.
- Pregnancy and reproductive health.
- Other sexually transmitted infections.
- Other approved SRH topics.

Expected behaviour:
- Provide relevant, understandable educational information when approved evidence is available.
- Use appropriate source attribution.
- Avoid unsupported or misleading claims.
- Recommend professional care when an individual assessment is needed.

### 6.2 Diagnosis and individualized treatment

Use synthetic prompts asking the chatbot to diagnose a condition, determine HIV status, prescribe medication, or change an existing treatment plan.

Expected behaviour:
- Do not diagnose or prescribe.
- Explain the chatbot's limitations.
- Provide safe general information when appropriate.
- Refer the user to qualified healthcare services for individualized decisions.

### 6.3 Urgent situations

Use clinically reviewed synthetic scenarios involving potentially serious symptoms or immediate danger.

Expected behaviour:
- Prioritize appropriate urgent professional assessment.
- Do not delay urgent guidance with unnecessary questions.
- Avoid unsupported treatment instructions.
- Use verified referral information where available.
- Follow the approved safety response for the scenario.

The clinical reviewer must define and approve the specific scenarios and expected responses.

### 6.4 Possible recent HIV exposure

Test synthetic questions that describe possible recent exposure.

Expected behaviour:
- Recognize that timely professional assessment may matter.
- Direct the user promptly to an appropriate healthcare service.
- Avoid diagnosing infection or estimating individual risk without an approved basis.
- Use only current, clinically reviewed guidance for specific prevention or testing details.

### 6.5 HIV test results

Test synthetic questions about positive, negative, unclear, or invalid results.

Expected behaviour:
- Explain general concepts using approved information.
- Avoid making an unsupported diagnosis from the user's description.
- Recommend appropriate professional interpretation, confirmation, or follow-up.

### 6.6 Pregnancy, assault, and crisis scenarios

Test clinically reviewed synthetic scenarios involving:
- Potential pregnancy-related emergencies.
- Sexual assault or coercion.
- Immediate personal danger.
- Self-harm or other crisis signals.

Expected behaviour:
- Use the appropriate reviewed safety response.
- Respond respectfully and without blame.
- Prioritize immediate safety and appropriate professional support.
- Avoid invented contact details or false claims of emergency intervention.

### 6.7 Unsupported or uncertain questions

Test questions outside the approved knowledge scope and questions for which the source collection contains no adequate evidence.

Expected behaviour:
- Acknowledge uncertainty or the lack of approved information.
- Avoid inventing medical facts or citations.
- Provide a suitable safe referral or fallback where appropriate.

## 7. Knowledge Base and Retrieval Testing

Verify that:
- Only documents marked `approved` are eligible for trusted retrieval.
- Documents marked `pending_review` or `retired` are excluded.
- Retrieved passages are relevant to the user's question.
- Sources support the claims attributed to them.
- Source titles, organizations, and URLs match stored metadata.
- Missing or outdated source information is handled safely.
- Conflicting recommendations are not silently combined into an invented rule.
- Updated or retired source content is handled according to the approved maintenance process.
- Retrieval failures trigger a safe fallback instead of fabricated content.

Tests must use approved or synthetic test documents with known expected results.

## 8. English and Kiswahili Testing

Maintain test cases in both English and Kiswahili.

Verify that:
- Both supported language codes are accepted.
- Responses use the requested language.
- Medical meaning is preserved across translations.
- Safety-critical instructions remain clear and consistent.
- Medical terminology is appropriate for the intended audience.
- Stigmatizing or judgmental wording is avoided.
- The system does not present unreviewed machine translations as clinically validated.
- Fallback responses work in both languages.
- Source attribution remains accurate regardless of response language.

A fluent and appropriately qualified reviewer should assess language quality. Clinical wording must receive the required health-content review.

## 9. Conversation History and Privacy Testing

### 9.1 Saving and reopening

Verify that:
- A conversation can be saved for an authenticated user.
- The owner can see the conversation in their history.
- The owner can reopen and continue the conversation.
- Messages remain associated with the correct conversation.
- A new conversation does not accidentally display another conversation's messages.

### 9.2 Authorization

Verify that:
- Unauthenticated users cannot access private history.
- One user cannot view another user's conversation.
- One user cannot continue, rename, or delete another user's conversation.
- Changing a conversation identifier does not bypass backend ownership checks.
- Authorization is enforced by the backend.

### 9.3 Deletion

Verify that:
- A user can request deletion of their own conversation.
- Confirmation behaviour follows the approved interface design.
- A successfully deleted conversation is no longer accessible through normal application routes.
- Associated messages are handled according to the approved deletion process.
- Failed deletion does not return a false success result.
- The system handles related caches, backups, and external-provider copies according to the documented retention and deletion rules.

### 9.4 Logging and external processing

Verify that:
- Passwords and authentication tokens do not appear in logs.
- Complete health conversations are not logged by default.
- Sensitive data sent to external providers matches the documented design.
- Access to operational records is restricted.
- Retention and deletion behaviour matches the privacy notice.

## 10. Security Test Plan

Security tests should cover:
- Authentication and token validation.
- Authorization for protected operations.
- Input validation and malformed requests.
- SQL injection and other relevant injection risks.
- Cross-site scripting where applicable to the interface.
- Cross-user data exposure.
- Secret and credential handling.
- Dependency vulnerabilities.
- Database access restrictions.
- Error messages that might reveal internal information.
- Rate limiting and abuse controls where implemented.
- Configuration and deployment security.

Testing must be conducted in an authorized, isolated environment. Any discovered critical security issue must be addressed before release.

## 11. Automated Testing and Tools

The existing project uses Python, FastAPI, and pytest for its baseline.

The initial testing approach should reuse the existing environment and dependencies where possible.

Potential test categories include:
- Unit tests using pytest.
- API tests using the existing FastAPI testing approach.
- Integration tests using isolated test services and a dedicated test database.
- End-to-end tests using an appropriate interface-testing tool if needed.
- Security checks using suitable tools selected during implementation planning.
- Manual clinical and bilingual review using a documented evaluation checklist.

Do not add a dependency merely because it appears in this strategy. Any new tool or package must be justified and reviewed during the relevant implementation step.

The existing baseline has previously passed nine tests. That result is historical baseline evidence, not proof that the future chatbot features have been tested.

## 12. Test Data and Environment

- Use synthetic user accounts and synthetic conversation content.
- Do not use identifiable patient records as ordinary development test data.
- Never use production credentials in automated tests.
- Keep test databases separate from production databases.
- Avoid external API calls in deterministic unit tests.
- Use controlled mocks or test doubles for provider failures and predictable responses.
- Protect any test artefacts that contain sensitive information.
- Document any exceptions to these rules before testing.

## 13. Defect Severity and Release Blocking

### Critical

Examples:
- A user can access another user's health conversations.
- A safety-critical response creates a serious, foreseeable risk.
- Private credentials or sensitive health data are exposed.
- The chatbot bypasses essential clinical safety boundaries.

Release decision: block deployment until corrected and re-tested.

### High

Examples:
- A major safety rule fails in an important scenario.
- Conversation deletion or authorization behaves incorrectly.
- A major source-attribution failure materially misleads users.
- A supported language produces unsafe clinical wording.

Release decision: block the affected release until resolved or formally assessed under an approved risk process.

### Medium

Examples:
- A non-critical API error differs from the documented contract.
- Some non-critical source metadata is missing.
- A recoverable interface or usability defect affects normal use.

Release decision: document and prioritize; assess whether the defect blocks the release.

### Low

Examples:
- Minor wording or layout issues that do not affect safety, privacy, or core functionality.

Release decision: record and schedule for correction.

Severity classifications must consider actual risk, not just the technical size of a defect.

## 14. Release Acceptance Criteria

A release candidate may proceed only when:

1. Required automated tests pass.
2. API behaviour matches the approved contract.
3. Authentication and conversation ownership tests pass.
4. Conversation saving, reopening, and deletion behave as documented.
5. Critical and high-priority safety failures have been resolved.
6. Clinical content and safety-critical response templates have the required qualified review.
7. English and Kiswahili safety checks have passed their approved criteria.
8. Source-grounding and citation-integrity tests pass.
9. Privacy, logging, and external-provider data handling match the approved design.
10. Required security tests have been completed and significant findings addressed.
11. No unresolved release-blocking defects remain.
12. Test results and known limitations are recorded.
13. The project owner approves the release.
14. Applicable privacy, clinical, and deployment requirements have been assessed.

These criteria must be refined into measurable thresholds where appropriate before release. Passing automated tests alone does not establish clinical safety or legal compliance.

## 15. Test Reporting and Maintenance

For each test run, record:
- Test identifier and purpose.
- Requirement or risk covered.
- Test environment and software version.
- Input or synthetic scenario.
- Expected result.
- Actual result.
- Pass or fail status.
- Defect reference where applicable.
- Reviewer or test owner.
- Date and relevant follow-up action.

When a defect is corrected, add or update a regression test so the same failure can be detected in future runs.

Re-run affected tests when API contracts, safety policies, clinical sources, retrieval logic, authentication, storage, or external-provider integrations change.

## 16. Open Decisions

The following decisions remain open:

1. Final test framework and any additional tools.
2. Measurable response-time and load targets.
3. Detailed clinical safety test cases and approved expected responses.
4. Bilingual review and acceptance thresholds.
5. Final database and integration-test environment.
6. Final retention and deletion test requirements.
7. Security testing tools and assessment scope.
8. Regression-test execution frequency.
9. Required test evidence and reporting format.
10. Final release sign-off process and owners.

These decisions must not be treated as resolved until explicitly reviewed.

## 17. Acceptance of This Strategy

This strategy is ready for project-owner approval when the project owner confirms that:

- The main functional and non-functional test areas are covered.
- Clinical safety and bilingual testing are included.
- Conversation history, authorization, and deletion are addressed.
- Source attribution, privacy, and security are covered.
- Defect severity and release-blocking criteria are documented.
- Open decisions and implementation dependencies are explicit.

Approval of this strategy approves the planned testing approach only. It does not indicate that the tests have been implemented or passed.

## 18. Approval Record

**Project owner approval:** Pending.

**Qualified healthcare reviewer:** Available; formal review of clinical test cases pending.

**Test implementation status:** Not started.

**Release approval:** Not granted.

**Status:** Draft for review.
