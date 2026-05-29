#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DEFAULT_TARGETS = ("docs_bilingual", "openspec")
DEFAULT_SEMANTIC_TARGETS = ("docs_bilingual", "openspec", "docs")
SUPPORTED_SUFFIXES = {".md", ".yaml", ".yml"}
MARKDOWN_SUFFIXES = {".md"}
LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+] |\d+[.)] )\s*(?:\[[ xX]\]\s*)?(?P<body>.+?)\s*$")
BARE_CODE_LIST_RE = re.compile(
    r"^`[^`]+`(?:\s*(?:[,，、/])\s*`[^`]+`|\s+(?:and|or)\s+`[^`]+`)*[。.]?$"
)
CODE_SPAN_RE = re.compile(r"`([^`]+)`")
SEMANTIC_ASSIGNMENT_RE = re.compile(
    r"\b(?P<field>[A-Za-z][A-Za-z0-9_]*(?:_status|_state|_decision|_phase|_reason|_count|_mode|_type|_gate))"
    r"\s*=\s*(?P<value>[A-Za-z0-9_-]+)\b"
)
EXPLANATION_HINT_RE = re.compile(
    r"\b("
    r"field|fields|record|records|means|meaning|indicates|describes|"
    r"workflow|operator|allowed value|gate condition|transition that|moves|"
    r"when|whether|blocks|phase progress|return path|control loop|"
    r"runtime|state|policy"
    r")\b|"
    r"[\u4e00-\u9fff]*(运行含义|字段|取值|含义|表示|说明|用于|回退|阶段|门禁|控制|解释|语义)[\u4e00-\u9fff]*",
    re.IGNORECASE,
)
SEMANTIC_FIELD_SUFFIXES = (
    "_status",
    "_state",
    "_decision",
    "_phase",
    "_reason",
    "_count",
    "_mode",
    "_type",
    "_gate",
)
SEMANTIC_HYPHEN_KEYWORDS = {
    "monitor",
    "return",
    "transition",
    "gate",
    "decision",
    "status",
    "phase",
    "control",
}
SEMANTIC_VALUE_TOKENS = {
    "clear",
    "blocked",
    "needs_decision",
    "continue",
    "adjust-current",
    "return-open",
    "return-design",
    "return-build",
    "return-verify",
    "stop",
}
IGNORED_TOKEN_EXTENSIONS = (
    ".py",
    ".pyw",
    ".md",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".sh",
    ".bash",
    ".ps1",
    ".cmd",
    ".bat",
    ".mjs",
    ".js",
    ".ts",
    ".tsx",
    ".test.py",
    ".test.mjs",
    ".txt",
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


def iter_semantic_target_files(root: Path, targets: Iterable[str]) -> list[Path]:
    files: set[Path] = set()
    for target in targets:
        base = (root / target).resolve()
        if not base.exists():
            continue
        if base.is_file():
            if base.suffix.lower() in MARKDOWN_SUFFIXES:
                files.add(base)
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in MARKDOWN_SUFFIXES:
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


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def is_git_repository(root: Path) -> bool:
    result = run_git(root, ["rev-parse", "--is-inside-work-tree"])
    return result.returncode == 0 and result.stdout.strip() == "true"


def forward_base_ref(root: Path) -> str | None:
    for ref in ("main", "HEAD"):
        result = run_git(root, ["merge-base", ref, "HEAD"])
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    return None


def parse_changed_lines_from_diff(diff_text: str) -> dict[str, set[int]]:
    changed: dict[str, set[int]] = defaultdict(set)
    current_path: str | None = None
    new_line = 0
    for raw_line in diff_text.splitlines():
        if raw_line.startswith("+++ b/"):
            current_path = raw_line[len("+++ b/") :]
            continue
        if raw_line.startswith("+++ /dev/null"):
            current_path = None
            continue
        if raw_line.startswith("@@ "):
            match = re.search(r"\+(\d+)(?:,(\d+))?", raw_line)
            if match:
                new_line = int(match.group(1))
            continue
        if current_path is None:
            continue
        if raw_line.startswith("+") and not raw_line.startswith("+++ "):
            changed[current_path].add(new_line)
            new_line += 1
        elif raw_line.startswith("-") and not raw_line.startswith("--- "):
            continue
        elif raw_line.startswith("\\"):
            continue
        else:
            new_line += 1
    return dict(changed)


def collect_forward_changed_lines(root: Path, semantic_targets: Iterable[str]) -> dict[str, set[int]] | None:
    if not is_git_repository(root):
        return None
    base = forward_base_ref(root)
    if not base:
        return None
    target_args = ["--", *semantic_targets]
    result = run_git(root, ["diff", "--unified=0", "--no-ext-diff", base, *target_args])
    if result.returncode != 0:
        return None
    changed = parse_changed_lines_from_diff(result.stdout)
    untracked = run_git(root, ["ls-files", "--others", "--exclude-standard", "--", *semantic_targets])
    if untracked.returncode == 0:
        for raw_path in untracked.stdout.splitlines():
            path = (root / raw_path).resolve()
            if path.suffix.lower() not in MARKDOWN_SUFFIXES or not path.exists():
                continue
            changed[Path(raw_path).as_posix()] = set(range(1, len(read_text(path).splitlines()) + 1))
    return changed


def is_ignored_code_token(token: str) -> bool:
    token = token.strip()
    lowered = token.lower()
    if not token:
        return True
    if "://" in lowered or "/" in token or "\\" in token:
        return True
    if " " in token:
        return True
    if lowered.endswith(IGNORED_TOKEN_EXTENSIONS):
        return True
    if re.search(r"\.[A-Za-z0-9]{1,8}$", token):
        return True
    return False


def is_semantic_token(token: str) -> bool:
    token = token.strip()
    lowered = token.lower()
    if is_ignored_code_token(token):
        return False
    assignment = SEMANTIC_ASSIGNMENT_RE.fullmatch(token)
    if assignment:
        return True
    if lowered in SEMANTIC_VALUE_TOKENS:
        return True
    if any(lowered.endswith(suffix) for suffix in SEMANTIC_FIELD_SUFFIXES):
        return True
    if "-" in lowered:
        parts = set(lowered.split("-"))
        return bool(parts & SEMANTIC_HYPHEN_KEYWORDS)
    return False


def semantic_terms_in_line(line: str) -> set[str]:
    terms: set[str] = set()
    for token in CODE_SPAN_RE.findall(line):
        token = token.strip()
        assignment = SEMANTIC_ASSIGNMENT_RE.fullmatch(token)
        if assignment:
            terms.add(assignment.group("field"))
            terms.add(f"{assignment.group('field')}={assignment.group('value')}")
            continue
        if is_semantic_token(token):
            terms.add(token)
    for assignment in SEMANTIC_ASSIGNMENT_RE.finditer(CODE_SPAN_RE.sub("", line)):
        terms.add(assignment.group("field"))
        terms.add(f"{assignment.group('field')}={assignment.group('value')}")
    return terms


def line_has_explanation(line: str) -> bool:
    without_code = CODE_SPAN_RE.sub("", line)
    without_assignments = SEMANTIC_ASSIGNMENT_RE.sub("", without_code)
    return bool(EXPLANATION_HINT_RE.search(without_assignments))


def table_row_has_explanation(line: str) -> bool:
    if "|" not in line:
        return False
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    if len(cells) < 2:
        return False
    explanatory_cells = [CODE_SPAN_RE.sub("", cell).strip() for cell in cells[1:]]
    return any(line_has_explanation(cell) or len(cell.split()) >= 6 for cell in explanatory_cells)


def list_item_has_explanation(line: str) -> bool:
    match = LIST_ITEM_RE.match(line)
    if not match:
        return False
    body = match.group("body")
    return (" - " in body or "： " in body or ": " in body) and line_has_explanation(body)


def collect_explained_semantic_terms(lines: list[str]) -> set[str]:
    explained: set[str] = set()
    for line in lines:
        terms = semantic_terms_in_line(line)
        if not terms:
            continue
        if table_row_has_explanation(line) or list_item_has_explanation(line):
            explained.update(terms)
    return explained


def semantic_line_is_clear(line: str, terms: set[str], explained_terms: set[str]) -> bool:
    if not terms:
        return True
    if terms.issubset(explained_terms):
        return True
    if table_row_has_explanation(line) or list_item_has_explanation(line):
        return True
    return line_has_explanation(line)


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


def find_semantic_findings(
    root: Path,
    semantic_targets: Iterable[str],
    *,
    full_scan: bool,
) -> tuple[list[Finding], int, str]:
    findings: list[Finding] = []
    files = iter_semantic_target_files(root, semantic_targets)
    changed_lines = None if full_scan else collect_forward_changed_lines(root, semantic_targets)
    scan_mode = "full" if full_scan or changed_lines is None else "forward"
    for path in files:
        relative_path = path.relative_to(root).as_posix()
        lines = read_text(path).splitlines()
        if scan_mode == "forward":
            line_numbers = changed_lines.get(relative_path, set()) if changed_lines is not None else set()
            if not line_numbers:
                continue
        else:
            line_numbers = set(range(1, len(lines) + 1))
        explained_terms = collect_explained_semantic_terms(lines)
        for index, line in enumerate(lines, start=1):
            if index not in line_numbers:
                continue
            terms = semantic_terms_in_line(line)
            if not terms:
                continue
            if semantic_line_is_clear(line, terms, explained_terms):
                continue
            findings.append(
                Finding(
                    relative_path=relative_path,
                    line=index,
                    text=normalize_text(line),
                    reason="semantic_term_without_explanation",
                    suggestion=(
                        "Add an inline explanation or a nearby glossary/table entry that defines the field, value, "
                        "transition, gate, or control decision."
                    ),
                )
            )
    return findings, len(files), scan_mode


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
    parser.add_argument(
        "--full-scan",
        action="store_true",
        help="Check semantic annotation rules across all target Markdown instead of only changed lines.",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Repository root does not exist: {root}")
    targets = tuple(args.targets or DEFAULT_TARGETS)
    baseline_path = Path(args.baseline).resolve() if args.baseline else default_baseline_path(root)

    findings, checked_files = find_findings(root, targets)
    semantic_findings, semantic_checked_files, semantic_scan_mode = find_semantic_findings(
        root,
        DEFAULT_SEMANTIC_TARGETS if args.targets is None else targets,
        full_scan=args.full_scan,
    )
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
    all_violations = [*violations, *semantic_findings]
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": "name_clarity_rules",
        "ok": len(all_violations) == 0,
        "errors": [
            f"{finding.relative_path}:{finding.line}: {finding.reason}: {finding.text}"
            for finding in all_violations
        ],
        "warnings": [],
        "info": [
            "Targets scanned: " + ", ".join(targets),
            "Semantic targets scanned: "
            + ", ".join(DEFAULT_SEMANTIC_TARGETS if args.targets is None else targets),
            "Semantic scan mode: " + semantic_scan_mode,
            "Compatibility baseline: " + ("disabled" if args.no_baseline else str(baseline_path)),
        ],
        "root": str(root),
        "targets": list(targets),
        "baseline_path": None if args.no_baseline else str(baseline_path),
        "counts": {
            "checked_files": checked_files,
            "semantic_checked_files": semantic_checked_files,
            "findings_total": len(findings),
            "semantic_findings_total": len(semantic_findings),
            "baseline_allowed": len(allowed),
            "violations": len(all_violations),
            "bare_code_violations": len(violations),
            "semantic_violations": len(semantic_findings),
        },
        "violations": [asdict(finding) for finding in all_violations],
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    if all_violations:
        print("Name clarity rules check failed:")
        for finding in all_violations:
            print(f"  - {finding.relative_path}:{finding.line}: {finding.text}")
            print(f"    {finding.suggestion}")
        print(f"Checked files: {checked_files}")
        print(f"Semantic checked files: {semantic_checked_files}")
        print(f"Semantic scan mode: {semantic_scan_mode}")
        print("Compatibility baseline: " + ("disabled" if args.no_baseline else str(baseline_path)))
        print(f"Baseline allowed findings: {len(allowed)}")
        return 1

    print("Name clarity rules check passed.")
    print(f"Checked files: {checked_files}")
    print(f"Semantic checked files: {semantic_checked_files}")
    print(f"Semantic scan mode: {semantic_scan_mode}")
    print("Compatibility baseline: " + ("disabled" if args.no_baseline else str(baseline_path)))
    print(f"Baseline allowed findings: {len(allowed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
