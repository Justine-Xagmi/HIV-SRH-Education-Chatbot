# HIV/SRH Education Chatbot — Privacy and Data Protection Design

**Phase:** 2 — Requirements and Design
**Step:** 7 — Privacy and Data Protection
**Status:** Draft for review
**Version:** 1.0
**Date:** 26 October 2026

## 1. Purpose

This document defines the proposed privacy and data-protection requirements for the HIV/SRH Education Chatbot.

The chatbot will allow authenticated users to save conversation history, return to previous conversations, keep conversations they want to retain, and delete conversations they no longer want.

Because conversations may contain sensitive HIV and sexual/reproductive health information, privacy and security must be considered before implementing conversation storage.

This document defines the intended design. It does not claim that storage, deletion, security controls, or legal compliance have already been implemented or verified.

## 2. Approved Product Decision

The project owner's requirements are:

- Conversation history must be saved so users can return to previous conversations.
- Users must be able to keep conversations they want to retain.
- Users must have an option to delete conversations.
- Users must be able to distinguish saved conversations from deleted ones.
- Conversation history must be private to the account that owns it.
- Saving and deleting conversations must be explicit, understandable user actions.
- Privacy and security controls must be tested before public deployment.

The implementation must not silently replace these requirements with a no-history design.

## 3. Privacy Principles

The design will follow these principles:

1. Transparency: explain what information is stored and why.
2. Data minimization: collect only what is needed for the service.
3. Purpose limitation: use stored data only for disclosed and approved purposes.
4. Confidentiality: prevent unauthorized access to health conversations.
5. User control: provide accessible history and deletion controls.
6. Security by design: protect data during transmission, storage, and access.
7. Retention limitation: do not retain personal information longer than justified by the approved purpose and applicable requirements.
8. Accountability: document access rules, retention decisions, security testing, and incidents.
9. Sensitive-data protection: treat health-related conversation content as highly sensitive.
10. Honest communication: do not promise security, confidentiality, or complete deletion beyond what the system can demonstrate.

## 4. Data Inventory

### 4.1 Account information

The service may process account information needed for authentication and account management, such as:
- Internal user identifier.
- Login identifier, such as an email address, if selected for the final design.
- Password hash rather than a stored plaintext password.
- Account creation and relevant security timestamps.

The exact account fields will follow the existing authentication design. Additional identifying information must not be collected without a defined purpose.

### 4.2 Conversation information

The proposed conversation record includes:
- Conversation identifier.
- Owner's internal user identifier.
- Conversation title, if titles are supported.
- Creation timestamp.
- Last-updated timestamp.
- Retention or deletion status, where needed.
- Optional user-controlled title or display metadata.

Each message may contain:
- Message identifier.
- Conversation identifier.
- Role, such as user or assistant.
- Message text.
- Creation timestamp.
- Language, when needed.
- Source references associated with an assistant response, where available.

The final data model must avoid duplicating sensitive content unnecessarily.

### 4.3 Operational information

The application may need limited operational records for reliability and security, such as error codes, request timestamps, and service-health information.

Routine logs must not contain complete health conversations, authentication tokens, passwords, or unnecessary personal identifiers.

Any additional diagnostic or analytics data requires a defined purpose, access rules, and retention decision.

## 5. Conversation History and User Controls

### 5.1 Saving history

Authenticated users should be able to:
- Start a new conversation.
- View their own saved conversation list.
- Reopen a saved conversation.
- Continue a previous conversation.
- Identify conversations using clear titles or timestamps.
- Delete an individual conversation.
- Understand whether a conversation remains saved.

A conversation must be associated with its owner using a trusted server-side identity, not an owner identifier supplied and trusted directly from the client.

### 5.2 Keeping conversations

A conversation remains saved until the user deletes it or another clearly disclosed, approved retention rule applies.

If automatic expiry, account closure deletion, or another retention mechanism is introduced, its behaviour must be documented before implementation and explained to users.

The initial design does not authorize an undisclosed automatic deletion period.

### 5.3 Deleting a conversation

The user should be able to delete an individual conversation from the conversation-history interface.

The intended deletion behaviour is:

1. Identify the conversation belonging to the authenticated user.
2. Ask for confirmation when appropriate to prevent accidental deletion.
3. Remove the conversation from the user's accessible history.
4. Remove its associated messages and conversation-specific stored content according to the approved deletion process.
5. Ensure the deleted conversation cannot be reopened through normal application access.
6. Handle related copies, caches, search indexes, and backups according to a documented retention and deletion schedule.
7. Provide clear confirmation only after the application has successfully completed the defined deletion action.

The implementation must not report successful deletion if the operation failed.

### 5.4 Deletion and backups

Deleting a conversation from the application does not automatically prove that every copy has been erased from backups, external AI providers, security logs, or other systems.

Before deployment, the project must define:
- Whether backups contain conversation data.
- How long backup copies are retained.
- How deletion requests affect backup restoration.
- How external providers handle submitted messages and deletion requests.
- Whether any legally required retention exceptions apply.
- How users will be informed about the actual deletion scope.

The system must not claim immediate, permanent deletion from every system unless that outcome is technically verified.

### 5.5 Whole-account deletion

Account deletion is a separate feature from deleting one conversation.

If account deletion is introduced, the project must define how it affects conversation history, account information, associated records, backups, and any retention obligations.

This feature must be reviewed and tested separately.

## 6. Authentication and Authorization

- Conversation history must require appropriate authentication.
- Each request to view, continue, rename, or delete a conversation must verify ownership or another explicitly authorized access rule.
- Users must not be able to access another user's conversations by changing an identifier in a URL or request body.
- Authorization must be enforced by the backend, not only by hiding interface elements.
- Session and token handling must follow the approved authentication design.
- Passwords must never be stored as plaintext.
- Sensitive tokens and credentials must not be written to logs.
- Administrative access must be limited to authorized personnel and legitimate operational purposes.
- Access-control failures must not reveal whether another user's private conversation exists.

## 7. Storage and Security

Before storing conversations in a database, the implementation design must specify:
- The approved database and hosting environment.
- Encryption in transit.
- Appropriate protection of stored data, including encryption-at-rest requirements based on the selected infrastructure.
- Database credentials and secret management.
- Least-privilege database access.
- Backup protection and restoration procedures.
- Security updates and dependency maintenance.
- Monitoring for unauthorized access and suspicious activity.
- Secure deletion and incident-response procedures.

Security measures must be verified in the actual deployment environment. Documentation alone is not evidence that the controls work.

## 8. External AI Providers

If conversation messages are sent to an external AI provider:

- Identify the provider and the data it receives.
- Review applicable retention, logging, training, and deletion terms.
- Check the provider's security and privacy documentation.
- Disclose relevant processing to users before public deployment.
- Send only the information necessary to produce the response.
- Avoid sending direct identifiers unless required for a documented and approved purpose.
- Do not assume that deleting an application conversation deletes provider-side copies.
- Assess applicable rules for processing or transferring personal data outside Tanzania.
- Provide an alternative or safe fallback if the provider is unavailable.

The selected AI provider, its data-handling terms, and any required cross-border transfer arrangements remain undecided.

## 9. Logs, Analytics, and Monitoring

Operational logging must be designed to diagnose failures without unnecessarily exposing sensitive conversations.

The proposed rules are:
- Do not log full message text by default.
- Do not log passwords, access tokens, or secret keys.
- Avoid placing sensitive health details in exception messages.
- Use internal identifiers only when necessary and protect the resulting records.
- Restrict log access to authorized maintainers.
- Define retention periods for operational logs.
- Assess analytics tools before enabling them.
- Do not reuse conversation content for model training, marketing, or unrelated research without a separate documented purpose, appropriate legal basis, and any required user choice or authorization.

Logging and analytics retention periods must be selected before deployment.

## 10. Privacy Notice and User Information

Before users submit health-related messages, the interface should provide a clear privacy notice explaining, in understandable language:

- What account information is collected.
- That conversations are saved to provide conversation history.
- What the service uses the stored conversations for.
- Who may process the information, including external providers where applicable.
- How long information is retained or how the retention period is determined.
- How users can view and delete their conversations.
- What deletion does and does not remove.
- How users can raise privacy concerns or exercise applicable rights.
- Any important limitations to confidentiality.

The notice must accurately describe the final implementation and must be reviewed before public deployment.

The project must determine whether consent or another lawful basis is required for each processing purpose. This decision must not be inferred from the user's ability to create an account.

## 11. Applicable Tanzanian Data-Protection Requirements

The project must assess the applicable requirements before public deployment, including:

- The Personal Data Protection Act, 2022.
- The Personal Data Protection (Personal Data Collection and Processing) Regulations, 2023, including applicable amendments.
- Applicable requirements concerning sensitive personal data, transparency, security, retention, data-subject rights, and cross-border processing.
- Applicable registration, governance, and other obligations for the entities and providers involved.

Official reference sources:

- Office of the Attorney General — Personal Data Protection Act, 2022:
  https://oagmis.oag.go.tz/portal/acts/237
- Office of the Attorney General — Personal Data Protection (Personal Data Collection and Processing) Regulations, 2023:
  https://oagmis.oag.go.tz/portal/legislation/1350
- Office of the Attorney General — 2024 amendment:
  https://oagmis.oag.go.tz/portal/legislation/3833
- Personal Data Protection Commission:
  https://pdpc.go.tz/

These references are starting points for a compliance review, not a substitute for reviewing the applicable legal text and obtaining qualified advice where necessary.

The project's legal obligations, registration requirements, and lawful bases for processing must be confirmed for the actual operator, hosting arrangements, intended users, and data flows.

## 12. Security and Privacy Testing

Before deployment, tests must verify:
- An authenticated user can view their own conversations.
- An unauthenticated user cannot access private history.
- A user cannot read or delete another user's conversations.
- Reopening a saved conversation restores the intended history.
- Deleting a conversation removes it from normal access.
- Associated messages are handled according to the approved deletion rules.
- Failed deletion operations do not produce false success messages.
- Logs do not expose complete sensitive conversations or credentials.
- Data sent to external providers matches the documented design.
- Privacy notices match the real storage and deletion behaviour.
- Backup restoration does not silently reintroduce conversations that should remain deleted.
- Access control, session handling, and relevant security protections are tested.

## 13. Open Decisions

The following decisions remain unresolved:

1. Final conversation database and hosting environment.
2. Exact account and conversation data fields.
3. Retention period and any approved expiry rules.
4. Deletion behaviour for backups, logs, caches, and external providers.
5. Whether whole-account deletion will be supported in the first release.
6. Selected AI provider and its retention and training policies.
7. Cross-border data-transfer assessment, where applicable.
8. Privacy notice wording and lawful basis for each processing purpose.
9. Registration and other applicable compliance obligations.
10. Logging and analytics retention periods.
11. Whether users may export or download their conversations.
12. The final procedure for privacy requests and security incidents.

These decisions must not be treated as resolved until explicitly reviewed and approved.

## 14. Acceptance Criteria

This design is ready for approval when the project owner confirms that:

- Saved conversation history is a defined product requirement.
- Users can keep or delete individual conversations.
- Ownership and backend authorization are required.
- Sensitive information, logs, and external processing are addressed.
- Deletion scope and backup limitations are explained honestly.
- Privacy notices, retention rules, and compliance review are included.
- Security tests and unresolved decisions are documented.

Approval of this design does not mean that conversation storage, deletion, security, or legal compliance has already been implemented or verified.

## 15. Approval Record

**Project owner decision on conversation history:** Save conversations and allow users to keep or delete them.

**Project owner approval of this document:** Pending.

**Privacy/legal review:** Pending.

**Implementation status:** Not started.

**Status:** Draft for review.
