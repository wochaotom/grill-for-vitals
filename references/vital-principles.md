# Vital Principles

Use these distilled principles during ordinary Grill runs. They summarize the source registry without turning the skill into a standards dump or generic code review.

## Principles

1. **Start with blast radius.** A finding matters here only when breach, misuse, or automation failure could cause severe harm.
2. **Unknown is not safe.** Missing evidence keeps a vital `Unknown` or `Amber`; intent, comments, and vendor claims do not prove control.
3. **Keep authority narrow.** Credentials, tokens, tools, agents, CI jobs, and reviewer bots should have the smallest useful scope, lifetime, network reach, and mutation authority.
4. **Enforce below prompt text.** Prompt instructions, review comments, UI hiding, and policy prose are not gates unless code/config/runtime enforcement backs them.
5. **Separate draft from execution.** Money movement, external sends, publishing, filings, deploys, deletes, approvals, and high-trust outputs need explicit final gates.
6. **Minimize sensitive data.** Store the least customer content, PII, source code, embeddings, prompts, uploads, logs, and traces the product can honestly support.
7. **Sandbox untrusted work.** File parsers, analyzer tools, reviewer bots, build scripts, model tools, browser automation, and shell execution are attack surfaces.
8. **Protect the evidence plane.** Audit logs, security traces, approval records, and incident evidence must not be writable by the actor being investigated.
9. **Use conditional authorities.** Activate HIPAA, COPPA, PCI DSS, FedRAMP, CMMC, sanctions, export, biometric, identity, or AI sources only when the vital triggers them.
10. **Treat vendor tools as signals.** Greptile, CodeRabbit, SAST, scanners, and AI reviewers can provide leads; pair them with Tier A/B sources unless the question is purely vendor configuration.
11. **Require rollback or containment.** High-risk writes need preview, scoped target, backup, dry-run, compensation, kill switch, revocation, or shutdown path.
12. **Bound automation.** Retries, queues, model calls, fanout, schedulers, and loops need limits, monitoring, owners, and cancellation paths.

## Source Families

- NIST/FTC/HHS/PCI/FedRAMP/CMMC/OFAC/BIS sources anchor regulated or official claims.
- NIST SP 800-82 and NIST CSF anchor OT, physical-control, and safety-critical actuation questions.
- OWASP/MITRE sources anchor technical failure modes and attack-path language.
- CISA/NIST SSDF sources anchor secure-by-design and producer/toolchain accountability.
- Greptile/CodeRabbit sources are Tier D practitioner references for AI reviewer/toolchain questions only.

## Non-Claims

Do not infer compliance, certification, readiness, legality, medical safety, financial suitability, or production safety from these principles. They guide questions and evidence collection.
