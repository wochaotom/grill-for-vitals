---
name: grill-for-vitals
description: "Maps the catastrophic failure paths in a system and grills the user on them in rounds, backed by code evidence: secrets/control plane, PII, auth/tenancy, money/payments/trading/procurement, irreversible writes, external sends/physical actions, agent tools/MCP/browser/shell, CI/CD, logs/audit, high-trust outputs, and runaway cost. Use before design, implementation, launch, security review, or automation that touches any of these. Do not use for ordinary code review, refactors, style, tests, maintainability or generic hardening unless a catastrophic vital is implicated."
---

# Grill For Vitals

Use this skill to find the parts of a system where compromise, misuse, or bad automation would be catastrophic. This is not a generic security checklist and not a compliance certification. It is a catastrophe-mapping interview backed by code evidence.

## Core Rules

1. Run the scope gate first. If no catastrophic vital is implicated, stop and route the task to ordinary code review.
2. Inspect code, docs, configs, and existing project rules before asking the user.
3. If the answer can be discovered locally, discover it instead of asking.
4. Classify each vital as `Red`, `Amber`, `Green`, or `Unknown`; never downgrade missing evidence to safe.
5. Facts are your job; decisions are the user's. Look up anything the code, config, docs, or a sub-agent can answer, and only ask the user for risk decisions and facts that exist nowhere you can read.
6. Grill in rounds (step 6): every question gets a recommended answer, the evidence that would prove it, and the catastrophic failure mode it guards against.
7. Separate evidence from inference. Say plainly when a claim is inferred.
8. Use authoritative sources only for activated vitals; do not load broad code-quality sources here.
9. Do not claim compliance, readiness, or safety unless the required evidence was inspected in this run.

## Reference Loading

Load only what the current step needs. Every path below is under `references/`.

Core, for most runs:

- `scope-boundary.md`: scope gate, out-of-scope handoff rules, and examples.
- `catastrophe-taxonomy.md`: vital categories and Red/Amber/Green/Unknown rules.
- `evidence-gates.md`: what proof is required for each high-risk area.
- `question-bank.md`: grill questions by vital, to draw each round from.
- `report-template.md`: output shape for Vitals reports.
- `vital-principles.md`: distilled source-backed principles for everyday Grill runs.

Sources, only after a vital activates them:

- `source-trigger-taxonomy.md`: surface-signal taxonomy for choosing presets before reading the wider source registry.
- `source-registry.md`: authoritative source tiers, freshness rules, and conditional source activation.
- `source-weights.json`: source activation weights for high-risk domains.
- `vitals-source-matrix.md`: vital-to-source-preset and evidence-gate map.
- `vendor-ai-reviewer-patterns.md`: Greptile/CodeRabbit-inspired AI code-review security patterns; use as vendor/practitioner input only.

Situational:

- `vault-research.md`: only when the user asks for vault research or the context depends on their Obsidian vault doctrine.
- `anti-overexpansion-query-protocol.md`: how to use `aquery` and `bquery` without graph or retrieval overflow becoming fake authority.

Skill development only; never load during a normal Grill run:

- `pressure-scenarios.md`: validation prompts for skill iteration.
- `behavioral-evaluation-protocol.md`: baseline/candidate promotion protocol for skill iteration.
- `source-map.md`: design lineage, not the active source registry.

Once a vital activates, pick its source preset(s): run `scripts/source_activation_plan.py --surface "<observed problem surface>"`, or, if you cannot run scripts, look the surface up in `source-trigger-taxonomy.md`. Choose a matching preset such as `identity-auth`, `control-plane-supply-chain`, `privacy-customer-content`, `financial-customer-data`, `ai-review-toolchain`, `high-trust-output`, `agentic-llm`, `health-ephi`, `child-privacy`, `biometric-identity`, `child-biometric`, `payments-cardholder`, `sanctions-export`, `customer-trust-soc2`, `incident-recovery`, `safety-ot`, `cost-availability`, `money-business-logic`, `file-ingress`, `payments-sanctions-export`, or `federal-defense`; do not load broad source packs by default. If no preset matches the surface (an irreversible delete or migration, for example), write `Sources: no matching preset`, rely on local evidence, the vital's evidence gate, and any provider's own documentation labelled as vendor evidence, and do not stretch an unrelated preset to fill the line.

## Workflow

### 0. Scope Gate

Before reviewing broadly, identify at least one candidate vital, its catastrophic failure mode, and the evidence gate that would prove it controlled. Use `scope-boundary.md`.

Out of scope examples:

- style, naming, readability, formatting, dependency cleanup, or ordinary test coverage
- generic "make this safer" work with no vital surface
- performance or architecture issues unless they create runaway cost, outage, data exposure, or irreversible mutation

If an ordinary code-quality issue appears while mapping a vital, record it as an out-of-scope handoff and return to the vital.

### 1. Context Sweep

Start with a local sweep. Prefer `rg --files` and targeted `rg` searches. For a large codebase, hand independent areas to parallel sub-agents and keep only their findings. Check, when present:

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

Every activated vital gets at least one preset, picked as described under Reference Loading. Name the presets in each round's `Sources:` line (step 6). Then use `source-registry.md` and `source-weights.json` only after a vital activates them. Prefer primary official sources for current claims. Label drafts, concepts, proposals, local vault notes, academic papers, and vendor writing as weaker evidence. For regulated-scope presets (for example `health-ephi`, `payments-cardholder`, `child-privacy`, `sanctions-export`, `federal-defense`): when the description names that kind of data or activity (patient records, card numbers, children's data), use the preset now and also ask whether the legal regime applies (for example covered entity or business associate, PCI scope) instead of assuming it does; when the description only makes it plausible (billing does not mean card data), do not activate the preset, and ask whether that scope exists. Do not claim SOC 2, HIPAA, PCI DSS, FedRAMP, CMMC, legal, medical, financial, tax, or safety compliance from this skill.

### 6. Grill In Rounds

Treat the open risk decisions as a tree: settling one decision opens the decisions that depend on it. The **frontier** is every open decision whose prerequisites are already settled.

Each round, ask the whole frontier at once, highest risk first (`Red` and `Unknown` before `Amber`). Ask at most five questions per round; if the frontier is larger, ask the riskiest five and hold the rest for the next round. Do not ask a question whose answer depends on another question in the same round; it belongs to a later round. Draw wording from `question-bank.md`.

Format each round like this:

```text
Round <n>
Main risk: <the one vital that would hurt most, with its Red/Amber/Unknown status>
Sources: <preset(s) in use; official sources first, weaker ones labelled draft, concept, vendor, or local>

Q1. <one concrete risk decision>
Recommended answer: <your recommendation>
Evidence needed: <what would prove it>
Why this matters: <catastrophic failure mode>

Q2. ...

Reply "yes" to accept every recommendation, or answer by number.
```

Lead with the main risk: when several vitals apply, pick the one whose failure would do the most harm (for example, high-trust advice that operators act on outranks the tool path that carries it out), and put it first. When no vital can be named yet, still use this format: write `Main risk: none named yet (Unknown)` and `Sources: no matching preset`, and ask the questions that would reveal the vital.

Word each question so that "yes" accepts your recommended answer.

When a frontier question needs a fact rather than a decision, find the fact yourself (read the code, run a search, or dispatch a sub-agent) instead of asking. Do not block the round on it: ask the rest of the frontier now and hold back only the questions that depend on the pending fact.

After each round, update the Vitals Map and statuses, recompute the frontier, and ask the next round. If an answer contradicts code evidence, say so and name the contradiction. The grilling is done when the frontier is empty: every vital is classified, and every hard stop has an owner and a fix or an explicit acceptance. Do not act on the map until the user confirms it.

### 7. Report

Use `report-template.md` for final or checkpoint reports. Always include:

- current Vitals Map
- catastrophe table
- hard stops
- unresolved Unknowns
- evidence inspected
- evidence still needed
- activated sources and checked dates when standards are used
- out-of-scope handoffs for ordinary code review
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

Only when the user asks for vault research, or local context clearly depends on their vault doctrine, load `vault-research.md` and follow it exactly.

## Skill Iteration Checks

When editing this skill, run `quick_validate.py`, `scripts/validate_grill_skill.py`, `scripts/source_activation_plan.py --self-test`, `scripts/calibrate_source_taxonomy.py` (GFV-100 plus regression cases), a representative `scripts/source_activation_plan.py --surface "<surface>"` check, `scripts/check_source_links.py`, and `scripts/validator_smoke_tests.py` before claiming the edit is sound. For behavior-changing edits, follow `behavioral-evaluation-protocol.md` and compare matched receipts with `scripts/evaluate_behavioral_runs.py`; static validation is not a behavioral promotion result. If making version-specific or high-stakes standards claims, also run `scripts/check_source_links.py --online` or browse the cited primary sources during the run.
