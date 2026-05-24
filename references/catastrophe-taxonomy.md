# Catastrophe Taxonomy

Use this file to decide what counts as a system vital and how to classify it.

## Contents

- Classification
- Vitals 1-12
- Cross-Cutting Red Flags

## Classification

| Label | Meaning |
|---|---|
| `Red` | Breach or misuse could cause catastrophic harm, and a required gate is missing or unproven. |
| `Amber` | Sensitive path exists, but controls, tests, rollback, ownership, or audit evidence are incomplete. |
| `Green` | Evidence proves narrow authority, effective controls, tests/verification, and rollback or containment. |
| `Unknown` | Evidence is missing, indirect, stale, or unavailable. Unknown is not safe. |

## Vitals

### 1. Secrets And Control Plane

API keys, OAuth tokens, deploy keys, cloud credentials, signing keys, SSH keys, service accounts, database URLs, encryption keys, wallet mnemonics, private keys, and admin consoles.

Red signals:

- secret committed, logged, pasted into prompt, stored in markdown memory, or exposed to agent-readable traces
- credential can deploy, delete, transfer funds, read all tenants, or access production
- no rotation/revocation path
- cloud IAM, service-account keys, PIM/privileged roles, MDM/MAM policy, or endpoint-management authority can administer identity, wipe devices, read enterprise data, or grant itself broader access

### 2. Identity, Auth, Sessions, Tenancy

Login, session issuance, authorization, RBAC/ABAC, tenant isolation, row-level security, admin impersonation, invite flows, password reset, and API auth.

Red signals:

- endpoints rely only on client-side checks
- tenant IDs are user-controlled without server authorization
- admin tools are reachable without strong gating
- no negative tests proving cross-tenant denial

### 3. PII And Customer Content

Personal data, customer files, uploads, transcripts, prompts, model responses, business strategy, legal/compliance material, ePHI/health records, child data, biometric identifiers, financial records, government/CUI data, and research intent revealed by URLs.

Red signals:

- raw content logged by default
- retention is accidental rather than explicit
- deletion/export path is missing for retained customer data
- analytics or error reporting captures sensitive fields
- sensitive data class is not identified before storage, model processing, logging, or vendor transfer
- biometric or child data is collected without explicit ownership of notice, consent, retention, deletion, and human escalation gates
- object storage, signed URLs, or public buckets expose customer files without tenant ownership checks and access-log evidence
- privacy lifecycle obligations are unowned: lawful basis, purpose limitation, ROPA, DPIA, data subject rights, consent withdrawal, retention schedule, deletion triggers, cross-border transfer basis, subprocessor register, or vendor DPA
- employee monitoring, workplace biometrics, child profiling, or automated decisions affect vulnerable people without documented proportionality, human escalation, and deletion/access paths

### 4. Money, Billing, Trading, Procurement

Payments, refunds, subscription state, invoices, purchasing, bids, contracts, trading, staking, transfers, wallets, broker/exchange APIs, procurement commitments, sanctions exposure, and export-controlled software/technology transfers.

Red signals:

- live money movement without human gate
- agent can read keys and execute transactions
- subscription/quota state trusts redirects rather than provider webhook truth
- cardholder data is stored or processed without explicit PCI scope controls
- sanctions, blocked-person, jurisdiction, or export-control trigger is present but unowned

### 5. Irreversible Mutation

Deletes, overwrites, migrations, destructive jobs, data retention jobs, production writes, and irreversible workflow transitions.

Red signals:

- destructive action lacks backup, confirmation, dry-run, or rollback
- agent can run broad shell/database commands
- migration can run against production without gating

### 6. External Effects

Email, SMS, Slack/Discord, PR merges, releases, package publishing, social posting, customer replies, legal filings, compliance submissions, bids, webhooks, public pages, device commands, safety alarms, industrial/IoT controls, and robot/vehicle/drone actions.

Red signals:

- draft and send are not separated
- no final human approval for high-risk send/publish
- remote state changes are not logged
- physical-world or safety-critical action lacks human approval, fail-safe behavior, or emergency stop

### 7. Agent, Tool, MCP, Browser, Shell Authority

Agent tools, MCP servers, browser automation, local web terminals, schedulers, memory, file writes, shell commands, plugin installation, config mutation, AI code-review tools, PR bots, and security-review agents.

Red signals:

- broad ambient shell/filesystem/network authority
- auto-registered MCP tools or hooks are not reviewed
- tool descriptions are treated as permission controls
- audit logs live inside the agent's write authority
- AI reviewer or analyzer runs project-controlled code/config outside a sandbox
- reviewer worker receives long-lived repo tokens, ambient secrets, or internal-network access
- reviewer can post fixes, commits, approvals, merges, or agent tasks on vital paths without human gate
- source-code indexes, embeddings, logs, or chat traces lack explicit retention/training controls

### 8. Supply Chain, Build, Deploy

Dependencies, lockfiles, CI/CD, artifact signing, package publish, Docker images, infrastructure configuration, model/package sources, and plugin/skill installation.

Red signals:

- unpinned or unreviewed code runs in privileged build/deploy path
- CI token has write/admin permissions beyond need
- package publish/deploy can happen from agent or PR without review
- Kubernetes RBAC, service accounts, clusterrolebindings, pod exec, privileged pods, kubeconfigs, or IaC plans can mutate production or read secrets without least privilege and audit evidence
- AWS/GCP/Azure IAM, service principals, access keys, Entra roles, PIM assignments, MDM/MAM, or endpoint-management policies create standing privilege without activation, approval, MFA, expiry, or review evidence
- IaC/security scanner output is treated as proof without inspecting the actual plan, manifest, CI permission boundary, and deploy authority

### 9. File Ingress And Storage

Uploads, parsers, OCR, PDF/image/video/transcript processing, object storage, path handling, signed URLs, malware scanning, and temp files.

Red signals:

- no size/type/path checks
- user-controlled paths or URLs reach filesystem/internal network
- temp files persist sensitive content
- object storage lacks tenant ownership checks
- signed URLs are long-lived, reusable, guessable, logged, or not tied to tenant/object ownership
- storage access logs are absent for sensitive files, so bulk downloads or public exposure cannot be reconstructed
- mobile apps store tokens, credentials, PII, legal/HR/customer data, or work files in plaintext local storage, backups, unmanaged apps, or personal cloud sync

### 10. Logs, Audit, Traces, Evidence Plane

Application logs, model traces, tool-call logs, audit tables, error reporting, analytics, SIEM, incident records, and raw execution traces.

Red signals:

- agent can modify/delete the logs used to investigate it
- logs contain secrets or raw customer content
- summary-only logs make incident reconstruction impossible
- denied actions are not logged
- ransomware, backup corruption, or destructive recovery can erase the evidence needed to scope the incident
- breach notification, chain-of-custody, and forensic timeline records live in the same mutable plane as the compromised actor
- EDR, endpoint telemetry, DLP screenshots, or sensor logs can be disabled or edited by the actor being investigated

### 11. High-Trust Outputs

Health, legal, financial, compliance, benefits, tax, employment, education, housing, safety-critical operations, and authority-figure advice.

Red signals:

- output can be mistaken for official advice or diagnosis
- no authoritative source corpus
- no refusal/escalation behavior
- no qualified human review for consequential decisions
- automated decision-making, profiling, or AI ranking creates legal, financial, employment, housing, education, health, or similarly significant effects without meaningful human intervention and contestation

### 12. Cost, Availability, Runaway Loops

API spend, model calls, job fanout, queues, schedulers, loops, resource limits, external rate limits, denial-of-wallet, and production availability.

Red signals:

- unbounded loops or retries
- no rate/usage caps
- no kill switch
- background jobs can fan out or spend money without monitoring
- GraphQL depth, query complexity, API enumeration, or rate-limit bypass can exhaust databases, queues, model spend, or provider quota

## Cross-Cutting Red Flags

- no clear owner for a high-risk path
- no rollback path
- no test or deterministic verifier
- no audit trail outside the actor's write authority
- "human in the loop" means rubber-stamp rather than meaningful approval
- model refusal or prompt text is the only control
