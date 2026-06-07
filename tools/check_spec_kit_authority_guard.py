#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


CHECK_NAME = "spec_kit_authority_guard"
DEFAULT_SCAN_ROOTS = (".",)
SPEC_KIT_SOURCE_URL = "https://github.com/github/spec-kit"
SPEC_KIT_SOURCE_PIN = "7106858c4e636098815fffa23f6c6b99eb0e156b"
ALLOWED_RUNTIME_MODES = {
    "source-refresh",
    "probe",
    "plan-dry-run",
    "init-dry-run",
    "self-check-dry-run",
}
ALLOWED_RECEIPT_DECISIONS = {"blocked", "subordinate"}
REQUIRED_SURFACE_STATUS_KEYS = (
    "specify_init",
    "specify_init_force",
    "specify_self_check",
    ".specify/",
    "specs/",
    "/speckit.*",
    "$speckit-*",
    "extensions",
    "presets",
    "workflow_outputs",
)
ALLOWED_MIGRATION_PLAN_DOC_IDS = {
    "spec_kit_authority_migration_plan",
    "spec_kit_governance_migration_plan",
}
SAFE_REFERENCE_HINT_RE = re.compile(
    r"\b(optional|subordinate|adapter|template|reference|docs?|safe references?|forbid|forbids|forbidden|"
    r"block|blocks|blocked|guard|guardrail|do not run|do not add|do not install|"
    r"no authority|not (?:a )?governance authority|without a separate active plan|dry[- ]run|receipt)\b|"
    r"(\u4e0d\u8fd0\u884c|\u4e0d\u6dfb\u52a0|\u4e0d\u5b89\u88c5|\u7981\u6b62|\u963b\u6b62|\u4ece\u5c5e|\u53c2\u8003|\u6a21\u677f|\u4e0d\u662f|\u6ca1\u6709\u5355\u72ec)",
    re.IGNORECASE,
)
AUTHORITY_TAKEOVER_RE = re.compile(
    r"\b(Spec Kit|spec-kit|specify|\.specify)\b.*\b("
    r"governance authority|authority layer|primary authority|source of truth|replace OpenSpec|replace Comet|take over|migration authority"
    r")\b|\b("
    r"governance authority|authority layer|primary authority|source of truth|take over"
    r")\b.*\b(Spec Kit|spec-kit|specify|\.specify)\b",
    re.IGNORECASE,
)
SPECIFY_INIT_RE = re.compile(r"\bspecify(?:\.exe|\.cmd)?\s+init\b", re.IGNORECASE)
SPECIFY_FORCE_RE = re.compile(r"\bspecify(?:\.exe|\.cmd)?\s+init\b[^\n]*\s--force\b", re.IGNORECASE)
SPECKIT_SLASH_COMMAND_RE = re.compile(r"(?<![\w.-])/speckit\.[A-Za-z0-9_.-]+", re.IGNORECASE)
SPECKIT_SKILL_COMMAND_RE = re.compile(r"(?<![\w.-])\$speckit-[A-Za-z0-9_.-]+", re.IGNORECASE)

EXCLUDED_DIR_NAMES = {
    ".git",
    ".worktrees",
    ".hg",
    ".svn",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "env",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".omx",
}
EXCLUDED_PATH_PARTS = {
    "archive",
    "test-artifacts",
}
EXCLUDED_FILE_NAMES = {
    "local-gate-report.json",
    "openspec-guard-report.json",
}
SCANNED_SUFFIXES = {
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".ps1",
    ".sh",
    ".cmd",
    ".bat",
    ".py",
    ".mjs",
    ".js",
    ".ts",
    ".tsx",
}


@dataclass(frozen=True)
class Finding:
    kind: str
    relative_path: str
    line: int
    text: str
    reason: str


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def normalize(path: str) -> str:
    return path.strip().replace("\\", "/")


def relative_to_root(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return str(path)


def relative_parts(relative: str) -> tuple[str, ...]:
    return tuple(part for part in normalize(relative).split("/") if part)


def path_is_excluded(relative: str) -> bool:
    parts = relative_parts(relative)
    if not parts:
        return False
    if any(part in EXCLUDED_DIR_NAMES for part in parts):
        return True
    if set(parts) & EXCLUDED_PATH_PARTS:
        return True
    if parts[-1] in EXCLUDED_FILE_NAMES:
        return True
    return False


def iter_scan_files(root: Path, scan_roots: Iterable[str]) -> list[Path]:
    files: set[Path] = set()
    root_resolved = root.resolve()
    for raw_target in scan_roots:
        target = (root / raw_target).resolve()
        if not target.exists():
            continue
        if target.is_file():
            if target.suffix.lower() in SCANNED_SUFFIXES:
                files.add(target)
            continue
        for path in target.rglob("*"):
            if not path.is_file():
                continue
            relative = relative_to_root(root_resolved, path)
            if path_is_excluded(relative):
                continue
            if path.suffix.lower() not in SCANNED_SUFFIXES:
                continue
            files.add(path)
    return sorted(files)


def iter_existing_paths(root: Path, scan_roots: Iterable[str]) -> list[str]:
    paths: set[str] = set()
    for raw_target in scan_roots:
        target = (root / raw_target).resolve()
        if not target.exists():
            continue
        if target.is_file() or target.is_dir():
            relative = relative_to_root(root, target)
            if relative != "." and not path_is_excluded(relative):
                paths.add(normalize(relative))
        if target.is_dir():
            for path in target.rglob("*"):
                relative = relative_to_root(root, path)
                if path_is_excluded(relative):
                    continue
                paths.add(normalize(relative))
    return sorted(paths)


def parse_status_paths(output: str) -> list[str]:
    paths: list[str] = []
    for raw in output.splitlines():
        if not raw.strip() or raw.startswith("##"):
            continue
        path_text = raw[3:] if len(raw) > 3 else ""
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        paths.append(normalize(path_text))
    return paths


def current_changed_paths(root: Path) -> set[str]:
    changed: set[str] = set()
    for args in (["diff", "--name-only"], ["diff", "--cached", "--name-only"]):
        result = run_git(root, args)
        if result.returncode == 0:
            changed.update(normalize(line) for line in result.stdout.splitlines() if line.strip())
    status = run_git(root, ["status", "--porcelain", "--untracked-files=all"])
    if status.returncode == 0:
        changed.update(parse_status_paths(status.stdout))
    return changed


def active_migration_plan_doc_ids(root: Path) -> set[str]:
    docs: set[str] = set()
    plans_root = root / "docs_bilingual" / "implementation_plans"
    if not plans_root.exists():
        return docs
    for path in plans_root.glob("*.md"):
        if path.name.endswith(".zh-CN.md"):
            continue
        try:
            text = read_text(path)
        except OSError:
            continue
        header = text.split("---", 2)
        front_matter = header[1] if len(header) >= 3 and text.startswith("---") else text[:2000]
        doc_id = ""
        status = ""
        migration_authorized = False
        for raw_line in front_matter.splitlines():
            if raw_line.startswith("doc_id:"):
                doc_id = raw_line.split(":", 1)[1].strip()
            elif raw_line.startswith("status:"):
                status = raw_line.split(":", 1)[1].strip()
            elif raw_line.startswith("spec_kit_authority_migration:"):
                migration_authorized = raw_line.split(":", 1)[1].strip().lower() == "true"
        if status == "active" and doc_id and (doc_id in ALLOWED_MIGRATION_PLAN_DOC_IDS or migration_authorized):
            docs.add(doc_id)
    return docs


def has_authorized_migration_plan(root: Path) -> bool:
    return bool(active_migration_plan_doc_ids(root))


def path_is_specify_governance(relative: str) -> bool:
    relative = normalize(relative)
    if relative == ".specify" or relative.startswith(".specify/"):
        return True
    return False


def generated_surface_kind(relative: str) -> str | None:
    relative = normalize(relative)
    parts = relative_parts(relative)
    if not parts:
        return None
    lower_relative = relative.lower()
    lower_name = parts[-1].lower()
    if parts[0] == "specs":
        return "specs_directory_present_without_plan"
    if len(parts) >= 3 and parts[0] == ".codex" and parts[1] in {"commands", "skills"} and "speckit" in lower_relative:
        return "generated_speckit_surface_present_without_plan"
    if len(parts) >= 3 and parts[0] == ".github" and parts[1] == "prompts" and "speckit" in lower_relative:
        return "generated_speckit_surface_present_without_plan"
    if len(parts) == 1 and (lower_name.startswith("speckit.") or lower_name.startswith("speckit-")):
        return "generated_speckit_surface_present_without_plan"
    if parts[0] == "extensions" and "speckit" in lower_relative:
        return "generated_speckit_extension_present_without_plan"
    if parts[0] == "presets" and "speckit" in lower_relative:
        return "generated_speckit_preset_present_without_plan"
    if parts[0] == "workflow_outputs" and "speckit" in lower_relative:
        return "generated_speckit_workflow_output_present_without_plan"
    return None


def line_is_safe_reference(line: str, relative_path: str) -> bool:
    if SAFE_REFERENCE_HINT_RE.search(line):
        return True
    normalized = normalize(relative_path)
    if normalized.startswith("docs_bilingual/implementation_plans/spec_kit_"):
        return True
    if normalized.startswith("docs_bilingual/governance/spec_kit_subordinate_adapter_policy"):
        return True
    if normalized.startswith("test/") and ("spec_kit_authority" in normalized or "spec_kit_subordinate_runtime" in normalized):
        return True
    if normalized in {"tools/check_spec_kit_authority_guard.py", "tools/spec_kit_subordinate_runtime.py"}:
        return True
    return False


def find_file_findings(root: Path, scan_roots: Iterable[str], authorized_migration_plan_present: bool) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    checked_files = 0
    for path in iter_scan_files(root, scan_roots):
        relative = relative_to_root(root, path)
        checked_files += 1
        try:
            lines = read_text(path).splitlines()
        except OSError as exc:
            findings.append(
                Finding(
                    kind="unreadable_file",
                    relative_path=relative,
                    line=0,
                    text=str(exc),
                    reason="scanned file could not be read",
                )
            )
            continue
        for index, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            if SPECIFY_FORCE_RE.search(line):
                if line_is_safe_reference(line, relative):
                    continue
                findings.append(
                    Finding(
                        kind="unsafe_specify_init_force",
                        relative_path=relative,
                        line=index,
                        text=stripped,
                        reason="`specify init --force` is an authority-changing Spec Kit command and must remain blocked in committed surfaces.",
                    )
                )
                continue
            if SPECIFY_INIT_RE.search(line) and not line_is_safe_reference(line, relative):
                findings.append(
                    Finding(
                        kind="unsafe_specify_init",
                        relative_path=relative,
                        line=index,
                        text=stripped,
                        reason="`specify init` references must explain they are blocked or subordinate; do not normalize initialization commands.",
                    )
                )
                continue
            if SPECKIT_SLASH_COMMAND_RE.search(line) and not line_is_safe_reference(line, relative):
                findings.append(
                    Finding(
                        kind="unsafe_speckit_slash_command",
                        relative_path=relative,
                        line=index,
                        text=stripped,
                        reason="Generated `/speckit.*` command surfaces must remain blocked/subordinate unless a separate active plan owns them.",
                    )
                )
            if SPECKIT_SKILL_COMMAND_RE.search(line) and not line_is_safe_reference(line, relative):
                findings.append(
                    Finding(
                        kind="unsafe_speckit_skill_command",
                        relative_path=relative,
                        line=index,
                        text=stripped,
                        reason="Generated `$speckit-*` skills-mode surfaces must remain blocked/subordinate unless a separate active plan owns them.",
                    )
                )
                continue
            if AUTHORITY_TAKEOVER_RE.search(line) and not line_is_safe_reference(line, relative):
                findings.append(
                    Finding(
                        kind="unsafe_authority_takeover_language",
                        relative_path=relative,
                        line=index,
                        text=stripped,
                        reason="Spec Kit must not be described as taking governance authority without a separate active plan.",
                    )
                )
    return findings, checked_files


def find_path_findings(root: Path, scan_roots: Iterable[str], authorized_migration_plan_present: bool) -> list[Finding]:
    findings: list[Finding] = []
    changed = current_changed_paths(root)
    specify_dir = root / ".specify"
    if specify_dir.exists() and not authorized_migration_plan_present:
        findings.append(
            Finding(
                kind="specify_directory_present_without_plan",
                relative_path=".specify",
                line=0,
                text=".specify/",
                reason="`.specify/` is a Spec Kit governance/runtime directory and requires an active authority-guard plan before creation.",
            )
        )
    if not authorized_migration_plan_present:
        seen_surface: set[tuple[str, str]] = set()
        for rel in iter_existing_paths(root, scan_roots):
            kind = generated_surface_kind(rel)
            if kind is None:
                continue
            key = (kind, rel)
            if key in seen_surface:
                continue
            seen_surface.add(key)
            findings.append(
                Finding(
                    kind=kind,
                    relative_path=rel,
                    line=0,
                    text=rel,
                    reason="Generated Spec Kit `.specify/`, root `specs/`, `/speckit.*`, `$speckit-*`, extension, preset, or workflow-output surfaces require a separate active plan.",
                )
            )
    for rel in sorted(changed):
        if path_is_specify_governance(rel) and not authorized_migration_plan_present:
            findings.append(
                Finding(
                    kind="specify_path_changed_without_plan",
                    relative_path=rel,
                    line=0,
                    text=rel,
                    reason="`.specify` path changes require an active Spec Kit authority migration plan.",
                )
            )
            continue
        kind = generated_surface_kind(rel)
        if kind and not authorized_migration_plan_present:
            findings.append(
                Finding(
                    kind=f"changed_{kind}",
                    relative_path=rel,
                    line=0,
                    text=rel,
                    reason="Changed generated Spec Kit surfaces require an active Spec Kit authority migration plan.",
                )
            )
    return findings


def read_json(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except FileNotFoundError:
        return None, "receipt_missing"
    except json.JSONDecodeError:
        return None, "receipt_invalid_json"
    except OSError:
        return None, "receipt_unreadable"


def redaction_is_valid(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"pass", "passed", "redacted", "no_secrets", "no-sensitive-data"}
    if isinstance(value, dict):
        return str(value.get("status", "")).strip().lower() in {"pass", "passed", "redacted", "no_secrets", "no-sensitive-data"}
    return False


def validate_receipt_object(receipt: Any, label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(receipt, dict):
        return [f"{label}:receipt_not_object"]
    mode = str(receipt.get("mode", "")).strip()
    if mode not in ALLOWED_RUNTIME_MODES:
        errors.append(f"{label}:receipt_mode_not_allowed:{mode or '<missing>'}")
    if receipt.get("dry_run_only") is not True:
        errors.append(f"{label}:receipt_dry_run_only_must_be_true")
    if receipt.get("would_run_specify") is not False:
        errors.append(f"{label}:receipt_would_run_specify_must_be_false")
    if receipt.get("source_url") != SPEC_KIT_SOURCE_URL:
        errors.append(f"{label}:receipt_source_url_mismatch")
    if receipt.get("source_pin") != SPEC_KIT_SOURCE_PIN:
        errors.append(f"{label}:receipt_source_pin_mismatch")

    decision = receipt.get("authority_decision")
    if not isinstance(decision, dict):
        errors.append(f"{label}:receipt_authority_decision_required")
    else:
        value = str(decision.get("decision", "")).strip()
        if value not in ALLOWED_RECEIPT_DECISIONS:
            errors.append(f"{label}:receipt_authority_decision_invalid:{value or '<missing>'}")
        if not isinstance(decision.get("winning_authority"), str) or not decision.get("winning_authority", "").strip():
            errors.append(f"{label}:receipt_winning_authority_required")

    surface = receipt.get("surface_status")
    if not isinstance(surface, dict):
        errors.append(f"{label}:receipt_surface_status_required")
    else:
        for key in REQUIRED_SURFACE_STATUS_KEYS:
            if key not in surface:
                errors.append(f"receipt_missing_surface_status_key:{key}")
            elif not isinstance(surface.get(key), str) or not surface.get(key, "").strip():
                errors.append(f"{label}:receipt_surface_status_empty:{key}")

    if not redaction_is_valid(receipt.get("redaction") or receipt.get("redaction_status")):
        errors.append(f"{label}:receipt_redaction_evidence_required")
    timeout = receipt.get("timeout")
    if not isinstance(timeout, dict) or timeout.get("released") is not True:
        errors.append(f"{label}:receipt_timeout_release_required")
    if not isinstance(receipt.get("rollback_pointer"), str) or not receipt.get("rollback_pointer", "").strip():
        errors.append(f"{label}:receipt_rollback_pointer_required")
    if not isinstance(receipt.get("local_main_first_validation"), dict):
        errors.append(f"{label}:receipt_local_main_first_validation_required")
    return errors


def validate_receipts(paths: Iterable[str]) -> dict[str, Any]:
    errors: list[str] = []
    summaries: list[dict[str, Any]] = []
    count = 0
    for raw in paths:
        path = Path(raw)
        count += 1
        receipt, load_error = read_json(path)
        label = path.name or f"receipt_{count}"
        if load_error:
            errors.append(f"{label}:{load_error}")
            continue
        receipt_errors = validate_receipt_object(receipt, label)
        errors.extend(receipt_errors)
        if isinstance(receipt, dict):
            summaries.append(
                {
                    "path_name": label,
                    "mode": receipt.get("mode"),
                    "decision": (receipt.get("authority_decision") or {}).get("decision") if isinstance(receipt.get("authority_decision"), dict) else None,
                    "ok": not receipt_errors,
                }
            )
    return {
        "ok": not errors,
        "errors": sorted(set(errors)),
        "summaries": summaries,
        "counts": {
            "receipts": count,
            "errors": len(set(errors)),
        },
    }


def evaluate(root: Path, scan_roots: Iterable[str], receipt_paths: Iterable[str] = ()) -> dict[str, object]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    authorized_migration_plan_present = has_authorized_migration_plan(root)
    file_findings, checked_files = find_file_findings(root, scan_roots, authorized_migration_plan_present)
    path_findings = find_path_findings(root, scan_roots, authorized_migration_plan_present)
    findings = [*file_findings, *path_findings]
    errors.extend(f"[{finding.kind}] {finding.relative_path}:{finding.line}: {finding.reason} :: {finding.text}" for finding in findings)
    receipt_validation = validate_receipts(receipt_paths)
    errors.extend(receipt_validation["errors"])
    if authorized_migration_plan_present:
        info.append("Authorized Spec Kit authority-migration plan is present; Spec Kit paths are still inspected for unsafe command or takeover language.")
    else:
        info.append("No authorized Spec Kit authority-migration plan detected; .specify, root specs, generated Spec Kit command/skill/prompt, extension, preset, workflow-output, and authority-changing Spec Kit surfaces fail closed.")
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "scan_roots": list(scan_roots),
        "authorized_migration_plan_present": authorized_migration_plan_present,
        "allowed_migration_plan_doc_ids": sorted(ALLOWED_MIGRATION_PLAN_DOC_IDS),
        "required_surface_status_keys": list(REQUIRED_SURFACE_STATUS_KEYS),
        "receipt_validation": receipt_validation,
        "findings": [asdict(finding) for finding in findings],
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "checked_files": checked_files,
            "findings": len(findings),
            "file_findings": len(file_findings),
            "path_findings": len(path_findings),
            "receipt_errors": receipt_validation["counts"]["errors"],
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed guard for Spec Kit authority-changing surfaces.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument(
        "--scan-root",
        action="append",
        default=None,
        help="Repository-relative file or directory to scan. Defaults to the repository root with common cache/state directories excluded.",
    )
    parser.add_argument("--receipt", action="append", default=[], help="Spec Kit subordinate runtime dry-run receipt to validate.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON output.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    payload = evaluate(root, tuple(args.scan_root or DEFAULT_SCAN_ROOTS), tuple(args.receipt or ()))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0 if payload["ok"] else 1
    for message in payload["info"]:
        print(message)
    for message in payload["warnings"]:
        print(f"WARNING: {message}")
    for message in payload["errors"]:
        print(f"ERROR: {message}")
    if payload["ok"]:
        print("Spec Kit authority guard passed.")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
