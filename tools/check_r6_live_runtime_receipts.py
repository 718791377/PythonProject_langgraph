#!/usr/bin/env python3
"""Validate R6 live-runtime receipts for the governed user-level lanes.

This checker is repo-local and non-mutating. It never launches browsers,
sends messages, starts harness jobs, installs user-level wrappers, runs Spec
Kit, mutates durable state, or publishes remotes. It only validates that a
receipt is an explicit R6 blocked/live-ready/live-executed record with
authorization, owner lease, redaction, rollback, cleanup, target-env hashing,
and the priority order:

    Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from user_level_receipt_governance import (
    REQUIRED_PRIORITY_ORDER,
    active_candidate_summary,
    redaction_pass,
    smoke_pass,
    stable_hash,
    timeout_release_pass,
)


CHECK_NAME = "r6_live_runtime_receipts"
DEFAULT_RECEIPT_DIR = Path(".omx/r6-live-runtime/receipts")

LIVE_MODES = {"blocked", "dry-run", "live-ready", "live-executed"}
SIDE_EFFECTS = {
    "none",
    "browser_gui",
    "external_message",
    "harness_job",
    "spec_kit_apply",
    "user_level_install",
    "mixed",
}
TEMPLATE_DISTRIBUTIONS = {
    "project-general-full",
    "project-general-2-stub",
    "repo-local-only",
    "user-level",
}
SPEC_KIT_APPLY_MODES = {"sandbox", "repository", "template"}
CANONICAL_ENV_KEYS = {
    "R6_BROWSER_TARGET_URL",
    "R6_BROWSER_ACTION",
    "R6_WXWORK_TARGET",
    "R6_WXWORK_MESSAGE_TEMPLATE",
    "R6_HARNESS_CANDIDATE_ID",
    "R6_HARNESS_JOB_PROFILE",
    "R6_SPEC_KIT_MODE",
    "R6_SPEC_KIT_TARGET_ROOT",
    "R6_USER_LEVEL_INSTALL_ROOT",
}

R5_ACTIVE_FIELDS = (
    "tool_name",
    "owner_lane",
    "action",
    "target",
    "authorization_receipt",
    "owner_lease",
    "target_action_allowlist",
    "command_transcript",
    "transcript_redaction",
    "redaction_status",
    "timeout_release",
    "rollback_pointer",
    "rollback_ready",
    "cleanup_evidence",
    "remote_publication_mutated",
    "authority_decision",
)
R6_REQUIRED_FIELDS = (
    "receipt_type",
    "lane",
    "runtime_stage",
    "live_mode",
    "live_attempted",
    "live_executed",
    "external_side_effects",
    "target_env_keys",
    "target_env_hash",
    "execution_receipt",
    "template_distribution",
    *R5_ACTIVE_FIELDS,
)

SECRET_VALUE_RE = re.compile(
    r"(?i)(sk-[A-Za-z0-9_-]{8,}|xox[baprs]-[A-Za-z0-9_-]+|"
    r"(?:token|secret|password|cookie|api[_-]?key)\s*[=:]\s*[^&\s]+)"
)
PRIVATE_PATH_RE = re.compile(
    r"(?i)(?:\b[A-Z]:\\(?:Users|PythonProject|project|tmp|temp)\\[^\s\"']+|"
    r"\\\\[^\s\"']+|/(?:home|Users|tmp|var/tmp)/[^\s\"']+)"
)
HEX_RE = re.compile(r"^[0-9a-f]{16,64}$")
SENSITIVE_KEY_PARTS = (
    "raw_env",
    "target_env_value",
    "raw_target",
    "raw_browser",
    "browser_payload",
    "cookie",
    "token",
    "secret",
    "password",
    "api_key",
    "apikey",
    "message_body",
    "message_content",
    "message_contents",
    "wxwork_message",
    "group_name",
    "member_name",
    "target_group",
    "target_member",
    "raw_recipient",
    "recipient_raw",
    "target_group_value",
    "target_member_value",
    "screenshot",
    "confirmation_image",
)
SENSITIVE_KEY_EXCEPTIONS = (
    "hash",
    "redaction",
    "secret_ref",
    "token_ref",
    "cookie_ref",
    "status",
    "policy",
)


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
    return smoke_pass(value) or (isinstance(value, str) and value.strip().lower() in {"ok", "executed"})


def absent_or_false(value: Any) -> bool:
    return value in (None, False, "", [], {})


def dict_status(receipt: dict[str, Any], field: str, blockers: list[str]) -> None:
    if not status_pass(receipt.get(field)):
        blockers.append(f"{field}_must_pass")


def execution_status(execution: dict[str, Any], field: str, blockers: list[str]) -> None:
    if not status_pass(execution.get(field)):
        blockers.append(f"execution_receipt_{field}_must_pass")


@dataclass(frozen=True)
class LaneProfile:
    lane: str
    plan_id: str
    tool_name: str
    owner_lane: str
    action: str
    side_effect: str
    env_keys: tuple[str, ...]
    distribution: str
    extra: Callable[[dict[str, Any], bool], list[str]]


def validate_capability_foundation(receipt: dict[str, Any], live_executed: bool) -> list[str]:
    blockers: list[str] = []
    execution = execution_object(receipt)
    if live_executed:
        for field in ("authorization", "rollback", "cleanup"):
            execution_status(execution, field, blockers)
    if execution.get("user_level_state_mutated") is True and execution.get("user_level_state_mutation_authorized") is not True:
        blockers.append("execution_receipt_user_level_state_mutation_requires_authorization")
    return blockers


def validate_worktree_lifecycle(receipt: dict[str, Any], live_executed: bool) -> list[str]:
    execution = execution_object(receipt)
    blockers: list[str] = []
    if live_executed:
        for field in ("worktree_receipt", "claim_lifecycle"):
            execution_status(execution, field, blockers)
    return blockers


def validate_selector_ownership(receipt: dict[str, Any], live_executed: bool) -> list[str]:
    execution = execution_object(receipt)
    blockers: list[str] = []
    if execution.get("selector_authority_path") not in {None, "", ".omx/state/selectors/active.json"}:
        blockers.append("selector_authority_path_must_be_repo_local_active_selector")
    if live_executed and not status_pass(execution.get("selector_owner_lease")):
        blockers.append("execution_receipt_selector_owner_lease_must_pass")
    if execution.get("persistent_team_claimed") is True and not status_pass(execution.get("selector_evidence")):
        blockers.append("persistent_team_claim_requires_selector_evidence")
    return blockers


def validate_durable_readiness(receipt: dict[str, Any], live_executed: bool) -> list[str]:
    execution = execution_object(receipt)
    blockers: list[str] = []
    if value_text(execution.get("backend_family")) not in {"", "native_omx", "langgraph"}:
        blockers.append("execution_receipt_backend_family_invalid")
    if live_executed and execution.get("selected_backend_ready") is not True:
        blockers.append("execution_receipt_selected_backend_ready_required")
    if live_executed and execution.get("selector_authority_path") != ".omx/state/selectors/active.json":
        blockers.append("execution_receipt_selector_authority_path_required")
    return blockers


def validate_langgraph_release(receipt: dict[str, Any], live_executed: bool) -> list[str]:
    execution = execution_object(receipt)
    blockers: list[str] = []
    if value_text(execution.get("langgraph_state_root")) not in {"", ".omx/state/langgraph/"}:
        blockers.append("langgraph_state_root_must_be_repo_local")
    if live_executed:
        execution_status(execution, "state_release_evidence", blockers)
    return blockers


def validate_durable_smoke_adoption(receipt: dict[str, Any], live_executed: bool) -> list[str]:
    execution = execution_object(receipt)
    blockers: list[str] = []
    if live_executed:
        if value_text(execution.get("backend_family")) not in {"native_omx", "langgraph"}:
            blockers.append("execution_receipt_backend_family_required")
        execution_status(execution, "backend_family_ownership", blockers)
        if not timeout_release_pass(execution.get("timeout_release")):
            blockers.append("execution_receipt_timeout_release_must_pass")
    return blockers


def validate_mcp_skills_cli(receipt: dict[str, Any], live_executed: bool) -> list[str]:
    execution = execution_object(receipt)
    blockers: list[str] = []
    if execution.get("agent_skill_profile_boundary_preserved") is False:
        blockers.append("agent_skill_profile_boundary_must_be_preserved")
    if live_executed and execution.get("user_level_state_mutated") is not True:
        blockers.append("mcp_skills_live_execution_requires_user_level_state_mutation_receipt")
    return blockers


def validate_browser_adapter(receipt: dict[str, Any], live_executed: bool) -> list[str]:
    execution = execution_object(receipt)
    blockers: list[str] = []
    if not absent_or_false(execution.get("raw_browser_data_stored")):
        blockers.append("raw_browser_data_stored_must_be_false")
    if live_executed:
        if execution.get("browser_action_allowlisted") is not True:
            blockers.append("execution_receipt_browser_action_allowlisted_required")
        if execution.get("browser_owner_lease") not in (None, "") and not status_pass(execution.get("browser_owner_lease")):
            blockers.append("execution_receipt_browser_owner_lease_must_pass")
    return blockers


def validate_wxwork(receipt: dict[str, Any], live_executed: bool) -> list[str]:
    execution = execution_object(receipt)
    blockers: list[str] = []
    if not absent_or_false(execution.get("message_body_included")):
        blockers.append("message_body_included_must_be_false")
    if not absent_or_false(execution.get("recipient_included")):
        blockers.append("recipient_included_must_be_false")
    if not absent_or_false(execution.get("direct_paste_mention_used")):
        blockers.append("direct_paste_mention_used_must_be_false")
    if not absent_or_false(execution.get("evidence_artifact_included")):
        blockers.append("evidence_artifact_included_must_be_false")
    if live_executed:
        for field in (
            "message_body_hash",
            "target_group_hash",
            "target_member_hash",
            "ordinary_message_hash",
            "mention_message_hash",
            "visual_confirmation_hash",
            "human_confirmable_evidence_hash",
        ):
            if not value_text(execution.get(field)).strip():
                blockers.append(f"execution_receipt_{field}_required")
        for field in (
            "cli_anything_visual_rendering_verified",
            "visual_control_verified",
            "external_message_sent",
            "ordinary_message_sent",
            "right_click_member_performed",
            "mention_menu_selected",
            "mention_message_sent",
        ):
            if execution.get(field) is not True:
                blockers.append(f"execution_receipt_{field}_required")
    return blockers


def validate_stop_slop(receipt: dict[str, Any], live_executed: bool) -> list[str]:
    execution = execution_object(receipt)
    blockers: list[str] = []
    if live_executed:
        if execution.get("canary_preserved") is not True:
            blockers.append("execution_receipt_canary_preserved_required")
        execution_status(execution, "response_density_guard", blockers)
    return blockers


def validate_gstack(receipt: dict[str, Any], live_executed: bool) -> list[str]:
    execution = execution_object(receipt)
    blockers: list[str] = []
    if execution.get("gstack_subordinate") is False:
        blockers.append("execution_receipt_gstack_subordinate_must_be_true_or_absent")
    for field in (
        "overrides_comet",
        "overrides_openspec",
        "overrides_superpowers",
        "local_main_gate_bypassed",
        "remote_publication_gate_bypassed",
    ):
        if execution.get(field) is True:
            blockers.append(f"execution_receipt_{field}_must_be_false")
    return blockers


def validate_codex_harnesses(receipt: dict[str, Any], live_executed: bool) -> list[str]:
    execution = execution_object(receipt)
    blockers: list[str] = []
    if live_executed:
        for field in ("read_guard", "write_guard", "isolated_worktree", "changed_paths_report", "job_state"):
            execution_status(execution, field, blockers)
        if execution.get("no_codex_takeover") is not True:
            blockers.append("execution_receipt_no_codex_takeover_required")
        if execution.get("active_sidecar_took_over_codex") is True:
            blockers.append("execution_receipt_active_sidecar_took_over_codex_must_be_false")
    return blockers


def validate_spec_kit(receipt: dict[str, Any], live_executed: bool) -> list[str]:
    execution = execution_object(receipt)
    blockers: list[str] = []
    if execution.get("spec_kit_subordinate") is False:
        blockers.append("execution_receipt_spec_kit_subordinate_must_be_true_or_absent")
    for field in ("takes_authority", "overrides_comet", "overrides_openspec", "overrides_superpowers", "remote_publication_mutated"):
        if execution.get(field) is True:
            blockers.append(f"execution_receipt_{field}_must_be_false")
    mode = value_text(execution.get("spec_kit_apply_mode"))
    if live_executed and mode not in SPEC_KIT_APPLY_MODES:
        blockers.append("execution_receipt_spec_kit_apply_mode_invalid")
    if mode == "sandbox":
        if execution.get("repository_surfaces_written") is True:
            blockers.append("spec_kit_sandbox_must_not_write_repository_surfaces")
        if live_executed and not value_text(execution.get("sandbox_root_hash")):
            blockers.append("spec_kit_sandbox_root_hash_required")
    elif mode == "repository":
        if execution.get("comet_openspec_owner") is not True:
            blockers.append("spec_kit_repository_apply_requires_comet_openspec_owner")
        if execution.get("spec_kit_subordinate") is not True:
            blockers.append("spec_kit_repository_apply_requires_subordinate_receipt")
        surfaces = execution.get("allowed_repo_surfaces")
        allowed = {".specify/", "specs/"}
        if not isinstance(surfaces, list) or not set(map(str, surfaces)).issubset(allowed):
            blockers.append("spec_kit_repository_allowed_surfaces_invalid")
    elif mode == "template":
        distribution = value_text(receipt.get("template_distribution"))
        if distribution not in {"project-general-full", "project-general-2-stub"}:
            blockers.append("spec_kit_template_apply_requires_template_distribution")
        if distribution == "project-general-2-stub" and execution.get("live_enablement_installed") is True:
            blockers.append("general2_stub_must_not_install_live_enablement")
    return blockers


NOOP_EXTRA: Callable[[dict[str, Any], bool], list[str]] = lambda _receipt, _live_executed: []

LANE_PROFILES: dict[str, LaneProfile] = {
    "user-level-capability-receipt-rollback-redaction": LaneProfile("user-level-capability-receipt-rollback-redaction", "user_level_capability_receipt_rollback_redaction_plan", "r6-capability-receipt", "user-level-capability-receipt", "r6.capability.receipt", "none", (), "repo-local-only", validate_capability_foundation),
    "worktree-receipt-claim-lifecycle": LaneProfile("worktree-receipt-claim-lifecycle", "worktree_receipt_claim_lifecycle_plan", "r6-worktree-receipt", "worktree-receipt-claim-lifecycle", "r6.worktree.receipt", "none", (), "repo-local-only", validate_worktree_lifecycle),
    "repo-local-selector-ownership": LaneProfile("repo-local-selector-ownership", "repo_local_selector_ownership_plan", "r6-selector-ownership", "repo-local-selector-ownership", "r6.selector.ownership", "none", (), "repo-local-only", validate_selector_ownership),
    "durable-capability-readiness-projection": LaneProfile("durable-capability-readiness-projection", "durable_capability_readiness_projection_plan", "r6-durable-readiness", "durable-capability-readiness", "r6.durable.readiness", "none", (), "repo-local-only", validate_durable_readiness),
    "langgraph-state-release-evidence": LaneProfile("langgraph-state-release-evidence", "langgraph_state_release_evidence_plan", "r6-langgraph-release", "langgraph-state-release", "r6.langgraph.release", "none", (), "repo-local-only", validate_langgraph_release),
    "durable-smoke-adoption-gate-template": LaneProfile("durable-smoke-adoption-gate-template", "durable_smoke_adoption_gate_template_plan", "r6-durable-smoke-adoption", "durable-smoke-adoption-gate", "r6.durable.smoke.adopt", "none", (), "repo-local-only", validate_durable_smoke_adoption),
    "user-level-mcp-skills-cli-runtime": LaneProfile("user-level-mcp-skills-cli-runtime", "user_level_mcp_skills_cli_runtime_plan", "r6-mcp-skills-cli", "user-level-mcp-skills-cli", "r6.mcp-skills.install", "user_level_install", ("R6_USER_LEVEL_INSTALL_ROOT",), "user-level", validate_mcp_skills_cli),
    "user-level-browser-cli-adapter-boundary": LaneProfile("user-level-browser-cli-adapter-boundary", "user_level_browser_cli_adapter_boundary_plan", "r6-browser-cli-adapter", "browser-cli-adapter", "r6.browser.action", "browser_gui", ("R6_BROWSER_TARGET_URL", "R6_BROWSER_ACTION"), "user-level", validate_browser_adapter),
    "user-level-cli-anything-wxwork-cli-governance": LaneProfile("user-level-cli-anything-wxwork-cli-governance", "user_level_cli_anything_wxwork_cli_governance_plan", "r6-wxwork-cli", "wxwork_cli", "r6.wxwork.send", "external_message", ("R6_WXWORK_TARGET", "R6_WXWORK_MESSAGE_TEMPLATE"), "user-level", validate_wxwork),
    "stop-slop-caveman-response-density-runtime": LaneProfile("stop-slop-caveman-response-density-runtime", "stop_slop_caveman_response_density_runtime_plan", "r6-stop-slop-caveman", "stop-slop-caveman", "r6.stop-slop.activate", "user_level_install", ("R6_USER_LEVEL_INSTALL_ROOT",), "user-level", validate_stop_slop),
    "gstack-codex-delivery-loop-runtime-governance": LaneProfile("gstack-codex-delivery-loop-runtime-governance", "gstack_codex_delivery_loop_runtime_governance_plan", "r6-gstack-delivery-loop", "gstack-delivery-loop", "r6.gstack.delivery-loop", "none", (), "repo-local-only", validate_gstack),
    "codex-harnesses-governance": LaneProfile("codex-harnesses-governance", "codex_harnesses_governance_plan", "r6-codex-harness", "codex-harnesses", "r6.codex-harness.job", "harness_job", ("R6_HARNESS_CANDIDATE_ID", "R6_HARNESS_JOB_PROFILE"), "repo-local-only", validate_codex_harnesses),
    "spec-kit-authority-guard": LaneProfile("spec-kit-authority-guard", "spec_kit_authority_guard_plan", "r6-spec-kit-authority", "spec-kit-authority-guard", "r6.spec-kit.apply", "spec_kit_apply", ("R6_SPEC_KIT_MODE", "R6_SPEC_KIT_TARGET_ROOT"), "repo-local-only", validate_spec_kit),
    "spec-kit-subordinate-adapter-governance": LaneProfile("spec-kit-subordinate-adapter-governance", "spec_kit_subordinate_adapter_governance_plan", "r6-spec-kit-subordinate", "spec-kit-subordinate-adapter", "r6.spec-kit.subordinate.apply", "spec_kit_apply", ("R6_SPEC_KIT_MODE", "R6_SPEC_KIT_TARGET_ROOT"), "repo-local-only", validate_spec_kit),
}

ALIASES = {
    "user_level_capability_receipt_rollback_redaction_plan": "user-level-capability-receipt-rollback-redaction",
    "worktree_receipt_claim_lifecycle_plan": "worktree-receipt-claim-lifecycle",
    "repo_local_selector_ownership_plan": "repo-local-selector-ownership",
    "durable_capability_readiness_projection_plan": "durable-capability-readiness-projection",
    "langgraph_state_release_evidence_plan": "langgraph-state-release-evidence",
    "durable_smoke_adoption_gate_template_plan": "durable-smoke-adoption-gate-template",
    "user_level_mcp_skills_cli_runtime_plan": "user-level-mcp-skills-cli-runtime",
    "mcp-skills-cli": "user-level-mcp-skills-cli-runtime",
    "user_level_browser_cli_adapter_boundary_plan": "user-level-browser-cli-adapter-boundary",
    "browser-cli-adapter": "user-level-browser-cli-adapter-boundary",
    "user_level_cli_anything_wxwork_cli_governance_plan": "user-level-cli-anything-wxwork-cli-governance",
    "wxwork-cli": "user-level-cli-anything-wxwork-cli-governance",
    "stop_slop_caveman_response_density_runtime_plan": "stop-slop-caveman-response-density-runtime",
    "stop-slop-caveman": "stop-slop-caveman-response-density-runtime",
    "gstack_codex_delivery_loop_runtime_governance_plan": "gstack-codex-delivery-loop-runtime-governance",
    "gstack-delivery-loop": "gstack-codex-delivery-loop-runtime-governance",
    "codex_harnesses_governance_plan": "codex-harnesses-governance",
    "codex-harnesses": "codex-harnesses-governance",
    "spec_kit_authority_guard_plan": "spec-kit-authority-guard",
    "spec-kit-authority": "spec-kit-authority-guard",
    "spec_kit_subordinate_adapter_governance_plan": "spec-kit-subordinate-adapter-governance",
    "spec-kit-subordinate": "spec-kit-subordinate-adapter-governance",
}


def normalize_lane(value: Any) -> str:
    raw = value_text(value).strip()
    dashed = raw.replace("_", "-")
    if dashed in LANE_PROFILES:
        return dashed
    lower = raw.lower()
    return ALIASES.get(lower, ALIASES.get(lower.replace("_", "-"), lower.replace("_", "-")))


def execution_object(receipt: dict[str, Any]) -> dict[str, Any]:
    value = receipt.get("execution_receipt")
    return value if isinstance(value, dict) else {}


def sensitive_key(key: str) -> bool:
    lowered = key.lower()
    if any(exception in lowered for exception in SENSITIVE_KEY_EXCEPTIONS):
        return False
    return any(part in lowered for part in SENSITIVE_KEY_PARTS)


def collect_sensitive_findings(value: Any, *, path: str = "$", findings: list[str] | None = None) -> list[str]:
    findings = findings if findings is not None else []
    if isinstance(value, dict):
        for key, item in value.items():
            child = f"{path}.{key}"
            if sensitive_key(str(key)) and item not in (None, "", [], {}, False):
                findings.append(f"sensitive_field_present:{child}")
            collect_sensitive_findings(item, path=child, findings=findings)
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            collect_sensitive_findings(item, path=f"{path}[{idx}]", findings=findings)
    elif isinstance(value, str):
        if SECRET_VALUE_RE.search(value):
            findings.append(f"inline_secret_value:{path}")
        if PRIVATE_PATH_RE.search(value):
            findings.append(f"raw_private_path:{path}")
    return findings


def validate_common_receipt(receipt: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field in R6_REQUIRED_FIELDS:
        if field not in receipt:
            blockers.append(f"r6_missing_{field}")
    if receipt.get("receipt_type") != "r6-live-runtime":
        blockers.append("receipt_type_must_be_r6_live_runtime")
    if value_text(receipt.get("runtime_stage")).lower().replace("_", "-") not in {"r6", "live-runtime", "live-ready", "live-executed"}:
        blockers.append("runtime_stage_must_be_r6")
    live_mode = value_text(receipt.get("live_mode"))
    live_executed = receipt.get("live_executed") is True
    if live_mode not in LIVE_MODES:
        blockers.append("live_mode_invalid")
    if live_mode == "live-executed" and not live_executed:
        blockers.append("live_executed_must_be_true_for_live_executed_mode")
    if live_mode != "live-executed" and live_executed:
        blockers.append("live_executed_requires_live_executed_mode")
    if live_mode in {"blocked", "dry-run", "live-ready"} and receipt.get("live_executed") is not False:
        blockers.append("non_executed_live_mode_requires_live_executed_false")
    if receipt.get("live_attempted") is not True:
        blockers.append("live_attempted_must_be_true")
    if receipt.get("live_executed") is False and not value_text(receipt.get("blocked_reason")).strip():
        blockers.append("blocked_reason_required_when_not_executed")
    if receipt.get("external_side_effects") not in SIDE_EFFECTS:
        blockers.append("external_side_effects_invalid")
    env_keys = receipt.get("target_env_keys")
    if not isinstance(env_keys, list) or any(not isinstance(item, str) or not item for item in env_keys):
        blockers.append("target_env_keys_must_be_string_list")
    else:
        for key in env_keys:
            if key not in CANONICAL_ENV_KEYS:
                blockers.append(f"target_env_key_not_canonical:{key}")
            if "=" in key or "://" in key or "\\" in key or "/" in key:
                blockers.append("target_env_keys_must_not_contain_values")
    if not HEX_RE.match(value_text(receipt.get("target_env_hash"))):
        blockers.append("target_env_hash_must_be_redacted_hex_hash")
    if receipt.get("template_distribution") not in TEMPLATE_DISTRIBUTIONS:
        blockers.append("template_distribution_invalid")
    if receipt.get("remote_publication_mutated") is not False:
        blockers.append("remote_publication_must_not_mutate")
    for field in ("authorization_receipt", "owner_lease"):
        dict_status(receipt, field, blockers)
    allowlist = receipt.get("target_action_allowlist")
    if not isinstance(allowlist, dict):
        blockers.append("target_action_allowlist_required")
    else:
        target = value_text(receipt.get("target"))
        action = value_text(receipt.get("action"))
        if target and target not in {str(item) for item in allowlist.get("targets", [])} and allowlist.get("targets") != "*":
            blockers.append("target_not_allowlisted")
        if action and action not in {str(item) for item in allowlist.get("actions", [])} and allowlist.get("actions") != "*":
            blockers.append("action_not_allowlisted")
    if not timeout_release_pass(receipt.get("timeout_release")):
        blockers.append("timeout_release_must_pass")
    if receipt.get("rollback_ready") is not True:
        blockers.append("rollback_ready_must_be_true")
    if not smoke_pass(receipt.get("cleanup_evidence")):
        blockers.append("cleanup_evidence_must_pass")
    if not redaction_pass(receipt.get("transcript_redaction")):
        blockers.append("transcript_redaction_must_pass")
    if not redaction_pass(receipt.get("redaction_status")):
        blockers.append("redaction_status_must_pass")
    execution = receipt.get("execution_receipt")
    if not isinstance(execution, dict):
        blockers.append("execution_receipt_must_be_object")
    elif live_executed:
        if not status_pass(execution.get("status")):
            blockers.append("execution_receipt_status_must_pass")
        if not redaction_pass(execution.get("redaction_status")):
            blockers.append("execution_receipt_redaction_status_must_pass")
        if not timeout_release_pass(execution.get("timeout_release")):
            blockers.append("execution_receipt_timeout_release_must_pass")
        if not absent_or_false(execution.get("remote_publication_mutated")):
            blockers.append("execution_receipt_remote_publication_mutated_must_be_false")
    authority = receipt.get("authority_decision")
    if not isinstance(authority, dict):
        blockers.append("authority_decision_required")
    else:
        if authority.get("priority_order") != REQUIRED_PRIORITY_ORDER:
            blockers.append("authority_priority_order_mismatch")
        if value_text(authority.get("decision")).strip().lower() in {
            "override",
            "takeover",
            "replace-openspec",
            "replace-comet",
            "spec-kit-authority",
        }:
            blockers.append("authority_decision_not_allowed")
    blockers.extend(collect_sensitive_findings(receipt))
    return sorted(set(blockers))


def validate_lane_receipt(receipt: dict[str, Any], lane: str | None = None) -> list[str]:
    blockers = validate_common_receipt(receipt)
    selected_lane = normalize_lane(lane or receipt.get("lane"))
    profile = LANE_PROFILES.get(selected_lane)
    if profile is None:
        return sorted(set([*blockers, "lane_required_or_invalid"]))
    if normalize_lane(receipt.get("lane")) != selected_lane:
        blockers.append("lane_mismatch")
    if value_text(receipt.get("tool_name")) != profile.tool_name:
        blockers.append("tool_name_mismatch")
    if value_text(receipt.get("owner_lane")) != profile.owner_lane:
        blockers.append("owner_lane_mismatch")
    if value_text(receipt.get("action")) != profile.action:
        blockers.append("action_mismatch")
    live_mode = value_text(receipt.get("live_mode"))
    live_executed = receipt.get("live_executed") is True
    side_effect = value_text(receipt.get("external_side_effects"))
    if live_executed and side_effect != profile.side_effect:
        blockers.append("external_side_effects_mismatch")
    if not live_executed and side_effect not in {"none", profile.side_effect}:
        blockers.append("non_executed_side_effects_must_be_none_or_profile_family")
    env_keys = receipt.get("target_env_keys") if isinstance(receipt.get("target_env_keys"), list) else []
    if live_mode in {"live-ready", "live-executed"} and not set(profile.env_keys).issubset(set(map(str, env_keys))):
        blockers.append("target_env_keys_missing_required_profile_keys")
    if receipt.get("template_distribution") == "project-general-2-stub" and live_executed:
        blockers.append("project_general_2_stub_must_not_live_execute")
    blockers.extend(profile.extra(receipt, live_executed))
    return sorted(set(blockers))


def base_receipt(profile: LaneProfile) -> dict[str, Any]:
    target = f"env-target-hash:{short_hash(profile.lane)}" if profile.env_keys else "repo-local:r6-runtime"
    return {
        "schema_version": 1,
        "receipt_type": "r6-live-runtime",
        "lane": profile.lane,
        "plan_id": profile.plan_id,
        "tool_name": profile.tool_name,
        "owner_lane": profile.owner_lane,
        "runtime_stage": "R6",
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
        "command_transcript": "redacted R6 live-runtime transcript",
        "transcript_redaction": {"status": "pass", "redacted_transcript_hash": short_hash("transcript"), "raw_transcript_omitted": True},
        "redaction_status": "pass",
        "timeout_release": {"status": "pass", "released": True, "timeout_seconds": 30},
        "rollback_pointer": "rollback-ref:r6-live-runtime-fixture",
        "rollback_ready": True,
        "cleanup_evidence": {"status": "pass", "cleaned": True},
        "remote_publication_mutated": False,
        "authority_decision": {"decision": "r6-live-runtime", "priority_order": REQUIRED_PRIORITY_ORDER},
        "live_attempted": True,
        "external_side_effects": profile.side_effect,
        "target_env_keys": list(profile.env_keys),
        "target_env_hash": short_hash({key: "redacted-present" for key in profile.env_keys}),
        "template_distribution": profile.distribution,
    }


def base_execution(profile: LaneProfile, *, live_executed: bool) -> dict[str, Any]:
    execution: dict[str, Any] = {
        "status": "pass" if live_executed else "blocked",
        "action_performed": live_executed,
        "redaction_status": "pass",
        "timeout_release": {"status": "pass", "released": True, "timeout_seconds": 30},
        "rollback": {"status": "pass"},
        "cleanup": {"status": "pass"},
        "authorization": {"status": "pass"},
        "remote_publication_mutated": False,
        "raw_transcript_omitted": True,
    }
    lane = profile.lane
    if lane == "worktree-receipt-claim-lifecycle":
        execution.update({"worktree_receipt": {"status": "pass"}, "claim_lifecycle": {"status": "pass"}})
    elif lane == "repo-local-selector-ownership":
        execution.update({"selector_authority_path": ".omx/state/selectors/active.json", "selector_owner_lease": {"status": "pass"}, "selector_evidence": {"status": "pass"}, "persistent_team_claimed": False})
    elif lane == "durable-capability-readiness-projection":
        execution.update({"backend_family": "langgraph", "selected_backend_ready": True, "selector_authority_path": ".omx/state/selectors/active.json"})
    elif lane == "langgraph-state-release-evidence":
        execution.update({"langgraph_state_root": ".omx/state/langgraph/", "state_release_evidence": {"status": "pass"}})
    elif lane == "durable-smoke-adoption-gate-template":
        execution.update({"backend_family": "langgraph", "backend_family_ownership": {"status": "pass"}})
    elif lane == "user-level-mcp-skills-cli-runtime":
        execution.update({"agent_skill_profile_boundary_preserved": True, "user_level_state_mutated": True, "user_level_state_mutation_authorized": True})
    elif lane == "user-level-browser-cli-adapter-boundary":
        execution.update({"browser_action_allowlisted": True, "raw_browser_data_stored": False, "browser_owner_lease": {"status": "pass"}})
    elif lane == "user-level-cli-anything-wxwork-cli-governance":
        execution.update({
            "message_body_hash": short_hash("message"),
            "target_group_hash": short_hash("target-group"),
            "target_member_hash": short_hash("target-member"),
            "ordinary_message_hash": short_hash("ordinary-message"),
            "mention_message_hash": short_hash("mention-message"),
            "visual_confirmation_hash": short_hash("visual-confirmation"),
            "human_confirmable_evidence_hash": short_hash("human-confirmable-evidence"),
            "message_body_included": False,
            "recipient_included": False,
            "direct_paste_mention_used": False,
            "evidence_artifact_included": False,
            "cli_anything_visual_rendering_verified": live_executed,
            "visual_control_verified": live_executed,
            "external_message_sent": live_executed,
            "ordinary_message_sent": live_executed,
            "right_click_member_performed": live_executed,
            "mention_menu_selected": live_executed,
            "mention_message_sent": live_executed,
        })
    elif lane == "stop-slop-caveman-response-density-runtime":
        execution.update({"canary_preserved": True, "response_density_guard": {"status": "pass"}, "user_level_state_mutated": True, "user_level_state_mutation_authorized": True})
    elif lane == "gstack-codex-delivery-loop-runtime-governance":
        execution.update({"gstack_subordinate": True, "overrides_comet": False, "overrides_openspec": False, "overrides_superpowers": False, "local_main_gate_bypassed": False, "remote_publication_gate_bypassed": False})
    elif lane == "codex-harnesses-governance":
        execution.update({"read_guard": {"status": "pass"}, "write_guard": {"status": "pass"}, "isolated_worktree": {"status": "pass"}, "changed_paths_report": {"status": "pass", "paths": []}, "job_state": {"status": "pass"}, "no_codex_takeover": True, "active_sidecar_took_over_codex": False})
    elif lane in {"spec-kit-authority-guard", "spec-kit-subordinate-adapter-governance"}:
        execution.update({"spec_kit_subordinate": True, "spec_kit_apply_mode": "sandbox", "repository_surfaces_written": False, "sandbox_root_hash": short_hash("sandbox"), "takes_authority": False, "overrides_comet": False, "overrides_openspec": False, "overrides_superpowers": False})
    return execution


def fixture_for_lane(lane: str, *, live_mode: str = "blocked") -> dict[str, Any]:
    normalized = normalize_lane(lane)
    profile = LANE_PROFILES[normalized]
    live_executed = live_mode == "live-executed"
    receipt = base_receipt(profile)
    receipt.update(
        {
            "live_mode": live_mode,
            "live_executed": live_executed,
            "execution_receipt": base_execution(profile, live_executed=live_executed),
            "blocked_reason": "missing_authorization_or_target" if not live_executed else "",
        }
    )
    if not live_executed:
        receipt["external_side_effects"] = "none"
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


def receipt_summary(receipt: dict[str, Any] | None, path: Path | None, lane: str | None, blockers: list[str]) -> dict[str, Any]:
    if not receipt:
        return {"lane": normalize_lane(lane or ""), "receipt_path_hash": short_hash(str(path)) if path else "", "r6_live_valid": False}
    active_summary = active_candidate_summary(receipt, receipt_path=path or Path("<inline>"))
    return {
        **active_summary,
        "lane": normalize_lane(lane or receipt.get("lane")),
        "plan_id": value_text(receipt.get("plan_id")),
        "r6_live_valid": not blockers,
        "live_mode": value_text(receipt.get("live_mode")),
        "live_attempted": receipt.get("live_attempted") is True,
        "live_executed": receipt.get("live_executed") is True,
        "external_side_effects": value_text(receipt.get("external_side_effects")),
        "target_env_keys": list(receipt.get("target_env_keys")) if isinstance(receipt.get("target_env_keys"), list) else [],
        "target_env_hash": value_text(receipt.get("target_env_hash")),
        "template_distribution": value_text(receipt.get("template_distribution")),
        "remote_publication_mutated": receipt.get("remote_publication_mutated") is True,
        "blockers": blockers,
    }


def parse_receipt_generated_at(receipt: dict[str, Any]) -> datetime | None:
    raw = value_text(receipt.get("generated_at")).strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def lane_accepts_receipt(profile: LaneProfile, receipt: dict[str, Any]) -> bool:
    """Return whether a valid receipt provides default executable evidence.

    Repository-local/default-safe lanes must have a live-executed no-side-effect
    receipt. Sensitive lanes may be represented by a current blocked/live-ready
    receipt when their browser, WXWork, harness, Spec Kit, or user-level install
    target is absent, because the runtime must be default executable without
    silently performing those external or user-level side effects.
    """

    live_mode = value_text(receipt.get("live_mode"))
    live_executed = receipt.get("live_executed") is True
    if profile.side_effect == "none":
        return live_mode == "live-executed" and live_executed and receipt.get("external_side_effects") == "none"
    return live_mode in LIVE_MODES and receipt.get("live_attempted") is True


def audit_receipt_dir(root: Path, receipt_dir: Path, *, max_age_hours: float | None = None) -> dict[str, Any]:
    resolved = receipt_dir if receipt_dir.is_absolute() else root / receipt_dir
    resolved = resolved.resolve()
    try:
        receipt_dir_display = resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        receipt_dir_display = f"external-hash:{short_hash(str(resolved))}"
    now = datetime.now(timezone.utc)
    lane_evidence: dict[str, dict[str, Any]] = {
        lane: {
            "accepted": False,
            "accepted_mode": "",
            "receipt_path_hash": "",
            "receipt_count": 0,
            "valid_receipt_count": 0,
            "policy": "live-executed-required" if profile.side_effect == "none" else "blocked-or-ready-or-executed",
            "side_effect": profile.side_effect,
            "blockers": [],
        }
        for lane, profile in LANE_PROFILES.items()
    }
    errors: list[str] = []
    warnings: list[str] = []
    receipt_files = sorted(resolved.glob("*.json")) if resolved.exists() else []
    invalid_receipts: list[dict[str, Any]] = []
    stale_receipts: list[dict[str, Any]] = []

    for path in receipt_files:
        receipt, load_errors = read_json(path)
        if receipt is None:
            invalid_receipts.append({"path_hash": short_hash(str(path)), "errors": load_errors})
            continue
        lane = normalize_lane(receipt.get("lane"))
        profile = LANE_PROFILES.get(lane)
        if profile is None:
            invalid_receipts.append({"path_hash": short_hash(str(path)), "lane": lane, "errors": ["lane_required_or_invalid"]})
            continue
        lane_record = lane_evidence[lane]
        lane_record["receipt_count"] += 1
        blockers = validate_lane_receipt(receipt, lane)
        generated_at = parse_receipt_generated_at(receipt)
        if max_age_hours is not None:
            if generated_at is None:
                blockers.append("generated_at_missing_or_invalid_for_current_coverage")
            else:
                age_hours = (now - generated_at).total_seconds() / 3600
                if age_hours > max_age_hours:
                    blockers.append(f"receipt_stale>{max_age_hours:g}h")
                    stale_receipts.append(
                        {
                            "path_hash": short_hash(str(path)),
                            "lane": lane,
                            "age_hours": round(age_hours, 3),
                        }
                    )
        if blockers:
            invalid_receipts.append({"path_hash": short_hash(str(path)), "lane": lane, "errors": sorted(set(blockers))})
            lane_record["blockers"].extend(sorted(set(blockers)))
            continue
        lane_record["valid_receipt_count"] += 1
        if lane_accepts_receipt(profile, receipt):
            current_best = lane_record.get("accepted") is True
            prefer_live = receipt.get("live_mode") == "live-executed"
            current_live = lane_record.get("accepted_mode") == "live-executed"
            if not current_best or (prefer_live and not current_live):
                lane_record.update(
                    {
                        "accepted": True,
                        "accepted_mode": value_text(receipt.get("live_mode")),
                        "receipt_path_hash": short_hash(str(path)),
                        "live_executed": receipt.get("live_executed") is True,
                        "external_side_effects": value_text(receipt.get("external_side_effects")),
                        "template_distribution": value_text(receipt.get("template_distribution")),
                    }
                )

    missing_lanes = sorted(lane for lane, record in lane_evidence.items() if not record["accepted"])
    if not resolved.exists():
        warnings.append("receipt_dir_missing")
    return {
        "receipt_dir": receipt_dir_display,
        "receipt_files": len(receipt_files),
        "known_lanes": sorted(LANE_PROFILES),
        "accepted_lanes": sorted(lane for lane, record in lane_evidence.items() if record["accepted"]),
        "missing_lanes": missing_lanes,
        "lane_evidence": lane_evidence,
        "invalid_receipts": invalid_receipts,
        "stale_receipts": stale_receipts,
        "coverage_ok": not missing_lanes,
        "errors": errors,
        "warnings": warnings,
        "policy": {
            "default_safe_lanes_require_live_executed": True,
            "sensitive_lanes_allow_blocked_receipts_without_targets": True,
            "remote_publication_mutated_allowed": False,
            "max_age_hours": max_age_hours,
        },
        "counts": {
            "known_lanes": len(LANE_PROFILES),
            "accepted_lanes": len(LANE_PROFILES) - len(missing_lanes),
            "missing_lanes": len(missing_lanes),
            "invalid_receipts": len(invalid_receipts),
            "stale_receipts": len(stale_receipts),
        },
    }


def run_self_test() -> dict[str, Any]:
    errors: list[str] = []
    cases: list[dict[str, Any]] = []
    for lane in LANE_PROFILES:
        for mode in ("blocked", "live-executed"):
            receipt = fixture_for_lane(lane, live_mode=mode)
            blockers = validate_lane_receipt(receipt, lane)
            cases.append({"lane": lane, "case": mode, "ok": not blockers, "blockers": blockers})
            if blockers:
                errors.append(f"{lane}:{mode}:failed:{','.join(blockers)}")
        remote = fixture_for_lane(lane, live_mode="live-executed")
        remote["remote_publication_mutated"] = True
        if not validate_lane_receipt(remote, lane):
            errors.append(f"{lane}:negative_remote_mutation_passed")
        secret = fixture_for_lane(lane, live_mode="live-executed")
        secret["execution_receipt"]["api_token"] = "token=raw-secret-value"
        if not validate_lane_receipt(secret, lane):
            errors.append(f"{lane}:negative_secret_passed")
        missing_lease = fixture_for_lane(lane, live_mode="live-executed")
        missing_lease.pop("owner_lease", None)
        if not validate_lane_receipt(missing_lease, lane):
            errors.append(f"{lane}:negative_missing_owner_lease_passed")
    authority = fixture_for_lane("spec-kit-subordinate-adapter-governance", live_mode="live-executed")
    authority["authority_decision"]["priority_order"] = "Spec Kit > OpenSpec"
    if not validate_lane_receipt(authority, "spec-kit-subordinate-adapter-governance"):
        errors.append("negative_authority_order_passed")
    return {
        "ok": not errors,
        "cases": cases,
        "errors": errors,
        "counts": {"profiles": len(LANE_PROFILES), "cases": len(cases), "errors": len(errors)},
    }


def evaluate(
    root: Path,
    lane: str | None,
    receipt_path: Path | None,
    *,
    self_test: bool = True,
    receipt_dir: Path | None = None,
    require_coverage: bool = False,
    max_age_hours: float | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    self_test_result = run_self_test() if self_test else None
    if self_test_result is not None:
        errors.extend(f"self_test:{error}" for error in self_test_result["errors"])
    summary: dict[str, Any] = {}
    coverage: dict[str, Any] = {}
    if receipt_path is not None:
        selected_lane = normalize_lane(lane or "") if lane else None
        resolved = receipt_path if receipt_path.is_absolute() else root / receipt_path
        receipt, load_errors = read_json(resolved)
        blockers = list(load_errors)
        if receipt is not None:
            selected_lane = normalize_lane(selected_lane or receipt.get("lane"))
            blockers.extend(validate_lane_receipt(receipt, selected_lane))
        errors.extend(blockers)
        summary = receipt_summary(receipt, resolved, selected_lane, sorted(set(blockers)))
    if receipt_dir is not None or require_coverage:
        coverage = audit_receipt_dir(root, receipt_dir or DEFAULT_RECEIPT_DIR, max_age_hours=max_age_hours)
        if require_coverage and not coverage.get("coverage_ok"):
            errors.extend(f"coverage_missing_lane:{lane}" for lane in coverage.get("missing_lanes", []))
        if require_coverage:
            errors.extend(f"coverage_invalid_receipt:{item.get('path_hash')}" for item in coverage.get("invalid_receipts", []))
    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "lane": normalize_lane(lane or "") if lane else "",
        "known_lanes": sorted(LANE_PROFILES),
        "aliases": dict(sorted(ALIASES.items())),
        "canonical_env_keys": sorted(CANONICAL_ENV_KEYS),
        "receipt_summary": summary,
        "coverage_summary": coverage,
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
    parser = argparse.ArgumentParser(description="Validate R6 live-runtime receipts without performing actions.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--lane", default=None, help="Canonical R6 lane or legacy R5/plan alias.")
    parser.add_argument("--receipt", default=None)
    parser.add_argument("--receipt-dir", default=None, help="Audit a directory of R6 receipt JSON files.")
    parser.add_argument("--require-coverage", action="store_true", help="Fail unless every known R6 lane has accepted receipt evidence.")
    parser.add_argument("--max-age-hours", type=float, default=None, help="Optional freshness window for receipt coverage.")
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
        receipt_dir=Path(args.receipt_dir) if args.receipt_dir else None,
        require_coverage=args.require_coverage,
        max_age_hours=args.max_age_hours,
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
