#!/usr/bin/env python3
"""Check that Grill for Vitals does not drift into Code Hygiene's corpus."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ALLOWED_OVERLAP = {
    "cisa-secure-by-design",
    "mitre-cwe-top25",
    "nist-ssdf",
    "owasp-asvs",
}

BANNED_GRILL_SOURCES = {
    "google-eng-practices",
    "google-testing",
    "google-style-guides",
    "google-developer-docs-style",
    "python-core-docs",
    "python-testing-packaging",
    "wcag-22",
    "opentelemetry",
    "microsoft-rest-api-guidelines",
    "semver",
}


def load_ids(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {entry["id"] for entry in data.get("weights", [])}


def default_code_hygiene_root(grill_root: Path) -> Path:
    return grill_root.parent / "code-hygiene-compounder"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--grill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--code-hygiene-root", type=Path)
    args = parser.parse_args()

    grill_root = args.grill_root.resolve()
    code_hygiene_root = (args.code_hygiene_root or default_code_hygiene_root(grill_root)).resolve()
    grill_weights = grill_root / "references" / "source-weights.json"
    hygiene_weights = code_hygiene_root / "references" / "source-weights.json"

    if not hygiene_weights.exists():
        print(f"SKIP: code hygiene source weights not found at {hygiene_weights}")
        return 0

    grill_ids = load_ids(grill_weights)
    hygiene_ids = load_ids(hygiene_weights)
    overlap = grill_ids & hygiene_ids
    unexpected = sorted(overlap - ALLOWED_OVERLAP)
    banned = sorted(grill_ids & BANNED_GRILL_SOURCES)

    if unexpected:
        print("ERROR: unexpected source overlap with code-hygiene-compounder: " + ", ".join(unexpected), file=sys.stderr)
        return 1
    if banned:
        print("ERROR: generic code-hygiene sources are present in Grill: " + ", ".join(banned), file=sys.stderr)
        return 1

    print(
        "CODE_HYGIENE_OVERLAP_OK "
        + json.dumps(
            {
                "allowed_overlap": sorted(overlap),
                "grill_only_count": len(grill_ids - hygiene_ids),
                "code_hygiene_only_count": len(hygiene_ids - grill_ids),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
