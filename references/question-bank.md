# Question Bank

Ask one question at a time. Prefer the highest-risk unresolved `Red` or `Unknown`.

## Contents

- Scope Gate
- Secrets And Control Plane
- Auth, Sessions, Tenancy
- PII And Customer Content
- Money, Payments, Trading, Procurement
- Irreversible Mutation
- External Actions
- Agent Tools And MCP
- Supply Chain And Deploy
- File Ingress
- Logs And Incident Evidence
- High-Trust Outputs
- Cost And Availability

Use this shape:

```text
Question: <one concrete decision>
Recommended answer: <recommended position>
Evidence needed: <what would prove it>
Why this matters: <catastrophic failure mode>
```

## Scope Gate

Question: Which catastrophic vital is actually implicated here?
Recommended answer: Continue only if the task touches a vital such as secrets, PII, auth/tenancy, money, irreversible mutation, external effects, agent authority, privileged deploy, file ingress, logs/audit, high-trust outputs, or runaway cost.
Evidence needed: A named vital, catastrophic failure mode, and evidence gate.
Why this matters: Without this gate, the skill drifts into generic code review and duplicates code hygiene.

## Secrets And Control Plane

Question: What secrets can this system read, and where is proof they never enter prompts, logs, screenshots, traces, or repo files?
Recommended answer: Secrets should live only in the platform secret store, environment, vault, or connector credential system.
Evidence needed: Secret scan, env loading code, logging config, CI secret usage, and no committed secret material.
Why this matters: A single leaked control-plane key can become production, tenant, or financial compromise.

Question: Which credential has the largest blast radius?
Recommended answer: Identify and isolate the credential that can deploy, delete, read all tenants, transfer funds, sign artifacts, publish releases, or administer identity; use `control-plane-supply-chain` for privileged deploy/signing/release paths.
Evidence needed: Credential inventory and permissions from code/config/provider docs.
Why this matters: Vitals work starts with the key that turns a bug into catastrophe.

## Auth, Sessions, Tenancy

Question: Which endpoint proves user A cannot read or mutate user B's records?
Recommended answer: There should be a negative test or route-level authorization proof for every customer-data boundary.
Evidence needed: Endpoint code, data-access layer, RLS policy, and cross-tenant denial tests.
Why this matters: Tenant isolation failure is usually catastrophic even if the app "has auth."

Question: What makes an admin action admin-only?
Recommended answer: Admin authorization should be server-enforced and separately tested.
Evidence needed: Middleware/guard code, admin role source, tests, and audit logs.
Why this matters: Admin UI hiding is not an authorization boundary.

Question: Does any login, recovery, identity proofing, or federation path unlock money, regulated data, admin access, or production authority?
Recommended answer: High-risk identity paths need explicit assurance level, recovery controls, authenticator lifecycle rules, and negative tests.
Evidence needed: Auth architecture, identity provider settings, recovery flow, MFA/passkey policy, session/federation config, and tests.
Why this matters: Account recovery and federation mistakes often bypass otherwise strong authorization.

Question: Which object-level authorization test proves one tenant cannot read or mutate another tenant's object?
Recommended answer: API and GraphQL paths should deny cross-tenant object IDs and function-level escalation in server-side tests.
Evidence needed: Route/resolver code, ownership checks near data access, negative BOLA/IDOR/BFLA tests, and audit logs for denied attempts.
Why this matters: BOLA and IDOR turn ordinary object IDs into customer-data breach paths.

## PII And Customer Content

Question: If breached tomorrow, what customer-sensitive content would attackers actually get?
Recommended answer: As little as the product can honestly support; raw content should be discarded unless retention is a named feature.
Evidence needed: Data inventory, schemas, storage buckets, logs, analytics, error reporting, retention/deletion docs.
Why this matters: Data minimization shrinks blast radius more reliably than promises.

Question: Are raw prompts, model responses, uploads, transcripts, URLs, or files logged anywhere?
Recommended answer: Logs should be allowlisted and exclude raw customer content by default.
Evidence needed: Logging middleware, model-call wrappers, error reporting config, analytics capture settings.
Why this matters: "We do not store it" is false if logs, traces, or temp files keep it.

Question: Does this system collect ePHI, child data, biometric information, financial records, legal records, or government/CUI data?
Recommended answer: Classify the data before design or launch and activate the relevant authority source only for the matching class.
Evidence needed: Data inventory, product audience, schemas, uploads, vendor processors, retention policy, consent/notice flows, and deletion/export behavior.
Why this matters: Regulated or uniquely sensitive data changes the blast radius and the evidence gates.

Question: Which bucket, container, signed URL, or object key path would expose customer files if misconfigured?
Recommended answer: Sensitive object storage should have public access blocked, short-lived scoped signed URLs, tenant ownership checks, and access logs.
Evidence needed: Bucket/container policy, ACL/public-access settings, signed URL generation code, object ownership checks, and provider object-access logs.
Why this matters: A public bucket or reusable signed URL can bypass app authorization and leak retained customer content at scale.

Question: Which privacy lifecycle obligation is actually implicated: access/export, deletion, retention, consent withdrawal, DPIA, ROPA, cross-border transfer, or processor/subprocessor control?
Recommended answer: Route to `privacy-customer-content` only for the matching lifecycle surface, then ask for the narrow artifact that proves it.
Evidence needed: Processing inventory, purpose/lawful-basis record, DPIA decision, rights workflow, retention schedule, DPA/subprocessor register, transfer basis, or deletion evidence.
Why this matters: Privacy failures become catastrophic when data cannot be found, limited, deleted, explained, or controlled after a breach.

## Money, Payments, Trading, Procurement

Question: Can this system charge, refund, trade, stake, transfer, bid, purchase, or commit money without a human gate?
Recommended answer: Live money movement and commitments need explicit human approval and hard limits.
Evidence needed: Payment/trading/procurement code, provider permissions, approval flow, audit log.
Why this matters: Money actions are catastrophic when automated beyond the operator's intent.

Question: Is subscription or quota state derived from webhook truth?
Recommended answer: Use signed provider webhooks as source of truth, not only checkout redirects.
Evidence needed: Webhook handler, signature verification, idempotency, tests.
Why this matters: Billing state drift creates revenue, access, and abuse failures.

Question: Can an agent read private keys or mnemonics and run execution scripts?
Recommended answer: No. Signing material must stay outside the agent workspace and execution must pass through a separate signer/human gate.
Evidence needed: File/env access boundary, wallet/broker permissions, signing architecture, audit log.
Why this matters: Agent plus keys plus execution is agent custody.

Question: Does this money, virtual-currency, procurement, export, or cross-border workflow need sanctions or export-control screening?
Recommended answer: Identify the trigger and route legal/compliance conclusions to qualified review; the skill can only flag the need for evidence.
Evidence needed: Jurisdictions, counterparties, user screening, product/export classification, payment rails, blocked-person checks, and compliance ownership.
Why this matters: The catastrophic path may be an illegal transaction or controlled technology transfer, not just a software bug.

## Irreversible Mutation

Question: What action here cannot be undone cleanly?
Recommended answer: Every destructive action should have preview, scope, confirmation, backup, and rollback or compensation.
Evidence needed: Delete/migration/job code, backup path, tests, runbook.
Why this matters: A bug becomes an incident when rollback is absent.

## External Actions

Question: What can be sent, published, filed, submitted, posted, pushed, merged, released, or physically actuated in a safety-critical setting?
Recommended answer: Draft and final external action should be separate, with human approval for high-risk outputs or actions.
Evidence needed: Send/publish/merge/deploy/actuator code, approval workflow, audit trail, safety stop or rollback path.
Why this matters: External state changes cause reputation, legal, customer, and operational harm.

Question: Is any external action an OT, industrial-control, IoT/physical-control, or safety-critical actuation path?
Recommended answer: Use `safety-ot` when software can change physical state or safety-critical operations, and require a human operator gate plus fail-safe and emergency-stop proof.
Evidence needed: Actuator/tool code, device scope, operator approval flow, fail-safe design, emergency stop, monitoring, and incident containment test.
Why this matters: A software or agent mistake can become physical harm when the system can control devices, doors, alarms, equipment, or operational processes.

## Agent Tools And MCP

Question: What is the smallest toolset needed for this workflow?
Recommended answer: Start read-only, add write authority only when the success condition, data boundary, write scope, and verifier are explicit.
Evidence needed: Tool registry/config, allowed tools, permissions, logs, approval gates.
Why this matters: Tool sprawl creates ambient authority.

Question: Which tools are write-capable, network-capable, shell-capable, browser-capable, or config-mutating?
Recommended answer: High-risk tool classes need separate gates and audit logs.
Evidence needed: MCP configs, hook configs, CLI/tool manifests, handler code.
Why this matters: A neutral-looking terminal or MCP can silently expand agent authority.

Question: Can the agent modify the audit trail used to investigate it?
Recommended answer: No. Monitoring and audit logs should live outside the agent's write authority.
Evidence needed: Log storage, write permissions, tool scopes.
Why this matters: An incident is harder to contain when the actor controls the evidence plane.

Question: Does any AI code-review tool, PR bot, or security-review agent ingest the repository, execute analyzers, or post fixes?
Recommended answer: Treat it as a privileged toolchain component with source-code, token, sandbox, retention, and mutation gates.
Evidence needed: Tool permissions, app installation scope, analyzer list, sandbox proof, token lifetime/scope, cache/embedding/log retention, training settings, branch protection, and audit logs.
Why this matters: A malicious PR or analyzer config can turn a reviewer into a source-code exfiltration, credential, or control-plane path.

## Supply Chain And Deploy

Question: What code can run in CI/CD or deployment with privileged credentials?
Recommended answer: Privileged CI/CD should use least privilege, pinned dependencies, reviewed workflows, and scoped secrets.
Evidence needed: CI workflows, action permissions, package scripts, deploy config.
Why this matters: Build and deploy pipelines are control-plane paths.

Question: What Kubernetes or IaC path can mutate production or read secrets?
Recommended answer: Use `control-plane-supply-chain` when manifests, Terraform plans, cluster RBAC, service accounts, pod exec, or scanner findings touch deploy authority.
Evidence needed: Terraform plan/tfplan, Kubernetes manifests, RBAC bindings, service account permissions, scanner output tied to the exact artifact, CI identity, and audit logs.
Why this matters: IaC and cluster permissions are production control-plane code, not just configuration.

Question: Which cloud IAM, PIM, service principal, or endpoint/mobile-management role can grant itself more authority?
Recommended answer: Use `control-plane-supply-chain` for AWS/GCP/Azure IAM, Entra privileged roles, service-account keys, MDM/MAM, and selective wipe when they touch production, identity, enterprise data, or device control.
Evidence needed: IAM policy graph, role assignments, dangerous permission combinations, service-account key inventory, PIM activation settings, access reviews, MDM/MAM policy scope, and audit logs.
Why this matters: A cloud or device-management role is a control plane when it can become admin, read enterprise data, or erase devices.

## File Ingress

Question: What can users upload or cause the system to fetch?
Recommended answer: Validate size, type, path, tenant ownership, parser behavior, and network access.
Evidence needed: Upload handlers, storage config, signed URL policy, parser sandbox, SSRF controls.
Why this matters: File and URL ingress often bridges untrusted input to filesystem, network, or parser bugs.

Question: What sensitive data survives on mobile devices, unmanaged apps, or backups?
Recommended answer: Keep tokens, customer data, HR/legal records, and work files out of plaintext local storage, personal backups, and unmanaged app transfer paths.
Evidence needed: Mobile storage code, keychain/keystore configuration, backup exclusion, managed/unmanaged app transfer rules, offline cache policy, selective wipe test, and device binding.
Why this matters: Mobile storage and BYOD paths can bypass server-side controls after the data leaves the service.

## Logs And Incident Evidence

Question: Can ransomware, restore tooling, or a compromised actor destroy the evidence needed to scope the incident?
Recommended answer: Use `incident-recovery` and keep audit, forensic, backup-integrity, and breach-notification evidence outside the compromised actor's write authority.
Evidence needed: Immutable/external logs, chain-of-custody record, backup integrity/hash checks, restore-test record, breach timeline, and access controls for incident records.
Why this matters: A breach becomes much worse when recovery also erases proof of what happened.

Question: Are honeytokens, canaries, or document beacons proving prevention, or only detection?
Recommended answer: Treat deception signals as detection leads only; they still need containment, evidence preservation, and source-of-truth logs.
Evidence needed: Alert routing, canary placement, trigger logs, response runbook, and proof that the actor cannot suppress the alert.
Why this matters: A triggered honeytoken can reveal compromise, but it does not prove the vital was controlled.

Question: Can local admins, compromised tools, or endpoint agents disable or rewrite endpoint evidence?
Recommended answer: Keep EDR, endpoint telemetry, DLP captures, and sensor-health evidence outside the local actor's control wherever the endpoint is part of incident reconstruction.
Evidence needed: EDR policy, tamper protection, sensor-health logs, telemetry retention, DLP capture scope, local admin permissions, and SIEM forwarding proof.
Why this matters: Endpoint evidence is weak if the compromised endpoint can erase the trail before responders see it.

## High-Trust Outputs

Question: Could a user reasonably treat this as medical, legal, financial, compliance, hiring, housing, safety, or official policy advice?
Recommended answer: Use `high-trust-output` for AI output risk, then add current official domain authorities; generic AI sources are not enough for tax, medical, legal, financial, or safety advice.
Evidence needed: Product copy, prompts, retrieval/source-ingestion path, official source set with checked date, citation/source logging, output policy, evals, escalation path.
Why this matters: The harm comes from authority, not only from model accuracy.

Question: Does automated decision-making or profiling create legal, financial, employment, housing, education, health, or similarly significant effects?
Recommended answer: Require meaningful human intervention, contestation, source logging, and evidence that review is not rubber-stamping.
Evidence needed: Decision flow, reviewer authority, review time/context, override logs, appeal workflow, explanation record, and tests for unsupported decisions.
Why this matters: A model ranking or decision can become catastrophic when it denies access to consequential services without a real human gate.

## Cost And Availability

Question: What prevents loops, fanout, API cost spikes, queue floods, or resource exhaustion?
Recommended answer: Bound retries, rate limits, timeouts, usage caps, and kill switches.
Evidence needed: Job config, queue limits, model-call wrapper, billing/usage monitors.
Why this matters: Unbounded automation can become denial-of-wallet or outage.

Question: What bounds GraphQL depth, query complexity, API enumeration, and rate-limit bypass?
Recommended answer: Treat these as `cost-availability` when they can exhaust databases, model calls, provider quota, or production capacity.
Evidence needed: Query complexity/depth config, pagination limits, rate-limit bypass tests, monitoring, and abuse detection.
Why this matters: A read-only API path can still take production down or create a large cloud bill.
