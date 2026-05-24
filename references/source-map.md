# Source Map

Use this file to remember where the skill's rules came from. Do not load this unless source lineage matters. For active source selection, freshness rules, and authoritative links, use `source-registry.md` and `source-weights.json`.

## Local Skill Lineage

- `grill-me`: one question at a time; inspect code if code can answer.
- `grill-with-docs`: challenge against existing domain language and docs; update docs only when approved and useful.
- Superpowers `brainstorming`: design before implementation; do not scaffold before approval.
- Great Code Hygiene: evidence-first reporting, smallest viable change, verification before completion, source packs outside the main skill body.
- Karpathy `autoresearch`: bounded loop, fixed metric, keep/discard, simplicity criterion.
- Udit `autoresearch`: bounded default iteration, security mode, structured reports.
- AutoResearchClaw: human-in-the-loop gates for high-impact stages.
- Greptile and CodeRabbit: AI reviewer/toolchain security patterns only; vendor/practitioner sources are Tier D leads, not authorities.
- mukul975/Anthropic-Cybersecurity-Skills: community/practitioner inspiration for ransomware recovery, cloud object storage, Kubernetes/RBAC, cloud IAM/PIM, endpoint/EDR evidence, mobile local storage/MAM, IaC scanners, API BOLA/IDOR/GraphQL cost paths, forensics, and honeytoken/canary detection prompts; not an authoritative source.
- mukul975/Privacy-Data-Protection-Skills: community/practitioner inspiration for DSAR/SAR, DPIA, ROPA, retention, consent withdrawal, cross-border transfers, breach notification, vendor/subprocessor, children, employee, biometric, and AI privacy governance routing; not legal advice or a compliance source.

## Private Note Themes Used During Design

Private design notes influenced the skill, but exact local note paths are intentionally not published. The durable themes were:

- harness structure, raw traces, ablation, and subtraction principles
- filesystem, network, process, secrets, and persistence isolation
- tool registries, schema-vs-implementation boundaries, and avoiding broad generic tools
- sandbox examples such as Docker, Firecracker, gVisor, and seccomp
- action risk classes, AFK boundaries, credential-as-data, and MCP/tool permission gates
- data minimization, log allowlists, and customer-data gates
- wallet/key anti-patterns, signing boundaries, human-controlled capital, and hard risk gates
- registry/gateway/owner/audit models for tools
- NIST-style risk loops, OWASP-style checks, layered controls, and high-trust output gates
- terminal hosts, hooks, auto-registered tools, billing gates, secrets gates, and deployment gates

## External Standards And Anchors

These were the original anchors used during design. They are retained for lineage, not as the active source registry.

| Source | Use In This Skill |
|---|---|
| NIST AI Risk Management Framework: https://www.nist.gov/itl/ai-risk-management-framework | Govern, Map, Measure, Manage risk framing for AI workflows. |
| NIST AI RMF Core: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/ | Concrete AI RMF core functions and categories. |
| OWASP Top 10 for LLM/GenAI Apps: https://owasp.org/www-project-top-10-for-large-language-model-applications/ | Prompt injection, sensitive information disclosure, excessive agency, supply chain, vector weaknesses, misinformation, unbounded consumption. |
| OWASP ASVS: https://owasp.org/www-project-application-security-verification-standard/ | Web-app verification baseline for auth, session, access control, validation, logging, and data protection. |
| NIST SSDF SP 800-218: https://csrc.nist.gov/pubs/sp/800/218/final | Secure software development practices and vulnerability reduction. |
| CISA Secure by Design: https://www.cisa.gov/securebydesign | Secure-by-design accountability, safe defaults, and manufacturer responsibility. |
| MITRE CWE Top 25: https://cwe.mitre.org/top25/ | Common high-impact software weakness classes. |
| MITRE ATLAS: https://atlas.mitre.org/ | Adversarial tactics and techniques for AI-enabled systems. |
| NIST Privacy Framework: https://www.nist.gov/privacy-framework | Privacy risk functions and data handling framing. |
| FTC Data Security: https://www.ftc.gov/business-guidance/privacy-security/data-security | Business data security guidance. |
| FTC Protecting Personal Information: https://www.ftc.gov/business-guidance/resources/protecting-personal-information-guide-business | Collect only what is needed, protect it, dispose securely. |
| PCI DSS: https://www.pcisecuritystandards.org/standards/pci-dss/ | Payment account data baseline when storing, processing, or transmitting cardholder data. |
| Greptile security/configuration docs | Vendor/practitioner questions for repo indexing, embeddings, retention, training settings, and scoped review rules. |
| CodeRabbit security/tool docs | Vendor/practitioner questions for sandboxed analyzer execution, short-lived tokens, customer isolation, and reviewer mutation authority. |

## Standards Use Rules

- Do not claim certification or compliance from a quick review.
- Use standards to select evidence gates and questions.
- Use primary/official sources when facts might be current.
- For legal, financial, medical, security, or regulated claims, verify current official sources before final advice.
- Use `source-registry.md` for current source activation and checked-date reporting.
