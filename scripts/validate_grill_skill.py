#!/usr/bin/env python3
"""Validate Grill for Vitals scope and source-registry invariants."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_REFERENCES = [
    "references/catastrophe-taxonomy.md",
    "references/evidence-gates.md",
    "references/vital-principles.md",
    "references/scope-boundary.md",
    "references/question-bank.md",
    "references/anti-overexpansion-query-protocol.md",
    "references/source-trigger-taxonomy.md",
    "references/source-registry.md",
    "references/source-weights.json",
    "references/vitals-source-matrix.md",
    "references/vendor-ai-reviewer-patterns.md",
    "references/pressure-scenarios.md",
    "references/behavioral-evaluation-protocol.md",
    "references/source-map.md",
    "references/report-template.md",
]

REQUIRED_SCRIPTS = [
    "quick_validate.py",
    "scripts/source_activation_plan.py",
    "scripts/calibrate_source_taxonomy.py",
    "scripts/check_source_links.py",
    "scripts/evaluate_behavioral_runs.py",
    "scripts/validator_smoke_tests.py",
]

SKILL_REQUIRED_PHRASES = [
    "Do not use for ordinary code review",
    "Run the scope gate first",
    "ordinary code review",
    "source-registry.md",
    "source-trigger-taxonomy.md",
    "source-weights.json",
    "vitals-source-matrix.md",
    "vendor-ai-reviewer-patterns.md",
    "pressure-scenarios.md",
    "behavioral-evaluation-protocol.md",
    "vital-principles.md",
    "Skill Iteration Checks",
    "calibrate_source_taxonomy.py",
    "check_source_links.py",
    "evaluate_behavioral_runs.py",
    "validator_smoke_tests.py",
    "catastrophic vital",
]

VENDOR_REQUIRED_PHRASES = [
    "Greptile",
    "CodeRabbit",
    "vendor/practitioner",
    "sandbox",
    "short-lived",
    "Do not let these sources pull Grill into generic PR review",
]

SOURCE_REGISTRY_REQUIRED_PHRASES = [
    "## Rejected Or Deferred Sources",
    "Google Engineering Practices",
    "SLSA/OpenSSF Scorecard",
    "General AI code-review checklists",
]

PRESSURE_REQUIRED_PHRASES = [
    "GFV-001",
    "GFV-003",
    "GFV-008",
    "GFV-013",
    "GFV-014",
    "GFV-015",
    "GFV-016",
    "GFV-017",
    "GFV-018",
    "GFV-019",
    "GFV-020",
    "ordinary code review",
    "vendor/practitioner",
    "safety-critical",
    "source_activation_plan.py",
    "Common Failure Modes To Catch",
]

BEHAVIOR_PROTOCOL_REQUIRED_PHRASES = [
    "## Measurement Objective",
    "## Baseline and candidate parity",
    "## Development, Regression, And Holdout Cases",
    "## Deterministic Checks",
    "## Independent Expert Checks",
    "## Hard Failures",
    "evaluate_behavioral_runs.py",
    "does not generate or judge responses",
    "not a safety certificate",
]

SOURCE_PLANNER_REQUIRED_PHRASES = [
    "--self-test",
    "--surface",
    "--list-trigger-taxonomy",
    "SOURCE_PRESETS_OK",
    "TRIGGER_TAXONOMY",
    "signal_matches",
    "PLAN_RULES",
    "ai-review-toolchain",
    "high-trust-output",
    "agentic-llm",
    "mcp-tooling",
    "identity-auth",
    "control-plane-supply-chain",
    "privacy-customer-content",
    "financial-customer-data",
    "health-ephi",
    "child-privacy",
    "biometric-identity",
    "child-biometric",
    "payments-cardholder",
    "sanctions-export",
    "customer-trust-soc2",
    "incident-recovery",
    "safety-ot",
    "cost-availability",
    "payments-sanctions-export",
    "federal-defense",
]

SOURCE_PLANNER_NON_PRESET_PHRASES = {
    "--self-test",
    "--surface",
    "--list-trigger-taxonomy",
    "SOURCE_PRESETS_OK",
    "TRIGGER_TAXONOMY",
    "signal_matches",
    "PLAN_RULES",
}

SOURCE_CALIBRATION_REQUIRED_PHRASES = [
    "EXPECTED_CATEGORY_COUNTS",
    '"routing": 60',
    '"handoff": 20',
    '"ambiguity": 10',
    '"adversarial": 10',
    "EXPECTED_REGRESSION_COUNT",
    "REGRESSION_CASES",
    "NO_COMPLIANCE_RULE",
    "SOURCE_TAXONOMY_CALIBRATION_OK",
    "allowed_presets",
    "question_contains",
    "require_no_compliance_rule",
    "expected 100 cases",
    "expected {EXPECTED_REGRESSION_COUNT} regression cases",
    "Terraform apply role can delete production database",
    "HIPAA PHI medical claims processed by summarizer",
    "brokerage trading app stores customer financial information",
    "personal information export includes raw prompts and transcripts",
    "MFA reset flow lets support impersonate customer admins",
    "payment token and cardholder name stored in logs",
    "SCADA agent changes PLC setpoint from ticket",
    "trust center claims SOC readiness from scanner pass",
    "document CodeRabbit setup steps without repo tokens or customer data",
    "unit tests for chatbot layout with mock messages and no model call",
    "fake patient fixture in parser unit test for health app code path",
    "fix typo in compliance marketing page without product claims",
    "refactor service layer naming and unit tests",
]

SOURCE_TRIGGER_REQUIRED_PHRASES = [
    "surface signal -> vital family -> source preset -> exact source IDs",
    "payments-sanctions-export",
    "child-biometric",
    "source_activation_plan.py --surface",
    "mcp-tooling",
    "do not scan every source",
    "MFA reset",
    "short-lived GitHub token",
    "pay APIs",
    "no production queue",
    "no model call",
    "no customer commitment",
]

VITAL_PRINCIPLES_REQUIRED_PHRASES = [
    "Start with blast radius",
    "Unknown is not safe",
    "Keep authority narrow",
    "Use conditional authorities",
    "Treat vendor tools as signals",
    "pair them with Tier A/B sources",
]

VITALS_SOURCE_MATRIX_REQUIRED_PHRASES = [
    "Secrets/control plane",
    "Identity/auth/sessions/tenancy",
    "Agent/tool/MCP/browser/shell",
    "High-trust outputs",
    "out-of-scope handoff",
]

EXPECTED_MATRIX_VITALS = [
    "Secrets/control plane",
    "Identity/auth/sessions/tenancy",
    "PII/customer content",
    "Money/billing/trading/procurement",
    "Irreversible mutation",
    "External effects",
    "Agent/tool/MCP/browser/shell",
    "Supply chain/build/deploy",
    "File ingress/storage",
    "Logs/audit/evidence",
    "High-trust outputs",
    "Cost/availability/runaway loops",
]

SCOPE_REQUIRED_PHRASES = [
    "## Entry Test",
    "## Out Of Scope",
    "## Handoff Rule",
    "## Overlap Rule",
    "## Stop Rule",
    "ordinary code review",
]

REPORT_REQUIRED_PHRASES = [
    "Activated standards/source IDs",
    "### Scope Gate",
    "Candidate vital:",
    "### Source Basis",
    "### Out-of-Scope Handoffs",
]

BANNED_ALWAYS_SOURCES = {
    "google-eng-practices",
    "google-testing",
    "google-style-guides",
    "google-developer-docs-style",
}

BANNED_ACTIVATIONS = {"always", "generic", "code_hygiene", "ordinary_review"}

RESERVED_OFFICIAL_SCOPES = {
    "incident-response",
    "federal-cloud",
    "fci",
    "cui",
    "ephi",
    "health-data",
    "children",
    "child-privacy",
    "cardholder-data",
    "payment-account-data",
    "sanctions",
    "export-control",
    "customer-financial-information",
    "financial-records",
    "safeguards-rule",
    "biometric-data",
    "digital-identity",
    "privacy-risk",
    "pii",
    "operational-technology",
    "industrial-control",
    "physical-safety",
    "ot-security",
}

ALLOWED_TIERS = {"A", "B", "B-provisional", "C", "D"}

BANNED_AUXILIARY_FILES = {
    "INSTALLATION_GUIDE.md",
    "QUICK_REFERENCE.md",
    "CHANGELOG.md",
}

TEXT_SUFFIXES = {".md", ".py", ".json", ".yaml", ".yml"}
PLACEHOLDER_RE = re.compile(r"\bTO" + r"DO\b|\[TO" + r"DO\]|FIX" + "ME")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def parse_frontmatter(text: str, errors: list[str]) -> dict[str, str]:
    if not text.startswith("---\n"):
        fail(errors, "SKILL.md must start with YAML frontmatter")
        return {}
    try:
        _, raw, _ = text.split("---", 2)
    except ValueError:
        fail(errors, "SKILL.md frontmatter is not delimited")
        return {}
    values: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            fail(errors, f"Invalid frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def registry_ids(registry: str) -> set[str]:
    match = re.search(r"## Activation Registry\n(?P<body>.*?)(?:\n## Current Source Links|\Z)", registry, flags=re.S)
    if not match:
        return set()
    return set(re.findall(r"\|\s*`([^`]+)`\s*\|", match.group("body")))


def registry_link_ids(registry: str) -> set[str]:
    match = re.search(r"## Current Source Links\n(?P<body>.*?)(?:\n## Source Admission Rules|\n## Rejected Or Deferred Sources|\Z)", registry, flags=re.S)
    if not match:
        return set()
    return set(re.findall(r"^-\s*`([^`]+)`\s*:", match.group("body"), flags=re.M))


def validate_question_bank(root: Path, errors: list[str]) -> None:
    path = root / "references" / "question-bank.md"
    text = path.read_text(encoding="utf-8")
    inline_text = re.sub(r"```.*?```", "", text, flags=re.S)
    allowed_presets = set(SOURCE_PLANNER_REQUIRED_PHRASES) - SOURCE_PLANNER_NON_PRESET_PHRASES
    allowed_tokens = allowed_presets | {"Red", "Amber", "Green", "Unknown"}
    for token in re.findall(r"`([^`]+)`", inline_text):
        if token not in allowed_tokens:
            fail(errors, f"question-bank.md references unknown token: {token}")
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("Question:"):
            continue
        if "<" in line:
            continue
        window = [item.strip() for item in lines[index + 1 : index + 4]]
        expected = ["Recommended answer:", "Evidence needed:", "Why this matters:"]
        for got, prefix in zip(window, expected):
            if not got.startswith(prefix):
                fail(errors, f"Question at {path.name}:{index + 1} missing {prefix}")


def validate_pressure_scenarios(root: Path, errors: list[str]) -> None:
    path = root / "references" / "pressure-scenarios.md"
    text = path.read_text(encoding="utf-8")
    scenario_ids = re.findall(r"\|\s*(GFV-\d{3})\s*\|", text)
    if len(scenario_ids) < 15:
        fail(errors, "pressure-scenarios.md should contain at least 15 scenarios")
    expected_ids = [f"GFV-{index:03d}" for index in range(1, len(scenario_ids) + 1)]
    if scenario_ids != expected_ids:
        fail(errors, "pressure-scenarios.md GFV IDs must be sequential from GFV-001")

    required_markers = {
        "generic handoff": "route to ordinary code review",
        "AI review preset": "Use `ai-review-toolchain`",
        "high trust output preset": "Use `high-trust-output`",
        "control plane preset": "Use `control-plane-supply-chain`",
        "payments cardholder preset": "Use `payments-cardholder` only",
        "health/LLM presets": "Use `health-ephi` and `agentic-llm`",
        "vendor weak evidence": "vendor reviews as weak evidence",
        "customer trust preset": "use `customer-trust-soc2`",
        "cost availability preset": "use `cost-availability`",
        "graph navigation only": "Graph output is navigation only",
        "sanctions/export": "Export-control + sanctions + money",
        "payments preset": "Use `payments-sanctions-export`",
        "incident recovery preset": "Use `incident-recovery`",
        "safety OT preset": "Use `safety-ot`",
        "child privacy": "Child privacy + PII",
        "child preset": "Use `child-privacy`",
        "biometric identity": "Biometric + money + identity",
        "biometric preset": "Use `biometric-identity`",
        "financial customer data preset": "Use `financial-customer-data`",
        "critical infrastructure AI": "critical infrastructure",
        "source trigger taxonomy": "source trigger taxonomy",
    }
    for label, marker in required_markers.items():
        if marker not in text:
            fail(errors, f"pressure-scenarios.md missing {label} marker: {marker}")


def validate_vitals_source_matrix(root: Path, errors: list[str], source_ids: set[str]) -> None:
    path = root / "references" / "vitals-source-matrix.md"
    text = path.read_text(encoding="utf-8")
    rows = []
    for line in text.splitlines():
        if not line.startswith("| "):
            continue
        if line.startswith("| Vital ") or line.startswith("|---"):
            continue
        parts = [part.strip() for part in line.strip("|").split("|")]
        if len(parts) == 4:
            rows.append(parts)
    vitals = [row[0] for row in rows]
    if vitals != EXPECTED_MATRIX_VITALS:
        fail(errors, "vitals-source-matrix.md must contain exactly the 12 expected vitals in taxonomy order")

    allowed_presets = set(SOURCE_PLANNER_REQUIRED_PHRASES) - SOURCE_PLANNER_NON_PRESET_PHRASES
    for token in re.findall(r"`([^`]+)`", text):
        if token not in source_ids and token not in allowed_presets:
            fail(errors, f"vitals-source-matrix.md references unknown source or preset: {token}")


def validate_pressure_backticks(root: Path, errors: list[str], source_ids: set[str]) -> None:
    path = root / "references" / "pressure-scenarios.md"
    text = path.read_text(encoding="utf-8")
    allowed_presets = set(SOURCE_PLANNER_REQUIRED_PHRASES) - SOURCE_PLANNER_NON_PRESET_PHRASES
    allowed = source_ids | allowed_presets | {
        "--surface",
        "behavioral-evaluation-protocol.md",
        "source_activation_plan.py",
    }
    for token in re.findall(r"`([^`]+)`", text):
        if token not in allowed:
            fail(errors, f"pressure-scenarios.md references unknown source, preset, or skill: {token}")


def validate_source_trigger_taxonomy(root: Path, errors: list[str]) -> None:
    path = root / "references" / "source-trigger-taxonomy.md"
    text = path.read_text(encoding="utf-8")
    inline_text = re.sub(r"```.*?```", "", text, flags=re.S)
    for phrase in SOURCE_TRIGGER_REQUIRED_PHRASES:
        if phrase not in text:
            fail(errors, f"source-trigger-taxonomy.md missing required phrase: {phrase}")

    allowed_presets = set(SOURCE_PLANNER_REQUIRED_PHRASES) - SOURCE_PLANNER_NON_PRESET_PHRASES
    allowed = allowed_presets | {
        "source-registry.md",
    }
    for token in re.findall(r"`([^`]+)`", inline_text):
        if token not in allowed:
            fail(errors, f"source-trigger-taxonomy.md references unknown preset or skill: {token}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("skill_root", type=Path)
    args = parser.parse_args()
    root = args.skill_root.resolve()
    errors: list[str] = []

    for rel in REQUIRED_REFERENCES:
        if not (root / rel).is_file():
            fail(errors, f"Missing required reference: {rel}")
    for banned in BANNED_AUXILIARY_FILES:
        if (root / banned).exists():
            fail(errors, f"Auxiliary file not allowed in skill package: {banned}")
    for rel in REQUIRED_SCRIPTS:
        if not (root / rel).is_file():
            fail(errors, f"Missing required script: {rel}")
    if any(part == "__pycache__" for path in root.rglob("*") for part in path.parts):
        fail(errors, "Generated __pycache__ directories are not allowed in the skill package")
    for path in (root / "references").glob("*.md"):
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) > 100 and "## Contents" not in lines[:20]:
            fail(errors, f"Long reference lacks a top contents section: {path.name}")
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        if any(ord(char) > 127 for char in text):
            fail(errors, f"Non-ASCII text is not allowed in skill file: {path.relative_to(root)}")
        if PLACEHOLDER_RE.search(text):
            fail(errors, f"Placeholder marker is not allowed in skill file: {path.relative_to(root)}")

    skill = read(root / "SKILL.md")
    if len(skill.splitlines()) > 500:
        fail(errors, "SKILL.md exceeds 500 lines; move details into references")
    frontmatter = parse_frontmatter(skill, errors)
    description = frontmatter.get("description", "")
    if len(description) > 1024:
        fail(errors, "Frontmatter description exceeds 1024 characters")
    for phrase in SKILL_REQUIRED_PHRASES:
        if phrase not in skill:
            fail(errors, f"SKILL.md missing required phrase: {phrase}")

    scope = read(root / "references" / "scope-boundary.md")
    for phrase in SCOPE_REQUIRED_PHRASES:
        if phrase not in scope:
            fail(errors, f"scope-boundary.md missing required phrase: {phrase}")

    report = read(root / "references" / "report-template.md")
    for phrase in REPORT_REQUIRED_PHRASES:
        if phrase not in report:
            fail(errors, f"report-template.md missing required phrase: {phrase}")

    vendor_patterns = read(root / "references" / "vendor-ai-reviewer-patterns.md")
    for phrase in VENDOR_REQUIRED_PHRASES:
        if phrase not in vendor_patterns:
            fail(errors, f"vendor-ai-reviewer-patterns.md missing required phrase: {phrase}")

    pressure = read(root / "references" / "pressure-scenarios.md")
    for phrase in PRESSURE_REQUIRED_PHRASES:
        if phrase not in pressure:
            fail(errors, f"pressure-scenarios.md missing required phrase: {phrase}")
    validate_pressure_scenarios(root, errors)

    behavior_protocol = read(root / "references" / "behavioral-evaluation-protocol.md")
    for phrase in BEHAVIOR_PROTOCOL_REQUIRED_PHRASES:
        if phrase not in behavior_protocol:
            fail(errors, f"behavioral-evaluation-protocol.md missing required phrase: {phrase}")

    validate_question_bank(root, errors)
    validate_source_trigger_taxonomy(root, errors)

    source_planner = read(root / "scripts" / "source_activation_plan.py")
    for phrase in SOURCE_PLANNER_REQUIRED_PHRASES:
        if phrase not in source_planner:
            fail(errors, f"source_activation_plan.py missing required preset: {phrase}")

    source_calibration = read(root / "scripts" / "calibrate_source_taxonomy.py")
    for phrase in SOURCE_CALIBRATION_REQUIRED_PHRASES:
        if phrase not in source_calibration:
            fail(errors, f"calibrate_source_taxonomy.py missing required phrase: {phrase}")

    registry = read(root / "references" / "source-registry.md")
    for phrase in SOURCE_REGISTRY_REQUIRED_PHRASES:
        if phrase not in registry:
            fail(errors, f"source-registry.md missing required phrase: {phrase}")
    ids_from_registry = registry_ids(registry)
    ids_from_links = registry_link_ids(registry)
    weights = json.loads(read(root / "references" / "source-weights.json"))
    weight_entries = weights.get("weights", [])
    seen_ids: set[str] = set()
    duplicate_ids: set[str] = set()
    for entry in weight_entries:
        source_id = entry.get("id")
        if source_id in seen_ids:
            duplicate_ids.add(source_id)
        seen_ids.add(source_id)
    if duplicate_ids:
        fail(errors, "Duplicate source IDs in source-weights.json: " + ", ".join(sorted(duplicate_ids)))
    ids_from_weights = {entry.get("id") for entry in weight_entries}

    missing_weights = sorted(ids_from_registry - ids_from_weights)
    extra_weights = sorted(ids_from_weights - ids_from_registry)
    if missing_weights:
        fail(errors, "Source IDs missing from source-weights.json: " + ", ".join(missing_weights))
    if extra_weights:
        fail(errors, "Source IDs missing from source-registry.md: " + ", ".join(extra_weights))
    missing_links = sorted(ids_from_registry - ids_from_links)
    if missing_links:
        fail(errors, "Source IDs missing from Current Source Links: " + ", ".join(missing_links))

    vital_principles = read(root / "references" / "vital-principles.md")
    for phrase in VITAL_PRINCIPLES_REQUIRED_PHRASES:
        if phrase not in vital_principles:
            fail(errors, f"vital-principles.md missing required phrase: {phrase}")

    vitals_source_matrix = read(root / "references" / "vitals-source-matrix.md")
    for phrase in VITALS_SOURCE_MATRIX_REQUIRED_PHRASES:
        if phrase not in vitals_source_matrix:
            fail(errors, f"vitals-source-matrix.md missing required phrase: {phrase}")
    validate_vitals_source_matrix(root, errors, ids_from_weights)
    validate_pressure_backticks(root, errors, ids_from_weights)

    for entry in weight_entries:
        source_id = entry.get("id", "")
        activation = str(entry.get("activation", "")).lower()
        if source_id in BANNED_ALWAYS_SOURCES:
            fail(errors, f"Generic code-quality source is not allowed: {source_id}")
        if activation in BANNED_ACTIVATIONS:
            fail(errors, f"Non-vital activation is not allowed for {source_id}: {activation}")
        if not activation:
            fail(errors, f"Source entry lacks activation: {source_id}")
        if not entry.get("tier"):
            fail(errors, f"Source entry lacks tier: {source_id}")
        elif entry.get("tier") not in ALLOWED_TIERS:
            fail(errors, f"Source entry has unknown tier: {source_id} -> {entry.get('tier')}")
        if not entry.get("scope"):
            fail(errors, f"Source entry lacks scope: {source_id}")
        try:
            weight = float(entry.get("default_weight"))
        except (TypeError, ValueError):
            fail(errors, f"Source entry has invalid default_weight: {source_id}")
            weight = 0
        if not 0 < weight <= 1:
            fail(errors, f"Source entry default_weight out of range: {source_id}")
        if entry.get("tier") == "D":
            if weight > 0.65:
                fail(errors, f"Tier D source weight too high: {source_id}")
            overlap = RESERVED_OFFICIAL_SCOPES.intersection(set(entry.get("scope", [])))
            if overlap:
                fail(errors, f"Tier D source {source_id} uses reserved official scopes: {', '.join(sorted(overlap))}")
        if entry.get("tier") == "B-provisional" and weight > 0.8:
            fail(errors, f"B-provisional source weight too high: {source_id}")

    metadata = read(root / "agents" / "openai.yaml")
    if "catastrophic vitals" not in metadata:
        fail(errors, "agents/openai.yaml should steer toward catastrophic vitals")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("GRILL_SKILL_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
