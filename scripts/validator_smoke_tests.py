#!/usr/bin/env python3
"""Smoke-test Grill validator failure modes on temporary skill copies."""

from __future__ import annotations

import argparse
import json
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

    with tempfile.TemporaryDirectory(prefix="grill-validator-") as tmp:
        tmp_path = Path(tmp)

        baseline = copy_skill(source, tmp_path / "baseline")
        expect_success([args.python, str(validator), str(baseline)], "baseline validator")
        expect_success([args.python, str(planner), "--skill-root", str(baseline), "--self-test"], "baseline source planner")
        expect_success_contains(
            [args.python, str(calibrator), "--skill-root", str(baseline)],
            "baseline source taxonomy calibration",
            ["SOURCE_TAXONOMY_CALIBRATION_OK 231 cases"],
        )
        expect_success_contains(
            [args.python, str(planner), "--skill-root", str(baseline), "--surface", "patient pdf summarized by llm"],
            "surface trigger taxonomy",
            ['"health-ephi"', '"agentic-llm"', '"source_trigger_taxonomy"'],
        )
        expect_success([args.python, str(link_checker), "--skill-root", str(baseline)], "baseline source link checker")

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
