#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DEFAULT_TARGETS = ("docs_bilingual", "openspec")
SUPPORTED_SUFFIXES = {".md", ".yaml", ".yml"}
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+] |\d+[.)] )\s*(?:\[[ xX]\]\s*)?(?P<body>.+?)\s*$")
BARE_CODE_LIST_RE = re.compile(
    r"^`[^`]+`(?:\s*(?:[,，、/])\s*`[^`]+`|\s+(?:and|or)\s+`[^`]+`)*[。.]?$"
)


@dataclass(frozen=True)
class Finding:
    relative_path: str
    line: int
    text: str
    reason: str
    suggestion: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def default_baseline_path(root: Path) -> Path:
    return root / "tools" / "name_clarity_baseline.json"


def iter_target_files(root: Path, targets: Iterable[str]) -> list[Path]:
    files: set[Path] = set()
    for target in targets:
        base = (root / target).resolve()
        if not base.exists():
            continue
        if base.is_file():
            if base.suffix.lower() in SUPPORTED_SUFFIXES:
                files.add(base)
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES:
                files.add(path)
    return sorted(files)


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split())


def is_bare_code_name_list_item(line: str) -> bool:
    match = LIST_ITEM_RE.match(line)
    if not match:
        return False
    body = normalize_text(match.group("body"))
    return bool(BARE_CODE_LIST_RE.fullmatch(body))


def find_findings(root: Path, targets: Iterable[str]) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    files = iter_target_files(root, targets)
    for path in files:
        relative_path = path.relative_to(root).as_posix()
        for index, line in enumerate(read_text(path).splitlines(), start=1):
            if not is_bare_code_name_list_item(line):
                continue
            findings.append(
                Finding(
                    relative_path=relative_path,
                    line=index,
                    text=normalize_text(line),
                    reason="bare_code_name_list_item",
                    suggestion="Add a short purpose phrase after the name, for example `name` - explains what it is for.",
                )
            )
    return findings, len(files)


def load_baseline(path: Path) -> dict[str, Counter[str]]:
    if not path.exists():
        return {}
    payload = json.loads(read_text(path))
    raw_allowed = payload.get("allowed_findings", {})
    baseline: dict[str, Counter[str]] = {}
    for relative_path, entries in raw_allowed.items():
        baseline[relative_path] = Counter(normalize_text(str(entry)) for entry in entries)
    return baseline


def write_baseline(path: Path, findings: list[Finding], targets: Iterable[str]) -> None:
    grouped: dict[str, list[str]] = defaultdict(list)
    for finding in findings:
        grouped[finding.relative_path].append(finding.text)
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": "name_clarity_baseline",
        "scope": list(targets),
        "note": (
            "Compatibility baseline for pre-existing bare code-name list items. "
            "Do not add entries for new work; fix new findings by adding short purpose explanations."
        ),
        "counts": {
            "allowed_findings": sum(len(values) for values in grouped.values()),
            "files": len(grouped),
        },
        "allowed_findings": {path: sorted(values) for path, values in sorted(grouped.items())},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def split_findings_by_baseline(
    findings: list[Finding],
    baseline: dict[str, Counter[str]],
) -> tuple[list[Finding], list[Finding]]:
    remaining = {path: Counter(counter) for path, counter in baseline.items()}
    allowed: list[Finding] = []
    violations: list[Finding] = []
    for finding in findings:
        counter = remaining.get(finding.relative_path)
        if counter and counter.get(finding.text, 0) > 0:
            counter[finding.text] -= 1
            allowed.append(finding)
            continue
        violations.append(finding)
    return allowed, violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check docs_bilingual and openspec for bare code-name list items that lack purpose explanations."
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument(
        "--target",
        action="append",
        dest="targets",
        default=None,
        help="Target file or directory relative to root. Defaults to docs_bilingual and openspec.",
    )
    parser.add_argument("--baseline", default=None, help="Baseline JSON path. Defaults to tools/name_clarity_baseline.json.")
    parser.add_argument("--no-baseline", action="store_true", help="Do not allow compatibility-baseline findings.")
    parser.add_argument("--update-baseline", action="store_true", help="Rewrite the baseline from current findings and exit.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Repository root does not exist: {root}")
    targets = tuple(args.targets or DEFAULT_TARGETS)
    baseline_path = Path(args.baseline).resolve() if args.baseline else default_baseline_path(root)

    findings, checked_files = find_findings(root, targets)
    if args.update_baseline:
        write_baseline(baseline_path, findings, targets)
        if not args.json:
            print(f"Updated name-clarity baseline: {baseline_path}")
            print(f"Allowed findings recorded: {len(findings)}")
        else:
            print(
                json.dumps(
                    {
                        "schema_version": 1,
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "check_name": "name_clarity_rules",
                        "ok": True,
                        "updated_baseline": str(baseline_path),
                        "counts": {
                            "checked_files": checked_files,
                            "baseline_findings_written": len(findings),
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
        return 0

    baseline = {} if args.no_baseline else load_baseline(baseline_path)
    allowed, violations = split_findings_by_baseline(findings, baseline)
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": "name_clarity_rules",
        "ok": len(violations) == 0,
        "errors": [
            f"{finding.relative_path}:{finding.line}: {finding.reason}: {finding.text}"
            for finding in violations
        ],
        "warnings": [],
        "info": [
            "Targets scanned: " + ", ".join(targets),
            "Compatibility baseline: " + ("disabled" if args.no_baseline else str(baseline_path)),
        ],
        "root": str(root),
        "targets": list(targets),
        "baseline_path": None if args.no_baseline else str(baseline_path),
        "counts": {
            "checked_files": checked_files,
            "findings_total": len(findings),
            "baseline_allowed": len(allowed),
            "violations": len(violations),
        },
        "violations": [asdict(finding) for finding in violations],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    if violations:
        print("Name clarity rules check failed:")
        for finding in violations:
            print(f"  - {finding.relative_path}:{finding.line}: {finding.text}")
            print(f"    {finding.suggestion}")
        print(f"Checked files: {checked_files}")
        print(f"Baseline allowed findings: {len(allowed)}")
        return 1

    print("Name clarity rules check passed.")
    print(f"Checked files: {checked_files}")
    print(f"Baseline allowed findings: {len(allowed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
