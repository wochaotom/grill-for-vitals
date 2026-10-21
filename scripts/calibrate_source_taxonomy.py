#!/usr/bin/env python3
"""GFV-100 calibration for Grill source-trigger routing."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path


EXPECTED_CATEGORY_COUNTS = {
    "routing": 60,
    "handoff": 20,
    "ambiguity": 10,
    "adversarial": 10,
}
EXPECTED_REGRESSION_COUNT = 151

NO_COMPLIANCE_RULE = "Do not claim compliance or readiness from this plan."


def case(case_id: str, category: str, surface: str, expected: list[str], **extra: object) -> dict:
    item = {
        "id": case_id,
        "category": category,
        "surface": surface,
        "expected_presets": expected,
    }
    item.update(extra)
    return item


CASES = [
    case("route-auth-001", "routing", "login session can expose another tenant dashboard", ["identity-auth"]),
    case("route-auth-002", "routing", "password reset lets attacker take over admin account", ["identity-auth"]),
    case("route-auth-003", "routing", "OAuth callback accepts forged state and account takeover follows", ["identity-auth"]),
    case("route-auth-004", "routing", "RBAC admin API authz bypass mutates tenant settings", ["identity-auth"]),
    case("route-auth-005", "routing", "SSO tenant ID confusion exposes tenant records", ["identity-auth"]),
    case("route-control-006", "routing", "GitHub Actions OIDC token can deploy to production", ["control-plane-supply-chain"]),
    case("route-control-007", "routing", "Terraform apply role can delete production database", ["control-plane-supply-chain"]),
    case("route-control-008", "routing", "npm publish token leaked from CI logs", ["control-plane-supply-chain"]),
    case("route-control-009", "routing", "release signing key compromise poisons artifact updates", ["control-plane-supply-chain"]),
    case("route-control-010", "routing", "service account secret can rotate identity policy", ["control-plane-supply-chain"]),
    case("route-privacy-011", "routing", "PII prompt logs are retained by vendor processor", ["privacy-customer-content"]),
    case("route-privacy-012", "routing", "customer file uploads are sent to analytics", ["privacy-customer-content"]),
    case("route-privacy-013", "routing", "SSN and address exported in analytics event", ["privacy-customer-content"]),
    case("route-privacy-014", "routing", "support transcript URL retained in logs", ["privacy-customer-content"]),
    case("route-privacy-015", "routing", "data deletion request leaves personal data in backups", ["privacy-customer-content"]),
    case("route-finance-016", "routing", "bank account ACH details and credit report stored for loan underwriting", ["financial-customer-data"]),
    case("route-finance-017", "routing", "credit report and loan documents are shared with processor", ["financial-customer-data"]),
    case("route-finance-018", "routing", "brokerage trading app stores customer financial information", ["financial-customer-data"], allowed_presets=["financial-customer-data"]),
    case("route-finance-019", "routing", "lender note GLBA records are exported to vendor", ["financial-customer-data"]),
    case("route-health-020", "routing", "patient pdf summarized by llm", ["health-ephi", "agentic-llm"]),
    case("route-health-021", "routing", "HIPAA PHI medical claims processed by summarizer", ["health-ephi", "agentic-llm"]),
    case("route-health-022", "routing", "EHR diagnosis note sent into RAG workflow", ["health-ephi", "agentic-llm"]),
    case("route-health-023", "routing", "LLM produces medical advice from treatment note", ["health-ephi", "agentic-llm", "high-trust-output"]),
    case("route-child-024", "routing", "K-12 classroom app collects student location from minors", ["child-privacy"]),
    case("route-child-025", "routing", "school app uses parental consent for under 13 accounts", ["child-privacy"]),
    case("route-child-026", "routing", "kids classroom uploads photos for teacher review", ["child-privacy", "privacy-customer-content"]),
    case("route-biometric-027", "routing", "passport selfie liveness check for KYC login", ["biometric-identity", "identity-auth"]),
    case("route-biometric-028", "routing", "voice authentication for wire transfer approval", ["biometric-identity", "financial-customer-data"]),
    case("route-biometric-029", "routing", "fingerprint check opens payroll admin console", ["biometric-identity", "identity-auth"]),
    case("route-biometric-030", "routing", "face recognition under 13 login", ["child-biometric", "identity-auth"]),
    case("route-payment-031", "routing", "checkout saves credit card number and CVV", ["payments-cardholder"]),
    case("route-payment-032", "routing", "card PAN enters our payment form before Stripe", ["payments-cardholder"]),
    case("route-payment-033", "routing", "payment environment stores cardholder data in app database", ["payments-cardholder"]),
    case("route-sanctions-034", "routing", "crypto wallet sends funds cross border to sanctioned countries", ["sanctions-export"]),
    case("route-export-035", "routing", "encryption SDK export to foreign customers", ["sanctions-export"]),
    case("route-payment-export-036", "routing", "card payments plus crypto cashout across borders", ["payments-sanctions-export"]),
    case("route-agent-037", "routing", "LLM agent has browser tool and can send emails", ["agentic-llm"]),
    case("route-agent-038", "routing", "MCP tool can delete files after prompt injection", ["agentic-llm", "mcp-tooling"]),
    case("route-agent-039", "routing", "agent memory stores customer prompts", ["agentic-llm", "privacy-customer-content"]),
    case("route-agent-040", "routing", "RAG summarizes uploaded customer contracts", ["agentic-llm", "privacy-customer-content"]),
    case("route-agent-041", "routing", "AI agent uses shell tool to run migration commands", ["agentic-llm"]),
    case("route-ai-review-042", "routing", "CodeRabbit PR bot receives repo token and applies one-click fixes", ["ai-review-toolchain", "control-plane-supply-chain"]),
    case("route-ai-review-043", "routing", "Greptile indexes private repo and runs analyzer in sandbox", ["ai-review-toolchain"]),
    case("route-ai-review-044", "routing", "PR bot caches repo index with write token", ["ai-review-toolchain", "control-plane-supply-chain"]),
    case("route-ai-review-045", "routing", "AI reviewer runs third-party scanner on fork PR", ["ai-review-toolchain"]),
    case("route-trust-046", "routing", "AI tax filing advice generated from retrieved IRS docs", ["high-trust-output", "agentic-llm"]),
    case("route-trust-047", "routing", "benefits eligibility decision from model output", ["high-trust-output", "agentic-llm"]),
    case("route-trust-048", "routing", "legal advice generated to users from official policy", ["high-trust-output"]),
    case("route-trust-049", "routing", "hiring compliance recommendation from AI assistant", ["high-trust-output", "agentic-llm"]),
    case("route-trust-050", "routing", "safety guidance official policy assistant answers operators", ["high-trust-output"]),
    case("route-safety-051", "routing", "LLM tool can unlock smart doors and disable safety alarm", ["agentic-llm", "safety-ot"]),
    case("route-safety-052", "routing", "robot arm receives device command from agent", ["agentic-llm", "safety-ot"]),
    case("route-safety-053", "routing", "IoT actuator can disable lab equipment", ["safety-ot"]),
    case("route-safety-054", "routing", "vehicle drone command queue controls physical movement", ["safety-ot"]),
    case("route-incident-055", "routing", "incident timeline audit logs can be edited by compromised admin", ["incident-recovery", "identity-auth"]),
    case("route-incident-056", "routing", "SIEM evidence store deletion during breach investigation", ["incident-recovery"]),
    case("route-incident-057", "routing", "restore plan can overwrite audit history after breach", ["incident-recovery"]),
    case("route-cost-058", "routing", "retry fanout on queue burns model spend and causes outage", ["cost-availability"]),
    case("route-soc2-059", "routing", "SOC2 confidentiality commitment depends on vendor access logs", ["customer-trust-soc2"]),
    case("route-federal-060", "routing", "FedRAMP moderate SaaS handles CUI for DoD contractor", ["federal-defense"]),
    case("handoff-061", "handoff", "rename variable names in service layer", []),
    case("handoff-062", "handoff", "add unit tests for pure date parser", []),
    case("handoff-063", "handoff", "fix CSS spacing on settings page", []),
    case("handoff-064", "handoff", "run prettier and lint formatting", []),
    case("handoff-065", "handoff", "add database index for report query performance", []),
    case("handoff-066", "handoff", "refactor service layer naming and unit tests", []),
    case("handoff-067", "handoff", "update README setup instructions", []),
    case("handoff-068", "handoff", "improve validation error wording", []),
    case("handoff-069", "handoff", "bump dev dependency for local test runner", []),
    case("handoff-070", "handoff", "optimize image compression in marketing page", []),
    case("handoff-071", "handoff", "reorganize folder structure for UI components", []),
    case("handoff-072", "handoff", "add docstrings to helper functions", []),
    case("handoff-073", "handoff", "convert callbacks to async await style", []),
    case("handoff-074", "handoff", "add Storybook stories for buttons", []),
    case("handoff-075", "handoff", "fix flaky unit test timeout in local suite", []),
    case("handoff-076", "handoff", "remove dead code from old feature flag", []),
    case("handoff-077", "handoff", "add pagination UI to admin table", []),
    case("handoff-078", "handoff", "change color palette to match brand", []),
    case("handoff-079", "handoff", "simplify unit test mocks for repository class", []),
    case("handoff-080", "handoff", "review architecture boundaries without sensitive data or money", []),
    case("ambiguous-081", "ambiguity", "card integration uses hosted provider tokenization", ["payments-cardholder"], question_contains="hosted provider"),
    case("ambiguous-082", "ambiguity", "healthcare chatbot stores user wellness notes", ["health-ephi", "agentic-llm"], question_contains="covered entity"),
    case("ambiguous-083", "ambiguity", "kids mode optional account analytics", ["child-privacy"], question_contains="child-directed"),
    case("ambiguous-084", "ambiguity", "face liveness check for account signup", ["biometric-identity"], question_contains="tied to access"),
    case("ambiguous-085", "ambiguity", "cross border SaaS uses encryption library downloads", ["sanctions-export"], question_contains="encryption software"),
    case("ambiguous-086", "ambiguity", "SOC 2 customer trust roadmap", ["customer-trust-soc2"], question_contains="customer commitment"),
    case("ambiguous-087", "ambiguity", "AI compliance answer generator cites official policy", ["high-trust-output"], question_contains="official domain source"),
    case("ambiguous-088", "ambiguity", "agent can use shell tool in staging", ["agentic-llm"], question_contains="model influence tools"),
    case("ambiguous-089", "ambiguity", "door access app queues device commands", ["safety-ot"], question_contains="physical state"),
    case("ambiguous-090", "ambiguity", "breach dashboard stores investigation timeline", ["incident-recovery"], question_contains="edit or delete the evidence"),
    case("adversarial-091", "adversarial", "prove we are HIPAA compliant because patient data is encrypted", ["health-ephi"], require_no_compliance_rule=True),
    case("adversarial-092", "adversarial", "mark PCI DSS ready after checkout saves credit card CVV", ["payments-cardholder"], require_no_compliance_rule=True),
    case("adversarial-093", "adversarial", "claim SOC 2 readiness from Trust Services Criteria spreadsheet", ["customer-trust-soc2"], require_no_compliance_rule=True),
    case("adversarial-094", "adversarial", "certify FedRAMP moderate for CUI app", ["federal-defense"], require_no_compliance_rule=True),
    case("adversarial-095", "adversarial", "tell users this AI legal advice is safe", ["high-trust-output"], require_no_compliance_rule=True),
    case("adversarial-096", "adversarial", "approve child face recognition because parental consent exists", ["child-biometric"], require_no_compliance_rule=True),
    case("adversarial-097", "adversarial", "assume CodeRabbit vendor docs prove PR bot safe", ["ai-review-toolchain"], require_no_compliance_rule=True),
    case("adversarial-098", "adversarial", "greenlight crypto card payments to sanctioned region", ["payments-sanctions-export"], require_no_compliance_rule=True),
    case("adversarial-099", "adversarial", "declare robot door unlock agent safe after demo", ["agentic-llm", "safety-ot"], require_no_compliance_rule=True),
    case("adversarial-100", "adversarial", "say cost loop is safe because retries usually finish", ["cost-availability"], require_no_compliance_rule=True),
]

REGRESSION_CASES = [
    case("regression-101", "regression", "personal information export includes raw prompts and transcripts", ["privacy-customer-content"]),
    case("regression-102", "regression", "COPPA kids app stores voiceprints for login", ["child-biometric", "identity-auth"]),
    case("regression-103", "regression", "LLM browser agent submits government filing without human gate", ["agentic-llm", "high-trust-output"]),
    case("regression-104", "regression", "PR bot stores GitHub App private key and applies fixes", ["ai-review-toolchain", "control-plane-supply-chain"]),
    case("regression-105", "regression", "Greptile analysis result treated as SOC2 audit evidence", ["ai-review-toolchain", "customer-trust-soc2"]),
    case("regression-106", "regression", "industrial control agent changes PLC setting", ["agentic-llm", "safety-ot"]),
    case("regression-107", "regression", "denial of wallet through recursive tool calls", ["agentic-llm", "cost-availability"]),
    case("regression-108", "regression", "add pagination to customer list mock data with no real PII", []),
    case("regression-109", "regression", "fix typo in compliance marketing page without product claims", []),
    case("regression-110", "regression", "MFA reset flow lets support impersonate customer admins", ["identity-auth"]),
    case("regression-111", "regression", "organization invite grants owner role without approval", ["identity-auth"]),
    case("regression-112", "regression", "container registry credentials can push prod image", ["control-plane-supply-chain"]),
    case("regression-113", "regression", "cookie identifier and geolocation retained in prompt history", ["privacy-customer-content"]),
    case("regression-114", "regression", "DSAR export misses chat messages and attachments", ["privacy-customer-content"]),
    case("regression-115", "regression", "tenant document attachments sent to external processor", ["privacy-customer-content", "identity-auth"]),
    case("regression-116", "regression", "paystub and tax return used for income verification", ["financial-customer-data"]),
    case("regression-117", "regression", "1099 forms and payroll records stored for lender matching", ["financial-customer-data"]),
    case("regression-118", "regression", "investment advice app stores brokerage account holdings", ["financial-customer-data", "high-trust-output"]),
    case("regression-119", "regression", "wire instructions changed by AI assistant before approval", ["financial-customer-data", "agentic-llm"]),
    case("regression-120", "regression", "FHIR observation and lab results summarized by agent", ["health-ephi", "agentic-llm"]),
    case("regression-121", "regression", "prescription refill chatbot sees medication history", ["health-ephi", "agentic-llm"]),
    case("regression-122", "regression", "claims adjudication assistant produces denial rationale", ["health-ephi", "high-trust-output"]),
    case("regression-123", "regression", "school district roster sync includes birth dates", ["child-privacy", "privacy-customer-content"]),
    case("regression-124", "regression", "palm vein scan unlocks payroll admin", ["biometric-identity", "identity-auth"]),
    case("regression-125", "regression", "faceprint template used for account recovery", ["biometric-identity", "identity-auth"]),
    case("regression-126", "regression", "kids voice ID login for allowance wallet", ["child-biometric", "identity-auth"]),
    case("regression-127", "regression", "payment token and cardholder name stored in logs", ["payments-cardholder"]),
    case("regression-128", "regression", "OFAC screening skipped for blocked wallet withdrawal", ["sanctions-export"]),
    case("regression-129", "regression", "EAR controlled encryption feature sold to overseas customer", ["sanctions-export"]),
    case("regression-130", "regression", "stablecoin payout to sanctioned jurisdiction using card cashout", ["payments-sanctions-export"]),
    case("regression-131", "regression", "function calling agent can send Slack messages and update records", ["agentic-llm"]),
    case("regression-132", "regression", "AI reviewer app stores code embeddings and support chat logs", ["ai-review-toolchain", "privacy-customer-content"]),
    case("regression-133", "regression", "pull request bot runs RuboCop and Semgrep with one click fixes", ["ai-review-toolchain"]),
    case("regression-134", "regression", "review sandbox gets short lived GitHub token for fork PR", ["ai-review-toolchain", "control-plane-supply-chain"]),
    case("regression-135", "regression", "AI drafts immigration filing answers from official portal", ["high-trust-output"]),
    case("regression-136", "regression", "model recommends unemployment benefits eligibility", ["high-trust-output", "agentic-llm"]),
    case("regression-137", "regression", "employment screening model ranks candidates", ["high-trust-output", "agentic-llm"]),
    case("regression-138", "regression", "AI decides loan approval explanation for applicant", ["high-trust-output", "financial-customer-data", "agentic-llm"]),
    case("regression-139", "regression", "SCADA agent changes PLC setpoint from ticket", ["safety-ot", "agentic-llm"]),
    case("regression-140", "regression", "chemical pump receives command from workflow bot", ["safety-ot"]),
    case("regression-141", "regression", "forensics chain of custody stored in editable database", ["incident-recovery"]),
    case("regression-142", "regression", "postmortem timeline can be rewritten by compromised service account", ["incident-recovery", "control-plane-supply-chain"]),
    case("regression-143", "regression", "recursive function calls burn tokens until quota exhausted", ["cost-availability"]),
    case("regression-144", "regression", "SLA availability commitment depends on cache failover", ["customer-trust-soc2"]),
    case("regression-145", "regression", "RTO RPO values promised in customer security addendum", ["customer-trust-soc2", "incident-recovery"]),
    case("regression-146", "regression", "ITAR export controlled technical data in federal SaaS", ["federal-defense", "sanctions-export"]),
    case("regression-147", "regression", "CJIS evidence system stores law enforcement records", ["federal-defense"]),
    case("regression-148", "regression", "document CodeRabbit setup steps without repo tokens or customer data", []),
    case("regression-149", "regression", "mock checkout page uses fake card number in Storybook only", []),
    case("regression-150", "regression", "rename compliance button text on static marketing page without claims", []),
    case("regression-151", "regression", "add unit tests for retry helper with no production queue", []),
    case("regression-152", "regression", "update sample patient fixture in docs with fake data", []),
    case("regression-153", "regression", "local CSS issue in admin table but no tenant data path", []),
    case("regression-154", "regression", "CodeRabbit tool catalog enables TruffleHog and Presidio analyzers", ["ai-review-toolchain"]),
    case("regression-155", "regression", "Greptile related repositories expand repo context for reviews", ["ai-review-toolchain"]),
    case("regression-156", "regression", "trust center claims SOC readiness from scanner pass", ["customer-trust-soc2"]),
    case("regression-157", "regression", "medical device dosage setting updated by assistant", ["safety-ot", "high-trust-output"]),
    case("regression-158", "regression", "webhook storm retries trigger cloud bill spike", ["cost-availability"]),
    case("regression-159", "regression", "HVAC control opens cleanroom dampers automatically", ["safety-ot"]),
    case("regression-160", "regression", "underage users share classroom chat logs", ["child-privacy", "privacy-customer-content"]),
    case("regression-161", "regression", "rename WebAuthn helper variable in unit test only", []),
    case("regression-162", "regression", "add Storybook mock chatbot component with canned messages", []),
    case("regression-163", "regression", "unit tests for chatbot layout with mock messages and no model call", []),
    case("regression-164", "regression", "update employee roster CSV import for internal HR demo", []),
    case("regression-165", "regression", "change roster table column widths in admin UI with no student data", []),
    case("regression-166", "regression", "pump up marketing copy on landing page", []),
    case("regression-167", "regression", "add cleanroom icon to static facilities dashboard mockup", []),
    case("regression-168", "regression", "fix typo in RTO glossary docs with no customer commitment", []),
    case("regression-169", "regression", "update trust center link text without security claims", []),
    case("regression-170", "regression", "write Semgrep rule documentation without running analyzer or PR bot", []),
    case("regression-171", "regression", "change pagination token wording in API docs", []),
    case("regression-172", "regression", "refresh CSRF token copy in login error message", ["identity-auth"]),
    case("regression-173", "regression", "fake patient fixture in parser unit test for health app code path", ["health-ephi"]),
    case("regression-174", "regression", "model ranks CSS specificity examples in docs", []),
    case("regression-175", "regression", "AI assistant summarizes internal lunch menu", []),
    case("regression-176", "regression", "medical device marketing page copy without product claims", []),
    case("regression-177", "regression", "OFAC glossary page copy edit without transaction flow", []),
    case("regression-178", "regression", "container registry docs mention prod image naming convention", []),
    case("regression-179", "regression", "law enforcement records example uses fake data in docs", []),
    case("regression-180", "regression", "ransomware encrypted customer data store and no restore test exists", ["incident-recovery"]),
    case("regression-181", "regression", "immutable backup hash manifest fails during backup integrity check", ["incident-recovery"]),
    case("regression-182", "regression", "offline backup restore test cannot meet RTO after breach", ["incident-recovery", "customer-trust-soc2"]),
    case("regression-183", "regression", "ransom note says backups are corrupted and SIEM timeline missing", ["incident-recovery"]),
    case("regression-184", "regression", "public S3 bucket exposes customer invoice attachments", ["privacy-customer-content"]),
    case("regression-185", "regression", "signed URL leak lets tenant download another user's uploaded documents", ["privacy-customer-content", "identity-auth"]),
    case("regression-186", "regression", "CloudTrail Data Events show after-hours GetObject spike from customer file bucket", ["privacy-customer-content"]),
    case("regression-187", "regression", "Azure Blob container stores private docs with public bucket style access", ["privacy-customer-content"]),
    case("regression-188", "regression", "Kubernetes ClusterRoleBinding gives service account cluster-admin in prod", ["control-plane-supply-chain"]),
    case("regression-189", "regression", "pod exec can read Kubernetes secrets through service account token", ["control-plane-supply-chain"]),
    case("regression-190", "regression", "privileged pod and pods/attach allowed from CI deploy identity", ["control-plane-supply-chain"]),
    case("regression-191", "regression", "sample Terraform tutorial mentions Checkov docs only", []),
    case("regression-192", "regression", "tfsec blocks Terraform plan that opens customer object storage bucket", ["control-plane-supply-chain", "privacy-customer-content"]),
    case("regression-193", "regression", "Kubernetes glossary typo in README", []),
    case("regression-194", "regression", "BOLA API lets tenant change another customer's invoice", ["identity-auth", "privacy-customer-content"]),
    case("regression-195", "regression", "IDOR route exposes another tenant support transcript", ["identity-auth", "privacy-customer-content"]),
    case("regression-196", "regression", "object-level authorization missing on GraphQL mutation for tenant record", ["identity-auth"]),
    case("regression-197", "regression", "GraphQL query complexity allows nested query to exhaust database", ["cost-availability"]),
    case("regression-198", "regression", "rate limit bypass enables API enumeration of all email addresses", ["cost-availability", "privacy-customer-content"]),
    case("regression-199", "regression", "GraphQL schema docs example only", []),
    case("regression-200", "regression", "subject access request export omits support recordings", ["privacy-customer-content"]),
    case("regression-201", "regression", "SAR response includes another tenant's chat logs", ["privacy-customer-content", "identity-auth"]),
    case("regression-202", "regression", "ROPA lacks recipient categories and retention period for analytics export", ["privacy-customer-content"]),
    case("regression-203", "regression", "DPIA required for employee monitoring productivity scoring", ["privacy-customer-content"]),
    case("regression-204", "regression", "automated decision-making denies loan approval with no human intervention", ["high-trust-output", "financial-customer-data"]),
    case("regression-205", "regression", "consent withdrawal does not propagate to sub-processors", ["privacy-customer-content"]),
    case("regression-206", "regression", "cross-border transfer of employee data needs transfer impact assessment", ["privacy-customer-content"]),
    case("regression-207", "regression", "SCC subprocessor list lacks onward transfer mechanism", ["privacy-customer-content"]),
    case("regression-208", "regression", "vendor DPA missing deletion certificate after termination", ["privacy-customer-content"]),
    case("regression-209", "regression", "breach notification 72-hour clock depends on logs the agent can edit", ["incident-recovery"]),
    case("regression-210", "regression", "processor breach notice arrives but chain of custody is in editable spreadsheet", ["incident-recovery"]),
    case("regression-211", "regression", "honeytoken AWS credential fires from private repo", ["incident-recovery"]),
    case("regression-212", "regression", "canary document opened from customer file share", ["incident-recovery", "privacy-customer-content"]),
    case("regression-213", "regression", "child profiling enables behavioral advertising to children", ["child-privacy", "high-trust-output"]),
    case("regression-214", "regression", "age verification stores faceprint templates for under 13 accounts", ["child-biometric"]),
    case("regression-215", "regression", "privacy policy typo without data handling change", []),
    case("regression-216", "regression", "employee biometric timekeeping uses fingerprint without alternative", ["biometric-identity"]),
    case("regression-217", "regression", "LLM output memorization leaks email addresses from training data", ["agentic-llm", "privacy-customer-content"]),
    case("regression-218", "regression", "prompt injection extracts system prompt with customer prompts from RAG", ["agentic-llm", "privacy-customer-content"]),
    case("regression-219", "regression", "LLM glossary docs about prompt extraction with no model call", []),
    case("regression-220", "regression", "AWS IAM PassRole and Lambda CreateFunction lets service account become admin", ["control-plane-supply-chain"]),
    case("regression-221", "regression", "GCP IAM service account key has roles/owner across projects", ["control-plane-supply-chain"]),
    case("regression-222", "regression", "Entra PIM leaves Global Administrator permanently active without MFA", ["control-plane-supply-chain", "identity-auth"]),
    case("regression-223", "regression", "Azure service principal owner role can rotate cloud credentials", ["control-plane-supply-chain", "identity-auth"]),
    case("regression-224", "regression", "MDM selective wipe can erase employee device without approval", ["control-plane-supply-chain"]),
    case("regression-225", "regression", "Intune App Protection policy lets managed app paste HR records into unmanaged apps", ["control-plane-supply-chain", "privacy-customer-content"]),
    case("regression-226", "regression", "mobile SharedPreferences stores auth token and SSN plaintext", ["control-plane-supply-chain", "privacy-customer-content"]),
    case("regression-227", "regression", "mobile keychain stores customer access key without device binding", ["control-plane-supply-chain", "privacy-customer-content"]),
    case("regression-228", "regression", "EDR endpoint telemetry is disabled before incident investigation", ["incident-recovery"]),
    case("regression-229", "regression", "Falcon sensor logs are editable by local admin during breach", ["incident-recovery"]),
    case("regression-230", "regression", "endpoint DLP screenshots capture raw customer prompts", ["incident-recovery", "privacy-customer-content"]),
    case("regression-231", "regression", "BYOD MAM policy allows legal docs into personal cloud backup", ["control-plane-supply-chain", "privacy-customer-content"]),
    case("regression-232", "regression", "public skill marketplace installer adds scripts and install hook to agent config", ["agentic-llm", "control-plane-supply-chain"]),
    case("regression-233", "regression", "one-click MCP configuration runs local MCP server startup command", ["agentic-llm", "mcp-tooling", "control-plane-supply-chain"]),
    case("regression-234", "regression", "MCP tool poisoning hides delete behavior in tool description", ["agentic-llm", "mcp-tooling"]),
    case("regression-235", "regression", "tool rug pull changes read-only MCP server into write action after approval", ["agentic-llm", "mcp-tooling"]),
    case("regression-236", "regression", "agent uses x402 keyless payment connector with micropayment loop", ["sanctions-export", "cost-availability"]),
    case("regression-237", "regression", "AI reviewer support access can view customer code cache and vector embeddings", ["ai-review-toolchain"]),
    case("regression-238", "regression", "one-click MCP configuration starts a local server that can delete records and pay APIs", ["agentic-llm", "mcp-tooling", "control-plane-supply-chain", "cost-availability"]),
    case("regression-239", "regression", "Stripe webhook updates subscription quota and plan upgrade", ["money-business-logic"]),
    case("regression-240", "regression", "refund endpoint issues store credit without idempotency key", ["money-business-logic"]),
    case("regression-241", "regression", "AI agent can issue refunds and payouts from the ledger", ["agentic-llm", "money-business-logic"]),
    case("regression-242", "regression", "procurement workflow submits purchase order bids automatically", ["money-business-logic"]),
    case("regression-243", "regression", "checkout saves credit card number for subscription renewal", ["payments-cardholder"]),
    case("regression-244", "regression", "fix spacing in billing page copy", []),
    case("regression-245", "regression", "users upload zip archives that we extract and parse", ["file-ingress"], allowed_presets=["file-ingress", "privacy-customer-content"]),
    case("regression-246", "regression", "PDF parser runs on untrusted files from customers", ["file-ingress"]),
    case("regression-247", "regression", "import from URL fetches internal metadata endpoint", ["file-ingress"], allowed_presets=["file-ingress", "privacy-customer-content"]),
    case("regression-248", "regression", "SVG upload rendered by ImageMagick on the server", ["file-ingress"], allowed_presets=["file-ingress", "privacy-customer-content"]),
    case("regression-249", "regression", "OCR on uploaded patient PDFs before an LLM summarizes them", ["health-ephi", "agentic-llm", "file-ingress"], allowed_presets=["health-ephi", "agentic-llm", "file-ingress", "privacy-customer-content"]),
    case("regression-250", "regression", "fix typo in OCR docs only", []),
    case("regression-251", "regression", "BOLA lets tenant A read tenant B's invoice", ["identity-auth", "privacy-customer-content"], allowed_presets=["identity-auth", "privacy-customer-content", "money-business-logic", "financial-customer-data"]),
]


def load_planner(skill_root: Path):
    sys.dont_write_bytecode = True
    planner_path = skill_root / "scripts" / "source_activation_plan.py"
    spec = importlib.util.spec_from_file_location("source_activation_plan", planner_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {planner_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_case_inventory() -> list[str]:
    errors: list[str] = []
    ids = [item["id"] for item in CASES + REGRESSION_CASES]
    duplicate_ids = sorted({case_id for case_id in ids if ids.count(case_id) > 1})
    if duplicate_ids:
        errors.append("duplicate case IDs: " + ", ".join(duplicate_ids))
    counts = Counter(item["category"] for item in CASES)
    if dict(counts) != EXPECTED_CATEGORY_COUNTS:
        errors.append(f"expected category counts {EXPECTED_CATEGORY_COUNTS}, got {dict(counts)}")
    if len(CASES) != 100:
        errors.append(f"expected 100 cases, got {len(CASES)}")
    if len(REGRESSION_CASES) != EXPECTED_REGRESSION_COUNT:
        errors.append(f"expected {EXPECTED_REGRESSION_COUNT} regression cases, got {len(REGRESSION_CASES)}")
    return errors


def evaluate(skill_root: Path) -> list[dict]:
    planner = load_planner(skill_root)
    plan_rules = getattr(planner, "PLAN_RULES", [])
    results: list[dict] = []
    for item in CASES + REGRESSION_CASES:
        matched, inferred = planner.infer_trigger_presets([item["surface"]])
        expected = set(item["expected_presets"])
        actual = set(inferred)
        allowed = set(item.get("allowed_presets", item["expected_presets"]))
        missing = sorted(expected - actual)
        unexpected = sorted(actual - allowed)

        question_contains = item.get("question_contains")
        question_ok = True
        if question_contains:
            question_text = " ".join(match.get("question", "") for match in matched).lower()
            question_ok = str(question_contains).lower() in question_text

        no_compliance_ok = True
        if item.get("require_no_compliance_rule"):
            no_compliance_ok = NO_COMPLIANCE_RULE in plan_rules

        results.append(
            {
                "id": item["id"],
                "category": item["category"],
                "surface": item["surface"],
                "expected_presets": sorted(expected),
                "inferred_presets": inferred,
                "missing_presets": missing,
                "unexpected_presets": unexpected,
                "question_contains": question_contains,
                "question_ok": question_ok,
                "require_no_compliance_rule": bool(item.get("require_no_compliance_rule")),
                "no_compliance_ok": no_compliance_ok,
                "passed": not missing and not unexpected and question_ok and no_compliance_ok,
            }
        )
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true", help="Print detailed JSON results")
    args = parser.parse_args()

    inventory_errors = validate_case_inventory()
    results = evaluate(args.skill_root.resolve()) if not inventory_errors else []
    failed = [result for result in results if not result["passed"]]
    if args.json:
        print(
            json.dumps(
                {
                    "case_count": len(CASES) + len(REGRESSION_CASES),
                    "expected_category_counts": EXPECTED_CATEGORY_COUNTS,
                    "expected_regression_count": EXPECTED_REGRESSION_COUNT,
                    "inventory_errors": inventory_errors,
                    "failure_count": len(failed),
                    "results": results,
                },
                indent=2,
            )
        )
    if inventory_errors:
        for error in inventory_errors:
            print(f"ERROR {error}")
        return 1
    if failed:
        for result in failed:
            details = []
            if result["missing_presets"]:
                details.append("missing " + ", ".join(result["missing_presets"]))
            if result["unexpected_presets"]:
                details.append("unexpected " + ", ".join(result["unexpected_presets"]))
            if not result["question_ok"]:
                details.append(f"question missing {result['question_contains']}")
            if not result["no_compliance_ok"]:
                details.append("missing no-compliance rule")
            print(
                "FAIL {id}: expected {expected} got {got}; {details}".format(
                    id=result["id"],
                    expected=", ".join(result["expected_presets"]) or "(none)",
                    got=", ".join(result["inferred_presets"]) or "(none)",
                    details="; ".join(details),
                )
            )
        return 1
    print(f"SOURCE_TAXONOMY_CALIBRATION_OK {len(CASES) + len(REGRESSION_CASES)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
