#!/usr/bin/env python3
"""Validate R4 Browser/CLI adapter smoke receipts.

Positive ``smoke-tested`` receipts are delegated to the generic
``user_level_receipt_governance`` R4 smoke contract and then tightened for this
adapter lane.  Honest blocked/not-installed receipts are accepted as evidence,
but they never count as smoke-tested runtime evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from user_level_receipt_governance import (
    collect_redaction_findings,
    smoke_summary,
    stable_hash,
    validate_smoke_receipt,
)


CHECK_NAME = "browser_cli_adapter_smoke_receipts"
RUNNER = Path("tools/run_browser_cli_adapter_smoke.py")
CHECKER = Path("tools/check_browser_cli_adapter_smoke_receipts.py")
PLAN_EN = Path("docs_bilingual/implementation_plans/user_level_browser_cli_adapter_boundary_plan.md")
PLAN_ZH = Path("docs_bilingual/implementation_plans/user_level_browser_cli_adapter_boundary_plan.zh-CN.md")
BOUNDARY_CHECKER = Path("tools/check_user_level_browser_cli_adapter_boundary.py")
CI_MANIFEST = Path("tools/ci/ci_test_manifest.json")
SAFETY_REGISTRY = Path("tools/safety_rule_script_backing_registry.json")
TEST_NAME = "browser_cli_adapter_smoke_receipts.test.py"
CANONICAL_ADAPTERS = ("chrome-devtools-mcp", "cdp-bridge-mcp", "OpenCLI")
ALIASES = {
    "chrome-devtools-mcp": "chrome-devtools-mcp",
    "chrome devtools mcp": "chrome-devtools-mcp",
    "cdp-bridge-mcp": "cdp-bridge-mcp",
    "cdp bridge": "cdp-bridge-mcp",
    "opencli": "OpenCLI",
    "open-cli": "OpenCLI",
}
FORBIDDEN_ADAPTER_TERMS = ("CLI-Anything", "WXWork_CLI", "WXWork.exe", "wecom-cli")
FORBIDDEN_COMMAND_PATTERNS = (
    re.compile(r"(?i)\b(mouse\.click|keyboard\.type|page\.navigate|js\.evaluate)\b"),
    re.compile(r"(?i)\b(click|type|navigate|javascript|cookie|cookies)\b"),
    re.compile(r"(?i)\b(raw[-_\s]?browser[-_\s]?data|browser[-_\s]?history)\b"),
    re.compile(r"(?i)\b(send|post|delete|write)\b"),
)
RAW_PRIVATE_PATH_PATTERNS = (
    re.compile(r"(?i)\b[A-Z]:\\(?:Users|PythonProject|project|tmp|temp)\\[^\s\"']+"),
    re.compile(r"\\\\[^\s\"']+"),
    re.compile(r"/(?:home|Users|tmp|var/tmp)/[^\s\"']+"),
)
SECRET_RE = re.compile(
    r"(?i)(sk-[A-Za-z0-9_-]{8,}|xox[baprs]-[A-Za-z0-9_-]+|"
    r"(?:token|secret|password|cookie|api[_-]?key)\s*[=:]\s*[^&\s]+)"
)
SAFETY_FLAGS = (
    "write_performed",
    "live_action_performed",
    "sensitive_action_performed",
    "user_level_state_mutated",
    "reads_browser_data",
    "external_message_sent",
)
REQUIRED_PLAN_MARKERS = (
    "tools/run_browser_cli_adapter_smoke.py",
    "tools/check_browser_cli_adapter_smoke_receipts.py",
    "browser_cli_adapter_smoke_receipts.test.py",
    "blocked receipts",
    "not smoke-tested",
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def hash_text(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError:
        errors.append(f"missing_or_unreadable:{path.as_posix()}")
        return ""


def read_json(path: Path, errors: list[str]) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except OSError:
        errors.append(f"missing_or_unreadable_json:{path.as_posix()}")
    except json.JSONDecodeError:
        errors.append(f"invalid_json:{path.as_posix()}")
    return None


def normalize_adapter(value: Any) -> str | None:
    text = str(value or "").strip()
    if text in CANONICAL_ADAPTERS:
        return text
    return ALIASES.get(text.lower())


def contains_forbidden_adapter_term(value: Any) -> list[str]:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True) if not isinstance(value, str) else value
    return [term for term in FORBIDDEN_ADAPTER_TERMS if term.lower() in text.lower()]


def contains_sensitive_command(value: Any) -> list[str]:
    text = "" if value is None else str(value)
    return [pattern.pattern for pattern in FORBIDDEN_COMMAND_PATTERNS if pattern.search(text)]


def contains_raw_path_or_secret(value: Any) -> list[str]:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    findings = [f"raw_private_path:{pattern.pattern}" for pattern in RAW_PRIVATE_PATH_PATTERNS if pattern.search(text)]
    if SECRET_RE.search(text):
        findings.append("raw_secret")
    return findings


def load_receipt(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None, [f"receipt_missing:{hash_text(str(path))}"]
    except json.JSONDecodeError:
        return None, [f"receipt_invalid_json:{path.name}"]
    except OSError:
        return None, [f"receipt_unreadable:{hash_text(str(path))}"]
    if not isinstance(data, dict):
        return None, [f"receipt_not_object:{path.name}"]
    return data, []


def receipt_paths(args: argparse.Namespace) -> list[Path]:
    paths: list[Path] = []
    if args.receipt_dir:
        directory = Path(args.receipt_dir)
        paths.extend(sorted(path for path in directory.glob("*.json") if path.is_file()))
    paths.extend(Path(value) for value in args.receipt)
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path.resolve())
        if key not in seen:
            unique.append(path)
            seen.add(key)
    return unique


def check_repo_surfaces(root: Path, errors: list[str]) -> dict[str, Any]:
    surface: dict[str, Any] = {
        "runner_exists": (root / RUNNER).exists(),
        "checker_exists": (root / CHECKER).exists(),
        "ci_manifest_has_test": False,
        "safety_registry_has_scripts": False,
        "boundary_checker_references_r4": False,
    }
    if not surface["runner_exists"]:
        errors.append(f"missing_runner:{RUNNER.as_posix()}")
    if not surface["checker_exists"]:
        errors.append(f"missing_checker:{CHECKER.as_posix()}")

    for rel in (PLAN_EN, PLAN_ZH):
        text = read_text(root / rel, errors)
        lowered = text.lower()
        for marker in REQUIRED_PLAN_MARKERS:
            if marker.lower() not in lowered:
                errors.append(f"{rel.as_posix()}:missing_marker:{marker}")

    manifest = read_json(root / CI_MANIFEST, errors)
    if isinstance(manifest, dict) and isinstance(manifest.get("python_unittest"), list):
        surface["ci_manifest_has_test"] = TEST_NAME in manifest["python_unittest"]
    if not surface["ci_manifest_has_test"]:
        errors.append(f"ci_manifest_missing:{TEST_NAME}")

    registry = read_json(root / SAFETY_REGISTRY, errors)
    if isinstance(registry, dict):
        for rule in registry.get("rules", []):
            if isinstance(rule, dict) and rule.get("id") == "user-level-browser-cli-adapter-boundary":
                scripts = set(rule.get("script_controls", [])) if isinstance(rule.get("script_controls"), list) else set()
                surface["safety_registry_has_scripts"] = RUNNER.as_posix() in scripts and CHECKER.as_posix() in scripts
    if not surface["safety_registry_has_scripts"]:
        errors.append("safety_registry_browser_cli_adapter_rule_missing_r4_scripts")

    boundary_text = read_text(root / BOUNDARY_CHECKER, errors)
    surface["boundary_checker_references_r4"] = (
        RUNNER.as_posix() in boundary_text
        and CHECKER.as_posix() in boundary_text
        and TEST_NAME in boundary_text
    )
    if not surface["boundary_checker_references_r4"]:
        errors.append("boundary_checker_missing_r4_smoke_surface_requirements")
    return surface


def receipt_is_blocked(receipt: dict[str, Any]) -> bool:
    result = receipt.get("smoke_result")
    result_status = str(result.get("status", "") if isinstance(result, dict) else result).strip().lower()
    r4_status = str(receipt.get("r4_status", "")).strip().lower()
    return receipt.get("smoke_tested") is not True and (
        result_status in {"blocked", "not-installed", "not_installed"} or r4_status in {"blocked", "not-installed", "not_installed"}
    )


def validate_blocked_receipt(receipt: dict[str, Any], adapter: str) -> list[str]:
    errors: list[str] = []
    if receipt.get("smoke_tested") is True:
        errors.append(f"{adapter}:blocked_receipt_must_not_be_smoke_tested")
    blockers = receipt.get("blockers")
    if not isinstance(blockers, list) or not blockers:
        errors.append(f"{adapter}:blocked_receipt_requires_blockers")
    if receipt.get("rollback_ready") is True:
        errors.append(f"{adapter}:blocked_receipt_must_not_claim_rollback_ready")
    for flag in SAFETY_FLAGS:
        if receipt.get(flag) is True:
            errors.append(f"{adapter}:blocked_receipt_forbidden_{flag}")
    return errors


def validate_positive_receipt(receipt: dict[str, Any], adapter: str, path: Path) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    errors.extend(validate_smoke_receipt(receipt, tool_name=adapter, owner_lane=str(receipt.get("owner_lane", ""))))
    owner_lane = str(receipt.get("owner_lane", ""))
    if not owner_lane.startswith("browser-cli-adapter:"):
        errors.append(f"{adapter}:owner_lane_must_be_browser_cli_adapter")
    if receipt.get("smoke_tested") is not True:
        errors.append(f"{adapter}:positive_receipt_must_set_smoke_tested_true")
    errors.extend(f"{adapter}:sensitive_command:{item}" for item in contains_sensitive_command(receipt.get("smoke_command")))
    for field in ("install_receipt", "rollback_pointer", "command_transcript"):
        findings = contains_raw_path_or_secret(receipt.get(field))
        errors.extend(f"{adapter}:{field}:{item}" for item in findings)
    errors.extend(f"{adapter}:redaction:{item}" for item in collect_redaction_findings(receipt))
    return errors, smoke_summary(receipt, receipt_path=path)


def validate_receipts(paths: list[Path], *, require_smoke_tested: bool) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    by_adapter: dict[str, list[dict[str, Any]]] = {adapter: [] for adapter in CANONICAL_ADAPTERS}
    summaries: list[dict[str, Any]] = []
    positive_count = 0
    blocked_count = 0

    for path in paths:
        receipt, load_errors = load_receipt(path)
        errors.extend(load_errors)
        if receipt is None:
            continue
        forbidden_terms = contains_forbidden_adapter_term(receipt)
        if forbidden_terms:
            errors.extend(f"forbidden_adapter_term:{term}:{path.name}" for term in forbidden_terms)
        adapter = normalize_adapter(receipt.get("tool_name"))
        if adapter is None:
            errors.append(f"unknown_or_noncanonical_adapter:{path.name}:{receipt.get('tool_name')}")
            continue
        by_adapter[adapter].append(receipt)
        raw_findings = contains_raw_path_or_secret(receipt)
        if raw_findings:
            errors.extend(f"{adapter}:receipt_contains_raw_private_path_or_secret:{item}" for item in raw_findings)
        if receipt_is_blocked(receipt):
            blocked_count += 1
            errors.extend(validate_blocked_receipt(receipt, adapter))
            if require_smoke_tested:
                errors.append(f"{adapter}:smoke_tested_required_but_receipt_blocked")
            summaries.append(
                {
                    "adapter": adapter,
                    "receipt_path_hash": stable_hash(str(path)),
                    "r4_status": "blocked",
                    "smoke_tested": False,
                    "blocker_count": len(receipt.get("blockers", [])) if isinstance(receipt.get("blockers"), list) else 0,
                }
            )
            continue
        positive_count += 1
        positive_errors, summary = validate_positive_receipt(receipt, adapter, path)
        errors.extend(positive_errors)
        summaries.append({"adapter": adapter, "r4_status": "smoke-tested", "smoke_tested": True, "summary": summary})

    for adapter, receipts in by_adapter.items():
        if not receipts:
            errors.append(f"missing_receipt:{adapter}")
        elif len(receipts) > 1:
            errors.append(f"duplicate_receipt:{adapter}:{len(receipts)}")

    if not paths:
        warnings.append("no_runtime_receipts_requested")

    return {
        "ok": not errors,
        "errors": sorted(set(errors)),
        "warnings": warnings,
        "summaries": summaries,
        "counts": {
            "receipt_files": len(paths),
            "positive_smoke_tested": positive_count,
            "blocked_or_not_installed": blocked_count,
            "errors": len(set(errors)),
            "warnings": len(warnings),
        },
    }


def evaluate(root: Path, args: argparse.Namespace) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    surface = check_repo_surfaces(root, errors)
    paths = receipt_paths(args)
    runtime = {
        "mode": "not_requested",
        "ok": True,
        "errors": [],
        "warnings": ["no_runtime_receipts_requested"],
        "summaries": [],
        "counts": {
            "receipt_files": 0,
            "positive_smoke_tested": 0,
            "blocked_or_not_installed": 0,
            "errors": 0,
            "warnings": 1,
        },
    }
    if paths:
        runtime = validate_receipts(paths, require_smoke_tested=bool(args.require_smoke_tested))
        runtime["mode"] = "receipt_validation"
        errors.extend(runtime["errors"])
    elif args.require_smoke_tested:
        errors.append("runtime_receipts_required_for_smoke_tested_gate")

    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root_hash": hash_text(str(root)),
        "canonical_adapters": list(CANONICAL_ADAPTERS),
        "repo_surfaces": surface,
        "runtime_receipts": runtime,
        "errors": sorted(set(errors)),
        "warnings": runtime.get("warnings", []),
        "mutates_user_level_state": False,
        "starts_browser": False,
        "performs_sensitive_browser_action": False,
        "reads_browser_data": False,
        "counts": {
            "errors": len(set(errors)),
            "warnings": len(runtime.get("warnings", [])),
            "receipt_files": runtime["counts"]["receipt_files"],
            "positive_smoke_tested": runtime["counts"]["positive_smoke_tested"],
            "blocked_or_not_installed": runtime["counts"]["blocked_or_not_installed"],
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate R4 Browser/CLI adapter smoke receipts.")
    parser.add_argument("--root", default=".", help="Repository root for checker-backed surfaces.")
    parser.add_argument("--receipt-dir", default=None, help="Directory containing R4 smoke receipts.")
    parser.add_argument("--receipt", action="append", default=[], help="Explicit R4 smoke receipt path.")
    parser.add_argument("--require-smoke-tested", action="store_true", help="Fail if any canonical adapter is blocked.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    payload = evaluate(Path(args.root), args)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
