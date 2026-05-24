---
name: grill-for-vitals
description: "Use when an agent must map catastrophic high-risk system surfaces before design, implementation, launch, security review, or automation: secrets/control plane, PII, auth/tenancy, money/payments/trading/procurement, irreversible writes, external sends/physical actions, agent tools/MCP/browser/shell, CI/CD, logs/audit, high-trust outputs, or runaway cost. Do not use for ordinary code review, refactors, style, tests, maintainability or generic hardening unless a catastrophic vital is implicated."
---

# Grill For Vitals

Use this skill to find the parts of a system where compromise, misuse, or bad automation would be catastrophic. This is not a generic security checklist and not a compliance certification. It is a catastrophe-mapping interview backed by code evidence.

## Core Rules

1. Run the scope gate first. If no catastrophic vital is implicated, stop and route the task to ordinary review or `code-hygiene-compounder`.
2. Inspect code, docs, configs, and existing project rules before asking the user.
3. If the answer can be discovered locally, discover it instead of asking.
4. Classify each vital as `Red`, `Amber`, `Green`, or `Unknown`; never downgrade missing evidence to safe.
5. Ask one question at a time when evidence is missing or a tradeoff needs a human decision.
6. For every question, provide your recommended answer and the evidence that would prove it.
7. Separate evidence from inference. Say plainly when a claim is inferred.
8. Use authoritative sources only for activated vitals; do not load broad code-quality sources here.
9. Do not claim compliance, readiness, or safety unless the required evidence was inspected in this run.

## Reference Loading

Load only the references needed for the current task:

- `references/catastrophe-taxonomy.md`: vital categories and Red/Amber/Green/Unknown rules.
- `references/evidence-gates.md`: what proof is required for each high-risk area.
- `references/vital-principles.md`: distilled source-backed principles for everyday Grill runs.
- `references/scope-boundary.md`: scope gate, code-hygiene handoff rules, and examples.
- `references/question-bank.md`: one-at-a-time grill questions by vital.
- `references/anti-overexpansion-query-protocol.md`: how to use `aquery` and `bquery` without graph or retrieval overflow becoming fake authority.
- `references/source-trigger-taxonomy.md`: surface-signal taxonomy for choosing presets before reading the wider source registry.
- `references/source-registry.md`: authoritative source tiers, freshness rules, and conditional source activation.
- `references/source-weights.json`: source activation weights for high-risk domains.
- `references/vitals-source-matrix.md`: vital-to-source-preset and evidence-gate map.
- `references/vendor-ai-reviewer-patterns.md`: Greptile/CodeRabbit-inspired AI code-review security patterns; use as vendor/practitioner input only.
- `references/pressure-scenarios.md`: validation prompts for skill iteration; do not load during normal Grill runs.
- `references/source-map.md`: local-vault and historical lineage, not the active source registry.
- `references/report-template.md`: output shape for Vitals reports.

When multiple sources may apply, run `scripts/source_activation_plan.py --surface "<observed problem surface>"` or inspect `source-trigger-taxonomy.md`, then choose a matching preset such as `identity-auth`, `control-plane-supply-chain`, `privacy-customer-content`, `financial-customer-data`, `ai-review-toolchain`, `high-trust-output`, `agentic-llm`, `health-ephi`, `child-privacy`, `biometric-identity`, `child-biometric`, `payments-cardholder`, `sanctions-export`, `customer-trust-soc2`, `incident-recovery`, `safety-ot`, `cost-availability`, `payments-sanctions-export`, or `federal-defense`; do not load broad source packs by default.

## Workflow

### 0. Scope Gate

Before reviewing broadly, identify at least one candidate vital, its catastrophic failure mode, and the evidence gate that would prove it controlled. Use `scope-boundary.md`.

Out of scope examples:

- style, naming, readability, formatting, dependency cleanup, or ordinary test coverage
- generic "make this safer" work with no vital surface
- performance or architecture issues unless they create runaway cost, outage, data exposure, or irreversible mutation

If a generic hygiene issue appears while mapping a vital, record it as a handoff and return to the vital.

### 1. Context Sweep

Start with a local sweep. Prefer `rg --files` and targeted `rg` searches. Check, when present:

- project rules: `AGENTS.md`, `CLAUDE.md`, `CONTEXT.md`, `docs/adr/`
- env and secret surfaces: `.env*`, `.npmrc`, `.pypirc`, `.netrc`, kubeconfig, service-account files, secret examples, CI secrets references
- auth and tenancy: middleware, route guards, RLS policies, session handling
- data and storage: schemas, uploads, buckets, retention, deletion/export paths
- money: billing, Stripe or payment providers, wallet/trading/bid/procurement code
- irreversible actions: deletes, migrations, overwrites, production jobs
- external actions: email, chat, webhooks, publishing, filings, submissions, physical-device or safety-critical commands
- agent authority: tools, MCP servers, shell/browser access, schedulers, memory
- supply chain/deploy: CI/CD, package publish, infra, dependency pins
- logs/audit: logging config, traces, error reporting, analytics, audit mutability

If the workspace is empty or lacks relevant files, say that directly and classify local code evidence as missing.

### 2. Build The Vitals Map

Identify:

- sensitive data classes
- actors, tenants, roles, and trust boundaries
- tools and credentials the system can use
- actions that change money, remote state, public state, or durable records
- logs and audit surfaces
- rollback and incident paths

Use `catastrophe-taxonomy.md` when deciding what counts as a vital.

### 3. Classify

Use this severity language consistently:

- `Red`: catastrophic blast radius, ungated irreversible action, live money/control-plane access, or missing control on a high-risk path.
- `Amber`: sensitive path exists, but controls or proof are incomplete.
- `Green`: evidence proves scoped authority, controls, tests, and rollback.
- `Unknown`: evidence is absent or indirect. Unknown is not safe.

### 4. Apply Evidence Gates

Use `evidence-gates.md` to decide whether a control is proven. Prefer direct artifacts: code, config, tests, logs, policy docs, runtime behavior, or source receipts. Do not accept intent, comments, or claims as proof by themselves.

### 5. Activate Sources

Use `source-trigger-taxonomy.md` first to map observed surface signals to presets. Then use `source-registry.md` and `source-weights.json` only after a vital activates them. Prefer primary official sources for current claims. Label drafts, concepts, proposals, local vault notes, academic papers, and vendor writing as weaker evidence. Do not claim SOC 2, HIPAA, PCI DSS, FedRAMP, CMMC, legal, medical, financial, tax, or safety compliance from this skill.

### 6. Grill One Question At A Time

Ask only the next highest-leverage unresolved question. Phrase it as:

```text
Question: <one concrete risk decision>
Recommended answer: <your recommendation>
Evidence needed: <what would prove it>
Why this matters: <catastrophic failure mode>
```

If the user answers, update the Vitals Map and continue. If the answer contradicts code evidence, say so and name the contradiction.

### 7. Report

Use `report-template.md` for final or checkpoint reports. Always include:

- current Vitals Map
- catastrophe table
- hard stops
- unresolved Unknowns
- evidence inspected
- evidence still needed
- activated sources and checked dates when standards are used
- out-of-scope handoffs for `code-hygiene-compounder`
- next verification steps

## Hard Stops

Escalate as `Red` until fixed or explicitly accepted:

- secrets, tokens, mnemonics, private keys, or OAuth credentials in repo, prompts, screenshots, transcripts, logs, or normal traces
- agent can read private keys or execute live trades/transfers
- agent can edit risk limits, signing policy, or audit logs
- tenant data can be read or mutated without proven authorization
- external sends, publishing, filings, bids, physical/safety-critical actions, or customer-visible outputs lack a final human gate
- raw prompts, uploads, transcripts, customer content, or business strategy are logged by default
- payment/card handling enters PCI scope without explicit architecture and controls
- high-trust advice is shipped without current official domain source corpus, refusal behavior, escalation, and qualified human review
- model/tool loops, retries, queues, or fanout can spend money or exhaust production resources without caps, timeouts, cancellation, and an owner

## Vault Research

Use vault research only when the user asks for it or when local context clearly requires the user's vault doctrine. Follow the relevant skill rules exactly.

- Academic: use `aquery`/Academic retrieval rules. By default, do not consult Academic Graphify. If the user explicitly changes that policy in the current turn, use Academic Graphify only as a navigation map to find candidate notes or terms, never as evidence or coverage.
- Business: use Business Graphify as navigation only, then verify against durable notes and deterministic retrieval receipts.
- Any overflowed retrieval is navigation only unless the full candidate set is read through the required process.

Use `anti-overexpansion-query-protocol.md` before making vault-grounded claims.

## Skill Iteration Checks

When editing this skill, run `quick_validate.py`, `scripts/validate_grill_skill.py`, `scripts/source_activation_plan.py --self-test`, `scripts/calibrate_source_taxonomy.py` (GFV-100 plus regression cases), a representative `scripts/source_activation_plan.py --surface "<surface>"` check, `scripts/check_source_links.py`, `scripts/check_code_hygiene_overlap.py`, and `scripts/validator_smoke_tests.py` before claiming the edit is sound. If making version-specific or high-stakes standards claims, also run `scripts/check_source_links.py --online` or browse the cited primary sources during the run.
