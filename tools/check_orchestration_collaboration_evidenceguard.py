#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "orchestration_collaboration_evidenceguard"
REGISTRY_RULE_ID = "orchestration-collaboration-evidenceguard"
GUARD_STEP = "check_orchestration_collaboration_evidenceguard"
DEFAULT_FIXTURE_DIR = Path("test/fixtures/orchestration_prompt_independent_collaboration_parity")
EXPERT_LIFECYCLE_HANDLING_EVENTS = {"inspect", "redirect", "respawn", "durable_handoff", "main_session_takeover"}
EXPERT_LIFECYCLE_EVENT_NAMES = {
    "spawn",
    "wait",
    "progress_check",
    "timeout",
    "provider_pacing",
    "result",
    "absorbed",
    "close",
    *EXPERT_LIFECYCLE_HANDLING_EVENTS,
}
EXPERT_LIFECYCLE_REQUIRED_STRING_FIELDS: dict[str, tuple[str, ...]] = {
    "spawn": ("role", "task_summary"),
    "wait": ("agent_id",),
    "progress_check": ("agent_id", "status"),
    "timeout": ("agent_id", "classification"),
    "provider_pacing": ("classification", "handling"),
    "result": ("agent_id", "summary"),
    "absorbed": ("agent_id", "leader_decision"),
    "close": ("agent_id", "retention_policy"),
    "inspect": ("agent_id", "summary"),
    "redirect": ("agent_id", "summary"),
    "respawn": ("agent_id", "summary"),
    "durable_handoff": ("agent_id", "summary"),
    "main_session_takeover": ("agent_id", "summary"),
}
EXPERT_LIFECYCLE_REQUIRED_LIST_FIELDS: dict[str, tuple[str, ...]] = {
    "spawn": ("scope", "non_goals"),
    "result": ("changed_paths",),
}

REQUIRED_FIXTURES = {
    "cold_start_read_order_valid.json",
    "doc_update_without_collaboration_phrase.json",
    "doc_update_with_collaboration_phrase.json",
    "durable_persistent_complete_valid.json",
    "expert_lifecycle_audit_valid.json",
    "qualified_governance_update_without_collaboration_phrase.json",
    "qualified_governance_update_with_collaboration_phrase.json",
    "missing_reminder_excuse_invalid.json",
    "explicit_omx_without_threshold.json",
    "explicit_langgraph_single_slice.json",
    "langgraph_state_release_valid.json",
    "main_session_escalation_pending.json",
    "main_session_escalation_granted.json",
    "main_session_escalation_timed_out.json",
    "main_session_escalation_not_needed.json",
    "conversation_surface_localized_routing_trace_invalid.json",
    "conversation_surface_markdown_updated_plan_invalid.json",
    "conversation_surface_prose_only_updated_plan_invalid.json",
    "conversation_surface_routing_trace_no_key_values_invalid.json",
    "conversation_surface_routing_trace_duplicate_invalid.json",
    "conversation_surface_routing_trace_label_valid.json",
    "conversation_surface_routing_trace_old_fields_invalid.json",
    "conversation_surface_updated_plan_duplicate_invalid.json",
    "conversation_surface_updated_plan_native_plus_handwritten_invalid.json",
    "conversation_surface_updated_plan_checklist_valid.json",
    "conversation_surface_updated_plan_nested_invalid.json",
    "expert_lifecycle_timeout_pacing_valid.json",
    "multi_slice_without_collaboration_phrase.json",
    "multi_slice_with_collaboration_phrase.json",
}

REQUIRED_SURFACE_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "tools/check_orchestration_collaboration_evidenceguard.py",
        "Prompt-independent collaboration parity",
        "durable/persistent evidenceguard",
        "LangGraph state release",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md": [
        "tools/check_orchestration_collaboration_evidenceguard.py",
        "Prompt-independent collaboration parity",
        "durable/persistent evidenceguard",
        "LangGraph state release",
        "`Routing trace` is a plain text diagnostic",
        "exactly one `Routing trace` label",
        "legacy short fields",
        "already injected `Routing trace`",
        "native `update_plan` render is the canonical `Updated Plan` panel",
        "MUST NOT handwrite a second `Updated Plan` heading",
        "non-conflicting label such as `Execution progress`",
        "`Updated Plan` is the progress panel",
        "exactly one user-visible CLI/tree",
        "Markdown checkbox syntax remains implementation-plan-internal",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md": [
        "tools/check_orchestration_collaboration_evidenceguard.py",
        "Prompt-independent collaboration parity",
        "durable/persistent evidenceguard",
        "LangGraph state release",
        "`Routing trace` \u662f\u666e\u901a\u6587\u672c\u8bca\u65ad",
        "\u5fc5\u987b\u53ea\u6709\u4e00\u4e2a `Routing trace` \u6807\u7b7e",
        "\u65e7\u77ed\u5b57\u6bb5",
        "\u5df2\u7ecf\u4e3a\u5f53\u524d activation \u6ce8\u5165 `Routing trace`",
        "Codex \u539f\u751f `update_plan`",
        "\u4e0d\u5f97\u518d\u624b\u5199\u7b2c\u4e8c\u4e2a `Updated Plan`",
        "`\u6267\u884c\u8fdb\u5ea6` \u7b49\u4e0d\u51b2\u7a81\u6807\u7b7e",
        "`Updated Plan` \u662f\u8fdb\u5ea6\u9762\u677f",
        "\u552f\u4e00\u4e00\u4e2a\u7528\u6237\u53ef\u89c1\u7684 CLI/tree",
        "Markdown checkbox syntax",
    ],
    "docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.md": [
        "tools/check_orchestration_collaboration_evidenceguard.py",
        "prompt-independent collaboration parity",
        "durable/persistent evidenceguard",
        "LangGraph state release",
    ],
    "docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md": [
        "tools/check_orchestration_collaboration_evidenceguard.py",
        "prompt-independent collaboration parity",
        "durable/persistent evidenceguard",
        "LangGraph state release",
    ],
    "openspec/specs/codex-user-level-orchestration-activation-policy/spec.md": [
        "Prompt-independent collaboration parity SHALL be checker-backed",
        "Registered collaboration evidenceguard fixtures SHALL be checker-backed",
        "durable/persistent evidenceguard",
        "LangGraph state release",
        "`Routing trace` SHALL be a plain text diagnostic",
        "exactly one visible trace label",
        "legacy short fields",
        "already injected `Routing trace`",
        "native `update_plan` render SHALL be the canonical `Updated Plan` panel",
        "non-conflicting label such as `Execution progress`",
        "`Updated Plan` SHALL be a user-visible progress panel",
        "exactly one CLI/tree",
        "Markdown checkbox syntax SHALL remain implementation-plan-internal",
        "tools/check_orchestration_collaboration_evidenceguard.py",
    ],
    "openspec/specs/codex-user-level-orchestration-activation-policy/spec.zh-CN.md": [
        "prompt-independent collaboration parity",
        "Registered collaboration evidenceguard fixtures",
        "durable/persistent evidenceguard",
        "LangGraph state release",
        "双语 OpenSpec heading parity",
        "`Routing trace` \u5fc5\u987b\u662f\u666e\u901a\u6587\u672c\u8bca\u65ad",
        "\u5fc5\u987b\u53ea\u6709\u4e00\u4e2a\u53ef\u89c1 trace \u6807\u7b7e",
        "\u65e7\u77ed\u5b57\u6bb5",
        "\u5df2\u7ecf\u4e3a\u5f53\u524d activation \u6ce8\u5165 `Routing trace`",
        "\u539f\u751f `update_plan` render \u5fc5\u987b\u662f canonical `Updated Plan` \u9762\u677f",
        "`\u6267\u884c\u8fdb\u5ea6` \u7b49\u4e0d\u51b2\u7a81\u6807\u7b7e",
        "`Updated Plan` \u5fc5\u987b\u662f\u7528\u6237\u53ef\u89c1\u8fdb\u5ea6\u9762\u677f",
        "\u5fc5\u987b\u53ea\u6709\u4e00\u4e2a CLI/tree",
        "Markdown checkbox syntax",
        "tools/check_orchestration_collaboration_evidenceguard.py",
    ],
}

OPENSPEC_PRIMARY_SPEC = "openspec/specs/codex-user-level-orchestration-activation-policy/spec.md"
OPENSPEC_ZH_CN_SPEC = "openspec/specs/codex-user-level-orchestration-activation-policy/spec.zh-CN.md"
OPENSPEC_PARITY_HEADING_PREFIXES = ("### Requirement:", "#### Scenario:")

ROUTE_FIELDS = (
    "phase",
    "capability_chain",
    "backend_default",
    "backend_ready",
    "experts",
    "durable_workflow",
    "persistent_team",
    "main_session_escalation",
    "approval_timeout_risk",
    "approval_receipt",
    "why",
)
LANE_STATES = {"not_needed", "candidate", "selected", "running", "complete", "blocked"}
MAIN_SESSION_ESCALATION_STATES = {"not_needed", "preflight", "pending_approval", "granted", "timed_out", "blocked"}
APPROVAL_TIMEOUT_RISKS = {"none", "low", "medium", "high", "expired"}
NO_APPROVAL_RECEIPT_VALUES = {"", "none", "not_needed", "n/a", "na", "-"}
FORBIDDEN_MISSING_REMINDERS = (
    "the user did not request parallelism",
    "the user did not request experts",
    "the user did not request expert",
    "the user did not request subagents",
    "the user did not request omx",
    "the user did not request langgraph",
    "the user did not request durable_team",
    "the user did not request durable team",
    "the user did not request persistent team",
    "user did not request parallelism",
    "user did not request experts",
    "user did not request expert",
    "user did not request subagents",
    "user did not request omx",
    "user did not request langgraph",
    "user did not request durable_team",
    "user did not request durable team",
    "user did not request persistent team",
    "user did not ask for parallelism",
    "user did not ask for experts",
    "user did not ask for expert",
    "user did not ask for subagents",
    "user did not ask for omx",
    "user did not ask for langgraph",
    "user did not ask for durable_team",
    "user did not ask for durable team",
    "user did not ask for persistent team",
    "\u7528\u6237\u6ca1\u6709\u8981\u6c42\u5e76\u884c",
    "\u7528\u6237\u6ca1\u6709\u8981\u6c42\u4e13\u5bb6",
    "\u7528\u6237\u6ca1\u6709\u8981\u6c42\u5b50\u4ee3\u7406",
    "\u7528\u6237\u6ca1\u6709\u8981\u6c42omx",
    "\u7528\u6237\u6ca1\u6709\u8981\u6c42langgraph",
    "\u7528\u6237\u6ca1\u6709\u63d0\u5230\u5e76\u884c",
    "\u7528\u6237\u672a\u8981\u6c42\u5e76\u884c",
    "\u7528\u6237\u672a\u8981\u6c42\u4e13\u5bb6",
    "\u7528\u6237\u672a\u8981\u6c42\u5b50\u4ee3\u7406",
)
COLLABORATION_PHRASES = (
    "experts",
    "expert",
    "durable_team",
    "durable team",
    "persistent team",
    "subagents",
    "subagent",
    "parallel",
)

CONVERSATION_SURFACES = {"routing_trace", "updated_plan"}
ROUTING_TRACE_KEY_VALUE_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)=")
ROUTING_TRACE_REQUIRED_KEYS = set(ROUTE_FIELDS)
ROUTING_TRACE_FORBIDDEN_KEYS = {"experts_now", "durable_team"}
ROUTING_TRACE_FORBIDDEN_LABEL_PREFIXES = (
    "\u8def\u7531\u8ddf\u8e2a",
    "\u8def\u7531\u8ffd\u8e2a",
    "\u8def\u7531\u8f68\u8ff9",
)
UPDATED_PLAN_FORBIDDEN_LABEL_PREFIXES = ("\u66f4\u65b0\u8ba1\u5212", "\u8ba1\u5212\u66f4\u65b0")
UPDATED_PLAN_STATUS_MARKERS = (
    "\u25a1",
    "\u2714",
)
UPDATED_PLAN_MARKDOWN_CHECKBOX_RE = re.compile(r"(?im)^\s*[-*+]\s+\[[ xX]\]\s+")
LABEL_PREFIX_CHARS = r"\s*(?:[\u2022\u2514\u251c\u2502>+\-*]+\s*)*"



def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        return None


def load_json(path: Path, errors: list[str]) -> dict[str, Any] | None:
    text = read_text(path)
    if text is None:
        errors.append(f"Missing or unreadable JSON evidence file: {path}")
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        errors.append(f"Invalid JSON evidence file: {path}: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"JSON evidence file must contain an object: {path}")
        return None
    return payload


def load_expert_lifecycle_jsonl(path: Path, errors: list[str]) -> dict[str, Any] | None:
    text = read_text(path)
    if text is None:
        errors.append(f"Missing or unreadable JSONL evidence file: {path}")
        return None
    events: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid JSONL evidence line {line_number} in {path}: {exc}")
            continue
        if not isinstance(payload, dict):
            errors.append(f"JSONL evidence line {line_number} must contain an object: {path}")
            continue
        events.append(payload)
    if not events:
        errors.append(f"JSONL evidence file must contain at least one event object: {path}")
        return None
    total_wait = sum(
        int(event.get("wait_seconds"))
        for event in events
        if lower(event.get("event")) == "wait" and isinstance(event.get("wait_seconds"), int)
    )
    case: dict[str, Any] = {
        "schema_version": 1,
        "case_type": "expert_lifecycle_audit",
        "events": events,
    }
    if total_wait > 0:
        case["total_wait_bound_seconds"] = total_wait
    return case


def lower(value: Any) -> str:
    return str(value or "").strip().lower()


def validate_required_string_list_field(
    event: dict[str, Any],
    *,
    label: str,
    index: int,
    event_name: str,
    field: str,
    errors: list[str],
    require_non_empty: bool = False,
) -> None:
    value = event.get(field)
    if not isinstance(value, list):
        errors.append(f"{label}.events[{index}] {event_name} event missing list field: {field}.")
        return
    if require_non_empty and not value:
        errors.append(f"{label}.events[{index}] {event_name} event list field must be non-empty: {field}.")
        return
    if any(not isinstance(item, str) or not str(item).strip() for item in value):
        errors.append(
            f"{label}.events[{index}] {event_name} event list field must contain only non-empty strings: {field}."
        )


def contains_any(text: str, markers: tuple[str, ...]) -> bool:
    haystack = text.lower()
    return any(marker.lower() in haystack for marker in markers)


def extract_openspec_requirement_scenario_headings(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if any(line.startswith(prefix) for prefix in OPENSPEC_PARITY_HEADING_PREFIXES)
    ]


def validate_openspec_companion_heading_parity(root: Path, errors: list[str]) -> None:
    primary_text = read_text(root / OPENSPEC_PRIMARY_SPEC)
    companion_text = read_text(root / OPENSPEC_ZH_CN_SPEC)
    if primary_text is None or companion_text is None:
        return

    primary_headings = extract_openspec_requirement_scenario_headings(primary_text)
    companion_headings = extract_openspec_requirement_scenario_headings(companion_text)
    if len(companion_headings) < len(primary_headings):
        errors.append(
            f"{OPENSPEC_ZH_CN_SPEC} has {len(companion_headings)} Requirement/Scenario headings; "
            f"{OPENSPEC_PRIMARY_SPEC} has {len(primary_headings)}."
        )
    for heading in primary_headings:
        if heading not in companion_text:
            errors.append(f"{OPENSPEC_ZH_CN_SPEC} missing source heading for bilingual parity: {heading}")


def require_string(payload: dict[str, Any], key: str, errors: list[str], label: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} missing non-empty string field: {key}")
        return ""
    return value.strip()


def expected_route(case: dict[str, Any], errors: list[str], label: str) -> dict[str, str]:
    expected = case.get("expected")
    if not isinstance(expected, dict):
        errors.append(f"{label} missing object field: expected")
        return {}
    route: dict[str, str] = {}
    for field in ROUTE_FIELDS:
        route[field] = require_string(expected, field, errors, f"{label}.expected")
    for lane in ("durable_workflow", "persistent_team"):
        value = lower(route.get(lane))
        if value and value not in LANE_STATES:
            errors.append(f"{label}.expected.{lane} uses unsupported state `{route[lane]}`.")
    escalation_state = lower(route.get("main_session_escalation"))
    if escalation_state and escalation_state not in MAIN_SESSION_ESCALATION_STATES:
        errors.append(
            f"{label}.expected.main_session_escalation uses unsupported state `{route.get('main_session_escalation')}`."
        )
    timeout_risk = lower(route.get("approval_timeout_risk"))
    if timeout_risk and timeout_risk not in APPROVAL_TIMEOUT_RISKS:
        errors.append(f"{label}.expected.approval_timeout_risk uses unsupported risk `{route.get('approval_timeout_risk')}`.")
    receipt_missing = lower(route.get("approval_receipt")) in NO_APPROVAL_RECEIPT_VALUES
    if escalation_state == "not_needed":
        if timeout_risk != "none":
            errors.append(f"{label}.expected.main_session_escalation=not_needed requires approval_timeout_risk=none.")
        if not receipt_missing:
            errors.append(f"{label}.expected.main_session_escalation=not_needed requires approval_receipt=none.")
    elif escalation_state in {"pending_approval", "granted", "timed_out", "blocked"} and receipt_missing:
        errors.append(f"{label}.expected.main_session_escalation={escalation_state} requires visible approval_receipt.")
    if escalation_state == "pending_approval" and timeout_risk in {"none", "expired"}:
        errors.append(
            f"{label}.expected.main_session_escalation=pending_approval requires approval_timeout_risk=low, medium, or high."
        )
    if timeout_risk == "expired" and escalation_state not in {"timed_out", "blocked"}:
        errors.append(f"{label}.expected.approval_timeout_risk=expired requires timed_out or blocked escalation state.")
    why = lower(route.get("why"))
    if contains_any(why, FORBIDDEN_MISSING_REMINDERS):
        errors.append(f"{label}.expected.why cites missing user reminders as a routing reason.")
    for lane in ("durable_workflow", "persistent_team"):
        state = lower(route.get(lane))
        if state == "not_needed" and "threshold_not_met:" not in why:
            errors.append(f"{label}.expected.{lane}=not_needed must cite threshold_not_met:* in why.")
        if state == "blocked" and not ("blocked:" in why or "threshold_not_met:" in why):
            errors.append(f"{label}.expected.{lane}=blocked must cite blocked:* or threshold_not_met:* in why.")
        if state in {"selected", "running"} and "triggered_threshold:" not in why:
            errors.append(f"{label}.expected.{lane}={state} must cite triggered_threshold:* in why.")
    return route


def validate_activation_parity_case(case: dict[str, Any], errors: list[str], label: str) -> dict[str, str]:
    require_string(case, "case_id", errors, label)
    require_string(case, "parity_group", errors, label)
    prompt = require_string(case, "prompt", errors, label)
    phrase_present = case.get("collaboration_phrase_present")
    if not isinstance(phrase_present, bool):
        errors.append(f"{label} missing boolean field: collaboration_phrase_present")
    else:
        has_phrase = contains_any(prompt, COLLABORATION_PHRASES)
        if phrase_present and not has_phrase:
            errors.append(f"{label} says collaboration phrase is present, but prompt lacks known collaboration phrases.")
        if not phrase_present and has_phrase:
            errors.append(f"{label} says collaboration phrase is absent, but prompt contains collaboration language.")
    expected = expected_route(case, errors, label)
    input_shape = case.get("input")
    if not isinstance(input_shape, dict):
        errors.append(f"{label} missing object field: input")
    else:
        explicit_directive = lower(input_shape.get("explicit_directive"))
        frozen_plan = bool(input_shape.get("frozen_plan"))
        execution_slices = input_shape.get("execution_slices")
        if not isinstance(execution_slices, int):
            errors.append(f"{label}.input.execution_slices must be an integer.")
            execution_slices = 0
        why = lower(expected.get("why"))
        if explicit_directive in {"omx", "langgraph"} and (not frozen_plan or execution_slices < 2):
            if "threshold_not_met:" not in why and "blocked:" not in why:
                errors.append(f"{label} explicit {explicit_directive} directive without thresholds must report a named blocker or unmet threshold.")
        if frozen_plan and execution_slices >= 2:
            for lane in ("durable_workflow", "persistent_team"):
                if lower(expected.get(lane)) in {"not_needed", "candidate"}:
                    errors.append(f"{label} has frozen plan with 2+ slices, so {lane} must not remain {expected.get(lane)}.")
    return expected


def validate_cold_start_case(case: dict[str, Any], errors: list[str], label: str) -> None:
    read_order = case.get("read_order")
    if not isinstance(read_order, list) or not read_order:
        errors.append(f"{label} missing non-empty read_order list.")
        return
    for index, item in enumerate(read_order, start=1):
        if not isinstance(item, dict):
            errors.append(f"{label}.read_order[{index}] must be an object.")
            continue
        path = item.get("path")
        decision = item.get("decision")
        reason = item.get("reason")
        if not isinstance(path, str) or not path.strip():
            errors.append(f"{label}.read_order[{index}] missing path.")
        if decision not in {"read", "skipped"}:
            errors.append(f"{label}.read_order[{index}] decision must be read or skipped.")
        if not isinstance(reason, str) or not reason.strip():
            errors.append(f"{label}.read_order[{index}] missing reason.")
        if decision == "read" and item.get("read_mode") not in {"full_text_utf8", "summary_utf8", "targeted_utf8"}:
            errors.append(f"{label}.read_order[{index}] read entries must state an accepted read_mode.")


def evidence_bool(evidence: dict[str, Any], key: str) -> bool:
    return evidence.get(key) is True or (isinstance(evidence.get(key), str) and bool(str(evidence.get(key)).strip()))


def validate_durable_claim_case(case: dict[str, Any], errors: list[str], label: str) -> None:
    state = lower(case.get("state"))
    claim = lower(case.get("claim"))
    evidence = case.get("evidence")
    if state not in LANE_STATES:
        errors.append(f"{label}.state must be one of {sorted(LANE_STATES)}.")
    if not claim:
        errors.append(f"{label} missing claim.")
    if not isinstance(evidence, dict):
        errors.append(f"{label} missing object field: evidence")
        return
    if state in {"selected", "running", "complete"}:
        for key in ("active_selector", "backend_family", "preflight_passed", "ownership_plan"):
            if not evidence_bool(evidence, key):
                errors.append(f"{label} {state} durable/persistent claim missing evidence: {key}")
    if state in {"running", "complete"}:
        if not (evidence_bool(evidence, "team_manifest") or evidence_bool(evidence, "langgraph_thread_state")):
            errors.append(f"{label} running/complete claim needs team_manifest or langgraph_thread_state.")
        if not evidence_bool(evidence, "heartbeat"):
            errors.append(f"{label} running/complete claim missing heartbeat.")
    if state == "complete":
        for key in ("result_summary", "close_record", "leader_absorbed_record"):
            if not evidence_bool(evidence, key):
                errors.append(f"{label} complete claim missing evidence: {key}")
    if "running" in claim and state in {"not_needed", "candidate"}:
        errors.append(f"{label} cannot claim running while state is {state}.")


def validate_langgraph_release_case(case: dict[str, Any], errors: list[str], label: str) -> None:
    state = case.get("thread_state")
    if not isinstance(state, dict):
        errors.append(f"{label} missing object field: thread_state")
        return
    task_completed = case.get("task_completed") is True
    status = lower(state.get("status"))
    if task_completed and status == "running":
        errors.append(f"{label} completed LangGraph task must not remain status=running.")
    if task_completed:
        for key in ("completed_at", "final_phase", "result_summary", "released_by"):
            if not isinstance(state.get(key), str) or not str(state.get(key)).strip():
                errors.append(f"{label} completed LangGraph release missing field: {key}")
    if case.get("handoff") is True:
        for key in ("handoff_at", "handoff_target", "reason"):
            if not isinstance(state.get(key), str) or not str(state.get(key)).strip():
                errors.append(f"{label} LangGraph handoff missing field: {key}")


def validate_main_session_escalation_case(case: dict[str, Any], errors: list[str], label: str) -> None:
    state = lower(case.get("main_session_escalation"))
    if state not in MAIN_SESSION_ESCALATION_STATES:
        errors.append(f"{label}.main_session_escalation must be one of {sorted(MAIN_SESSION_ESCALATION_STATES)}.")

    pending = case.get("pending_approval")
    if not isinstance(pending, bool):
        errors.append(f"{label}.pending_approval must be a boolean.")

    risk = lower(case.get("approval_timeout_risk"))
    if risk not in APPROVAL_TIMEOUT_RISKS:
        errors.append(f"{label}.approval_timeout_risk must be one of {sorted(APPROVAL_TIMEOUT_RISKS)}.")

    receipt = lower(case.get("approval_receipt"))
    receipt_missing = receipt in NO_APPROVAL_RECEIPT_VALUES

    main_session_only = case.get("main_session_only")
    if state != "not_needed" and main_session_only is not True:
        errors.append(f"{label}.main_session_only must be true for escalation states that need approval.")

    if state == "not_needed":
        if pending is not False:
            errors.append(f"{label}.pending_approval must be false when main_session_escalation=not_needed.")
        if risk != "none":
            errors.append(f"{label}.approval_timeout_risk must be none when main_session_escalation=not_needed.")
        if not receipt_missing:
            errors.append(f"{label}.approval_receipt must be none when main_session_escalation=not_needed.")
        return

    if state in {"pending_approval", "granted", "timed_out", "blocked"} and receipt_missing:
        errors.append(f"{label}.approval_receipt must be visible for main_session_escalation={state}.")

    if state == "pending_approval":
        if pending is not True:
            errors.append(f"{label}.pending_approval must be true when main_session_escalation=pending_approval.")
        if risk in {"none", "expired"}:
            errors.append(f"{label}.approval_timeout_risk must be low, medium, or high while approval is pending.")
        liveness = case.get("liveness_summary")
        if not isinstance(liveness, str) or not liveness.strip():
            errors.append(f"{label}.liveness_summary must explain the visible main-session approval wait.")

    if state == "granted":
        if pending is not False:
            errors.append(f"{label}.pending_approval must be false after approval is granted.")
        if lower(case.get("granted_by")) != "main_session":
            errors.append(f"{label}.granted_by must be main_session for granted approval.")

    if state == "timed_out":
        if risk != "expired":
            errors.append(f"{label}.approval_timeout_risk must be expired when main_session_escalation=timed_out.")
        blocked_reason = lower(case.get("blocked_reason"))
        if not (blocked_reason.startswith("blocked:") or "approval_timeout" in blocked_reason):
            errors.append(f"{label}.blocked_reason must name blocked:approval_timeout or equivalent timeout blocker.")

    if state == "blocked":
        blocked_reason = lower(case.get("blocked_reason"))
        if not (blocked_reason.startswith("blocked:") or blocked_reason.startswith("threshold_not_met:")):
            errors.append(f"{label}.blocked_reason must use blocked:* or threshold_not_met:* when escalation is blocked.")


def validate_expert_lifecycle_case(case: dict[str, Any], errors: list[str], label: str) -> None:
    events = case.get("events")
    if not isinstance(events, list) or not events:
        errors.append(f"{label} missing non-empty events list.")
        return

    names: list[str] = []
    waits_by_agent: dict[str, int] = {}
    quiet_checks_by_agent: dict[str, int] = {}
    handling_by_agent: dict[str, set[str]] = {}
    result_agents: set[str] = set()
    absorbed_agents: set[str] = set()
    closed_agents: set[str] = set()
    timeout_agents: set[str] = set()

    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            errors.append(f"{label}.events[{index}] must be an object.")
            continue
        name = lower(event.get("event"))
        agent_id = str(event.get("agent_id") or "").strip()
        if not name:
            errors.append(f"{label}.events[{index}] missing event name.")
        elif name not in EXPERT_LIFECYCLE_EVENT_NAMES:
            allowed = ", ".join(sorted(EXPERT_LIFECYCLE_EVENT_NAMES))
            errors.append(
                f"{label}.events[{index}] has unsupported expert lifecycle event `{name}`; allowed: {allowed}."
            )
        for field in EXPERT_LIFECYCLE_REQUIRED_STRING_FIELDS.get(name, ()):
            if not isinstance(event.get(field), str) or not str(event.get(field)).strip():
                errors.append(f"{label}.events[{index}] {name} event missing non-empty string field: {field}.")
        for field in EXPERT_LIFECYCLE_REQUIRED_LIST_FIELDS.get(name, ()):
            validate_required_string_list_field(
                event,
                label=label,
                index=index,
                event_name=name,
                field=field,
                errors=errors,
                require_non_empty=name == "spawn",
            )
        names.append(name)

        if name == "wait" and agent_id:
            waits_by_agent[agent_id] = waits_by_agent.get(agent_id, 0) + 1
        if name == "progress_check" and agent_id:
            status = lower(event.get("status"))
            if status in {"quiet", "silent", "no_progress", "no-progress", "stalled"}:
                quiet_checks_by_agent[agent_id] = quiet_checks_by_agent.get(agent_id, 0) + 1
        if name in EXPERT_LIFECYCLE_HANDLING_EVENTS and agent_id:
            handling_by_agent.setdefault(agent_id, set()).add(name)
        if name == "result" and agent_id:
            result_agents.add(agent_id)
        if name == "absorbed" and agent_id:
            absorbed_agents.add(agent_id)
        if name == "close" and agent_id:
            closed_agents.add(agent_id)

        if name == "timeout":
            timeout_agents.add(agent_id)
            if lower(event.get("classification")) != "non-evidence":
                errors.append(f"{label}.events[{index}] timeout must be classified as non-evidence.")
            if event.get("used_as_evidence") is True:
                errors.append(f"{label}.events[{index}] timeout must not set used_as_evidence=true.")
            decision = lower(event.get("leader_decision"))
            if decision in {"accepted", "valid", "accepted_result", "used_as_evidence"}:
                errors.append(f"{label}.events[{index}] timeout must not be accepted as valid result evidence.")
            if not agent_id or waits_by_agent.get(agent_id, 0) == 0:
                errors.append(f"{label}.events[{index}] timeout requires prior wait event for the same agent.")
        if name == "provider_pacing":
            if lower(event.get("classification")) != "backpressure":
                errors.append(f"{label}.events[{index}] provider_pacing must be classified as backpressure.")
            handling_text = lower(event.get("handling"))
            has_disable = any(token in handling_text for token in ("disable", "avoid", "skip", "forbid", "not use"))
            has_surface = any(token in handling_text for token in ("orchestration", "langgraph", "omx", "subagent", "expert"))
            if has_disable and has_surface:
                errors.append(
                    f"{label}.events[{index}] provider_pacing handling must not disable orchestration, LangGraph, OMX, subagents, or experts."
                )

    for agent_id in sorted(result_agents):
        if agent_id not in absorbed_agents:
            errors.append(f"{label} result event for {agent_id} requires absorbed event for the same agent.")
    for agent_id in sorted(absorbed_agents):
        if agent_id not in closed_agents and not case.get("preserved_thread_reason"):
            errors.append(f"{label} absorbed expert {agent_id} requires close event for the same agent or preserved_thread_reason.")
    for agent_id in sorted(timeout_agents):
        if not handling_by_agent.get(agent_id):
            errors.append(
                f"{label} timeout for {agent_id} requires inspect, redirect, respawn, durable_handoff, or main_session_takeover event for the same agent."
            )
    for agent_id, count in sorted(quiet_checks_by_agent.items()):
        if count >= 2 and not handling_by_agent.get(agent_id):
            errors.append(
                f"{label} two quiet progress checks for {agent_id} require inspect, redirect, respawn, durable_handoff, or main_session_takeover."
            )
    if "wait" in names:
        waits = [event for event in events if isinstance(event, dict) and lower(event.get("event")) == "wait"]
        if any(not isinstance(event.get("wait_seconds"), int) or event.get("wait_seconds") <= 0 for event in waits):
            errors.append(f"{label} wait events must include positive integer wait_seconds.")
        if not isinstance(case.get("total_wait_bound_seconds"), int) or int(case.get("total_wait_bound_seconds")) <= 0:
            errors.append(f"{label} wait evidence requires total_wait_bound_seconds.")


def first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def strip_label_prefix(line: str) -> str:
    return re.sub(rf"^{LABEL_PREFIX_CHARS}", "", line.strip())


def starts_with_label(line: str, label: str) -> bool:
    return strip_label_prefix(line).startswith(label)


def label_line_count(text: str, label: str) -> int:
    pattern = re.compile(rf"(?im)^{LABEL_PREFIX_CHARS}{re.escape(label)}\b")
    return len(pattern.findall(text))


def conversation_surface_issues(surface: str, text: str) -> list[str]:
    issues: list[str] = []
    first_line = first_nonempty_line(text)
    if surface == "routing_trace":
        if not starts_with_label(first_line, "Routing trace"):
            issues.append("routing trace surface must start with the literal `Routing trace` label.")
        if label_line_count(text, "Routing trace") > 1:
            issues.append("routing trace surface must contain exactly one `Routing trace` label, not duplicate trace panels.")
        if any(strip_label_prefix(first_line).startswith(prefix) for prefix in ROUTING_TRACE_FORBIDDEN_LABEL_PREFIXES):
            issues.append("routing trace surface must not replace `Routing trace` with a localized label.")
        route_keys = {match.group(1) for match in ROUTING_TRACE_KEY_VALUE_RE.finditer(text)}
        if not route_keys:
            issues.append("routing trace surface must remain a plain text diagnostic with key=value fields.")
        for forbidden_key in sorted(ROUTING_TRACE_FORBIDDEN_KEYS & route_keys):
            issues.append(
                f"routing trace surface must not use legacy short field `{forbidden_key}=...`; use the full current field set."
            )
        for required_key in sorted(ROUTING_TRACE_REQUIRED_KEYS - route_keys):
            issues.append(f"routing trace surface must include `{required_key}=...` key=value evidence.")
        return issues
    if surface == "updated_plan":
        if not starts_with_label(first_line, "Updated Plan"):
            issues.append("updated plan surface must start with the literal `Updated Plan` label.")
        if label_line_count(text, "Updated Plan") > 1:
            issues.append("updated plan surface must contain exactly one `Updated Plan` label, not duplicate, nested, or native-plus-handwritten panels.")
        if any(strip_label_prefix(first_line).startswith(prefix) for prefix in UPDATED_PLAN_FORBIDDEN_LABEL_PREFIXES):
            issues.append("updated plan surface must not replace `Updated Plan` with a localized label.")
        if UPDATED_PLAN_MARKDOWN_CHECKBOX_RE.search(text):
            issues.append(
                "updated plan surface must use the CLI/tree checkmark/open-square panel style, not Markdown checkbox list syntax."
            )
        if not any(marker in text for marker in UPDATED_PLAN_STATUS_MARKERS):
            issues.append(
                "updated plan surface must preserve CLI/tree checkmark/open-square status-list semantics, not prose-only text."
            )
        return issues
    issues.append(f"unsupported conversation surface `{surface}`.")
    return issues


def validate_conversation_surface_case(case: dict[str, Any], errors: list[str], label: str) -> None:
    require_string(case, "case_id", errors, label)
    surface = lower(case.get("surface"))
    if surface not in CONVERSATION_SURFACES:
        errors.append(f"{label}.surface must be one of {sorted(CONVERSATION_SURFACES)}.")
        return
    text = require_string(case, "text", errors, label)
    expected_valid = case.get("expected_valid")
    if not isinstance(expected_valid, bool):
        errors.append(f"{label}.expected_valid must be a boolean.")
        return
    issues = conversation_surface_issues(surface, text)
    if expected_valid and issues:
        for issue in issues:
            errors.append(f"{label}: {issue}")
    if not expected_valid and not issues:
        errors.append(f"{label} is expected to be invalid but passed conversation surface validation.")


CASE_VALIDATORS = {
    "activation_parity": validate_activation_parity_case,
    "cold_start_read_order": validate_cold_start_case,
    "durable_persistent_claim": validate_durable_claim_case,
    "langgraph_state_release": validate_langgraph_release_case,
    "main_session_escalation_visibility": validate_main_session_escalation_case,
    "expert_lifecycle_audit": validate_expert_lifecycle_case,
    "conversation_surface": validate_conversation_surface_case,
}


def validate_case(case: dict[str, Any], errors: list[str], label: str) -> dict[str, str] | None:
    case_type = lower(case.get("case_type"))
    if case_type not in CASE_VALIDATORS:
        errors.append(f"{label} has unsupported case_type `{case.get('case_type')}`.")
        return None
    validator = CASE_VALIDATORS[case_type]
    result = validator(case, errors, label)
    return result if isinstance(result, dict) else None


def run_fixture_check(root: Path, fixture_dir: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    directory = (root / (fixture_dir or DEFAULT_FIXTURE_DIR)).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checked_cases: list[str] = []
    parity_routes: dict[str, list[tuple[bool, dict[str, str], str]]] = {}

    if not directory.exists():
        errors.append(f"Missing orchestration collaboration fixture directory: {directory}")
        files: list[Path] = []
    else:
        files = sorted(directory.glob("*.json"))
        present = {path.name for path in files}
        for required in sorted(REQUIRED_FIXTURES - present):
            errors.append(f"Missing required prompt-independent parity fixture: {required}")

    for path in files:
        payload = load_json(path, errors)
        if payload is None:
            continue
        checked_cases.append(path.name)
        case_errors: list[str] = []
        route = validate_case(payload, case_errors, path.name)
        if payload.get("expected_failure") is True:
            if not case_errors:
                errors.append(f"{path.name} is marked expected_failure but passed validation.")
            continue
        errors.extend(case_errors)
        if route is not None and not case_errors and lower(payload.get("case_type")) == "activation_parity":
            group = str(payload.get("parity_group")).strip()
            if not group.startswith("explicit_"):
                parity_routes.setdefault(group, []).append((bool(payload.get("collaboration_phrase_present")), route, path.name))

    for group, entries in sorted(parity_routes.items()):
        if len(entries) < 2:
            errors.append(f"Parity group `{group}` must include with-phrase and without-phrase fixtures.")
            continue
        flags = {flag for flag, _, _ in entries}
        if flags != {False, True}:
            errors.append(f"Parity group `{group}` must include both collaboration_phrase_present true and false cases.")
        baseline = {
            key: value
            for key, value in entries[0][1].items()
            if key in {
                "phase",
                "backend_default",
                "backend_ready",
                "experts",
                "durable_workflow",
                "persistent_team",
                "main_session_escalation",
                "approval_timeout_risk",
                "approval_receipt",
                "why",
            }
        }
        for _, route, name in entries[1:]:
            current = {key: value for key, value in route.items() if key in baseline}
            if current != baseline:
                errors.append(f"Parity group `{group}` route mismatch between fixtures; {name} differs from baseline.")

    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "check_name": CHECK_NAME,
        "mode": "fixtures",
        "ok": not errors,
        "root": str(root),
        "fixture_dir": str(directory),
        "checked_cases": checked_cases,
        "errors": errors,
        "warnings": warnings,
        "counts": {"checked_cases": len(checked_cases), "errors": len(errors), "warnings": len(warnings)},
    }


def run_repository_check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    fixture_payload = run_fixture_check(root)
    errors = list(fixture_payload["errors"])
    warnings = list(fixture_payload["warnings"])
    checked_surfaces: list[str] = []

    for rel, snippets in REQUIRED_SURFACE_SNIPPETS.items():
        text = read_text(root / rel)
        if text is None:
            errors.append(f"Missing required orchestration collaboration evidenceguard surface: {rel}")
            continue
        checked_surfaces.append(rel)
        for snippet in snippets:
            if snippet not in text:
                errors.append(f"{rel} missing required snippet: {snippet}")

    validate_openspec_companion_heading_parity(root, errors)

    guard_text = read_text(root / "tools/run_openspec_guard.py") or ""
    if GUARD_STEP not in guard_text:
        errors.append(f"tools/run_openspec_guard.py must run {GUARD_STEP}.")

    registry = load_json(root / "tools/safety_rule_script_backing_registry.json", errors)
    if registry is not None:
        rules = registry.get("rules")
        if not isinstance(rules, list):
            errors.append("Safety rule registry `rules` must be a list.")
        else:
            matches = [rule for rule in rules if isinstance(rule, dict) and rule.get("id") == REGISTRY_RULE_ID]
            if not matches:
                errors.append(f"Safety rule registry missing rule id: {REGISTRY_RULE_ID}")
            else:
                rule = matches[0]
                expected_entries = {
                    "prompt_reminders": "docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.md",
                    "script_controls": "tools/check_orchestration_collaboration_evidenceguard.py",
                    "guard_steps": GUARD_STEP,
                }
                for field, expected in expected_entries.items():
                    values = rule.get(field)
                    if not isinstance(values, list) or expected not in values:
                        errors.append(f"Safety rule {REGISTRY_RULE_ID} missing {field} entry: {expected}")

    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "check_name": CHECK_NAME,
        "mode": "repository",
        "ok": not errors,
        "root": str(root),
        "checked_surfaces": checked_surfaces,
        "fixture_counts": fixture_payload["counts"],
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "checked_surfaces": len(checked_surfaces),
            "checked_cases": fixture_payload["counts"]["checked_cases"],
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def run_evidence_check(path: Path) -> dict[str, Any]:
    errors: list[str] = []
    evidence_format = "jsonl" if path.suffix.lower() == ".jsonl" else "json"
    payload = load_expert_lifecycle_jsonl(path, errors) if evidence_format == "jsonl" else load_json(path, errors)
    checked = False
    if payload is not None:
        checked = True
        validate_case(payload, errors, path.name)
    return {
        "schema_version": 1,
        "generated_at": utc_now(),
        "check_name": CHECK_NAME,
        "mode": "evidence",
        "ok": not errors,
        "evidence_path": str(path),
        "evidence_format": evidence_format,
        "checked": checked,
        "errors": errors,
        "warnings": [],
        "counts": {"checked": 1 if checked else 0, "errors": len(errors), "warnings": 0},
    }


def emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    for item in payload.get("warnings", []):
        print(f"WARNING: {item}")
    for item in payload.get("errors", []):
        print(f"ERROR: {item}")
    if payload["ok"]:
        if payload.get("mode") == "repository":
            print("Orchestration collaboration evidenceguard repository checks passed.")
        elif payload.get("mode") == "fixtures":
            print("Orchestration collaboration evidenceguard fixtures passed.")
        else:
            print("Orchestration collaboration evidenceguard evidence passed.")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate prompt-independent collaboration parity, durable evidenceguard, expert lifecycle, cold-start evidence, and LangGraph release evidence."
    )
    parser.add_argument("--root", default=".", help="Repository root for repository and fixture checks.")
    parser.add_argument("--fixture-dir", default=None, help="Fixture directory relative to root.")
    parser.add_argument(
        "--evidence",
        default=None,
        help="Validate one JSON evidence case or JSONL expert lifecycle audit instead of repository surfaces.",
    )
    parser.add_argument("--fixtures-only", action="store_true", help="Validate fixtures without repository surface checks.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    if args.evidence:
        payload = run_evidence_check(Path(args.evidence))
    elif args.fixtures_only:
        payload = run_fixture_check(Path(args.root), Path(args.fixture_dir) if args.fixture_dir else None)
    else:
        payload = run_repository_check(Path(args.root))
    emit(payload, args.json)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
