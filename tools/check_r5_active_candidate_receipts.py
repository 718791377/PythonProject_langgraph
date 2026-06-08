#!/usr/bin/env python3
"""Validate R5 active-candidate receipts across user-level runtime lanes.

This checker is deliberately repo-local and non-mutating.  It does not install
tools, launch browsers, send messages, start harness jobs, initialize Spec Kit,
select durable backends, or publish remotes.  It validates the shared R5
receipt contract from ``user_level_receipt_governance`` and tightens it for the
specific lane named by ``--lane``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from user_level_receipt_governance import (
    REQUIRED_PRIORITY_ORDER,
    active_candidate_summary,
    smoke_pass,
    stable_hash,
    validate_active_candidate_receipt,
)


CHECK_NAME = "r5_active_candidate_receipts"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def future_expiry(minutes: int = 10) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()


def short_hash(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


def value_text(value: Any) -> str:
    return "" if value is None else str(value)


def status_pass(value: Any) -> bool:
    return smoke_pass(value)


@dataclass(frozen=True)
class LaneProfile:
    lane: str
    tool_name: str
    owner_lane: str
    action: str
    extra: Callable[[dict[str, Any]], list[str]]


def _require_field(receipt: dict[str, Any], field: str, blockers: list[str]) -> Any:
    value = receipt.get(field)
    if value in (None, "", [], {}):
        blockers.append(f"{field}_required")
    return value


def _require_false(receipt: dict[str, Any], field: str, blockers: list[str]) -> None:
    if receipt.get(field) is not False:
        blockers.append(f"{field}_must_be_false")


def _require_true(receipt: dict[str, Any], field: str, blockers: list[str]) -> None:
    if receipt.get(field) is not True:
        blockers.append(f"{field}_must_be_true")


def _require_pass(receipt: dict[str, Any], field: str, blockers: list[str]) -> None:
    if not status_pass(receipt.get(field)):
        blockers.append(f"{field}_must_pass")


def validate_mcp_skills(receipt: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    _require_pass(receipt, "risk_profile", blockers)
    _require_pass(receipt, "sensitive_call_authorization", blockers)
    _require_false(receipt, "native_subagent_evidence", blockers)
    _require_false(receipt, "direct_mcp_call_performed", blockers)
    if value_text(receipt.get("tool_name")) not in {"mcp2cli", "skills2cli"}:
        blockers.append("tool_name_must_be_mcp2cli_or_skills2cli")
    return blockers


def validate_browser_adapter(receipt: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if value_text(receipt.get("tool_name")) not in {"chrome-devtools-mcp", "cdp-bridge-mcp", "OpenCLI"}:
        blockers.append("tool_name_must_be_browser_cli_adapter")
    _require_pass(receipt, "browser_owner_lease", blockers)
    if receipt.get("reads_browser_data") is True:
        _require_pass(receipt, "browser_data_access_authorization", blockers)
    if receipt.get("gui_write_requested") is True:
        _require_pass(receipt, "gui_write_authorization", blockers)
    _require_false(receipt, "raw_browser_data_stored", blockers)
    return blockers


def validate_wxwork(receipt: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    _require_pass(receipt, "send_action_authorization", blockers)
    _require_field(receipt, "message_body_hash", blockers)
    _require_false(receipt, "message_body_included", blockers)
    _require_false(receipt, "external_message_sent", blockers)
    if value_text(receipt.get("tool_name")) != "WXWork_CLI":
        blockers.append("tool_name_must_be_WXWork_CLI")
    return blockers


def validate_stop_slop(receipt: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    _require_pass(receipt, "protected_text_guard", blockers)
    _require_pass(receipt, "response_density_guard", blockers)
    _require_true(receipt, "canary_preserved", blockers)
    if value_text(receipt.get("hook_policy")) not in {"bounded", "disabled-until-authorized"}:
        blockers.append("hook_policy_must_be_bounded")
    if value_text(receipt.get("compression_policy")) not in {"bounded", "disabled-until-authorized"}:
        blockers.append("compression_policy_must_be_bounded")
    return blockers


def validate_gstack(receipt: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    _require_true(receipt, "gstack_subordinate", blockers)
    _require_field(receipt, "delivery_loop_stage", blockers)
    _require_false(receipt, "overrides_comet", blockers)
    _require_false(receipt, "overrides_openspec", blockers)
    _require_false(receipt, "remote_publication_allowed", blockers)
    return blockers


def validate_codex_harnesses(receipt: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field in ("candidate_id", "sensitive_command_policy", "hook_policy"):
        _require_field(receipt, field, blockers)
    for field in ("read_guard", "write_guard", "isolated_worktree", "changed_paths_report", "job_state"):
        _require_pass(receipt, field, blockers)
    _require_true(receipt, "no_codex_takeover", blockers)
    _require_false(receipt, "active_sidecar_took_over_codex", blockers)
    return blockers


def validate_spec_kit_common(receipt: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    _require_true(receipt, "spec_kit_subordinate", blockers)
    _require_false(receipt, "runs_specify", blockers)
    _require_false(receipt, "creates_specify_directory", blockers)
    _require_false(receipt, "creates_root_specs", blockers)
    _require_false(receipt, "writes_speckit_commands", blockers)
    decision = receipt.get("authority_decision")
    if isinstance(decision, dict) and value_text(decision.get("decision")) != "subordinate":
        blockers.append("authority_decision_must_be_subordinate")
    return blockers


def validate_spec_kit_subordinate(receipt: dict[str, Any]) -> list[str]:
    blockers = validate_spec_kit_common(receipt)
    if value_text(receipt.get("adapter_mode")) not in {
        "source-refresh",
        "probe",
        "plan-dry-run",
        "init-dry-run",
        "self-check-dry-run",
    }:
        blockers.append("adapter_mode_must_be_dry_run")
    return blockers


def validate_durable_routing(receipt: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if value_text(receipt.get("backend_family")) not in {"native_omx", "langgraph"}:
        blockers.append("backend_family_must_be_native_omx_or_langgraph")
    if value_text(receipt.get("adoption_decision")) not in {"selected", "running", "adopted", "released"}:
        blockers.append("adoption_decision_invalid")
    if receipt.get("selector_source") != ".omx/state/selectors/active.json":
        blockers.append("selector_source_must_be_repo_local_active_selector")
    return blockers


PROFILES: dict[str, LaneProfile] = {
    "mcp-skills-cli": LaneProfile(
        lane="mcp-skills-cli",
        tool_name="mcp2cli",
        owner_lane="user-level-mcp-skills-cli",
        action="mcp-skills.active-candidate",
        extra=validate_mcp_skills,
    ),
    "browser-cli-adapter": LaneProfile(
        lane="browser-cli-adapter",
        tool_name="chrome-devtools-mcp",
        owner_lane="browser-cli-adapter",
        action="browser-cli.active-candidate",
        extra=validate_browser_adapter,
    ),
    "wxwork-cli": LaneProfile(
        lane="wxwork-cli",
        tool_name="WXWork_CLI",
        owner_lane="wxwork_cli",
        action="wxwork.send.active-candidate",
        extra=validate_wxwork,
    ),
    "stop-slop-caveman": LaneProfile(
        lane="stop-slop-caveman",
        tool_name="stop-slop-caveman",
        owner_lane="stop-slop-caveman",
        action="stop-slop.compress.active-candidate",
        extra=validate_stop_slop,
    ),
    "gstack-delivery-loop": LaneProfile(
        lane="gstack-delivery-loop",
        tool_name="gstack",
        owner_lane="gstack-delivery-loop",
        action="gstack.delivery-loop.active-candidate",
        extra=validate_gstack,
    ),
    "codex-harnesses": LaneProfile(
        lane="codex-harnesses",
        tool_name="codex-harness",
        owner_lane="codex-harnesses",
        action="codex-harness.job.active-candidate",
        extra=validate_codex_harnesses,
    ),
    "spec-kit-authority": LaneProfile(
        lane="spec-kit-authority",
        tool_name="spec-kit-authority",
        owner_lane="spec-kit-authority-guard",
        action="spec-kit.authority.active-candidate",
        extra=validate_spec_kit_common,
    ),
    "spec-kit-subordinate": LaneProfile(
        lane="spec-kit-subordinate",
        tool_name="spec-kit-subordinate",
        owner_lane="spec-kit-subordinate-adapter",
        action="spec-kit.subordinate.active-candidate",
        extra=validate_spec_kit_subordinate,
    ),
    "durable-routing": LaneProfile(
        lane="durable-routing",
        tool_name="durable-routing-adoption",
        owner_lane="durable-smoke-adoption-gate",
        action="durable.adopt.apply",
        extra=validate_durable_routing,
    ),
}


def base_receipt(profile: LaneProfile) -> dict[str, Any]:
    target = "repo:D:/PythonProject_langgraph"
    return {
        "schema_version": 1,
        "receipt_type": "r5-active-candidate",
        "lane": profile.lane,
        "tool_name": profile.tool_name,
        "owner_lane": profile.owner_lane,
        "runtime_stage": "active-candidate",
        "action": profile.action,
        "target": target,
        "authorization_receipt": {
            "status": "pass",
            "action": profile.action,
            "target": target,
            "scope": [profile.action],
            "expiry": future_expiry(),
            "session": "main-session",
            "operator_confirmation": True,
        },
        "owner_lease": {"status": "pass", "owner": "main-session", "expires_at": future_expiry()},
        "target_action_allowlist": {"targets": [target], "actions": [profile.action]},
        "command_transcript": "bounded active-candidate transcript",
        "transcript_redaction": {"status": "pass", "redacted_transcript_hash": "redacted-hash"},
        "redaction_status": "pass",
        "timeout_release": {"status": "pass", "released": True, "timeout_seconds": 30},
        "rollback_pointer": "rollback-ref",
        "rollback_ready": True,
        "cleanup_evidence": {"status": "pass", "cleaned": True},
        "remote_publication_mutated": False,
        "authority_decision": {"decision": "active-candidate", "priority_order": REQUIRED_PRIORITY_ORDER},
    }


def fixture_for_lane(lane: str) -> dict[str, Any]:
    profile = PROFILES[lane]
    receipt = base_receipt(profile)
    if lane == "mcp-skills-cli":
        receipt.update(
            {
                "risk_profile": {"status": "pass", "risk": "bounded-discovery"},
                "sensitive_call_authorization": {"status": "pass"},
                "native_subagent_evidence": False,
                "direct_mcp_call_performed": False,
            }
        )
    elif lane == "browser-cli-adapter":
        receipt.update(
            {
                "browser_owner_lease": {"status": "pass"},
                "reads_browser_data": True,
                "browser_data_access_authorization": {"status": "pass"},
                "gui_write_requested": True,
                "gui_write_authorization": {"status": "pass"},
                "raw_browser_data_stored": False,
            }
        )
    elif lane == "wxwork-cli":
        receipt.update(
            {
                "send_action_authorization": {"status": "pass"},
                "message_body_hash": short_hash("hello"),
                "message_body_included": False,
                "external_message_sent": False,
            }
        )
    elif lane == "stop-slop-caveman":
        receipt.update(
            {
                "protected_text_guard": {"status": "pass"},
                "response_density_guard": {"status": "pass"},
                "canary_preserved": True,
                "hook_policy": "bounded",
                "compression_policy": "bounded",
            }
        )
    elif lane == "gstack-delivery-loop":
        receipt.update(
            {
                "gstack_subordinate": True,
                "delivery_loop_stage": "review",
                "overrides_comet": False,
                "overrides_openspec": False,
                "remote_publication_allowed": False,
            }
        )
    elif lane == "codex-harnesses":
        receipt.update(
            {
                "candidate_id": "revfactory-harness",
                "job_state": {"status": "pass", "job_id": "job-1"},
                "read_guard": {"status": "pass"},
                "write_guard": {"status": "pass"},
                "isolated_worktree": {"status": "pass"},
                "changed_paths_report": {"status": "pass", "paths": []},
                "no_codex_takeover": True,
                "active_sidecar_took_over_codex": False,
                "sensitive_command_policy": "blocked-by-default",
                "hook_policy": "disabled-until-authorized",
            }
        )
    elif lane == "spec-kit-authority":
        receipt["authority_decision"] = {"decision": "subordinate", "priority_order": REQUIRED_PRIORITY_ORDER}
        receipt.update(
            {
                "spec_kit_subordinate": True,
                "runs_specify": False,
                "creates_specify_directory": False,
                "creates_root_specs": False,
                "writes_speckit_commands": False,
            }
        )
    elif lane == "spec-kit-subordinate":
        receipt["authority_decision"] = {"decision": "subordinate", "priority_order": REQUIRED_PRIORITY_ORDER}
        receipt.update(
            {
                "spec_kit_subordinate": True,
                "runs_specify": False,
                "creates_specify_directory": False,
                "creates_root_specs": False,
                "writes_speckit_commands": False,
                "adapter_mode": "probe",
            }
        )
    elif lane == "durable-routing":
        receipt["receipt_type"] = "durable-routing-adoption"
        receipt.update(
            {
                "backend_family": "langgraph",
                "adoption_decision": "selected",
                "selector_source": ".omx/state/selectors/active.json",
            }
        )
    return receipt


def read_json(path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None, ["receipt_missing"]
    except json.JSONDecodeError:
        return None, ["receipt_invalid_json"]
    except OSError:
        return None, ["receipt_unreadable"]
    if not isinstance(data, dict):
        return None, ["receipt_not_object"]
    return data, []


def validate_lane_receipt(receipt: dict[str, Any], lane: str) -> list[str]:
    profile = PROFILES[lane]
    blockers = list(
        validate_active_candidate_receipt(
            receipt,
            tool_name=profile.tool_name if lane not in {"mcp-skills-cli", "browser-cli-adapter"} else None,
            owner_lane=profile.owner_lane,
        )
    )
    if receipt.get("lane") not in {None, "", lane}:
        blockers.append("lane_mismatch")
    if receipt.get("remote_publication_mutated") is not False:
        blockers.append("remote_publication_must_not_mutate")
    blockers.extend(profile.extra(receipt))
    return sorted(set(blockers))


def receipt_summary(receipt: dict[str, Any] | None, path: Path | None, lane: str, blockers: list[str]) -> dict[str, Any]:
    if not receipt:
        return {"lane": lane, "receipt_path_hash": short_hash(str(path)) if path else "", "active_candidate_valid": False}
    summary = active_candidate_summary(receipt, receipt_path=path or Path("<inline>"))
    summary.update(
        {
            "lane": lane,
            "active_candidate_valid": not blockers,
            "tool_name": value_text(receipt.get("tool_name")),
            "owner_lane": value_text(receipt.get("owner_lane")),
            "remote_publication_mutated": receipt.get("remote_publication_mutated") is True,
            "blockers": blockers,
        }
    )
    return summary


def run_self_test() -> dict[str, Any]:
    errors: list[str] = []
    cases: list[dict[str, Any]] = []
    for lane in PROFILES:
        positive = fixture_for_lane(lane)
        blockers = validate_lane_receipt(positive, lane)
        cases.append({"lane": lane, "case": "positive", "ok": not blockers, "blockers": blockers})
        if blockers:
            errors.append(f"{lane}:positive_failed:{','.join(blockers)}")
        negative = json.loads(json.dumps(positive))
        negative["remote_publication_mutated"] = True
        neg_blockers = validate_lane_receipt(negative, lane)
        cases.append({"lane": lane, "case": "remote_mutation", "ok": not neg_blockers, "blockers": neg_blockers})
        if not neg_blockers:
            errors.append(f"{lane}:negative_remote_mutation_passed")
    return {
        "ok": not errors,
        "cases": cases,
        "errors": errors,
        "counts": {"profiles": len(PROFILES), "cases": len(cases), "errors": len(errors)},
    }


def evaluate(root: Path, lane: str | None, receipt_path: Path | None, self_test: bool = True) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    self_test_result = run_self_test() if self_test else None
    if self_test_result is not None:
        errors.extend(f"self_test:{error}" for error in self_test_result["errors"])
    summary: dict[str, Any] = {}
    if receipt_path is not None:
        if lane not in PROFILES:
            errors.append("lane_required_or_invalid")
            selected_lane = lane or ""
        else:
            selected_lane = lane
        resolved = receipt_path if receipt_path.is_absolute() else root / receipt_path
        receipt, load_errors = read_json(resolved)
        blockers = list(load_errors)
        if receipt is not None and selected_lane:
            blockers.extend(validate_lane_receipt(receipt, selected_lane))
        errors.extend(blockers)
        summary = receipt_summary(receipt, resolved, selected_lane, sorted(set(blockers)))
    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "lane": lane or "",
        "known_lanes": sorted(PROFILES),
        "receipt_summary": summary,
        "self_test": self_test_result,
        "errors": sorted(set(errors)),
        "warnings": warnings,
        "mutates_user_level_state": False,
        "runs_external_tool": False,
        "starts_browser_or_gui": False,
        "sends_external_message": False,
        "mutates_remote_publication": False,
        "counts": {
            "errors": len(set(errors)),
            "warnings": len(warnings),
            "self_test_profiles": 0 if self_test_result is None else self_test_result["counts"]["profiles"],
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate R5 active-candidate receipts without performing actions.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--lane", choices=sorted(PROFILES), default=None)
    parser.add_argument("--receipt", default=None)
    parser.add_argument("--skip-self-test", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = evaluate(
        Path(args.root),
        args.lane,
        Path(args.receipt) if args.receipt else None,
        self_test=not args.skip_self_test,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"{CHECK_NAME}: {'ok' if payload['ok'] else 'failed'}")
        for message in payload["errors"]:
            print(f"ERROR: {message}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
