#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


MOJIBAKE_MARKERS = ("????", "\ufffd")
IMPLEMENTATION_PHASES = {"build", "verify", "archive"}
PLAN_SIZE_WARNING_BYTES = 40 * 1024
PLAN_SIZE_FAIL_BYTES = 60 * 1024
PLAN_SIZE_BASELINE = Path("tools/implementation_plan_size_baseline.json")
PLAN_FILES_ROOT = Path("docs_bilingual/implementation_plans")
REQUIRED_ANCHOR_PAIRS = (
    ("CURRENT_STATUS_START", "CURRENT_STATUS_END"),
    ("TASK_BACKLOG_START", "TASK_BACKLOG_END"),
    ("EVIDENCE_INDEX_START", "EVIDENCE_INDEX_END"),
)
EVIDENCE_HEADING_RE = re.compile(r"^##\s+20\d\d-\d\d-\d\d\b.*(?:Evidence|证据)", re.MULTILINE)
BACKTICK_PATH_RE = re.compile(r"`([^`]+)`")
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
EVIDENCE_PATH_PREFIXES = ("docs/", "docs_bilingual/", "openspec/")


def read_text_utf8(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def parse_docs_registry(path: Path) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw_line in read_text_utf8(path).splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            if current:
                entries.append(current)
            current = {}
            stripped = stripped[2:]
            if ":" in stripped:
                key, value = stripped.split(":", 1)
                current[key.strip()] = value.strip()
            continue
        if current is None or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        current[key.strip()] = value.strip()

    if current:
        entries.append(current)

    return entries


def validate_text_health(path: Path, root: Path, errors: list[str]) -> None:
    text = read_text_utf8(path)
    for line_number, line in enumerate(text.splitlines(), start=1):
        if any(marker in line for marker in MOJIBAKE_MARKERS):
            errors.append(
                f"{path.relative_to(root).as_posix()}:{line_number}: contains mojibake or replacement-character marker."
            )


def parse_simple_yaml(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw_line in read_text_utf8(path).splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        data[key.strip()] = value.strip().strip("'\"")
    return data


def parse_front_matter(path: Path) -> dict[str, str]:
    text = read_text_utf8(path)
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    data: dict[str, str] = {}
    for raw_line in lines[1:]:
        stripped = raw_line.strip()
        if stripped == "---":
            return data
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        data[key.strip()] = value.strip().strip("'\"")
    return data


def active_plan_guidance() -> str:
    return (
        "\u4e2d\u6587\u63d0\u793a\uff1a\u5f00\u59cb\u5b9e\u65bd\u524d\uff0c"
        "\u8bf7\u5148\u5728 docs_bilingual/docs_registry.yaml \u767b\u8bb0 active "
        "\u53cc\u8bed implementation plan\uff0c\u5e76\u4fdd\u6301\u82f1\u6587\u4e3b\u6587\u4ef6"
        "\u548c zh-CN companion \u72b6\u6001\u4e00\u81f4\u3002"
    )


def load_plan_size_baseline(root: Path) -> dict[str, set[str]]:
    path = root / PLAN_SIZE_BASELINE
    if not path.exists():
        return {}
    payload = json.loads(read_text_utf8(path))
    entries = payload.get("entries", {})
    baseline: dict[str, set[str]] = {}
    if isinstance(entries, dict):
        for relative_path, value in entries.items():
            checks = value.get("allowed_findings", value) if isinstance(value, dict) else value
            if isinstance(checks, list):
                baseline[relative_path.replace("\\", "/")] = {str(item) for item in checks}
    return baseline


def anchor_counts(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for start, end in REQUIRED_ANCHOR_PAIRS:
        counts[start] = text.count(start)
        counts[end] = text.count(end)
    return counts


def missing_required_anchors(text: str) -> list[str]:
    missing: list[str] = []
    counts = anchor_counts(text)
    for start, end in REQUIRED_ANCHOR_PAIRS:
        if counts[start] != 1:
            missing.append(start)
        if counts[end] != 1:
            missing.append(end)
    return missing


def evidence_index_section(text: str) -> str | None:
    start = text.find("EVIDENCE_INDEX_START")
    end = text.find("EVIDENCE_INDEX_END")
    if start == -1 or end == -1 or end <= start:
        return None
    return text[start:end]


def referenced_evidence_paths(section: str) -> list[str]:
    paths: set[str] = set()
    for value in [*BACKTICK_PATH_RE.findall(section), *MARKDOWN_LINK_RE.findall(section)]:
        candidate = value.strip().replace("\\", "/")
        if candidate.startswith(EVIDENCE_PATH_PREFIXES):
            paths.add(candidate)
    return sorted(paths)


def add_or_allow_plan_finding(
    *,
    relative_path: str,
    finding_code: str,
    message: str,
    baseline: dict[str, set[str]],
    errors: list[str],
    warnings: list[str],
) -> None:
    allowed = finding_code in baseline.get(relative_path, set())
    if allowed:
        warnings.append(f"{relative_path}: legacy-baseline allows `{finding_code}`; {message}")
    else:
        errors.append(f"{relative_path}: {message}")


def validate_plan_structure(
    path: Path,
    root: Path,
    baseline: dict[str, set[str]],
    errors: list[str],
    warnings: list[str],
    plan_files: list[dict[str, object]],
) -> None:
    relative_path = path.relative_to(root).as_posix()
    text = read_text_utf8(path)
    size_bytes = path.stat().st_size
    missing_anchors = missing_required_anchors(text)
    evidence_heading_count = len(EVIDENCE_HEADING_RE.findall(text))
    section = evidence_index_section(text)
    evidence_paths = referenced_evidence_paths(section) if section is not None else []

    if size_bytes > PLAN_SIZE_WARNING_BYTES:
        warnings.append(
            f"{relative_path}: size {size_bytes} bytes exceeds warning threshold {PLAN_SIZE_WARNING_BYTES} bytes."
        )
    if size_bytes > PLAN_SIZE_FAIL_BYTES:
        add_or_allow_plan_finding(
            relative_path=relative_path,
            finding_code="oversized_fail_threshold",
            message=f"size {size_bytes} bytes exceeds fail threshold {PLAN_SIZE_FAIL_BYTES} bytes.",
            baseline=baseline,
            errors=errors,
            warnings=warnings,
        )
    if missing_anchors:
        add_or_allow_plan_finding(
            relative_path=relative_path,
            finding_code="missing_required_anchors",
            message="missing required stable update anchors: " + ", ".join(missing_anchors),
            baseline=baseline,
            errors=errors,
            warnings=warnings,
        )
    if evidence_heading_count > 3 and section is None:
        add_or_allow_plan_finding(
            relative_path=relative_path,
            finding_code="evidence_ledger_without_index",
            message=(
                f"contains {evidence_heading_count} dated evidence-package headings but no "
                "EVIDENCE_INDEX_START/EVIDENCE_INDEX_END section."
            ),
            baseline=baseline,
            errors=errors,
            warnings=warnings,
        )
    for evidence_path in evidence_paths:
        if not (root / evidence_path).exists():
            errors.append(f"{relative_path}: evidence index references missing path: {evidence_path}")

    plan_files.append(
        {
            "path": relative_path,
            "size_bytes": size_bytes,
            "missing_required_anchors": missing_anchors,
            "evidence_heading_count": evidence_heading_count,
            "evidence_index_paths": evidence_paths,
            "baseline_allowed_findings": sorted(baseline.get(relative_path, set())),
        }
    )


def validate_on_disk_plan_registry_state(
    root: Path,
    impl_by_path: dict[str, dict[str, str]],
    errors: list[str],
    warnings: list[str],
) -> int:
    plan_root = root / PLAN_FILES_ROOT
    if not plan_root.exists():
        return 0

    disk_plan_count = 0
    for path in sorted(plan_root.glob("*.md")):
        front_matter = parse_front_matter(path)
        if front_matter.get("doc_class") != "implementation_plan":
            continue

        disk_plan_count += 1
        relative_path = path.relative_to(root).as_posix()
        status = front_matter.get("status", "").strip().lower()
        doc_id = front_matter.get("doc_id", "").strip()
        registry_entry = impl_by_path.get(relative_path)

        if registry_entry is None:
            message = (
                f"Implementation plan file `{relative_path}` is missing a docs_registry.yaml record."
                f" {active_plan_guidance()}"
            )
            if status == "active":
                errors.append("Active " + message)
            else:
                warnings.append("Draft/non-active " + message)
            continue

        registry_status = registry_entry.get("status", "").strip().lower()
        registry_doc_id = registry_entry.get("doc_id", "<unknown>")
        if doc_id and registry_doc_id != doc_id:
            errors.append(
                f"Implementation plan file `{relative_path}` has doc_id `{doc_id}` but docs_registry.yaml records `{registry_doc_id}`. {active_plan_guidance()}"
            )
        if status == "active" and registry_status != "active":
            errors.append(
                f"Active implementation plan file `{relative_path}` is registered with status `{registry_status}`; expected `active`. {active_plan_guidance()}"
            )
        elif registry_status == "active" and status != "active":
            errors.append(
                f"Implementation plan registry entry `{registry_doc_id}` is active, but `{relative_path}` front matter status is `{status or '<missing>'}`; expected `active`. {active_plan_guidance()}"
            )

        if status == "active" and relative_path.endswith(".zh-CN.md"):
            translation_of = front_matter.get("translation_of", "").replace("\\", "/")
            if translation_of and translation_of not in impl_by_path:
                errors.append(
                    f"Active implementation plan companion `{relative_path}` points to unregistered translation_of `{translation_of}`. {active_plan_guidance()}"
                )

    return disk_plan_count


def active_comet_plan_references(root: Path) -> list[dict[str, str]]:
    references: list[dict[str, str]] = []
    changes_root = root / "openspec" / "changes"
    if not changes_root.exists():
        return references
    for state_path in sorted(changes_root.glob("*/.comet.yaml")):
        if "archive" in state_path.parts:
            continue
        state = parse_simple_yaml(state_path)
        phase = state.get("phase", "").strip().lower()
        plan = state.get("plan", "").strip()
        if phase not in IMPLEMENTATION_PHASES or not plan:
            continue
        normalized_plan = plan.replace("\\", "/")
        if "/implementation_plans/" not in normalized_plan:
            continue
        references.append(
            {
                "change": state_path.parent.name,
                "phase": phase,
                "plan": normalized_plan,
                "state": state_path.relative_to(root).as_posix(),
            }
        )
    return references


def main() -> int:
    parser = argparse.ArgumentParser(description="Check implementation-plan registry and bilingual integrity rules.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        raise SystemExit(f"Repository root does not exist: {root}")

    registry_path = root / "docs_bilingual" / "docs_registry.yaml"
    if not registry_path.exists():
        raise SystemExit("docs_bilingual/docs_registry.yaml is missing.")

    errors: list[str] = []
    warnings: list[str] = []
    infos: list[str] = []
    plan_files: list[dict[str, object]] = []
    size_baseline = load_plan_size_baseline(root)

    entries = parse_docs_registry(registry_path)
    impl_entries = [entry for entry in entries if entry.get("doc_class") == "implementation_plan"]
    infos.append(f"Implementation plan registry entries: {len(impl_entries)}")
    impl_by_path: dict[str, dict[str, str]] = {}
    for entry in impl_entries:
        for key in ("canonical_path", "zh_cn_path"):
            value = entry.get(key, "")
            if value:
                impl_by_path[value.replace("\\", "/")] = entry

    disk_plan_files = validate_on_disk_plan_registry_state(root, impl_by_path, errors, warnings)
    infos.append(f"Implementation plan files with front matter: {disk_plan_files}")

    for entry in impl_entries:
        doc_id = entry.get("doc_id", "<unknown>")
        status = entry.get("status", "").strip().lower()
        canonical_path = entry.get("canonical_path", "")
        zh_cn_path = entry.get("zh_cn_path", "")

        if not canonical_path:
            errors.append(f"Implementation plan `{doc_id}` is missing canonical_path in docs_registry.yaml.")
            continue
        if not zh_cn_path:
            errors.append(f"Implementation plan `{doc_id}` is missing zh_cn_path in docs_registry.yaml.")
            continue

        canonical_file = root / canonical_path
        zh_file = root / zh_cn_path

        if not canonical_file.exists():
            errors.append(f"Implementation plan `{doc_id}` canonical_path does not exist: {canonical_path}")
        else:
            validate_text_health(canonical_file, root, errors)
            validate_plan_structure(canonical_file, root, size_baseline, errors, warnings, plan_files)
        if not zh_file.exists():
            errors.append(f"Implementation plan `{doc_id}` zh_cn_path does not exist: {zh_cn_path}")
        elif zh_file != canonical_file:
            validate_text_health(zh_file, root, errors)
            validate_plan_structure(zh_file, root, size_baseline, errors, warnings, plan_files)

        canonical_is_chinese = canonical_path.endswith(".zh-CN.md")
        zh_is_chinese = zh_cn_path.endswith(".zh-CN.md")
        if not zh_is_chinese:
            errors.append(f"Implementation plan `{doc_id}` zh_cn_path is not a .zh-CN.md file: {zh_cn_path}")

        if status == "active":
            if canonical_is_chinese:
                errors.append(
                    f"Active implementation plan `{doc_id}` uses a Chinese file as canonical_path: {canonical_path}"
                )
            expected_zh = canonical_file.with_name(canonical_file.stem + ".zh-CN.md").relative_to(root).as_posix()
            if zh_cn_path != expected_zh:
                errors.append(
                    f"Active implementation plan `{doc_id}` has mismatched zh_cn_path. Expected `{expected_zh}`, got `{zh_cn_path}`."
                )
        else:
            if canonical_is_chinese:
                warnings.append(
                    f"Draft implementation plan `{doc_id}` still uses a Chinese file as canonical_path: {canonical_path}"
                )
            if canonical_path == zh_cn_path:
                warnings.append(
                    f"Draft implementation plan `{doc_id}` uses the same file for canonical_path and zh_cn_path."
                )

    active_plan_refs = active_comet_plan_references(root)
    infos.append(f"Active Comet implementation plan references: {len(active_plan_refs)}")
    for reference in active_plan_refs:
        plan_path = reference["plan"]
        entry = impl_by_path.get(plan_path)
        if entry is None:
            errors.append(
                f"Comet change `{reference['change']}` phase `{reference['phase']}` references unregistered implementation plan: {plan_path}"
            )
            continue
        status = entry.get("status", "").strip().lower()
        if status != "active":
            errors.append(
                f"Comet change `{reference['change']}` phase `{reference['phase']}` references implementation plan `{entry.get('doc_id', '<unknown>')}` with status `{status}`; implementation plan status must be active before implementation."
            )

    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": "implementation_plan_rules",
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "info": infos,
        "root": str(root),
        "counts": {
            "implementation_plan_entries": len(impl_entries),
            "implementation_plan_files": len(plan_files),
            "disk_implementation_plan_files": disk_plan_files,
            "active_comet_plan_references": len(active_plan_refs),
            "errors": len(errors),
            "warnings": len(warnings),
        },
        "implementation_plan_entries": len(impl_entries),
        "thresholds": {
            "plan_size_warning_bytes": PLAN_SIZE_WARNING_BYTES,
            "plan_size_fail_bytes": PLAN_SIZE_FAIL_BYTES,
        },
        "plan_size_baseline_path": str(root / PLAN_SIZE_BASELINE),
        "implementation_plan_files": plan_files,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1

    if errors:
        print("Implementation plan rules check failed:")
        for error in errors:
            print(f"  - {error}")
        if warnings:
            print("Warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        return 1

    print("Implementation plan rules check passed.")
    for info in infos:
        print(f"  - {info}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
