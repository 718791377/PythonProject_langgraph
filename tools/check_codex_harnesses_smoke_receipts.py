#!/usr/bin/env python3
"""Validate R4 Codex harness smoke receipts.

Positive ``smoke-tested`` receipts are delegated to the generic
``user_level_receipt_governance`` R4 smoke contract and then tightened for the
Codex harness lane.  Honest blocked/not-installed receipts are accepted as
evidence, but they never count as smoke-tested runtime evidence.

R4 is candidate-registry-driven: Pi and oh-my-pi are no longer the only
recognized shapes.  The checker requires each receipt to carry the selected
candidate id, adapter kind, guard profile, source pin, license note, sensitive
command policy, hook policy, async/headless lifecycle state, and an authority
decision explaining the harness runtime-safety decision.
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


CHECK_NAME = "codex_harnesses_smoke_receipts"
RUNNER = Path("tools/run_codex_harnesses_smoke.py")
CHECKER = Path("tools/check_codex_harnesses_smoke_receipts.py")
PLAN_EN = Path("docs_bilingual/implementation_plans/codex_harnesses_governance_plan.md")
PLAN_ZH = Path("docs_bilingual/implementation_plans/codex_harnesses_governance_plan.zh-CN.md")
GOVERNANCE_CHECKER = Path("tools/check_codex_harnesses_governance.py")
CI_MANIFEST = Path("tools/ci/ci_test_manifest.json")
SAFETY_REGISTRY = Path("tools/safety_rule_script_backing_registry.json")
GUARD_SCRIPT = Path("tools/run_openspec_guard.py")
TEST_NAME = "codex_harnesses_smoke_receipts.test.py"
CANDIDATE_REGISTRY = {
    "pi-runtime": {
        "owner_lane": "codex-harnesses:pi-runtime",
        "adapter_kind": "package-runtime",
        "source_url": "https://pi.dev/",
        "aliases": {"Pi", "pi", "pi.dev", "pi-runtime"},
    },
    "oh-my-pi-sidecar": {
        "owner_lane": "codex-harnesses:oh-my-pi-sidecar",
        "adapter_kind": "sidecar-ux",
        "source_url": "https://github.com/can1357/oh-my-pi",
        "aliases": {"oh-my-pi", "oh_my_pi", "oh my pi", "oh-my-pi-sidecar"},
    },
    "revfactory-harness-team-factory": {
        "owner_lane": "codex-harnesses:revfactory-harness-team-factory",
        "adapter_kind": "team-factory",
        "source_url": "https://github.com/revfactory/harness",
        "aliases": {"revfactory", "revfactory/harness", "revfactory-harness", "revfactory-harness-team-factory"},
    },
    "ohmyopenagent-discipline-layer": {
        "owner_lane": "codex-harnesses:ohmyopenagent-discipline-layer",
        "adapter_kind": "discipline-layer",
        "source_url": "https://github.com/ymymssss/ohmyopenagent",
        "aliases": {"ohmyopenagent", "oh-my-openagent", "ohmyopenagent-discipline-layer"},
    },
    "snow-cli-terminal-agent-runtime": {
        "owner_lane": "codex-harnesses:snow-cli-terminal-agent-runtime",
        "adapter_kind": "terminal-agent-runtime",
        "source_url": "https://github.com/MayDay-wpf/snow-cli",
        "aliases": {"snow-cli", "snow cli", "snow-cli-terminal-agent-runtime"},
    },
}
ALIASES = {
    alias.lower(): candidate_id
    for candidate_id, meta in CANDIDATE_REGISTRY.items()
    for alias in set(meta["aliases"]) | {candidate_id}
}
FORBIDDEN_SIBLING_TERMS = (
    "CLI-Anything",
    "WXWork_CLI",
    "WXWork.exe",
    "chrome-devtools-mcp",
    "cdp-bridge-mcp",
    "OpenCLI",
)
FORBIDDEN_COMMAND_PATTERNS = (
    re.compile(r"(?i)\b(write|send|post|delete|mutate|patch|apply|commit|merge|push)\b"),
    re.compile(r"(?i)\b(start|daemon|serve|attach|takeover|replace)\b"),
    re.compile(r"(?i)\b(job\.run|run[-_\s]?job|harness[-_\s]?job)\b"),
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
GENERIC_SAFETY_FLAGS = (
    "write_performed",
    "live_action_performed",
    "sensitive_action_performed",
    "user_level_state_mutated",
    "reads_browser_data",
    "external_message_sent",
)
HARNESS_TAKEOVER_FLAGS = (
    "write_capable_harness_job",
    "codex_launcher_mutated",
    "native_codex_replaced",
    "native_subagents_replaced",
    "native_omx_replaced",
    "langgraph_replaced",
    "apply_patch_replaced",
    "local_main_gate_bypassed",
    "active_candidate",
    "sidecar_takeover",
)
REQUIRED_PLAN_MARKERS = (
    "tools/run_codex_harnesses_smoke.py",
    "tools/check_codex_harnesses_smoke_receipts.py",
    "codex_harnesses_smoke_receipts.test.py",
    "blocked receipts",
    "not smoke-tested",
    "candidate registry",
    "candidate_id",
    "adapter_kind",
    "guard_profile",
    "sensitive_command_policy",
    "hook_policy",
    "authority_decision",
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


def normalize_harness(value: Any) -> str | None:
    text = str(value or "").strip()
    if text in CANDIDATE_REGISTRY:
        return text
    return ALIASES.get(text.lower())


def contains_forbidden_sibling_term(value: Any) -> list[str]:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True) if not isinstance(value, str) else value
    return [term for term in FORBIDDEN_SIBLING_TERMS if term.lower() in text.lower()]


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
        "safety_registry_has_guard_step": False,
        "openspec_guard_references_checker": False,
        "governance_checker_references_r4": False,
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
            if isinstance(rule, dict) and rule.get("id") == "codex-harnesses-governance":
                scripts = set(rule.get("script_controls", [])) if isinstance(rule.get("script_controls"), list) else set()
                steps = set(rule.get("guard_steps", [])) if isinstance(rule.get("guard_steps"), list) else set()
                surface["safety_registry_has_scripts"] = RUNNER.as_posix() in scripts and CHECKER.as_posix() in scripts
                surface["safety_registry_has_guard_step"] = CHECK_NAME in steps
    if not surface["safety_registry_has_scripts"]:
        errors.append("safety_registry_codex_harnesses_rule_missing_r4_scripts")
    if not surface["safety_registry_has_guard_step"]:
        errors.append("safety_registry_codex_harnesses_rule_missing_r4_guard_step")

    guard_text = read_text(root / GUARD_SCRIPT, errors)
    surface["openspec_guard_references_checker"] = "check_codex_harnesses_smoke_receipts" in guard_text
    if not surface["openspec_guard_references_checker"]:
        errors.append("openspec_guard_missing:check_codex_harnesses_smoke_receipts")

    governance_text = read_text(root / GOVERNANCE_CHECKER, errors)
    surface["governance_checker_references_r4"] = (
        RUNNER.as_posix() in governance_text
        and CHECKER.as_posix() in governance_text
        and TEST_NAME in governance_text
    )
    if not surface["governance_checker_references_r4"]:
        errors.append("codex_harnesses_governance_checker_missing_r4_smoke_surface_requirements")
    return surface


def receipt_is_blocked(receipt: dict[str, Any]) -> bool:
    result = receipt.get("smoke_result")
    result_status = str(result.get("status", "") if isinstance(result, dict) else result).strip().lower()
    r4_status = str(receipt.get("r4_status", "")).strip().lower()
    return receipt.get("smoke_tested") is not True and (
        result_status in {"blocked", "not-installed", "not_installed"} or r4_status in {"blocked", "not-installed", "not_installed"}
    )


def validate_authority_decision(receipt: dict[str, Any], candidate_id: str, *, blocked: bool) -> list[str]:
    errors: list[str] = []
    decision = receipt.get("authority_decision")
    if not isinstance(decision, dict):
        return [f"{candidate_id}:authority_decision_required"]
    if decision.get("candidate_id") not in {candidate_id, None}:
        errors.append(f"{candidate_id}:authority_decision_candidate_id_mismatch")
    source = str(decision.get("source", ""))
    if source != "harness runtime safety":
        errors.append(f"{candidate_id}:authority_decision_source_must_be_harness_runtime_safety")
    priority = str(decision.get("priority_order", ""))
    for marker in ("Comet", "OpenSpec/Superpowers", "gstack", "harness runtime safety", "Spec Kit"):
        if marker not in priority:
            errors.append(f"{candidate_id}:authority_decision_priority_missing:{marker}")
    status = str(decision.get("status", "")).strip().lower()
    if blocked:
        if status != "blocked":
            errors.append(f"{candidate_id}:blocked_authority_decision_must_be_blocked")
    elif status != "allow-read-only-smoke":
        errors.append(f"{candidate_id}:positive_authority_decision_must_allow_read_only_smoke")
    return errors


def validate_policy_fields(receipt: dict[str, Any], candidate_id: str) -> list[str]:
    errors: list[str] = []
    sensitive = receipt.get("sensitive_command_policy")
    if not isinstance(sensitive, dict):
        errors.append(f"{candidate_id}:sensitive_command_policy_required")
    else:
        if sensitive.get("writes_allowed") is not False:
            errors.append(f"{candidate_id}:sensitive_command_policy_writes_must_be_false")
        if sensitive.get("sensitive_commands_allowed") is not False:
            errors.append(f"{candidate_id}:sensitive_command_policy_sensitive_commands_must_be_false")
    hooks = receipt.get("hook_policy")
    if not isinstance(hooks, dict):
        errors.append(f"{candidate_id}:hook_policy_required")
    else:
        if hooks.get("mutation_hooks_allowed") is not False:
            errors.append(f"{candidate_id}:hook_policy_mutation_hooks_must_be_false")
    lifecycle = receipt.get("async_headless_lifecycle_state")
    if not isinstance(lifecycle, dict):
        errors.append(f"{candidate_id}:async_headless_lifecycle_state_required")
    else:
        mode = str(lifecycle.get("mode", ""))
        if "read-only" not in mode:
            errors.append(f"{candidate_id}:async_headless_lifecycle_state_must_be_read_only")
    return errors


def validate_harness_guards(receipt: dict[str, Any], candidate_id: str) -> list[str]:
    errors: list[str] = []
    meta = CANDIDATE_REGISTRY[candidate_id]
    if receipt.get("candidate_id") != candidate_id:
        errors.append(f"{candidate_id}:candidate_id_mismatch")
    if receipt.get("adapter_kind") != meta["adapter_kind"]:
        errors.append(f"{candidate_id}:adapter_kind_mismatch")
    if receipt.get("source_url") != meta["source_url"]:
        errors.append(f"{candidate_id}:source_url_mismatch")
    for field in ("source_pin", "license_note", "guard_profile"):
        if not isinstance(receipt.get(field), str) or not str(receipt.get(field)).strip():
            errors.append(f"{candidate_id}:{field}_required")
    errors.extend(validate_policy_fields(receipt, candidate_id))
    owner_lane = str(receipt.get("owner_lane", ""))
    if not owner_lane.startswith("codex-harnesses:"):
        errors.append(f"{candidate_id}:owner_lane_must_be_codex_harnesses")
    expected_owner = meta["owner_lane"]
    if owner_lane != expected_owner:
        errors.append(f"{candidate_id}:owner_lane_mismatch")
    read_guard = receipt.get("read_guard")
    if not isinstance(read_guard, dict) or str(read_guard.get("status", "")).lower() != "pass" or read_guard.get("read_only") is not True:
        errors.append(f"{candidate_id}:read_guard_must_pass_read_only")
    write_guard = receipt.get("write_guard")
    if (
        not isinstance(write_guard, dict)
        or str(write_guard.get("status", "")).lower() != "pass"
        or write_guard.get("write_allowed") is not False
        or write_guard.get("write_performed") is not False
    ):
        errors.append(f"{candidate_id}:write_guard_must_block_writes")
    job_state = receipt.get("job_state")
    if not isinstance(job_state, dict):
        errors.append(f"{candidate_id}:job_state_required")
    else:
        if job_state.get("write_capable") is not False:
            errors.append(f"{candidate_id}:job_state_must_not_be_write_capable")
        if job_state.get("sidecar_started") is True:
            errors.append(f"{candidate_id}:job_state_must_not_start_sidecar")
    if receipt.get("no_codex_takeover") is not True:
        errors.append(f"{candidate_id}:no_codex_takeover_must_be_true")
    for flag in GENERIC_SAFETY_FLAGS + HARNESS_TAKEOVER_FLAGS:
        if receipt.get(flag) is True:
            errors.append(f"{candidate_id}:smoke_receipt_forbidden_{flag}")
    return errors


def validate_blocked_receipt(receipt: dict[str, Any], candidate_id: str) -> list[str]:
    errors = validate_harness_guards(receipt, candidate_id)
    errors.extend(validate_authority_decision(receipt, candidate_id, blocked=True))
    if receipt.get("smoke_tested") is True:
        errors.append(f"{candidate_id}:blocked_receipt_must_not_be_smoke_tested")
    blockers = receipt.get("blockers")
    if not isinstance(blockers, list) or not blockers:
        errors.append(f"{candidate_id}:blocked_receipt_requires_blockers")
    if receipt.get("rollback_ready") is True:
        errors.append(f"{candidate_id}:blocked_receipt_must_not_claim_rollback_ready")
    return errors


def validate_positive_receipt(receipt: dict[str, Any], candidate_id: str, path: Path) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    errors.extend(validate_smoke_receipt(receipt, tool_name=candidate_id, owner_lane=CANDIDATE_REGISTRY[candidate_id]["owner_lane"]))
    errors.extend(validate_harness_guards(receipt, candidate_id))
    errors.extend(validate_authority_decision(receipt, candidate_id, blocked=False))
    if receipt.get("smoke_tested") is not True:
        errors.append(f"{candidate_id}:positive_receipt_must_set_smoke_tested_true")
    errors.extend(f"{candidate_id}:sensitive_command:{item}" for item in contains_sensitive_command(receipt.get("smoke_command")))
    for field in ("install_receipt", "rollback_pointer", "command_transcript"):
        findings = contains_raw_path_or_secret(receipt.get(field))
        errors.extend(f"{candidate_id}:{field}:{item}" for item in findings)
    errors.extend(f"{candidate_id}:redaction:{item}" for item in collect_redaction_findings(receipt))
    return errors, smoke_summary(receipt, receipt_path=path)


def validate_receipts(paths: list[Path], *, require_smoke_tested: bool) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    by_harness: dict[str, list[dict[str, Any]]] = {candidate_id: [] for candidate_id in CANDIDATE_REGISTRY}
    summaries: list[dict[str, Any]] = []
    positive_count = 0
    blocked_count = 0

    for path in paths:
        receipt, load_errors = load_receipt(path)
        errors.extend(load_errors)
        if receipt is None:
            continue
        forbidden_terms = contains_forbidden_sibling_term(receipt)
        if forbidden_terms:
            errors.extend(f"forbidden_sibling_lane_term:{term}:{path.name}" for term in forbidden_terms)
        harness = normalize_harness(receipt.get("candidate_id") or receipt.get("tool_name"))
        if harness is None:
            errors.append(f"unknown_or_noncanonical_candidate:{path.name}:{receipt.get('tool_name')}")
            continue
        by_harness[harness].append(receipt)
        raw_findings = contains_raw_path_or_secret(receipt)
        if raw_findings:
            errors.extend(f"{harness}:receipt_contains_raw_private_path_or_secret:{item}" for item in raw_findings)
        if receipt_is_blocked(receipt):
            blocked_count += 1
            errors.extend(validate_blocked_receipt(receipt, harness))
            if require_smoke_tested:
                errors.append(f"{harness}:smoke_tested_required_but_receipt_blocked")
            summaries.append(
                {
                    "candidate_id": harness,
                    "adapter_kind": CANDIDATE_REGISTRY[harness]["adapter_kind"],
                    "receipt_path_hash": stable_hash(str(path)),
                    "r4_status": "blocked",
                    "smoke_tested": False,
                    "blocker_count": len(receipt.get("blockers", [])) if isinstance(receipt.get("blockers"), list) else 0,
                }
            )
            continue
        positive_count += 1
        positive_errors, summary = validate_positive_receipt(receipt, harness, path)
        errors.extend(positive_errors)
        summaries.append({"candidate_id": harness, "r4_status": "smoke-tested", "smoke_tested": True, "summary": summary})

    for harness, receipts in by_harness.items():
        if not receipts:
            errors.append(f"missing_receipt:{harness}")
        elif len(receipts) > 1:
            errors.append(f"duplicate_receipt:{harness}:{len(receipts)}")

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
        "candidate_registry": {
            "candidate_ids": list(CANDIDATE_REGISTRY),
            "adapter_kinds": sorted({meta["adapter_kind"] for meta in CANDIDATE_REGISTRY.values()}),
        },
        "repo_surfaces": surface,
        "runtime_receipts": runtime,
        "errors": sorted(set(errors)),
        "warnings": runtime.get("warnings", []),
        "mutates_user_level_state": False,
        "installs_pi_or_oh_my_pi": False,
        "starts_sidecar": False,
        "runs_write_capable_harness_job": False,
        "codex_launcher_mutated": False,
        "native_codex_replaced": False,
        "native_subagents_replaced": False,
        "native_omx_replaced": False,
        "langgraph_replaced": False,
        "apply_patch_replaced": False,
        "local_main_gate_bypassed": False,
        "counts": {
            "errors": len(set(errors)),
            "warnings": len(runtime.get("warnings", [])),
            "receipt_files": runtime["counts"]["receipt_files"],
            "positive_smoke_tested": runtime["counts"]["positive_smoke_tested"],
            "blocked_or_not_installed": runtime["counts"]["blocked_or_not_installed"],
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate R4 Codex harness smoke receipts.")
    parser.add_argument("--root", default=".", help="Repository root for checker-backed surfaces.")
    parser.add_argument("--receipt-dir", default=None, help="Directory containing R4 smoke receipts.")
    parser.add_argument("--receipt", action="append", default=[], help="Explicit R4 smoke receipt path.")
    parser.add_argument("--require-smoke-tested", action="store_true", help="Fail if any canonical harness is blocked.")
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
