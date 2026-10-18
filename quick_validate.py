#!/usr/bin/env python3
"""Run the fast local validation suite for Grill for Vitals."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


COMMANDS = [
    [sys.executable, "scripts/validate_grill_skill.py", "."],
    [sys.executable, "scripts/source_activation_plan.py", "--self-test"],
    [sys.executable, "scripts/calibrate_source_taxonomy.py"],
    [sys.executable, "scripts/check_source_links.py"],
]


def main() -> int:
    for command in COMMANDS:
        print("+ " + " ".join(command))
        result = subprocess.run(command, cwd=ROOT)
        if result.returncode != 0:
            return result.returncode
    print("QUICK_VALIDATE_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
