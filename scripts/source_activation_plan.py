#!/usr/bin/env python3
"""Create a conditional source activation plan for Grill for Vitals."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PRESETS = {
    "ai-review-toolchain": {
        "description": "AI code reviewers, PR bots, hosted repo analysis, analyzer execution, and reviewer mutation authority.",
        "activations": {
            "agentic_workflow",
            "agent_skill_or_plugin",
            "privileged_build_deploy_or_supplier",
            "product_or_vendor_risk",
            "ai_code_review_tool_or_skill_design",
            "ai_code_review_tool_or_analyzer_execution",
        },
        "scopes": {"ai-code-review", "sandbox", "third-party-analyzers"},
    },
    "high-trust-output": {
        "description": "AI outputs users may rely on for health, legal, financial, tax, compliance, benefits, housing, employment, safety, or official decisions.",
        "activations": {"ai_or_high_trust", "genai_or_llm"},
        "scopes": {"ai-risk", "high-trust-ai", "generative-ai", "predeployment-testing", "incident-disclosure"},
    },
    "agentic-llm": {
        "description": "LLM apps, RAG, tool-using agents, agent skills/plugins, high-trust AI, and AI attack paths.",
        "activations": {
            "ai_or_high_trust",
            "genai_or_llm",
            "llm_app",
            "agentic_workflow",
            "agent_skill_or_plugin",
            "ai_attack_path",
        },
        "scopes": {"llm", "agent-governance", "prompt-injection"},
    },
    "mcp-tooling": {
        "description": "MCP servers, clients, gateways, OAuth-backed tools, local server installs, and MCP tool metadata boundaries.",
        "activations": {"mcp_tooling"},
        "scopes": {"mcp-security", "mcp-authorization", "oauth", "local-mcp-server", "tool-gateway", "scope-minimization"},
    },
    "identity-auth": {
        "description": "High-risk login, account recovery, federation, sessions, API authorization, admin, and tenant isolation.",
        "activations": {"high_risk_identity_or_auth", "web_auth_or_tenancy", "api_or_business_flow"},
        "scopes": {"digital-identity", "web-auth", "sessions", "api-authz"},
    },
    "control-plane-supply-chain": {
        "description": "Secrets, signing, privileged CI/CD, deploy, release, package publish, and supplier/product accountability paths.",
        "activations": {"privileged_build_deploy_or_supplier", "product_or_vendor_risk"},
        "scopes": {"secure-sdlc", "supply-chain", "secure-defaults", "product-accountability"},
    },
    "privacy-customer-content": {
        "description": "PII, customer content, prompts, uploads, model I/O, retention, disposal, and vendor access.",
        "activations": {"pii_or_customer_content", "us_business_pii"},
        "scopes": {"privacy-risk", "pii", "personal-information", "retention"},
    },
    "financial-customer-data": {
        "description": "Customer financial information, financial records, GLBA/Safeguards questions, and financial-service processors.",
        "activations": {"financial_customer_information", "pii_or_customer_content", "us_business_pii"},
        "scopes": {"customer-financial-information", "financial-records", "privacy-risk", "personal-information"},
    },
    "health-ephi": {
        "description": "ePHI, health records, covered-entity/business-associate questions, and HIPAA Security Rule mapping.",
        "activations": {"health_or_ephi", "pii_or_customer_content"},
        "scopes": {"ephi", "health-data", "privacy-risk"},
    },
    "child-privacy": {
        "description": "Child-directed services or known under-13 personal information handling.",
        "activations": {"child_directed_or_under13_data", "pii_or_customer_content"},
        "scopes": {"children", "child-privacy", "privacy-risk"},
    },
    "biometric-identity": {
        "description": "Biometric identifiers or biometric identity checks tied to access, money, or high-trust decisions.",
        "activations": {"biometric_information", "high_risk_identity_or_auth", "pii_or_customer_content"},
        "scopes": {"biometric-data", "digital-identity", "privacy-risk"},
    },
    "child-biometric": {
        "description": "Combined child privacy and biometric identity handling.",
        "activations": {"child_directed_or_under13_data", "biometric_information", "high_risk_identity_or_auth", "pii_or_customer_content"},
        "scopes": {"children", "biometric-data", "digital-identity", "privacy-risk"},
    },
    "payments-cardholder": {
        "description": "Cardholder data, payment account data, and payment-environment scope questions.",
        "activations": {"cardholder_or_payment_account_data"},
        "scopes": {"cardholder-data", "payment-account-data", "cde"},
    },
    "sanctions-export": {
        "description": "Virtual currency, sanctions exposure, cross-border finance, encryption software, and export-controlled technology.",
        "activations": {"sanctions_or_cross_border_finance", "export_control_or_encryption_software"},
        "scopes": {"sanctions", "export-control", "virtual-currency"},
    },
    "customer-trust-soc2": {
        "description": "SOC 2 customer commitments, trust services criteria, and audit-readiness questions without claiming readiness.",
        "activations": {"soc2_or_customer_trust_commitment"},
        "scopes": {"soc2", "customer-commitments", "security", "availability", "confidentiality", "privacy"},
    },
    "incident-recovery": {
        "description": "Incident readiness, breach response, evidence-plane integrity, recovery, and executive risk governance.",
        "activations": {"incident_or_program_risk", "incident_response"},
        "scopes": {"risk-governance", "incident-readiness", "incident-response", "evidence-plane", "recovery"},
    },
    "safety-ot": {
        "description": "Operational technology, industrial or IoT control, physical actuation, and safety-critical agent actions.",
        "activations": {"operational_technology_or_safety_critical", "incident_or_program_risk"},
        "scopes": {"operational-technology", "industrial-control", "physical-safety", "ot-security"},
    },
    "cost-availability": {
        "description": "API cost spikes, retry or fanout cascades, resource consumption, outage, and denial-of-wallet paths.",
        "activations": {"api_or_business_flow", "incident_or_program_risk"},
        "scopes": {"resource-consumption", "recoverability"},
    },
    "payments-sanctions-export": {
        "description": "Combined cardholder/payment data plus sanctions, virtual-currency, cross-border finance, or export-control exposure.",
        "activations": {
            "cardholder_or_payment_account_data",
            "sanctions_or_cross_border_finance",
            "export_control_or_encryption_software",
        },
        "scopes": {"cardholder-data", "payment-account-data", "sanctions", "export-control", "virtual-currency"},
    },
    "federal-defense": {
        "description": "FedRAMP/federal cloud, FCI/CUI, DoD/DIB, and federal incident-response evidence surfaces.",
        "activations": {"federal_cloud", "defense_fci_or_cui", "incident_response"},
        "scopes": {"federal-cloud", "fci", "cui", "incident-response"},
    },
}

TRIGGER_TAXONOMY = [
    {
        "id": "identity-tenancy",
        "vital": "Identity/auth/sessions/tenancy",
        "signals": ["login", "session", "password reset", "recovery", "sso", "oauth", "saml", "passkey", "webauthn", "mfa", "mfa reset", "admin account", "admin api", "admin console", "admin role", "owner role", "payroll admin", "admin session", "compromised admin", "impersonate", "support impersonate", "organization invite", "org invite", "rbac", "rls", "row level security", "tenant", "tenant_id", "account takeover", "api authz", "bola", "idor", "bfla", "object-level authorization", "function-level authorization", "per-object authorization", "tenant object id"],
        "presets": ["identity-auth"],
        "question": "Does this path unlock admin, tenant data, money, regulated data, or production authority?",
    },
    {
        "id": "control-plane-supply-chain",
        "vital": "Secrets/control plane and supply chain/build/deploy",
        "signals": ["secret", "token", "deploy key", "private key", "github app private key", "github app installation token", "service account", "service account token", "service account key", "service principal", "kms key", "kms signing key", "ci/cd", "ci", "oidc", "github action", "signing", "release", "package publish", "npm publish", "artifact", "dependency execution", "privileged workflow", "terraform", "terraform plan", "tfplan", "cloudformation", "infrastructure as code", "iac scan", "checkov", "tfsec", "terrascan", "kics", "opa policy", "rego policy", "kubernetes", "k8s", "kubeconfig", "kubernetes manifest", "helm chart", "clusterrolebinding", "cluster-admin", "pod exec", "pods/exec", "pods/attach", "privileged pod", "kubernetes audit", "aws iam", "gcp iam", "iam role", "iam policy", "iam:passrole", "passrole", "sts:assumerole", "assumerole", "createfunction", "lambda createfunction", "roles/owner", "roles/editor", "cloud admin", "cloud credential", "access key", "entra role", "azure role", "global administrator", "privileged identity management", "pim", "mdm", "mam", "mobile application management", "intune app protection", "selective wipe", "production database", "prod database", "container registry", "prod image", "protected branches", "install hook", "startup command", "skill lockfile", "marketplace install", "one-click mcp configuration", "local mcp server install"],
        "presets": ["control-plane-supply-chain"],
        "question": "Can this credential or workflow deploy, sign, publish, read tenants, delete, or administer identity?",
    },
    {
        "id": "pii-customer-content",
        "vital": "PII/customer content",
        "signals": ["pii", "personal data", "personal information", "ssn", "social security", "address", "email", "phone", "phone number", "ip address", "cookie identifier", "geolocation", "birth date", "birth dates", "prompt log", "prompt logs", "raw prompt", "raw prompts", "user prompt", "user prompts", "customer prompt", "customer prompts", "transcript", "transcripts", "chat message", "chat messages", "chat logs", "support chat logs", "recording", "recordings", "support recordings", "upload", "uploads", "uploaded", "attachment", "attachments", "document attachment", "document attachments", "customer file", "customer invoice", "customer's invoice", "private docs", "legal docs", "legal records", "hr records", "url", "s3 bucket", "gcs bucket", "azure blob", "object storage", "signed url", "public bucket", "bucket policy", "bucket acl", "block public access", "cloudtrail data events", "getobject", "listbucket", "mobile local storage", "sharedpreferences", "keychain", "keystore", "sqlite database", "app sandbox", "unmanaged app", "personal cloud backup", "analytics event", "customer analytics", "analytics export", "retention", "retention schedule", "retention period", "storage limitation", "deletion trigger", "dsar", "subject access", "subject access request", "access request", "sar", "data subject request", "data subject rights", "ropa", "record of processing", "processing purpose", "recipient categories", "lawful basis", "purpose limitation", "consent withdrawal", "dpia", "privacy impact assessment", "data protection impact assessment", "cross-border transfer", "third-country transfer", "transfer impact assessment", "tia", "scc", "standard contractual clauses", "bcr", "adequacy", "subprocessor", "sub-processor", "dpa", "data processing agreement", "vendor privacy due diligence", "employee monitoring", "workplace monitoring", "data deletion", "deletion request", "export request", "vendor processor", "external processor"],
        "presets": ["privacy-customer-content"],
        "question": "What sensitive data class would be exposed in a breach?",
    },
    {
        "id": "financial-customer-data",
        "vital": "PII/customer content and financial records",
        "signals": ["bank statement", "bank account", "ach", "credit report", "loan", "lender note", "underwriting", "brokerage", "trading", "wire transfer", "wire instructions", "financial record", "customer financial information", "paystub", "tax return", "income verification", "1099", "payroll record", "payroll records", "account holdings", "glba"],
        "presets": ["financial-customer-data"],
        "question": "Is this customer financial information or only ordinary billing metadata?",
    },
    {
        "id": "health-ephi",
        "vital": "PII/customer content and high-trust health output",
        "signals": ["patient", "diagnosis", "treatment", "medical record", "medical claim", "medical claims", "claims adjudication", "fhir", "lab result", "lab results", "prescription", "medication history", "mental health", "therapist", "ephi", "phi", "hipaa", "ehr", "healthcare", "covered entity", "business associate"],
        "presets": ["health-ephi"],
        "question": "Is the system a covered entity/business associate workflow or otherwise handling health data?",
    },
    {
        "id": "child-privacy",
        "vital": "PII/customer content and child data",
        "signals": ["child", "under 13", "underage", "minor", "minors", "kids", "k-12", "student", "school", "school district", "classroom", "parental consent", "coppa", "age gate", "age gating", "age verification", "parental access", "child deletion", "children deletion", "child profiling", "youth data", "aadc", "behavioral advertising to children"],
        "presets": ["child-privacy"],
        "question": "Is the product child-directed or knowingly collecting under-13 data?",
    },
    {
        "id": "biometric-identity",
        "vital": "PII/customer content and identity",
        "signals": ["face recognition", "fingerprint", "voiceprint", "voiceprints", "voice authentication", "voice auth", "voice id", "biometric", "liveness", "selfie", "kyc", "identity verification", "palm vein", "palm", "retina", "faceprint"],
        "presets": ["biometric-identity"],
        "question": "Is biometric data tied to access, money, eligibility, or high-trust decisions?",
    },
    {
        "id": "payments-cardholder",
        "vital": "Money/billing/trading/procurement",
        "signals": ["cardholder", "cardholder name", "pan", "full pan", "cvv", "credit card", "card number", "card integration", "payment card", "card payment", "card payments", "payment account", "payment token", "card storage", "payment environment", "payment form", "checkout", "tokenization", "hosted provider", "psp", "vaulting", "card cashout", "card payout"],
        "presets": ["payments-cardholder"],
        "question": "Does cardholder/payment-account data enter the app or only the hosted provider?",
    },
    {
        "id": "sanctions-export",
        "vital": "Money/billing/trading/procurement and controlled technology",
        "signals": ["crypto", "virtual currency", "stablecoin", "x402", "micropayment", "agent payment", "keyless payment", "cross-border finance", "cross border finance", "cashout", "blocked person", "blocked wallet", "ofac", "sanctioned", "sanctioned country", "sanctioned countries", "sanctioned jurisdiction", "encryption export", "encryption sdk", "encryption library", "encryption software", "ear", "itar", "export controlled", "foreign customer", "foreign customers", "overseas customer", "controlled technology"],
        "presets": ["sanctions-export"],
        "question": "Is there international finance, virtual currency, encryption software, or controlled technology transfer?",
    },
    {
        "id": "agentic-llm",
        "vital": "Agent/tool/MCP/browser/shell and high-trust output",
        "signals": ["llm", "rag", "retrieved", "retrieved docs", "summarizer", "summary", "summarized by agent", "chatbot", "prompt injection", "function calling", "tool use", "tool calls", "browser tool", "browser automation", "shell tool", "agent tool registry", "agent tool catalog", "agent tool manifest", "agent tool schema", "agent tool description", "agent tool metadata", "tool poisoning", "tool rug pull", "tool shadowing", "agent skill", "agent plugin", "skills registry", "skill marketplace", "plugin marketplace", "permission manifest", "memory", "agent goal", "ai agent", "workflow agent", "autonomous workflow", "control agent", "agent changes", "agent safe", "from agent", "ai assistant", "ai decides", "model output", "model recommends", "model ranks", "model-mediated", "llm output", "memorization", "memorisation", "pii leakage", "prompt extraction", "training data extraction"],
        "presets": ["agentic-llm"],
        "question": "Can the model influence tools, private data, decisions, sends, or state changes?",
    },
    {
        "id": "mcp-tooling",
        "vital": "Agent/tool/MCP/browser/shell",
        "signals": ["mcp", "mcp server", "local mcp server", "mcp gateway", "mcp client", "mcp tool", "mcp tool catalog", "mcp tool schema", "mcp tool description", "mcp authorization", "mcp oauth", "mcp session", "remote mcp server"],
        "presets": ["agentic-llm", "mcp-tooling"],
        "question": "Does this MCP surface expose local execution, remote APIs, OAuth tokens, mutable tools, or model-visible tool metadata?",
    },
    {
        "id": "ai-review-toolchain",
        "vital": "Agent/tool/MCP/browser/shell and supply chain/build/deploy",
        "signals": ["pr bot", "pull request bot", "ai reviewer", "reviewer app", "greptile", "coderabbit", "analyzer", "rubocop", "semgrep", "trufflehog", "presidio", "linter", "linters", "one-click fix", "one click fixes", "review sandbox", "review worker", "third-party analyzer", "repo index", "related repositories", "code embeddings", "vector embeddings", "customer code cache", "support access", "training opt-out", "short lived github token", "short-lived github token", "short lived repo token", "short-lived repo token"],
        "presets": ["ai-review-toolchain"],
        "question": "Does the tool ingest source, execute analyzers, receive tokens, cache indexes, or mutate PRs?",
    },
    {
        "id": "high-trust-output",
        "vital": "High-trust outputs",
        "signals": ["medical advice", "legal advice", "tax advice", "tax filing", "irs", "benefits", "unemployment benefits", "eligibility decision", "government filing", "immigration filing", "investment advice", "loan approval", "employment screening", "denial rationale", "housing", "hiring", "compliance", "official policy", "safety guidance", "dosage setting", "automated decision", "automated decision-making", "profiling", "significant effects", "human oversight", "human intervention", "contest decision", "contest automated decision", "ai act high-risk"],
        "presets": ["high-trust-output"],
        "question": "Which current official domain source corpus governs the output?",
    },
    {
        "id": "safety-ot",
        "vital": "External effects and safety-critical operations",
        "signals": ["door", "doors", "lab equipment", "device command", "industrial control", "scada", "plc", "setpoint", "iot", "actuator", "robot", "vehicle", "drone", "safety alarm", "chemical pump", "medical device", "dosage setting", "hvac", "cleanroom", "damper", "dampers"],
        "presets": ["safety-ot"],
        "question": "Can software alter physical state or safety-critical operations?",
    },
    {
        "id": "incident-recovery",
        "vital": "Logs/audit/evidence and incident recovery",
        "signals": ["breach", "incident", "timeline", "audit log", "audit trail", "siem", "evidence store", "forensics", "chain of custody", "postmortem", "rto", "rpo", "incident recovery", "disaster recovery", "recovery plan", "restore", "backup restore", "restore test", "ransomware", "ransom note", "mass file encryption", "encrypted production data", "offline backup", "immutable backup", "air-gapped backup", "backup integrity", "hash manifest", "backup corruption", "breach notification", "72-hour", "processor breach notice", "honeytoken", "honeytokens", "canary token", "canary document", "document beacon", "edr", "endpoint telemetry", "falcon sensor", "crowdstrike", "osquery", "endpoint detection", "endpoint dlp", "endpoint forensics", "investigation record"],
        "presets": ["incident-recovery"],
        "question": "Can the actor under review edit or delete the evidence used to investigate it?",
    },
    {
        "id": "cost-availability",
        "vital": "Cost/availability/runaway loops",
        "signals": ["retry", "retries", "fanout", "job queue", "queue backlog", "queue fanout", "queue retry", "background job", "model spend", "rate limit", "rate limit bypass", "outage", "denial-of-wallet", "denial of wallet", "cost loop", "recursive", "quota exhausted", "cloud bill", "bill spike", "infinite retry", "burn tokens", "token burn", "pay api", "pay apis", "paid api", "api payment", "api spend", "pay-per-call tool", "usage-metered tool", "micropayment loop", "x402 loop", "graphql depth", "graphql query complexity", "query complexity", "depth limit", "recursive query", "nested query", "api enumeration"],
        "presets": ["cost-availability"],
        "question": "Can this loop spend money, exhaust quota, or take production down?",
    },
    {
        "id": "customer-trust-soc2",
        "vital": "Customer trust commitments",
        "signals": ["soc 2", "soc2", "soc readiness", "trust services", "customer trust", "trust center", "availability commitment", "confidentiality commitment", "sla", "rto", "rpo", "security addendum", "customer security addendum"],
        "presets": ["customer-trust-soc2"],
        "question": "Is this a customer commitment/audit evidence question rather than a readiness claim?",
    },
    {
        "id": "federal-defense",
        "vital": "Federal/defense data and cloud authorization",
        "signals": ["fedramp", "federal cloud", "cmmc", "dod", "dib", "fci", "cui", "800-171", "800-53", "itar", "cjis", "fouo", "law enforcement records", "export controlled technical data"],
        "presets": ["federal-defense"],
        "question": "Is the system handling federal cloud authorization, FCI, CUI, or defense supplier obligations?",
    },
]

TIER_RANK = {
    "A": 0,
    "B": 1,
    "B-provisional": 2,
    "C": 3,
    "D": 4,
}

PLAN_RULES = [
    "Use sources only after a catastrophic vital activates them.",
    "Verify listed URLs before version-specific or high-stakes claims.",
    "Prefer Tier A/B official or standards sources over Tier D vendor/practitioner sources.",
    "Pair Tier D vendor/practitioner sources with Tier A/B sources unless the question is purely vendor configuration.",
    "Verify current official sources before version-specific or high-stakes claims.",
    "Label draft, initial-public-draft, concept, provisional, academic, vault, and vendor sources as weaker evidence.",
    "Do not claim compliance or readiness from this plan.",
]

SUPPRESS_TRIGGER_PHRASES = {
    "identity-tenancy": ["no tenant data", "no tenant data path", "without tenant data", "unit test only"],
    "control-plane-supply-chain": ["payment token", "pagination token", "csrf token", "docs mention prod image naming convention", "kubernetes glossary typo", "kubernetes glossary", "sample terraform", "terraform tutorial", "terraform docs", "checkov docs", "tfsec documentation", "iac scanner docs only", "iam glossary", "pim docs only", "intune docs only", "mdm policy docs only"],
    "pii-customer-content": ["no real pii", "mock pii", "fake pii", "sample pii", "fake data", "sample fixture", "privacy policy typo", "privacy policy copy edit", "privacy glossary", "dpia template docs only", "ropa template docs only", "consent button css without tracking change", "mobile storage docs only"],
    "health-ephi": ["sample patient fixture in docs", "generic docs with fake data", "patient fixture in docs", "example uses fake data in docs"],
    "child-privacy": ["no student data", "internal hr demo", "employee roster"],
    "payments-cardholder": ["fake card", "mock checkout", "storybook"],
    "cost-availability": ["no production queue", "unit tests for retry", "local suite", "graphql schema docs example only", "graphql query docs only"],
    "agentic-llm": ["storybook mock", "mock chatbot", "unit tests for chatbot", "no model call", "canned messages", "internal lunch menu", "css specificity examples in docs", "llm glossary docs"],
    "ai-review-toolchain": ["without repo tokens or customer data", "document coderabbit setup steps", "without running analyzer or pr bot", "semgrep rule documentation"],
    "sanctions-export": ["glossary page copy edit", "without transaction flow"],
    "customer-trust-soc2": ["no customer commitment", "without security claims", "trust center link text without security claims"],
    "incident-recovery": ["no customer commitment", "glossary docs", "edr docs only", "falcon sensor docs only"],
    "safety-ot": ["cleanroom icon", "static facilities dashboard mockup", "marketing page copy without product claims"],
    "federal-defense": ["example uses fake data in docs", "fake data in docs"],
    "high-trust-output": ["without product claims", "marketing page without product claims", "without claims", "static marketing page without claims"],
}


def load_weights(skill_root: Path) -> list[dict]:
    path = skill_root / "references" / "source-weights.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("weights", [])


def load_links(skill_root: Path) -> dict[str, list[str]]:
    path = skill_root / "references" / "source-registry.md"
    links: dict[str, list[str]] = {}
    in_links = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line == "## Current Source Links":
            in_links = True
            continue
        if in_links and line.startswith("## "):
            break
        if not in_links or not line.startswith("- `"):
            continue
        source_id, rest = line[3:].split("`:", 1)
        links.setdefault(source_id, []).append(rest.strip())
    return links


def matches(entry: dict, activations: set[str], scopes: set[str], tiers: set[str], include_all: bool) -> bool:
    if include_all:
        return True
    if activations and entry.get("activation") in activations:
        return True
    if tiers and entry.get("tier") in tiers:
        return True
    entry_scopes = set(entry.get("scope", []))
    if scopes and entry_scopes.intersection(scopes):
        return True
    return False


def select_sources(entries: list[dict], activations: set[str], scopes: set[str], tiers: set[str], include_all: bool) -> list[dict]:
    selected = [
        entry
        for entry in entries
        if matches(entry, activations, scopes, tiers, include_all)
    ]
    selected.sort(key=lambda item: (TIER_RANK.get(item.get("tier", ""), 99), -float(item.get("default_weight", 0)), item.get("id", "")))
    return selected


def preset_query(preset_names: list[str]) -> tuple[set[str], set[str]]:
    activations: set[str] = set()
    scopes: set[str] = set()
    for preset in preset_names:
        activations.update(PRESETS[preset]["activations"])
        scopes.update(PRESETS[preset]["scopes"])
    return activations, scopes


def signal_matches(surface_text: str, signal: str) -> bool:
    pattern = r"(?<![a-z0-9])" + re.escape(signal.lower()) + r"(?![a-z0-9])"
    return re.search(pattern, surface_text) is not None


def infer_trigger_presets(surfaces: list[str]) -> tuple[list[dict], list[str]]:
    surface_text = " ".join(surfaces).lower()
    matched: list[dict] = []
    presets: list[str] = []
    if not surface_text.strip():
        return matched, presets

    for trigger in TRIGGER_TAXONOMY:
        if any(phrase in surface_text for phrase in SUPPRESS_TRIGGER_PHRASES.get(trigger["id"], [])):
            continue
        hits = [signal for signal in trigger["signals"] if signal_matches(surface_text, signal)]
        if not hits:
            continue
        matched.append(
            {
                "id": trigger["id"],
                "vital": trigger["vital"],
                "signals": hits,
                "presets": trigger["presets"],
                "question": trigger["question"],
            }
        )
        presets.extend(trigger["presets"])

    preset_set = set(presets)
    if {"payments-cardholder", "sanctions-export"}.issubset(preset_set):
        preset_set.difference_update({"payments-cardholder", "sanctions-export"})
        preset_set.add("payments-sanctions-export")
    if {"child-privacy", "biometric-identity"}.issubset(preset_set):
        preset_set.difference_update({"child-privacy", "biometric-identity"})
        preset_set.add("child-biometric")

    return matched, sorted(preset_set)


def self_test(entries: list[dict], links: dict[str, list[str]]) -> int:
    covered_source_ids: set[str] = set()
    for preset in sorted(PRESETS):
        if not PRESETS[preset].get("description"):
            raise SystemExit(f"preset lacks description: {preset}")
        activations, scopes = preset_query([preset])
        sources = select_sources(entries, activations, scopes, set(), False)
        if not sources:
            raise SystemExit(f"empty preset: {preset}")
        ids = {source["id"] for source in sources}
        covered_source_ids.update(ids)
        tiers = {source["tier"] for source in sources}
        missing_links = sorted(source_id for source_id in ids if not links.get(source_id))
        if missing_links:
            raise SystemExit(f"preset {preset} returned sources without URLs: {', '.join(missing_links)}")
        if preset == "federal-defense" and any(source_id.startswith(("coderabbit", "greptile")) for source_id in ids):
            raise SystemExit("federal-defense leaked vendor AI-reviewer source")
        if preset == "identity-auth" and "owasp-top10" in ids:
            raise SystemExit("identity-auth should use ASVS/API Top 10, not broad OWASP Top 10")
        if preset == "ai-review-toolchain" and not ({"A", "B"}.intersection(tiers) and "D" in tiers):
            raise SystemExit("ai-review-toolchain must include Tier A/B and Tier D sources")
        if preset == "mcp-tooling" and ids != {"mcp-security-best-practices"}:
            raise SystemExit("mcp-tooling should only return MCP security best practices")
        if preset == "high-trust-output" and ids != {"nist-ai-rmf", "nist-ai-600-1"}:
            raise SystemExit("high-trust-output should only return NIST AI RMF and NIST AI 600-1")
        if preset == "control-plane-supply-chain" and ids != {"nist-ssdf", "cisa-secure-by-design"}:
            raise SystemExit("control-plane-supply-chain should only return NIST SSDF and CISA Secure by Design")
        if preset == "privacy-customer-content":
            if ids != {"nist-privacy-framework", "ftc-protecting-pii"}:
                raise SystemExit("privacy-customer-content should only return NIST Privacy Framework and FTC PII sources")
        if preset == "financial-customer-data" and not {"nist-privacy-framework", "ftc-protecting-pii", "ftc-glba-safeguards"}.issubset(ids):
            raise SystemExit("financial-customer-data missing privacy or GLBA source")
        if preset == "financial-customer-data" and ids != {"nist-privacy-framework", "ftc-protecting-pii", "ftc-glba-safeguards"}:
            raise SystemExit("financial-customer-data should only return privacy and GLBA sources")
        if preset == "payments-cardholder":
            if ids != {"pci-dss"}:
                raise SystemExit("payments-cardholder should only return pci-dss")
        if preset == "sanctions-export":
            if ids != {"ofac-sanctions-framework", "bis-ear-encryption"}:
                raise SystemExit("sanctions-export should only return OFAC and BIS sources")
        if preset == "customer-trust-soc2":
            if ids != {"aicpa-tsc"}:
                raise SystemExit("customer-trust-soc2 should only return aicpa-tsc")
        if preset == "incident-recovery" and not {"nist-csf-2", "nist-sp-800-61r3"}.issubset(ids):
            raise SystemExit("incident-recovery missing NIST CSF 2.0 or SP 800-61r3")
        if preset == "safety-ot" and ids != {"nist-sp-800-82r3", "nist-csf-2"}:
            raise SystemExit("safety-ot should only return NIST SP 800-82 Rev. 3 and NIST CSF")
        if preset == "cost-availability" and ids != {"owasp-api-top10", "nist-csf-2"}:
            raise SystemExit("cost-availability should only return OWASP API Top 10 and NIST CSF")
        if preset == "payments-sanctions-export":
            required = {"pci-dss", "ofac-sanctions-framework", "bis-ear-encryption"}
            if ids != required:
                raise SystemExit("payments-sanctions-export should only return PCI, OFAC, and BIS sources")
        if preset == "federal-defense":
            required = {"fedramp", "cmmc", "nist-sp-800-171r3", "nist-sp-800-53r5"}
            missing = sorted(required - ids)
            if missing:
                raise SystemExit(f"federal-defense missing required source: {', '.join(missing)}")
        if preset == "health-ephi" and ids != {"hhs-hipaa-security", "nist-sp-800-66r2", "nist-privacy-framework"}:
            raise SystemExit("health-ephi should only return HIPAA Security Rule and privacy sources")
        if preset == "child-privacy" and ids != {"ftc-coppa", "nist-privacy-framework"}:
            raise SystemExit("child-privacy should only return COPPA and privacy sources")
        if preset == "biometric-identity" and ids != {"ftc-biometric-policy", "nist-sp-800-63-4", "nist-privacy-framework"}:
            raise SystemExit("biometric-identity should only return biometric, identity, and privacy sources")
        if preset == "child-biometric" and ids != {"ftc-coppa", "ftc-biometric-policy", "nist-sp-800-63-4", "nist-privacy-framework"}:
            raise SystemExit("child-biometric should only return COPPA, biometric, identity, and privacy sources")
    allowed_unpreset = {"mitre-cwe-top25", "owasp-top10"}
    all_source_ids = {entry["id"] for entry in entries}
    unpreset = all_source_ids - covered_source_ids
    if unpreset != allowed_unpreset:
        raise SystemExit(
            "unexpected unpreset sources; expected "
            + ", ".join(sorted(allowed_unpreset))
            + " but found "
            + ", ".join(sorted(unpreset))
        )
    for trigger in TRIGGER_TAXONOMY:
        for preset in trigger["presets"]:
            if preset not in PRESETS:
                raise SystemExit(f"trigger taxonomy references unknown preset: {trigger['id']} -> {preset}")
    trigger_cases = {
        "stripe cardholder data": {"payments-cardholder"},
        "crypto cross-border encryption export": {"sanctions-export"},
        "patient pdf summarized by llm": {"health-ephi", "agentic-llm"},
        "agent unlocks doors with llm tool use": {"agentic-llm", "safety-ot"},
        "child face recognition login": {"child-biometric"},
        "pr bot runs analyzer and one-click fix": {"ai-review-toolchain"},
        "tax advice from retrieved sources": {"high-trust-output"},
        "cui fedramp federal cloud": {"federal-defense"},
        "public s3 bucket exposes customer invoice": {"privacy-customer-content"},
        "kubernetes clusterrolebinding gives service account cluster-admin": {"control-plane-supply-chain"},
        "ransomware restore test fails backup integrity": {"incident-recovery"},
        "graphql query complexity nested query exhausts database": {"cost-availability"},
        "aws iam passrole lets service account create admin lambda": {"control-plane-supply-chain"},
        "edr endpoint telemetry disabled during breach": {"incident-recovery"},
        "mobile sharedpreferences stores ssn and auth token": {"privacy-customer-content", "control-plane-supply-chain"},
        "public skill marketplace installer adds scripts and install hook": {"agentic-llm", "control-plane-supply-chain"},
        "one-click mcp configuration runs local mcp server startup command": {"agentic-llm", "mcp-tooling", "control-plane-supply-chain"},
        "mcp tool poisoning hides delete behavior in tool description": {"agentic-llm", "mcp-tooling"},
        "agent uses x402 keyless payment connector with micropayment loop": {"sanctions-export", "cost-availability"},
        "one-click mcp configuration starts a local server that can delete records and pay apis": {"agentic-llm", "mcp-tooling", "control-plane-supply-chain", "cost-availability"},
        "ai reviewer support access can view customer code cache and vector embeddings": {"ai-review-toolchain"},
    }
    for surface, expected_presets in trigger_cases.items():
        _, inferred = infer_trigger_presets([surface])
        if not expected_presets.issubset(set(inferred)):
            raise SystemExit(f"surface trigger failed for {surface}: expected {sorted(expected_presets)}, got {inferred}")
    print("SOURCE_PRESETS_OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--activation", action="append", default=[], help="Exact activation value from source-weights.json")
    parser.add_argument("--scope", action="append", default=[], help="Scope tag to match")
    parser.add_argument("--tier", action="append", default=[], help="Tier to include, such as A, B, or D")
    parser.add_argument("--preset", action="append", choices=sorted(PRESETS), default=[], help="Named vital source preset")
    parser.add_argument("--surface", action="append", default=[], help="Observed problem surface text used to infer source presets")
    parser.add_argument("--list-presets", action="store_true", help="List available presets and exit")
    parser.add_argument("--list-trigger-taxonomy", action="store_true", help="List surface-trigger taxonomy and exit")
    parser.add_argument("--self-test", action="store_true", help="Validate preset behavior and exit")
    parser.add_argument("--all", action="store_true", help="List all sources")
    parser.add_argument("--out", type=Path, help="Optional output JSON path")
    args = parser.parse_args()

    skill_root = args.skill_root.resolve()
    if args.list_presets:
        print(json.dumps({"presets": {name: PRESETS[name]["description"] for name in sorted(PRESETS)}}, indent=2))
        return 0
    if args.list_trigger_taxonomy:
        print(json.dumps({"trigger_taxonomy": TRIGGER_TAXONOMY}, indent=2))
        return 0

    entries = load_weights(skill_root)
    links = load_links(skill_root)
    if args.self_test:
        return self_test(entries, links)

    matched_triggers, inferred_presets = infer_trigger_presets(args.surface)
    activations = set(args.activation)
    scopes = set(args.scope)
    tiers = set(args.tier)
    requested_presets = sorted(set(args.preset).union(inferred_presets))
    preset_activations, preset_scopes = preset_query(requested_presets)
    activations.update(preset_activations)
    scopes.update(preset_scopes)

    entries = select_sources(entries, activations, scopes, tiers, args.all)
    for entry in entries:
        entry["urls"] = links.get(entry["id"], [])

    plan = {
        "skill_root": str(skill_root),
        "query": {
            "activation": sorted(activations),
            "scope": sorted(scopes),
            "tier": sorted(tiers),
            "preset": requested_presets,
            "surface": args.surface,
            "all": args.all,
        },
        "source_trigger_taxonomy": {
            "matched_triggers": matched_triggers,
            "inferred_presets": inferred_presets,
            "rule": "Use matched triggers to choose presets before reading the broader source registry.",
        },
        "source_count": len(entries),
        "sources": entries,
        "rules": PLAN_RULES,
    }

    text = json.dumps(plan, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
