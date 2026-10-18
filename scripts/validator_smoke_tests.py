#!/usr/bin/env python3
"""Smoke-test Grill validator failure modes on temporary skill copies."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run(command: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True)


def replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"pattern not found in {path}: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def copy_skill(src: Path, dst: Path) -> Path:
    target = dst / "grill-for-vitals"
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    shutil.copytree(src, target, ignore=ignore)
    return target


def expect_success(command: list[str], label: str) -> None:
    result = run(command)
    if result.returncode != 0:
        raise AssertionError(f"{label} should pass\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")


def expect_success_contains(command: list[str], label: str, needles: list[str]) -> None:
    result = run(command)
    if result.returncode != 0:
        raise AssertionError(f"{label} should pass\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
    missing = [needle for needle in needles if needle not in result.stdout]
    if missing:
        raise AssertionError(
            f"{label} missing expected output: {', '.join(missing)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def expect_failure(command: list[str], label: str) -> None:
    result = run(command)
    if result.returncode == 0:
        raise AssertionError(f"{label} should fail\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")


def write_behavior_results(path: Path, skill_root: Path, mutation=None, case_ids=None) -> None:
    scenario_revision = hashlib.sha256(
        (skill_root / "references" / "pressure-scenarios.md").read_bytes()
    ).hexdigest()
    deterministic_checks = {
        "answer_shape": True,
        "no_forbidden_claim": True,
        "question_limit": True,
        "receipt_complete": True,
    }
    expert_checks = {
        "catastrophe_path": True,
        "evidence_gate": True,
        "handoff_or_escalation": True,
        "scope_gate": True,
        "source_routing": True,
        "vital_selection": True,
    }
    hard_failures = {
        "catastrophic_miss": False,
        "compliance_overclaim": False,
        "missing_handoff": False,
        "source_authority_inversion": False,
        "unsafe_action": False,
    }
    if case_ids is None:
        case_ids = re.findall(
            r"\|\s*(GFV-\d{3})\s*\|",
            (skill_root / "references" / "pressure-scenarios.md").read_text(encoding="utf-8"),
        )
    records = []
    for variant in ("baseline", "candidate"):
        for case_id in case_ids:
            for repetition in range(1, 4):
                transcript_sha256 = hashlib.sha256(
                    f"{variant}:{case_id}:{repetition}".encode("ascii")
                ).hexdigest()
                records.append(
                    {
                        "case_id": case_id,
                        "variant": variant,
                        "repetition": repetition,
                        "model": "test-model",
                        "runtime": "test-runtime",
                        "tool_policy": "read-only",
                        "scenario_revision": scenario_revision,
                        "skill_revision": f"{variant}-revision",
                        "transcript_sha256": transcript_sha256,
                        "runner_id": "runner-a",
                        "reviewer_id": "reviewer-b",
                        "deterministic_checks": deterministic_checks.copy(),
                        "expert_checks": expert_checks.copy(),
                        "hard_failures": hard_failures.copy(),
                    }
                )
    if mutation is not None:
        mutation(records)
    path.write_text("\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()

    source = args.skill_root.resolve()
    validator = source / "scripts" / "validate_grill_skill.py"
    planner = source / "scripts" / "source_activation_plan.py"
    calibrator = source / "scripts" / "calibrate_source_taxonomy.py"
    link_checker = source / "scripts" / "check_source_links.py"
    behavior_evaluator = source / "scripts" / "evaluate_behavioral_runs.py"

    with tempfile.TemporaryDirectory(prefix="grill-validator-") as tmp:
        tmp_path = Path(tmp)

        baseline = copy_skill(source, tmp_path / "baseline")
        expect_success([args.python, str(validator), str(baseline)], "baseline validator")
        expect_success([args.python, str(planner), "--skill-root", str(baseline), "--self-test"], "baseline source planner")
        expect_success_contains(
            [args.python, str(calibrator), "--skill-root", str(baseline)],
            "baseline source taxonomy calibration",
            ["SOURCE_TAXONOMY_CALIBRATION_OK 238 cases"],
        )
        expect_success_contains(
            [args.python, str(planner), "--skill-root", str(baseline), "--surface", "patient pdf summarized by llm"],
            "surface trigger taxonomy",
            ['"health-ephi"', '"agentic-llm"', '"source_trigger_taxonomy"'],
        )
        expect_success([args.python, str(link_checker), "--skill-root", str(baseline)], "baseline source link checker")

        behavior_results = tmp_path / "behavior-results.jsonl"
        write_behavior_results(behavior_results, baseline)
        expect_success_contains(
            [
                args.python,
                str(baseline / "scripts" / behavior_evaluator.name),
                "--skill-root",
                str(baseline),
                "--results",
                str(behavior_results),
            ],
            "baseline behavior evaluation",
            ["BEHAVIOR_EVAL_PROMOTE", '"minimum_repetitions": 3'],
        )

        expect_failure(
            [
                args.python,
                str(baseline / "scripts" / behavior_evaluator.name),
                "--skill-root",
                str(baseline),
                "--results",
                str(behavior_results),
                "--minimum-repetitions",
                "1",
            ],
            "behavior evaluation weakened repetition floor",
        )

        mixed_skill_revision = tmp_path / "behavior-mixed-skill-revision.jsonl"
        write_behavior_results(
            mixed_skill_revision,
            baseline,
            lambda records: next(record for record in records if record["variant"] == "candidate").update(
                {"skill_revision": "different-candidate-revision"}
            ),
        )
        expect_failure(
            [
                args.python,
                str(baseline / "scripts" / behavior_evaluator.name),
                "--skill-root",
                str(baseline),
                "--results",
                str(mixed_skill_revision),
            ],
            "behavior evaluation mixed skill revision",
        )

        same_skill_revision = tmp_path / "behavior-same-skill-revision.jsonl"
        write_behavior_results(
            same_skill_revision,
            baseline,
            lambda records: [
                record.update({"skill_revision": "same-revision"}) for record in records
            ],
        )
        expect_failure(
            [
                args.python,
                str(baseline / "scripts" / behavior_evaluator.name),
                "--skill-root",
                str(baseline),
                "--results",
                str(same_skill_revision),
            ],
            "behavior evaluation identical skill revisions",
        )

        config_drift = tmp_path / "behavior-config-drift.jsonl"
        write_behavior_results(
            config_drift,
            baseline,
            lambda records: next(record for record in records if record["variant"] == "candidate").update(
                {"runtime": "different-runtime"}
            ),
        )
        expect_failure(
            [args.python, str(baseline / "scripts" / behavior_evaluator.name), "--skill-root", str(baseline), "--results", str(config_drift)],
            "behavior evaluation config drift",
        )

        hard_failure = tmp_path / "behavior-hard-failure.jsonl"
        write_behavior_results(
            hard_failure,
            baseline,
            lambda records: next(record for record in records if record["variant"] == "candidate")[
                "hard_failures"
            ].update({"compliance_overclaim": True}),
        )
        expect_failure(
            [args.python, str(baseline / "scripts" / behavior_evaluator.name), "--skill-root", str(baseline), "--results", str(hard_failure)],
            "behavior evaluation hard failure",
        )

        score_regression = tmp_path / "behavior-score-regression.jsonl"
        write_behavior_results(
            score_regression,
            baseline,
            lambda records: next(record for record in records if record["variant"] == "candidate")[
                "expert_checks"
            ].update({"handoff_or_escalation": False}),
        )
        expect_failure(
            [args.python, str(baseline / "scripts" / behavior_evaluator.name), "--skill-root", str(baseline), "--results", str(score_regression)],
            "behavior evaluation per-check regression",
        )

        incomplete_results = tmp_path / "behavior-incomplete.jsonl"
        write_behavior_results(incomplete_results, baseline, lambda records: records.pop())
        expect_failure(
            [args.python, str(baseline / "scripts" / behavior_evaluator.name), "--skill-root", str(baseline), "--results", str(incomplete_results)],
            "behavior evaluation incomplete matched set",
        )

        self_reviewed = tmp_path / "behavior-self-reviewed.jsonl"
        write_behavior_results(
            self_reviewed,
            baseline,
            lambda records: next(record for record in records if record["variant"] == "candidate").update(
                {"reviewer_id": "runner-a"}
            ),
        )
        expect_failure(
            [args.python, str(baseline / "scripts" / behavior_evaluator.name), "--skill-root", str(baseline), "--results", str(self_reviewed)],
            "behavior evaluation self review",
        )

        partial_results = tmp_path / "behavior-partial.jsonl"
        write_behavior_results(
            partial_results,
            baseline,
            case_ids=("GFV-001", "GFV-002"),
        )
        expect_failure(
            [args.python, str(baseline / "scripts" / behavior_evaluator.name), "--skill-root", str(baseline), "--results", str(partial_results)],
            "behavior evaluation partial release suite",
        )

        missing_behavior_evaluator = copy_skill(source, tmp_path / "missing-behavior-evaluator")
        (missing_behavior_evaluator / "scripts" / "evaluate_behavioral_runs.py").unlink()
        expect_failure(
            [args.python, str(validator), str(missing_behavior_evaluator)],
            "missing behavior evaluator",
        )

        missing_behavior_protocol = copy_skill(source, tmp_path / "missing-behavior-protocol")
        behavior_protocol = missing_behavior_protocol / "references" / "behavioral-evaluation-protocol.md"
        if behavior_protocol.exists():
            behavior_protocol.unlink()
        expect_failure(
            [args.python, str(validator), str(missing_behavior_protocol)],
            "missing behavior evaluation protocol",
        )

        broken_behavior_protocol = copy_skill(source, tmp_path / "broken-behavior-protocol")
        behavior_protocol = broken_behavior_protocol / "references" / "behavioral-evaluation-protocol.md"
        if behavior_protocol.exists():
            replace(behavior_protocol, "## Baseline and candidate parity", "## Loose comparison")
        expect_failure(
            [args.python, str(validator), str(broken_behavior_protocol)],
            "behavior evaluation protocol contract",
        )

        broken_behavior_skill_link = copy_skill(source, tmp_path / "broken-behavior-skill-link")
        skill_path = broken_behavior_skill_link / "SKILL.md"
        if "behavioral-evaluation-protocol.md" in skill_path.read_text(encoding="utf-8"):
            skill_path.write_text(
                skill_path.read_text(encoding="utf-8").replace(
                    "behavioral-evaluation-protocol.md",
                    "pressure-scenarios.md",
                ),
                encoding="utf-8",
            )
        expect_failure(
            [args.python, str(validator), str(broken_behavior_skill_link)],
            "missing behavior protocol link from runtime skill",
        )

        broken_pressure = copy_skill(source, tmp_path / "broken-pressure")
        replace(broken_pressure / "references" / "pressure-scenarios.md", "GFV-015", "GFV-999")
        expect_failure([args.python, str(validator), str(broken_pressure)], "non-sequential pressure scenario IDs")

        broken_pressure_token = copy_skill(source, tmp_path / "broken-pressure-token")
        replace(broken_pressure_token / "references" / "pressure-scenarios.md", "`payments-cardholder`", "`fake-preset`")
        expect_failure([args.python, str(validator), str(broken_pressure_token)], "unknown pressure scenario preset")

        broken_question_token = copy_skill(source, tmp_path / "broken-question-token")
        replace(broken_question_token / "references" / "question-bank.md", "`safety-ot`", "`fake-preset`")
        expect_failure([args.python, str(validator), str(broken_question_token)], "unknown question-bank preset")

        broken_taxonomy_token = copy_skill(source, tmp_path / "broken-taxonomy-token")
        replace(broken_taxonomy_token / "references" / "source-trigger-taxonomy.md", "`health-ephi`", "`fake-preset`")
        expect_failure([args.python, str(validator), str(broken_taxonomy_token)], "unknown source trigger preset")

        broken_paid_api_trigger = copy_skill(source, tmp_path / "broken-paid-api-trigger")
        replace(
            broken_paid_api_trigger / "references" / "source-trigger-taxonomy.md",
            "pay APIs",
            "paid endpoints",
        )
        expect_failure(
            [args.python, str(validator), str(broken_paid_api_trigger)],
            "missing paid API trigger documentation",
        )

        broken_taxonomy_calibration = copy_skill(source, tmp_path / "broken-taxonomy-calibration")
        replace(
            broken_taxonomy_calibration / "scripts" / "source_activation_plan.py",
            "signal_matches(surface_text, signal)",
            "signal in surface_text",
        )
        expect_failure(
            [args.python, str(calibrator), "--skill-root", str(broken_taxonomy_calibration)],
            "source taxonomy substring overmatch",
        )

        broken_no_compliance_guard = copy_skill(source, tmp_path / "broken-no-compliance-guard")
        replace(
            broken_no_compliance_guard / "scripts" / "source_activation_plan.py",
            '"Do not claim compliance or readiness from this plan.",',
            '"Do not claim readiness from this plan.",',
        )
        expect_failure(
            [args.python, str(calibrator), "--skill-root", str(broken_no_compliance_guard)],
            "missing no-compliance calibration guard",
        )

        broken_matrix = copy_skill(source, tmp_path / "broken-matrix")
        matrix = broken_matrix / "references" / "vitals-source-matrix.md"
        matrix.write_text(
            matrix.read_text(encoding="utf-8").replace(
                "| Cost/availability/runaway loops |",
                "| Extra generic review | Anything tidy | `owasp-top10` | Generic issue list |\n| Cost/availability/runaway loops |",
                1,
            ),
            encoding="utf-8",
        )
        expect_failure([args.python, str(validator), str(broken_matrix)], "extra matrix vital")

        broken_vendor_scope = copy_skill(source, tmp_path / "broken-vendor-scope")
        replace(broken_vendor_scope / "references" / "source-weights.json", "vendor-incident-response", "incident-response")
        expect_failure([args.python, str(validator), str(broken_vendor_scope)], "Tier D reserved official scope")

        broken_vendor_ot_scope = copy_skill(source, tmp_path / "broken-vendor-ot-scope")
        replace(broken_vendor_ot_scope / "references" / "source-weights.json", "model-provider-boundary", "operational-technology")
        expect_failure([args.python, str(validator), str(broken_vendor_ot_scope)], "Tier D OT scope")

        broken_links = copy_skill(source, tmp_path / "broken-links")
        replace(broken_links / "references" / "source-registry.md", "- `pci-dss`: https://www.pcisecuritystandards.org/standards/pci-dss/\n", "")
        expect_failure([args.python, str(validator), str(broken_links)], "missing source URL")

        malformed_links = copy_skill(source, tmp_path / "malformed-links")
        replace(
            malformed_links / "references" / "source-registry.md",
            "- `pci-dss`: https://www.pcisecuritystandards.org/standards/pci-dss/",
            "- `pci-dss` https://www.pcisecuritystandards.org/standards/pci-dss/",
        )
        expect_failure([args.python, str(link_checker), "--skill-root", str(malformed_links)], "malformed source URL")

        unknown_link = copy_skill(source, tmp_path / "unknown-link")
        replace(
            unknown_link / "references" / "source-registry.md",
            "## Source Admission Rules",
            "- `unknown-source`: https://example.com\n\n## Source Admission Rules",
        )
        expect_failure([args.python, str(link_checker), "--skill-root", str(unknown_link)], "unknown source URL")

        unpreset_source = copy_skill(source, tmp_path / "unpreset-source")
        registry_path = unpreset_source / "references" / "source-registry.md"
        replace(
            registry_path,
            "## Current Source Links",
            "| `fake-official-source` | A | Fake catastrophic vital | Fake source for planner smoke test. |\n\n## Current Source Links",
        )
        replace(
            registry_path,
            "## Source Admission Rules",
            "- `fake-official-source`: https://example.com\n\n## Source Admission Rules",
        )
        weights_path = unpreset_source / "references" / "source-weights.json"
        weights = json.loads(weights_path.read_text(encoding="utf-8"))
        weights["weights"].append(
            {
                "id": "fake-official-source",
                "name": "Fake official source",
                "tier": "A",
                "default_weight": 0.5,
                "scope": ["fake-scope"],
                "activation": "fake_activation",
            }
        )
        weights_path.write_text(json.dumps(weights, indent=2) + "\n", encoding="utf-8")
        expect_failure([args.python, str(planner), "--skill-root", str(unpreset_source), "--self-test"], "unexpected unpreset source")

        broken_vendor_weight = copy_skill(source, tmp_path / "broken-vendor-weight")
        weights_path = broken_vendor_weight / "references" / "source-weights.json"
        weights = json.loads(weights_path.read_text(encoding="utf-8"))
        for entry in weights["weights"]:
            if entry["id"] == "coderabbit-ai-review-security":
                entry["default_weight"] = 0.95
                break
        weights_path.write_text(json.dumps(weights, indent=2) + "\n", encoding="utf-8")
        expect_failure([args.python, str(validator), str(broken_vendor_weight)], "Tier D vendor weight too high")

        placeholder_marker = "TO" + "DO"
        broken_placeholder = copy_skill(source, tmp_path / "broken-placeholder")
        with (broken_placeholder / "references" / "scope-boundary.md").open("a", encoding="utf-8") as handle:
            handle.write(f"\n{placeholder_marker}: should fail validation\n")
        expect_failure([args.python, str(validator), str(broken_placeholder)], "placeholder marker")

        broken_non_ascii = copy_skill(source, tmp_path / "broken-non-ascii")
        with (broken_non_ascii / "references" / "scope-boundary.md").open("a", encoding="utf-8") as handle:
            handle.write("\n" + chr(0x2603) + "\n")
        expect_failure([args.python, str(validator), str(broken_non_ascii)], "non-ASCII text")

    print("VALIDATOR_SMOKE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
