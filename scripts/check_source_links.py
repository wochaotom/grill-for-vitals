#!/usr/bin/env python3
"""Audit Grill for Vitals source-registry link invariants."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


REGISTRY_ID_RE = re.compile(r"^\| `([^`]+)` \|")
LINK_RE = re.compile(r"^- `([^`]+)`: (https://\S+)$")


def error_detail(error: BaseException) -> str:
    return str(getattr(error, "reason", error))


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_registry_ids(text: str) -> set[str]:
    ids: set[str] = set()
    in_registry = False
    for line in text.splitlines():
        if line == "## Activation Registry":
            in_registry = True
            continue
        if in_registry and line == "## Current Source Links":
            break
        if not in_registry:
            continue
        match = REGISTRY_ID_RE.match(line)
        if match:
            ids.add(match.group(1))
    return ids


def parse_links(text: str) -> dict[str, list[str]]:
    links: dict[str, list[str]] = {}
    in_links = False
    for line in text.splitlines():
        if line == "## Current Source Links":
            in_links = True
            continue
        if in_links and line.startswith("## "):
            break
        if not in_links or not line.startswith("- `"):
            continue
        match = LINK_RE.match(line)
        if not match:
            raise ValueError(f"Malformed source link line: {line}")
        links.setdefault(match.group(1), []).append(match.group(2))
    return links


def parse_weight_ids(skill_root: Path) -> set[str]:
    data = json.loads(read(skill_root / "references" / "source-weights.json"))
    return {entry["id"] for entry in data.get("weights", [])}


def check_online(url: str, timeout: float) -> tuple[str, int | None, str | None]:
    request = Request(url, method="HEAD", headers={"User-Agent": "grill-for-vitals-source-audit/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return "ok", response.status, None
    except HTTPError as error:
        request = Request(url, method="GET", headers={"User-Agent": "grill-for-vitals-source-audit/1.0"})
        try:
            with urlopen(request, timeout=timeout) as response:
                return "ok", response.status, None
        except HTTPError as second_error:
            if second_error.code == 403:
                return "warning", second_error.code, "forbidden to bot/user-agent"
            return "error", second_error.code, second_error.reason
        except (OSError, TimeoutError, URLError) as second_error:
            return "error", None, error_detail(second_error)
    except (OSError, TimeoutError, URLError) as error:
        return "error", None, error_detail(error)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--online", action="store_true", help="Also perform best-effort live URL checks")
    parser.add_argument("--timeout", type=float, default=10.0, help="Per-URL timeout for --online checks")
    args = parser.parse_args()

    skill_root = args.skill_root.resolve()
    registry_text = read(skill_root / "references" / "source-registry.md")
    registry_ids = parse_registry_ids(registry_text)
    weight_ids = parse_weight_ids(skill_root)
    links = parse_links(registry_text)

    errors: list[str] = []
    warnings: list[str] = []

    missing_links = sorted(registry_ids - set(links))
    unknown_link_ids = sorted(set(links) - registry_ids)
    weight_mismatches = sorted(registry_ids ^ weight_ids)

    if missing_links:
        errors.append(f"source IDs without links: {', '.join(missing_links)}")
    if unknown_link_ids:
        errors.append(f"links for unknown source IDs: {', '.join(unknown_link_ids)}")
    if weight_mismatches:
        errors.append(f"registry/source-weights ID mismatch: {', '.join(weight_mismatches)}")

    seen_pairs: set[tuple[str, str]] = set()
    seen_urls: dict[str, str] = {}
    for source_id, urls in sorted(links.items()):
        for url in urls:
            pair = (source_id, url)
            if pair in seen_pairs:
                errors.append(f"duplicate source link: {source_id} {url}")
            seen_pairs.add(pair)
            previous_id = seen_urls.get(url)
            if previous_id and previous_id != source_id:
                errors.append(f"URL shared by multiple source IDs: {previous_id}, {source_id}: {url}")
            seen_urls[url] = source_id

    online_results: list[dict] = []
    if args.online:
        for source_id, urls in sorted(links.items()):
            for url in urls:
                status, http_status, detail = check_online(url, args.timeout)
                result = {"source_id": source_id, "url": url, "status": status, "http_status": http_status}
                if detail:
                    result["detail"] = detail
                online_results.append(result)
                if status == "error":
                    errors.append(f"live URL check failed for {source_id}: {url}: {http_status or detail}")
                elif status == "warning":
                    warnings.append(f"live URL check warning for {source_id}: {url}: {http_status} {detail}")

    if errors:
        print("SOURCE_LINKS_FAILED", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        if warnings:
            for warning in warnings:
                print(f"- warning: {warning}", file=sys.stderr)
        return 1

    summary = {
        "source_count": len(registry_ids),
        "link_count": sum(len(urls) for urls in links.values()),
        "warnings": warnings,
    }
    if args.online:
        summary["online_results"] = online_results
    print("SOURCE_LINKS_OK " + json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
