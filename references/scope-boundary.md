# Scope Boundary

Use this file before reading broadly. The skill exists to map catastrophic failure paths, not to improve code in general.

## Entry Test

Proceed only when all three can be named:

1. Candidate vital: secrets, PII, auth/tenancy, money, irreversible mutation, external effect, agent authority, supply chain/deploy, file ingress, logs/audit, high-trust output, or runaway cost/availability.
2. Catastrophic failure mode: what breach, misuse, or automation failure would cause severe harm.
3. Evidence gate: what code, config, test, log, policy, runtime behavior, or source receipt would prove the path controlled.

If the entry test fails, say this is not a Grill for Vitals task and route to ordinary code review.

## In Scope

| Area | In scope when |
|---|---|
| Secrets/control plane | A credential can deploy, delete, administer identity, read tenants, sign, or move money. |
| Auth/tenancy | Server-side authorization, tenant isolation, admin boundaries, or session trust is unclear. |
| PII/customer content | Raw prompts, uploads, transcripts, ePHI, child data, biometric data, government/CUI data, health/finance/legal data, URLs, logs, analytics, or retention create breach blast radius. |
| Money/procurement/trading | The system can charge, refund, trade, transfer, stake, bid, buy, or create commitments. |
| Irreversible mutation | Deletes, migrations, overwrites, production jobs, or durable workflow transitions may be hard to undo. |
| External effects | Email, SMS, chat, social posts, PR merges, releases, filings, submissions, bids, webhooks, physical/safety-critical commands, or customer-visible outputs leave the system. |
| Agent/tool authority | MCP, browser, shell, schedulers, hooks, memory, plugins, or skills can read private data, mutate state, spend, send, or install code. |
| Supply chain/deploy | CI/CD, package publish, artifact provenance, privileged build scripts, or dependency execution touches production or trust. |
| AI code-review toolchain | A hosted reviewer, PR bot, scanner, or reviewer plugin ingests repo data, executes analyzers, stores indexes, receives tokens, or can post fixes. |
| File ingress/storage | Uploads, parsers, OCR, object storage, signed URLs, SSRF, paths, or temp files bridge untrusted content to sensitive systems. |
| Logs/audit/evidence | The evidence plane can leak secrets/PII, omit denied actions, or be edited by the actor under review. |
| High-trust outputs | Users may rely on output for health, legal, financial, tax, compliance, housing, employment, safety, or official decisions. |
| Cost/availability | Loops, retries, fanout, queues, model calls, background jobs, or external rate limits can create outage or denial-of-wallet. |

## Out Of Scope

Route these to ordinary code review unless they cross an in-scope vital:

- style, formatting, naming, comments, readability, dead code, or ordinary refactors
- generic maintainability, modularity, abstraction, architecture, or design cleanliness
- generic unit-test coverage, snapshot churn, flaky tests, CI speed, or test organization
- dependency cleanup, package upgrades, linting, static typing, or build warnings without a privileged path
- ordinary performance work without runaway spend, availability, data exposure, or safety impact
- broad "security review" findings that do not connect to a catastrophic vital

## Handoff Rule

If a non-vital issue appears during a Grill run:

```text
Out-of-scope handoff: <issue>
Why not grilled: <no catastrophic vital / no severe blast radius>
Suggested owner: ordinary code review
```

Do not keep chasing the handoff. Return to the highest-risk unresolved vital.

## Overlap Rule

Allowed overlap:

- using NIST, OWASP, CISA, MITRE, or similar sources to choose evidence gates for an activated vital
- naming a non-vital code-quality issue as a handoff
- recommending verification that proves or disproves a catastrophic path

Not allowed:

- general refactoring, cleanup, linting, style, maintainability, or test-coverage advice
- broad "secure coding" checklists disconnected from a named vital
- turning the report into a bug list after the Vitals Map is clear
- using CodeRabbit, Greptile, SAST, or scanner output as proof instead of as leads
- running a cleanup or refactor workflow unless the user separately asks for implementation or cleanup

## Boundary Examples

| Finding | Grill? | Why |
|---|---|---|
| Missing route authorization on `/admin/refunds` | Yes | Auth plus money creates catastrophic misuse. |
| Button label is unclear | No | Usability or ordinary review unless it causes a high-trust or destructive-action mistake. |
| Unpinned dependency in a dev-only formatter | No | Ordinary review unless it runs with privileged CI/deploy credentials. |
| Unpinned GitHub Action with write token | Yes | Supply chain plus control-plane authority. |
| No test for a pure date helper | No | Ordinary test review. |
| No negative cross-tenant access test | Yes | Tenant isolation is a vital evidence gate. |
| Slow endpoint | Usually no | Grill only if it can trigger outage, cost runaway, or rate-limit cascade. |
| Logs include raw prompts and uploaded files | Yes | PII/customer content plus evidence-plane leakage. |
| Agent can unlock doors or stop lab equipment | Yes | External effect plus safety-critical action requires hard gates and fail-safe proof. |
| Sensor dashboard has messy CSS | No | Product polish unless it can cause high-trust or safety-critical operator error. |

## Stop Rule

Stop the Grill run when the Vitals Map, statuses, hard stops, unknowns, evidence, and next verification steps are clear. Do not continue into general bug hunting or cleanup.
