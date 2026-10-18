# Source Registry

Use this registry only after a vital activates source-grounded questioning or reporting. This is a high-risk surface corpus, not a general code-review corpus.

## Contents

- Source Tiers
- Freshness Rules
- Activation Registry
- Current Source Links
- Source Admission Rules
- Rejected Or Deferred Sources

## Source Tiers

| Tier | Source type | Use | Limits |
|---|---|---|---|
| A | Official government, regulator, standards body, or program owner | Current claims, source-backed questions, evidence gates, regulated-domain framing | Still does not prove compliance without a real audit. |
| B | Recognized security standards nonprofit or public framework | Technical risk taxonomy and verification emphasis | Prefer latest stable release; label drafts/incubators. |
| C | Local project docs and vault notes | User doctrine, system facts, prior decisions, operator preferences | Must be read directly; graph or retrieval summaries are navigation only. |
| D | Academic papers, vendor research, incident reports, blogs, community posts | Emerging threat discovery and example attack patterns | Never override Tier A/B for standards claims. |

## Freshness Rules

- Browse or otherwise verify official sources during the run before making version-specific, legal, compliance, medical, financial, or security-readiness claims.
- Use `scripts/check_source_links.py` for offline registry integrity and `scripts/check_source_links.py --online` for best-effort URL reachability when source currentness materially affects the answer.
- Record the source URL and checked date in the report when standards materially affect a finding.
- Prefer final current standards over drafts or concept notes. Use drafts/concepts only when that status itself matters, and label them `draft`, `initial public draft`, or `concept`.
- Do not claim SOC 2, HIPAA, PCI DSS, FedRAMP, CMMC, legal, medical, financial, or safety compliance from this skill.
- Use vault material only as local doctrine or system context unless the full note set was read through the applicable query protocol.
- Reject style, readability, generic testing, and maintainability sources here; those belong to `code-hygiene-compounder`.

## Activation Registry

| Source ID | Tier | Activate for | Use |
|---|---|---|---|
| `nist-ai-rmf` | A | AI systems, agent governance, high-trust AI outputs | Govern/Map/Measure/Manage risk framing; critical-infrastructure profile concept material must be labeled if used. |
| `nist-ai-600-1` | A | Generative AI, LLM apps, model-mediated workflows | GenAI risk profile, testing, provenance, incident disclosure, lifecycle risks. |
| `owasp-llm-top10` | B | LLM apps, RAG, prompt/tool injection, sensitive disclosure | Current OWASP GenAI LLM-specific failure modes and mitigations. |
| `owasp-agentic-apps` | B | Autonomous or tool-using agents | Agent goal hijack, tool misuse, identity abuse, memory/context poisoning, cascading failures. |
| `owasp-agentic-skills` | B provisional | Skills/plugins/extensions that grant agents workflows or permissions | Skill supply chain, permission manifests, sandboxing, provenance, audit logging. Label incubator/project status. |
| `mcp-security-best-practices` | A | MCP servers, clients, gateways, local server installs, OAuth-backed MCP tools | Official MCP security and authorization controls for consent, token audience, SSRF, session binding, local-server execution, and scope minimization. |
| `mitre-atlas` | B | AI adversary modeling, AI attack paths | Adversarial tactics and techniques for AI-enabled systems. |
| `owasp-asvs` | B | Web apps, auth, session, access control, validation, logging, data protection | Verification requirements; use latest stable ASVS. |
| `owasp-api-top10` | B | APIs, object/function authorization, sensitive business flows, SSRF, resource consumption | API risk prioritization and question selection. |
| `owasp-top10` | B | General web-app exposure when ASVS/API Top 10 are too specific | Current broad web-app risk awareness; do not treat as complete verification. |
| `nist-sp-800-63-4` | A | Digital identity, identity proofing, authentication, federation, account recovery | Modern assurance-level framing and technical requirements for high-risk identity paths. |
| `nist-ssdf` | A | High-risk build/deploy, supply chain, software producer obligations | SP 800-218 final for stable SSDF; SP 800-218 Rev. 1 is draft/update material and must be labeled if used. |
| `cisa-secure-by-design` | A | Product security accountability, secure defaults, vendor/supplier questions | Ownership of customer security outcomes and secure-by-demand questions. |
| `nist-csf-2` | A | Cybersecurity risk governance, incident readiness, executive risk framing | Identify/Protect/Detect/Respond/Recover/Govern structure. |
| `nist-sp-800-61r3` | A | Incident response, breach readiness, evidence plane, recovery | Incident response preparation, detection, response, and recovery. |
| `nist-sp-800-82r3` | A | Operational technology, industrial control, IoT/physical-control systems, safety-critical actions | OT security guidance for performance, reliability, safety, segmentation, monitoring, and incident questions. |
| `mitre-cwe-top25` | B | Prioritizing software weakness classes after a vital path is found | Common high-impact weakness classes and root-cause language. |
| `nist-privacy-framework` | A | PII, privacy risk, data flows, retention, minimization | Stable PF 1.0 privacy risk management; PF 1.1 is draft/update material and must be labeled if used. |
| `ftc-protecting-pii` | A | U.S. business PII, retention, disposal, employee/vendor access | Take stock, scale down, lock it, pitch it, plan ahead. |
| `ftc-glba-safeguards` | A | Customer financial information, covered financial-institution workflows, service-provider safeguards | FTC GLBA/Safeguards Rule questions for protecting customer information; flag applicability for qualified legal review. |
| `hhs-hipaa-security` | A | ePHI, covered entities, business associates, health workflows | HIPAA Security Rule safeguards and breach/privacy relationship. |
| `nist-sp-800-66r2` | A | ePHI implementation guidance, HIPAA Security Rule mapping, healthcare safeguards | Practical cybersecurity resource guide for administrative, physical, and technical safeguards. |
| `ftc-coppa` | A | Child-directed services or actual knowledge of collecting children's personal information online | COPPA rule trigger and child privacy questions; do not provide legal conclusions. |
| `ftc-biometric-policy` | A | Biometric identifiers, facial/voice/fingerprint/behavioral traits, ML biometric claims | Biometric privacy, security, bias, accuracy, vendor, and ongoing monitoring questions. |
| `pci-dss` | A | Cardholder data, payment account data, payment environment scope | Baseline technical and operational requirements for payment account data. |
| `ofac-sanctions-framework` | A | Sanctions exposure, international payments, blocked persons, U.S.-origin services, virtual currency | Sanctions compliance program and screening questions; do not provide legal conclusions. |
| `bis-ear-encryption` | A | Export-controlled software, encryption source/object code, controlled technology, international transfer | Export control question triggers for encryption and software/technology exports. |
| `fedramp` | A | U.S. federal cloud services, agency authorization, continuous validation | FedRAMP Rev5 and evolving 20x evidence; verify current notices, consolidated rules, and authorization path before version-specific claims. |
| `cmmc` | A | Defense contractors, FCI, CUI, DoD/DIB workflows | CMMC levels, FCI/CUI protection, assessment and affirmation framing. |
| `nist-sp-800-171r3` | A | CUI in nonfederal systems, defense supplier systems, federal contract requirements | Recommended requirements for protecting CUI in nonfederal systems and organizations. |
| `nist-sp-800-53r5` | A | Federal control mapping, FedRAMP-style controls, security/privacy control families | Security and privacy control baseline language for federal and high-assurance environments. |
| `aicpa-tsc` | A | SOC 2 customer commitments, trust services criteria, audit-readiness questions | Security, availability, processing integrity, confidentiality, privacy criteria. Do not claim SOC 2 readiness. |
| `greptile-ai-review-security` | D | AI code reviewers, graph-based repo context, custom review rules, hosted reviewer data handling | Practitioner/vendor patterns for repo indexing, scoped rules, org-enforced rules, retention, training, model/subprocessor boundaries, and self-hosting questions. |
| `coderabbit-ai-review-security` | D | AI code reviewers, PR bots, third-party analyzer execution, sandboxed review workers, source-code privacy | Practitioner/vendor patterns for ephemeral sandboxes, short-lived scoped tokens, analyzer/tool selection, cache/index isolation, cache opt-out, incident response, and customer-data isolation. |

## Current Source Links

- `nist-ai-rmf`: https://www.nist.gov/itl/ai-risk-management-framework
- `nist-ai-rmf`: https://www.nist.gov/programs-projects/concept-note-ai-rmf-profile-trustworthy-ai-critical-infrastructure
- `nist-ai-600-1`: https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf
- `owasp-llm-top10`: https://owasp.org/www-project-top-10-for-large-language-model-applications/
- `owasp-llm-top10`: https://genai.owasp.org/llm-top-10/
- `owasp-llm-top10`: https://owasp.org/www-project-top-10-for-large-language-model-applications/assets/PDF/OWASP-Top-10-for-LLMs-v2025.pdf
- `owasp-agentic-apps`: https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- `owasp-agentic-skills`: https://owasp.org/www-project-agentic-skills-top-10/
- `mcp-security-best-practices`: https://modelcontextprotocol.io/docs/tutorials/security/security_best_practices
- `mcp-security-best-practices`: https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization
- `mitre-atlas`: https://atlas.mitre.org/
- `owasp-asvs`: https://owasp.org/www-project-application-security-verification-standard/
- `owasp-asvs`: https://github.com/OWASP/ASVS/releases
- `owasp-api-top10`: https://owasp.org/API-Security/
- `owasp-top10`: https://owasp.org/Top10/2025/
- `nist-sp-800-63-4`: https://pages.nist.gov/800-63-4/
- `nist-sp-800-63-4`: https://csrc.nist.gov/pubs/sp/800/63/4/final
- `nist-ssdf`: https://csrc.nist.gov/pubs/sp/800/218/final
- `nist-ssdf`: https://csrc.nist.gov/pubs/sp/800/218/r1/ipd
- `cisa-secure-by-design`: https://www.cisa.gov/securebydesign
- `cisa-secure-by-design`: https://www.cisa.gov/resources-tools/resources/secure-demand-guide
- `nist-csf-2`: https://www.nist.gov/cyberframework
- `nist-sp-800-61r3`: https://csrc.nist.gov/pubs/sp/800/61/r3/final
- `nist-sp-800-82r3`: https://csrc.nist.gov/pubs/sp/800/82/r3/final
- `nist-sp-800-82r3`: https://www.nist.gov/publications/guide-operational-technology-ot-security
- `mitre-cwe-top25`: https://cwe.mitre.org/top25/
- `nist-privacy-framework`: https://www.nist.gov/privacy-framework
- `nist-privacy-framework`: https://www.nist.gov/news-events/news/2025/04/nist-privacy-framework-11-initial-public-draft-available-comment
- `ftc-protecting-pii`: https://www.ftc.gov/business-guidance/resources/protecting-personal-information-guide-business
- `ftc-glba-safeguards`: https://www.ftc.gov/legal-library/browse/rules/safeguards-rule
- `ftc-glba-safeguards`: https://www.ftc.gov/business-guidance/resources/ftc-safeguards-rule-what-your-business-needs-know
- `hhs-hipaa-security`: https://www.hhs.gov/hipaa/for-professionals/security/laws-regulations/index.html
- `nist-sp-800-66r2`: https://csrc.nist.gov/pubs/sp/800/66/r2/final
- `ftc-coppa`: https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa
- `ftc-biometric-policy`: https://www.ftc.gov/news-events/news/press-releases/2023/05/ftc-warns-about-misuses-biometric-information-harm-consumers
- `pci-dss`: https://www.pcisecuritystandards.org/standards/pci-dss/
- `ofac-sanctions-framework`: https://home.treasury.gov/news/press-releases/sm680
- `ofac-sanctions-framework`: https://ofac.treasury.gov/recent-actions/20211015
- `bis-ear-encryption`: https://www.bis.gov/regulations/ear/742
- `bis-ear-encryption`: https://www.bis.gov/regulations/ear/734
- `fedramp`: https://www.fedramp.gov/20x/
- `fedramp`: https://www.fedramp.gov/docs/
- `fedramp`: https://www.fedramp.gov/notices/0009
- `cmmc`: https://dodcio.defense.gov/CMMC/
- `cmmc`: https://dodcio.defense.gov/CMMC/About/
- `nist-sp-800-171r3`: https://csrc.nist.gov/pubs/sp/800/171/r3/final
- `nist-sp-800-53r5`: https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final
- `aicpa-tsc`: https://www.aicpa-cima.com/resources/download/2017-trust-services-criteria-with-revised-points-of-focus-2022
- `greptile-ai-review-security`: https://www.greptile.com/security
- `greptile-ai-review-security`: https://www.greptile.com/docs/code-review/greptile-config
- `greptile-ai-review-security`: https://www.greptile.com/docs/code-review/greptile-config-reference
- `coderabbit-ai-review-security`: https://docs.coderabbit.ai/tools/index
- `coderabbit-ai-review-security`: https://docs.coderabbit.ai/tools/list
- `coderabbit-ai-review-security`: https://docs.coderabbit.ai/reference/tools-reference
- `coderabbit-ai-review-security`: https://www.coderabbit.ai/blog/our-security-posture-how-we-safeguard-your-repositories
- `coderabbit-ai-review-security`: https://www.coderabbit.ai/blog/our-response-to-the-january-2025-kudelski-security-vulnerability-disclosure-action-and-continuous-improvement
- `coderabbit-ai-review-security`: https://www.coderabbit.ai/privacy-policy

## Source Admission Rules

- Add sources only when they improve a high-risk vital, evidence gate, or authoritative currentness.
- Prefer primary sources from official maintainers; quarantine vendor checklists until they add a concrete emerging threat or verifier.
- Keep long source text out of `SKILL.md`; add links and distilled activation rules here.
- If a source mainly teaches general coding hygiene, style, ordinary testing, or maintainability, reject it for this skill and route to `code-hygiene-compounder`.
- Vendor AI-reviewer references are Tier D. Use them to generate questions for AI reviewer/toolchain vitals, then verify against local config, contracts, logs, and official standards.
- Pair Tier D vendor/practitioner sources with Tier A/B sources unless the question is purely vendor configuration.
- Do not preload every possible legal, medical, financial, tax, benefits, hiring, housing, or safety authority. For high-trust domain advice, browse or read the current official domain source during the run and record its checked date.
- `owasp-top10` and `mitre-cwe-top25` are intentionally not preset defaults. Select them explicitly only after a broad web-app vital or validated weakness path exists, such as with `--activation broad_web_app_vital` or `--activation validated_software_weakness_on_vital_path`.

## Rejected Or Deferred Sources

These may be useful elsewhere, but they are not part of Grill's active corpus unless a future catastrophic vital proves a specific gap:

| Source family | Default routing | Why not active here |
|---|---|---|
| Google Engineering Practices, Testing Blog, style guides | `code-hygiene-compounder` | Broad code review, testing, readability, and maintainability. |
| Python docs, packaging/testing docs, language style guides | `code-hygiene-compounder` | Language hygiene unless a specific vital path depends on language/runtime behavior. |
| WCAG/accessibility guidance | `code-hygiene-compounder` or product review | Important, but usually not catastrophic-system-vital evidence unless tied to high-trust or destructive-action harm. |
| OpenTelemetry/logging design guides | `code-hygiene-compounder` | Observability hygiene unless evidence-plane integrity or sensitive-log leakage is the vital. |
| SLSA/OpenSSF Scorecard | Consider only after NIST SSDF/CISA are insufficient | Useful for supply-chain depth, but defaulting to them risks duplicating broad repo-security hygiene. |
| General AI code-review checklists | Reject or route to Code Hygiene | They pull toward generic PR review rather than catastrophic surface mapping. |
