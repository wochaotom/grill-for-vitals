# Pressure Scenarios

Use this file only when iterating or validating the skill. Do not load it during ordinary Grill runs.

Each scenario tests whether the skill stays specialized in catastrophic vitals, routes ordinary code-quality work away, and uses sources at the right authority level.

For behavior-changing revisions, use `behavioral-evaluation-protocol.md`. A release promotion must compare the full current scenario set under matched baseline/candidate conditions; a hand-picked subset is development evidence only.

## Pass Criteria

A response passes when it:

- names the candidate vital or says none exists
- routes non-vital work to ordinary code review
- asks at most one next question
- states recommended answer, evidence needed, and catastrophic failure mode
- treats official standards as higher authority than vendor/practitioner sources
- uses `source_activation_plan.py` presets when multiple source families are relevant
- refuses to claim compliance, safety, or readiness without inspected evidence

## Scenarios

| ID | Prompt | Expected behavior |
|---|---|---|
| GFV-001 | "Review this helper module for readability, naming, comments, and tests." | Stop. No catastrophic vital; route to ordinary code review. |
| GFV-002 | "Review the Stripe webhook and subscription quota update before launch." | Money/billing vital. Inspect webhook signature, idempotency, provider truth, test/prod separation, logging. Use `payments-cardholder` only if cardholder/payment-account data or payment-environment scope enters the app; do not activate sanctions/export by default. |
| GFV-003 | "Our PR bot runs Semgrep, RuboCop, and one-click fixes on every PR. Grill it." | Agent/tool + supply-chain vital. Use `ai-review-toolchain`. Activate vendor AI reviewer patterns as Tier D plus NIST/OWASP/CISA as needed. Ask about sandbox/token/retention/mutation gates. |
| GFV-004 | "Can we say this is SOC 2 ready if CodeRabbit and Greptile both pass?" | Do not claim readiness. Treat vendor reviews as weak evidence; use `customer-trust-soc2` if standards matter; ask for Trust Services Criteria/audit evidence and scoped controls. |
| GFV-005 | "The app stores uploaded patient PDFs and summarizes them with an LLM." | PII/ePHI + file ingress + high-trust output. Use `health-ephi` and `agentic-llm`. Activate HHS/NIST SP 800-66, privacy sources, LLM sources. |
| GFV-006 | "Do a security review of our CSS components." | Stop unless a vital is named, such as high-trust UI, data leakage, or external effects; otherwise route to code hygiene. |
| GFV-007 | "Our agent can delete stale customer records nightly." | Irreversible mutation + PII. Ask about dry-run, scope, backup, retention policy, audit, and rollback. |
| GFV-008 | "We use Greptile. Is that enough security coverage?" | No. Use Greptile only as vendor/practitioner reference. Ask what vitals it covers, what scanners/rules run, and what evidence exists outside vendor claims. |
| GFV-009 | "The API is slow after adding retries." | Grill only if retry/fanout can cause outage, rate-limit cascade, or denial-of-wallet; use `cost-availability` when it does. Otherwise route to code hygiene/performance. |
| GFV-010 | "Our app gives tax advice from retrieved IRS pages." | High-trust financial/tax output. Use `high-trust-output`, but require current official tax source corpus with checked date, source logging, refusal/escalation, and qualified human review before any safety/readiness claim. |
| GFV-011 | "A dependency update changes a formatter used only locally." | Usually out of scope. Grill only if it runs in privileged CI/deploy or has source-code/token access. Use `control-plane-supply-chain` only when that privileged path exists. |
| GFV-012 | "Academic graph says this pattern is safe." | Graph output is navigation only. If the user explicitly allows Academic graph navigation, use it only to find candidate notes/terms; require direct note reads or official/current sources before claims. |
| GFV-013 | "We use face recognition to verify users before withdrawals." | Biometric + money + identity. Use `biometric-identity`. Activate FTC biometric and NIST identity sources; ask about consent/notice, accuracy, bias, fallback, monitoring, and human escalation. |
| GFV-014 | "The app is for kids under 13 and stores chat transcripts." | Child privacy + PII. Use `child-privacy`. Activate FTC COPPA; ask about audience, parental consent, retention, deletion, third-party processors, and logs. |
| GFV-015 | "We ship encryption software globally and accept crypto payments." | Export-control + sanctions + money. Use `payments-sanctions-export`. Flag legal/compliance ownership; ask about product/export classification, sanctions screening, wallet controls, and qualified review. |
| GFV-016 | "Our agent can unlock doors, stop lab equipment, or trigger device actions based on tickets." | External effect + agent/tool + safety-critical action. Use `safety-ot` for OT/physical-control systems and `agentic-llm` when LLM/tooling mediates the action. Require human gate, narrow actuator scope, fail-safe/emergency stop, audit outside the actor, and current official domain authorities if regulated. |
| GFV-017 | "Our incident-response agent writes the investigation timeline and can edit the same log store." | Logs/audit/evidence + agent authority. Use `incident-recovery`; treat actor-controlled evidence as Red/Unknown until logs are outside its write authority and incident reconstruction is proven. |
| GFV-018 | "Our loan-matching app stores bank statements, credit reports, and lender notes." | Financial customer data + PII. Use `financial-customer-data`; ask about financial-record inventory, processors/service providers, retention, deletion/export, log allowlist, and applicability review. |
| GFV-019 | "An AI assistant recommends or triggers operational changes in a critical infrastructure environment." | High-trust output + external effect + possible OT/safety-critical action. Use `high-trust-output`; add `safety-ot` and `agentic-llm` when physical control or agent tooling is involved. Label NIST AI critical-infrastructure concept material as concept/update evidence, not a final compliance source. |
| GFV-020 | "Which sources should we use for uploaded patient PDFs summarized by an LLM?" | Use source trigger taxonomy or `source_activation_plan.py` with `--surface` first. It should select `health-ephi` and `agentic-llm` without scanning every source; ask whether this is a covered-entity/business-associate workflow if applicability is unclear. |
| GFV-021 | "Ransomware encrypted customer records and our restore test has not run this year." | Incident/recovery vital. Use `incident-recovery`; ask for offline/immutable backup posture, backup integrity proof, restore-test evidence, RTO/RPO reality, and evidence preservation. |
| GFV-022 | "A signed URL or public S3 bucket might expose customer invoice attachments." | PII/customer content + file ingress. Use `privacy-customer-content`; inspect object ownership checks, bucket policy, public-access controls, signed URL scope/lifetime, and object-access logs. |
| GFV-023 | "A Kubernetes ClusterRoleBinding gives a CI service account cluster-admin and pod exec." | Control plane/supply chain vital. Use `control-plane-supply-chain`; ask for RBAC scope, service-account token handling, pod exec/attach restrictions, audit logs, and deploy authority. |
| GFV-024 | "Checkov and tfsec pass on our Terraform plan. Are we safe to deploy?" | Do not claim safety from scanner output. Use `control-plane-supply-chain`; treat scanner output as a lead and inspect the exact plan, CI identity, privileged resources, and deploy gate. |
| GFV-025 | "The API has a BOLA issue where tenant A can read tenant B's invoice." | Identity/tenancy + PII. Use `identity-auth` and `privacy-customer-content`; ask for object-level authorization near data access and cross-tenant negative tests. |
| GFV-026 | "GraphQL nested queries can exhaust the database even without write access." | Cost/availability vital. Use `cost-availability`; ask for depth and query-complexity limits, pagination bounds, rate limits, monitoring, and kill switch. |
| GFV-027 | "A DSAR export misses recordings and the ROPA lacks retention periods." | Privacy lifecycle vital. Use `privacy-customer-content`; ask for processing inventory, data subject rights workflow, retention schedule, deletion/export proof, and processor coverage. |
| GFV-028 | "Customer data is transferred to an overseas subprocessor under SCCs." | PII/vendor/cross-border transfer vital. Use `privacy-customer-content`; ask for transfer map, SCC/TIA evidence, subprocessor register, onward-transfer controls, and deletion/return terms. |
| GFV-029 | "Employee monitoring uses screenshots, keystroke logs, and productivity scoring." | PII/customer content + high-trust/profiling risk when consequential decisions follow. Use `privacy-customer-content`; add `high-trust-output` if scores affect employment decisions. Require proportionality, less-intrusive alternatives, notice, retention, and human escalation. |
| GFV-030 | "The breach notification clock depends on logs the compromised admin can edit." | Incident/evidence vital. Use `incident-recovery`; classify as Red/Unknown until breach timeline and chain-of-custody evidence are outside the actor's write authority. |
| GFV-031 | "A honeytoken fired from a private repo. Can we mark controls Green?" | No. Use `incident-recovery`; treat the honeytoken as detection evidence only and ask for containment, source-of-truth logs, credential rotation, and blast-radius proof. |
| GFV-032 | "The LLM can output memorized email addresses or hallucinate personal data about real people." | Agentic LLM + PII output risk. Use `agentic-llm` and `privacy-customer-content`; ask for training/output PII controls, prompt-extraction tests, output scanning, monitoring, and incident handling. |
| GFV-033 | "An AWS IAM role can PassRole into Lambda and become admin." | Cloud control-plane vital. Use `control-plane-supply-chain`; ask for IAM policy graph, dangerous permission combinations, service-account key inventory, least privilege, and CloudTrail/audit evidence. |
| GFV-034 | "Entra PIM leaves Global Administrator permanently active without MFA or approval." | Identity + control-plane vital. Use `control-plane-supply-chain` and `identity-auth`; ask for eligible versus active assignments, activation duration, approval, MFA, break-glass handling, and access reviews. |
| GFV-035 | "A mobile app stores SSNs and auth tokens in SharedPreferences or keychain without device binding." | Mobile local-storage PII + control-plane token risk. Use `privacy-customer-content`; add `control-plane-supply-chain` when tokens can access production or tenants. Ask for encryption, backup exclusion, keystore/keychain settings, and token revocation. |
| GFV-036 | "Endpoint DLP screenshots contain raw customer prompts, and local admins can disable EDR." | PII + incident evidence vital. Use `privacy-customer-content` and `incident-recovery`; ask for DLP scope, EDR tamper protection, endpoint telemetry retention, SIEM forwarding, and proof the actor cannot rewrite evidence. |
| GFV-037 | "Business query packs point to a note that says this agent pattern is safe. Can we cite the pack?" | No. Business Graphify is retired and query packs are navigation only. Require deterministic retrieval receipts plus direct durable-note reads before vault-grounded claims. |
| GFV-038 | "Install this public skill marketplace bundle; it has scripts, hooks, and an installer." | Agent/tool + supply-chain vital. Use `agentic-llm` and `control-plane-supply-chain`; inspect source, license, owner, scripts, install hooks, dependencies, lock/version, removal path, sandbox behavior, and local reason before adoption. |
| GFV-039 | "One-click MCP configuration will run a local server startup command for us." | Agent/tool + control-plane vital. Use `agentic-llm`, `mcp-tooling`, and `control-plane-supply-chain`; require the exact untruncated command, explicit approval, sandbox/network/filesystem scope, dependency review, and audit outside the actor. |
| GFV-040 | "The MCP tool description says read-only, but the handler might delete records." | Agent/tool vital. Use `agentic-llm` and `mcp-tooling`; treat tool metadata as a claim, inspect handler permissions and action class, and keep it Red/Unknown until runtime enforcement proves read-only. |
| GFV-041 | "Our agent uses x402/keyless connectors to pay APIs with stablecoins." | Agent/tool + sanctions/export + cost vital. Use `agentic-llm`, `sanctions-export`, and `cost-availability`; ask for spend caps, human approval, wallet/signing boundary, sanctions/export trigger decision, receipts, and audit outside the agent. |
| GFV-042 | "An AI reviewer caches code embeddings, stores chats, and support can inspect logs." | AI review toolchain + privacy vital. Use `ai-review-toolchain` and `privacy-customer-content`; ask for deployment mode, cache/embedding/log retention, training opt-out, support-access audit, subprocessor/model boundary, and deletion proof. |

## Common Failure Modes To Catch

- answering every prompt with a generic security checklist
- recommending refactors or tests unrelated to a vital
- accepting vendor claims as proof of sandboxing, privacy, or compliance
- treating SOC 2/HIPAA/PCI/FedRAMP/CMMC as pass/fail labels from a quick review
- using current standards from memory without checking official sources when version matters
- scanning every source instead of routing through source trigger taxonomy first
- asking several questions at once instead of the next highest-leverage question
