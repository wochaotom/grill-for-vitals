# Grill For Vitals

> Find the part of the system where a bug becomes a catastrophe.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skill](https://img.shields.io/badge/skill-grill--for--vitals-blue)](SKILL.md)

Grill For Vitals is a review skill for high-risk engineering work. It is not a generic security checklist, a compliance certification, or a replacement for code hygiene.

It exists for the moments where the question is sharper:

```text
If this code path is breached, misused, or automated badly, what is the immediate catastrophe?
```

Use it before design, launch, security review, or agent automation when the system touches secrets, PII, auth and tenancy, money, irreversible writes, external actions, agent tools, privileged deploy, logs and audit evidence, high-trust outputs, or runaway cost.

## Install

If your tool supports skills.sh-compatible GitHub installs:

```bash
npx skills add wochaotom/grill-for-vitals
```

For manual installs, place this folder in your tool's local skills directory. Then invoke `grill-for-vitals` when a catastrophic vital may be involved.

## Quickstart

Good prompts:

```text
Grill this Stripe webhook and subscription quota flow before launch.
```

```text
Map the catastrophic vitals for our PR bot. It runs Semgrep and posts one-click fixes.
```

```text
Which sources should we use for uploaded patient PDFs summarized by an LLM?
```

```text
Our Kubernetes service account can pod exec and read secrets. Grill the control-plane risk.
```

Bad prompt for this skill:

```text
Review this helper for naming, readability, and tests.
```

That belongs in ordinary code review or a code-hygiene skill unless a catastrophic vital is implicated.

## What It Covers

| Vital | Catastrophe it is looking for |
|---|---|
| Secrets and control plane | A leaked key becomes production, tenant, identity, deploy, or money authority. |
| Identity, auth, sessions, tenancy | One user or tenant can become another, or admin boundaries fail. |
| PII and customer content | Customer data, prompts, files, logs, uploads, or privacy lifecycle obligations become breach blast radius. |
| Money and regulated financial paths | Payments, refunds, trades, payouts, procurement, sanctions, or export triggers move beyond control. |
| Irreversible mutation | Deletes, migrations, retention jobs, or recovery actions cannot be rolled back. |
| External effects | Emails, filings, releases, webhooks, posts, bids, or physical actions escape a human gate. |
| Agent/tool authority | MCP, browser, shell, PR bots, analyzers, schedulers, and skills get too much ambient power. |
| Supply chain/build/deploy | CI/CD, packages, IaC, Kubernetes, cloud IAM, or release flows become privileged attack paths. |
| File ingress/storage | Uploads, parsers, signed URLs, object storage, mobile storage, or temp files bridge into sensitive systems. |
| Logs/audit/evidence | The actor can rewrite the evidence needed to investigate it. |
| High-trust outputs | AI output looks like medical, legal, tax, benefits, employment, housing, financial, safety, or official advice. |
| Cost/availability | Loops, retries, GraphQL depth, queue fanout, or model calls burn money or take production down. |

## How It Works

Grill For Vitals runs a narrow loop:

1. Scope gate: identify the candidate vital and catastrophic failure mode.
2. Local sweep: inspect code, docs, configs, tests, logs, and project rules before asking.
3. Source routing: use `scripts/source_activation_plan.py --surface "<surface>"` to activate only the relevant source family.
4. Evidence gate: classify each vital as `Red`, `Amber`, `Green`, or `Unknown`.
5. One question: ask the next highest-leverage unresolved question with a recommended answer and evidence needed.
6. Report: separate evidence from inference, list hard stops, unknowns, sources used, and code-hygiene handoffs.

It is intentionally conditional. It should not scan every security, privacy, AI, or compliance source for every task.

## Source Routing

The router maps observed surfaces to small source presets:

```bash
python scripts/source_activation_plan.py --surface "BOLA API exposes another tenant invoice"
```

Example output includes inferred presets such as:

```text
identity-auth
privacy-customer-content
```

The skill then uses those presets to choose evidence gates and source families. Vendor and practitioner material can provide leads, but official or standards sources outrank it for high-stakes claims.

## Validation

The repo includes deterministic checks for drift:

```bash
python quick_validate.py
python scripts/validate_grill_skill.py .
python scripts/source_activation_plan.py --self-test
python scripts/calibrate_source_taxonomy.py
python scripts/check_source_links.py
python scripts/check_code_hygiene_overlap.py
python scripts/validator_smoke_tests.py
```

Behavior-changing revisions use matched baseline and candidate transcripts rather than static checks alone. Follow `references/behavioral-evaluation-protocol.md`, then evaluate the reviewed JSONL receipts:

```bash
python scripts/evaluate_behavioral_runs.py --results path/to/results.jsonl
```

A promotion result requires every current public pressure case, at least three fresh repetitions per case and variant, matching runtime configuration, independent review, zero hard failures, and no per-check regression. The evaluator compares receipts; it does not run or judge the agent.

Current calibration covers 238 routing and regression cases, including:

- ransomware and restore-test failure
- public object storage and signed URL exposure
- Kubernetes RBAC and service account risk
- IaC scanner evidence handling
- BOLA, IDOR, GraphQL query complexity, and rate-limit bypass
- cloud IAM, Entra PIM, MDM/MAM, mobile local storage, and EDR evidence
- DSAR, DPIA, ROPA, retention, consent withdrawal, cross-border transfer, breach notification, vendor/subprocessor, child, employee, biometric, and AI privacy governance
- docs-only and mock-data suppression cases

## Repository Structure

```text
grill-for-vitals/
|-- SKILL.md
|-- agents/
|   `-- openai.yaml
|-- references/
|   |-- catastrophe-taxonomy.md
|   |-- evidence-gates.md
|   |-- question-bank.md
|   |-- source-trigger-taxonomy.md
|   |-- source-registry.md
|   |-- source-weights.json
|   |-- pressure-scenarios.md
|   `-- ...
`-- scripts/
    |-- source_activation_plan.py
    |-- calibrate_source_taxonomy.py
    |-- validate_grill_skill.py
    `-- ...
```

`SKILL.md` is the runtime skill. `references/` holds drill-down material loaded only when needed. `scripts/` keeps routing, validation, source checks, and smoke tests deterministic.

How to read this layout:

| Path | Purpose |
|---|---|
| `SKILL.md` | The runtime instruction file an agent loads after the skill triggers. Keep this concise and procedural. |
| `agents/openai.yaml` | UI metadata for skill lists and default prompts. It does not define the review logic. |
| `references/catastrophe-taxonomy.md` | The twelve catastrophic vitals and what counts as an immediate high-risk failure mode. |
| `references/evidence-gates.md` | The proof standard for `Red`, `Amber`, `Green`, and `Unknown` findings. |
| `references/question-bank.md` | High-leverage grilling questions, recommended answers, and required evidence by vital. |
| `references/source-trigger-taxonomy.md` | Routing triggers and suppressions so the skill activates the right source family instead of checking everything. |
| `references/source-registry.md` | Source catalog with authority tiers, freshness expectations, and links. |
| `references/source-weights.json` | Machine-readable source weights used by the routing and calibration scripts. |
| `references/pressure-scenarios.md` | Realistic prompts used to test whether the skill catches catastrophic paths and avoids overreach. |
| `references/behavioral-evaluation-protocol.md` | Baseline/candidate transcript, review, and promotion contract for behavior-changing revisions. |
| `quick_validate.py` | Fast local validation wrapper for the core structural, routing, calibration, and link-integrity checks. |
| `scripts/source_activation_plan.py` | CLI router that maps an observed surface to source presets and questions. |
| `scripts/calibrate_source_taxonomy.py` | Regression suite for routing misses, ambiguity failures, and over-claim risks. |
| `scripts/evaluate_behavioral_runs.py` | Validates matched behavior receipts and blocks incomplete, drifted, self-reviewed, or regressed promotion sets. |
| `scripts/validate_grill_skill.py` | Structural validator for source IDs, references, required files, and scope boundaries. |

The repo is split this way so agents can start from the small runtime skill, then pull only the reference or script needed for the risk surface in front of them.

## What This Is Not

Grill For Vitals does not:

- certify SOC 2, HIPAA, PCI DSS, FedRAMP, CMMC, legal, medical, financial, tax, or safety compliance
- replace a security audit, privacy counsel, incident-response firm, or qualified domain expert
- perform generic hardening, refactoring, formatting, or test cleanup
- mark missing evidence safe
- treat vendor scanner output as proof by itself

If no catastrophic vital is present, the correct move is to stop and hand off to ordinary review or code hygiene.

## License

MIT. Use it, fork it, adapt it, and ship your own version. No warranty; do not use this skill as a compliance or safety certification.
