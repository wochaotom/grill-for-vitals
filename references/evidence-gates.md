# Evidence Gates

Use this file to decide what proof is required before marking a vital `Green`.

## Contents

- General Proof Standard
- Evidence gates by vital
- Green Classification Checklist

## General Proof Standard

Good evidence:

- source code or config read in this run
- tests that exercise the specific risk
- runtime behavior observed in this run
- provider/dashboard configuration when available
- architecture docs that match the code
- logs or traces outside the actor's write authority

Weak evidence:

- comments without enforcement
- README claims without code/config
- "we plan to"
- prompt instructions without tool/runtime enforcement
- a passing test suite that does not cover the risk
- a graph or retrieval summary without direct note reads

## Secrets And Credentials

Require:

- no committed secret files or hardcoded credentials
- secrets loaded from environment, platform secret store, vault, or connector credential system
- logs/traces/screenshots/prompts do not include secrets
- rotation and revocation path exists for high-impact credentials
- CI/CD permissions are scoped

Useful checks:

- search file names: `.env`, `.npmrc`, `.pypirc`, `.netrc`, `id_rsa`, `pem`, `key`, `secret`, `token`, `mnemonic`, `kubeconfig`, `service-account`, `credentials`
- inspect examples without printing real secret values
- inspect logging middleware and error reporting capture settings
- inspect CI workflow permissions and secret usage

## Auth, Authorization, Tenancy

Require:

- server-side authorization for every customer-data endpoint
- tenant ownership checks near data access
- admin routes gated separately
- negative tests for cross-tenant read/write denial
- object-level and function-level authorization tests for API, REST, and GraphQL paths that accept object IDs, tenant IDs, or admin actions
- session/cookie settings are appropriate for the framework
- for high-risk identity paths, identity proofing, authentication, federation, account recovery, and authenticator lifecycle are explicitly scoped

Not enough:

- UI hides buttons
- route names imply protection
- database includes `tenant_id` but no enforcement

## PII, Customer Content, Retention

Require:

- data inventory by class
- explicit flags for regulated or high-risk data classes such as ePHI, child data, biometric information, financial records, legal records, and government/CUI data
- explicit retention defaults
- logs allowlist rather than log-everything-redact-later
- deletion/export behavior for retained customer content
- temp files, caches, analytics, and error reporters checked
- model provider boundary documented for customer content
- object storage evidence for sensitive files: bucket/container policy, public-access controls, ACLs, signed URL lifetime/scope, tenant ownership checks, and access logs such as CloudTrail Data Events or provider equivalents
- lifecycle evidence when privacy obligations surface: lawful basis, purpose, ROPA or processing inventory, DPIA trigger decision, data subject access/deletion/export flow, consent withdrawal propagation, retention schedule, deletion trigger, vendor DPA/subprocessor register, and cross-border transfer basis where applicable
- employee, child, biometric, or automated-decision flows include proportionality, notice/consent where applicable, less-intrusive alternatives, human escalation, and contestation or deletion/access paths
- mobile or BYOD evidence when enterprise/customer data appears: local storage encryption, keychain/keystore settings, backup exclusion, app sandbox boundaries, managed/unmanaged app data-transfer rules, selective wipe behavior, and offline access limits

Strong posture:

```text
store account/subscription/usage metadata
process customer content for the current job
return output
discard raw prompts/responses/uploads unless retention is a named feature
```

## Payments And Billing

Require:

- hosted checkout or payment-provider boundary unless PCI scope is explicitly owned
- subscription/quota state derived from webhook truth
- webhook signature verification
- idempotency handling for payment events
- test and production credentials separated
- no cardholder data stored unless PCI DSS scope and controls are explicit

Not enough:

- checkout success redirect alone
- client-side plan update
- logs that include payment secrets or raw provider payloads unnecessarily

## Wallets, Trading, Capital, Procurement

Require:

- paper/read-only mode by default
- private keys, mnemonics, broker write keys, and signing material outside agent workspace
- agent cannot edit risk limits, signing policy, or kill switch
- human approval for live trades, transfers, bids, purchases, or commitments
- immutable or external audit log for proposals and executions
- execution stops if logs, risk checks, or data feeds fail
- sanctions, blocked-person, jurisdiction, and export-control questions are identified when money, virtual currency, cross-border services, or controlled technology are involved

Hard stop:

```text
agent can read mnemonic/private key + run execution command
```

## Agent Tools, MCP, Browser, Shell

Require:

- smallest useful tool set
- action classes: read, draft, write local, write remote, spend/commit, send/publish, delete/overwrite
- explicit gates for high-risk action classes
- tool registry or manifest with owner, permission, and risk metadata
- shell/network/filesystem scope documented and enforced
- audit logs outside the agent's write authority
- for AI code-review tools: repo data ingestion, cache/embedding/log retention, model-provider boundary, and training settings documented
- for AI code-review tools: related-repo context, include/exclude paths, skip-review settings, strictness, and file limits prove vital paths are not silently skipped
- for analyzer execution: sandbox proof, internal-network blocking, no ambient secrets, and short-lived scoped tokens
- for Kubernetes or IaC-controlled systems: reviewed plan/manifest, cluster/RBAC/service-account scope, pod exec/attach restrictions, secret read permissions, CI identity, scanner findings tied to the exact artifact, and audit logs outside the deploy actor
- for cloud identity and endpoint/mobile management: IAM policy and role graph, dangerous permission combinations, service-account key inventory, PIM activation/approval/MFA/expiry settings, MDM/MAM policy scope, selective-wipe approval, and privileged-role access reviews

Not enough:

- tool description says "read-only" but handler can mutate
- MCP server is installed because it is convenient
- terminal panes are assumed safe while hooks/tools mutate config
- vendor says "secure" or "sandboxed" without configuration, architecture, audit, or contractual evidence

## External Sends, Publications, And Physical Actions

Require:

- draft and send separated
- final human approval for customer/legal/compliance/reputation-sensitive outputs
- destination, payload, timestamp, actor, source basis logged
- rollback or correction path documented when possible
- for physical or safety-critical actions, target state, operator approval, fail-safe behavior, emergency stop, and incident rollback/containment are documented and tested

## Irreversible Mutation

Require:

- dry-run or preview
- backup/snapshot where applicable
- confirmation gate
- scoped target
- rollback or compensation plan
- tests or rehearsals for migrations/destructive jobs
- for ransomware or recovery paths, offline/immutable backup posture, restore-test evidence, backup integrity/hash verification, RTO/RPO reality, and a recovery path that preserves incident evidence

## Logs And Audit

Require:

- logs do not contain secrets/raw sensitive content
- denied actions are logged
- high-risk tool calls include input summary, actor, approval, result, and timestamp
- audit storage is outside the actor's write authority
- enough raw detail exists for incident reconstruction
- forensic or breach records preserve acquisition time, evidence hash or integrity marker, chain of custody, and actor identity
- breach notification timing can be reconstructed from logs outside the compromised actor's write authority
- honeytokens, canaries, and document beacons are treated as detection evidence only; they do not prove prevention or compliance
- endpoint evidence includes EDR/sensor health, tamper resistance, endpoint telemetry retention, DLP capture scope, and proof that local admins or compromised tools cannot erase the investigation trail

Avoid:

- only storing LLM summaries of incidents
- letting the agent edit the investigation record

## High-Trust Outputs

Require:

- current official domain source corpus named; generic web results, vendor writing, vault graph output, or model memory are not enough
- source ingestion, corpus updates, provenance, and freshness are logged or reviewable
- citation/source-set logging for consequential claims
- refusal and escalation behavior tested
- tests cover unsupported claims, stale sources, source poisoning, and citation/source mismatch
- qualified human review for official decisions
- UI/output language separates draft guidance from official advice
- for automated decisions or profiling with significant effects, proof that human intervention is meaningful: reviewer authority, competence, context, time, override ability, contestation path, and records showing the review is not rubber-stamping
- for LLM privacy output risk, training/output PII controls, extraction/prompt-injection tests, output scanning or review gates, and incident handling for memorized or hallucinated personal data

For financial, tax, legal, medical, benefits, hiring, housing, safety, or official-policy advice, activate or browse the domain authority during the run and record the checked date. Do not mark `Green` from generic AI safety sources alone.

## Cost And Availability

Require:

- rate limits
- usage caps
- retry bounds
- queue/fanout limits
- timeout and cancellation
- monitoring and owner for runaway spend or outage
- GraphQL depth and query-complexity limits, pagination bounds, API enumeration detection, and rate-limit bypass tests when those surfaces exist

## Green Classification Checklist

Only classify `Green` when all are true:

1. The vital exists or is explicitly absent.
2. Evidence was inspected in this run.
3. Controls are enforced below prompt text.
4. A verifier/test/log proves the control or the risk is demonstrably absent.
5. Rollback, revocation, shutdown, or containment exists where relevant.
