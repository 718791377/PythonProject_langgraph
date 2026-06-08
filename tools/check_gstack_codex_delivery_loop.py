#!/usr/bin/env python3
"""Validate gstack-style Codex delivery-loop runtime governance surfaces."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from user_level_receipt_governance import (
    collect_redaction_findings,
    smoke_summary,
    stable_hash,
    validate_smoke_receipt,
)


CHECK_NAME = "gstack_codex_delivery_loop"
TOOL_NAME = "gstack"
OWNER_LANE = "gstack-codex-delivery-loop"
PRIORITY_ORDER = "Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit"
PLAN_EN = Path("docs_bilingual/implementation_plans/gstack_codex_delivery_loop_runtime_governance_plan.md")
PLAN_ZH = Path("docs_bilingual/implementation_plans/gstack_codex_delivery_loop_runtime_governance_plan.zh-CN.md")
PARENT_EN = Path("docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md")
PARENT_ZH = Path("docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.zh-CN.md")
RUNTIME = Path("tools/gstack_codex_delivery_loop_runtime.py")
CHECKER = Path("tools/check_gstack_codex_delivery_loop.py")
CI_MANIFEST = Path("tools/ci/ci_test_manifest.json")
SAFETY_REGISTRY = Path("tools/safety_rule_script_backing_registry.json")
GUARD_SCRIPT = Path("tools/run_openspec_guard.py")
REQUIRED_TESTS = {"gstack_codex_delivery_loop_runtime.test.py", "check_gstack_codex_delivery_loop.test.py"}
REQUIRED_ACTIONS = ("analyze", "plan-dry-run", "review-dry-run", "qa-dry-run", "ship-dry-run")
REQUIRED_PLAN_MARKERS = (
    "Status: implemented-local",
    "tools/check_gstack_codex_delivery_loop.py",
    "tools/gstack_codex_delivery_loop_runtime.py",
    "analyze --root . --json",
    "plan-dry-run",
    "review-dry-run",
    "qa-dry-run",
    "ship-dry-run",
    "smoke-tested",
    "blocked receipts",
    "authority_decision",
    PRIORITY_ORDER,
    "R4 smoke runtime",
)
FORBIDDEN_COMMAND_PATTERNS = (
    re.compile(r"(?i)\b(write|send|post|delete|mutate|patch|apply|commit|merge|push)\b"),
    re.compile(r"(?i)\b(start|sidecar|daemon|serve|attach|takeover|replace|telemetry|browser)\b"),
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
FORBIDDEN_FLAGS = (
    "write_performed",
    "live_action_performed",
    "sensitive_action_performed",
    "user_level_state_mutated",
    "remote_state_mutated",
    "browser_launch_performed",
    "telemetry_enabled",
    "codex_launcher_mutated",
    "local_main_gate_bypassed",
    "active_candidate",
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


def require_markers(label: str, text: str, markers: tuple[str, ...], errors: list[str]) -> None:
    lowered = text.lower()
    for marker in markers:
        if marker.lower() not in lowered:
            errors.append(f"{label}:missing_marker:{marker}")


def extract_anchor_block(text: str, anchor: str) -> str:
    start = f"<!-- {anchor}_START -->"
    end = f"<!-- {anchor}_END -->"
    if start not in text or end not in text:
        return ""
    return text.split(start, 1)[1].split(end, 1)[0]


def run_json_command(command: list[str], cwd: Path) -> tuple[int, dict[str, Any] | None, str]:
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        data = None
    return proc.returncode, data, proc.stderr


def check_repo_surfaces(root: Path, errors: list[str]) -> dict[str, Any]:
    surface = {
        "runtime_exists": (root / RUNTIME).exists(),
        "checker_exists": (root / CHECKER).exists(),
        "ci_manifest_has_tests": False,
        "safety_registry_has_rule": False,
        "openspec_guard_references_checker": False,
    }
    if not surface["runtime_exists"]:
        errors.append(f"missing_runtime:{RUNTIME.as_posix()}")
    if not surface["checker_exists"]:
        errors.append(f"missing_checker:{CHECKER.as_posix()}")

    for rel in (PLAN_EN, PLAN_ZH):
        text = read_text(root / rel, errors)
        require_markers(rel.as_posix(), text, REQUIRED_PLAN_MARKERS, errors)
        backlog = extract_anchor_block(text, "TASK_BACKLOG")
        if "- [ ]" in backlog:
            errors.append(f"{rel.as_posix()}:unchecked_task_backlog_items")
    for rel in (PARENT_EN, PARENT_ZH):
        text = read_text(root / rel, errors)
        require_markers(rel.as_posix(), text, ("gstack_codex_delivery_loop_runtime_governance_plan", "implemented-local", PRIORITY_ORDER), errors)

    manifest = read_json(root / CI_MANIFEST, errors)
    if isinstance(manifest, dict) and isinstance(manifest.get("python_unittest"), list):
        surface["ci_manifest_has_tests"] = REQUIRED_TESTS.issubset(set(map(str, manifest["python_unittest"])))
    if not surface["ci_manifest_has_tests"]:
        errors.append("ci_manifest_missing:gstack_codex_delivery_loop_tests")

    registry = read_json(root / SAFETY_REGISTRY, errors)
    if isinstance(registry, dict):
        for rule in registry.get("rules", []):
            if isinstance(rule, dict) and rule.get("id") == "gstack-codex-delivery-loop-runtime-governance":
                scripts = set(rule.get("script_controls", [])) if isinstance(rule.get("script_controls"), list) else set()
                steps = set(rule.get("guard_steps", [])) if isinstance(rule.get("guard_steps"), list) else set()
                surface["safety_registry_has_rule"] = (
                    RUNTIME.as_posix() in scripts
                    and CHECKER.as_posix() in scripts
                    and "check_gstack_codex_delivery_loop" in steps
                )
    if not surface["safety_registry_has_rule"]:
        errors.append("safety_registry_missing:gstack-codex-delivery-loop-runtime-governance")

    guard_text = read_text(root / GUARD_SCRIPT, errors)
    surface["openspec_guard_references_checker"] = "check_gstack_codex_delivery_loop" in guard_text
    if not surface["openspec_guard_references_checker"]:
        errors.append("openspec_guard_missing:check_gstack_codex_delivery_loop")
    return surface


def probe_runtime(root: Path, errors: list[str]) -> dict[str, Any]:
    action_results: dict[str, Any] = {}
    all_ok = True
    runtime = root / RUNTIME
    if not runtime.exists():
        return {"all_required_actions_ok": False, "actions": {}}
    for action in REQUIRED_ACTIONS:
        code, payload, stderr = run_json_command([sys.executable, str(runtime), action, "--root", str(root), "--json"], root)
        ok = code == 0 and isinstance(payload, dict) and payload.get("ok") is True
        ok = ok and isinstance(payload.get("authority_decision"), list) and bool(payload.get("authority_decision"))
        ok = ok and payload.get("authority_decision", [{}])[0].get("priority_order") == PRIORITY_ORDER
        ok = ok and payload.get("mutation", {}).get("file_write_performed") is False
        ok = ok and payload.get("safety", {}).get("browser_launch_performed") is False
        action_results[action] = {
            "ok": ok,
            "stage": payload.get("delivery_loop_stage") if isinstance(payload, dict) else None,
            "stderr_hash": hash_text(stderr),
        }
        if not ok:
            all_ok = False
            errors.append(f"runtime_probe_failed:{action}")
    return {"all_required_actions_ok": all_ok, "actions": action_results}


def receipt_paths(args: argparse.Namespace) -> list[Path]:
    paths: list[Path] = []
    if args.receipt_dir:
        paths.extend(sorted(path for path in Path(args.receipt_dir).glob("*.json") if path.is_file()))
    paths.extend(Path(value) for value in args.receipt)
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path.resolve())
        if key not in seen:
            unique.append(path)
            seen.add(key)
    return unique


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


def contains_sensitive_command(value: Any) -> list[str]:
    text = "" if value is None else str(value)
    return [pattern.pattern for pattern in FORBIDDEN_COMMAND_PATTERNS if pattern.search(text)]


def contains_raw_path_or_secret(value: Any) -> list[str]:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    findings = [f"raw_private_path:{pattern.pattern}" for pattern in RAW_PRIVATE_PATH_PATTERNS if pattern.search(text)]
    if SECRET_RE.search(text):
        findings.append("raw_secret")
    return findings


def receipt_is_blocked(receipt: dict[str, Any]) -> bool:
    result = receipt.get("smoke_result")
    result_status = str(result.get("status", "") if isinstance(result, dict) else result).strip().lower()
    r4_status = str(receipt.get("r4_status", "")).strip().lower()
    return receipt.get("smoke_tested") is not True and (
        result_status in {"blocked", "not-installed", "not_installed"}
        or r4_status in {"blocked", "not-installed", "not_installed"}
    )


def validate_authority(receipt: dict[str, Any], errors: list[str]) -> None:
    decision = receipt.get("authority_decision")
    if not isinstance(decision, list) or not decision:
        errors.append("gstack:authority_decision_required")
        return
    first = decision[0]
    if not isinstance(first, dict) or first.get("priority_order") != PRIORITY_ORDER:
        errors.append("gstack:authority_decision_priority_order_mismatch")


def validate_gstack_guards(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if receipt.get("owner_lane") != OWNER_LANE:
        errors.append("gstack:owner_lane_mismatch")
    read_guard = receipt.get("read_guard")
    if not isinstance(read_guard, dict) or read_guard.get("read_only") is not True or str(read_guard.get("status", "")).lower() != "pass":
        errors.append("gstack:read_guard_must_pass_read_only")
    write_guard = receipt.get("write_guard")
    if not isinstance(write_guard, dict) or write_guard.get("write_allowed") is not False or write_guard.get("write_performed") is not False:
        errors.append("gstack:write_guard_must_block_writes")
    remote_gate = receipt.get("remote_publication_gate")
    if not isinstance(remote_gate, dict) or remote_gate.get("remote_mutation_allowed") is not False:
        errors.append("gstack:remote_publication_gate_must_block_remote_mutation")
    for flag in FORBIDDEN_FLAGS:
        if receipt.get(flag) is True:
            errors.append(f"gstack:smoke_receipt_forbidden_{flag}")
    return errors


def validate_blocked_receipt(receipt: dict[str, Any]) -> list[str]:
    errors = validate_gstack_guards(receipt)
    validate_authority(receipt, errors)
    if receipt.get("smoke_tested") is True:
        errors.append("gstack:blocked_receipt_must_not_be_smoke_tested")
    blockers = receipt.get("blockers")
    if not isinstance(blockers, list) or not blockers:
        errors.append("gstack:blocked_receipt_requires_blockers")
    if receipt.get("rollback_ready") is True:
        errors.append("gstack:blocked_receipt_must_not_claim_rollback_ready")
    return errors


def validate_positive_receipt(receipt: dict[str, Any], path: Path) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    errors.extend(validate_smoke_receipt(receipt, tool_name=TOOL_NAME, owner_lane=OWNER_LANE))
    errors.extend(validate_gstack_guards(receipt))
    validate_authority(receipt, errors)
    if receipt.get("smoke_tested") is not True:
        errors.append("gstack:positive_receipt_must_set_smoke_tested_true")
    errors.extend(f"gstack:sensitive_command:{item}" for item in contains_sensitive_command(receipt.get("smoke_command")))
    for field in ("install_receipt", "rollback_pointer", "command_transcript"):
        findings = contains_raw_path_or_secret(receipt.get(field))
        errors.extend(f"gstack:{field}:{item}" for item in findings)
    errors.extend(f"gstack:redaction:{item}" for item in collect_redaction_findings(receipt))
    return errors, smoke_summary(receipt, receipt_path=path)


def validate_receipts(paths: list[Path], *, require_smoke_tested: bool) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    summaries: list[dict[str, Any]] = []
    positive_count = 0
    blocked_count = 0
    seen = 0
    for path in paths:
        receipt, load_errors = load_receipt(path)
        errors.extend(load_errors)
        if receipt is None:
            continue
        if str(receipt.get("tool_name", "")).strip().lower() != TOOL_NAME:
            errors.append(f"unknown_or_noncanonical_tool:{path.name}:{receipt.get('tool_name')}")
            continue
        seen += 1
        raw_findings = contains_raw_path_or_secret(receipt)
        if raw_findings:
            errors.extend(f"gstack:receipt_contains_raw_private_path_or_secret:{item}" for item in raw_findings)
        if receipt_is_blocked(receipt):
            blocked_count += 1
            errors.extend(validate_blocked_receipt(receipt))
            if require_smoke_tested:
                errors.append("gstack:smoke_tested_required_but_receipt_blocked")
            summaries.append({"tool_name": TOOL_NAME, "receipt_path_hash": stable_hash(str(path)), "r4_status": "blocked", "smoke_tested": False})
            continue
        positive_count += 1
        positive_errors, summary = validate_positive_receipt(receipt, path)
        errors.extend(positive_errors)
        summaries.append({"tool_name": TOOL_NAME, "r4_status": "smoke-tested", "smoke_tested": True, "summary": summary})
    if seen == 0 and paths:
        errors.append("missing_receipt:gstack")
    if seen > 1:
        errors.append(f"duplicate_receipt:gstack:{seen}")
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
    info: list[str] = []
    surface = check_repo_surfaces(root, errors)
    runtime_probe = probe_runtime(root, errors)
    if runtime_probe.get("all_required_actions_ok"):
        info.append("gstack_delivery_loop_runtime_plan_ok")
    paths = receipt_paths(args)
    runtime_receipts = {
        "mode": "not_requested",
        "ok": True,
        "errors": [],
        "warnings": ["no_runtime_receipts_requested"],
        "summaries": [],
        "counts": {"receipt_files": 0, "positive_smoke_tested": 0, "blocked_or_not_installed": 0, "errors": 0, "warnings": 1},
    }
    if paths:
        runtime_receipts = validate_receipts(paths, require_smoke_tested=bool(args.require_smoke_tested))
        runtime_receipts["mode"] = "receipt_validation"
        errors.extend(runtime_receipts["errors"])
    elif args.require_smoke_tested:
        errors.append("runtime_receipts_required_for_smoke_tested_gate")
    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root_hash": hash_text(str(root)),
        "repo_surfaces": surface,
        "runtime_probe": runtime_probe,
        "runtime_receipts": runtime_receipts,
        "errors": sorted(set(errors)),
        "warnings": runtime_receipts.get("warnings", []),
        "info": info,
        "authority_priority": PRIORITY_ORDER,
        "mutates_user_level_state": False,
        "installs_or_clones_gstack": False,
        "launches_browser": False,
        "enables_telemetry": False,
        "remote_publication_allowed": False,
        "local_main_gate_bypassed": False,
        "counts": {
            "errors": len(set(errors)),
            "warnings": len(runtime_receipts.get("warnings", [])),
            "receipt_files": runtime_receipts["counts"]["receipt_files"],
            "positive_smoke_tested": runtime_receipts["counts"]["positive_smoke_tested"],
            "blocked_or_not_installed": runtime_receipts["counts"]["blocked_or_not_installed"],
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate gstack Codex delivery-loop governance surfaces.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--receipt-dir", default=None)
    parser.add_argument("--receipt", action="append", default=[])
    parser.add_argument("--require-smoke-tested", action="store_true")
    parser.add_argument("--json", action="store_true")
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
    raise SystemExit(main(sys.argv[1:]))
