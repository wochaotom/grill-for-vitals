# Vendor AI Reviewer Patterns

Use this only when the vital involves AI code-review tools, PR bots, hosted source-code analysis, reviewer plugins, or security-review agents. Greptile and CodeRabbit are vendor/practitioner references, not authoritative standards. Their patterns can suggest questions and evidence gates; they do not prove safety, compliance, or correctness.

## What These Sources Add

| Pattern | Why it matters for vitals |
|---|---|
| Graph/codebase context | AI reviewers may index large portions of a repository, related repos, file paths, docs, comments, and generated summaries. Treat this as source-code and sensitive-business-data ingestion. |
| Scoped review rules | Directory-specific or org-enforced rules help keep high-risk packages stricter than generic code. Vitals can require rules tied to payment, auth, data, deploy, or tool surfaces. |
| Third-party analyzers | Linters, SAST, secret scanners, IaC scanners, and language tools may execute untrusted project configuration. Treat analyzer execution as a sandbox and supply-chain surface. |
| Sandboxed review events | A review worker should have no ambient secrets, no internal-network reach, no long-lived credentials, and only a short-lived repo-scoped token. |
| Token service separation | Tokens should be event-scoped, short-lived, rate-limited, audited, and unavailable to analyzer subprocesses unless strictly required. |
| Per-customer isolation | Code indexes, caches, embeddings, and logs should be isolated and encrypted per customer or tenant. |
| Model/subprocessor boundary | Hosted reviewers may send prompts, code context, embeddings, logs, or summaries to model providers or subprocessors. The deployment mode decides where customer code and metadata can flow. |
| Training and retention controls | Vendor claims about "not training" or deletion must be backed by contracts, product settings, trust-center evidence, and observed configuration. |
| Incident response receipts | The CodeRabbit RuboCop disclosure is a useful example: analyzer outside sandbox, immediate disablement, credential rotation, full audit, automated sandbox enforcement, deployment gates. |

## Source-Specific Cues

Use these as question seeds, not as accepted proof.

Greptile cues:

- cloud, on-prem, and bring-your-own-LLM modes change the data boundary
- customer code, vector embeddings, file paths, docs, generated docstrings, and chat logs may be distinct retention surfaces
- hosted mode may involve external model providers and cloud infrastructure; self-hosted mode still needs local secret, network, logging, and model-key controls
- account settings, DPA/trust-center evidence, deletion behavior, and AI-training opt-out need direct verification
- directory-scoped rules, rule IDs, severity, inheritance, and org-enforced rules are useful controls only if they cannot be bypassed by the risky PR
- related-repository context settings can expand ingestion beyond the changed repo; verify exact repo scope and credentials
- filters, ignore patterns, skip-review controls, strictness, and file-change limits can accidentally exclude vital paths
- support access to chat logs or customer data requires audit evidence, least privilege, and customer-visible retention settings
- As checked on 2026-05-24, Greptile's config docs expose `.greptile/` cascading configuration, `files.json` context inputs, related-repository context, structured rule IDs/severity/scope, and dashboard-enforced org rules; use those as concrete evidence targets, not proof of enforcement
- As checked on 2026-07-11, Greptile's security page says hosted, self-hosted, and bring-your-own-LLM modes have different code/data boundaries; customer code cache, vector embeddings, chat logs, support access, AI-training opt-out, and administrator deletion are separate evidence targets.

CodeRabbit cues:

- review events, CLI/IDE review flows, third-party tools, linters, web search, and verification checks are separate execution surfaces
- event-isolated sandboxes, blocked internal-network access, short-lived repo-scoped tokens, and per-customer cache/index encryption are evidence targets
- tool catalogs can reveal which scanners or analyzers run and which project-controlled configuration they may parse
- incident-response claims should be checked against deployment gates, automated sandbox enforcement, audit logs, and vulnerability disclosure process
- cache opt-out, token scope, and analyzer allowlists should be checked in product settings or config, not assumed from public docs
- reconcile marketing, documentation, contract, and active-setting claims when retention wording differs; the deployed configuration and enforceable terms control the evidence decision
- As checked on 2026-05-24, CodeRabbit's tool docs name security and privacy analyzers such as Semgrep/OpenGrep, TruffleHog, Betterleaks, OSV-Scanner, Checkov, Trivy, Brakeman, and Microsoft Presidio; treat each enabled tool as an execution/configuration surface requiring sandbox evidence
- As checked on 2026-07-11, CodeRabbit's docs and security-posture writing point to cache encryption/expiration, cache opt-out, per-review sandboxing, no ambient sandbox secrets, blocked internal network access, short-lived event-scoped tokens, per-customer cache/index encryption, and training/retention settings as concrete evidence targets.

## Grill Questions

Question: What repository data does the AI reviewer ingest, cache, embed, log, or send to model providers?
Recommended answer: Limit ingestion to the minimum needed; document code storage, embeddings, logs, training settings, retention, deletion, subprocessors, and provider boundaries.
Evidence needed: Vendor/security docs, contracts or DPA, app settings, audit logs, cache/embedding architecture, model-provider configuration.
Why this matters: Source code can contain secrets, unreleased strategy, customer-specific logic, vulnerabilities, and regulated data.

Question: Which deployment mode, model providers, subprocessors, and support-access paths are active?
Recommended answer: Choose the narrowest viable deployment mode, disable avoidable training/logging, require DPA/subprocessor review, and prove support access is audited and least-privilege.
Evidence needed: Contract/DPA, subprocessor list, deployment architecture, model-provider settings, support-access logs, retention and deletion settings.
Why this matters: A reviewer can leak sensitive code through metadata, prompts, embeddings, support workflows, or model-provider boundaries even when PR comments look harmless.

Question: Can reviewer workers or analyzers reach secrets, internal networks, or long-lived credentials?
Recommended answer: No. Each review should run in a sandbox with no ambient secrets, blocked internal-network access, and only short-lived repo-scoped credentials.
Evidence needed: Sandbox architecture, token issuer policy, network policy, environment inventory, analyzer execution policy, deployment gate checks.
Why this matters: A malicious PR can turn an analyzer, linter, or build hook into code execution.

Question: Which third-party tools execute code or parse project-controlled configuration?
Recommended answer: Treat every analyzer and parser as untrusted-code execution unless proven otherwise.
Evidence needed: Tool list, config files, sandbox proof, allowed network/filesystem scope, scanner logs, and enforcement tests.
Why this matters: Security scanners can become the attack path if they run unsafe project config outside containment.

Question: Are high-risk review rules enforced at the organization level or only suggested in repo files?
Recommended answer: Vitals should use org-enforced or otherwise non-bypassable rules for auth, payments, secrets, PII, deploy, and external effects.
Evidence needed: Rule registry, rule IDs, severity, scopes, last-applied timestamps, bypass/audit policy.
Why this matters: Repo-local rules are easy to weaken in the same PR that introduces risk.

Question: Can review filters, ignored paths, related-repo context, file limits, or skip-review settings hide a vital path?
Recommended answer: High-risk paths should be explicitly included or separately reviewed, and related-repo context should be narrowly scoped.
Evidence needed: Reviewer config, inherited/org config, include/exclude path rules, related repository list, last applied settings, review logs.
Why this matters: A reviewer can look active while silently skipping the auth, payment, deploy, or safety-critical code that matters.

Question: Can AI review findings auto-fix, commit, approve, merge, publish, or trigger agent work on vital paths?
Recommended answer: AI review output can draft fixes, but high-risk changes require human approval and independent verification.
Evidence needed: App permissions, one-click-fix settings, branch protection, required reviews, status checks, merge rules, audit logs.
Why this matters: A reviewer that can also mutate code is part of the control plane.

## Use Limits

- Treat vendor claims as prompts for evidence, not proof.
- Treat apparently conflicting retention or security claims as an unresolved configuration question until current settings and terms are inspected.
- Prefer official standards for requirements and compliance language.
- Do not copy vendor marketing metrics into findings unless independently verified.
- Do not let these sources pull Grill into generic PR review. Use them only when source-code ingestion, analyzer execution, AI reviewer authority, or vendor toolchain risk is a vital.
