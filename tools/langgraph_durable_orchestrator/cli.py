"""CLI skeleton for LangGraph durable orchestration."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any, Literal, TypedDict

from contracts import (
    APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
    APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
    APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
    APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
    APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
    APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
    APPROVAL_QUEUE_ITEM_FIELDS,
    APPROVAL_QUEUE_ITEM_STATUSES,
    APPROVAL_QUEUE_POSTURES,
    APPROVAL_QUEUE_PROJECTION_FIELDS,
    AUTOMATIC_RUNTIME_POLICY_ACTIONS,
    AUTOMATIC_RUNTIME_POLICY_APPROVAL_POSTURES,
    AUTOMATIC_RUNTIME_POLICY_IDENTITY,
    AUTOMATIC_RUNTIME_POLICY_IDENTITY_FIELDS,
    AUTOMATIC_RUNTIME_POLICY_MIGRATION_POSTURES,
    AUTOMATIC_RUNTIME_POLICY_RECOVERY_POSTURES,
    AUTOMATIC_RUNTIME_POLICY_PROJECTION_FIELDS,
    BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_IDENTITY,
    BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
    BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_POSTURES,
    BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
    BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
    BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
    COMPILED_INVOCATION_IDENTITY,
    COMPILED_INVOCATION_IDENTITY_FIELDS,
    COMPILED_INVOCATION_POSTURES,
    COMPILED_INVOCATION_PROJECTION_FIELDS,
    COMPILED_INVOCATION_RUN_KINDS,
    COMMAND_GRAPH_SCOPES,
    CURRENT_GRAPH_CONTRACT,
    DEEPER_LIVE_PRIMARY_ENGINE_IDENTITY,
    DEEPER_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
    DEEPER_LIVE_PRIMARY_ENGINE_POSTURES,
    DEEPER_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
    DEEPER_LIVE_PRIMARY_ENGINE_RUN_KINDS,
    DEEPER_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
    COMMAND_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
    COMMAND_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
    COMMAND_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
    COMMAND_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
    COMMAND_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
    COMMAND_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
    MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
    MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
    MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
    MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
    MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
    MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
    MEMORY_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
    MEMORY_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
    MEMORY_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
    MEMORY_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
    MEMORY_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
    MEMORY_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
    RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
    RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
    RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
    RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
    RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
    RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
    DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
    DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
    DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
    DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
    DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
    DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
    REDUCER_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
    REDUCER_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
    REDUCER_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
    REDUCER_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
    REDUCER_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
    REDUCER_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
    FULLER_LIVE_PRIMARY_ENGINE_IDENTITY,
    FULLER_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
    FULLER_LIVE_PRIMARY_ENGINE_POSTURES,
    FULLER_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
    FULLER_LIVE_PRIMARY_ENGINE_RUN_KINDS,
    FULLER_LIVE_PRIMARY_ENGINE_TRANSITION_KINDS,
    GENERALIZED_LIVE_ROUTING_IDENTITY,
    GENERALIZED_LIVE_ROUTING_IDENTITY_FIELDS,
    GENERALIZED_LIVE_ROUTING_POSTURES,
    GENERALIZED_LIVE_ROUTING_PROJECTION_FIELDS,
    GENERALIZED_LIVE_ROUTING_ROUTE_KINDS,
    HANDOFF_STATE_LIVE_PRIMARY_ENGINE_IDENTITY,
    HANDOFF_STATE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
    HANDOFF_STATE_LIVE_PRIMARY_ENGINE_POSTURES,
    HANDOFF_STATE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
    HANDOFF_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
    HANDOFF_STATE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
    LIVE_EXECUTION_IDENTITY,
    LIVE_EXECUTION_IDENTITY_FIELDS,
    LIVE_EXECUTION_POSTURES,
    LIVE_EXECUTION_PROJECTION_FIELDS,
    LIVE_EXECUTION_RUN_KINDS,
    MEMORY_PROJECTION_FIELDS,
    MEMORY_STORE_FIELDS,
    COMMAND_PROJECTION_FIELDS,
    COMMAND_RESUME_POSTURES,
    COMMAND_STATE_FIELDS,
    COMMAND_TRANSITION_KINDS,
    GRAPH_KERNEL_EDGE_FIELDS,
    GRAPH_KERNEL_EDGES,
    GRAPH_KERNEL_IDENTITY,
    GRAPH_KERNEL_IDENTITY_FIELDS,
    GRAPH_KERNEL_NODE_FIELDS,
    GRAPH_KERNEL_NODES,
    GRAPH_KERNEL_NODE_POSTURES,
    GRAPH_KERNEL_PHASE_TO_NODE,
    GRAPH_KERNEL_PROJECTION_FIELDS,
    GRAPH_KERNEL_TRANSITION_KINDS,
    PRIMARY_RUNTIME_ENGINE_IDENTITY,
    PRIMARY_RUNTIME_ENGINE_IDENTITY_FIELDS,
    PRIMARY_RUNTIME_ENGINE_POSTURES,
    PRIMARY_RUNTIME_ENGINE_PROJECTION_FIELDS,
    PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_IDENTITY,
    PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
    PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_POSTURES,
    PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
    PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
    PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
    GRAPH_CONTRACT_FIELDS,
    GATE_VERDICTS,
    HISTORY_COMPATIBILITY_STATES,
    HISTORY_PROJECTION_FIELDS,
    IMPLEMENTATION_BRIEF_FIELDS,
    INTERRUPT_POINTS,
    LEADER_OWNED_SUMMARY_FIELDS,
    LOOP_CAPABLE_FLOWS,
    LOOP_PROJECTION_FIELDS,
    MIGRATION_PROJECTION_FIELDS,
    MIGRATION_REASON_CODES,
    PHASE_TO_SUBGRAPH,
    RECOVERABLE_INTERRUPT_FIELDS,
    RECOVERABLE_THREAD_FIELDS,
    RECOVERY_MUTATION_INTENTS,
    RECOVERY_POSTURES,
    RECOVERY_PROJECTION_FIELDS,
    REDUCER_COMPATIBILITY_STATES,
    REDUCER_MERGE_CHANNELS,
    REDUCER_PROJECTION_FIELDS,
    RUNTIME_CONTEXT_FIELDS,
    RUNTIME_INJECTION_PROJECTION_FIELDS,
    ROOT_PHASES,
    SEMANTIC_MEMORY_FIELDS,
    SINGLE_WRITER_FIELDS,
    STATE_SCHEMA_COMPATIBILITY_POSTURES,
    STATEFUL_LIVE_PRIMARY_ENGINE_IDENTITY,
    STATEFUL_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
    STATEFUL_LIVE_PRIMARY_ENGINE_POSTURES,
    STATEFUL_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
    STATEFUL_LIVE_PRIMARY_ENGINE_RUN_KINDS,
    STATEFUL_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
    STORE_INJECTION_FIELDS,
    SUPERSTEP_LIVE_PRIMARY_ENGINE_IDENTITY,
    SUPERSTEP_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
    SUPERSTEP_LIVE_PRIMARY_ENGINE_POSTURES,
    SUPERSTEP_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
    SUPERSTEP_LIVE_PRIMARY_ENGINE_RUN_KINDS,
    SUPERSTEP_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
    SUBGRAPH_LIBRARY_FIELDS,
    SUBGRAPH_CHECKPOINTER_MODES,
    SUBGRAPH_PERSISTENCE_MODES,
    SUBGRAPH_PROJECTION_FIELDS,
    SUBGRAPH_STATE_INSPECTION_FIELDS,
    SUBGRAPH_STATE_INSPECTION_PROJECTION_FIELDS,
    SUBGRAPH_STATE_INSPECTION_SCOPES,
    STREAM_EVENT_FIELDS,
    STREAM_OBSERVABILITY_MODES,
    STREAM_PROJECTION_FIELDS,
    SUBGRAPHS,
    SURVIVOR_QUEUE_FIELDS,
    SURVIVOR_QUEUE_METADATA_FIELDS,
    THREAD_COMPATIBILITY_VERDICTS,
    TOPOLOGY_COMPATIBILITY_POSTURES,
)
from runtime import (
    active_selector_path,
    backend_record_path,
    checkpoint_record_path,
    detect_worktree_id,
    delete_interrupt,
    ensure_layout,
    history_record_path,
    implementation_brief_path,
    interrupt_record_path,
    load_backend_record,
    read_checkpoint,
    read_history,
    read_implementation_brief,
    read_interrupt,
    read_release_receipt,
    read_survivor_queue,
    read_thread_record,
    save_active_selector,
    resolve_repo_root,
    save_backend_record,
    stable_thread_id,
    release_receipt_path,
    survivor_queue_path,
    write_release_receipt,
    write_selector_lease,
    thread_record_path,
    write_checkpoint,
    write_history,
    write_implementation_brief,
    write_interrupt,
    write_survivor_queue,
    write_thread_record,
)

try:
    import langgraph  # type: ignore  # noqa: F401

    LANGGRAPH_AVAILABLE = True
except Exception:
    LANGGRAPH_AVAILABLE = False


def _emit(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=True))


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _loop_projection(thread: dict[str, Any]) -> dict[str, Any]:
    return {
        "active_loop": thread.get("active_loop", ""),
        "loop_stage": thread.get("loop_stage", ""),
        "iteration_count": int(thread.get("iteration_count", 0) or 0),
        "iteration_budget": int(thread.get("iteration_budget", 0) or 0),
        "last_gate_verdict": thread.get("last_gate_verdict", ""),
        "last_gate_reason": thread.get("last_gate_reason", ""),
        "stop_reason": thread.get("stop_reason", ""),
    }


def _default_reducer_state() -> dict[str, Any]:
    return {
        "compatibility": "reducer_aware",
        "fanout_state": "idle",
        "channels": {},
        "invalid_multi_writer_updates": [],
        "source_records": [],
    }


def _ensure_reducer_state(thread: dict[str, Any]) -> dict[str, Any]:
    state = thread.get("reducer_state")
    if isinstance(state, dict):
        state.setdefault("compatibility", "reducer_aware")
        state.setdefault("fanout_state", "idle")
        state.setdefault("channels", {})
        state.setdefault("invalid_multi_writer_updates", [])
        state.setdefault("source_records", [])
        thread["reducer_state"] = state
        return state
    state = _default_reducer_state()
    thread["reducer_state"] = state
    return state


def _reducer_projection(thread: dict[str, Any]) -> dict[str, Any]:
    state = thread.get("reducer_state")
    if not isinstance(state, dict):
        return {
            "compatibility": "pre_reducer",
            "reducer_channels_present": [],
            "fanout_state": "unknown",
            "invalid_multi_writer_detected": False,
            "invalid_multi_writer_updates": [],
            "merge_channels_updated": [],
            "channel_item_counts": {},
            "source_records": [],
        }

    channels = state.get("channels", {})
    channel_item_counts = {
        channel_name: int(channel_state.get("item_count", 0) or 0)
        for channel_name, channel_state in channels.items()
    }
    merge_channels_updated = sorted([name for name, count in channel_item_counts.items() if count > 0])
    return {
        "compatibility": state.get("compatibility", "reducer_aware"),
        "reducer_channels_present": sorted(channels.keys()),
        "fanout_state": state.get("fanout_state", "idle"),
        "invalid_multi_writer_detected": bool(state.get("invalid_multi_writer_updates")),
        "invalid_multi_writer_updates": state.get("invalid_multi_writer_updates", []),
        "merge_channels_updated": merge_channels_updated,
        "channel_item_counts": channel_item_counts,
        "source_records": sorted(state.get("source_records", [])),
    }


def _clone_payload(payload: Any) -> Any:
    return json.loads(json.dumps(payload, ensure_ascii=True))


def _checkpoint_id(thread_id: str) -> str:
    return f"checkpoint-{thread_id.replace(':', '-')}-{uuid.uuid4().hex[:8]}"


def _default_history_bundle(thread_id: str) -> dict[str, Any]:
    return {
        "thread_id": thread_id,
        "history_version": 1,
        "compatibility": "tracked_history",
        "next_ordinal": 1,
        "records": [],
        "updated_at": "",
    }


def _recovery_projection(thread: dict[str, Any]) -> dict[str, Any]:
    state = thread.get("recovery_state")
    if not isinstance(state, dict):
        return {
            "posture": "ordinary",
            "last_action": "",
            "target_id": "",
            "recovered_at": "",
            "source_records": [],
            "recoverable_fields_touched": [],
        }
    return {
        "posture": state.get("posture", "ordinary"),
        "last_action": state.get("last_action", ""),
        "target_id": state.get("target_id", ""),
        "recovered_at": state.get("recovered_at", ""),
        "source_records": state.get("source_records", []),
        "recoverable_fields_touched": state.get("recoverable_fields_touched", []),
    }


def _payload_keys(payload: Any) -> list[str]:
    if isinstance(payload, dict):
        return sorted([str(key) for key in payload.keys()])
    if payload in (None, "", [], {}):
        return []
    return ["$scalar"]


def _parse_json_option(raw_value: str) -> Any:
    return json.loads(raw_value.lstrip("\ufeff"))


def _load_json_option(raw_json: str | None, raw_file: Any) -> Any:
    if raw_file:
        path = raw_file if hasattr(raw_file, "read_text") else Path(str(raw_file))
        return json.loads(path.read_text(encoding="utf-8").lstrip("\ufeff"))
    if raw_json:
        return _parse_json_option(raw_json)
    return None


def _current_graph_contract(
    *,
    graph_contract_id: str = "",
    topology_version: str = "",
    state_schema_version: str = "",
) -> dict[str, str]:
    return {
        "graph_contract_id": graph_contract_id or CURRENT_GRAPH_CONTRACT["graph_contract_id"],
        "topology_version": topology_version or CURRENT_GRAPH_CONTRACT["topology_version"],
        "state_schema_version": state_schema_version or CURRENT_GRAPH_CONTRACT["state_schema_version"],
    }


def _thread_graph_contract(thread: dict[str, Any]) -> dict[str, str]:
    contract = thread.get("graph_contract")
    if not isinstance(contract, dict):
        migration_state = thread.get("migration_state")
        if isinstance(migration_state, dict):
            contract = migration_state.get("thread_graph_contract")
    if not isinstance(contract, dict):
        return {}
    return {
        "graph_contract_id": str(contract.get("graph_contract_id", "")),
        "topology_version": str(contract.get("topology_version", "")),
        "state_schema_version": str(contract.get("state_schema_version", "")),
    }


def _ensure_graph_contract(
    thread: dict[str, Any],
    *,
    graph_contract_id: str = "",
    topology_version: str = "",
    state_schema_version: str = "",
) -> dict[str, str]:
    existing = _thread_graph_contract(thread)
    if existing:
        thread["graph_contract"] = existing
        return existing
    contract = _current_graph_contract(
        graph_contract_id=graph_contract_id,
        topology_version=topology_version,
        state_schema_version=state_schema_version,
    )
    thread["graph_contract"] = contract
    return contract


def _version_segments(raw_value: str) -> tuple[int, ...] | None:
    matches = re.findall(r"\d+", str(raw_value))
    if not matches:
        return None
    return tuple(int(match) for match in matches)


def _classify_version_drift(
    current_version: str,
    thread_version: str,
    *,
    missing_reason: str,
    minor_reason: str,
    major_reason: str,
) -> tuple[str, list[str]]:
    if not thread_version:
        return "degraded_compatible", [missing_reason]
    if current_version == thread_version:
        return "migration_safe", []

    current_segments = _version_segments(current_version)
    thread_segments = _version_segments(thread_version)
    if current_segments and thread_segments and current_segments[0] != thread_segments[0]:
        return "incompatible", [major_reason]
    return "degraded_compatible", [minor_reason]


def _migration_state_payload(
    thread: dict[str, Any],
    *,
    current_contract: dict[str, str] | None = None,
) -> dict[str, Any]:
    normalized_current = _current_graph_contract(**(current_contract or {}))
    thread_contract = _thread_graph_contract(thread)

    topology_compatibility, topology_reasons = _classify_version_drift(
        normalized_current["topology_version"],
        thread_contract.get("topology_version", ""),
        missing_reason="topology_version_missing",
        minor_reason="topology_minor_drift",
        major_reason="topology_major_drift",
    )
    state_schema_compatibility, state_schema_reasons = _classify_version_drift(
        normalized_current["state_schema_version"],
        thread_contract.get("state_schema_version", ""),
        missing_reason="state_schema_version_missing",
        minor_reason="state_schema_minor_drift",
        major_reason="state_schema_major_drift",
    )

    reason_codes = topology_reasons + state_schema_reasons
    if (
        thread_contract.get("graph_contract_id")
        and normalized_current["graph_contract_id"] != thread_contract.get("graph_contract_id")
        and "graph_contract_id_mismatch" not in reason_codes
    ):
        reason_codes.append("graph_contract_id_mismatch")

    compatibility = "migration_safe"
    if topology_compatibility == "incompatible" or state_schema_compatibility == "incompatible":
        compatibility = "incompatible"
    elif (
        topology_compatibility == "degraded_compatible"
        or state_schema_compatibility == "degraded_compatible"
        or "graph_contract_id_mismatch" in reason_codes
    ):
        compatibility = "degraded_compatible"

    return {
        "current_graph_contract": normalized_current,
        "thread_graph_contract": thread_contract,
        "topology_compatibility": topology_compatibility,
        "state_schema_compatibility": state_schema_compatibility,
        "compatibility": compatibility,
        "reason_codes": sorted(dict.fromkeys(reason_codes)),
    }


def _persist_migration_state(
    thread: dict[str, Any],
    *,
    current_contract: dict[str, str] | None = None,
) -> dict[str, Any]:
    state = _migration_state_payload(thread, current_contract=current_contract)
    thread["migration_state"] = state
    return state


def _migration_projection(
    thread: dict[str, Any],
    thread_id: str = "",
    *,
    current_contract: dict[str, str] | None = None,
) -> dict[str, Any]:
    state = _migration_state_payload(thread, current_contract=current_contract)
    helper_pointer: dict[str, Any] = {
        "command": "migration",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id
    return {**state, "helper_pointer": helper_pointer}


def _default_approval_queue_state() -> dict[str, Any]:
    return {
        "queue_posture": "no_interrupts",
        "current_interrupt_id": "",
        "queue_items": [],
        "resume_map": {},
        "updated_at": "",
    }


def _load_interrupt_items(raw_values: list[str] | None, raw_files: list[Any] | None) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for raw_json in raw_values or []:
        parsed = _parse_json_option(raw_json)
        if isinstance(parsed, list):
            items.extend([item for item in parsed if isinstance(item, dict)])
        elif isinstance(parsed, dict):
            items.append(parsed)
    for raw_file in raw_files or []:
        parsed = _load_json_option(None, raw_file)
        if isinstance(parsed, list):
            items.extend([item for item in parsed if isinstance(item, dict)])
        elif isinstance(parsed, dict):
            items.append(parsed)
    return items


def _normalize_approval_queue_state(state: dict[str, Any]) -> dict[str, Any]:
    items = state.get("queue_items", [])
    if not isinstance(items, list):
        items = []
    normalized_items: list[dict[str, Any]] = []
    resume_map = state.get("resume_map", {})
    normalized_resume_map = resume_map if isinstance(resume_map, dict) else {}
    for order, raw_item in enumerate(items, start=1):
        if not isinstance(raw_item, dict):
            continue
        normalized_items.append(
            {
                "interrupt_id": str(raw_item.get("interrupt_id", f"interrupt-{uuid.uuid4().hex[:12]}")),
                "order": int(raw_item.get("order", order) or order),
                "interrupt_point": str(raw_item.get("interrupt_point", "")),
                "value_summary": str(raw_item.get("value_summary", "")),
                "reason": str(raw_item.get("reason", "")),
                "status": str(raw_item.get("status", "pending")) if str(raw_item.get("status", "pending")) in APPROVAL_QUEUE_ITEM_STATUSES else "pending",
                "resume_value_present": bool(raw_item.get("resume_value_present", False)),
                "resume_value_keys": list(raw_item.get("resume_value_keys", [])),
                "created_at": str(raw_item.get("created_at", "")),
                "resolved_at": str(raw_item.get("resolved_at", "")),
            }
        )

    pending_items = [item for item in normalized_items if item["status"] == "pending"]
    resolved_items = [item for item in normalized_items if item["status"] == "resolved"]
    queue_posture = "no_interrupts"
    if pending_items and resolved_items:
        queue_posture = "partially_resolved"
    elif pending_items:
        queue_posture = "pending"
    elif resolved_items:
        queue_posture = "resolved"

    return {
        "queue_posture": queue_posture,
        "current_interrupt_id": pending_items[0]["interrupt_id"] if pending_items else "",
        "queue_items": sorted(normalized_items, key=lambda item: (int(item["order"]), item["interrupt_id"])),
        "resume_map": normalized_resume_map,
        "updated_at": str(state.get("updated_at", "")),
    }


def _ensure_approval_queue_state(thread: dict[str, Any]) -> dict[str, Any]:
    state = thread.get("approval_queue_state")
    if isinstance(state, dict):
        normalized = _normalize_approval_queue_state(state)
        thread["approval_queue_state"] = normalized
        return normalized
    state = _default_approval_queue_state()
    thread["approval_queue_state"] = state
    return state


def _build_approval_queue_state(
    raw_items: list[dict[str, Any]],
    *,
    default_interrupt_point: str = "",
    default_reason: str = "",
) -> dict[str, Any]:
    queue_items: list[dict[str, Any]] = []
    created_at = _now()
    for order, raw_item in enumerate(raw_items, start=1):
        item = dict(raw_item)
        interrupt_id = str(item.get("interrupt_id", f"interrupt-{uuid.uuid4().hex[:12]}"))
        interrupt_point = str(item.get("interrupt_point", default_interrupt_point))
        reason = str(item.get("reason", default_reason))
        value_summary = str(item.get("value_summary", reason or interrupt_point or interrupt_id))
        queue_items.append(
            {
                "interrupt_id": interrupt_id,
                "order": order,
                "interrupt_point": interrupt_point,
                "value_summary": value_summary,
                "reason": reason,
                "status": "pending",
                "resume_value_present": False,
                "resume_value_keys": [],
                "created_at": created_at,
                "resolved_at": "",
            }
        )
    return _normalize_approval_queue_state(
        {
            "queue_items": queue_items,
            "resume_map": {},
            "updated_at": created_at,
        }
    )


def _set_approval_queue_state(
    thread: dict[str, Any],
    raw_items: list[dict[str, Any]],
    *,
    default_interrupt_point: str = "",
    default_reason: str = "",
) -> dict[str, Any]:
    state = _build_approval_queue_state(
        raw_items,
        default_interrupt_point=default_interrupt_point,
        default_reason=default_reason,
    )
    thread["approval_queue_state"] = state
    return state


def _apply_approval_resume_map(thread: dict[str, Any], resume_map: dict[str, Any]) -> dict[str, Any]:
    state = _ensure_approval_queue_state(thread)
    if not resume_map:
        return state

    items = state.get("queue_items", [])
    for item in items:
        interrupt_id = item["interrupt_id"]
        if interrupt_id not in resume_map:
            continue
        resume_value = resume_map[interrupt_id]
        item["status"] = "resolved"
        item["resume_value_present"] = True
        item["resume_value_keys"] = _payload_keys(resume_value)
        item["resolved_at"] = _now()
        state.setdefault("resume_map", {})[interrupt_id] = _clone_payload(resume_value)

    state["updated_at"] = _now()
    normalized = _normalize_approval_queue_state(state)
    thread["approval_queue_state"] = normalized
    return normalized


def _approval_resume_map_from_payload(thread: dict[str, Any], resume_payload: Any) -> dict[str, Any]:
    if resume_payload is None:
        return {}
    state = _ensure_approval_queue_state(thread)
    for item in state.get("queue_items", []):
        if item.get("status") == "pending":
            return {str(item["interrupt_id"]): resume_payload}
    return {}


def _interrupt_payload_from_queue(thread: dict[str, Any]) -> dict[str, Any]:
    state = _ensure_approval_queue_state(thread)
    queue_items = state.get("queue_items", [])
    pending_items = [item for item in queue_items if item.get("status") == "pending"]
    if not pending_items:
        return {}
    current_item = pending_items[0]
    return {
        "thread_id": thread["thread_id"],
        "interrupt_id": current_item["interrupt_id"],
        "interrupt_point": current_item["interrupt_point"],
        "status": "waiting_for_approval",
        "reason": current_item["reason"],
        "value_summary": current_item["value_summary"],
        "loop_projection": _loop_projection(thread),
        "approval_queue_state": _clone_payload(state),
        "updated_at": _now(),
    }


def _approval_queue_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    state = _ensure_approval_queue_state(thread)
    queue_items = state.get("queue_items", [])
    pending_items = [item for item in queue_items if item.get("status") == "pending"]
    resolved_items = [item for item in queue_items if item.get("status") == "resolved"]
    helper_pointer: dict[str, Any] = {
        "command": "approval-queue",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id
    bounded_items = [
        {
            "interrupt_id": str(item.get("interrupt_id", "")),
            "order": int(item.get("order", 0) or 0),
            "interrupt_point": str(item.get("interrupt_point", "")),
            "value_summary": str(item.get("value_summary", "")),
            "reason": str(item.get("reason", "")),
            "status": str(item.get("status", "")),
            "resume_value_present": bool(item.get("resume_value_present", False)),
            "resume_value_keys": list(item.get("resume_value_keys", [])),
        }
        for item in queue_items
    ]
    return {
        "queue_posture": str(state.get("queue_posture", "no_interrupts")),
        "queue_size": len(queue_items),
        "pending_count": len(pending_items),
        "resolved_count": len(resolved_items),
        "pending_interrupt_ids": [str(item["interrupt_id"]) for item in pending_items],
        "resolved_interrupt_ids": [str(item["interrupt_id"]) for item in resolved_items],
        "current_interrupt_id": str(state.get("current_interrupt_id", "")),
        "resume_map_keys": sorted([str(key) for key in state.get("resume_map", {}).keys()]),
        "queue_items": bounded_items,
        "helper_pointer": helper_pointer,
    }


def _automatic_runtime_policy_identity() -> dict[str, Any]:
    return _clone_payload(AUTOMATIC_RUNTIME_POLICY_IDENTITY)


def _automatic_runtime_policy_decision(thread: dict[str, Any]) -> dict[str, Any]:
    migration_projection = _migration_projection(thread)
    approval_queue_projection = _approval_queue_projection(thread)
    recovery_projection = _recovery_projection(thread)
    migration_reason_codes = [str(code) for code in migration_projection.get("reason_codes", [])]
    migration_compatibility = str(migration_projection.get("compatibility", "migration_safe"))
    queue_pending_count = int(approval_queue_projection.get("pending_count", 0) or 0)
    queue_resolved_count = int(approval_queue_projection.get("resolved_count", 0) or 0)
    recovery_posture = str(recovery_projection.get("posture", "ordinary"))

    automatic_actions_available: list[str] = []

    if migration_compatibility == "migration_safe":
        migration_policy_posture = "auto_continue_safe"
        automatic_actions_available.append("continue_on_migration_safe")
    elif migration_compatibility == "degraded_compatible" and (
        set(migration_reason_codes)
        <= {
            "topology_version_missing",
            "topology_minor_drift",
            "state_schema_version_missing",
            "state_schema_minor_drift",
        }
    ):
        migration_policy_posture = "auto_continue_with_notice"
        automatic_actions_available.append("continue_on_degraded_compatible")
    elif migration_compatibility == "incompatible" or "graph_contract_id_mismatch" in migration_reason_codes:
        migration_policy_posture = "manual_recovery_required"
    else:
        migration_policy_posture = "manual_only"

    if recovery_posture == "recovered_pending_resume" and queue_pending_count == 0:
        if migration_policy_posture in {"auto_continue_safe", "auto_continue_with_notice"}:
            recovery_policy_posture = "auto_continue_safe"
            automatic_actions_available.append("continue_after_safe_recovery")
        else:
            recovery_policy_posture = "manual_recovery_required"
    else:
        recovery_policy_posture = "ordinary"

    if queue_pending_count > 0:
        approval_policy_posture = "waiting_for_manual_approval"
    elif queue_resolved_count > 0 and (
        str(thread.get("status", "")) == "waiting_for_approval"
        or str(thread.get("stop_reason", "")) == "needs_human"
    ):
        approval_policy_posture = "auto_resume_safe"
        automatic_actions_available.append("resume_after_resolved_queue")
    elif queue_pending_count == 0 and queue_resolved_count == 0 and str(thread.get("status", "")) != "waiting_for_approval":
        approval_policy_posture = "auto_clear_stale_interrupt"
        automatic_actions_available.append("clear_stale_interrupt")
    elif queue_resolved_count > 0:
        approval_policy_posture = "resolved_queue_retained"
    else:
        approval_policy_posture = "no_queue_work"

    safe_to_auto_apply = any(
        action in {"resume_after_resolved_queue", "continue_after_safe_recovery", "clear_stale_interrupt"}
        for action in automatic_actions_available
    )
    return {
        "migration_policy_posture": migration_policy_posture,
        "approval_policy_posture": approval_policy_posture,
        "recovery_policy_posture": recovery_policy_posture,
        "automatic_actions_available": sorted(dict.fromkeys(automatic_actions_available)),
        "safe_to_auto_apply": safe_to_auto_apply,
    }


def _automatic_runtime_policy_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    decision = _automatic_runtime_policy_decision(thread)
    state = thread.get("automatic_runtime_policy_state")
    helper_pointer: dict[str, Any] = {
        "command": "auto-policy",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "policy_identity": _automatic_runtime_policy_identity(),
            **decision,
            "last_auto_action": "",
            "last_auto_reason": "",
        }

    return {
        "policy_identity": state.get("policy_identity", _automatic_runtime_policy_identity()),
        "migration_policy_posture": str(
            state.get("migration_policy_posture", decision["migration_policy_posture"])
        ),
        "approval_policy_posture": str(
            state.get("approval_policy_posture", decision["approval_policy_posture"])
        ),
        "recovery_policy_posture": str(
            state.get("recovery_policy_posture", decision["recovery_policy_posture"])
        ),
        "automatic_actions_available": list(
            state.get("automatic_actions_available", decision["automatic_actions_available"])
        ),
        "safe_to_auto_apply": bool(state.get("safe_to_auto_apply", decision["safe_to_auto_apply"])),
        "last_auto_action": str(state.get("last_auto_action", "")),
        "last_auto_reason": str(state.get("last_auto_reason", "")),
        "helper_pointer": helper_pointer,
    }


def _persist_automatic_runtime_policy_state(thread: dict[str, Any]) -> dict[str, Any]:
    decision = _automatic_runtime_policy_decision(thread)
    existing_state = thread.get("automatic_runtime_policy_state")
    stored = {
        "policy_identity": _automatic_runtime_policy_identity(),
        "migration_policy_posture": decision["migration_policy_posture"],
        "approval_policy_posture": decision["approval_policy_posture"],
        "recovery_policy_posture": decision["recovery_policy_posture"],
        "automatic_actions_available": decision["automatic_actions_available"],
        "safe_to_auto_apply": decision["safe_to_auto_apply"],
        "last_auto_action": (
            str(existing_state.get("last_auto_action", "")) if isinstance(existing_state, dict) else ""
        ),
        "last_auto_reason": (
            str(existing_state.get("last_auto_reason", "")) if isinstance(existing_state, dict) else ""
        ),
        "updated_at": _now(),
    }
    thread["automatic_runtime_policy_state"] = stored
    return stored


def _apply_automatic_runtime_policy(
    thread: dict[str, Any], interrupt: dict[str, Any] | None
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    decision = _automatic_runtime_policy_decision(thread)
    applied_actions: list[str] = []
    applied_reason = ""
    updated_interrupt = _clone_payload(interrupt) if isinstance(interrupt, dict) else {}

    if decision["migration_policy_posture"] == "auto_continue_safe":
        applied_actions.append("continue_on_migration_safe")
        applied_reason = applied_reason or "migration_safe"
    elif decision["migration_policy_posture"] == "auto_continue_with_notice":
        applied_actions.append("continue_on_degraded_compatible")
        applied_reason = applied_reason or "degraded_compatible_minor_drift"

    if decision["approval_policy_posture"] == "auto_resume_safe":
        if str(thread.get("status", "")) == "waiting_for_approval":
            thread["status"] = "resumed"
        if str(thread.get("stop_reason", "")) == "needs_human":
            thread["stop_reason"] = ""
        thread.pop("recovery_state", None)
        updated_interrupt = {}
        applied_actions.append("resume_after_resolved_queue")
        applied_reason = applied_reason or "resolved_queue_without_pending_interrupts"
    elif decision["approval_policy_posture"] == "auto_clear_stale_interrupt" and updated_interrupt:
        updated_interrupt = {}
        applied_actions.append("clear_stale_interrupt")
        applied_reason = applied_reason or "stale_interrupt_without_pending_queue"

    if decision["recovery_policy_posture"] == "auto_continue_safe":
        thread.pop("recovery_state", None)
        if str(thread.get("status", "")) in {"", "resumed", "running"}:
            thread["status"] = "resumed"
        applied_actions.append("continue_after_safe_recovery")
        applied_reason = applied_reason or "safe_recovery_continuation"

    state = _persist_automatic_runtime_policy_state(thread)
    state["last_auto_action"] = ",".join(applied_actions)
    state["last_auto_reason"] = applied_reason
    thread["automatic_runtime_policy_state"] = state

    return (updated_interrupt if updated_interrupt else {}), state


def _graph_kernel_identity() -> dict[str, Any]:
    return _clone_payload(GRAPH_KERNEL_IDENTITY)


def _graph_kernel_node_id_for_thread(thread: dict[str, Any]) -> str:
    recovery_state = thread.get("recovery_state")
    if isinstance(recovery_state, dict) and recovery_state.get("posture") == "recovered_pending_resume":
        return "recovery_pending_resume"
    approval_queue = _approval_queue_projection(thread)
    if approval_queue["pending_count"] > 0 or thread.get("status") == "waiting_for_approval":
        return "approval_wait"
    if thread.get("status") == "accepted" or thread.get("stop_reason") == "accepted":
        return "accepted_terminal"
    if thread.get("status") == "halted":
        return "halted_terminal"
    if thread.get("status") == "escalated" or thread.get("stop_reason") == "escalated":
        return "escalated_terminal"
    return GRAPH_KERNEL_PHASE_TO_NODE.get(str(thread.get("phase", "")), "")


def _graph_kernel_node(node_id: str, mapped_phase: str) -> dict[str, Any]:
    node = _clone_payload(GRAPH_KERNEL_NODES.get(node_id, {}))
    if node and mapped_phase and not node.get("phase"):
        node["phase"] = mapped_phase
    return node


def _graph_kernel_node_posture(node_id: str) -> str:
    if node_id == "approval_wait":
        return "approval_wait"
    if node_id == "recovery_pending_resume":
        return "recovery_pending_resume"
    node = GRAPH_KERNEL_NODES.get(node_id, {})
    if isinstance(node, dict) and node.get("terminal"):
        return "terminal"
    return "phase_active"


def _graph_kernel_available_next_nodes(thread: dict[str, Any], node_id: str, mapped_phase: str) -> list[str]:
    if node_id in {"approval_wait", "recovery_pending_resume"}:
        resume_node = GRAPH_KERNEL_PHASE_TO_NODE.get(mapped_phase, "")
        return [resume_node] if resume_node else []

    next_nodes = [
        str(edge["target_node"])
        for edge in GRAPH_KERNEL_EDGES
        if edge["source_node"] == node_id and not str(edge["target_node"]).startswith("*")
    ]
    if node_id == "freeze_plan":
        next_nodes.append("approval_wait")
    if node_id in {"execute_parallel", "stabilize", "verify_accept"}:
        next_nodes.append("approval_wait")
    return sorted(dict.fromkeys([node for node in next_nodes if node]))


def _graph_kernel_last_transition(thread: dict[str, Any], node_id: str, mapped_phase: str) -> dict[str, Any]:
    command_state = thread.get("command_state")
    recovery_state = thread.get("recovery_state")
    approval_queue = _approval_queue_projection(thread)
    source_node = GRAPH_KERNEL_PHASE_TO_NODE.get(mapped_phase, "")

    if isinstance(recovery_state, dict) and recovery_state.get("posture") == "recovered_pending_resume":
        return {
            "transition_kind": "recovery",
            "source_node": source_node,
            "target_node": "recovery_pending_resume",
            "reason": str(recovery_state.get("last_action", "")),
        }
    if approval_queue["pending_count"] > 0 or thread.get("status") == "waiting_for_approval":
        return {
            "transition_kind": "interrupt",
            "source_node": source_node,
            "target_node": "approval_wait",
            "reason": str(thread.get("last_gate_reason", "")),
        }
    if isinstance(command_state, dict) and command_state.get("transition_kind"):
        return {
            "transition_kind": "command",
            "source_node": str(command_state.get("source_subgraph", "")) or source_node,
            "target_node": node_id,
            "reason": str(command_state.get("transition_kind", "")),
        }
    if thread.get("last_gate_verdict"):
        verdict = str(thread.get("last_gate_verdict", ""))
        transition_kind = "terminal" if verdict in {"accept", "halt", "escalate"} else "loop"
        return {
            "transition_kind": transition_kind,
            "source_node": source_node,
            "target_node": node_id,
            "reason": verdict,
        }
    return {
        "transition_kind": "sequential",
        "source_node": source_node,
        "target_node": node_id,
        "reason": str(thread.get("phase", "")),
    }


def _graph_kernel_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    mapped_phase = str(thread.get("phase", ""))
    current_node_id = _graph_kernel_node_id_for_thread(thread)
    current_node = _graph_kernel_node(current_node_id, mapped_phase)
    helper_pointer: dict[str, Any] = {
        "command": "kernel",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id
    return {
        "kernel_identity": _graph_kernel_identity(),
        "current_node_id": current_node_id,
        "mapped_phase": mapped_phase,
        "node_posture": _graph_kernel_node_posture(current_node_id),
        "current_node": current_node,
        "available_next_nodes": _graph_kernel_available_next_nodes(thread, current_node_id, mapped_phase),
        "last_transition": _graph_kernel_last_transition(thread, current_node_id, mapped_phase),
        "helper_pointer": helper_pointer,
    }


def _persist_graph_kernel_state(thread: dict[str, Any]) -> dict[str, Any]:
    projection = _graph_kernel_projection(thread, str(thread.get("thread_id", "")))
    stored = {
        "kernel_identity": projection["kernel_identity"],
        "current_node_id": projection["current_node_id"],
        "mapped_phase": projection["mapped_phase"],
        "node_posture": projection["node_posture"],
        "current_node": projection["current_node"],
        "available_next_nodes": projection["available_next_nodes"],
        "last_transition": projection["last_transition"],
        "updated_at": _now(),
    }
    thread["graph_kernel_state"] = stored
    return stored


def _primary_runtime_engine_identity() -> dict[str, Any]:
    return _clone_payload(PRIMARY_RUNTIME_ENGINE_IDENTITY)


def _primary_runtime_engine_posture(thread: dict[str, Any]) -> str:
    kernel_projection = _graph_kernel_projection(thread)
    node_posture = kernel_projection["node_posture"]
    if node_posture == "approval_wait":
        return "interrupt_wait"
    if node_posture == "recovery_pending_resume":
        return "recovery_wait"
    if node_posture == "terminal":
        return "terminal"
    if not LANGGRAPH_AVAILABLE:
        return "compiled_unavailable"
    return "compiled_ready"


def _primary_runtime_engine_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    kernel_projection = _graph_kernel_projection(thread, thread_id)
    helper_pointer: dict[str, Any] = {
        "command": "engine",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id
    return {
        "engine_identity": _primary_runtime_engine_identity(),
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": bool(LANGGRAPH_AVAILABLE),
        "checkpointer_expected": True,
        "entry_node": "define_target",
        "finish_nodes": ["accepted_terminal", "halted_terminal", "escalated_terminal"],
        "current_execution_node": kernel_projection["current_node_id"],
        "mapped_phase": kernel_projection["mapped_phase"],
        "execution_posture": _primary_runtime_engine_posture(thread),
        "last_execution_reason": kernel_projection["last_transition"]["reason"],
        "helper_pointer": helper_pointer,
    }


def _persist_primary_runtime_engine_state(thread: dict[str, Any]) -> dict[str, Any]:
    projection = _primary_runtime_engine_projection(thread, str(thread.get("thread_id", "")))
    stored = {
        "engine_identity": projection["engine_identity"],
        "compile_supported": projection["compile_supported"],
        "compiled_graph_present": projection["compiled_graph_present"],
        "checkpointer_expected": projection["checkpointer_expected"],
        "entry_node": projection["entry_node"],
        "finish_nodes": projection["finish_nodes"],
        "current_execution_node": projection["current_execution_node"],
        "mapped_phase": projection["mapped_phase"],
        "execution_posture": projection["execution_posture"],
        "last_execution_reason": projection["last_execution_reason"],
        "updated_at": _now(),
    }
    thread["primary_runtime_engine_state"] = stored
    return stored


def _compiled_invocation_identity() -> dict[str, Any]:
    return _clone_payload(COMPILED_INVOCATION_IDENTITY)


def _compiled_graph_metadata() -> dict[str, Any]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compiled_node_count": len([node for node in GRAPH_KERNEL_NODES.values() if not node.get("terminal") or node.get("node_kind") == "terminal"]),
        "compiled_edge_count": len(GRAPH_KERNEL_EDGES),
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class DurableState(TypedDict, total=False):
            phase: str
            status: str
            active_loop: str
            last_gate_verdict: str
            stop_reason: str

        def make_phase_node(phase_name: str):
            def _node(state: DurableState) -> DurableState:
                return {"phase": phase_name}

            return _node

        builder = StateGraph(DurableState)
        builder.add_node("define_target", make_phase_node("define-target"))
        builder.add_node("read_context", make_phase_node("read-context"))
        builder.add_node("freeze_plan", make_phase_node("freeze-plan"))
        builder.add_node("execute_parallel", make_phase_node("execute-parallel"))
        builder.add_node("integrate_converge", make_phase_node("integrate-converge"))
        builder.add_node("stabilize", make_phase_node("stabilize"))
        builder.add_node("verify_accept", make_phase_node("verify-accept"))
        builder.add_edge(START, "define_target")
        builder.add_edge("define_target", "read_context")
        builder.add_edge("read_context", "freeze_plan")
        builder.add_edge("freeze_plan", "execute_parallel")
        builder.add_edge("execute_parallel", "integrate_converge")
        builder.add_edge("integrate_converge", "stabilize")
        builder.add_edge("stabilize", "verify_accept")
        builder.add_edge("verify_accept", END)
        compiled = builder.compile()

        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return metadata
    except Exception as exc:  # pragma: no cover - only exercised when langgraph is installed
        metadata["compile_error"] = str(exc)
        return metadata


def _compiled_invocation_posture(thread: dict[str, Any], metadata: dict[str, Any]) -> str:
    kernel_projection = _graph_kernel_projection(thread)
    node_posture = kernel_projection["node_posture"]
    if node_posture == "approval_wait":
        return "interrupt_wait"
    if node_posture == "recovery_pending_resume":
        return "recovery_wait"
    if node_posture == "terminal":
        return "completed"
    if metadata["compiled_graph_present"]:
        return "compiled_ready"
    return "unavailable"


def _compiled_invocation_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    metadata = _compiled_graph_metadata()
    kernel_projection = _graph_kernel_projection(thread, thread_id)
    helper_pointer: dict[str, Any] = {
        "command": "invocation",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id
    return {
        "invocation_identity": _compiled_invocation_identity(),
        "compile_supported": metadata["compile_supported"],
        "compiled_graph_present": metadata["compiled_graph_present"],
        "invoke_supported": metadata["invoke_supported"],
        "stream_supported": metadata["stream_supported"],
        "compiled_node_count": metadata["compiled_node_count"],
        "compiled_edge_count": metadata["compiled_edge_count"],
        "current_execution_node": kernel_projection["current_node_id"],
        "mapped_phase": kernel_projection["mapped_phase"],
        "invocation_posture": _compiled_invocation_posture(thread, metadata),
        "last_invoke_kind": str(thread.get("last_compiled_invoke_kind", "")),
        "last_invoke_reason": str(thread.get("last_compiled_invoke_reason", metadata["compile_error"])),
        "helper_pointer": helper_pointer,
    }


def _persist_compiled_invocation_state(thread: dict[str, Any]) -> dict[str, Any]:
    projection = _compiled_invocation_projection(thread, str(thread.get("thread_id", "")))
    stored = {
        "invocation_identity": projection["invocation_identity"],
        "compile_supported": projection["compile_supported"],
        "compiled_graph_present": projection["compiled_graph_present"],
        "invoke_supported": projection["invoke_supported"],
        "stream_supported": projection["stream_supported"],
        "compiled_node_count": projection["compiled_node_count"],
        "compiled_edge_count": projection["compiled_edge_count"],
        "current_execution_node": projection["current_execution_node"],
        "mapped_phase": projection["mapped_phase"],
        "invocation_posture": projection["invocation_posture"],
        "last_invoke_kind": projection["last_invoke_kind"],
        "last_invoke_reason": projection["last_invoke_reason"],
        "updated_at": _now(),
    }
    thread["compiled_invocation_state"] = stored
    return stored


def _live_execution_identity() -> dict[str, Any]:
    return _clone_payload(LIVE_EXECUTION_IDENTITY)


def _phase_node_names() -> list[str]:
    return [
        "define_target",
        "read_context",
        "freeze_plan",
        "execute_parallel",
        "integrate_converge",
        "stabilize",
        "verify_accept",
    ]


def _build_live_compiled_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class DurableState(TypedDict, total=False):
            phase: str
            status: str
            active_loop: str
            last_gate_verdict: str
            stop_reason: str
            executed_node: str
            execution_reason: str

        phase_nodes = _phase_node_names()

        def route_phase(state: DurableState) -> Literal[
            "define_target",
            "read_context",
            "freeze_plan",
            "execute_parallel",
            "integrate_converge",
            "stabilize",
            "verify_accept",
        ]:
            node_name = GRAPH_KERNEL_PHASE_TO_NODE.get(str(state.get("phase", "")), "define_target")
            return node_name if node_name in phase_nodes else "define_target"

        def make_phase_node(node_name: str, phase_name: str):
            def _node(state: DurableState) -> DurableState:
                return {
                    "phase": phase_name,
                    "executed_node": node_name,
                    "execution_reason": f"executed:{node_name}",
                }

            return _node

        builder = StateGraph(DurableState)
        builder.add_node("route", lambda state: {})
        builder.add_edge(START, "route")
        for node_name in phase_nodes:
            phase_name = GRAPH_KERNEL_NODES[node_name]["phase"]
            builder.add_node(node_name, make_phase_node(node_name, phase_name))
            builder.add_edge(node_name, END)
        builder.add_conditional_edges("route", route_phase)
        compiled = builder.compile()

        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return compiled, metadata
    except Exception as exc:  # pragma: no cover - only exercised when langgraph is installed
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_live_compiled_graph(thread: dict[str, Any], run_kind: str) -> dict[str, Any]:
    compiled, metadata = _build_live_compiled_graph()
    kernel_projection = _graph_kernel_projection(thread)
    current_node = kernel_projection["current_node_id"]
    mapped_phase = kernel_projection["mapped_phase"]
    posture = kernel_projection["node_posture"]

    if posture == "approval_wait":
        return {
            **metadata,
            "current_execution_node": current_node,
            "mapped_phase": mapped_phase,
            "execution_posture": "interrupt_wait",
            "last_run_kind": run_kind,
            "last_run_status": "blocked",
            "last_run_reason": "approval_wait",
            "last_output_keys": [],
            "last_stream_event_count": 0,
        }
    if posture == "recovery_pending_resume":
        return {
            **metadata,
            "current_execution_node": current_node,
            "mapped_phase": mapped_phase,
            "execution_posture": "recovery_wait",
            "last_run_kind": run_kind,
            "last_run_status": "blocked",
            "last_run_reason": "recovery_pending_resume",
            "last_output_keys": [],
            "last_stream_event_count": 0,
        }
    if posture == "terminal":
        return {
            **metadata,
            "current_execution_node": current_node,
            "mapped_phase": mapped_phase,
            "execution_posture": "terminal",
            "last_run_kind": run_kind,
            "last_run_status": "noop",
            "last_run_reason": "terminal_state",
            "last_output_keys": [],
            "last_stream_event_count": 0,
        }
    if compiled is None:
        return {
            **metadata,
            "current_execution_node": current_node,
            "mapped_phase": mapped_phase,
            "execution_posture": "unavailable",
            "last_run_kind": run_kind,
            "last_run_status": "unavailable",
            "last_run_reason": metadata["compile_error"] or "langgraph_package_unavailable",
            "last_output_keys": [],
            "last_stream_event_count": 0,
        }

    input_state = {
        "phase": mapped_phase or "define-target",
        "status": str(thread.get("status", "")),
        "active_loop": str(thread.get("active_loop", "")),
        "last_gate_verdict": str(thread.get("last_gate_verdict", "")),
        "stop_reason": str(thread.get("stop_reason", "")),
    }

    try:
        if run_kind == "stream":
            chunks = list(compiled.stream(input_state))
            output = chunks[-1] if chunks else {}
            stream_count = len(chunks)
        else:
            output = compiled.invoke(input_state)
            stream_count = 0
        output_dict = output if isinstance(output, dict) else {"$scalar": output}
        output_phase = str(output_dict.get("phase", mapped_phase))
        output_node = GRAPH_KERNEL_PHASE_TO_NODE.get(output_phase, current_node)
        return {
            **metadata,
            "current_execution_node": output_node,
            "mapped_phase": output_phase,
            "execution_posture": "executed",
            "last_run_kind": run_kind,
            "last_run_status": "ok",
            "last_run_reason": str(output_dict.get("execution_reason", f"executed:{run_kind}")),
            "last_output_keys": _payload_keys(output_dict),
            "last_stream_event_count": stream_count,
        }
    except Exception as exc:  # pragma: no cover - only exercised when langgraph is installed
        return {
            **metadata,
            "current_execution_node": current_node,
            "mapped_phase": mapped_phase,
            "execution_posture": "execution_failed",
            "last_run_kind": run_kind,
            "last_run_status": "error",
            "last_run_reason": str(exc),
            "last_output_keys": [],
            "last_stream_event_count": 0,
        }


def _live_execution_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    state = thread.get("live_execution_state")
    helper_pointer: dict[str, Any] = {
        "command": "live-execution",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id
    if not isinstance(state, dict):
        state = {
            "execution_identity": _live_execution_identity(),
            "compile_supported": bool(LANGGRAPH_AVAILABLE),
            "compiled_graph_present": False,
            "invoke_supported": False,
            "stream_supported": False,
            "current_execution_node": _graph_kernel_projection(thread)["current_node_id"],
            "mapped_phase": _graph_kernel_projection(thread)["mapped_phase"],
            "execution_posture": "unavailable" if not LANGGRAPH_AVAILABLE else "ready",
            "last_run_kind": "",
            "last_run_status": "",
            "last_run_reason": "",
            "last_output_keys": [],
            "last_stream_event_count": 0,
        }
    return {
        "execution_identity": state.get("execution_identity", _live_execution_identity()),
        "compile_supported": bool(state.get("compile_supported", False)),
        "compiled_graph_present": bool(state.get("compiled_graph_present", False)),
        "invoke_supported": bool(state.get("invoke_supported", False)),
        "stream_supported": bool(state.get("stream_supported", False)),
        "current_execution_node": str(state.get("current_execution_node", "")),
        "mapped_phase": str(state.get("mapped_phase", "")),
        "execution_posture": str(state.get("execution_posture", "unavailable")),
        "last_run_kind": str(state.get("last_run_kind", "")),
        "last_run_status": str(state.get("last_run_status", "")),
        "last_run_reason": str(state.get("last_run_reason", "")),
        "last_output_keys": list(state.get("last_output_keys", [])),
        "last_stream_event_count": int(state.get("last_stream_event_count", 0) or 0),
        "helper_pointer": helper_pointer,
    }


def _persist_live_execution_state(thread: dict[str, Any], run_kind: str = "") -> dict[str, Any]:
    run_kind = run_kind or str(thread.get("last_live_execution_kind", "")) or "invoke"
    result = _execute_live_compiled_graph(thread, run_kind)
    stored = {
        "execution_identity": _live_execution_identity(),
        "compile_supported": result["compile_supported"],
        "compiled_graph_present": result["compiled_graph_present"],
        "invoke_supported": result["invoke_supported"],
        "stream_supported": result["stream_supported"],
        "current_execution_node": result["current_execution_node"],
        "mapped_phase": result["mapped_phase"],
        "execution_posture": result["execution_posture"],
        "last_run_kind": result["last_run_kind"],
        "last_run_status": result["last_run_status"],
        "last_run_reason": result["last_run_reason"],
        "last_output_keys": result["last_output_keys"],
        "last_stream_event_count": result["last_stream_event_count"],
        "updated_at": _now(),
    }
    thread["last_live_execution_kind"] = run_kind
    thread["last_live_execution_reason"] = result["last_run_reason"]
    thread["live_execution_state"] = stored
    return stored


def _fuller_live_primary_engine_identity() -> dict[str, Any]:
    return _clone_payload(FULLER_LIVE_PRIMARY_ENGINE_IDENTITY)


def _phase_successor(phase: str) -> str:
    successors = {
        "define-target": "read-context",
        "read-context": "freeze-plan",
        "freeze-plan": "execute-parallel",
        "execute-parallel": "integrate-converge",
        "integrate-converge": "stabilize",
        "stabilize": "verify-accept",
    }
    return successors.get(phase, "")


def _fuller_live_primary_engine_preview(thread: dict[str, Any], run_kind: str) -> dict[str, Any]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    kernel_projection = _graph_kernel_projection(thread)
    command_projection = _command_projection(thread)
    current_node = str(kernel_projection["current_node_id"])
    mapped_phase = str(kernel_projection["mapped_phase"])
    node_posture = str(kernel_projection["node_posture"])
    execution_path = [current_node] if current_node else []
    current_status = str(thread.get("status", "")) or "running"

    if node_posture == "approval_wait":
        return {
            **metadata,
            "current_execution_node": current_node,
            "mapped_phase": mapped_phase,
            "execution_node_path": execution_path,
            "resulting_phase": mapped_phase,
            "resulting_status": current_status or "waiting_for_approval",
            "phase_transition_kind": "interrupt",
            "execution_posture": "interrupt_wait",
            "last_run_kind": run_kind,
            "last_run_status": "blocked",
            "last_run_reason": "approval_wait",
        }
    if node_posture == "recovery_pending_resume":
        return {
            **metadata,
            "current_execution_node": current_node,
            "mapped_phase": mapped_phase,
            "execution_node_path": execution_path,
            "resulting_phase": mapped_phase,
            "resulting_status": current_status,
            "phase_transition_kind": "recovery",
            "execution_posture": "recovery_wait",
            "last_run_kind": run_kind,
            "last_run_status": "blocked",
            "last_run_reason": "recovery_pending_resume",
        }
    if node_posture == "terminal":
        return {
            **metadata,
            "current_execution_node": current_node,
            "mapped_phase": mapped_phase,
            "execution_node_path": execution_path,
            "resulting_phase": mapped_phase,
            "resulting_status": current_status,
            "phase_transition_kind": "terminal",
            "execution_posture": "terminal",
            "last_run_kind": run_kind,
            "last_run_status": "noop",
            "last_run_reason": "terminal_state",
        }

    command_target_phase = _command_target_phase(
        str(command_projection["parent_handoff_target"]) or str(command_projection["goto_target"])
    )
    transition_kind = "stayed_put"
    resulting_phase = mapped_phase
    resulting_status = "running" if current_status in {"", "resumed", "running"} else current_status
    last_run_reason = f"stay:{mapped_phase or current_node}"

    if str(command_projection["transition_kind"]) in {"goto", "update_goto", "parent_handoff", "resume_parent_handoff"} and command_target_phase:
        resulting_phase = command_target_phase
        transition_kind = "command"
        last_run_reason = f"command:{command_projection['transition_kind']}->{command_target_phase}"
    elif mapped_phase in {"execute-parallel", "stabilize"} and str(thread.get("last_gate_verdict", "")) == "revise":
        resulting_phase = mapped_phase
        transition_kind = "loop"
        last_run_reason = f"loop:{thread.get('active_loop', '')}:revise"
    else:
        successor = _phase_successor(mapped_phase)
        if successor:
            resulting_phase = successor
            transition_kind = "sequential"
            last_run_reason = f"advance:{mapped_phase}->{successor}"

    next_node = GRAPH_KERNEL_PHASE_TO_NODE.get(resulting_phase, "")
    if next_node and (not execution_path or next_node != execution_path[-1] or transition_kind == "loop"):
        execution_path.append(next_node)

    return {
        **metadata,
        "current_execution_node": current_node,
        "mapped_phase": mapped_phase,
        "execution_node_path": execution_path,
        "resulting_phase": resulting_phase,
        "resulting_status": resulting_status,
        "phase_transition_kind": transition_kind,
        "execution_posture": "ready" if LANGGRAPH_AVAILABLE else "unavailable",
        "last_run_kind": run_kind,
        "last_run_status": "planned" if not LANGGRAPH_AVAILABLE else "ok",
        "last_run_reason": last_run_reason,
    }


def _build_fuller_live_primary_engine_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class EngineState(TypedDict, total=False):
            current_execution_node: str
            target_execution_node: str
            mapped_phase: str
            resulting_phase: str
            resulting_status: str
            phase_transition_kind: str
            execution_node_path: list[str]
            last_run_reason: str

        valid_nodes = _phase_node_names()

        def route_current(
            state: EngineState,
        ) -> Literal[
            "define_target",
            "read_context",
            "freeze_plan",
            "execute_parallel",
            "integrate_converge",
            "stabilize",
            "verify_accept",
        ]:
            node_name = str(state.get("current_execution_node", ""))
            return node_name if node_name in valid_nodes else "define_target"

        def route_target(state: EngineState) -> Literal[
            "define_target",
            "read_context",
            "freeze_plan",
            "execute_parallel",
            "integrate_converge",
            "stabilize",
            "verify_accept",
            "phase_end",
        ]:
            node_name = str(state.get("target_execution_node", ""))
            return node_name if node_name in valid_nodes else "phase_end"

        def make_phase_node(node_name: str, phase_name: str):
            def _node(state: EngineState) -> EngineState:
                path = list(state.get("execution_node_path", []))
                path.append(node_name)
                return {
                    "execution_node_path": path,
                    "mapped_phase": phase_name,
                    "resulting_phase": phase_name,
                }

            return _node

        def phase_end(state: EngineState) -> EngineState:
            return {
                "execution_node_path": list(state.get("execution_node_path", [])),
                "resulting_phase": str(state.get("resulting_phase", state.get("mapped_phase", ""))),
                "resulting_status": str(state.get("resulting_status", "")),
            }

        builder = StateGraph(EngineState)
        builder.add_node("route_current", lambda state: state)
        builder.add_node("route_target", lambda state: state)
        builder.add_node("phase_end", phase_end)
        builder.add_edge(START, "route_current")
        for node_name in valid_nodes:
            phase_name = str(GRAPH_KERNEL_NODES[node_name]["phase"])
            builder.add_node(node_name, make_phase_node(node_name, phase_name))
            builder.add_edge(node_name, "route_target")
        builder.add_conditional_edges("route_current", route_current)
        builder.add_conditional_edges("route_target", route_target)
        builder.add_edge("phase_end", END)
        compiled = builder.compile()
        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return compiled, metadata
    except Exception as exc:  # pragma: no cover - only exercised when langgraph is installed
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_fuller_live_primary_engine(thread: dict[str, Any], run_kind: str) -> dict[str, Any]:
    preview = _fuller_live_primary_engine_preview(thread, run_kind)
    compiled, metadata = _build_fuller_live_primary_engine_graph()
    if compiled is None:
        unavailable_posture = (
            preview["execution_posture"] if preview["execution_posture"] in {"interrupt_wait", "recovery_wait", "terminal"} else "unavailable"
        )
        unavailable_status = (
            preview["last_run_status"] if preview["last_run_status"] in {"blocked", "noop"} else "unavailable"
        )
        return {
            **preview,
            **metadata,
            "execution_posture": unavailable_posture,
            "last_run_status": unavailable_status,
            "last_run_reason": metadata["compile_error"] or preview["last_run_reason"],
        }

    current_node = str(preview["current_execution_node"])
    execution_path = list(preview["execution_node_path"])
    target_execution_node = execution_path[-1] if len(execution_path) > 1 else ""

    try:
        if run_kind == "stream":
            chunks = list(
                compiled.stream(
                    {
                        "current_execution_node": current_node,
                        "target_execution_node": target_execution_node,
                        "mapped_phase": preview["mapped_phase"],
                        "resulting_phase": preview["resulting_phase"],
                        "resulting_status": preview["resulting_status"],
                        "phase_transition_kind": preview["phase_transition_kind"],
                        "execution_node_path": [],
                        "last_run_reason": preview["last_run_reason"],
                    }
                )
            )
            output = chunks[-1] if chunks else {}
        else:
            output = compiled.invoke(
                {
                    "current_execution_node": current_node,
                    "target_execution_node": target_execution_node,
                    "mapped_phase": preview["mapped_phase"],
                    "resulting_phase": preview["resulting_phase"],
                    "resulting_status": preview["resulting_status"],
                    "phase_transition_kind": preview["phase_transition_kind"],
                    "execution_node_path": [],
                    "last_run_reason": preview["last_run_reason"],
                }
            )
        output_dict = output if isinstance(output, dict) else {}
        rendered_path = list(output_dict.get("execution_node_path", execution_path))
        if not rendered_path:
            rendered_path = execution_path
        return {
            **metadata,
            "current_execution_node": current_node,
            "mapped_phase": preview["mapped_phase"],
            "execution_node_path": rendered_path,
            "resulting_phase": str(output_dict.get("resulting_phase", preview["resulting_phase"])),
            "resulting_status": str(output_dict.get("resulting_status", preview["resulting_status"])),
            "phase_transition_kind": str(
                output_dict.get("phase_transition_kind", preview["phase_transition_kind"])
            ),
            "execution_posture": preview["execution_posture"] if preview["execution_posture"] != "ready" else "executed",
            "last_run_kind": run_kind,
            "last_run_status": "ok",
            "last_run_reason": str(output_dict.get("last_run_reason", preview["last_run_reason"])),
        }
    except Exception as exc:  # pragma: no cover - only exercised when langgraph is installed
        return {
            **preview,
            **metadata,
            "execution_posture": "execution_failed",
            "last_run_status": "error",
            "last_run_reason": str(exc),
        }


def _fuller_live_primary_engine_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    state = thread.get("fuller_live_primary_engine_state")
    preview = _fuller_live_primary_engine_preview(
        thread, str(thread.get("last_fuller_live_primary_engine_kind", "")) or "invoke"
    )
    helper_pointer: dict[str, Any] = {
        "command": "fuller-engine",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "engine_identity": _fuller_live_primary_engine_identity(),
            **preview,
        }

    return {
        "engine_identity": state.get("engine_identity", _fuller_live_primary_engine_identity()),
        "compile_supported": bool(state.get("compile_supported", preview["compile_supported"])),
        "compiled_graph_present": bool(state.get("compiled_graph_present", preview["compiled_graph_present"])),
        "invoke_supported": bool(state.get("invoke_supported", preview["invoke_supported"])),
        "stream_supported": bool(state.get("stream_supported", preview["stream_supported"])),
        "current_execution_node": str(state.get("current_execution_node", preview["current_execution_node"])),
        "mapped_phase": str(state.get("mapped_phase", preview["mapped_phase"])),
        "execution_node_path": list(state.get("execution_node_path", preview["execution_node_path"])),
        "resulting_phase": str(state.get("resulting_phase", preview["resulting_phase"])),
        "resulting_status": str(state.get("resulting_status", preview["resulting_status"])),
        "phase_transition_kind": str(state.get("phase_transition_kind", preview["phase_transition_kind"])),
        "execution_posture": str(state.get("execution_posture", preview["execution_posture"])),
        "last_run_kind": str(state.get("last_run_kind", preview["last_run_kind"])),
        "last_run_status": str(state.get("last_run_status", preview["last_run_status"])),
        "last_run_reason": str(state.get("last_run_reason", preview["last_run_reason"])),
        "helper_pointer": helper_pointer,
    }


def _persist_fuller_live_primary_engine_state(thread: dict[str, Any], run_kind: str = "") -> dict[str, Any]:
    run_kind = run_kind or str(thread.get("last_fuller_live_primary_engine_kind", "")) or "invoke"
    result = _execute_fuller_live_primary_engine(thread, run_kind)
    stored = {
        "engine_identity": _fuller_live_primary_engine_identity(),
        "compile_supported": result["compile_supported"],
        "compiled_graph_present": result["compiled_graph_present"],
        "invoke_supported": result["invoke_supported"],
        "stream_supported": result["stream_supported"],
        "current_execution_node": result["current_execution_node"],
        "mapped_phase": result["mapped_phase"],
        "execution_node_path": result["execution_node_path"],
        "resulting_phase": result["resulting_phase"],
        "resulting_status": result["resulting_status"],
        "phase_transition_kind": result["phase_transition_kind"],
        "execution_posture": result["execution_posture"],
        "last_run_kind": result["last_run_kind"],
        "last_run_status": result["last_run_status"],
        "last_run_reason": result["last_run_reason"],
        "updated_at": _now(),
    }
    thread["last_fuller_live_primary_engine_kind"] = run_kind
    thread["last_fuller_live_primary_engine_reason"] = result["last_run_reason"]
    thread["fuller_live_primary_engine_state"] = stored
    return stored


def _deeper_live_primary_engine_identity() -> dict[str, Any]:
    return _clone_payload(DEEPER_LIVE_PRIMARY_ENGINE_IDENTITY)


def _phase_node_for_phase(phase: str) -> str:
    return str(GRAPH_KERNEL_PHASE_TO_NODE.get(phase, ""))


def _deeper_live_primary_engine_preview(thread: dict[str, Any], run_kind: str, recursion_limit: int) -> dict[str, Any]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    kernel_projection = _graph_kernel_projection(thread)
    command_projection = _command_projection(thread)
    current_node = str(kernel_projection["current_node_id"])
    mapped_phase = str(kernel_projection["mapped_phase"])
    node_posture = str(kernel_projection["node_posture"])
    projected_node_path = [current_node] if current_node else []
    projected_phase_path = [mapped_phase] if mapped_phase else []

    if node_posture == "approval_wait":
        return {
            **metadata,
            "current_execution_node": current_node,
            "mapped_phase": mapped_phase,
            "projected_node_path": projected_node_path,
            "projected_phase_path": projected_phase_path,
            "planned_supersteps": 0,
            "stop_boundary": "interrupt_boundary",
            "terminal_reached": False,
            "recursion_limit_supported": True,
            "remaining_steps_supported": True,
            "recursion_limit": recursion_limit,
            "execution_posture": "interrupt_wait",
            "last_run_kind": run_kind,
            "last_run_status": "blocked",
            "last_run_reason": "approval_wait",
        }
    if node_posture == "recovery_pending_resume":
        return {
            **metadata,
            "current_execution_node": current_node,
            "mapped_phase": mapped_phase,
            "projected_node_path": projected_node_path,
            "projected_phase_path": projected_phase_path,
            "planned_supersteps": 0,
            "stop_boundary": "recovery_boundary",
            "terminal_reached": False,
            "recursion_limit_supported": True,
            "remaining_steps_supported": True,
            "recursion_limit": recursion_limit,
            "execution_posture": "recovery_wait",
            "last_run_kind": run_kind,
            "last_run_status": "blocked",
            "last_run_reason": "recovery_pending_resume",
        }
    if node_posture == "terminal":
        return {
            **metadata,
            "current_execution_node": current_node,
            "mapped_phase": mapped_phase,
            "projected_node_path": projected_node_path,
            "projected_phase_path": projected_phase_path,
            "planned_supersteps": 0,
            "stop_boundary": "terminal_boundary",
            "terminal_reached": True,
            "recursion_limit_supported": True,
            "remaining_steps_supported": True,
            "recursion_limit": recursion_limit,
            "execution_posture": "terminal",
            "last_run_kind": run_kind,
            "last_run_status": "noop",
            "last_run_reason": "terminal_state",
        }

    command_transition = str(command_projection.get("transition_kind", ""))
    command_target_phase = _command_target_phase(
        str(command_projection.get("parent_handoff_target", "")) or str(command_projection.get("goto_target", ""))
    )
    active_loop = str(thread.get("active_loop", ""))
    last_gate_verdict = str(thread.get("last_gate_verdict", ""))

    stop_boundary = "phase_boundary"
    last_run_reason = "projected_to_phase_boundary"

    if command_transition in {"goto", "update_goto", "parent_handoff", "resume_parent_handoff"} and command_target_phase:
        if command_target_phase not in projected_phase_path:
            projected_phase_path.append(command_target_phase)
        command_node = _phase_node_for_phase(command_target_phase)
        if command_node and command_node not in projected_node_path:
            projected_node_path.append(command_node)
        stop_boundary = "command_boundary"
        last_run_reason = f"command:{command_transition}->{command_target_phase}"
    elif mapped_phase in {"execute-parallel", "stabilize"} and last_gate_verdict == "revise":
        stop_boundary = "loop_boundary"
        last_run_reason = f"loop:{active_loop or mapped_phase}:revise"
        loop_node = _phase_node_for_phase(mapped_phase)
        if loop_node:
            projected_node_path.append(loop_node)
            if mapped_phase:
                projected_phase_path.append(mapped_phase)
    else:
        current_phase = mapped_phase
        visited_steps = 0
        while current_phase and visited_steps < recursion_limit:
            next_phase = _phase_successor(current_phase)
            if not next_phase:
                break
            current_phase = next_phase
            visited_steps += 1
            projected_phase_path.append(current_phase)
            next_node = _phase_node_for_phase(current_phase)
            if next_node:
                projected_node_path.append(next_node)
            if current_phase == "verify-accept":
                break
        if projected_phase_path and projected_phase_path[-1] != "verify-accept" and visited_steps >= recursion_limit:
            stop_boundary = "recursion_limit_boundary"
            last_run_reason = f"recursion_limit:{recursion_limit}"
        else:
            stop_boundary = "phase_boundary"
            last_run_reason = (
                f"projected:{projected_phase_path[0]}->{projected_phase_path[-1]}"
                if len(projected_phase_path) > 1
                else f"projected:{mapped_phase}"
            )

    planned_supersteps = max(0, len(projected_node_path) - 1)
    execution_posture = "projected" if LANGGRAPH_AVAILABLE else "unavailable"
    last_run_status = "ok" if LANGGRAPH_AVAILABLE else "unavailable"

    return {
        **metadata,
        "current_execution_node": current_node,
        "mapped_phase": mapped_phase,
        "projected_node_path": projected_node_path,
        "projected_phase_path": projected_phase_path,
        "planned_supersteps": planned_supersteps,
        "stop_boundary": stop_boundary,
        "terminal_reached": stop_boundary == "terminal_boundary",
        "recursion_limit_supported": True,
        "remaining_steps_supported": True,
        "recursion_limit": recursion_limit,
        "execution_posture": execution_posture,
        "last_run_kind": run_kind,
        "last_run_status": last_run_status,
        "last_run_reason": last_run_reason,
    }


def _build_deeper_live_primary_engine_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class DeeperEngineState(TypedDict, total=False):
            projected_node_path: list[str]
            projected_phase_path: list[str]
            stop_boundary: str
            terminal_reached: bool
            planned_supersteps: int
            recursion_limit: int

        def passthrough(state: DeeperEngineState) -> DeeperEngineState:
            return state

        builder = StateGraph(DeeperEngineState)
        builder.add_node("project", passthrough)
        builder.add_edge(START, "project")
        builder.add_edge("project", END)
        compiled = builder.compile()
        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return compiled, metadata
    except Exception as exc:  # pragma: no cover - only exercised when langgraph is installed
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_deeper_live_primary_engine(thread: dict[str, Any], run_kind: str, recursion_limit: int) -> dict[str, Any]:
    preview = _deeper_live_primary_engine_preview(thread, run_kind, recursion_limit)
    compiled, metadata = _build_deeper_live_primary_engine_graph()
    if compiled is None:
        unavailable_posture = (
            preview["execution_posture"] if preview["execution_posture"] in {"interrupt_wait", "recovery_wait", "terminal"} else "unavailable"
        )
        unavailable_status = (
            preview["last_run_status"] if preview["last_run_status"] in {"blocked", "noop"} else "unavailable"
        )
        return {
            **preview,
            **metadata,
            "execution_posture": unavailable_posture,
            "last_run_status": unavailable_status,
            "last_run_reason": metadata["compile_error"] or preview["last_run_reason"],
        }

    try:
        if run_kind == "stream":
            chunks = list(
                compiled.stream(
                    {
                        "projected_node_path": preview["projected_node_path"],
                        "projected_phase_path": preview["projected_phase_path"],
                        "stop_boundary": preview["stop_boundary"],
                        "terminal_reached": preview["terminal_reached"],
                        "planned_supersteps": preview["planned_supersteps"],
                        "recursion_limit": preview["recursion_limit"],
                    }
                )
            )
            output = chunks[-1] if chunks else {}
        else:
            output = compiled.invoke(
                {
                    "projected_node_path": preview["projected_node_path"],
                    "projected_phase_path": preview["projected_phase_path"],
                    "stop_boundary": preview["stop_boundary"],
                    "terminal_reached": preview["terminal_reached"],
                    "planned_supersteps": preview["planned_supersteps"],
                    "recursion_limit": preview["recursion_limit"],
                }
            )
        output_dict = output if isinstance(output, dict) else {}
        return {
            **metadata,
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "projected_node_path": list(output_dict.get("projected_node_path", preview["projected_node_path"])),
            "projected_phase_path": list(output_dict.get("projected_phase_path", preview["projected_phase_path"])),
            "planned_supersteps": int(output_dict.get("planned_supersteps", preview["planned_supersteps"])),
            "stop_boundary": str(output_dict.get("stop_boundary", preview["stop_boundary"])),
            "terminal_reached": bool(output_dict.get("terminal_reached", preview["terminal_reached"])),
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": int(output_dict.get("recursion_limit", preview["recursion_limit"])),
            "execution_posture": preview["execution_posture"] if preview["execution_posture"] != "ready" else "projected",
            "last_run_kind": run_kind,
            "last_run_status": "ok",
            "last_run_reason": preview["last_run_reason"],
        }
    except Exception as exc:  # pragma: no cover - only exercised when langgraph is installed
        return {
            **preview,
            **metadata,
            "execution_posture": "projection_failed",
            "last_run_status": "error",
            "last_run_reason": str(exc),
        }


def _deeper_live_primary_engine_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    state = thread.get("deeper_live_primary_engine_state")
    preview = _deeper_live_primary_engine_preview(
        thread,
        str(thread.get("last_deeper_live_primary_engine_kind", "")) or "invoke",
        int(thread.get("last_deeper_live_primary_engine_recursion_limit", 8) or 8),
    )
    helper_pointer: dict[str, Any] = {
        "command": "deeper-engine",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "engine_identity": _deeper_live_primary_engine_identity(),
            **preview,
        }

    return {
        "engine_identity": state.get("engine_identity", _deeper_live_primary_engine_identity()),
        "compile_supported": bool(state.get("compile_supported", preview["compile_supported"])),
        "compiled_graph_present": bool(state.get("compiled_graph_present", preview["compiled_graph_present"])),
        "invoke_supported": bool(state.get("invoke_supported", preview["invoke_supported"])),
        "stream_supported": bool(state.get("stream_supported", preview["stream_supported"])),
        "current_execution_node": str(state.get("current_execution_node", preview["current_execution_node"])),
        "mapped_phase": str(state.get("mapped_phase", preview["mapped_phase"])),
        "projected_node_path": list(state.get("projected_node_path", preview["projected_node_path"])),
        "projected_phase_path": list(state.get("projected_phase_path", preview["projected_phase_path"])),
        "planned_supersteps": int(state.get("planned_supersteps", preview["planned_supersteps"])),
        "stop_boundary": str(state.get("stop_boundary", preview["stop_boundary"])),
        "terminal_reached": bool(state.get("terminal_reached", preview["terminal_reached"])),
        "recursion_limit_supported": bool(state.get("recursion_limit_supported", preview["recursion_limit_supported"])),
        "remaining_steps_supported": bool(state.get("remaining_steps_supported", preview["remaining_steps_supported"])),
        "recursion_limit": int(state.get("recursion_limit", preview["recursion_limit"])),
        "execution_posture": str(state.get("execution_posture", preview["execution_posture"])),
        "last_run_kind": str(state.get("last_run_kind", preview["last_run_kind"])),
        "last_run_status": str(state.get("last_run_status", preview["last_run_status"])),
        "last_run_reason": str(state.get("last_run_reason", preview["last_run_reason"])),
        "helper_pointer": helper_pointer,
    }


def _persist_deeper_live_primary_engine_state(
    thread: dict[str, Any], run_kind: str = "", recursion_limit: int = 8
) -> dict[str, Any]:
    run_kind = run_kind or str(thread.get("last_deeper_live_primary_engine_kind", "")) or "invoke"
    recursion_limit = int(recursion_limit or thread.get("last_deeper_live_primary_engine_recursion_limit", 8) or 8)
    result = _execute_deeper_live_primary_engine(thread, run_kind, recursion_limit)
    stored = {
        "engine_identity": _deeper_live_primary_engine_identity(),
        "compile_supported": result["compile_supported"],
        "compiled_graph_present": result["compiled_graph_present"],
        "invoke_supported": result["invoke_supported"],
        "stream_supported": result["stream_supported"],
        "current_execution_node": result["current_execution_node"],
        "mapped_phase": result["mapped_phase"],
        "projected_node_path": result["projected_node_path"],
        "projected_phase_path": result["projected_phase_path"],
        "planned_supersteps": result["planned_supersteps"],
        "stop_boundary": result["stop_boundary"],
        "terminal_reached": result["terminal_reached"],
        "recursion_limit_supported": result["recursion_limit_supported"],
        "remaining_steps_supported": result["remaining_steps_supported"],
        "recursion_limit": result["recursion_limit"],
        "execution_posture": result["execution_posture"],
        "last_run_kind": result["last_run_kind"],
        "last_run_status": result["last_run_status"],
        "last_run_reason": result["last_run_reason"],
        "updated_at": _now(),
    }
    thread["last_deeper_live_primary_engine_kind"] = run_kind
    thread["last_deeper_live_primary_engine_reason"] = result["last_run_reason"]
    thread["last_deeper_live_primary_engine_recursion_limit"] = recursion_limit
    thread["deeper_live_primary_engine_state"] = stored
    return stored


def _superstep_live_primary_engine_identity() -> dict[str, Any]:
    return _clone_payload(SUPERSTEP_LIVE_PRIMARY_ENGINE_IDENTITY)


def _append_superstep_phase_visit(
    phase_visit_path: list[str], node_visit_path: list[str], phase_name: str
) -> None:
    if not phase_name:
        return
    phase_visit_path.append(phase_name)
    node_name = _phase_node_for_phase(phase_name)
    if node_name:
        node_visit_path.append(node_name)


def _superstep_live_primary_engine_trace(thread: dict[str, Any], recursion_limit: int) -> dict[str, Any]:
    kernel_projection = _graph_kernel_projection(thread)
    command_projection = _command_projection(thread)
    current_node = str(kernel_projection["current_node_id"])
    mapped_phase = str(kernel_projection["mapped_phase"])
    node_posture = str(kernel_projection["node_posture"])
    node_visit_path = [current_node] if current_node else []
    phase_visit_path = [mapped_phase] if mapped_phase else []

    if node_posture == "approval_wait":
        return {
            "current_execution_node": current_node,
            "mapped_phase": mapped_phase,
            "node_visit_path": node_visit_path,
            "phase_visit_path": phase_visit_path,
            "superstep_count": 0,
            "stop_boundary": "interrupt_boundary",
            "terminal_reached": False,
            "recursion_limit_supported": True,
            "remaining_steps_supported": True,
            "recursion_limit": recursion_limit,
            "last_run_reason": "approval_wait",
        }
    if node_posture == "recovery_pending_resume":
        return {
            "current_execution_node": current_node,
            "mapped_phase": mapped_phase,
            "node_visit_path": node_visit_path,
            "phase_visit_path": phase_visit_path,
            "superstep_count": 0,
            "stop_boundary": "recovery_boundary",
            "terminal_reached": False,
            "recursion_limit_supported": True,
            "remaining_steps_supported": True,
            "recursion_limit": recursion_limit,
            "last_run_reason": "recovery_pending_resume",
        }
    if node_posture == "terminal":
        return {
            "current_execution_node": current_node,
            "mapped_phase": mapped_phase,
            "node_visit_path": node_visit_path,
            "phase_visit_path": phase_visit_path,
            "superstep_count": 0,
            "stop_boundary": "terminal_boundary",
            "terminal_reached": True,
            "recursion_limit_supported": True,
            "remaining_steps_supported": True,
            "recursion_limit": recursion_limit,
            "last_run_reason": "terminal_state",
        }

    command_transition = str(command_projection.get("transition_kind", ""))
    command_target_phase = _command_target_phase(
        str(command_projection.get("parent_handoff_target", "")) or str(command_projection.get("goto_target", ""))
    )
    active_loop = str(thread.get("active_loop", ""))
    last_gate_verdict = str(thread.get("last_gate_verdict", ""))
    stop_boundary = "phase_boundary"
    last_run_reason = "projected_to_phase_boundary"

    if command_transition in {"goto", "update_goto", "parent_handoff", "resume_parent_handoff"} and command_target_phase:
        _append_superstep_phase_visit(phase_visit_path, node_visit_path, command_target_phase)
        stop_boundary = "command_boundary"
        last_run_reason = f"command:{command_transition}->{command_target_phase}"
    elif mapped_phase in {"execute-parallel", "stabilize"} and last_gate_verdict == "revise":
        _append_superstep_phase_visit(phase_visit_path, node_visit_path, mapped_phase)
        stop_boundary = "loop_boundary"
        last_run_reason = f"loop:{active_loop or mapped_phase}:revise"
    else:
        current_phase = mapped_phase
        visited_steps = 0
        while current_phase and visited_steps < recursion_limit:
            next_phase = _phase_successor(current_phase)
            if not next_phase:
                break
            current_phase = next_phase
            visited_steps += 1
            _append_superstep_phase_visit(phase_visit_path, node_visit_path, current_phase)
            if current_phase == "verify-accept":
                break
        if phase_visit_path and phase_visit_path[-1] != "verify-accept" and visited_steps >= recursion_limit:
            stop_boundary = "recursion_limit_boundary"
            last_run_reason = f"recursion_limit:{recursion_limit}"
        else:
            stop_boundary = "phase_boundary"
            last_run_reason = (
                f"superstep:{phase_visit_path[0]}->{phase_visit_path[-1]}"
                if len(phase_visit_path) > 1
                else f"superstep:{mapped_phase}"
            )

    return {
        "current_execution_node": current_node,
        "mapped_phase": mapped_phase,
        "node_visit_path": node_visit_path,
        "phase_visit_path": phase_visit_path,
        "superstep_count": max(0, len(node_visit_path) - 1),
        "stop_boundary": stop_boundary,
        "terminal_reached": stop_boundary == "terminal_boundary",
        "recursion_limit_supported": True,
        "remaining_steps_supported": True,
        "recursion_limit": recursion_limit,
        "last_run_reason": last_run_reason,
    }


def _superstep_live_primary_engine_preview(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    kernel_projection = _graph_kernel_projection(thread)
    node_posture = str(kernel_projection["node_posture"])
    trace = _superstep_live_primary_engine_trace(thread, recursion_limit)

    if node_posture == "approval_wait":
        return {
            **metadata,
            **trace,
            "execution_posture": "interrupt_wait",
            "last_run_kind": run_kind,
            "last_run_status": "blocked",
        }
    if node_posture == "recovery_pending_resume":
        return {
            **metadata,
            **trace,
            "execution_posture": "recovery_wait",
            "last_run_kind": run_kind,
            "last_run_status": "blocked",
        }
    if node_posture == "terminal":
        return {
            **metadata,
            **trace,
            "execution_posture": "terminal",
            "last_run_kind": run_kind,
            "last_run_status": "noop",
        }

    return {
        **metadata,
        **trace,
        "execution_posture": "ready" if LANGGRAPH_AVAILABLE else "unavailable",
        "last_run_kind": run_kind,
        "last_run_status": "planned" if not LANGGRAPH_AVAILABLE else "ok",
    }


def _build_superstep_live_primary_engine_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class SuperstepEngineState(TypedDict, total=False):
            remaining_node_path: list[str]
            node_visit_path: list[str]
            phase_visit_path: list[str]
            superstep_count: int
            stop_boundary: str
            terminal_reached: bool
            recursion_limit: int

        valid_nodes = _phase_node_names()

        def route_next(
            state: SuperstepEngineState,
        ) -> Literal[
            "define_target",
            "read_context",
            "freeze_plan",
            "execute_parallel",
            "integrate_converge",
            "stabilize",
            "verify_accept",
            "phase_end",
        ]:
            remaining = list(state.get("remaining_node_path", []))
            node_name = str(remaining[0]) if remaining else ""
            return node_name if node_name in valid_nodes else "phase_end"

        def make_phase_node(node_name: str, phase_name: str):
            def _node(state: SuperstepEngineState) -> SuperstepEngineState:
                remaining = list(state.get("remaining_node_path", []))
                node_visit_path = list(state.get("node_visit_path", []))
                phase_visit_path = list(state.get("phase_visit_path", []))
                node_visit_path.append(node_name)
                phase_visit_path.append(phase_name)
                if remaining:
                    remaining = remaining[1:]
                return {
                    "remaining_node_path": remaining,
                    "node_visit_path": node_visit_path,
                    "phase_visit_path": phase_visit_path,
                    "superstep_count": max(0, len(node_visit_path) - 1),
                    "stop_boundary": str(state.get("stop_boundary", "")),
                    "terminal_reached": bool(state.get("terminal_reached", False)),
                    "recursion_limit": int(state.get("recursion_limit", 0) or 0),
                }

            return _node

        def phase_end(state: SuperstepEngineState) -> SuperstepEngineState:
            return {
                "remaining_node_path": list(state.get("remaining_node_path", [])),
                "node_visit_path": list(state.get("node_visit_path", [])),
                "phase_visit_path": list(state.get("phase_visit_path", [])),
                "superstep_count": int(state.get("superstep_count", 0) or 0),
                "stop_boundary": str(state.get("stop_boundary", "")),
                "terminal_reached": bool(state.get("terminal_reached", False)),
                "recursion_limit": int(state.get("recursion_limit", 0) or 0),
            }

        builder = StateGraph(SuperstepEngineState)
        builder.add_node("route_next", lambda state: state)
        builder.add_node("phase_end", phase_end)
        builder.add_edge(START, "route_next")
        for node_name in valid_nodes:
            phase_name = str(GRAPH_KERNEL_NODES[node_name]["phase"])
            builder.add_node(node_name, make_phase_node(node_name, phase_name))
            builder.add_edge(node_name, "route_next")
        builder.add_conditional_edges("route_next", route_next)
        builder.add_edge("phase_end", END)
        compiled = builder.compile()
        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return compiled, metadata
    except Exception as exc:  # pragma: no cover - only exercised when langgraph is installed
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_superstep_live_primary_engine(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    preview = _superstep_live_primary_engine_preview(thread, run_kind, recursion_limit)
    compiled, metadata = _build_superstep_live_primary_engine_graph()
    if preview["execution_posture"] in {"interrupt_wait", "recovery_wait", "terminal"}:
        return {
            **preview,
            **metadata,
            "execution_posture": preview["execution_posture"],
            "last_run_kind": preview["last_run_kind"],
            "last_run_status": preview["last_run_status"],
            "last_run_reason": preview["last_run_reason"],
        }
    if compiled is None:
        return {
            **preview,
            **metadata,
            "execution_posture": "unavailable",
            "last_run_status": "unavailable",
            "last_run_reason": metadata["compile_error"] or preview["last_run_reason"],
        }

    try:
        input_payload = {
            "remaining_node_path": list(preview["node_visit_path"]),
            "node_visit_path": [],
            "phase_visit_path": [],
            "superstep_count": 0,
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit": preview["recursion_limit"],
        }
        if run_kind == "stream":
            chunks = list(compiled.stream(input_payload))
            output = chunks[-1] if chunks else {}
        else:
            output = compiled.invoke(input_payload)
        output_dict = output if isinstance(output, dict) else {}
        stop_boundary = str(output_dict.get("stop_boundary", preview["stop_boundary"]))
        return {
            **metadata,
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "node_visit_path": list(output_dict.get("node_visit_path", preview["node_visit_path"])),
            "phase_visit_path": list(output_dict.get("phase_visit_path", preview["phase_visit_path"])),
            "superstep_count": int(output_dict.get("superstep_count", preview["superstep_count"])),
            "stop_boundary": stop_boundary,
            "terminal_reached": bool(output_dict.get("terminal_reached", preview["terminal_reached"])),
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": int(output_dict.get("recursion_limit", preview["recursion_limit"])),
            "execution_posture": (
                "recursion_limited" if stop_boundary == "recursion_limit_boundary" else "executed"
            ),
            "last_run_kind": run_kind,
            "last_run_status": "ok",
            "last_run_reason": preview["last_run_reason"],
        }
    except Exception as exc:  # pragma: no cover - only exercised when langgraph is installed
        return {
            **preview,
            **metadata,
            "execution_posture": "execution_failed",
            "last_run_status": "error",
            "last_run_reason": str(exc),
        }


def _superstep_live_primary_engine_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    state = thread.get("superstep_live_primary_engine_state")
    preview = _superstep_live_primary_engine_preview(
        thread,
        str(thread.get("last_superstep_live_primary_engine_kind", "")) or "invoke",
        int(thread.get("last_superstep_live_primary_engine_recursion_limit", 8) or 8),
    )
    helper_pointer: dict[str, Any] = {
        "command": "superstep-engine",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "engine_identity": _superstep_live_primary_engine_identity(),
            **preview,
        }

    return {
        "engine_identity": state.get("engine_identity", _superstep_live_primary_engine_identity()),
        "compile_supported": bool(state.get("compile_supported", preview["compile_supported"])),
        "compiled_graph_present": bool(state.get("compiled_graph_present", preview["compiled_graph_present"])),
        "invoke_supported": bool(state.get("invoke_supported", preview["invoke_supported"])),
        "stream_supported": bool(state.get("stream_supported", preview["stream_supported"])),
        "current_execution_node": str(state.get("current_execution_node", preview["current_execution_node"])),
        "mapped_phase": str(state.get("mapped_phase", preview["mapped_phase"])),
        "node_visit_path": list(state.get("node_visit_path", preview["node_visit_path"])),
        "phase_visit_path": list(state.get("phase_visit_path", preview["phase_visit_path"])),
        "superstep_count": int(state.get("superstep_count", preview["superstep_count"])),
        "stop_boundary": str(state.get("stop_boundary", preview["stop_boundary"])),
        "terminal_reached": bool(state.get("terminal_reached", preview["terminal_reached"])),
        "recursion_limit_supported": bool(
            state.get("recursion_limit_supported", preview["recursion_limit_supported"])
        ),
        "remaining_steps_supported": bool(
            state.get("remaining_steps_supported", preview["remaining_steps_supported"])
        ),
        "recursion_limit": int(state.get("recursion_limit", preview["recursion_limit"])),
        "execution_posture": str(state.get("execution_posture", preview["execution_posture"])),
        "last_run_kind": str(state.get("last_run_kind", preview["last_run_kind"])),
        "last_run_status": str(state.get("last_run_status", preview["last_run_status"])),
        "last_run_reason": str(state.get("last_run_reason", preview["last_run_reason"])),
        "helper_pointer": helper_pointer,
    }


def _persist_superstep_live_primary_engine_state(
    thread: dict[str, Any], run_kind: str = "", recursion_limit: int = 8
) -> dict[str, Any]:
    run_kind = run_kind or str(thread.get("last_superstep_live_primary_engine_kind", "")) or "invoke"
    recursion_limit = int(
        recursion_limit or thread.get("last_superstep_live_primary_engine_recursion_limit", 8) or 8
    )
    result = _execute_superstep_live_primary_engine(thread, run_kind, recursion_limit)
    stored = {
        "engine_identity": _superstep_live_primary_engine_identity(),
        "compile_supported": result["compile_supported"],
        "compiled_graph_present": result["compiled_graph_present"],
        "invoke_supported": result["invoke_supported"],
        "stream_supported": result["stream_supported"],
        "current_execution_node": result["current_execution_node"],
        "mapped_phase": result["mapped_phase"],
        "node_visit_path": result["node_visit_path"],
        "phase_visit_path": result["phase_visit_path"],
        "superstep_count": result["superstep_count"],
        "stop_boundary": result["stop_boundary"],
        "terminal_reached": result["terminal_reached"],
        "recursion_limit_supported": result["recursion_limit_supported"],
        "remaining_steps_supported": result["remaining_steps_supported"],
        "recursion_limit": result["recursion_limit"],
        "execution_posture": result["execution_posture"],
        "last_run_kind": result["last_run_kind"],
        "last_run_status": result["last_run_status"],
        "last_run_reason": result["last_run_reason"],
        "updated_at": _now(),
    }
    thread["last_superstep_live_primary_engine_kind"] = run_kind
    thread["last_superstep_live_primary_engine_reason"] = result["last_run_reason"]
    thread["last_superstep_live_primary_engine_recursion_limit"] = recursion_limit
    thread["superstep_live_primary_engine_state"] = stored
    return stored


def _stateful_live_primary_engine_identity() -> dict[str, Any]:
    return _clone_payload(STATEFUL_LIVE_PRIMARY_ENGINE_IDENTITY)


def _stateful_live_primary_engine_visit_phase(
    state: dict[str, Any], node_name: str, phase_name: str
) -> dict[str, Any]:
    node_path = list(state.get("stateful_node_path", []))
    phase_path = list(state.get("stateful_phase_path", []))
    node_path.append(node_name)
    phase_path.append(phase_name)
    state["current_execution_node"] = node_name
    state["mapped_phase"] = phase_name
    state["stateful_node_path"] = node_path
    state["stateful_phase_path"] = phase_path
    state["superstep_count"] = max(0, len(node_path) - 1)
    return state


def _stateful_live_primary_engine_initial_state(thread: dict[str, Any], recursion_limit: int) -> dict[str, Any]:
    kernel_projection = _graph_kernel_projection(thread)
    command_projection = _command_projection(thread)
    return {
        "current_execution_node": str(kernel_projection["current_node_id"]),
        "mapped_phase": str(kernel_projection["mapped_phase"]),
        "stateful_node_path": [],
        "stateful_phase_path": [],
        "stateful_transition_log": [],
        "superstep_count": 0,
        "next_execution_node": "",
        "stop_boundary": "",
        "terminal_reached": False,
        "recursion_limit_supported": True,
        "remaining_steps_supported": True,
        "recursion_limit": recursion_limit,
        "command_transition": str(command_projection.get("transition_kind", "")),
        "command_target_phase": _command_target_phase(
            str(command_projection.get("parent_handoff_target", "")) or str(command_projection.get("goto_target", ""))
        ),
        "active_loop": str(thread.get("active_loop", "")),
        "last_gate_verdict": str(thread.get("last_gate_verdict", "")),
        "command_consumed": False,
        "loop_consumed": False,
        "boundary_pending": False,
        "boundary_kind": "",
        "last_run_reason": "",
    }


def _stateful_live_primary_engine_decide_next(state: dict[str, Any]) -> dict[str, Any]:
    current_phase = str(state.get("mapped_phase", ""))
    current_node = str(state.get("current_execution_node", ""))
    transition_log = list(state.get("stateful_transition_log", []))
    recursion_limit = int(state.get("recursion_limit", 0) or 0)
    superstep_count = int(state.get("superstep_count", 0) or 0)
    boundary_pending = bool(state.get("boundary_pending", False))

    if boundary_pending:
        state["next_execution_node"] = "phase_end"
        state["stop_boundary"] = str(state.get("boundary_kind", ""))
        state["boundary_pending"] = False
        state["boundary_kind"] = ""
        state["last_run_reason"] = transition_log[-1] if transition_log else str(state.get("stop_boundary", ""))
        return state

    if current_phase == "verify-accept":
        transition_log.append("boundary:phase_boundary:verify-accept")
        state["stateful_transition_log"] = transition_log
        state["next_execution_node"] = "phase_end"
        state["stop_boundary"] = "phase_boundary"
        state["last_run_reason"] = "stateful:verify-accept"
        return state

    if current_phase and recursion_limit and superstep_count >= recursion_limit:
        transition_log.append(f"boundary:recursion_limit:{recursion_limit}")
        state["stateful_transition_log"] = transition_log
        state["next_execution_node"] = "phase_end"
        state["stop_boundary"] = "recursion_limit_boundary"
        state["last_run_reason"] = f"stateful:recursion_limit:{recursion_limit}"
        return state

    command_transition = str(state.get("command_transition", ""))
    command_target_phase = str(state.get("command_target_phase", ""))
    if (
        command_transition in {"goto", "update_goto", "parent_handoff", "resume_parent_handoff"}
        and command_target_phase
        and not bool(state.get("command_consumed", False))
    ):
        target_node = _phase_node_for_phase(command_target_phase)
        transition_log.append(f"command:{command_transition}->{command_target_phase}")
        state["stateful_transition_log"] = transition_log
        state["next_execution_node"] = target_node or "phase_end"
        state["boundary_pending"] = True
        state["boundary_kind"] = "command_boundary"
        state["command_consumed"] = True
        state["last_run_reason"] = transition_log[-1]
        return state

    if current_phase in {"execute-parallel", "stabilize"} and str(state.get("last_gate_verdict", "")) == "revise" and not bool(
        state.get("loop_consumed", False)
    ):
        transition_log.append(f"loop:{str(state.get('active_loop', '')) or current_phase}:revise")
        state["stateful_transition_log"] = transition_log
        state["next_execution_node"] = current_node or "phase_end"
        state["boundary_pending"] = True
        state["boundary_kind"] = "loop_boundary"
        state["loop_consumed"] = True
        state["last_run_reason"] = transition_log[-1]
        return state

    successor = _phase_successor(current_phase)
    if successor:
        target_node = _phase_node_for_phase(successor)
        transition_log.append(f"sequential:{current_phase}->{successor}")
        state["stateful_transition_log"] = transition_log
        state["next_execution_node"] = target_node or "phase_end"
        state["stop_boundary"] = "phase_boundary"
        state["last_run_reason"] = transition_log[-1]
        return state

    transition_log.append(f"boundary:phase_boundary:{current_phase or current_node}")
    state["stateful_transition_log"] = transition_log
    state["next_execution_node"] = "phase_end"
    state["stop_boundary"] = "phase_boundary"
    state["last_run_reason"] = transition_log[-1]
    return state


def _stateful_live_primary_engine_terminal_projection(thread: dict[str, Any], recursion_limit: int) -> dict[str, Any] | None:
    kernel_projection = _graph_kernel_projection(thread)
    current_node = str(kernel_projection["current_node_id"])
    mapped_phase = str(kernel_projection["mapped_phase"])
    node_posture = str(kernel_projection["node_posture"])
    node_path = [current_node] if current_node else []
    phase_path = [mapped_phase] if mapped_phase else []
    base = {
        "current_execution_node": current_node,
        "mapped_phase": mapped_phase,
        "stateful_node_path": node_path,
        "stateful_phase_path": phase_path,
        "stateful_transition_log": [],
        "superstep_count": 0,
        "terminal_reached": False,
        "recursion_limit_supported": True,
        "remaining_steps_supported": True,
        "recursion_limit": recursion_limit,
    }
    if node_posture == "approval_wait":
        return {
            **base,
            "stop_boundary": "interrupt_boundary",
            "terminal_reached": False,
            "last_run_reason": "approval_wait",
        }
    if node_posture == "recovery_pending_resume":
        return {
            **base,
            "stop_boundary": "recovery_boundary",
            "terminal_reached": False,
            "last_run_reason": "recovery_pending_resume",
        }
    if node_posture == "terminal":
        return {
            **base,
            "stop_boundary": "terminal_boundary",
            "terminal_reached": True,
            "last_run_reason": "terminal_state",
        }
    return None


def _stateful_live_primary_engine_preview(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    terminal_projection = _stateful_live_primary_engine_terminal_projection(thread, recursion_limit)
    if terminal_projection is not None:
        posture_map = {
            "interrupt_boundary": ("interrupt_wait", "blocked"),
            "recovery_boundary": ("recovery_wait", "blocked"),
            "terminal_boundary": ("terminal", "noop"),
        }
        execution_posture, last_run_status = posture_map[str(terminal_projection["stop_boundary"])]
        return {
            **metadata,
            **terminal_projection,
            "execution_posture": execution_posture,
            "last_run_kind": run_kind,
            "last_run_status": last_run_status,
        }

    state = _stateful_live_primary_engine_initial_state(thread, recursion_limit)
    current_node = str(state.get("current_execution_node", ""))
    if current_node:
        state = _stateful_live_primary_engine_visit_phase(
            state,
            current_node,
            str(state.get("mapped_phase", "")),
        )

    while True:
        state = _stateful_live_primary_engine_decide_next(state)
        next_node = str(state.get("next_execution_node", ""))
        if next_node in {"", "phase_end"}:
            break
        next_phase = str(GRAPH_KERNEL_NODES.get(next_node, {}).get("phase", ""))
        state = _stateful_live_primary_engine_visit_phase(state, next_node, next_phase)

    return {
        **metadata,
        "current_execution_node": str(state.get("current_execution_node", "")),
        "mapped_phase": str(state.get("mapped_phase", "")),
        "stateful_node_path": list(state.get("stateful_node_path", [])),
        "stateful_phase_path": list(state.get("stateful_phase_path", [])),
        "stateful_transition_log": list(state.get("stateful_transition_log", [])),
        "superstep_count": int(state.get("superstep_count", 0) or 0),
        "stop_boundary": str(state.get("stop_boundary", "")),
        "terminal_reached": bool(state.get("terminal_reached", False)),
        "recursion_limit_supported": bool(state.get("recursion_limit_supported", True)),
        "remaining_steps_supported": bool(state.get("remaining_steps_supported", True)),
        "recursion_limit": int(state.get("recursion_limit", recursion_limit) or recursion_limit),
        "execution_posture": "ready" if LANGGRAPH_AVAILABLE else "unavailable",
        "last_run_kind": run_kind,
        "last_run_status": "planned" if not LANGGRAPH_AVAILABLE else "ok",
        "last_run_reason": str(state.get("last_run_reason", "")),
    }


def _build_stateful_live_primary_engine_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class StatefulEngineState(TypedDict, total=False):
            current_execution_node: str
            mapped_phase: str
            stateful_node_path: list[str]
            stateful_phase_path: list[str]
            stateful_transition_log: list[str]
            superstep_count: int
            next_execution_node: str
            stop_boundary: str
            terminal_reached: bool
            recursion_limit_supported: bool
            remaining_steps_supported: bool
            recursion_limit: int
            command_transition: str
            command_target_phase: str
            active_loop: str
            last_gate_verdict: str
            command_consumed: bool
            loop_consumed: bool
            boundary_pending: bool
            boundary_kind: str
            last_run_reason: str

        valid_nodes = _phase_node_names()

        def route_current(
            state: StatefulEngineState,
        ) -> Literal[
            "define_target",
            "read_context",
            "freeze_plan",
            "execute_parallel",
            "integrate_converge",
            "stabilize",
            "verify_accept",
            "phase_end",
        ]:
            node_name = str(state.get("current_execution_node", ""))
            return node_name if node_name in valid_nodes else "phase_end"

        def route_next(
            state: StatefulEngineState,
        ) -> Literal[
            "define_target",
            "read_context",
            "freeze_plan",
            "execute_parallel",
            "integrate_converge",
            "stabilize",
            "verify_accept",
            "phase_end",
        ]:
            node_name = str(state.get("next_execution_node", ""))
            return node_name if node_name in valid_nodes else "phase_end"

        def make_phase_node(node_name: str, phase_name: str):
            def _node(state: StatefulEngineState) -> StatefulEngineState:
                return _stateful_live_primary_engine_visit_phase(dict(state), node_name, phase_name)

            return _node

        def decide_next(state: StatefulEngineState) -> StatefulEngineState:
            return _stateful_live_primary_engine_decide_next(dict(state))

        def phase_end(state: StatefulEngineState) -> StatefulEngineState:
            return state

        builder = StateGraph(StatefulEngineState)
        builder.add_node("route_current", lambda state: state)
        builder.add_node("decide_next", decide_next)
        builder.add_node("phase_end", phase_end)
        builder.add_edge(START, "route_current")
        for node_name in valid_nodes:
            phase_name = str(GRAPH_KERNEL_NODES[node_name]["phase"])
            builder.add_node(node_name, make_phase_node(node_name, phase_name))
            builder.add_edge(node_name, "decide_next")
        builder.add_conditional_edges("route_current", route_current)
        builder.add_conditional_edges("decide_next", route_next)
        builder.add_edge("phase_end", END)
        compiled = builder.compile()
        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return compiled, metadata
    except Exception as exc:  # pragma: no cover - only exercised when langgraph is installed
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_stateful_live_primary_engine(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    preview = _stateful_live_primary_engine_preview(thread, run_kind, recursion_limit)
    compiled, metadata = _build_stateful_live_primary_engine_graph()
    if preview["execution_posture"] in {"interrupt_wait", "recovery_wait", "terminal"}:
        return {
            **preview,
            **metadata,
            "execution_posture": preview["execution_posture"],
            "last_run_kind": preview["last_run_kind"],
            "last_run_status": preview["last_run_status"],
            "last_run_reason": preview["last_run_reason"],
        }
    if compiled is None:
        return {
            **preview,
            **metadata,
            "execution_posture": "unavailable",
            "last_run_status": "unavailable",
            "last_run_reason": metadata["compile_error"] or preview["last_run_reason"],
        }

    try:
        input_payload = _stateful_live_primary_engine_initial_state(thread, recursion_limit)
        if run_kind == "stream":
            chunks = list(compiled.stream(input_payload))
            output = chunks[-1] if chunks else {}
        else:
            output = compiled.invoke(input_payload)
        output_dict = output if isinstance(output, dict) else {}
        stop_boundary = str(output_dict.get("stop_boundary", preview["stop_boundary"]))
        return {
            **metadata,
            "current_execution_node": str(output_dict.get("current_execution_node", preview["current_execution_node"])),
            "mapped_phase": str(output_dict.get("mapped_phase", preview["mapped_phase"])),
            "stateful_node_path": list(output_dict.get("stateful_node_path", preview["stateful_node_path"])),
            "stateful_phase_path": list(output_dict.get("stateful_phase_path", preview["stateful_phase_path"])),
            "stateful_transition_log": list(
                output_dict.get("stateful_transition_log", preview["stateful_transition_log"])
            ),
            "superstep_count": int(output_dict.get("superstep_count", preview["superstep_count"])),
            "stop_boundary": stop_boundary,
            "terminal_reached": bool(output_dict.get("terminal_reached", preview["terminal_reached"])),
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": int(output_dict.get("recursion_limit", preview["recursion_limit"])),
            "execution_posture": (
                "recursion_limited" if stop_boundary == "recursion_limit_boundary" else "executed"
            ),
            "last_run_kind": run_kind,
            "last_run_status": "ok",
            "last_run_reason": str(output_dict.get("last_run_reason", preview["last_run_reason"])),
        }
    except Exception as exc:  # pragma: no cover - only exercised when langgraph is installed
        return {
            **preview,
            **metadata,
            "execution_posture": "execution_failed",
            "last_run_status": "error",
            "last_run_reason": str(exc),
        }


def _stateful_live_primary_engine_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    state = thread.get("stateful_live_primary_engine_state")
    preview = _stateful_live_primary_engine_preview(
        thread,
        str(thread.get("last_stateful_live_primary_engine_kind", "")) or "invoke",
        int(thread.get("last_stateful_live_primary_engine_recursion_limit", 8) or 8),
    )
    helper_pointer: dict[str, Any] = {
        "command": "stateful-engine",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "engine_identity": _stateful_live_primary_engine_identity(),
            **preview,
        }

    return {
        "engine_identity": state.get("engine_identity", _stateful_live_primary_engine_identity()),
        "compile_supported": bool(state.get("compile_supported", preview["compile_supported"])),
        "compiled_graph_present": bool(state.get("compiled_graph_present", preview["compiled_graph_present"])),
        "invoke_supported": bool(state.get("invoke_supported", preview["invoke_supported"])),
        "stream_supported": bool(state.get("stream_supported", preview["stream_supported"])),
        "current_execution_node": str(state.get("current_execution_node", preview["current_execution_node"])),
        "mapped_phase": str(state.get("mapped_phase", preview["mapped_phase"])),
        "stateful_node_path": list(state.get("stateful_node_path", preview["stateful_node_path"])),
        "stateful_phase_path": list(state.get("stateful_phase_path", preview["stateful_phase_path"])),
        "stateful_transition_log": list(
            state.get("stateful_transition_log", preview["stateful_transition_log"])
        ),
        "superstep_count": int(state.get("superstep_count", preview["superstep_count"])),
        "stop_boundary": str(state.get("stop_boundary", preview["stop_boundary"])),
        "terminal_reached": bool(state.get("terminal_reached", preview["terminal_reached"])),
        "recursion_limit_supported": bool(
            state.get("recursion_limit_supported", preview["recursion_limit_supported"])
        ),
        "remaining_steps_supported": bool(
            state.get("remaining_steps_supported", preview["remaining_steps_supported"])
        ),
        "recursion_limit": int(state.get("recursion_limit", preview["recursion_limit"])),
        "execution_posture": str(state.get("execution_posture", preview["execution_posture"])),
        "last_run_kind": str(state.get("last_run_kind", preview["last_run_kind"])),
        "last_run_status": str(state.get("last_run_status", preview["last_run_status"])),
        "last_run_reason": str(state.get("last_run_reason", preview["last_run_reason"])),
        "helper_pointer": helper_pointer,
    }


def _persist_stateful_live_primary_engine_state(
    thread: dict[str, Any], run_kind: str = "", recursion_limit: int = 8
) -> dict[str, Any]:
    run_kind = run_kind or str(thread.get("last_stateful_live_primary_engine_kind", "")) or "invoke"
    recursion_limit = int(
        recursion_limit or thread.get("last_stateful_live_primary_engine_recursion_limit", 8) or 8
    )
    result = _execute_stateful_live_primary_engine(thread, run_kind, recursion_limit)
    stored = {
        "engine_identity": _stateful_live_primary_engine_identity(),
        "compile_supported": result["compile_supported"],
        "compiled_graph_present": result["compiled_graph_present"],
        "invoke_supported": result["invoke_supported"],
        "stream_supported": result["stream_supported"],
        "current_execution_node": result["current_execution_node"],
        "mapped_phase": result["mapped_phase"],
        "stateful_node_path": result["stateful_node_path"],
        "stateful_phase_path": result["stateful_phase_path"],
        "stateful_transition_log": result["stateful_transition_log"],
        "superstep_count": result["superstep_count"],
        "stop_boundary": result["stop_boundary"],
        "terminal_reached": result["terminal_reached"],
        "recursion_limit_supported": result["recursion_limit_supported"],
        "remaining_steps_supported": result["remaining_steps_supported"],
        "recursion_limit": result["recursion_limit"],
        "execution_posture": result["execution_posture"],
        "last_run_kind": result["last_run_kind"],
        "last_run_status": result["last_run_status"],
        "last_run_reason": result["last_run_reason"],
        "updated_at": _now(),
    }
    thread["last_stateful_live_primary_engine_kind"] = run_kind
    thread["last_stateful_live_primary_engine_reason"] = result["last_run_reason"]
    thread["last_stateful_live_primary_engine_recursion_limit"] = recursion_limit
    thread["stateful_live_primary_engine_state"] = stored
    return stored


def _boundary_state_live_primary_engine_identity() -> dict[str, Any]:
    return _clone_payload(BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_IDENTITY)


def _boundary_state_live_primary_engine_append_visit(
    state: dict[str, Any], node_name: str, phase_name: str = ""
) -> dict[str, Any]:
    node_path = list(state.get("boundary_node_path", []))
    phase_path = list(state.get("boundary_phase_path", []))
    transition_log = list(state.get("boundary_transition_log", []))
    node_path.append(node_name)
    if phase_name:
        phase_path.append(phase_name)
        state["mapped_phase"] = phase_name
    state["current_execution_node"] = node_name
    state["boundary_node_path"] = node_path
    state["boundary_phase_path"] = phase_path
    state["boundary_transition_log"] = transition_log
    state["superstep_count"] = max(0, len(node_path) - 1)
    return state


def _boundary_state_live_primary_engine_initial_state(thread: dict[str, Any], recursion_limit: int) -> dict[str, Any]:
    kernel_projection = _graph_kernel_projection(thread)
    command_projection = _command_projection(thread)
    return {
        "current_execution_node": str(kernel_projection["current_node_id"]),
        "mapped_phase": str(kernel_projection["mapped_phase"]),
        "boundary_node_path": [],
        "boundary_phase_path": [],
        "boundary_transition_log": [],
        "boundary_state_kind": "ordinary",
        "superstep_count": 0,
        "next_execution_node": "",
        "stop_boundary": "",
        "terminal_reached": False,
        "recursion_limit_supported": True,
        "remaining_steps_supported": True,
        "recursion_limit": recursion_limit,
        "command_transition": str(command_projection.get("transition_kind", "")),
        "command_target_phase": _command_target_phase(
            str(command_projection.get("parent_handoff_target", "")) or str(command_projection.get("goto_target", ""))
        ),
        "active_loop": str(thread.get("active_loop", "")),
        "last_gate_verdict": str(thread.get("last_gate_verdict", "")),
        "command_consumed": False,
        "loop_consumed": False,
        "boundary_pending": False,
        "boundary_kind": "",
        "last_run_reason": "",
    }


def _boundary_state_live_primary_engine_visit_node(state: dict[str, Any], node_name: str) -> dict[str, Any]:
    node = GRAPH_KERNEL_NODES.get(node_name, {})
    phase_name = str(node.get("phase", "")) or str(state.get("mapped_phase", ""))
    node_kind = str(node.get("node_kind", ""))
    state = _boundary_state_live_primary_engine_append_visit(
        state,
        node_name,
        phase_name if node_kind == "phase" else phase_name,
    )
    transition_log = list(state.get("boundary_transition_log", []))

    if node_name == "approval_wait":
        transition_log.append(f"boundary:interrupt:{phase_name}")
        state["boundary_transition_log"] = transition_log
        state["boundary_state_kind"] = "interrupt"
        state["stop_boundary"] = "interrupt_boundary"
        state["next_execution_node"] = "phase_end"
        state["last_run_reason"] = transition_log[-1]
        return state
    if node_name == "recovery_pending_resume":
        transition_log.append(f"boundary:recovery:{phase_name}")
        state["boundary_transition_log"] = transition_log
        state["boundary_state_kind"] = "recovery"
        state["stop_boundary"] = "recovery_boundary"
        state["next_execution_node"] = "phase_end"
        state["last_run_reason"] = transition_log[-1]
        return state
    if node_name in {"accepted_terminal", "halted_terminal", "escalated_terminal"}:
        transition_log.append(f"boundary:terminal:{node_name}")
        state["boundary_transition_log"] = transition_log
        state["boundary_state_kind"] = "terminal"
        state["stop_boundary"] = "terminal_boundary"
        state["terminal_reached"] = True
        state["next_execution_node"] = "phase_end"
        state["last_run_reason"] = transition_log[-1]
        return state

    state["boundary_state_kind"] = "ordinary"
    return state


def _boundary_state_live_primary_engine_decide_next(state: dict[str, Any]) -> dict[str, Any]:
    current_phase = str(state.get("mapped_phase", ""))
    current_node = str(state.get("current_execution_node", ""))
    transition_log = list(state.get("boundary_transition_log", []))
    recursion_limit = int(state.get("recursion_limit", 0) or 0)
    superstep_count = int(state.get("superstep_count", 0) or 0)
    boundary_pending = bool(state.get("boundary_pending", False))

    if boundary_pending:
        state["next_execution_node"] = "phase_end"
        state["stop_boundary"] = str(state.get("boundary_kind", ""))
        state["boundary_pending"] = False
        state["boundary_kind"] = ""
        state["last_run_reason"] = transition_log[-1] if transition_log else str(state.get("stop_boundary", ""))
        return state

    if current_phase == "verify-accept":
        transition_log.append("boundary:phase_boundary:verify-accept")
        state["boundary_transition_log"] = transition_log
        state["next_execution_node"] = "phase_end"
        state["stop_boundary"] = "phase_boundary"
        state["last_run_reason"] = "boundary-engine:verify-accept"
        return state

    if current_phase and recursion_limit and superstep_count >= recursion_limit:
        transition_log.append(f"boundary:recursion_limit:{recursion_limit}")
        state["boundary_transition_log"] = transition_log
        state["next_execution_node"] = "phase_end"
        state["stop_boundary"] = "recursion_limit_boundary"
        state["last_run_reason"] = f"boundary-engine:recursion_limit:{recursion_limit}"
        return state

    command_transition = str(state.get("command_transition", ""))
    command_target_phase = str(state.get("command_target_phase", ""))
    if (
        command_transition in {"goto", "update_goto", "parent_handoff", "resume_parent_handoff"}
        and command_target_phase
        and not bool(state.get("command_consumed", False))
    ):
        target_node = _phase_node_for_phase(command_target_phase)
        transition_log.append(f"command:{command_transition}->{command_target_phase}")
        state["boundary_transition_log"] = transition_log
        state["next_execution_node"] = target_node or "phase_end"
        state["boundary_pending"] = True
        state["boundary_kind"] = "command_boundary"
        state["command_consumed"] = True
        state["last_run_reason"] = transition_log[-1]
        return state

    if current_phase in {"execute-parallel", "stabilize"} and str(state.get("last_gate_verdict", "")) == "revise" and not bool(
        state.get("loop_consumed", False)
    ):
        transition_log.append(f"loop:{str(state.get('active_loop', '')) or current_phase}:revise")
        state["boundary_transition_log"] = transition_log
        state["next_execution_node"] = current_node or "phase_end"
        state["boundary_pending"] = True
        state["boundary_kind"] = "loop_boundary"
        state["loop_consumed"] = True
        state["last_run_reason"] = transition_log[-1]
        return state

    successor = _phase_successor(current_phase)
    if successor:
        target_node = _phase_node_for_phase(successor)
        transition_log.append(f"sequential:{current_phase}->{successor}")
        state["boundary_transition_log"] = transition_log
        state["next_execution_node"] = target_node or "phase_end"
        state["stop_boundary"] = "phase_boundary"
        state["last_run_reason"] = transition_log[-1]
        return state

    transition_log.append(f"boundary:phase_boundary:{current_phase or current_node}")
    state["boundary_transition_log"] = transition_log
    state["next_execution_node"] = "phase_end"
    state["stop_boundary"] = "phase_boundary"
    state["last_run_reason"] = transition_log[-1]
    return state


def _boundary_state_live_primary_engine_preview(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    state = _boundary_state_live_primary_engine_initial_state(thread, recursion_limit)
    current_node = str(state.get("current_execution_node", ""))
    if current_node:
        state = _boundary_state_live_primary_engine_visit_node(state, current_node)
        if current_node not in {"approval_wait", "recovery_pending_resume", "accepted_terminal", "halted_terminal", "escalated_terminal"}:
            while True:
                state = _boundary_state_live_primary_engine_decide_next(state)
                next_node = str(state.get("next_execution_node", ""))
                if next_node in {"", "phase_end"}:
                    break
                state = _boundary_state_live_primary_engine_visit_node(state, next_node)

    posture_map = {
        "interrupt_boundary": ("interrupt_wait", "blocked"),
        "recovery_boundary": ("recovery_wait", "blocked"),
        "terminal_boundary": ("terminal", "noop"),
        "recursion_limit_boundary": ("recursion_limited", "ok"),
        "phase_boundary": ("ready" if LANGGRAPH_AVAILABLE else "unavailable", "planned" if not LANGGRAPH_AVAILABLE else "ok"),
        "command_boundary": ("ready" if LANGGRAPH_AVAILABLE else "unavailable", "planned" if not LANGGRAPH_AVAILABLE else "ok"),
        "loop_boundary": ("ready" if LANGGRAPH_AVAILABLE else "unavailable", "planned" if not LANGGRAPH_AVAILABLE else "ok"),
        "": ("ready" if LANGGRAPH_AVAILABLE else "unavailable", "planned" if not LANGGRAPH_AVAILABLE else "ok"),
    }
    execution_posture, last_run_status = posture_map[str(state.get("stop_boundary", ""))]
    return {
        **metadata,
        "current_execution_node": str(state.get("current_execution_node", "")),
        "mapped_phase": str(state.get("mapped_phase", "")),
        "boundary_node_path": list(state.get("boundary_node_path", [])),
        "boundary_phase_path": list(state.get("boundary_phase_path", [])),
        "boundary_transition_log": list(state.get("boundary_transition_log", [])),
        "boundary_state_kind": str(state.get("boundary_state_kind", "ordinary")),
        "superstep_count": int(state.get("superstep_count", 0) or 0),
        "stop_boundary": str(state.get("stop_boundary", "")),
        "terminal_reached": bool(state.get("terminal_reached", False)),
        "recursion_limit_supported": bool(state.get("recursion_limit_supported", True)),
        "remaining_steps_supported": bool(state.get("remaining_steps_supported", True)),
        "recursion_limit": int(state.get("recursion_limit", recursion_limit) or recursion_limit),
        "execution_posture": execution_posture,
        "last_run_kind": run_kind,
        "last_run_status": last_run_status,
        "last_run_reason": str(state.get("last_run_reason", "")),
    }


def _build_boundary_state_live_primary_engine_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class BoundaryEngineState(TypedDict, total=False):
            current_execution_node: str
            mapped_phase: str
            boundary_node_path: list[str]
            boundary_phase_path: list[str]
            boundary_transition_log: list[str]
            boundary_state_kind: str
            superstep_count: int
            next_execution_node: str
            stop_boundary: str
            terminal_reached: bool
            recursion_limit_supported: bool
            remaining_steps_supported: bool
            recursion_limit: int
            command_transition: str
            command_target_phase: str
            active_loop: str
            last_gate_verdict: str
            command_consumed: bool
            loop_consumed: bool
            boundary_pending: bool
            boundary_kind: str
            last_run_reason: str

        valid_nodes = [str(node_name) for node_name in GRAPH_KERNEL_NODES.keys()]

        def route_current(state: BoundaryEngineState) -> str:
            node_name = str(state.get("current_execution_node", ""))
            return node_name if node_name in valid_nodes else "phase_end"

        def route_next(state: BoundaryEngineState) -> str:
            node_name = str(state.get("next_execution_node", ""))
            return node_name if node_name in valid_nodes else "phase_end"

        def make_node(node_name: str):
            def _node(state: BoundaryEngineState) -> BoundaryEngineState:
                return _boundary_state_live_primary_engine_visit_node(dict(state), node_name)

            return _node

        def decide_next(state: BoundaryEngineState) -> BoundaryEngineState:
            return _boundary_state_live_primary_engine_decide_next(dict(state))

        def phase_end(state: BoundaryEngineState) -> BoundaryEngineState:
            return state

        builder = StateGraph(BoundaryEngineState)
        builder.add_node("route_current", lambda state: state)
        builder.add_node("decide_next", decide_next)
        builder.add_node("phase_end", phase_end)
        builder.add_edge(START, "route_current")
        for node_name in valid_nodes:
            builder.add_node(node_name, make_node(node_name))
            if str(GRAPH_KERNEL_NODES[node_name].get("node_kind", "")) == "phase":
                builder.add_edge(node_name, "decide_next")
            else:
                builder.add_edge(node_name, "phase_end")
        builder.add_conditional_edges("route_current", route_current)
        builder.add_conditional_edges("decide_next", route_next)
        builder.add_edge("phase_end", END)
        compiled = builder.compile()
        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return compiled, metadata
    except Exception as exc:  # pragma: no cover
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_boundary_state_live_primary_engine(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    preview = _boundary_state_live_primary_engine_preview(thread, run_kind, recursion_limit)
    compiled, metadata = _build_boundary_state_live_primary_engine_graph()
    if compiled is None:
        unavailable_posture = (
            preview["execution_posture"]
            if preview["execution_posture"] in {"interrupt_wait", "recovery_wait", "terminal", "recursion_limited"}
            else "unavailable"
        )
        unavailable_status = (
            preview["last_run_status"] if preview["last_run_status"] in {"blocked", "noop", "ok"} else "unavailable"
        )
        return {
            **preview,
            **metadata,
            "execution_posture": unavailable_posture,
            "last_run_status": unavailable_status,
            "last_run_reason": metadata["compile_error"] or preview["last_run_reason"],
        }

    try:
        input_payload = _boundary_state_live_primary_engine_initial_state(thread, recursion_limit)
        if run_kind == "stream":
            chunks = list(compiled.stream(input_payload))
            output = chunks[-1] if chunks else {}
        else:
            output = compiled.invoke(input_payload)
        output_dict = output if isinstance(output, dict) else {}
        stop_boundary = str(output_dict.get("stop_boundary", preview["stop_boundary"]))
        posture = preview["execution_posture"]
        if stop_boundary == "recursion_limit_boundary":
            posture = "recursion_limited"
        elif posture not in {"interrupt_wait", "recovery_wait", "terminal"}:
            posture = "executed"
        return {
            **metadata,
            "current_execution_node": str(output_dict.get("current_execution_node", preview["current_execution_node"])),
            "mapped_phase": str(output_dict.get("mapped_phase", preview["mapped_phase"])),
            "boundary_node_path": list(output_dict.get("boundary_node_path", preview["boundary_node_path"])),
            "boundary_phase_path": list(output_dict.get("boundary_phase_path", preview["boundary_phase_path"])),
            "boundary_transition_log": list(
                output_dict.get("boundary_transition_log", preview["boundary_transition_log"])
            ),
            "boundary_state_kind": str(output_dict.get("boundary_state_kind", preview["boundary_state_kind"])),
            "superstep_count": int(output_dict.get("superstep_count", preview["superstep_count"])),
            "stop_boundary": stop_boundary,
            "terminal_reached": bool(output_dict.get("terminal_reached", preview["terminal_reached"])),
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": int(output_dict.get("recursion_limit", preview["recursion_limit"])),
            "execution_posture": posture,
            "last_run_kind": run_kind,
            "last_run_status": "ok",
            "last_run_reason": str(output_dict.get("last_run_reason", preview["last_run_reason"])),
        }
    except Exception as exc:  # pragma: no cover
        return {
            **preview,
            **metadata,
            "execution_posture": "execution_failed",
            "last_run_status": "error",
            "last_run_reason": str(exc),
        }


def _boundary_state_live_primary_engine_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    state = thread.get("boundary_state_live_primary_engine_state")
    preview = _boundary_state_live_primary_engine_preview(
        thread,
        str(thread.get("last_boundary_state_live_primary_engine_kind", "")) or "invoke",
        int(thread.get("last_boundary_state_live_primary_engine_recursion_limit", 8) or 8),
    )
    helper_pointer: dict[str, Any] = {
        "command": "boundary-engine",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "engine_identity": _boundary_state_live_primary_engine_identity(),
            **preview,
        }

    return {
        "engine_identity": state.get("engine_identity", _boundary_state_live_primary_engine_identity()),
        "compile_supported": bool(state.get("compile_supported", preview["compile_supported"])),
        "compiled_graph_present": bool(state.get("compiled_graph_present", preview["compiled_graph_present"])),
        "invoke_supported": bool(state.get("invoke_supported", preview["invoke_supported"])),
        "stream_supported": bool(state.get("stream_supported", preview["stream_supported"])),
        "current_execution_node": str(state.get("current_execution_node", preview["current_execution_node"])),
        "mapped_phase": str(state.get("mapped_phase", preview["mapped_phase"])),
        "boundary_node_path": list(state.get("boundary_node_path", preview["boundary_node_path"])),
        "boundary_phase_path": list(state.get("boundary_phase_path", preview["boundary_phase_path"])),
        "boundary_transition_log": list(
            state.get("boundary_transition_log", preview["boundary_transition_log"])
        ),
        "boundary_state_kind": str(state.get("boundary_state_kind", preview["boundary_state_kind"])),
        "superstep_count": int(state.get("superstep_count", preview["superstep_count"])),
        "stop_boundary": str(state.get("stop_boundary", preview["stop_boundary"])),
        "terminal_reached": bool(state.get("terminal_reached", preview["terminal_reached"])),
        "recursion_limit_supported": bool(
            state.get("recursion_limit_supported", preview["recursion_limit_supported"])
        ),
        "remaining_steps_supported": bool(
            state.get("remaining_steps_supported", preview["remaining_steps_supported"])
        ),
        "recursion_limit": int(state.get("recursion_limit", preview["recursion_limit"])),
        "execution_posture": str(state.get("execution_posture", preview["execution_posture"])),
        "last_run_kind": str(state.get("last_run_kind", preview["last_run_kind"])),
        "last_run_status": str(state.get("last_run_status", preview["last_run_status"])),
        "last_run_reason": str(state.get("last_run_reason", preview["last_run_reason"])),
        "helper_pointer": helper_pointer,
    }


def _persist_boundary_state_live_primary_engine_state(
    thread: dict[str, Any], run_kind: str = "", recursion_limit: int = 8
) -> dict[str, Any]:
    run_kind = run_kind or str(thread.get("last_boundary_state_live_primary_engine_kind", "")) or "invoke"
    recursion_limit = int(
        recursion_limit or thread.get("last_boundary_state_live_primary_engine_recursion_limit", 8) or 8
    )
    result = _execute_boundary_state_live_primary_engine(thread, run_kind, recursion_limit)
    stored = {
        "engine_identity": _boundary_state_live_primary_engine_identity(),
        "compile_supported": result["compile_supported"],
        "compiled_graph_present": result["compiled_graph_present"],
        "invoke_supported": result["invoke_supported"],
        "stream_supported": result["stream_supported"],
        "current_execution_node": result["current_execution_node"],
        "mapped_phase": result["mapped_phase"],
        "boundary_node_path": result["boundary_node_path"],
        "boundary_phase_path": result["boundary_phase_path"],
        "boundary_transition_log": result["boundary_transition_log"],
        "boundary_state_kind": result["boundary_state_kind"],
        "superstep_count": result["superstep_count"],
        "stop_boundary": result["stop_boundary"],
        "terminal_reached": result["terminal_reached"],
        "recursion_limit_supported": result["recursion_limit_supported"],
        "remaining_steps_supported": result["remaining_steps_supported"],
        "recursion_limit": result["recursion_limit"],
        "execution_posture": result["execution_posture"],
        "last_run_kind": result["last_run_kind"],
        "last_run_status": result["last_run_status"],
        "last_run_reason": result["last_run_reason"],
        "updated_at": _now(),
    }
    thread["last_boundary_state_live_primary_engine_kind"] = run_kind
    thread["last_boundary_state_live_primary_engine_reason"] = result["last_run_reason"]
    thread["last_boundary_state_live_primary_engine_recursion_limit"] = recursion_limit
    thread["boundary_state_live_primary_engine_state"] = stored
    return stored


def _handoff_state_live_primary_engine_identity() -> dict[str, Any]:
    return _clone_payload(HANDOFF_STATE_LIVE_PRIMARY_ENGINE_IDENTITY)


def _handoff_state_live_primary_engine_append_visit(
    state: dict[str, Any], node_name: str, phase_name: str, subgraph_name: str
) -> dict[str, Any]:
    node_path = list(state.get("handoff_node_path", []))
    phase_path = list(state.get("handoff_phase_path", []))
    subgraph_path = list(state.get("handoff_subgraph_path", []))
    node_path.append(node_name)
    if phase_name:
        phase_path.append(phase_name)
        state["mapped_phase"] = phase_name
    if subgraph_name:
        subgraph_path.append(subgraph_name)
        state["active_subgraph"] = subgraph_name
    state["current_execution_node"] = node_name
    state["handoff_node_path"] = node_path
    state["handoff_phase_path"] = phase_path
    state["handoff_subgraph_path"] = subgraph_path
    state["superstep_count"] = max(0, len(node_path) - 1)
    return state


def _handoff_state_live_primary_engine_initial_state(thread: dict[str, Any], recursion_limit: int) -> dict[str, Any]:
    kernel_projection = _graph_kernel_projection(thread)
    command_projection = _command_projection(thread)
    active_subgraph = str(thread.get("active_subgraph", "")) or str(command_projection.get("source_subgraph", ""))
    return {
        "current_execution_node": str(kernel_projection["current_node_id"]),
        "mapped_phase": str(kernel_projection["mapped_phase"]),
        "handoff_node_path": [],
        "handoff_phase_path": [],
        "handoff_subgraph_path": [],
        "handoff_transition_log": [],
        "handoff_state_kind": "ordinary",
        "active_subgraph": active_subgraph,
        "source_subgraph": str(command_projection.get("source_subgraph", "")) or active_subgraph,
        "target_subgraph": str(command_projection.get("target_subgraph", "")),
        "parent_handoff_target": str(command_projection.get("parent_handoff_target", "")),
        "graph_scope": str(command_projection.get("graph_scope", "")),
        "superstep_count": 0,
        "next_execution_node": "",
        "stop_boundary": "",
        "terminal_reached": False,
        "recursion_limit_supported": True,
        "remaining_steps_supported": True,
        "recursion_limit": recursion_limit,
        "command_transition": str(command_projection.get("transition_kind", "")),
        "command_target_phase": _command_target_phase(
            str(command_projection.get("parent_handoff_target", "")) or str(command_projection.get("goto_target", ""))
        ),
        "active_loop": str(thread.get("active_loop", "")),
        "last_gate_verdict": str(thread.get("last_gate_verdict", "")),
        "command_consumed": False,
        "loop_consumed": False,
        "boundary_pending": False,
        "boundary_kind": "",
        "last_run_reason": "",
    }


def _subgraph_id_for_node(node_name: str, fallback_subgraph: str = "") -> str:
    node = GRAPH_KERNEL_NODES.get(node_name, {})
    subgraph_id = str(node.get("subgraph_id", "")) if isinstance(node, dict) else ""
    return subgraph_id or fallback_subgraph


def _handoff_state_live_primary_engine_visit_node(state: dict[str, Any], node_name: str) -> dict[str, Any]:
    node = GRAPH_KERNEL_NODES.get(node_name, {})
    phase_name = str(node.get("phase", "")) if isinstance(node, dict) else ""
    subgraph_name = _subgraph_id_for_node(node_name, str(state.get("active_subgraph", "")))
    state = _handoff_state_live_primary_engine_append_visit(state, node_name, phase_name, subgraph_name)
    transition_log = list(state.get("handoff_transition_log", []))

    if node_name == "approval_wait":
        transition_log.append(f"boundary:interrupt:{str(state.get('mapped_phase', ''))}")
        state["handoff_transition_log"] = transition_log
        state["handoff_state_kind"] = "interrupt"
        state["stop_boundary"] = "interrupt_boundary"
        state["next_execution_node"] = "phase_end"
        state["last_run_reason"] = transition_log[-1]
        return state
    if node_name == "recovery_pending_resume":
        transition_log.append(f"boundary:recovery:{str(state.get('mapped_phase', ''))}")
        state["handoff_transition_log"] = transition_log
        state["handoff_state_kind"] = "recovery"
        state["stop_boundary"] = "recovery_boundary"
        state["next_execution_node"] = "phase_end"
        state["last_run_reason"] = transition_log[-1]
        return state
    if node_name in {"accepted_terminal", "halted_terminal", "escalated_terminal"}:
        transition_log.append(f"boundary:terminal:{node_name}")
        state["handoff_transition_log"] = transition_log
        state["handoff_state_kind"] = "terminal"
        state["stop_boundary"] = "terminal_boundary"
        state["terminal_reached"] = True
        state["next_execution_node"] = "phase_end"
        state["last_run_reason"] = transition_log[-1]
        return state

    return state


def _handoff_state_live_primary_engine_decide_next(state: dict[str, Any]) -> dict[str, Any]:
    current_phase = str(state.get("mapped_phase", ""))
    current_subgraph = str(state.get("active_subgraph", ""))
    current_node = str(state.get("current_execution_node", ""))
    transition_log = list(state.get("handoff_transition_log", []))
    recursion_limit = int(state.get("recursion_limit", 0) or 0)
    superstep_count = int(state.get("superstep_count", 0) or 0)
    boundary_pending = bool(state.get("boundary_pending", False))

    if boundary_pending:
        state["next_execution_node"] = "phase_end"
        state["stop_boundary"] = str(state.get("boundary_kind", ""))
        state["boundary_pending"] = False
        state["boundary_kind"] = ""
        state["last_run_reason"] = transition_log[-1] if transition_log else str(state.get("stop_boundary", ""))
        return state

    if current_phase == "verify-accept":
        transition_log.append("boundary:phase_boundary:verify-accept")
        state["handoff_transition_log"] = transition_log
        state["next_execution_node"] = "phase_end"
        state["stop_boundary"] = "phase_boundary"
        state["handoff_state_kind"] = "ordinary"
        state["last_run_reason"] = "handoff-engine:verify-accept"
        return state

    if current_phase and recursion_limit and superstep_count >= recursion_limit:
        transition_log.append(f"boundary:recursion_limit:{recursion_limit}")
        state["handoff_transition_log"] = transition_log
        state["next_execution_node"] = "phase_end"
        state["stop_boundary"] = "recursion_limit_boundary"
        state["handoff_state_kind"] = "ordinary"
        state["last_run_reason"] = f"handoff-engine:recursion_limit:{recursion_limit}"
        return state

    command_transition = str(state.get("command_transition", ""))
    command_target_phase = str(state.get("command_target_phase", ""))
    if (
        command_transition in {"goto", "update_goto", "parent_handoff", "resume_parent_handoff"}
        and command_target_phase
        and not bool(state.get("command_consumed", False))
    ):
        target_node = _phase_node_for_phase(command_target_phase)
        target_subgraph = str(state.get("target_subgraph", "")) or _subgraph_id_for_phase(command_target_phase)
        source_subgraph = str(state.get("source_subgraph", "")) or current_subgraph
        if command_transition in {"parent_handoff", "resume_parent_handoff"}:
            transition_log.append(f"handoff:{command_transition}:{source_subgraph}->{target_subgraph}:{command_target_phase}")
            state["handoff_state_kind"] = "parent_handoff"
        elif target_subgraph and source_subgraph and target_subgraph != source_subgraph:
            transition_log.append(f"handoff:subgraph:{source_subgraph}->{target_subgraph}:{command_target_phase}")
            state["handoff_state_kind"] = "subgraph_transition"
        else:
            transition_log.append(f"handoff:local:{command_transition}:{command_target_phase}")
            state["handoff_state_kind"] = "local_transition"
        state["handoff_transition_log"] = transition_log
        state["target_subgraph"] = target_subgraph
        state["next_execution_node"] = target_node or "phase_end"
        state["boundary_pending"] = True
        state["boundary_kind"] = "command_boundary"
        state["command_consumed"] = True
        state["last_run_reason"] = transition_log[-1]
        return state

    if current_phase in {"execute-parallel", "stabilize"} and str(state.get("last_gate_verdict", "")) == "revise" and not bool(
        state.get("loop_consumed", False)
    ):
        transition_log.append(f"loop:{str(state.get('active_loop', '')) or current_phase}:revise")
        state["handoff_transition_log"] = transition_log
        state["next_execution_node"] = current_node or "phase_end"
        state["boundary_pending"] = True
        state["boundary_kind"] = "loop_boundary"
        state["loop_consumed"] = True
        state["handoff_state_kind"] = "ordinary"
        state["last_run_reason"] = transition_log[-1]
        return state

    successor = _phase_successor(current_phase)
    if successor:
        target_node = _phase_node_for_phase(successor)
        successor_subgraph = _subgraph_id_for_phase(successor)
        if successor_subgraph and current_subgraph and successor_subgraph != current_subgraph:
            transition_log.append(f"handoff:phase:{current_subgraph}->{successor_subgraph}:{successor}")
            state["handoff_state_kind"] = "subgraph_transition"
        else:
            transition_log.append(f"sequential:{current_phase}->{successor}")
            state["handoff_state_kind"] = "ordinary"
        state["handoff_transition_log"] = transition_log
        state["target_subgraph"] = successor_subgraph
        state["next_execution_node"] = target_node or "phase_end"
        state["stop_boundary"] = "phase_boundary"
        state["last_run_reason"] = transition_log[-1]
        return state

    transition_log.append(f"boundary:phase_boundary:{current_phase or current_node}")
    state["handoff_transition_log"] = transition_log
    state["next_execution_node"] = "phase_end"
    state["stop_boundary"] = "phase_boundary"
    state["handoff_state_kind"] = "ordinary"
    state["last_run_reason"] = transition_log[-1]
    return state


def _handoff_state_live_primary_engine_preview(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    state = _handoff_state_live_primary_engine_initial_state(thread, recursion_limit)
    current_node = str(state.get("current_execution_node", ""))
    if current_node:
        state = _handoff_state_live_primary_engine_visit_node(state, current_node)
        if current_node not in {"approval_wait", "recovery_pending_resume", "accepted_terminal", "halted_terminal", "escalated_terminal"}:
            while True:
                state = _handoff_state_live_primary_engine_decide_next(state)
                next_node = str(state.get("next_execution_node", ""))
                if next_node in {"", "phase_end"}:
                    break
                state = _handoff_state_live_primary_engine_visit_node(state, next_node)

    posture_map = {
        "interrupt_boundary": ("interrupt_wait", "blocked"),
        "recovery_boundary": ("recovery_wait", "blocked"),
        "terminal_boundary": ("terminal", "noop"),
        "recursion_limit_boundary": ("recursion_limited", "ok"),
        "phase_boundary": ("ready" if LANGGRAPH_AVAILABLE else "unavailable", "planned" if not LANGGRAPH_AVAILABLE else "ok"),
        "command_boundary": ("ready" if LANGGRAPH_AVAILABLE else "unavailable", "planned" if not LANGGRAPH_AVAILABLE else "ok"),
        "loop_boundary": ("ready" if LANGGRAPH_AVAILABLE else "unavailable", "planned" if not LANGGRAPH_AVAILABLE else "ok"),
        "": ("ready" if LANGGRAPH_AVAILABLE else "unavailable", "planned" if not LANGGRAPH_AVAILABLE else "ok"),
    }
    execution_posture, last_run_status = posture_map[str(state.get("stop_boundary", ""))]
    return {
        **metadata,
        "current_execution_node": str(state.get("current_execution_node", "")),
        "mapped_phase": str(state.get("mapped_phase", "")),
        "handoff_node_path": list(state.get("handoff_node_path", [])),
        "handoff_phase_path": list(state.get("handoff_phase_path", [])),
        "handoff_subgraph_path": list(state.get("handoff_subgraph_path", [])),
        "handoff_transition_log": list(state.get("handoff_transition_log", [])),
        "handoff_state_kind": str(state.get("handoff_state_kind", "ordinary")),
        "active_subgraph": str(state.get("active_subgraph", "")),
        "source_subgraph": str(state.get("source_subgraph", "")),
        "target_subgraph": str(state.get("target_subgraph", "")),
        "parent_handoff_target": str(state.get("parent_handoff_target", "")),
        "graph_scope": str(state.get("graph_scope", "")),
        "superstep_count": int(state.get("superstep_count", 0) or 0),
        "stop_boundary": str(state.get("stop_boundary", "")),
        "terminal_reached": bool(state.get("terminal_reached", False)),
        "recursion_limit_supported": bool(state.get("recursion_limit_supported", True)),
        "remaining_steps_supported": bool(state.get("remaining_steps_supported", True)),
        "recursion_limit": int(state.get("recursion_limit", recursion_limit) or recursion_limit),
        "execution_posture": execution_posture,
        "last_run_kind": run_kind,
        "last_run_status": last_run_status,
        "last_run_reason": str(state.get("last_run_reason", "")),
    }


def _build_handoff_state_live_primary_engine_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class HandoffEngineState(TypedDict, total=False):
            current_execution_node: str
            mapped_phase: str
            handoff_node_path: list[str]
            handoff_phase_path: list[str]
            handoff_subgraph_path: list[str]
            handoff_transition_log: list[str]
            handoff_state_kind: str
            active_subgraph: str
            source_subgraph: str
            target_subgraph: str
            parent_handoff_target: str
            graph_scope: str
            superstep_count: int
            next_execution_node: str
            stop_boundary: str
            terminal_reached: bool
            recursion_limit_supported: bool
            remaining_steps_supported: bool
            recursion_limit: int
            command_transition: str
            command_target_phase: str
            active_loop: str
            last_gate_verdict: str
            command_consumed: bool
            loop_consumed: bool
            boundary_pending: bool
            boundary_kind: str
            last_run_reason: str

        valid_nodes = [str(node_name) for node_name in GRAPH_KERNEL_NODES.keys()]

        def route_current(state: HandoffEngineState) -> str:
            node_name = str(state.get("current_execution_node", ""))
            return node_name if node_name in valid_nodes else "phase_end"

        def route_next(state: HandoffEngineState) -> str:
            node_name = str(state.get("next_execution_node", ""))
            return node_name if node_name in valid_nodes else "phase_end"

        def make_node(node_name: str):
            def _node(state: HandoffEngineState) -> HandoffEngineState:
                return _handoff_state_live_primary_engine_visit_node(dict(state), node_name)

            return _node

        def decide_next(state: HandoffEngineState) -> HandoffEngineState:
            return _handoff_state_live_primary_engine_decide_next(dict(state))

        def phase_end(state: HandoffEngineState) -> HandoffEngineState:
            return state

        builder = StateGraph(HandoffEngineState)
        builder.add_node("route_current", lambda state: state)
        builder.add_node("decide_next", decide_next)
        builder.add_node("phase_end", phase_end)
        builder.add_edge(START, "route_current")
        for node_name in valid_nodes:
            builder.add_node(node_name, make_node(node_name))
            if str(GRAPH_KERNEL_NODES[node_name].get("node_kind", "")) == "phase":
                builder.add_edge(node_name, "decide_next")
            else:
                builder.add_edge(node_name, "phase_end")
        builder.add_conditional_edges("route_current", route_current)
        builder.add_conditional_edges("decide_next", route_next)
        builder.add_edge("phase_end", END)
        compiled = builder.compile()
        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return compiled, metadata
    except Exception as exc:  # pragma: no cover
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_handoff_state_live_primary_engine(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    preview = _handoff_state_live_primary_engine_preview(thread, run_kind, recursion_limit)
    compiled, metadata = _build_handoff_state_live_primary_engine_graph()
    if compiled is None:
        unavailable_posture = (
            preview["execution_posture"]
            if preview["execution_posture"] in {"interrupt_wait", "recovery_wait", "terminal", "recursion_limited"}
            else "unavailable"
        )
        unavailable_status = (
            preview["last_run_status"] if preview["last_run_status"] in {"blocked", "noop", "ok"} else "unavailable"
        )
        return {
            **preview,
            **metadata,
            "execution_posture": unavailable_posture,
            "last_run_status": unavailable_status,
            "last_run_reason": metadata["compile_error"] or preview["last_run_reason"],
        }

    try:
        input_payload = _handoff_state_live_primary_engine_initial_state(thread, recursion_limit)
        if run_kind == "stream":
            chunks = list(compiled.stream(input_payload))
            output = chunks[-1] if chunks else {}
        else:
            output = compiled.invoke(input_payload)
        output_dict = output if isinstance(output, dict) else {}
        stop_boundary = str(output_dict.get("stop_boundary", preview["stop_boundary"]))
        posture = preview["execution_posture"]
        if stop_boundary == "recursion_limit_boundary":
            posture = "recursion_limited"
        elif posture not in {"interrupt_wait", "recovery_wait", "terminal"}:
            posture = "executed"
        return {
            **metadata,
            "current_execution_node": str(output_dict.get("current_execution_node", preview["current_execution_node"])),
            "mapped_phase": str(output_dict.get("mapped_phase", preview["mapped_phase"])),
            "handoff_node_path": list(output_dict.get("handoff_node_path", preview["handoff_node_path"])),
            "handoff_phase_path": list(output_dict.get("handoff_phase_path", preview["handoff_phase_path"])),
            "handoff_subgraph_path": list(output_dict.get("handoff_subgraph_path", preview["handoff_subgraph_path"])),
            "handoff_transition_log": list(
                output_dict.get("handoff_transition_log", preview["handoff_transition_log"])
            ),
            "handoff_state_kind": str(output_dict.get("handoff_state_kind", preview["handoff_state_kind"])),
            "active_subgraph": str(output_dict.get("active_subgraph", preview["active_subgraph"])),
            "source_subgraph": str(output_dict.get("source_subgraph", preview["source_subgraph"])),
            "target_subgraph": str(output_dict.get("target_subgraph", preview["target_subgraph"])),
            "parent_handoff_target": str(
                output_dict.get("parent_handoff_target", preview["parent_handoff_target"])
            ),
            "graph_scope": str(output_dict.get("graph_scope", preview["graph_scope"])),
            "superstep_count": int(output_dict.get("superstep_count", preview["superstep_count"])),
            "stop_boundary": stop_boundary,
            "terminal_reached": bool(output_dict.get("terminal_reached", preview["terminal_reached"])),
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": int(output_dict.get("recursion_limit", preview["recursion_limit"])),
            "execution_posture": posture,
            "last_run_kind": run_kind,
            "last_run_status": "ok",
            "last_run_reason": str(output_dict.get("last_run_reason", preview["last_run_reason"])),
        }
    except Exception as exc:  # pragma: no cover
        return {
            **preview,
            **metadata,
            "execution_posture": "execution_failed",
            "last_run_status": "error",
            "last_run_reason": str(exc),
        }


def _handoff_state_live_primary_engine_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    state = thread.get("handoff_state_live_primary_engine_state")
    preview = _handoff_state_live_primary_engine_preview(
        thread,
        str(thread.get("last_handoff_state_live_primary_engine_kind", "")) or "invoke",
        int(thread.get("last_handoff_state_live_primary_engine_recursion_limit", 8) or 8),
    )
    helper_pointer: dict[str, Any] = {
        "command": "handoff-engine",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "engine_identity": _handoff_state_live_primary_engine_identity(),
            **preview,
        }

    return {
        "engine_identity": state.get("engine_identity", _handoff_state_live_primary_engine_identity()),
        "compile_supported": bool(state.get("compile_supported", preview["compile_supported"])),
        "compiled_graph_present": bool(state.get("compiled_graph_present", preview["compiled_graph_present"])),
        "invoke_supported": bool(state.get("invoke_supported", preview["invoke_supported"])),
        "stream_supported": bool(state.get("stream_supported", preview["stream_supported"])),
        "current_execution_node": str(state.get("current_execution_node", preview["current_execution_node"])),
        "mapped_phase": str(state.get("mapped_phase", preview["mapped_phase"])),
        "handoff_node_path": list(state.get("handoff_node_path", preview["handoff_node_path"])),
        "handoff_phase_path": list(state.get("handoff_phase_path", preview["handoff_phase_path"])),
        "handoff_subgraph_path": list(state.get("handoff_subgraph_path", preview["handoff_subgraph_path"])),
        "handoff_transition_log": list(state.get("handoff_transition_log", preview["handoff_transition_log"])),
        "handoff_state_kind": str(state.get("handoff_state_kind", preview["handoff_state_kind"])),
        "active_subgraph": str(state.get("active_subgraph", preview["active_subgraph"])),
        "source_subgraph": str(state.get("source_subgraph", preview["source_subgraph"])),
        "target_subgraph": str(state.get("target_subgraph", preview["target_subgraph"])),
        "parent_handoff_target": str(state.get("parent_handoff_target", preview["parent_handoff_target"])),
        "graph_scope": str(state.get("graph_scope", preview["graph_scope"])),
        "superstep_count": int(state.get("superstep_count", preview["superstep_count"])),
        "stop_boundary": str(state.get("stop_boundary", preview["stop_boundary"])),
        "terminal_reached": bool(state.get("terminal_reached", preview["terminal_reached"])),
        "recursion_limit_supported": bool(
            state.get("recursion_limit_supported", preview["recursion_limit_supported"])
        ),
        "remaining_steps_supported": bool(
            state.get("remaining_steps_supported", preview["remaining_steps_supported"])
        ),
        "recursion_limit": int(state.get("recursion_limit", preview["recursion_limit"])),
        "execution_posture": str(state.get("execution_posture", preview["execution_posture"])),
        "last_run_kind": str(state.get("last_run_kind", preview["last_run_kind"])),
        "last_run_status": str(state.get("last_run_status", preview["last_run_status"])),
        "last_run_reason": str(state.get("last_run_reason", preview["last_run_reason"])),
        "helper_pointer": helper_pointer,
    }


def _persist_handoff_state_live_primary_engine_state(
    thread: dict[str, Any], run_kind: str = "", recursion_limit: int = 8
) -> dict[str, Any]:
    run_kind = run_kind or str(thread.get("last_handoff_state_live_primary_engine_kind", "")) or "invoke"
    recursion_limit = int(
        recursion_limit or thread.get("last_handoff_state_live_primary_engine_recursion_limit", 8) or 8
    )
    result = _execute_handoff_state_live_primary_engine(thread, run_kind, recursion_limit)
    stored = {
        "engine_identity": _handoff_state_live_primary_engine_identity(),
        "compile_supported": result["compile_supported"],
        "compiled_graph_present": result["compiled_graph_present"],
        "invoke_supported": result["invoke_supported"],
        "stream_supported": result["stream_supported"],
        "current_execution_node": result["current_execution_node"],
        "mapped_phase": result["mapped_phase"],
        "handoff_node_path": result["handoff_node_path"],
        "handoff_phase_path": result["handoff_phase_path"],
        "handoff_subgraph_path": result["handoff_subgraph_path"],
        "handoff_transition_log": result["handoff_transition_log"],
        "handoff_state_kind": result["handoff_state_kind"],
        "active_subgraph": result["active_subgraph"],
        "source_subgraph": result["source_subgraph"],
        "target_subgraph": result["target_subgraph"],
        "parent_handoff_target": result["parent_handoff_target"],
        "graph_scope": result["graph_scope"],
        "superstep_count": result["superstep_count"],
        "stop_boundary": result["stop_boundary"],
        "terminal_reached": result["terminal_reached"],
        "recursion_limit_supported": result["recursion_limit_supported"],
        "remaining_steps_supported": result["remaining_steps_supported"],
        "recursion_limit": result["recursion_limit"],
        "execution_posture": result["execution_posture"],
        "last_run_kind": result["last_run_kind"],
        "last_run_status": result["last_run_status"],
        "last_run_reason": result["last_run_reason"],
        "updated_at": _now(),
    }
    thread["last_handoff_state_live_primary_engine_kind"] = run_kind
    thread["last_handoff_state_live_primary_engine_reason"] = result["last_run_reason"]
    thread["last_handoff_state_live_primary_engine_recursion_limit"] = recursion_limit
    thread["handoff_state_live_primary_engine_state"] = stored
    return stored


def _approval_aware_live_primary_engine_identity() -> dict[str, Any]:
    return _clone_payload(APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY)


def _approval_aware_live_primary_engine_preview(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    approval_projection = _approval_queue_projection(thread)
    boundary_projection = _boundary_state_live_primary_engine_projection(thread)
    pending_count = int(approval_projection.get("pending_count", 0) or 0)
    resolved_count = int(approval_projection.get("resolved_count", 0) or 0)
    queue_posture = str(approval_projection.get("queue_posture", "no_interrupts"))
    current_interrupt_id = str(approval_projection.get("current_interrupt_id", ""))
    resume_map_keys = [str(key) for key in approval_projection.get("resume_map_keys", [])]

    approval_node_path = list(boundary_projection.get("boundary_node_path", []))
    approval_phase_path = list(boundary_projection.get("boundary_phase_path", []))
    stop_boundary = str(boundary_projection.get("stop_boundary", ""))
    current_execution_node = str(boundary_projection.get("current_execution_node", ""))
    mapped_phase = str(boundary_projection.get("mapped_phase", ""))
    terminal_reached = bool(boundary_projection.get("terminal_reached", False))
    execution_posture = str(boundary_projection.get("execution_posture", "unavailable"))
    last_run_status = str(boundary_projection.get("last_run_status", ""))
    last_run_reason = str(boundary_projection.get("last_run_reason", ""))

    transition_log: list[str] = []
    resume_state_kind = "ordinary"

    if pending_count > 0:
        resume_state_kind = "awaiting_manual_approval"
        stop_boundary = "interrupt_boundary"
        current_execution_node = "approval_wait"
        transition_log.append(f"approval:pending:{current_interrupt_id or pending_count}")
        execution_posture = "interrupt_wait"
        last_run_status = "blocked"
        last_run_reason = transition_log[-1]
        if not approval_node_path:
            approval_node_path = ["approval_wait"]
        if not approval_phase_path and mapped_phase:
            approval_phase_path = [mapped_phase]
    elif resolved_count > 0 and pending_count == 0:
        resume_state_kind = "resolved_queue_retained"
        transition_log.append(f"approval:resolved:{resolved_count}")
        if resume_map_keys:
            transition_log.append(f"approval:resume_map:{','.join(resume_map_keys)}")
        last_run_reason = transition_log[-1]
    elif resume_map_keys:
        resume_state_kind = "resume_map_present"
        transition_log.append(f"approval:resume_map:{','.join(resume_map_keys)}")
        last_run_reason = transition_log[-1]

    return {
        **metadata,
        "current_execution_node": current_execution_node,
        "mapped_phase": mapped_phase,
        "approval_node_path": approval_node_path,
        "approval_phase_path": approval_phase_path,
        "approval_transition_log": transition_log,
        "resume_state_kind": resume_state_kind,
        "queue_posture": queue_posture,
        "pending_count": pending_count,
        "resolved_count": resolved_count,
        "current_interrupt_id": current_interrupt_id,
        "resume_map_keys": resume_map_keys,
        "superstep_count": max(0, len(approval_node_path) - 1),
        "stop_boundary": stop_boundary,
        "terminal_reached": terminal_reached,
        "recursion_limit_supported": True,
        "remaining_steps_supported": True,
        "recursion_limit": recursion_limit,
        "execution_posture": execution_posture,
        "last_run_kind": run_kind,
        "last_run_status": last_run_status or ("planned" if not LANGGRAPH_AVAILABLE else "ok"),
        "last_run_reason": last_run_reason,
    }


def _build_approval_aware_live_primary_engine_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class ApprovalEngineState(TypedDict, total=False):
            approval_node_path: list[str]
            approval_phase_path: list[str]
            approval_transition_log: list[str]
            resume_state_kind: str
            queue_posture: str
            pending_count: int
            resolved_count: int
            current_interrupt_id: str
            resume_map_keys: list[str]
            superstep_count: int
            stop_boundary: str
            terminal_reached: bool
            recursion_limit: int

        def passthrough(state: ApprovalEngineState) -> ApprovalEngineState:
            return state

        builder = StateGraph(ApprovalEngineState)
        builder.add_node("approval_state", passthrough)
        builder.add_edge(START, "approval_state")
        builder.add_edge("approval_state", END)
        compiled = builder.compile()
        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return compiled, metadata
    except Exception as exc:  # pragma: no cover
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_approval_aware_live_primary_engine(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    preview = _approval_aware_live_primary_engine_preview(thread, run_kind, recursion_limit)
    compiled, metadata = _build_approval_aware_live_primary_engine_graph()
    if compiled is None:
        unavailable_posture = (
            preview["execution_posture"]
            if preview["execution_posture"] in {"interrupt_wait", "recovery_wait", "terminal", "recursion_limited"}
            else "unavailable"
        )
        unavailable_status = (
            preview["last_run_status"] if preview["last_run_status"] in {"blocked", "noop", "ok"} else "unavailable"
        )
        return {
            **preview,
            **metadata,
            "execution_posture": unavailable_posture,
            "last_run_status": unavailable_status,
            "last_run_reason": metadata["compile_error"] or preview["last_run_reason"],
        }

    try:
        input_payload = {
            "approval_node_path": list(preview["approval_node_path"]),
            "approval_phase_path": list(preview["approval_phase_path"]),
            "approval_transition_log": list(preview["approval_transition_log"]),
            "resume_state_kind": preview["resume_state_kind"],
            "queue_posture": preview["queue_posture"],
            "pending_count": preview["pending_count"],
            "resolved_count": preview["resolved_count"],
            "current_interrupt_id": preview["current_interrupt_id"],
            "resume_map_keys": list(preview["resume_map_keys"]),
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit": preview["recursion_limit"],
        }
        if run_kind == "stream":
            chunks = list(compiled.stream(input_payload))
            output = chunks[-1] if chunks else {}
        else:
            output = compiled.invoke(input_payload)
        output_dict = output if isinstance(output, dict) else {}
        return {
            **metadata,
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "approval_node_path": list(output_dict.get("approval_node_path", preview["approval_node_path"])),
            "approval_phase_path": list(output_dict.get("approval_phase_path", preview["approval_phase_path"])),
            "approval_transition_log": list(
                output_dict.get("approval_transition_log", preview["approval_transition_log"])
            ),
            "resume_state_kind": str(output_dict.get("resume_state_kind", preview["resume_state_kind"])),
            "queue_posture": str(output_dict.get("queue_posture", preview["queue_posture"])),
            "pending_count": int(output_dict.get("pending_count", preview["pending_count"])),
            "resolved_count": int(output_dict.get("resolved_count", preview["resolved_count"])),
            "current_interrupt_id": str(output_dict.get("current_interrupt_id", preview["current_interrupt_id"])),
            "resume_map_keys": list(output_dict.get("resume_map_keys", preview["resume_map_keys"])),
            "superstep_count": int(output_dict.get("superstep_count", preview["superstep_count"])),
            "stop_boundary": str(output_dict.get("stop_boundary", preview["stop_boundary"])),
            "terminal_reached": bool(output_dict.get("terminal_reached", preview["terminal_reached"])),
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": int(output_dict.get("recursion_limit", preview["recursion_limit"])),
            "execution_posture": preview["execution_posture"],
            "last_run_kind": run_kind,
            "last_run_status": "ok" if preview["last_run_status"] != "blocked" else "blocked",
            "last_run_reason": preview["last_run_reason"],
        }
    except Exception as exc:  # pragma: no cover
        return {
            **preview,
            **metadata,
            "execution_posture": "execution_failed",
            "last_run_status": "error",
            "last_run_reason": str(exc),
        }


def _approval_aware_live_primary_engine_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    state = thread.get("approval_aware_live_primary_engine_state")
    preview = _approval_aware_live_primary_engine_preview(
        thread,
        str(thread.get("last_approval_aware_live_primary_engine_kind", "")) or "invoke",
        int(thread.get("last_approval_aware_live_primary_engine_recursion_limit", 8) or 8),
    )
    helper_pointer: dict[str, Any] = {
        "command": "approval-engine",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "engine_identity": _approval_aware_live_primary_engine_identity(),
            **preview,
        }

    return {
        "engine_identity": state.get("engine_identity", _approval_aware_live_primary_engine_identity()),
        "compile_supported": bool(state.get("compile_supported", preview["compile_supported"])),
        "compiled_graph_present": bool(state.get("compiled_graph_present", preview["compiled_graph_present"])),
        "invoke_supported": bool(state.get("invoke_supported", preview["invoke_supported"])),
        "stream_supported": bool(state.get("stream_supported", preview["stream_supported"])),
        "current_execution_node": str(state.get("current_execution_node", preview["current_execution_node"])),
        "mapped_phase": str(state.get("mapped_phase", preview["mapped_phase"])),
        "approval_node_path": list(state.get("approval_node_path", preview["approval_node_path"])),
        "approval_phase_path": list(state.get("approval_phase_path", preview["approval_phase_path"])),
        "approval_transition_log": list(state.get("approval_transition_log", preview["approval_transition_log"])),
        "resume_state_kind": str(state.get("resume_state_kind", preview["resume_state_kind"])),
        "queue_posture": str(state.get("queue_posture", preview["queue_posture"])),
        "pending_count": int(state.get("pending_count", preview["pending_count"])),
        "resolved_count": int(state.get("resolved_count", preview["resolved_count"])),
        "current_interrupt_id": str(state.get("current_interrupt_id", preview["current_interrupt_id"])),
        "resume_map_keys": list(state.get("resume_map_keys", preview["resume_map_keys"])),
        "superstep_count": int(state.get("superstep_count", preview["superstep_count"])),
        "stop_boundary": str(state.get("stop_boundary", preview["stop_boundary"])),
        "terminal_reached": bool(state.get("terminal_reached", preview["terminal_reached"])),
        "recursion_limit_supported": bool(
            state.get("recursion_limit_supported", preview["recursion_limit_supported"])
        ),
        "remaining_steps_supported": bool(
            state.get("remaining_steps_supported", preview["remaining_steps_supported"])
        ),
        "recursion_limit": int(state.get("recursion_limit", preview["recursion_limit"])),
        "execution_posture": str(state.get("execution_posture", preview["execution_posture"])),
        "last_run_kind": str(state.get("last_run_kind", preview["last_run_kind"])),
        "last_run_status": str(state.get("last_run_status", preview["last_run_status"])),
        "last_run_reason": str(state.get("last_run_reason", preview["last_run_reason"])),
        "helper_pointer": helper_pointer,
    }


def _persist_approval_aware_live_primary_engine_state(
    thread: dict[str, Any], run_kind: str = "", recursion_limit: int = 8
) -> dict[str, Any]:
    run_kind = run_kind or str(thread.get("last_approval_aware_live_primary_engine_kind", "")) or "invoke"
    recursion_limit = int(
        recursion_limit or thread.get("last_approval_aware_live_primary_engine_recursion_limit", 8) or 8
    )
    result = _execute_approval_aware_live_primary_engine(thread, run_kind, recursion_limit)
    stored = {
        "engine_identity": _approval_aware_live_primary_engine_identity(),
        "compile_supported": result["compile_supported"],
        "compiled_graph_present": result["compiled_graph_present"],
        "invoke_supported": result["invoke_supported"],
        "stream_supported": result["stream_supported"],
        "current_execution_node": result["current_execution_node"],
        "mapped_phase": result["mapped_phase"],
        "approval_node_path": result["approval_node_path"],
        "approval_phase_path": result["approval_phase_path"],
        "approval_transition_log": result["approval_transition_log"],
        "resume_state_kind": result["resume_state_kind"],
        "queue_posture": result["queue_posture"],
        "pending_count": result["pending_count"],
        "resolved_count": result["resolved_count"],
        "current_interrupt_id": result["current_interrupt_id"],
        "resume_map_keys": result["resume_map_keys"],
        "superstep_count": result["superstep_count"],
        "stop_boundary": result["stop_boundary"],
        "terminal_reached": result["terminal_reached"],
        "recursion_limit_supported": result["recursion_limit_supported"],
        "remaining_steps_supported": result["remaining_steps_supported"],
        "recursion_limit": result["recursion_limit"],
        "execution_posture": result["execution_posture"],
        "last_run_kind": result["last_run_kind"],
        "last_run_status": result["last_run_status"],
        "last_run_reason": result["last_run_reason"],
        "updated_at": _now(),
    }
    thread["last_approval_aware_live_primary_engine_kind"] = run_kind
    thread["last_approval_aware_live_primary_engine_reason"] = result["last_run_reason"]
    thread["last_approval_aware_live_primary_engine_recursion_limit"] = recursion_limit
    thread["approval_aware_live_primary_engine_state"] = stored
    return stored


def _provenance_state_live_primary_engine_identity() -> dict[str, Any]:
    return _clone_payload(PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_IDENTITY)


def _recovery_target_kind(target_id: str, last_action: str) -> str:
    if target_id.startswith("checkpoint:"):
        return "checkpoint"
    if target_id.startswith("history:"):
        return "state_history"
    if last_action == "update-state":
        return "update_state"
    return ""


def _provenance_state_live_primary_engine_preview(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }

    provenance_node_path: list[str] = []
    provenance_phase_path: list[str] = []
    provenance_transition_log: list[str] = []
    provenance_state_kind = "ordinary"
    current_execution_node = ""
    mapped_phase = str(thread.get("phase", ""))
    stop_boundary = "phase_boundary"
    terminal_reached = False
    execution_posture = "ready" if LANGGRAPH_AVAILABLE else "unavailable"
    last_run_status = "planned" if not LANGGRAPH_AVAILABLE else "ok"
    last_run_reason = ""

    repo_root_value = str(thread.get("repo_root", ""))
    thread_id = str(thread.get("thread_id", ""))
    history_projection = {
        "compatibility": "no_history",
        "target_count": 0,
        "source_records": [],
    }
    if repo_root_value and thread_id:
        repo_root = resolve_repo_root(repo_root_value)
        checkpoint = read_checkpoint(repo_root, thread_id)
        interrupt = read_interrupt(repo_root, thread_id)
        history_projection = _history_projection(repo_root, thread_id, thread, checkpoint, interrupt)

    recovery_projection = _recovery_projection(thread)
    recovery_posture = str(recovery_projection.get("posture", "ordinary"))
    recovery_action = str(recovery_projection.get("last_action", ""))
    recovery_target_id = str(recovery_projection.get("target_id", ""))
    recovery_target_kind = _recovery_target_kind(recovery_target_id, recovery_action)
    source_records = [str(item) for item in recovery_projection.get("source_records", []) if str(item)]
    recoverable_fields_touched = [
        str(item) for item in recovery_projection.get("recoverable_fields_touched", []) if str(item)
    ]
    history_compatibility = str(history_projection.get("compatibility", "no_history"))
    history_target_count = int(history_projection.get("target_count", 0) or 0)

    if recovery_posture == "recovered_pending_resume":
        current_execution_node = "recovery_pending_resume"
        provenance_node_path = [current_execution_node]
        if mapped_phase:
            provenance_phase_path = [mapped_phase]
        stop_boundary = "recovery_boundary"
        execution_posture = "recovery_wait"
        last_run_status = "blocked"
        if recovery_action == "time-travel":
            provenance_state_kind = "time_travel_recovery"
        elif recovery_action == "update-state":
            provenance_state_kind = "update_state_recovery"
        else:
            provenance_state_kind = "recovery_pending_resume"
        provenance_transition_log.append(f"recovery:{recovery_action or 'unknown'}")
        if recovery_target_id:
            provenance_transition_log.append(f"target:{recovery_target_id}")
        if source_records:
            provenance_transition_log.append(f"source_records:{len(source_records)}")
        last_run_reason = provenance_transition_log[-1] if provenance_transition_log else "recovery_pending_resume"
    else:
        boundary_projection = _boundary_state_live_primary_engine_projection(thread)
        current_execution_node = str(boundary_projection.get("current_execution_node", ""))
        mapped_phase = str(boundary_projection.get("mapped_phase", mapped_phase))
        provenance_node_path = list(boundary_projection.get("boundary_node_path", []))
        provenance_phase_path = list(boundary_projection.get("boundary_phase_path", []))
        stop_boundary = str(boundary_projection.get("stop_boundary", "phase_boundary"))
        terminal_reached = bool(boundary_projection.get("terminal_reached", False))
        execution_posture = str(boundary_projection.get("execution_posture", execution_posture))
        last_run_status = str(boundary_projection.get("last_run_status", last_run_status))
        last_run_reason = str(boundary_projection.get("last_run_reason", last_run_reason))

        if history_compatibility == "tracked_history" and history_target_count > 0:
            provenance_state_kind = "history_available"
            provenance_transition_log.append(f"history:{history_target_count}")
        elif history_target_count > 0:
            provenance_state_kind = "synthetic_history"
            provenance_transition_log.append(f"history:{history_target_count}")
        else:
            provenance_state_kind = "ordinary"
        if history_projection.get("source_records"):
            source_records = [str(item) for item in history_projection.get("source_records", []) if str(item)]

    return {
        **metadata,
        "current_execution_node": current_execution_node,
        "mapped_phase": mapped_phase,
        "provenance_node_path": provenance_node_path,
        "provenance_phase_path": provenance_phase_path,
        "provenance_transition_log": provenance_transition_log,
        "provenance_state_kind": provenance_state_kind,
        "recovery_posture": recovery_posture,
        "recovery_action": recovery_action,
        "recovery_target_id": recovery_target_id,
        "recovery_target_kind": recovery_target_kind,
        "source_records": source_records,
        "recoverable_fields_touched": recoverable_fields_touched,
        "history_compatibility": history_compatibility,
        "history_target_count": history_target_count,
        "superstep_count": max(0, len(provenance_node_path) - 1),
        "stop_boundary": stop_boundary,
        "terminal_reached": terminal_reached,
        "recursion_limit_supported": True,
        "remaining_steps_supported": True,
        "recursion_limit": recursion_limit,
        "execution_posture": execution_posture,
        "last_run_kind": run_kind,
        "last_run_status": last_run_status,
        "last_run_reason": last_run_reason,
    }


def _build_provenance_state_live_primary_engine_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class ProvenanceEngineState(TypedDict, total=False):
            provenance_node_path: list[str]
            provenance_phase_path: list[str]
            provenance_transition_log: list[str]
            provenance_state_kind: str
            recovery_posture: str
            recovery_action: str
            recovery_target_id: str
            recovery_target_kind: str
            source_records: list[str]
            recoverable_fields_touched: list[str]
            history_compatibility: str
            history_target_count: int
            superstep_count: int
            stop_boundary: str
            terminal_reached: bool
            recursion_limit: int

        def passthrough(state: ProvenanceEngineState) -> ProvenanceEngineState:
            return state

        builder = StateGraph(ProvenanceEngineState)
        builder.add_node("provenance_state", passthrough)
        builder.add_edge(START, "provenance_state")
        builder.add_edge("provenance_state", END)
        compiled = builder.compile()
        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return compiled, metadata
    except Exception as exc:  # pragma: no cover
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_provenance_state_live_primary_engine(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    preview = _provenance_state_live_primary_engine_preview(thread, run_kind, recursion_limit)
    compiled, metadata = _build_provenance_state_live_primary_engine_graph()
    if compiled is None:
        unavailable_posture = (
            preview["execution_posture"]
            if preview["execution_posture"] in {"interrupt_wait", "recovery_wait", "terminal", "recursion_limited"}
            else "unavailable"
        )
        unavailable_status = (
            preview["last_run_status"] if preview["last_run_status"] in {"blocked", "noop", "ok"} else "unavailable"
        )
        return {
            **preview,
            **metadata,
            "execution_posture": unavailable_posture,
            "last_run_status": unavailable_status,
            "last_run_reason": metadata["compile_error"] or preview["last_run_reason"],
        }

    try:
        input_payload = {
            "provenance_node_path": list(preview["provenance_node_path"]),
            "provenance_phase_path": list(preview["provenance_phase_path"]),
            "provenance_transition_log": list(preview["provenance_transition_log"]),
            "provenance_state_kind": preview["provenance_state_kind"],
            "recovery_posture": preview["recovery_posture"],
            "recovery_action": preview["recovery_action"],
            "recovery_target_id": preview["recovery_target_id"],
            "recovery_target_kind": preview["recovery_target_kind"],
            "source_records": list(preview["source_records"]),
            "recoverable_fields_touched": list(preview["recoverable_fields_touched"]),
            "history_compatibility": preview["history_compatibility"],
            "history_target_count": preview["history_target_count"],
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit": preview["recursion_limit"],
        }
        if run_kind == "stream":
            chunks = list(compiled.stream(input_payload))
            output = chunks[-1] if chunks else {}
        else:
            output = compiled.invoke(input_payload)
        output_dict = output if isinstance(output, dict) else {}
        return {
            **metadata,
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "provenance_node_path": list(output_dict.get("provenance_node_path", preview["provenance_node_path"])),
            "provenance_phase_path": list(output_dict.get("provenance_phase_path", preview["provenance_phase_path"])),
            "provenance_transition_log": list(
                output_dict.get("provenance_transition_log", preview["provenance_transition_log"])
            ),
            "provenance_state_kind": str(
                output_dict.get("provenance_state_kind", preview["provenance_state_kind"])
            ),
            "recovery_posture": str(output_dict.get("recovery_posture", preview["recovery_posture"])),
            "recovery_action": str(output_dict.get("recovery_action", preview["recovery_action"])),
            "recovery_target_id": str(output_dict.get("recovery_target_id", preview["recovery_target_id"])),
            "recovery_target_kind": str(
                output_dict.get("recovery_target_kind", preview["recovery_target_kind"])
            ),
            "source_records": list(output_dict.get("source_records", preview["source_records"])),
            "recoverable_fields_touched": list(
                output_dict.get("recoverable_fields_touched", preview["recoverable_fields_touched"])
            ),
            "history_compatibility": str(
                output_dict.get("history_compatibility", preview["history_compatibility"])
            ),
            "history_target_count": int(
                output_dict.get("history_target_count", preview["history_target_count"])
            ),
            "superstep_count": int(output_dict.get("superstep_count", preview["superstep_count"])),
            "stop_boundary": str(output_dict.get("stop_boundary", preview["stop_boundary"])),
            "terminal_reached": bool(output_dict.get("terminal_reached", preview["terminal_reached"])),
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": int(output_dict.get("recursion_limit", preview["recursion_limit"])),
            "execution_posture": preview["execution_posture"],
            "last_run_kind": run_kind,
            "last_run_status": "ok" if preview["last_run_status"] != "blocked" else "blocked",
            "last_run_reason": preview["last_run_reason"],
        }
    except Exception as exc:  # pragma: no cover
        return {
            **preview,
            **metadata,
            "execution_posture": "execution_failed",
            "last_run_status": "error",
            "last_run_reason": str(exc),
        }


def _provenance_state_live_primary_engine_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    state = thread.get("provenance_state_live_primary_engine_state")
    preview = _provenance_state_live_primary_engine_preview(
        thread,
        str(thread.get("last_provenance_state_live_primary_engine_kind", "")) or "invoke",
        int(thread.get("last_provenance_state_live_primary_engine_recursion_limit", 8) or 8),
    )
    helper_pointer: dict[str, Any] = {
        "command": "provenance-engine",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "engine_identity": _provenance_state_live_primary_engine_identity(),
            **preview,
        }

    return {
        "engine_identity": state.get("engine_identity", _provenance_state_live_primary_engine_identity()),
        "compile_supported": bool(state.get("compile_supported", preview["compile_supported"])),
        "compiled_graph_present": bool(state.get("compiled_graph_present", preview["compiled_graph_present"])),
        "invoke_supported": bool(state.get("invoke_supported", preview["invoke_supported"])),
        "stream_supported": bool(state.get("stream_supported", preview["stream_supported"])),
        "current_execution_node": str(state.get("current_execution_node", preview["current_execution_node"])),
        "mapped_phase": str(state.get("mapped_phase", preview["mapped_phase"])),
        "provenance_node_path": list(state.get("provenance_node_path", preview["provenance_node_path"])),
        "provenance_phase_path": list(state.get("provenance_phase_path", preview["provenance_phase_path"])),
        "provenance_transition_log": list(
            state.get("provenance_transition_log", preview["provenance_transition_log"])
        ),
        "provenance_state_kind": str(state.get("provenance_state_kind", preview["provenance_state_kind"])),
        "recovery_posture": str(state.get("recovery_posture", preview["recovery_posture"])),
        "recovery_action": str(state.get("recovery_action", preview["recovery_action"])),
        "recovery_target_id": str(state.get("recovery_target_id", preview["recovery_target_id"])),
        "recovery_target_kind": str(state.get("recovery_target_kind", preview["recovery_target_kind"])),
        "source_records": list(state.get("source_records", preview["source_records"])),
        "recoverable_fields_touched": list(
            state.get("recoverable_fields_touched", preview["recoverable_fields_touched"])
        ),
        "history_compatibility": str(
            state.get("history_compatibility", preview["history_compatibility"])
        ),
        "history_target_count": int(state.get("history_target_count", preview["history_target_count"])),
        "superstep_count": int(state.get("superstep_count", preview["superstep_count"])),
        "stop_boundary": str(state.get("stop_boundary", preview["stop_boundary"])),
        "terminal_reached": bool(state.get("terminal_reached", preview["terminal_reached"])),
        "recursion_limit_supported": bool(
            state.get("recursion_limit_supported", preview["recursion_limit_supported"])
        ),
        "remaining_steps_supported": bool(
            state.get("remaining_steps_supported", preview["remaining_steps_supported"])
        ),
        "recursion_limit": int(state.get("recursion_limit", preview["recursion_limit"])),
        "execution_posture": str(state.get("execution_posture", preview["execution_posture"])),
        "last_run_kind": str(state.get("last_run_kind", preview["last_run_kind"])),
        "last_run_status": str(state.get("last_run_status", preview["last_run_status"])),
        "last_run_reason": str(state.get("last_run_reason", preview["last_run_reason"])),
        "helper_pointer": helper_pointer,
    }


def _persist_provenance_state_live_primary_engine_state(
    thread: dict[str, Any], run_kind: str = "", recursion_limit: int = 8
) -> dict[str, Any]:
    run_kind = run_kind or str(thread.get("last_provenance_state_live_primary_engine_kind", "")) or "invoke"
    recursion_limit = int(
        recursion_limit or thread.get("last_provenance_state_live_primary_engine_recursion_limit", 8) or 8
    )
    result = _execute_provenance_state_live_primary_engine(thread, run_kind, recursion_limit)
    stored = {
        "engine_identity": _provenance_state_live_primary_engine_identity(),
        "compile_supported": result["compile_supported"],
        "compiled_graph_present": result["compiled_graph_present"],
        "invoke_supported": result["invoke_supported"],
        "stream_supported": result["stream_supported"],
        "current_execution_node": result["current_execution_node"],
        "mapped_phase": result["mapped_phase"],
        "provenance_node_path": result["provenance_node_path"],
        "provenance_phase_path": result["provenance_phase_path"],
        "provenance_transition_log": result["provenance_transition_log"],
        "provenance_state_kind": result["provenance_state_kind"],
        "recovery_posture": result["recovery_posture"],
        "recovery_action": result["recovery_action"],
        "recovery_target_id": result["recovery_target_id"],
        "recovery_target_kind": result["recovery_target_kind"],
        "source_records": result["source_records"],
        "recoverable_fields_touched": result["recoverable_fields_touched"],
        "history_compatibility": result["history_compatibility"],
        "history_target_count": result["history_target_count"],
        "superstep_count": result["superstep_count"],
        "stop_boundary": result["stop_boundary"],
        "terminal_reached": result["terminal_reached"],
        "recursion_limit_supported": result["recursion_limit_supported"],
        "remaining_steps_supported": result["remaining_steps_supported"],
        "recursion_limit": result["recursion_limit"],
        "execution_posture": result["execution_posture"],
        "last_run_kind": result["last_run_kind"],
        "last_run_status": result["last_run_status"],
        "last_run_reason": result["last_run_reason"],
        "updated_at": _now(),
    }
    thread["last_provenance_state_live_primary_engine_kind"] = run_kind
    thread["last_provenance_state_live_primary_engine_reason"] = result["last_run_reason"]
    thread["last_provenance_state_live_primary_engine_recursion_limit"] = recursion_limit
    thread["provenance_state_live_primary_engine_state"] = stored
    return stored


def _durable_artifact_aware_live_primary_engine_identity() -> dict[str, Any]:
    return _clone_payload(DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY)


def _durable_artifact_state_summary(repo_root: Any, thread_id: str) -> dict[str, Any]:
    brief = read_implementation_brief(repo_root, thread_id)
    queue = read_survivor_queue(repo_root, thread_id)
    queue_items = queue.get("items", []) if isinstance(queue, dict) else []
    brief_present = bool(brief)
    queue_present = bool(queue)
    artifact_state_kind = "ordinary"
    if brief_present and queue_present:
        artifact_state_kind = "brief_and_survivor_queue_present"
    elif brief_present:
        artifact_state_kind = "implementation_brief_present"
    elif queue_present:
        artifact_state_kind = "survivor_queue_present"
    return {
        "artifact_state_kind": artifact_state_kind,
        "implementation_brief_present": brief_present,
        "implementation_brief_id": str(brief.get("brief_id", "")) if isinstance(brief, dict) else "",
        "implementation_brief_source_evidence_ref_count": (
            len(brief.get("source_evidence_refs", [])) if isinstance(brief, dict) else 0
        ),
        "survivor_queue_present": queue_present,
        "survivor_queue_kind": str(queue.get("queue_kind", "")) if isinstance(queue, dict) else "",
        "survivor_count": len(queue_items),
    }


def _artifact_transition_log(
    base_log: list[str],
    artifact_summary: dict[str, Any],
) -> list[str]:
    transition_log = [str(item) for item in base_log if str(item)]
    brief_id = str(artifact_summary.get("implementation_brief_id", ""))
    brief_ref_count = int(artifact_summary.get("implementation_brief_source_evidence_ref_count", 0) or 0)
    survivor_queue_kind = str(artifact_summary.get("survivor_queue_kind", ""))
    survivor_count = int(artifact_summary.get("survivor_count", 0) or 0)

    if artifact_summary.get("implementation_brief_present"):
        transition_log.append(f"brief:{brief_id or 'present'}")
        transition_log.append(f"brief_refs:{brief_ref_count}")
    if artifact_summary.get("survivor_queue_present"):
        transition_log.append(f"survivor_queue:{survivor_queue_kind or 'present'}")
        transition_log.append(f"survivors:{survivor_count}")
    if not transition_log and artifact_summary.get("artifact_state_kind") not in {"", "ordinary"}:
        transition_log.append(f"artifacts:{artifact_summary['artifact_state_kind']}")
    return list(dict.fromkeys(transition_log))


def _durable_artifact_aware_live_primary_engine_preview(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }

    provenance_preview = _provenance_state_live_primary_engine_preview(thread, run_kind, recursion_limit)
    artifact_summary = {
        "artifact_state_kind": "ordinary",
        "implementation_brief_present": False,
        "implementation_brief_id": "",
        "implementation_brief_source_evidence_ref_count": 0,
        "survivor_queue_present": False,
        "survivor_queue_kind": "",
        "survivor_count": 0,
    }
    repo_root_value = str(thread.get("repo_root", ""))
    thread_id = str(thread.get("thread_id", ""))
    if repo_root_value and thread_id:
        repo_root = resolve_repo_root(repo_root_value)
        artifact_summary = _durable_artifact_state_summary(repo_root, thread_id)

    artifact_node_path = list(provenance_preview.get("provenance_node_path", []))
    artifact_phase_path = list(provenance_preview.get("provenance_phase_path", []))
    artifact_transition_log = _artifact_transition_log(
        list(provenance_preview.get("provenance_transition_log", [])),
        artifact_summary,
    )

    return {
        **metadata,
        "current_execution_node": provenance_preview["current_execution_node"],
        "mapped_phase": provenance_preview["mapped_phase"],
        "artifact_node_path": artifact_node_path,
        "artifact_phase_path": artifact_phase_path,
        "artifact_transition_log": artifact_transition_log,
        "artifact_state_kind": artifact_summary["artifact_state_kind"],
        "implementation_brief_present": artifact_summary["implementation_brief_present"],
        "implementation_brief_id": artifact_summary["implementation_brief_id"],
        "implementation_brief_source_evidence_ref_count": artifact_summary[
            "implementation_brief_source_evidence_ref_count"
        ],
        "survivor_queue_present": artifact_summary["survivor_queue_present"],
        "survivor_queue_kind": artifact_summary["survivor_queue_kind"],
        "survivor_count": artifact_summary["survivor_count"],
        "superstep_count": int(provenance_preview["superstep_count"]),
        "stop_boundary": provenance_preview["stop_boundary"],
        "terminal_reached": bool(provenance_preview["terminal_reached"]),
        "recursion_limit_supported": bool(provenance_preview["recursion_limit_supported"]),
        "remaining_steps_supported": bool(provenance_preview["remaining_steps_supported"]),
        "recursion_limit": int(provenance_preview["recursion_limit"]),
        "execution_posture": provenance_preview["execution_posture"],
        "last_run_kind": run_kind,
        "last_run_status": provenance_preview["last_run_status"],
        "last_run_reason": provenance_preview["last_run_reason"],
    }


def _build_durable_artifact_aware_live_primary_engine_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class DurableArtifactAwareEngineState(TypedDict, total=False):
            artifact_node_path: list[str]
            artifact_phase_path: list[str]
            artifact_transition_log: list[str]
            artifact_state_kind: str
            implementation_brief_present: bool
            implementation_brief_id: str
            implementation_brief_source_evidence_ref_count: int
            survivor_queue_present: bool
            survivor_queue_kind: str
            survivor_count: int
            superstep_count: int
            stop_boundary: str
            terminal_reached: bool
            recursion_limit: int

        def passthrough(state: DurableArtifactAwareEngineState) -> DurableArtifactAwareEngineState:
            return state

        builder = StateGraph(DurableArtifactAwareEngineState)
        builder.add_node("artifact_state", passthrough)
        builder.add_edge(START, "artifact_state")
        builder.add_edge("artifact_state", END)
        compiled = builder.compile()
        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return compiled, metadata
    except Exception as exc:  # pragma: no cover
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_durable_artifact_aware_live_primary_engine(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    preview = _durable_artifact_aware_live_primary_engine_preview(thread, run_kind, recursion_limit)
    compiled, metadata = _build_durable_artifact_aware_live_primary_engine_graph()
    if compiled is None:
        unavailable_posture = (
            preview["execution_posture"]
            if preview["execution_posture"] in {"interrupt_wait", "recovery_wait", "terminal", "recursion_limited"}
            else "unavailable"
        )
        unavailable_status = (
            preview["last_run_status"] if preview["last_run_status"] in {"blocked", "noop", "ok"} else "unavailable"
        )
        return {
            **preview,
            **metadata,
            "execution_posture": unavailable_posture,
            "last_run_status": unavailable_status,
            "last_run_reason": metadata["compile_error"] or preview["last_run_reason"],
        }

    try:
        input_payload = {
            "artifact_node_path": list(preview["artifact_node_path"]),
            "artifact_phase_path": list(preview["artifact_phase_path"]),
            "artifact_transition_log": list(preview["artifact_transition_log"]),
            "artifact_state_kind": preview["artifact_state_kind"],
            "implementation_brief_present": preview["implementation_brief_present"],
            "implementation_brief_id": preview["implementation_brief_id"],
            "implementation_brief_source_evidence_ref_count": preview[
                "implementation_brief_source_evidence_ref_count"
            ],
            "survivor_queue_present": preview["survivor_queue_present"],
            "survivor_queue_kind": preview["survivor_queue_kind"],
            "survivor_count": preview["survivor_count"],
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit": preview["recursion_limit"],
        }
        if run_kind == "stream":
            chunks = list(compiled.stream(input_payload))
            output = chunks[-1] if chunks else {}
        else:
            output = compiled.invoke(input_payload)
        output_dict = output if isinstance(output, dict) else {}
        return {
            **metadata,
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "artifact_node_path": list(output_dict.get("artifact_node_path", preview["artifact_node_path"])),
            "artifact_phase_path": list(output_dict.get("artifact_phase_path", preview["artifact_phase_path"])),
            "artifact_transition_log": list(
                output_dict.get("artifact_transition_log", preview["artifact_transition_log"])
            ),
            "artifact_state_kind": str(output_dict.get("artifact_state_kind", preview["artifact_state_kind"])),
            "implementation_brief_present": bool(
                output_dict.get("implementation_brief_present", preview["implementation_brief_present"])
            ),
            "implementation_brief_id": str(
                output_dict.get("implementation_brief_id", preview["implementation_brief_id"])
            ),
            "implementation_brief_source_evidence_ref_count": int(
                output_dict.get(
                    "implementation_brief_source_evidence_ref_count",
                    preview["implementation_brief_source_evidence_ref_count"],
                )
            ),
            "survivor_queue_present": bool(
                output_dict.get("survivor_queue_present", preview["survivor_queue_present"])
            ),
            "survivor_queue_kind": str(output_dict.get("survivor_queue_kind", preview["survivor_queue_kind"])),
            "survivor_count": int(output_dict.get("survivor_count", preview["survivor_count"])),
            "superstep_count": int(output_dict.get("superstep_count", preview["superstep_count"])),
            "stop_boundary": str(output_dict.get("stop_boundary", preview["stop_boundary"])),
            "terminal_reached": bool(output_dict.get("terminal_reached", preview["terminal_reached"])),
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": int(output_dict.get("recursion_limit", preview["recursion_limit"])),
            "execution_posture": preview["execution_posture"],
            "last_run_kind": run_kind,
            "last_run_status": "ok" if preview["last_run_status"] != "blocked" else "blocked",
            "last_run_reason": preview["last_run_reason"],
        }
    except Exception as exc:  # pragma: no cover
        return {
            **preview,
            **metadata,
            "execution_posture": "execution_failed",
            "last_run_status": "error",
            "last_run_reason": str(exc),
        }


def _durable_artifact_aware_live_primary_engine_projection(
    thread: dict[str, Any], thread_id: str = ""
) -> dict[str, Any]:
    state = thread.get("durable_artifact_aware_live_primary_engine_state")
    preview = _durable_artifact_aware_live_primary_engine_preview(
        thread,
        str(thread.get("last_durable_artifact_aware_live_primary_engine_kind", "")) or "invoke",
        int(thread.get("last_durable_artifact_aware_live_primary_engine_recursion_limit", 8) or 8),
    )
    helper_pointer: dict[str, Any] = {
        "command": "artifact-engine",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "engine_identity": _durable_artifact_aware_live_primary_engine_identity(),
            **preview,
        }

    return {
        "engine_identity": state.get("engine_identity", _durable_artifact_aware_live_primary_engine_identity()),
        "compile_supported": bool(state.get("compile_supported", preview["compile_supported"])),
        "compiled_graph_present": bool(state.get("compiled_graph_present", preview["compiled_graph_present"])),
        "invoke_supported": bool(state.get("invoke_supported", preview["invoke_supported"])),
        "stream_supported": bool(state.get("stream_supported", preview["stream_supported"])),
        "current_execution_node": str(state.get("current_execution_node", preview["current_execution_node"])),
        "mapped_phase": str(state.get("mapped_phase", preview["mapped_phase"])),
        "artifact_node_path": list(state.get("artifact_node_path", preview["artifact_node_path"])),
        "artifact_phase_path": list(state.get("artifact_phase_path", preview["artifact_phase_path"])),
        "artifact_transition_log": list(preview["artifact_transition_log"]),
        "artifact_state_kind": str(preview["artifact_state_kind"]),
        "implementation_brief_present": bool(preview["implementation_brief_present"]),
        "implementation_brief_id": str(preview["implementation_brief_id"]),
        "implementation_brief_source_evidence_ref_count": int(
            preview["implementation_brief_source_evidence_ref_count"]
        ),
        "survivor_queue_present": bool(preview["survivor_queue_present"]),
        "survivor_queue_kind": str(preview["survivor_queue_kind"]),
        "survivor_count": int(preview["survivor_count"]),
        "superstep_count": int(state.get("superstep_count", preview["superstep_count"])),
        "stop_boundary": str(state.get("stop_boundary", preview["stop_boundary"])),
        "terminal_reached": bool(state.get("terminal_reached", preview["terminal_reached"])),
        "recursion_limit_supported": bool(
            state.get("recursion_limit_supported", preview["recursion_limit_supported"])
        ),
        "remaining_steps_supported": bool(
            state.get("remaining_steps_supported", preview["remaining_steps_supported"])
        ),
        "recursion_limit": int(state.get("recursion_limit", preview["recursion_limit"])),
        "execution_posture": str(state.get("execution_posture", preview["execution_posture"])),
        "last_run_kind": str(state.get("last_run_kind", preview["last_run_kind"])),
        "last_run_status": str(state.get("last_run_status", preview["last_run_status"])),
        "last_run_reason": str(state.get("last_run_reason", preview["last_run_reason"])),
        "helper_pointer": helper_pointer,
    }


def _persist_durable_artifact_aware_live_primary_engine_state(
    thread: dict[str, Any], run_kind: str = "", recursion_limit: int = 8
) -> dict[str, Any]:
    run_kind = run_kind or str(thread.get("last_durable_artifact_aware_live_primary_engine_kind", "")) or "invoke"
    recursion_limit = int(
        recursion_limit or thread.get("last_durable_artifact_aware_live_primary_engine_recursion_limit", 8) or 8
    )
    result = _execute_durable_artifact_aware_live_primary_engine(thread, run_kind, recursion_limit)
    stored = {
        "engine_identity": _durable_artifact_aware_live_primary_engine_identity(),
        "compile_supported": result["compile_supported"],
        "compiled_graph_present": result["compiled_graph_present"],
        "invoke_supported": result["invoke_supported"],
        "stream_supported": result["stream_supported"],
        "current_execution_node": result["current_execution_node"],
        "mapped_phase": result["mapped_phase"],
        "artifact_node_path": result["artifact_node_path"],
        "artifact_phase_path": result["artifact_phase_path"],
        "artifact_transition_log": result["artifact_transition_log"],
        "artifact_state_kind": result["artifact_state_kind"],
        "implementation_brief_present": result["implementation_brief_present"],
        "implementation_brief_id": result["implementation_brief_id"],
        "implementation_brief_source_evidence_ref_count": result[
            "implementation_brief_source_evidence_ref_count"
        ],
        "survivor_queue_present": result["survivor_queue_present"],
        "survivor_queue_kind": result["survivor_queue_kind"],
        "survivor_count": result["survivor_count"],
        "superstep_count": result["superstep_count"],
        "stop_boundary": result["stop_boundary"],
        "terminal_reached": result["terminal_reached"],
        "recursion_limit_supported": result["recursion_limit_supported"],
        "remaining_steps_supported": result["remaining_steps_supported"],
        "recursion_limit": result["recursion_limit"],
        "execution_posture": result["execution_posture"],
        "last_run_kind": result["last_run_kind"],
        "last_run_status": result["last_run_status"],
        "last_run_reason": result["last_run_reason"],
        "updated_at": _now(),
    }
    thread["last_durable_artifact_aware_live_primary_engine_kind"] = run_kind
    thread["last_durable_artifact_aware_live_primary_engine_reason"] = result["last_run_reason"]
    thread["last_durable_artifact_aware_live_primary_engine_recursion_limit"] = recursion_limit
    thread["durable_artifact_aware_live_primary_engine_state"] = stored
    return stored


def _reducer_aware_live_primary_engine_identity() -> dict[str, Any]:
    return _clone_payload(REDUCER_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY)


def _reducer_transition_log(
    base_log: list[str],
    reducer_projection: dict[str, Any],
) -> list[str]:
    transition_log = [str(item) for item in base_log if str(item)]
    fanout_state = str(reducer_projection.get("fanout_state", ""))
    merge_channels_updated = [
        str(item) for item in reducer_projection.get("merge_channels_updated", []) if str(item)
    ]
    source_records = [str(item) for item in reducer_projection.get("source_records", []) if str(item)]
    invalid_updates = reducer_projection.get("invalid_multi_writer_updates", [])

    if fanout_state:
        transition_log.append(f"fanout:{fanout_state}")
    if merge_channels_updated:
        transition_log.append(f"merge_channels:{len(merge_channels_updated)}")
    if invalid_updates:
        transition_log.append(f"invalid_multi_writer:{len(invalid_updates)}")
    if source_records:
        transition_log.append(f"reducer_sources:{len(source_records)}")
    return list(dict.fromkeys(transition_log))


def _reducer_merge_state_kind(reducer_projection: dict[str, Any]) -> str:
    compatibility = str(reducer_projection.get("compatibility", "pre_reducer"))
    merge_channels_updated = reducer_projection.get("merge_channels_updated", [])
    source_records = reducer_projection.get("source_records", [])
    invalid_multi_writer_detected = bool(reducer_projection.get("invalid_multi_writer_detected", False))
    if compatibility == "pre_reducer":
        return "pre_reducer"
    if invalid_multi_writer_detected:
        return "invalid_multi_writer_detected"
    if merge_channels_updated and len(source_records) > 1:
        return "multi_branch_merge"
    if merge_channels_updated:
        return "single_branch_merge"
    if compatibility == "reducer_aware":
        return "reducer_ready"
    return "ordinary"


def _reducer_aware_live_primary_engine_preview(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }

    artifact_preview = _durable_artifact_aware_live_primary_engine_preview(thread, run_kind, recursion_limit)
    reducer_projection = _reducer_projection(thread)
    merge_state_kind = _reducer_merge_state_kind(reducer_projection)
    merge_node_path = list(artifact_preview.get("artifact_node_path", []))
    merge_phase_path = list(artifact_preview.get("artifact_phase_path", []))
    merge_transition_log = _reducer_transition_log(
        list(artifact_preview.get("artifact_transition_log", [])),
        reducer_projection,
    )
    channel_item_counts = {
        str(name): int(count or 0)
        for name, count in dict(reducer_projection.get("channel_item_counts", {})).items()
    }
    invalid_updates = [
        dict(item) for item in reducer_projection.get("invalid_multi_writer_updates", []) if isinstance(item, dict)
    ]

    return {
        **metadata,
        "current_execution_node": artifact_preview["current_execution_node"],
        "mapped_phase": artifact_preview["mapped_phase"],
        "merge_node_path": merge_node_path,
        "merge_phase_path": merge_phase_path,
        "merge_transition_log": merge_transition_log,
        "merge_state_kind": merge_state_kind,
        "reducer_compatibility": str(reducer_projection.get("compatibility", "pre_reducer")),
        "fanout_state": str(reducer_projection.get("fanout_state", "unknown")),
        "invalid_multi_writer_detected": bool(
            reducer_projection.get("invalid_multi_writer_detected", False)
        ),
        "invalid_multi_writer_updates": invalid_updates,
        "merge_channels_updated": [
            str(item) for item in reducer_projection.get("merge_channels_updated", []) if str(item)
        ],
        "channel_item_counts": channel_item_counts,
        "source_records": [str(item) for item in reducer_projection.get("source_records", []) if str(item)],
        "superstep_count": int(artifact_preview["superstep_count"]),
        "stop_boundary": artifact_preview["stop_boundary"],
        "terminal_reached": bool(artifact_preview["terminal_reached"]),
        "recursion_limit_supported": bool(artifact_preview["recursion_limit_supported"]),
        "remaining_steps_supported": bool(artifact_preview["remaining_steps_supported"]),
        "recursion_limit": int(artifact_preview["recursion_limit"]),
        "execution_posture": artifact_preview["execution_posture"],
        "last_run_kind": run_kind,
        "last_run_status": artifact_preview["last_run_status"],
        "last_run_reason": artifact_preview["last_run_reason"],
    }


def _build_reducer_aware_live_primary_engine_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class ReducerAwareEngineState(TypedDict, total=False):
            merge_node_path: list[str]
            merge_phase_path: list[str]
            merge_transition_log: list[str]
            merge_state_kind: str
            reducer_compatibility: str
            fanout_state: str
            invalid_multi_writer_detected: bool
            invalid_multi_writer_updates: list[dict[str, Any]]
            merge_channels_updated: list[str]
            channel_item_counts: dict[str, int]
            source_records: list[str]
            superstep_count: int
            stop_boundary: str
            terminal_reached: bool
            recursion_limit: int

        def passthrough(state: ReducerAwareEngineState) -> ReducerAwareEngineState:
            return state

        builder = StateGraph(ReducerAwareEngineState)
        builder.add_node("reducer_state", passthrough)
        builder.add_edge(START, "reducer_state")
        builder.add_edge("reducer_state", END)
        compiled = builder.compile()
        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return compiled, metadata
    except Exception as exc:  # pragma: no cover
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_reducer_aware_live_primary_engine(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    preview = _reducer_aware_live_primary_engine_preview(thread, run_kind, recursion_limit)
    compiled, metadata = _build_reducer_aware_live_primary_engine_graph()
    if compiled is None:
        unavailable_posture = (
            preview["execution_posture"]
            if preview["execution_posture"] in {"interrupt_wait", "recovery_wait", "terminal", "recursion_limited"}
            else "unavailable"
        )
        unavailable_status = (
            preview["last_run_status"] if preview["last_run_status"] in {"blocked", "noop", "ok"} else "unavailable"
        )
        return {
            **preview,
            **metadata,
            "execution_posture": unavailable_posture,
            "last_run_status": unavailable_status,
            "last_run_reason": metadata["compile_error"] or preview["last_run_reason"],
        }

    try:
        input_payload = {
            "merge_node_path": list(preview["merge_node_path"]),
            "merge_phase_path": list(preview["merge_phase_path"]),
            "merge_transition_log": list(preview["merge_transition_log"]),
            "merge_state_kind": preview["merge_state_kind"],
            "reducer_compatibility": preview["reducer_compatibility"],
            "fanout_state": preview["fanout_state"],
            "invalid_multi_writer_detected": preview["invalid_multi_writer_detected"],
            "invalid_multi_writer_updates": list(preview["invalid_multi_writer_updates"]),
            "merge_channels_updated": list(preview["merge_channels_updated"]),
            "channel_item_counts": dict(preview["channel_item_counts"]),
            "source_records": list(preview["source_records"]),
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit": preview["recursion_limit"],
        }
        if run_kind == "stream":
            chunks = list(compiled.stream(input_payload))
            output = chunks[-1] if chunks else {}
        else:
            output = compiled.invoke(input_payload)
        output_dict = output if isinstance(output, dict) else {}
        return {
            **metadata,
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "merge_node_path": list(output_dict.get("merge_node_path", preview["merge_node_path"])),
            "merge_phase_path": list(output_dict.get("merge_phase_path", preview["merge_phase_path"])),
            "merge_transition_log": list(output_dict.get("merge_transition_log", preview["merge_transition_log"])),
            "merge_state_kind": str(output_dict.get("merge_state_kind", preview["merge_state_kind"])),
            "reducer_compatibility": str(
                output_dict.get("reducer_compatibility", preview["reducer_compatibility"])
            ),
            "fanout_state": str(output_dict.get("fanout_state", preview["fanout_state"])),
            "invalid_multi_writer_detected": bool(
                output_dict.get("invalid_multi_writer_detected", preview["invalid_multi_writer_detected"])
            ),
            "invalid_multi_writer_updates": [
                dict(item)
                for item in output_dict.get("invalid_multi_writer_updates", preview["invalid_multi_writer_updates"])
                if isinstance(item, dict)
            ],
            "merge_channels_updated": [
                str(item)
                for item in output_dict.get("merge_channels_updated", preview["merge_channels_updated"])
                if str(item)
            ],
            "channel_item_counts": {
                str(name): int(count or 0)
                for name, count in dict(
                    output_dict.get("channel_item_counts", preview["channel_item_counts"])
                ).items()
            },
            "source_records": [
                str(item) for item in output_dict.get("source_records", preview["source_records"]) if str(item)
            ],
            "superstep_count": int(output_dict.get("superstep_count", preview["superstep_count"])),
            "stop_boundary": str(output_dict.get("stop_boundary", preview["stop_boundary"])),
            "terminal_reached": bool(output_dict.get("terminal_reached", preview["terminal_reached"])),
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": int(output_dict.get("recursion_limit", preview["recursion_limit"])),
            "execution_posture": preview["execution_posture"],
            "last_run_kind": run_kind,
            "last_run_status": "ok" if preview["last_run_status"] != "blocked" else "blocked",
            "last_run_reason": preview["last_run_reason"],
        }
    except Exception as exc:  # pragma: no cover
        return {
            **preview,
            **metadata,
            "execution_posture": "execution_failed",
            "last_run_status": "error",
            "last_run_reason": str(exc),
        }


def _reducer_aware_live_primary_engine_projection(
    thread: dict[str, Any], thread_id: str = ""
) -> dict[str, Any]:
    state = thread.get("reducer_aware_live_primary_engine_state")
    preview = _reducer_aware_live_primary_engine_preview(
        thread,
        str(thread.get("last_reducer_aware_live_primary_engine_kind", "")) or "invoke",
        int(thread.get("last_reducer_aware_live_primary_engine_recursion_limit", 8) or 8),
    )
    helper_pointer: dict[str, Any] = {
        "command": "reducer-engine",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "engine_identity": _reducer_aware_live_primary_engine_identity(),
            **preview,
        }

    return {
        "engine_identity": state.get("engine_identity", _reducer_aware_live_primary_engine_identity()),
        "compile_supported": bool(state.get("compile_supported", preview["compile_supported"])),
        "compiled_graph_present": bool(state.get("compiled_graph_present", preview["compiled_graph_present"])),
        "invoke_supported": bool(state.get("invoke_supported", preview["invoke_supported"])),
        "stream_supported": bool(state.get("stream_supported", preview["stream_supported"])),
        "current_execution_node": str(state.get("current_execution_node", preview["current_execution_node"])),
        "mapped_phase": str(state.get("mapped_phase", preview["mapped_phase"])),
        "merge_node_path": list(state.get("merge_node_path", preview["merge_node_path"])),
        "merge_phase_path": list(state.get("merge_phase_path", preview["merge_phase_path"])),
        "merge_transition_log": list(preview["merge_transition_log"]),
        "merge_state_kind": str(preview["merge_state_kind"]),
        "reducer_compatibility": str(preview["reducer_compatibility"]),
        "fanout_state": str(preview["fanout_state"]),
        "invalid_multi_writer_detected": bool(preview["invalid_multi_writer_detected"]),
        "invalid_multi_writer_updates": list(preview["invalid_multi_writer_updates"]),
        "merge_channels_updated": list(preview["merge_channels_updated"]),
        "channel_item_counts": dict(preview["channel_item_counts"]),
        "source_records": list(preview["source_records"]),
        "superstep_count": int(state.get("superstep_count", preview["superstep_count"])),
        "stop_boundary": str(state.get("stop_boundary", preview["stop_boundary"])),
        "terminal_reached": bool(state.get("terminal_reached", preview["terminal_reached"])),
        "recursion_limit_supported": bool(
            state.get("recursion_limit_supported", preview["recursion_limit_supported"])
        ),
        "remaining_steps_supported": bool(
            state.get("remaining_steps_supported", preview["remaining_steps_supported"])
        ),
        "recursion_limit": int(state.get("recursion_limit", preview["recursion_limit"])),
        "execution_posture": str(state.get("execution_posture", preview["execution_posture"])),
        "last_run_kind": str(state.get("last_run_kind", preview["last_run_kind"])),
        "last_run_status": str(state.get("last_run_status", preview["last_run_status"])),
        "last_run_reason": str(state.get("last_run_reason", preview["last_run_reason"])),
        "helper_pointer": helper_pointer,
    }


def _persist_reducer_aware_live_primary_engine_state(
    thread: dict[str, Any], run_kind: str = "", recursion_limit: int = 8
) -> dict[str, Any]:
    run_kind = run_kind or str(thread.get("last_reducer_aware_live_primary_engine_kind", "")) or "invoke"
    recursion_limit = int(
        recursion_limit or thread.get("last_reducer_aware_live_primary_engine_recursion_limit", 8) or 8
    )
    result = _execute_reducer_aware_live_primary_engine(thread, run_kind, recursion_limit)
    stored = {
        "engine_identity": _reducer_aware_live_primary_engine_identity(),
        "compile_supported": result["compile_supported"],
        "compiled_graph_present": result["compiled_graph_present"],
        "invoke_supported": result["invoke_supported"],
        "stream_supported": result["stream_supported"],
        "current_execution_node": result["current_execution_node"],
        "mapped_phase": result["mapped_phase"],
        "merge_node_path": result["merge_node_path"],
        "merge_phase_path": result["merge_phase_path"],
        "merge_transition_log": result["merge_transition_log"],
        "merge_state_kind": result["merge_state_kind"],
        "reducer_compatibility": result["reducer_compatibility"],
        "fanout_state": result["fanout_state"],
        "invalid_multi_writer_detected": result["invalid_multi_writer_detected"],
        "invalid_multi_writer_updates": result["invalid_multi_writer_updates"],
        "merge_channels_updated": result["merge_channels_updated"],
        "channel_item_counts": result["channel_item_counts"],
        "source_records": result["source_records"],
        "superstep_count": result["superstep_count"],
        "stop_boundary": result["stop_boundary"],
        "terminal_reached": result["terminal_reached"],
        "recursion_limit_supported": result["recursion_limit_supported"],
        "remaining_steps_supported": result["remaining_steps_supported"],
        "recursion_limit": result["recursion_limit"],
        "execution_posture": result["execution_posture"],
        "last_run_kind": result["last_run_kind"],
        "last_run_status": result["last_run_status"],
        "last_run_reason": result["last_run_reason"],
        "updated_at": _now(),
    }
    thread["last_reducer_aware_live_primary_engine_kind"] = run_kind
    thread["last_reducer_aware_live_primary_engine_reason"] = result["last_run_reason"]
    thread["last_reducer_aware_live_primary_engine_recursion_limit"] = recursion_limit
    thread["reducer_aware_live_primary_engine_state"] = stored
    return stored


def _command_aware_live_primary_engine_identity() -> dict[str, Any]:
    return _clone_payload(COMMAND_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY)


def _command_control_state_kind(command_projection: dict[str, Any]) -> str:
    transition_kind = str(command_projection.get("transition_kind", ""))
    resume_posture = str(command_projection.get("resume_posture", "ordinary"))
    if resume_posture == "awaiting_command_resume":
        return "awaiting_command_resume"
    if transition_kind in {"parent_handoff", "resume_parent_handoff"}:
        return "parent_handoff_control"
    if transition_kind in {"goto", "update_goto"}:
        return "goto_control"
    if transition_kind in {"resume", "resume_with_payload"}:
        return "resume_control"
    if transition_kind == "update":
        return "update_control"
    if transition_kind:
        return "command_control"
    return "ordinary"


def _command_transition_log(
    base_log: list[str],
    command_projection: dict[str, Any],
) -> list[str]:
    transition_log = [str(item) for item in base_log if str(item)]
    transition_kind = str(command_projection.get("transition_kind", ""))
    graph_scope = str(command_projection.get("graph_scope", ""))
    goto_target = str(command_projection.get("goto_target", ""))
    parent_handoff_target = str(command_projection.get("parent_handoff_target", ""))
    resume_posture = str(command_projection.get("resume_posture", "ordinary"))
    update_keys = [str(item) for item in command_projection.get("update_keys", []) if str(item)]
    resume_payload_keys = [str(item) for item in command_projection.get("resume_payload_keys", []) if str(item)]

    if transition_kind:
        transition_log.append(f"command:{transition_kind}")
    if graph_scope:
        transition_log.append(f"graph_scope:{graph_scope}")
    if goto_target:
        transition_log.append(f"goto:{goto_target}")
    if parent_handoff_target:
        transition_log.append(f"parent_handoff:{parent_handoff_target}")
    if update_keys:
        transition_log.append(f"update_keys:{len(update_keys)}")
    if resume_posture and resume_posture != "ordinary":
        transition_log.append(f"resume:{resume_posture}")
    if resume_payload_keys:
        transition_log.append(f"resume_payload:{len(resume_payload_keys)}")
    return list(dict.fromkeys(transition_log))


def _command_aware_live_primary_engine_preview(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }

    reducer_preview = _reducer_aware_live_primary_engine_preview(thread, run_kind, recursion_limit)
    command_projection = _command_projection(thread)
    control_state_kind = _command_control_state_kind(command_projection)
    command_node_path = list(reducer_preview.get("merge_node_path", []))
    command_phase_path = list(reducer_preview.get("merge_phase_path", []))
    command_transition_log = _command_transition_log(
        list(reducer_preview.get("merge_transition_log", [])),
        command_projection,
    )

    return {
        **metadata,
        "current_execution_node": reducer_preview["current_execution_node"],
        "mapped_phase": reducer_preview["mapped_phase"],
        "command_node_path": command_node_path,
        "command_phase_path": command_phase_path,
        "command_transition_log": command_transition_log,
        "control_state_kind": control_state_kind,
        "transition_kind": str(command_projection.get("transition_kind", "")),
        "update_keys": [str(item) for item in command_projection.get("update_keys", []) if str(item)],
        "goto_target": str(command_projection.get("goto_target", "")),
        "graph_scope": str(command_projection.get("graph_scope", "")),
        "source_subgraph": str(command_projection.get("source_subgraph", "")),
        "target_subgraph": str(command_projection.get("target_subgraph", "")),
        "parent_handoff_target": str(command_projection.get("parent_handoff_target", "")),
        "resume_posture": str(command_projection.get("resume_posture", "ordinary")),
        "resume_payload_present": bool(command_projection.get("resume_payload_present", False)),
        "resume_payload_keys": [
            str(item) for item in command_projection.get("resume_payload_keys", []) if str(item)
        ],
        "superstep_count": int(reducer_preview["superstep_count"]),
        "stop_boundary": reducer_preview["stop_boundary"],
        "terminal_reached": bool(reducer_preview["terminal_reached"]),
        "recursion_limit_supported": bool(reducer_preview["recursion_limit_supported"]),
        "remaining_steps_supported": bool(reducer_preview["remaining_steps_supported"]),
        "recursion_limit": int(reducer_preview["recursion_limit"]),
        "execution_posture": reducer_preview["execution_posture"],
        "last_run_kind": run_kind,
        "last_run_status": reducer_preview["last_run_status"],
        "last_run_reason": reducer_preview["last_run_reason"],
    }


def _build_command_aware_live_primary_engine_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class CommandAwareEngineState(TypedDict, total=False):
            command_node_path: list[str]
            command_phase_path: list[str]
            command_transition_log: list[str]
            control_state_kind: str
            transition_kind: str
            update_keys: list[str]
            goto_target: str
            graph_scope: str
            source_subgraph: str
            target_subgraph: str
            parent_handoff_target: str
            resume_posture: str
            resume_payload_present: bool
            resume_payload_keys: list[str]
            superstep_count: int
            stop_boundary: str
            terminal_reached: bool
            recursion_limit: int

        def passthrough(state: CommandAwareEngineState) -> CommandAwareEngineState:
            return state

        builder = StateGraph(CommandAwareEngineState)
        builder.add_node("command_state", passthrough)
        builder.add_edge(START, "command_state")
        builder.add_edge("command_state", END)
        compiled = builder.compile()
        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return compiled, metadata
    except Exception as exc:  # pragma: no cover
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_command_aware_live_primary_engine(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    preview = _command_aware_live_primary_engine_preview(thread, run_kind, recursion_limit)
    compiled, metadata = _build_command_aware_live_primary_engine_graph()
    if compiled is None:
        unavailable_posture = (
            preview["execution_posture"]
            if preview["execution_posture"] in {"interrupt_wait", "recovery_wait", "terminal", "recursion_limited"}
            else "unavailable"
        )
        unavailable_status = (
            preview["last_run_status"] if preview["last_run_status"] in {"blocked", "noop", "ok"} else "unavailable"
        )
        return {
            **preview,
            **metadata,
            "execution_posture": unavailable_posture,
            "last_run_status": unavailable_status,
            "last_run_reason": metadata["compile_error"] or preview["last_run_reason"],
        }

    try:
        input_payload = {
            "command_node_path": list(preview["command_node_path"]),
            "command_phase_path": list(preview["command_phase_path"]),
            "command_transition_log": list(preview["command_transition_log"]),
            "control_state_kind": preview["control_state_kind"],
            "transition_kind": preview["transition_kind"],
            "update_keys": list(preview["update_keys"]),
            "goto_target": preview["goto_target"],
            "graph_scope": preview["graph_scope"],
            "source_subgraph": preview["source_subgraph"],
            "target_subgraph": preview["target_subgraph"],
            "parent_handoff_target": preview["parent_handoff_target"],
            "resume_posture": preview["resume_posture"],
            "resume_payload_present": preview["resume_payload_present"],
            "resume_payload_keys": list(preview["resume_payload_keys"]),
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit": preview["recursion_limit"],
        }
        if run_kind == "stream":
            chunks = list(compiled.stream(input_payload))
            output = chunks[-1] if chunks else {}
        else:
            output = compiled.invoke(input_payload)
        output_dict = output if isinstance(output, dict) else {}
        return {
            **metadata,
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "command_node_path": list(output_dict.get("command_node_path", preview["command_node_path"])),
            "command_phase_path": list(output_dict.get("command_phase_path", preview["command_phase_path"])),
            "command_transition_log": list(
                output_dict.get("command_transition_log", preview["command_transition_log"])
            ),
            "control_state_kind": str(output_dict.get("control_state_kind", preview["control_state_kind"])),
            "transition_kind": str(output_dict.get("transition_kind", preview["transition_kind"])),
            "update_keys": [str(item) for item in output_dict.get("update_keys", preview["update_keys"]) if str(item)],
            "goto_target": str(output_dict.get("goto_target", preview["goto_target"])),
            "graph_scope": str(output_dict.get("graph_scope", preview["graph_scope"])),
            "source_subgraph": str(output_dict.get("source_subgraph", preview["source_subgraph"])),
            "target_subgraph": str(output_dict.get("target_subgraph", preview["target_subgraph"])),
            "parent_handoff_target": str(
                output_dict.get("parent_handoff_target", preview["parent_handoff_target"])
            ),
            "resume_posture": str(output_dict.get("resume_posture", preview["resume_posture"])),
            "resume_payload_present": bool(
                output_dict.get("resume_payload_present", preview["resume_payload_present"])
            ),
            "resume_payload_keys": [
                str(item)
                for item in output_dict.get("resume_payload_keys", preview["resume_payload_keys"])
                if str(item)
            ],
            "superstep_count": int(output_dict.get("superstep_count", preview["superstep_count"])),
            "stop_boundary": str(output_dict.get("stop_boundary", preview["stop_boundary"])),
            "terminal_reached": bool(output_dict.get("terminal_reached", preview["terminal_reached"])),
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": int(output_dict.get("recursion_limit", preview["recursion_limit"])),
            "execution_posture": preview["execution_posture"],
            "last_run_kind": run_kind,
            "last_run_status": "ok" if preview["last_run_status"] != "blocked" else "blocked",
            "last_run_reason": preview["last_run_reason"],
        }
    except Exception as exc:  # pragma: no cover
        return {
            **preview,
            **metadata,
            "execution_posture": "execution_failed",
            "last_run_status": "error",
            "last_run_reason": str(exc),
        }


def _command_aware_live_primary_engine_projection(
    thread: dict[str, Any], thread_id: str = ""
) -> dict[str, Any]:
    state = thread.get("command_aware_live_primary_engine_state")
    preview = _command_aware_live_primary_engine_preview(
        thread,
        str(thread.get("last_command_aware_live_primary_engine_kind", "")) or "invoke",
        int(thread.get("last_command_aware_live_primary_engine_recursion_limit", 8) or 8),
    )
    helper_pointer: dict[str, Any] = {
        "command": "command-engine",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "engine_identity": _command_aware_live_primary_engine_identity(),
            **preview,
        }

    return {
        "engine_identity": state.get("engine_identity", _command_aware_live_primary_engine_identity()),
        "compile_supported": bool(state.get("compile_supported", preview["compile_supported"])),
        "compiled_graph_present": bool(state.get("compiled_graph_present", preview["compiled_graph_present"])),
        "invoke_supported": bool(state.get("invoke_supported", preview["invoke_supported"])),
        "stream_supported": bool(state.get("stream_supported", preview["stream_supported"])),
        "current_execution_node": str(state.get("current_execution_node", preview["current_execution_node"])),
        "mapped_phase": str(state.get("mapped_phase", preview["mapped_phase"])),
        "command_node_path": list(state.get("command_node_path", preview["command_node_path"])),
        "command_phase_path": list(state.get("command_phase_path", preview["command_phase_path"])),
        "command_transition_log": list(preview["command_transition_log"]),
        "control_state_kind": str(preview["control_state_kind"]),
        "transition_kind": str(preview["transition_kind"]),
        "update_keys": list(preview["update_keys"]),
        "goto_target": str(preview["goto_target"]),
        "graph_scope": str(preview["graph_scope"]),
        "source_subgraph": str(preview["source_subgraph"]),
        "target_subgraph": str(preview["target_subgraph"]),
        "parent_handoff_target": str(preview["parent_handoff_target"]),
        "resume_posture": str(preview["resume_posture"]),
        "resume_payload_present": bool(preview["resume_payload_present"]),
        "resume_payload_keys": list(preview["resume_payload_keys"]),
        "superstep_count": int(state.get("superstep_count", preview["superstep_count"])),
        "stop_boundary": str(state.get("stop_boundary", preview["stop_boundary"])),
        "terminal_reached": bool(state.get("terminal_reached", preview["terminal_reached"])),
        "recursion_limit_supported": bool(
            state.get("recursion_limit_supported", preview["recursion_limit_supported"])
        ),
        "remaining_steps_supported": bool(
            state.get("remaining_steps_supported", preview["remaining_steps_supported"])
        ),
        "recursion_limit": int(state.get("recursion_limit", preview["recursion_limit"])),
        "execution_posture": str(state.get("execution_posture", preview["execution_posture"])),
        "last_run_kind": str(state.get("last_run_kind", preview["last_run_kind"])),
        "last_run_status": str(state.get("last_run_status", preview["last_run_status"])),
        "last_run_reason": str(state.get("last_run_reason", preview["last_run_reason"])),
        "helper_pointer": helper_pointer,
    }


def _persist_command_aware_live_primary_engine_state(
    thread: dict[str, Any], run_kind: str = "", recursion_limit: int = 8
) -> dict[str, Any]:
    run_kind = run_kind or str(thread.get("last_command_aware_live_primary_engine_kind", "")) or "invoke"
    recursion_limit = int(
        recursion_limit or thread.get("last_command_aware_live_primary_engine_recursion_limit", 8) or 8
    )
    result = _execute_command_aware_live_primary_engine(thread, run_kind, recursion_limit)
    stored = {
        "engine_identity": _command_aware_live_primary_engine_identity(),
        "compile_supported": result["compile_supported"],
        "compiled_graph_present": result["compiled_graph_present"],
        "invoke_supported": result["invoke_supported"],
        "stream_supported": result["stream_supported"],
        "current_execution_node": result["current_execution_node"],
        "mapped_phase": result["mapped_phase"],
        "command_node_path": result["command_node_path"],
        "command_phase_path": result["command_phase_path"],
        "command_transition_log": result["command_transition_log"],
        "control_state_kind": result["control_state_kind"],
        "transition_kind": result["transition_kind"],
        "update_keys": result["update_keys"],
        "goto_target": result["goto_target"],
        "graph_scope": result["graph_scope"],
        "source_subgraph": result["source_subgraph"],
        "target_subgraph": result["target_subgraph"],
        "parent_handoff_target": result["parent_handoff_target"],
        "resume_posture": result["resume_posture"],
        "resume_payload_present": result["resume_payload_present"],
        "resume_payload_keys": result["resume_payload_keys"],
        "superstep_count": result["superstep_count"],
        "stop_boundary": result["stop_boundary"],
        "terminal_reached": result["terminal_reached"],
        "recursion_limit_supported": result["recursion_limit_supported"],
        "remaining_steps_supported": result["remaining_steps_supported"],
        "recursion_limit": result["recursion_limit"],
        "execution_posture": result["execution_posture"],
        "last_run_kind": result["last_run_kind"],
        "last_run_status": result["last_run_status"],
        "last_run_reason": result["last_run_reason"],
        "updated_at": _now(),
    }
    thread["last_command_aware_live_primary_engine_kind"] = run_kind
    thread["last_command_aware_live_primary_engine_reason"] = result["last_run_reason"]
    thread["last_command_aware_live_primary_engine_recursion_limit"] = recursion_limit
    thread["command_aware_live_primary_engine_state"] = stored
    return stored


def _runtime_aware_live_primary_engine_identity() -> dict[str, Any]:
    return _clone_payload(RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY)


def _runtime_state_kind(runtime_projection: dict[str, Any]) -> str:
    runtime_context_present = bool(runtime_projection.get("runtime_context_present", False))
    store_configured = bool(runtime_projection.get("store_configured", False))
    store_access_expected = bool(runtime_projection.get("store_access_expected", False))
    if runtime_context_present and store_configured:
        return "runtime_context_and_store_ready"
    if runtime_context_present:
        return "runtime_context_ready"
    if store_configured and store_access_expected:
        return "store_ready"
    if store_configured:
        return "store_configured"
    return "ordinary"


def _runtime_transition_log(
    base_log: list[str],
    runtime_projection: dict[str, Any],
) -> list[str]:
    transition_log = [str(item) for item in base_log if str(item)]
    context_schema = str(runtime_projection.get("context_schema", ""))
    runtime_context_keys = [
        str(item) for item in runtime_projection.get("runtime_context_keys", []) if str(item)
    ]
    runtime_context_kind_hints = [
        str(item) for item in runtime_projection.get("runtime_context_kind_hints", []) if str(item)
    ]
    store_kind = str(runtime_projection.get("store_kind", ""))
    if context_schema:
        transition_log.append(f"context_schema:{context_schema}")
    if runtime_projection.get("runtime_context_present"):
        transition_log.append(f"runtime_context_keys:{len(runtime_context_keys)}")
    if runtime_context_kind_hints:
        transition_log.append(f"runtime_hints:{len(runtime_context_kind_hints)}")
    if runtime_projection.get("store_configured"):
        transition_log.append(f"store:{store_kind or 'configured'}")
    if runtime_projection.get("store_access_expected"):
        transition_log.append("store_access:expected")
    return list(dict.fromkeys(transition_log))


def _runtime_aware_live_primary_engine_preview(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }

    command_preview = _command_aware_live_primary_engine_preview(thread, run_kind, recursion_limit)
    runtime_projection = _runtime_injection_projection(thread)
    runtime_state_kind = _runtime_state_kind(runtime_projection)
    runtime_node_path = list(command_preview.get("command_node_path", []))
    runtime_phase_path = list(command_preview.get("command_phase_path", []))
    runtime_transition_log = _runtime_transition_log(
        list(command_preview.get("command_transition_log", [])),
        runtime_projection,
    )

    return {
        **metadata,
        "current_execution_node": command_preview["current_execution_node"],
        "mapped_phase": command_preview["mapped_phase"],
        "runtime_node_path": runtime_node_path,
        "runtime_phase_path": runtime_phase_path,
        "runtime_transition_log": runtime_transition_log,
        "runtime_state_kind": runtime_state_kind,
        "context_schema": str(runtime_projection.get("context_schema", "")),
        "runtime_context_present": bool(runtime_projection.get("runtime_context_present", False)),
        "runtime_context_keys": [
            str(item) for item in runtime_projection.get("runtime_context_keys", []) if str(item)
        ],
        "runtime_context_kind_hints": [
            str(item) for item in runtime_projection.get("runtime_context_kind_hints", []) if str(item)
        ],
        "store_configured": bool(runtime_projection.get("store_configured", False)),
        "store_access_expected": bool(runtime_projection.get("store_access_expected", False)),
        "store_kind": str(runtime_projection.get("store_kind", "")),
        "superstep_count": int(command_preview["superstep_count"]),
        "stop_boundary": command_preview["stop_boundary"],
        "terminal_reached": bool(command_preview["terminal_reached"]),
        "recursion_limit_supported": bool(command_preview["recursion_limit_supported"]),
        "remaining_steps_supported": bool(command_preview["remaining_steps_supported"]),
        "recursion_limit": int(command_preview["recursion_limit"]),
        "execution_posture": command_preview["execution_posture"],
        "last_run_kind": run_kind,
        "last_run_status": command_preview["last_run_status"],
        "last_run_reason": command_preview["last_run_reason"],
    }


def _build_runtime_aware_live_primary_engine_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class RuntimeAwareEngineState(TypedDict, total=False):
            runtime_node_path: list[str]
            runtime_phase_path: list[str]
            runtime_transition_log: list[str]
            runtime_state_kind: str
            context_schema: str
            runtime_context_present: bool
            runtime_context_keys: list[str]
            runtime_context_kind_hints: list[str]
            store_configured: bool
            store_access_expected: bool
            store_kind: str
            superstep_count: int
            stop_boundary: str
            terminal_reached: bool
            recursion_limit: int

        def passthrough(state: RuntimeAwareEngineState) -> RuntimeAwareEngineState:
            return state

        builder = StateGraph(RuntimeAwareEngineState)
        builder.add_node("runtime_state", passthrough)
        builder.add_edge(START, "runtime_state")
        builder.add_edge("runtime_state", END)
        compiled = builder.compile()
        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return compiled, metadata
    except Exception as exc:  # pragma: no cover
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_runtime_aware_live_primary_engine(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    preview = _runtime_aware_live_primary_engine_preview(thread, run_kind, recursion_limit)
    compiled, metadata = _build_runtime_aware_live_primary_engine_graph()
    if compiled is None:
        unavailable_posture = (
            preview["execution_posture"]
            if preview["execution_posture"] in {"interrupt_wait", "recovery_wait", "terminal", "recursion_limited"}
            else "unavailable"
        )
        unavailable_status = (
            preview["last_run_status"] if preview["last_run_status"] in {"blocked", "noop", "ok"} else "unavailable"
        )
        return {
            **preview,
            **metadata,
            "execution_posture": unavailable_posture,
            "last_run_status": unavailable_status,
            "last_run_reason": metadata["compile_error"] or preview["last_run_reason"],
        }

    try:
        input_payload = {
            "runtime_node_path": list(preview["runtime_node_path"]),
            "runtime_phase_path": list(preview["runtime_phase_path"]),
            "runtime_transition_log": list(preview["runtime_transition_log"]),
            "runtime_state_kind": preview["runtime_state_kind"],
            "context_schema": preview["context_schema"],
            "runtime_context_present": preview["runtime_context_present"],
            "runtime_context_keys": list(preview["runtime_context_keys"]),
            "runtime_context_kind_hints": list(preview["runtime_context_kind_hints"]),
            "store_configured": preview["store_configured"],
            "store_access_expected": preview["store_access_expected"],
            "store_kind": preview["store_kind"],
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit": preview["recursion_limit"],
        }
        if run_kind == "stream":
            chunks = list(compiled.stream(input_payload))
            output = chunks[-1] if chunks else {}
        else:
            output = compiled.invoke(input_payload)
        output_dict = output if isinstance(output, dict) else {}
        return {
            **metadata,
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "runtime_node_path": list(output_dict.get("runtime_node_path", preview["runtime_node_path"])),
            "runtime_phase_path": list(output_dict.get("runtime_phase_path", preview["runtime_phase_path"])),
            "runtime_transition_log": list(
                output_dict.get("runtime_transition_log", preview["runtime_transition_log"])
            ),
            "runtime_state_kind": str(output_dict.get("runtime_state_kind", preview["runtime_state_kind"])),
            "context_schema": str(output_dict.get("context_schema", preview["context_schema"])),
            "runtime_context_present": bool(
                output_dict.get("runtime_context_present", preview["runtime_context_present"])
            ),
            "runtime_context_keys": [
                str(item)
                for item in output_dict.get("runtime_context_keys", preview["runtime_context_keys"])
                if str(item)
            ],
            "runtime_context_kind_hints": [
                str(item)
                for item in output_dict.get(
                    "runtime_context_kind_hints", preview["runtime_context_kind_hints"]
                )
                if str(item)
            ],
            "store_configured": bool(output_dict.get("store_configured", preview["store_configured"])),
            "store_access_expected": bool(
                output_dict.get("store_access_expected", preview["store_access_expected"])
            ),
            "store_kind": str(output_dict.get("store_kind", preview["store_kind"])),
            "superstep_count": int(output_dict.get("superstep_count", preview["superstep_count"])),
            "stop_boundary": str(output_dict.get("stop_boundary", preview["stop_boundary"])),
            "terminal_reached": bool(output_dict.get("terminal_reached", preview["terminal_reached"])),
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": int(output_dict.get("recursion_limit", preview["recursion_limit"])),
            "execution_posture": preview["execution_posture"],
            "last_run_kind": run_kind,
            "last_run_status": "ok" if preview["last_run_status"] != "blocked" else "blocked",
            "last_run_reason": preview["last_run_reason"],
        }
    except Exception as exc:  # pragma: no cover
        return {
            **preview,
            **metadata,
            "execution_posture": "execution_failed",
            "last_run_status": "error",
            "last_run_reason": str(exc),
        }


def _runtime_aware_live_primary_engine_projection(
    thread: dict[str, Any], thread_id: str = ""
) -> dict[str, Any]:
    state = thread.get("runtime_aware_live_primary_engine_state")
    preview = _runtime_aware_live_primary_engine_preview(
        thread,
        str(thread.get("last_runtime_aware_live_primary_engine_kind", "")) or "invoke",
        int(thread.get("last_runtime_aware_live_primary_engine_recursion_limit", 8) or 8),
    )
    helper_pointer: dict[str, Any] = {
        "command": "runtime-engine",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "engine_identity": _runtime_aware_live_primary_engine_identity(),
            **preview,
        }

    return {
        "engine_identity": state.get("engine_identity", _runtime_aware_live_primary_engine_identity()),
        "compile_supported": bool(state.get("compile_supported", preview["compile_supported"])),
        "compiled_graph_present": bool(state.get("compiled_graph_present", preview["compiled_graph_present"])),
        "invoke_supported": bool(state.get("invoke_supported", preview["invoke_supported"])),
        "stream_supported": bool(state.get("stream_supported", preview["stream_supported"])),
        "current_execution_node": str(state.get("current_execution_node", preview["current_execution_node"])),
        "mapped_phase": str(state.get("mapped_phase", preview["mapped_phase"])),
        "runtime_node_path": list(state.get("runtime_node_path", preview["runtime_node_path"])),
        "runtime_phase_path": list(state.get("runtime_phase_path", preview["runtime_phase_path"])),
        "runtime_transition_log": list(preview["runtime_transition_log"]),
        "runtime_state_kind": str(preview["runtime_state_kind"]),
        "context_schema": str(preview["context_schema"]),
        "runtime_context_present": bool(preview["runtime_context_present"]),
        "runtime_context_keys": list(preview["runtime_context_keys"]),
        "runtime_context_kind_hints": list(preview["runtime_context_kind_hints"]),
        "store_configured": bool(preview["store_configured"]),
        "store_access_expected": bool(preview["store_access_expected"]),
        "store_kind": str(preview["store_kind"]),
        "superstep_count": int(state.get("superstep_count", preview["superstep_count"])),
        "stop_boundary": str(state.get("stop_boundary", preview["stop_boundary"])),
        "terminal_reached": bool(state.get("terminal_reached", preview["terminal_reached"])),
        "recursion_limit_supported": bool(
            state.get("recursion_limit_supported", preview["recursion_limit_supported"])
        ),
        "remaining_steps_supported": bool(
            state.get("remaining_steps_supported", preview["remaining_steps_supported"])
        ),
        "recursion_limit": int(state.get("recursion_limit", preview["recursion_limit"])),
        "execution_posture": str(state.get("execution_posture", preview["execution_posture"])),
        "last_run_kind": str(state.get("last_run_kind", preview["last_run_kind"])),
        "last_run_status": str(state.get("last_run_status", preview["last_run_status"])),
        "last_run_reason": str(state.get("last_run_reason", preview["last_run_reason"])),
        "helper_pointer": helper_pointer,
    }


def _persist_runtime_aware_live_primary_engine_state(
    thread: dict[str, Any], run_kind: str = "", recursion_limit: int = 8
) -> dict[str, Any]:
    run_kind = run_kind or str(thread.get("last_runtime_aware_live_primary_engine_kind", "")) or "invoke"
    recursion_limit = int(
        recursion_limit or thread.get("last_runtime_aware_live_primary_engine_recursion_limit", 8) or 8
    )
    result = _execute_runtime_aware_live_primary_engine(thread, run_kind, recursion_limit)
    stored = {
        "engine_identity": _runtime_aware_live_primary_engine_identity(),
        "compile_supported": result["compile_supported"],
        "compiled_graph_present": result["compiled_graph_present"],
        "invoke_supported": result["invoke_supported"],
        "stream_supported": result["stream_supported"],
        "current_execution_node": result["current_execution_node"],
        "mapped_phase": result["mapped_phase"],
        "runtime_node_path": result["runtime_node_path"],
        "runtime_phase_path": result["runtime_phase_path"],
        "runtime_transition_log": result["runtime_transition_log"],
        "runtime_state_kind": result["runtime_state_kind"],
        "context_schema": result["context_schema"],
        "runtime_context_present": result["runtime_context_present"],
        "runtime_context_keys": result["runtime_context_keys"],
        "runtime_context_kind_hints": result["runtime_context_kind_hints"],
        "store_configured": result["store_configured"],
        "store_access_expected": result["store_access_expected"],
        "store_kind": result["store_kind"],
        "superstep_count": result["superstep_count"],
        "stop_boundary": result["stop_boundary"],
        "terminal_reached": result["terminal_reached"],
        "recursion_limit_supported": result["recursion_limit_supported"],
        "remaining_steps_supported": result["remaining_steps_supported"],
        "recursion_limit": result["recursion_limit"],
        "execution_posture": result["execution_posture"],
        "last_run_kind": result["last_run_kind"],
        "last_run_status": result["last_run_status"],
        "last_run_reason": result["last_run_reason"],
        "updated_at": _now(),
    }
    thread["last_runtime_aware_live_primary_engine_kind"] = run_kind
    thread["last_runtime_aware_live_primary_engine_reason"] = result["last_run_reason"]
    thread["last_runtime_aware_live_primary_engine_recursion_limit"] = recursion_limit
    thread["runtime_aware_live_primary_engine_state"] = stored
    return stored


def _memory_aware_live_primary_engine_identity() -> dict[str, Any]:
    return _clone_payload(MEMORY_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY)


def _memory_state_kind(memory_projection: dict[str, Any]) -> str:
    memory_store_configured = bool(memory_projection.get("memory_store_configured", False))
    semantic_memory_enabled = bool(memory_projection.get("semantic_memory_enabled", False))
    if memory_store_configured and semantic_memory_enabled:
        return "memory_and_semantic_ready"
    if semantic_memory_enabled:
        return "semantic_memory_ready"
    if memory_store_configured:
        return "memory_store_ready"
    return "ordinary"


def _memory_transition_log(
    base_log: list[str],
    memory_projection: dict[str, Any],
) -> list[str]:
    transition_log = [str(item) for item in base_log if str(item)]
    memory_store_kind = str(memory_projection.get("memory_store_kind", ""))
    memory_namespaces = [str(item) for item in memory_projection.get("memory_namespaces", []) if str(item)]
    semantic_store_kind = str(memory_projection.get("semantic_store_kind", ""))
    semantic_namespaces = [str(item) for item in memory_projection.get("semantic_namespaces", []) if str(item)]
    if memory_projection.get("memory_store_configured"):
        transition_log.append(f"memory_store:{memory_store_kind or 'configured'}")
    if memory_namespaces:
        transition_log.append(f"memory_namespaces:{len(memory_namespaces)}")
    if memory_projection.get("semantic_memory_enabled"):
        transition_log.append(f"semantic_store:{semantic_store_kind or 'enabled'}")
    if semantic_namespaces:
        transition_log.append(f"semantic_namespaces:{len(semantic_namespaces)}")
    return list(dict.fromkeys(transition_log))


def _memory_aware_live_primary_engine_preview(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }

    runtime_preview = _runtime_aware_live_primary_engine_preview(thread, run_kind, recursion_limit)
    memory_projection = _memory_projection(thread)
    memory_state_kind = _memory_state_kind(memory_projection)
    memory_node_path = list(runtime_preview.get("runtime_node_path", []))
    memory_phase_path = list(runtime_preview.get("runtime_phase_path", []))
    memory_transition_log = _memory_transition_log(
        list(runtime_preview.get("runtime_transition_log", [])),
        memory_projection,
    )

    return {
        **metadata,
        "current_execution_node": runtime_preview["current_execution_node"],
        "mapped_phase": runtime_preview["mapped_phase"],
        "memory_node_path": memory_node_path,
        "memory_phase_path": memory_phase_path,
        "memory_transition_log": memory_transition_log,
        "memory_state_kind": memory_state_kind,
        "memory_store_configured": bool(memory_projection.get("memory_store_configured", False)),
        "memory_store_kind": str(memory_projection.get("memory_store_kind", "")),
        "memory_namespaces": [str(item) for item in memory_projection.get("memory_namespaces", []) if str(item)],
        "semantic_memory_enabled": bool(memory_projection.get("semantic_memory_enabled", False)),
        "semantic_store_kind": str(memory_projection.get("semantic_store_kind", "")),
        "semantic_namespaces": [str(item) for item in memory_projection.get("semantic_namespaces", []) if str(item)],
        "superstep_count": int(runtime_preview["superstep_count"]),
        "stop_boundary": runtime_preview["stop_boundary"],
        "terminal_reached": bool(runtime_preview["terminal_reached"]),
        "recursion_limit_supported": bool(runtime_preview["recursion_limit_supported"]),
        "remaining_steps_supported": bool(runtime_preview["remaining_steps_supported"]),
        "recursion_limit": int(runtime_preview["recursion_limit"]),
        "execution_posture": runtime_preview["execution_posture"],
        "last_run_kind": run_kind,
        "last_run_status": runtime_preview["last_run_status"],
        "last_run_reason": runtime_preview["last_run_reason"],
    }


def _build_memory_aware_live_primary_engine_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class MemoryAwareEngineState(TypedDict, total=False):
            memory_node_path: list[str]
            memory_phase_path: list[str]
            memory_transition_log: list[str]
            memory_state_kind: str
            memory_store_configured: bool
            memory_store_kind: str
            memory_namespaces: list[str]
            semantic_memory_enabled: bool
            semantic_store_kind: str
            semantic_namespaces: list[str]
            superstep_count: int
            stop_boundary: str
            terminal_reached: bool
            recursion_limit: int

        def passthrough(state: MemoryAwareEngineState) -> MemoryAwareEngineState:
            return state

        builder = StateGraph(MemoryAwareEngineState)
        builder.add_node("memory_state", passthrough)
        builder.add_edge(START, "memory_state")
        builder.add_edge("memory_state", END)
        compiled = builder.compile()
        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return compiled, metadata
    except Exception as exc:  # pragma: no cover
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_memory_aware_live_primary_engine(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    preview = _memory_aware_live_primary_engine_preview(thread, run_kind, recursion_limit)
    compiled, metadata = _build_memory_aware_live_primary_engine_graph()
    if compiled is None:
        unavailable_posture = (
            preview["execution_posture"]
            if preview["execution_posture"] in {"interrupt_wait", "recovery_wait", "terminal", "recursion_limited"}
            else "unavailable"
        )
        unavailable_status = (
            preview["last_run_status"] if preview["last_run_status"] in {"blocked", "noop", "ok"} else "unavailable"
        )
        return {
            **preview,
            **metadata,
            "execution_posture": unavailable_posture,
            "last_run_status": unavailable_status,
            "last_run_reason": metadata["compile_error"] or preview["last_run_reason"],
        }

    try:
        input_payload = {
            "memory_node_path": list(preview["memory_node_path"]),
            "memory_phase_path": list(preview["memory_phase_path"]),
            "memory_transition_log": list(preview["memory_transition_log"]),
            "memory_state_kind": preview["memory_state_kind"],
            "memory_store_configured": preview["memory_store_configured"],
            "memory_store_kind": preview["memory_store_kind"],
            "memory_namespaces": list(preview["memory_namespaces"]),
            "semantic_memory_enabled": preview["semantic_memory_enabled"],
            "semantic_store_kind": preview["semantic_store_kind"],
            "semantic_namespaces": list(preview["semantic_namespaces"]),
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit": preview["recursion_limit"],
        }
        if run_kind == "stream":
            chunks = list(compiled.stream(input_payload))
            output = chunks[-1] if chunks else {}
        else:
            output = compiled.invoke(input_payload)
        output_dict = output if isinstance(output, dict) else {}
        return {
            **metadata,
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "memory_node_path": list(output_dict.get("memory_node_path", preview["memory_node_path"])),
            "memory_phase_path": list(output_dict.get("memory_phase_path", preview["memory_phase_path"])),
            "memory_transition_log": list(
                output_dict.get("memory_transition_log", preview["memory_transition_log"])
            ),
            "memory_state_kind": str(output_dict.get("memory_state_kind", preview["memory_state_kind"])),
            "memory_store_configured": bool(
                output_dict.get("memory_store_configured", preview["memory_store_configured"])
            ),
            "memory_store_kind": str(output_dict.get("memory_store_kind", preview["memory_store_kind"])),
            "memory_namespaces": [
                str(item) for item in output_dict.get("memory_namespaces", preview["memory_namespaces"]) if str(item)
            ],
            "semantic_memory_enabled": bool(
                output_dict.get("semantic_memory_enabled", preview["semantic_memory_enabled"])
            ),
            "semantic_store_kind": str(
                output_dict.get("semantic_store_kind", preview["semantic_store_kind"])
            ),
            "semantic_namespaces": [
                str(item)
                for item in output_dict.get("semantic_namespaces", preview["semantic_namespaces"])
                if str(item)
            ],
            "superstep_count": int(output_dict.get("superstep_count", preview["superstep_count"])),
            "stop_boundary": str(output_dict.get("stop_boundary", preview["stop_boundary"])),
            "terminal_reached": bool(output_dict.get("terminal_reached", preview["terminal_reached"])),
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": int(output_dict.get("recursion_limit", preview["recursion_limit"])),
            "execution_posture": preview["execution_posture"],
            "last_run_kind": run_kind,
            "last_run_status": "ok" if preview["last_run_status"] != "blocked" else "blocked",
            "last_run_reason": preview["last_run_reason"],
        }
    except Exception as exc:  # pragma: no cover
        return {
            **preview,
            **metadata,
            "execution_posture": "execution_failed",
            "last_run_status": "error",
            "last_run_reason": str(exc),
        }


def _memory_aware_live_primary_engine_projection(
    thread: dict[str, Any], thread_id: str = ""
) -> dict[str, Any]:
    state = thread.get("memory_aware_live_primary_engine_state")
    preview = _memory_aware_live_primary_engine_preview(
        thread,
        str(thread.get("last_memory_aware_live_primary_engine_kind", "")) or "invoke",
        int(thread.get("last_memory_aware_live_primary_engine_recursion_limit", 8) or 8),
    )
    helper_pointer: dict[str, Any] = {
        "command": "memory-engine",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "engine_identity": _memory_aware_live_primary_engine_identity(),
            **preview,
        }

    return {
        "engine_identity": state.get("engine_identity", _memory_aware_live_primary_engine_identity()),
        "compile_supported": bool(state.get("compile_supported", preview["compile_supported"])),
        "compiled_graph_present": bool(state.get("compiled_graph_present", preview["compiled_graph_present"])),
        "invoke_supported": bool(state.get("invoke_supported", preview["invoke_supported"])),
        "stream_supported": bool(state.get("stream_supported", preview["stream_supported"])),
        "current_execution_node": str(state.get("current_execution_node", preview["current_execution_node"])),
        "mapped_phase": str(state.get("mapped_phase", preview["mapped_phase"])),
        "memory_node_path": list(state.get("memory_node_path", preview["memory_node_path"])),
        "memory_phase_path": list(state.get("memory_phase_path", preview["memory_phase_path"])),
        "memory_transition_log": list(preview["memory_transition_log"]),
        "memory_state_kind": str(preview["memory_state_kind"]),
        "memory_store_configured": bool(preview["memory_store_configured"]),
        "memory_store_kind": str(preview["memory_store_kind"]),
        "memory_namespaces": list(preview["memory_namespaces"]),
        "semantic_memory_enabled": bool(preview["semantic_memory_enabled"]),
        "semantic_store_kind": str(preview["semantic_store_kind"]),
        "semantic_namespaces": list(preview["semantic_namespaces"]),
        "superstep_count": int(state.get("superstep_count", preview["superstep_count"])),
        "stop_boundary": str(state.get("stop_boundary", preview["stop_boundary"])),
        "terminal_reached": bool(state.get("terminal_reached", preview["terminal_reached"])),
        "recursion_limit_supported": bool(
            state.get("recursion_limit_supported", preview["recursion_limit_supported"])
        ),
        "remaining_steps_supported": bool(
            state.get("remaining_steps_supported", preview["remaining_steps_supported"])
        ),
        "recursion_limit": int(state.get("recursion_limit", preview["recursion_limit"])),
        "execution_posture": str(state.get("execution_posture", preview["execution_posture"])),
        "last_run_kind": str(state.get("last_run_kind", preview["last_run_kind"])),
        "last_run_status": str(state.get("last_run_status", preview["last_run_status"])),
        "last_run_reason": str(state.get("last_run_reason", preview["last_run_reason"])),
        "helper_pointer": helper_pointer,
    }


def _persist_memory_aware_live_primary_engine_state(
    thread: dict[str, Any], run_kind: str = "", recursion_limit: int = 8
) -> dict[str, Any]:
    run_kind = run_kind or str(thread.get("last_memory_aware_live_primary_engine_kind", "")) or "invoke"
    recursion_limit = int(
        recursion_limit or thread.get("last_memory_aware_live_primary_engine_recursion_limit", 8) or 8
    )
    result = _execute_memory_aware_live_primary_engine(thread, run_kind, recursion_limit)
    stored = {
        "engine_identity": _memory_aware_live_primary_engine_identity(),
        "compile_supported": result["compile_supported"],
        "compiled_graph_present": result["compiled_graph_present"],
        "invoke_supported": result["invoke_supported"],
        "stream_supported": result["stream_supported"],
        "current_execution_node": result["current_execution_node"],
        "mapped_phase": result["mapped_phase"],
        "memory_node_path": result["memory_node_path"],
        "memory_phase_path": result["memory_phase_path"],
        "memory_transition_log": result["memory_transition_log"],
        "memory_state_kind": result["memory_state_kind"],
        "memory_store_configured": result["memory_store_configured"],
        "memory_store_kind": result["memory_store_kind"],
        "memory_namespaces": result["memory_namespaces"],
        "semantic_memory_enabled": result["semantic_memory_enabled"],
        "semantic_store_kind": result["semantic_store_kind"],
        "semantic_namespaces": result["semantic_namespaces"],
        "superstep_count": result["superstep_count"],
        "stop_boundary": result["stop_boundary"],
        "terminal_reached": result["terminal_reached"],
        "recursion_limit_supported": result["recursion_limit_supported"],
        "remaining_steps_supported": result["remaining_steps_supported"],
        "recursion_limit": result["recursion_limit"],
        "execution_posture": result["execution_posture"],
        "last_run_kind": result["last_run_kind"],
        "last_run_status": result["last_run_status"],
        "last_run_reason": result["last_run_reason"],
        "updated_at": _now(),
    }
    thread["last_memory_aware_live_primary_engine_kind"] = run_kind
    thread["last_memory_aware_live_primary_engine_reason"] = result["last_run_reason"]
    thread["last_memory_aware_live_primary_engine_recursion_limit"] = recursion_limit
    thread["memory_aware_live_primary_engine_state"] = stored
    return stored


def _migration_aware_live_primary_engine_identity() -> dict[str, Any]:
    return _clone_payload(MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY)


def _migration_compatibility_state_kind(migration_projection: dict[str, Any]) -> str:
    compatibility = str(migration_projection.get("compatibility", "migration_safe"))
    if compatibility == "incompatible":
        return "incompatible_thread"
    if compatibility == "degraded_compatible":
        return "degraded_compatible_thread"
    if compatibility == "migration_safe":
        return "migration_safe_thread"
    return "ordinary"


def _migration_transition_log(
    base_log: list[str],
    migration_projection: dict[str, Any],
) -> list[str]:
    transition_log = [str(item) for item in base_log if str(item)]
    compatibility = str(migration_projection.get("compatibility", ""))
    topology_compatibility = str(migration_projection.get("topology_compatibility", ""))
    state_schema_compatibility = str(migration_projection.get("state_schema_compatibility", ""))
    reason_codes = [str(item) for item in migration_projection.get("reason_codes", []) if str(item)]
    current_contract = migration_projection.get("current_graph_contract", {})
    thread_contract = migration_projection.get("thread_graph_contract", {})
    current_graph_contract_id = str(dict(current_contract).get("graph_contract_id", "")) if isinstance(current_contract, dict) else ""
    thread_graph_contract_id = str(dict(thread_contract).get("graph_contract_id", "")) if isinstance(thread_contract, dict) else ""

    if compatibility:
        transition_log.append(f"compatibility:{compatibility}")
    if topology_compatibility:
        transition_log.append(f"topology:{topology_compatibility}")
    if state_schema_compatibility:
        transition_log.append(f"state_schema:{state_schema_compatibility}")
    if current_graph_contract_id:
        transition_log.append(f"current_graph:{current_graph_contract_id}")
    if thread_graph_contract_id:
        transition_log.append(f"thread_graph:{thread_graph_contract_id}")
    if reason_codes:
        transition_log.append(f"reasons:{len(reason_codes)}")
    return list(dict.fromkeys(transition_log))


def _migration_aware_live_primary_engine_preview(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }

    memory_preview = _memory_aware_live_primary_engine_preview(thread, run_kind, recursion_limit)
    migration_projection = _migration_projection(thread)
    compatibility_state_kind = _migration_compatibility_state_kind(migration_projection)
    compatibility_node_path = list(memory_preview.get("memory_node_path", []))
    compatibility_phase_path = list(memory_preview.get("memory_phase_path", []))
    compatibility_transition_log = _migration_transition_log(
        list(memory_preview.get("memory_transition_log", [])),
        migration_projection,
    )

    return {
        **metadata,
        "current_execution_node": memory_preview["current_execution_node"],
        "mapped_phase": memory_preview["mapped_phase"],
        "compatibility_node_path": compatibility_node_path,
        "compatibility_phase_path": compatibility_phase_path,
        "compatibility_transition_log": compatibility_transition_log,
        "compatibility_state_kind": compatibility_state_kind,
        "current_graph_contract": dict(migration_projection.get("current_graph_contract", {})),
        "thread_graph_contract": dict(migration_projection.get("thread_graph_contract", {})),
        "topology_compatibility": str(migration_projection.get("topology_compatibility", "")),
        "state_schema_compatibility": str(migration_projection.get("state_schema_compatibility", "")),
        "compatibility": str(migration_projection.get("compatibility", "")),
        "reason_codes": [str(item) for item in migration_projection.get("reason_codes", []) if str(item)],
        "superstep_count": int(memory_preview["superstep_count"]),
        "stop_boundary": memory_preview["stop_boundary"],
        "terminal_reached": bool(memory_preview["terminal_reached"]),
        "recursion_limit_supported": bool(memory_preview["recursion_limit_supported"]),
        "remaining_steps_supported": bool(memory_preview["remaining_steps_supported"]),
        "recursion_limit": int(memory_preview["recursion_limit"]),
        "execution_posture": memory_preview["execution_posture"],
        "last_run_kind": run_kind,
        "last_run_status": memory_preview["last_run_status"],
        "last_run_reason": memory_preview["last_run_reason"],
    }


def _build_migration_aware_live_primary_engine_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "invoke_supported": False,
        "stream_supported": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class MigrationAwareEngineState(TypedDict, total=False):
            compatibility_node_path: list[str]
            compatibility_phase_path: list[str]
            compatibility_transition_log: list[str]
            compatibility_state_kind: str
            current_graph_contract: dict[str, str]
            thread_graph_contract: dict[str, str]
            topology_compatibility: str
            state_schema_compatibility: str
            compatibility: str
            reason_codes: list[str]
            superstep_count: int
            stop_boundary: str
            terminal_reached: bool
            recursion_limit: int

        def passthrough(state: MigrationAwareEngineState) -> MigrationAwareEngineState:
            return state

        builder = StateGraph(MigrationAwareEngineState)
        builder.add_node("migration_state", passthrough)
        builder.add_edge(START, "migration_state")
        builder.add_edge("migration_state", END)
        compiled = builder.compile()
        metadata["compiled_graph_present"] = True
        metadata["invoke_supported"] = hasattr(compiled, "invoke")
        metadata["stream_supported"] = hasattr(compiled, "stream")
        return compiled, metadata
    except Exception as exc:  # pragma: no cover
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_migration_aware_live_primary_engine(
    thread: dict[str, Any], run_kind: str, recursion_limit: int
) -> dict[str, Any]:
    preview = _migration_aware_live_primary_engine_preview(thread, run_kind, recursion_limit)
    compiled, metadata = _build_migration_aware_live_primary_engine_graph()
    if compiled is None:
        unavailable_posture = (
            preview["execution_posture"]
            if preview["execution_posture"] in {"interrupt_wait", "recovery_wait", "terminal", "recursion_limited"}
            else "unavailable"
        )
        unavailable_status = (
            preview["last_run_status"] if preview["last_run_status"] in {"blocked", "noop", "ok"} else "unavailable"
        )
        return {
            **preview,
            **metadata,
            "execution_posture": unavailable_posture,
            "last_run_status": unavailable_status,
            "last_run_reason": metadata["compile_error"] or preview["last_run_reason"],
        }

    try:
        input_payload = {
            "compatibility_node_path": list(preview["compatibility_node_path"]),
            "compatibility_phase_path": list(preview["compatibility_phase_path"]),
            "compatibility_transition_log": list(preview["compatibility_transition_log"]),
            "compatibility_state_kind": preview["compatibility_state_kind"],
            "current_graph_contract": dict(preview["current_graph_contract"]),
            "thread_graph_contract": dict(preview["thread_graph_contract"]),
            "topology_compatibility": preview["topology_compatibility"],
            "state_schema_compatibility": preview["state_schema_compatibility"],
            "compatibility": preview["compatibility"],
            "reason_codes": list(preview["reason_codes"]),
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit": preview["recursion_limit"],
        }
        if run_kind == "stream":
            chunks = list(compiled.stream(input_payload))
            output = chunks[-1] if chunks else {}
        else:
            output = compiled.invoke(input_payload)
        output_dict = output if isinstance(output, dict) else {}
        return {
            **metadata,
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "compatibility_node_path": list(
                output_dict.get("compatibility_node_path", preview["compatibility_node_path"])
            ),
            "compatibility_phase_path": list(
                output_dict.get("compatibility_phase_path", preview["compatibility_phase_path"])
            ),
            "compatibility_transition_log": list(
                output_dict.get("compatibility_transition_log", preview["compatibility_transition_log"])
            ),
            "compatibility_state_kind": str(
                output_dict.get("compatibility_state_kind", preview["compatibility_state_kind"])
            ),
            "current_graph_contract": dict(
                output_dict.get("current_graph_contract", preview["current_graph_contract"])
            ),
            "thread_graph_contract": dict(
                output_dict.get("thread_graph_contract", preview["thread_graph_contract"])
            ),
            "topology_compatibility": str(
                output_dict.get("topology_compatibility", preview["topology_compatibility"])
            ),
            "state_schema_compatibility": str(
                output_dict.get("state_schema_compatibility", preview["state_schema_compatibility"])
            ),
            "compatibility": str(output_dict.get("compatibility", preview["compatibility"])),
            "reason_codes": [str(item) for item in output_dict.get("reason_codes", preview["reason_codes"]) if str(item)],
            "superstep_count": int(output_dict.get("superstep_count", preview["superstep_count"])),
            "stop_boundary": str(output_dict.get("stop_boundary", preview["stop_boundary"])),
            "terminal_reached": bool(output_dict.get("terminal_reached", preview["terminal_reached"])),
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": int(output_dict.get("recursion_limit", preview["recursion_limit"])),
            "execution_posture": preview["execution_posture"],
            "last_run_kind": run_kind,
            "last_run_status": "ok" if preview["last_run_status"] != "blocked" else "blocked",
            "last_run_reason": preview["last_run_reason"],
        }
    except Exception as exc:  # pragma: no cover
        return {
            **preview,
            **metadata,
            "execution_posture": "execution_failed",
            "last_run_status": "error",
            "last_run_reason": str(exc),
        }


def _migration_aware_live_primary_engine_projection(
    thread: dict[str, Any], thread_id: str = ""
) -> dict[str, Any]:
    state = thread.get("migration_aware_live_primary_engine_state")
    preview = _migration_aware_live_primary_engine_preview(
        thread,
        str(thread.get("last_migration_aware_live_primary_engine_kind", "")) or "invoke",
        int(thread.get("last_migration_aware_live_primary_engine_recursion_limit", 8) or 8),
    )
    helper_pointer: dict[str, Any] = {
        "command": "migration-engine",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "engine_identity": _migration_aware_live_primary_engine_identity(),
            **preview,
        }

    return {
        "engine_identity": state.get("engine_identity", _migration_aware_live_primary_engine_identity()),
        "compile_supported": bool(state.get("compile_supported", preview["compile_supported"])),
        "compiled_graph_present": bool(state.get("compiled_graph_present", preview["compiled_graph_present"])),
        "invoke_supported": bool(state.get("invoke_supported", preview["invoke_supported"])),
        "stream_supported": bool(state.get("stream_supported", preview["stream_supported"])),
        "current_execution_node": str(state.get("current_execution_node", preview["current_execution_node"])),
        "mapped_phase": str(state.get("mapped_phase", preview["mapped_phase"])),
        "compatibility_node_path": list(state.get("compatibility_node_path", preview["compatibility_node_path"])),
        "compatibility_phase_path": list(state.get("compatibility_phase_path", preview["compatibility_phase_path"])),
        "compatibility_transition_log": list(preview["compatibility_transition_log"]),
        "compatibility_state_kind": str(preview["compatibility_state_kind"]),
        "current_graph_contract": dict(preview["current_graph_contract"]),
        "thread_graph_contract": dict(preview["thread_graph_contract"]),
        "topology_compatibility": str(preview["topology_compatibility"]),
        "state_schema_compatibility": str(preview["state_schema_compatibility"]),
        "compatibility": str(preview["compatibility"]),
        "reason_codes": list(preview["reason_codes"]),
        "superstep_count": int(state.get("superstep_count", preview["superstep_count"])),
        "stop_boundary": str(state.get("stop_boundary", preview["stop_boundary"])),
        "terminal_reached": bool(state.get("terminal_reached", preview["terminal_reached"])),
        "recursion_limit_supported": bool(
            state.get("recursion_limit_supported", preview["recursion_limit_supported"])
        ),
        "remaining_steps_supported": bool(
            state.get("remaining_steps_supported", preview["remaining_steps_supported"])
        ),
        "recursion_limit": int(state.get("recursion_limit", preview["recursion_limit"])),
        "execution_posture": str(state.get("execution_posture", preview["execution_posture"])),
        "last_run_kind": str(state.get("last_run_kind", preview["last_run_kind"])),
        "last_run_status": str(state.get("last_run_status", preview["last_run_status"])),
        "last_run_reason": str(state.get("last_run_reason", preview["last_run_reason"])),
        "helper_pointer": helper_pointer,
    }


def _persist_migration_aware_live_primary_engine_state(
    thread: dict[str, Any], run_kind: str = "", recursion_limit: int = 8
) -> dict[str, Any]:
    run_kind = run_kind or str(thread.get("last_migration_aware_live_primary_engine_kind", "")) or "invoke"
    recursion_limit = int(
        recursion_limit or thread.get("last_migration_aware_live_primary_engine_recursion_limit", 8) or 8
    )
    result = _execute_migration_aware_live_primary_engine(thread, run_kind, recursion_limit)
    stored = {
        "engine_identity": _migration_aware_live_primary_engine_identity(),
        "compile_supported": result["compile_supported"],
        "compiled_graph_present": result["compiled_graph_present"],
        "invoke_supported": result["invoke_supported"],
        "stream_supported": result["stream_supported"],
        "current_execution_node": result["current_execution_node"],
        "mapped_phase": result["mapped_phase"],
        "compatibility_node_path": result["compatibility_node_path"],
        "compatibility_phase_path": result["compatibility_phase_path"],
        "compatibility_transition_log": result["compatibility_transition_log"],
        "compatibility_state_kind": result["compatibility_state_kind"],
        "current_graph_contract": result["current_graph_contract"],
        "thread_graph_contract": result["thread_graph_contract"],
        "topology_compatibility": result["topology_compatibility"],
        "state_schema_compatibility": result["state_schema_compatibility"],
        "compatibility": result["compatibility"],
        "reason_codes": result["reason_codes"],
        "superstep_count": result["superstep_count"],
        "stop_boundary": result["stop_boundary"],
        "terminal_reached": result["terminal_reached"],
        "recursion_limit_supported": result["recursion_limit_supported"],
        "remaining_steps_supported": result["remaining_steps_supported"],
        "recursion_limit": result["recursion_limit"],
        "execution_posture": result["execution_posture"],
        "last_run_kind": result["last_run_kind"],
        "last_run_status": result["last_run_status"],
        "last_run_reason": result["last_run_reason"],
        "updated_at": _now(),
    }
    thread["last_migration_aware_live_primary_engine_kind"] = run_kind
    thread["last_migration_aware_live_primary_engine_reason"] = result["last_run_reason"]
    thread["last_migration_aware_live_primary_engine_recursion_limit"] = recursion_limit
    thread["migration_aware_live_primary_engine_state"] = stored
    return stored


def _generalized_live_routing_identity() -> dict[str, Any]:
    return _clone_payload(GENERALIZED_LIVE_ROUTING_IDENTITY)


def _route_label_for_node(node_id: str, mapped_phase: str = "") -> str:
    if node_id == "approval_wait":
        return "approval_wait"
    if node_id == "recovery_pending_resume":
        return "recovery_wait"
    if node_id == "accepted_terminal":
        return "terminal:accept"
    if node_id == "halted_terminal":
        return "terminal:halt"
    if node_id == "escalated_terminal":
        return "terminal:escalate"
    node = GRAPH_KERNEL_NODES.get(node_id, {})
    phase = str(node.get("phase", "")) or mapped_phase
    if phase:
        return f"phase:{phase}"
    return ""


def _command_target_phase(target: str) -> str:
    if not target:
        return ""
    if target in ROOT_PHASES:
        return target
    if target in GRAPH_KERNEL_NODES:
        return str(GRAPH_KERNEL_NODES[target].get("phase", ""))
    if target in SUBGRAPHS:
        return str(SUBGRAPHS[target].get("default_phase", ""))
    return ""


def _generalized_live_routing_decision(thread: dict[str, Any]) -> dict[str, Any]:
    kernel_projection = _graph_kernel_projection(thread)
    approval_queue_projection = _approval_queue_projection(thread)
    command_projection = _command_projection(thread)
    current_node = str(kernel_projection["current_node_id"])
    mapped_phase = str(kernel_projection["mapped_phase"])
    next_execution_nodes = list(kernel_projection["available_next_nodes"])
    active_loop = str(thread.get("active_loop", ""))
    loop_route_kind = active_loop if active_loop in LOOP_CAPABLE_FLOWS else ""
    current_route = _route_label_for_node(current_node, mapped_phase)
    selected_route = current_route
    route_posture = "ready" if mapped_phase or current_route else "unavailable"
    approval_route_pending = bool(approval_queue_projection["pending_count"] > 0 or current_node == "approval_wait")

    route_candidates: list[str] = []
    if current_route:
        route_candidates.append(current_route)
    if loop_route_kind:
        route_candidates.append(f"loop:{loop_route_kind}")
    for next_node in next_execution_nodes:
        route_label = _route_label_for_node(str(next_node))
        if route_label:
            route_candidates.append(route_label)

    transition_kind = str(command_projection["transition_kind"])
    goto_target = str(command_projection["goto_target"])
    parent_handoff_target = str(command_projection["parent_handoff_target"])
    if transition_kind:
        route_candidates.append(f"command:{transition_kind}")

    if current_node == "approval_wait":
        route_posture = "interrupt_wait"
        current_route = "approval_wait"
        selected_route = "approval_wait"
    elif current_node == "recovery_pending_resume":
        route_posture = "recovery_wait"
        current_route = "recovery_wait"
        selected_route = "recovery_wait"
    elif current_node in {"accepted_terminal", "halted_terminal", "escalated_terminal"}:
        route_posture = "terminal"
        current_route = _route_label_for_node(current_node, mapped_phase)
        selected_route = current_route
    elif transition_kind in {"goto", "update_goto", "parent_handoff", "resume_parent_handoff"}:
        route_posture = "routed"
        current_route = f"command:{transition_kind}"
        target_phase = _command_target_phase(parent_handoff_target or goto_target)
        selected_route = f"phase:{target_phase}" if target_phase else current_route
    elif loop_route_kind and mapped_phase == str(LOOP_CAPABLE_FLOWS[loop_route_kind]["entry_phase"]):
        route_posture = "routed"
        current_route = f"loop:{loop_route_kind}"
        selected_route = current_route
    else:
        current_route = current_route or (f"phase:{mapped_phase}" if mapped_phase else "")
        selected_route = current_route
        if current_route:
            route_posture = "routed"

    deduped_candidates = list(dict.fromkeys(route_candidates))
    if selected_route and selected_route not in deduped_candidates:
        deduped_candidates.append(selected_route)

    return {
        "route_posture": route_posture,
        "current_route": current_route,
        "candidate_routes": deduped_candidates,
        "selected_route": selected_route,
        "loop_route_kind": loop_route_kind,
        "current_execution_node": current_node,
        "mapped_phase": mapped_phase,
        "next_execution_nodes": next_execution_nodes,
        "approval_route_pending": approval_route_pending,
    }


def _build_generalized_live_routing_graph() -> tuple[Any | None, dict[str, Any]]:
    metadata = {
        "compile_supported": bool(LANGGRAPH_AVAILABLE),
        "compiled_graph_present": False,
        "compile_error": "",
    }
    if not LANGGRAPH_AVAILABLE:
        return None, metadata

    try:
        from langgraph.graph import END, START, StateGraph  # type: ignore

        class GeneralizedRoutingState(TypedDict, total=False):
            route_posture: str
            current_route: str
            candidate_routes: list[str]
            selected_route: str
            loop_route_kind: str
            current_execution_node: str
            mapped_phase: str
            next_execution_nodes: list[str]
            approval_route_pending: bool

        def choose_route(
            state: GeneralizedRoutingState,
        ) -> Literal[
            "phase_route",
            "loop_route",
            "approval_route",
            "recovery_route",
            "terminal_route",
            "command_route",
        ]:
            posture = str(state.get("route_posture", ""))
            current_route = str(state.get("current_route", ""))
            if posture == "interrupt_wait":
                return "approval_route"
            if posture == "recovery_wait":
                return "recovery_route"
            if posture == "terminal":
                return "terminal_route"
            if current_route.startswith("command:"):
                return "command_route"
            if current_route.startswith("loop:"):
                return "loop_route"
            return "phase_route"

        def make_route_node(node_name: str):
            def _node(state: GeneralizedRoutingState) -> GeneralizedRoutingState:
                next_execution_nodes = list(state.get("next_execution_nodes", []))
                if node_name == "approval_route":
                    return {
                        "route_posture": "interrupt_wait",
                        "current_route": "approval_wait",
                        "selected_route": "approval_wait",
                        "approval_route_pending": True,
                        "next_execution_nodes": next_execution_nodes,
                    }
                if node_name == "recovery_route":
                    return {
                        "route_posture": "recovery_wait",
                        "current_route": "recovery_wait",
                        "selected_route": "recovery_wait",
                        "approval_route_pending": bool(state.get("approval_route_pending", False)),
                        "next_execution_nodes": next_execution_nodes,
                    }
                return {
                    "route_posture": str(state.get("route_posture", "")),
                    "current_route": str(state.get("current_route", "")),
                    "selected_route": str(state.get("selected_route", "")),
                    "approval_route_pending": bool(state.get("approval_route_pending", False)),
                    "next_execution_nodes": next_execution_nodes,
                }

            return _node

        builder = StateGraph(GeneralizedRoutingState)
        builder.add_node("route", lambda state: state)
        builder.add_edge(START, "route")
        for node_name in (
            "phase_route",
            "loop_route",
            "approval_route",
            "recovery_route",
            "terminal_route",
            "command_route",
        ):
            builder.add_node(node_name, make_route_node(node_name))
            builder.add_edge(node_name, END)
        builder.add_conditional_edges("route", choose_route)
        compiled = builder.compile()
        metadata["compiled_graph_present"] = True
        return compiled, metadata
    except Exception as exc:  # pragma: no cover - only exercised when langgraph is installed
        metadata["compile_error"] = str(exc)
        return None, metadata


def _execute_generalized_live_routing(thread: dict[str, Any]) -> dict[str, Any]:
    decision = _generalized_live_routing_decision(thread)
    compiled, metadata = _build_generalized_live_routing_graph()
    if compiled is None:
        return {
            **metadata,
            **decision,
        }

    try:
        output = compiled.invoke(
            {
                "route_posture": decision["route_posture"],
                "current_route": decision["current_route"],
                "candidate_routes": decision["candidate_routes"],
                "selected_route": decision["selected_route"],
                "loop_route_kind": decision["loop_route_kind"],
                "current_execution_node": decision["current_execution_node"],
                "mapped_phase": decision["mapped_phase"],
                "next_execution_nodes": decision["next_execution_nodes"],
                "approval_route_pending": decision["approval_route_pending"],
            }
        )
        output_dict = output if isinstance(output, dict) else {}
        return {
            **metadata,
            "route_posture": str(output_dict.get("route_posture", decision["route_posture"])),
            "current_route": str(output_dict.get("current_route", decision["current_route"])),
            "candidate_routes": list(output_dict.get("candidate_routes", decision["candidate_routes"])),
            "selected_route": str(output_dict.get("selected_route", decision["selected_route"])),
            "loop_route_kind": str(output_dict.get("loop_route_kind", decision["loop_route_kind"])),
            "current_execution_node": str(
                output_dict.get("current_execution_node", decision["current_execution_node"])
            ),
            "mapped_phase": str(output_dict.get("mapped_phase", decision["mapped_phase"])),
            "next_execution_nodes": list(output_dict.get("next_execution_nodes", decision["next_execution_nodes"])),
            "approval_route_pending": bool(
                output_dict.get("approval_route_pending", decision["approval_route_pending"])
            ),
        }
    except Exception:  # pragma: no cover - only exercised when langgraph is installed
        return {
            **metadata,
            **decision,
            "route_posture": "routing_failed",
        }


def _generalized_live_routing_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    state = thread.get("generalized_live_routing_state")
    decision = _generalized_live_routing_decision(thread)
    helper_pointer: dict[str, Any] = {
        "command": "generalized-routing",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    if not isinstance(state, dict):
        state = {
            "routing_identity": _generalized_live_routing_identity(),
            "compile_supported": bool(LANGGRAPH_AVAILABLE),
            "compiled_graph_present": False,
            **decision,
        }

    return {
        "routing_identity": state.get("routing_identity", _generalized_live_routing_identity()),
        "compile_supported": bool(state.get("compile_supported", False)),
        "compiled_graph_present": bool(state.get("compiled_graph_present", False)),
        "route_posture": str(
            state.get("route_posture", decision["route_posture"])
            if str(state.get("route_posture", "")) == "routing_failed"
            else decision["route_posture"]
        ),
        "current_route": decision["current_route"],
        "candidate_routes": decision["candidate_routes"],
        "selected_route": decision["selected_route"],
        "loop_route_kind": decision["loop_route_kind"],
        "current_execution_node": decision["current_execution_node"],
        "mapped_phase": decision["mapped_phase"],
        "next_execution_nodes": decision["next_execution_nodes"],
        "approval_route_pending": decision["approval_route_pending"],
        "helper_pointer": helper_pointer,
    }


def _backend_routing_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    generalized_routing = _generalized_live_routing_projection(thread, thread_id)
    route_posture = str(generalized_routing.get("route_posture", "unavailable"))
    status = str(thread.get("status", ""))
    stop_reason = str(thread.get("stop_reason", ""))
    selector_id = str(thread.get("selector_id", ""))
    session_scope_id = str(thread.get("session_scope_id", ""))
    released_at = str(thread.get("released_at", ""))
    has_scoped_selector = bool(selector_id and session_scope_id and not released_at)

    terminal_statuses = {"accepted", "halted", "escalated", "closed", "released", "handoff", "handed_off"}
    if route_posture == "terminal" or status in terminal_statuses or stop_reason in {
        "accepted",
        "escalated",
        "non_repairable_failure",
        "closed",
        "released",
        "handoff",
        "handed_off",
    }:
        routing_posture = "terminal_thread"
    elif route_posture in {"interrupt_wait", "recovery_wait"}:
        routing_posture = "active_resumable_thread"
    elif has_scoped_selector:
        routing_posture = "active_scoped_selector"
    elif thread_id or str(thread.get("thread_id", "")):
        routing_posture = "historical_preserved_thread"
    else:
        routing_posture = "missing_or_stale_selector"

    return {
        "routing_posture": routing_posture,
        "routing_eligible": bool(has_scoped_selector and routing_posture in {"active_scoped_selector", "active_resumable_thread"}),
    }


def _session_lineage_hint() -> str:
    for candidate in (
        os.environ.get("CODEX_SESSION_ID"),
        os.environ.get("OMX_SESSION_SCOPE_ID"),
        os.environ.get("OMX_SESSION_ID"),
    ):
        if candidate:
            return str(candidate)
    return ""


def _ensure_scoped_activation_state(thread: dict[str, Any]) -> None:
    selector_id = str(thread.get("selector_id", ""))
    session_scope_id = str(thread.get("session_scope_id", ""))
    session_lineage = _session_lineage_hint()

    if not selector_id:
        selector_id = f"selector-{uuid.uuid4().hex[:12]}"
        thread["selector_id"] = selector_id
    if not session_scope_id:
        session_scope_id = session_lineage or f"session-{uuid.uuid4().hex[:12]}"
        thread["session_scope_id"] = session_scope_id
    if not thread.get("leader_session_lineage"):
        thread["leader_session_lineage"] = session_lineage or session_scope_id
    if not thread.get("acquired_at"):
        thread["acquired_at"] = _now()

    status = str(thread.get("status", ""))
    stop_reason = str(thread.get("stop_reason", ""))
    if status in {"accepted", "halted", "escalated"} or stop_reason in {"accepted", "escalated", "non_repairable_failure"}:
        if not thread.get("released_at"):
            thread["released_at"] = _now()
    else:
        thread["released_at"] = ""

    thread["last_selector_heartbeat_at"] = _now()


def _persist_scoped_activation(repo_root: Any, layout: dict[str, str], thread: dict[str, Any], routing_projection: dict[str, Any]) -> None:
    selector_id = str(thread.get("selector_id", ""))
    session_scope_id = str(thread.get("session_scope_id", ""))
    if not selector_id or not session_scope_id:
        return

    selector_payload = {
        "backend_family": "langgraph",
        "selector_id": selector_id,
        "repo_root": str(repo_root),
        "worktree_id": str(thread.get("worktree_id", "")),
        "thread_id": str(thread.get("thread_id", "")),
        "session_scope_id": session_scope_id,
        "leader_session_lineage": str(thread.get("leader_session_lineage", session_scope_id)),
        "acquired_at": str(thread.get("acquired_at", "")),
        "last_heartbeat_at": str(thread.get("last_selector_heartbeat_at", thread.get("updated_at", _now()))),
        "released_at": str(thread.get("released_at", "")),
        "generation": int(time.time() * 1000),
        "routing_posture": str(routing_projection.get("routing_posture", "")),
        "routing_eligible": bool(routing_projection.get("routing_eligible", False)),
        "layout": {
            "root": str(layout.get("selectors", "")),
            "active_selector": str(layout.get("active_selector", active_selector_path(Path(repo_root)))),
            "selector_leases": str(layout.get("selector_leases", "")),
        },
    }
    save_active_selector(Path(repo_root), selector_payload)
    write_selector_lease(Path(repo_root), session_scope_id, selector_payload)


def _persist_generalized_live_routing_state(thread: dict[str, Any]) -> dict[str, Any]:
    projection = _execute_generalized_live_routing(thread)
    stored = {
        "routing_identity": _generalized_live_routing_identity(),
        "compile_supported": projection["compile_supported"],
        "compiled_graph_present": projection["compiled_graph_present"],
        "route_posture": projection["route_posture"],
        "current_route": projection["current_route"],
        "candidate_routes": projection["candidate_routes"],
        "selected_route": projection["selected_route"],
        "loop_route_kind": projection["loop_route_kind"],
        "current_execution_node": projection["current_execution_node"],
        "mapped_phase": projection["mapped_phase"],
        "next_execution_nodes": projection["next_execution_nodes"],
        "approval_route_pending": projection["approval_route_pending"],
        "updated_at": _now(),
    }
    thread["generalized_live_routing_state"] = stored
    return stored


def _persist_subgraph_state_inspection_state(thread: dict[str, Any]) -> dict[str, Any]:
    projection = _subgraph_state_inspection_projection(thread, str(thread.get("thread_id", "")))
    stored = {
        "active_subgraph": projection["active_subgraph"],
        "persistence_mode": projection["persistence_mode"],
        "checkpointer_mode": projection["checkpointer_mode"],
        "inherits_parent_checkpointer": projection["inherits_parent_checkpointer"],
        "separate_subgraph_memory": projection["separate_subgraph_memory"],
        "durable_execution_supported": projection["durable_execution_supported"],
        "interrupts_supported": projection["interrupts_supported"],
        "state_inspection_available": projection["state_inspection_available"],
        "state_inspection_scope": projection["state_inspection_scope"],
        "static_discoverable": projection["static_discoverable"],
        "same_subgraph_parallel_calls_supported": projection["same_subgraph_parallel_calls_supported"],
        "inspection_blockers": projection["inspection_blockers"],
        "updated_at": _now(),
    }
    thread["subgraph_state_inspection_state"] = stored
    return stored


def _persist_runtime_state_layers(thread: dict[str, Any], *, live_run_kind: str = "") -> None:
    _ensure_subgraph_state(thread)
    _persist_graph_kernel_state(thread)
    _persist_primary_runtime_engine_state(thread)
    _persist_compiled_invocation_state(thread)
    _persist_live_execution_state(thread, live_run_kind)
    _persist_fuller_live_primary_engine_state(thread, live_run_kind)
    _persist_deeper_live_primary_engine_state(thread, live_run_kind)
    _persist_superstep_live_primary_engine_state(thread, live_run_kind)
    _persist_stateful_live_primary_engine_state(thread, live_run_kind)
    _persist_boundary_state_live_primary_engine_state(thread, live_run_kind)
    _persist_handoff_state_live_primary_engine_state(thread, live_run_kind)
    _persist_approval_aware_live_primary_engine_state(thread, live_run_kind)
    _persist_provenance_state_live_primary_engine_state(thread, live_run_kind)
    _persist_durable_artifact_aware_live_primary_engine_state(thread, live_run_kind)
    _persist_reducer_aware_live_primary_engine_state(thread, live_run_kind)
    _persist_command_aware_live_primary_engine_state(thread, live_run_kind)
    _persist_runtime_aware_live_primary_engine_state(thread, live_run_kind)
    _persist_memory_aware_live_primary_engine_state(thread, live_run_kind)
    _persist_migration_aware_live_primary_engine_state(thread, live_run_kind)
    _persist_generalized_live_routing_state(thread)
    _persist_subgraph_state_inspection_state(thread)
    _persist_automatic_runtime_policy_state(thread)


def _target_subgraph_for_command(thread: dict[str, Any], goto_target: str, parent_handoff_target: str) -> str:
    for candidate in (parent_handoff_target, goto_target):
        if candidate in SUBGRAPHS:
            return candidate
        derived = _subgraph_id_for_phase(candidate)
        if derived:
            return derived
    return str(thread.get("active_subgraph", ""))


def _resume_posture_for_command(
    existing_state: dict[str, Any],
    transition_kind: str,
    await_command_resume: bool,
    resume_payload_present: bool,
) -> str:
    if await_command_resume:
        return "awaiting_command_resume"
    if resume_payload_present:
        return "resumed_with_payload"
    if transition_kind in {"resume", "resume_with_payload", "resume_parent_handoff"}:
        return "resumed_without_payload"
    if existing_state.get("resume_posture") == "awaiting_command_resume":
        return "resumed_without_payload"
    return existing_state.get("resume_posture", "ordinary")


def _build_command_state(
    thread: dict[str, Any],
    *,
    existing_state: dict[str, Any] | None = None,
    transition_kind: str = "",
    goto_target: str = "",
    graph_scope: str = "",
    parent_handoff_target: str = "",
    update_payload: Any = None,
    resume_payload: Any = None,
    await_command_resume: bool = False,
    source_subgraph: str = "",
) -> dict[str, Any]:
    existing_state = existing_state or {}
    normalized_transition_kind = transition_kind or str(existing_state.get("transition_kind", ""))
    normalized_graph_scope = graph_scope or str(existing_state.get("graph_scope", ""))
    if not normalized_graph_scope:
        normalized_graph_scope = "parent" if parent_handoff_target else ("current" if goto_target else "")

    normalized_goto_target = goto_target or str(existing_state.get("goto_target", ""))
    normalized_parent_handoff_target = parent_handoff_target or str(existing_state.get("parent_handoff_target", ""))
    if (
        existing_state.get("resume_posture") == "awaiting_command_resume"
        and normalized_transition_kind in {"resume", "resume_with_payload", "resume_parent_handoff"}
        and existing_state.get("source_subgraph")
    ):
        normalized_source_subgraph = str(existing_state.get("source_subgraph", ""))
    else:
        normalized_source_subgraph = source_subgraph or str(existing_state.get("source_subgraph", "")) or str(
            thread.get("active_subgraph", "")
        )
    target_subgraph = _target_subgraph_for_command(
        thread,
        normalized_goto_target,
        normalized_parent_handoff_target,
    )

    update_keys = _payload_keys(update_payload) if update_payload is not None else list(existing_state.get("update_keys", []))
    resume_payload_present = resume_payload is not None
    resume_payload_keys = (
        _payload_keys(resume_payload) if resume_payload_present else list(existing_state.get("resume_payload_keys", []))
    )

    return {
        "transition_kind": normalized_transition_kind,
        "update_keys": update_keys,
        "goto_target": normalized_goto_target,
        "graph_scope": normalized_graph_scope,
        "source_subgraph": normalized_source_subgraph,
        "target_subgraph": target_subgraph,
        "parent_handoff_target": normalized_parent_handoff_target,
        "resume_posture": _resume_posture_for_command(
            existing_state,
            normalized_transition_kind,
            await_command_resume,
            resume_payload_present,
        ),
        "resume_payload_present": resume_payload_present or bool(existing_state.get("resume_payload_present", False)),
        "resume_payload_keys": resume_payload_keys,
    }


def _command_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    state = thread.get("command_state")
    if not isinstance(state, dict):
        state = {}

    helper_pointer: dict[str, Any] = {
        "command": "inspect",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    return {
        "transition_kind": str(state.get("transition_kind", "")),
        "update_keys": list(state.get("update_keys", [])),
        "goto_target": str(state.get("goto_target", "")),
        "graph_scope": str(state.get("graph_scope", "")),
        "source_subgraph": str(state.get("source_subgraph", "")),
        "target_subgraph": str(state.get("target_subgraph", "")),
        "parent_handoff_target": str(state.get("parent_handoff_target", "")),
        "resume_posture": str(state.get("resume_posture", "ordinary")),
        "resume_payload_present": bool(state.get("resume_payload_present", False)),
        "resume_payload_keys": list(state.get("resume_payload_keys", [])),
        "helper_pointer": helper_pointer,
    }


def _ensure_stream_state(thread: dict[str, Any]) -> dict[str, Any]:
    state = thread.get("stream_state")
    if isinstance(state, dict):
        state.setdefault("selected_modes", [])
        state.setdefault("subgraphs", False)
        state.setdefault("latest_event_kind", "")
        state.setdefault("latest_namespace", [])
        state.setdefault("latest_checkpoint_kind", "")
        state.setdefault("latest_task_path", "")
        state.setdefault("latest_task_status", "")
        state.setdefault("latest_debug_summary", "")
        state.setdefault("event_count", 0)
        thread["stream_state"] = state
        return state

    state = {
        "selected_modes": [],
        "subgraphs": False,
        "latest_event_kind": "",
        "latest_namespace": [],
        "latest_checkpoint_kind": "",
        "latest_task_path": "",
        "latest_task_status": "",
        "latest_debug_summary": "",
        "event_count": 0,
    }
    thread["stream_state"] = state
    return state


def _stream_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    state = thread.get("stream_state")
    if not isinstance(state, dict):
        state = {}

    helper_pointer: dict[str, Any] = {
        "command": "stream",
        "read_only": False,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    return {
        "selected_modes": list(state.get("selected_modes", [])),
        "subgraphs": bool(state.get("subgraphs", False)),
        "latest_event_kind": str(state.get("latest_event_kind", "")),
        "latest_namespace": list(state.get("latest_namespace", [])),
        "latest_checkpoint_kind": str(state.get("latest_checkpoint_kind", "")),
        "latest_task_path": str(state.get("latest_task_path", "")),
        "latest_task_status": str(state.get("latest_task_status", "")),
        "latest_debug_summary": str(state.get("latest_debug_summary", "")),
        "event_count": int(state.get("event_count", 0) or 0),
        "helper_pointer": helper_pointer,
    }


def _apply_stream_state(
    thread: dict[str, Any],
    *,
    selected_modes: list[str] | None = None,
    subgraphs: bool | None = None,
    latest_event_kind: str = "",
    latest_namespace: list[str] | None = None,
    latest_checkpoint_kind: str = "",
    latest_task_path: str = "",
    latest_task_status: str = "",
    latest_debug_summary: str = "",
) -> dict[str, Any]:
    state = _ensure_stream_state(thread)
    if selected_modes is not None:
        state["selected_modes"] = sorted(dict.fromkeys(selected_modes))
    if subgraphs is not None:
        state["subgraphs"] = bool(subgraphs)
    if latest_event_kind:
        state["latest_event_kind"] = latest_event_kind
        state["event_count"] = int(state.get("event_count", 0) or 0) + 1
    if latest_namespace is not None:
        state["latest_namespace"] = latest_namespace
    if latest_checkpoint_kind:
        state["latest_checkpoint_kind"] = latest_checkpoint_kind
    if latest_task_path:
        state["latest_task_path"] = latest_task_path
    if latest_task_status:
        state["latest_task_status"] = latest_task_status
    if latest_debug_summary:
        state["latest_debug_summary"] = latest_debug_summary
    thread["stream_state"] = state
    return state


def _kind_hints_from_context(context_payload: Any) -> list[str]:
    if not isinstance(context_payload, dict):
        return []

    hints: list[str] = []
    for key in sorted(context_payload.keys()):
        normalized = str(key)
        lower = normalized.lower()
        if any(token in lower for token in ("user", "actor", "session")):
            hints.append(f"{normalized}:user_scope")
        elif any(token in lower for token in ("model", "provider", "llm")):
            hints.append(f"{normalized}:model_scope")
        elif any(token in lower for token in ("db", "store", "cache", "redis")):
            hints.append(f"{normalized}:dependency_scope")
        else:
            hints.append(f"{normalized}:opaque")
    return hints


def _ensure_runtime_injection_state(thread: dict[str, Any]) -> dict[str, Any]:
    state = thread.get("runtime_injection_state")
    if isinstance(state, dict):
        state.setdefault("context_schema", "")
        state.setdefault("runtime_context_present", False)
        state.setdefault("runtime_context_keys", [])
        state.setdefault("runtime_context_kind_hints", [])
        state.setdefault("store_configured", False)
        state.setdefault("store_access_expected", False)
        state.setdefault("store_kind", "")
        thread["runtime_injection_state"] = state
        return state

    state = {
        "context_schema": "",
        "runtime_context_present": False,
        "runtime_context_keys": [],
        "runtime_context_kind_hints": [],
        "store_configured": False,
        "store_access_expected": False,
        "store_kind": "",
    }
    thread["runtime_injection_state"] = state
    return state


def _apply_runtime_injection_state(
    thread: dict[str, Any],
    *,
    context_schema: str = "",
    runtime_context: Any = None,
    store_configured: bool | None = None,
    store_access_expected: bool | None = None,
    store_kind: str = "",
) -> dict[str, Any]:
    state = _ensure_runtime_injection_state(thread)
    if context_schema:
        state["context_schema"] = context_schema
    if runtime_context is not None:
        state["runtime_context_present"] = True
        state["runtime_context_keys"] = _payload_keys(runtime_context)
        state["runtime_context_kind_hints"] = _kind_hints_from_context(runtime_context)
    if store_configured is not None:
        state["store_configured"] = bool(store_configured)
    if store_access_expected is not None:
        state["store_access_expected"] = bool(store_access_expected)
    if store_kind:
        state["store_kind"] = store_kind
    thread["runtime_injection_state"] = state
    return state


def _runtime_injection_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    state = thread.get("runtime_injection_state")
    if not isinstance(state, dict):
        state = {}

    helper_pointer: dict[str, Any] = {
        "command": "runtime",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    return {
        "context_schema": str(state.get("context_schema", "")),
        "runtime_context_present": bool(state.get("runtime_context_present", False)),
        "runtime_context_keys": list(state.get("runtime_context_keys", [])),
        "runtime_context_kind_hints": list(state.get("runtime_context_kind_hints", [])),
        "store_configured": bool(state.get("store_configured", False)),
        "store_access_expected": bool(state.get("store_access_expected", False)),
        "store_kind": str(state.get("store_kind", "")),
        "helper_pointer": helper_pointer,
    }


def _ensure_memory_state(thread: dict[str, Any]) -> dict[str, Any]:
    state = thread.get("memory_state")
    if isinstance(state, dict):
        state.setdefault("memory_store_configured", False)
        state.setdefault("memory_store_kind", "")
        state.setdefault("memory_namespaces", [])
        state.setdefault("semantic_memory_enabled", False)
        state.setdefault("semantic_store_kind", "")
        state.setdefault("semantic_namespaces", [])
        thread["memory_state"] = state
        return state

    state = {
        "memory_store_configured": False,
        "memory_store_kind": "",
        "memory_namespaces": [],
        "semantic_memory_enabled": False,
        "semantic_store_kind": "",
        "semantic_namespaces": [],
    }
    thread["memory_state"] = state
    return state


def _apply_memory_state(
    thread: dict[str, Any],
    *,
    memory_store_configured: bool | None = None,
    memory_store_kind: str = "",
    memory_namespaces: list[str] | None = None,
    semantic_memory_enabled: bool | None = None,
    semantic_store_kind: str = "",
    semantic_namespaces: list[str] | None = None,
) -> dict[str, Any]:
    state = _ensure_memory_state(thread)
    if memory_store_configured is not None:
        state["memory_store_configured"] = bool(memory_store_configured)
    if memory_store_kind:
        state["memory_store_kind"] = memory_store_kind
    if memory_namespaces is not None:
        state["memory_namespaces"] = sorted(dict.fromkeys(memory_namespaces))
    if semantic_memory_enabled is not None:
        state["semantic_memory_enabled"] = bool(semantic_memory_enabled)
    if semantic_store_kind:
        state["semantic_store_kind"] = semantic_store_kind
    if semantic_namespaces is not None:
        state["semantic_namespaces"] = sorted(dict.fromkeys(semantic_namespaces))
    thread["memory_state"] = state
    return state


def _memory_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    state = thread.get("memory_state")
    if not isinstance(state, dict):
        state = {}

    helper_pointer: dict[str, Any] = {
        "command": "memory",
        "read_only": False,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    return {
        "memory_store_configured": bool(state.get("memory_store_configured", False)),
        "memory_store_kind": str(state.get("memory_store_kind", "")),
        "memory_namespaces": list(state.get("memory_namespaces", [])),
        "semantic_memory_enabled": bool(state.get("semantic_memory_enabled", False)),
        "semantic_store_kind": str(state.get("semantic_store_kind", "")),
        "semantic_namespaces": list(state.get("semantic_namespaces", [])),
        "helper_pointer": helper_pointer,
    }


def _subgraph_contract(subgraph_id: str) -> dict[str, Any]:
    contract = SUBGRAPHS.get(subgraph_id)
    if isinstance(contract, dict):
        return _clone_payload(contract)
    return {}


def _subgraph_id_for_phase(phase: str) -> str:
    return PHASE_TO_SUBGRAPH.get(phase, "")


def _ensure_subgraph_state(thread: dict[str, Any]) -> dict[str, Any]:
    derived_subgraph = _subgraph_id_for_phase(str(thread.get("phase", "")))
    active_subgraph = derived_subgraph or thread.get("active_subgraph", "")

    if active_subgraph not in SUBGRAPHS:
        thread["active_subgraph"] = ""
        thread["active_subgraph_posture"] = {}
        return {}

    posture = _subgraph_contract(active_subgraph)
    posture["current_phase"] = str(thread.get("phase", ""))
    thread["active_subgraph"] = active_subgraph
    thread["active_subgraph_posture"] = posture
    return posture


def _subgraph_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    active_subgraph = ""
    posture: dict[str, Any] = {}
    if isinstance(thread, dict) and thread:
        derived_subgraph = _subgraph_id_for_phase(str(thread.get("phase", "")))
        stored_subgraph = thread.get("active_subgraph", "")
        if derived_subgraph in SUBGRAPHS:
            active_subgraph = derived_subgraph
            posture = _subgraph_contract(active_subgraph)
        elif stored_subgraph in SUBGRAPHS:
            active_subgraph = stored_subgraph
            stored_posture = thread.get("active_subgraph_posture")
            if isinstance(stored_posture, dict) and stored_posture:
                posture = _clone_payload(stored_posture)
            else:
                posture = _subgraph_contract(active_subgraph)

        if posture:
            posture["current_phase"] = str(thread.get("phase", ""))

    helper_pointer: dict[str, Any] = {
        "command": "subgraphs",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    return {
        "active_subgraph": active_subgraph,
        "active_subgraph_posture": posture,
        "available_subgraphs": sorted(SUBGRAPHS.keys()),
        "helper_pointer": helper_pointer,
    }


def _subgraph_state_inspection_projection(thread: dict[str, Any], thread_id: str = "") -> dict[str, Any]:
    subgraph_projection = _subgraph_projection(thread, thread_id)
    active_subgraph = str(subgraph_projection.get("active_subgraph", ""))
    posture = subgraph_projection.get("active_subgraph_posture")
    posture = posture if isinstance(posture, dict) else {}
    persistence_mode = str(posture.get("persistence_mode_default", ""))
    checkpointer_mode = str(posture.get("checkpointer_mode_default", ""))
    state_inspection_scope = str(posture.get("state_inspection_scope_default", ""))
    static_discoverable = bool(posture.get("static_discoverable", False))
    same_subgraph_parallel_calls_supported = bool(posture.get("same_subgraph_parallel_calls_supported", False))
    state_inspection_default = bool(posture.get("state_inspection_default", False))

    inspection_blockers: list[str] = []
    if not active_subgraph:
        inspection_blockers.append("no_active_subgraph")
    if not static_discoverable:
        inspection_blockers.append("subgraph_not_statically_discoverable")
    if persistence_mode == "stateless" or checkpointer_mode == "disabled":
        inspection_blockers.append("stateless_subgraph")

    state_inspection_available = state_inspection_default and not inspection_blockers
    if not state_inspection_available and not state_inspection_scope:
        state_inspection_scope = "unavailable"

    helper_pointer: dict[str, Any] = {
        "command": "subgraph-state",
        "read_only": True,
    }
    if thread_id:
        helper_pointer["thread_id"] = thread_id

    return {
        "active_subgraph": active_subgraph,
        "persistence_mode": persistence_mode if persistence_mode in SUBGRAPH_PERSISTENCE_MODES else "",
        "checkpointer_mode": checkpointer_mode if checkpointer_mode in SUBGRAPH_CHECKPOINTER_MODES else "",
        "inherits_parent_checkpointer": checkpointer_mode == "inherit_parent",
        "separate_subgraph_memory": checkpointer_mode == "separate_subgraph",
        "durable_execution_supported": persistence_mode != "stateless",
        "interrupts_supported": persistence_mode != "stateless",
        "state_inspection_available": state_inspection_available,
        "state_inspection_scope": (
            state_inspection_scope if state_inspection_scope in SUBGRAPH_STATE_INSPECTION_SCOPES else "unavailable"
        ),
        "static_discoverable": static_discoverable,
        "same_subgraph_parallel_calls_supported": same_subgraph_parallel_calls_supported,
        "inspection_blockers": sorted(dict.fromkeys(inspection_blockers)),
        "helper_pointer": helper_pointer,
    }


def _helper_pointers(thread_id: str) -> dict[str, Any]:
    return {
        "deeper_engine": {
            "command": "deeper-engine",
            "thread_id": thread_id,
            "read_only": True,
        },
        "superstep_engine": {
            "command": "superstep-engine",
            "thread_id": thread_id,
            "read_only": True,
        },
        "stateful_engine": {
            "command": "stateful-engine",
            "thread_id": thread_id,
            "read_only": True,
        },
        "boundary_engine": {
            "command": "boundary-engine",
            "thread_id": thread_id,
            "read_only": True,
        },
        "handoff_engine": {
            "command": "handoff-engine",
            "thread_id": thread_id,
            "read_only": True,
        },
        "approval_engine": {
            "command": "approval-engine",
            "thread_id": thread_id,
            "read_only": True,
        },
        "provenance_engine": {
            "command": "provenance-engine",
            "thread_id": thread_id,
            "read_only": True,
        },
        "artifact_engine": {
            "command": "artifact-engine",
            "thread_id": thread_id,
            "read_only": True,
        },
        "reducer_engine": {
            "command": "reducer-engine",
            "thread_id": thread_id,
            "read_only": True,
        },
        "command_engine": {
            "command": "command-engine",
            "thread_id": thread_id,
            "read_only": True,
        },
        "runtime_engine": {
            "command": "runtime-engine",
            "thread_id": thread_id,
            "read_only": True,
        },
        "memory_engine": {
            "command": "memory-engine",
            "thread_id": thread_id,
            "read_only": True,
        },
        "migration_engine": {
            "command": "migration-engine",
            "thread_id": thread_id,
            "read_only": True,
        },
        "auto_policy": {
            "command": "auto-policy",
            "thread_id": thread_id,
            "read_only": True,
        },
        "fuller_engine": {
            "command": "fuller-engine",
            "thread_id": thread_id,
            "read_only": True,
        },
        "subgraph_state": {
            "command": "subgraph-state",
            "thread_id": thread_id,
            "read_only": True,
        },
        "generalized_routing": {
            "command": "generalized-routing",
            "thread_id": thread_id,
            "read_only": True,
        },
        "live_execution": {
            "command": "live-execution",
            "thread_id": thread_id,
            "read_only": True,
        },
        "invocation": {
            "command": "invocation",
            "thread_id": thread_id,
            "read_only": True,
        },
        "engine": {
            "command": "engine",
            "thread_id": thread_id,
            "read_only": True,
        },
        "approval_queue": {
            "command": "approval-queue",
            "thread_id": thread_id,
            "read_only": True,
        },
        "migration": {
            "command": "migration",
            "thread_id": thread_id,
            "read_only": True,
        },
        "memory": {
            "command": "memory",
            "thread_id": thread_id,
            "read_only": False,
        },
        "runtime": {
            "command": "runtime",
            "thread_id": thread_id,
            "read_only": False,
        },
        "subgraphs": {
            "command": "subgraphs",
            "thread_id": thread_id,
            "read_only": True,
        },
        "status": {
            "command": "status",
            "thread_id": thread_id,
            "read_only": True,
        },
        "inspect": {
            "command": "inspect",
            "thread_id": thread_id,
            "read_only": True,
        },
        "release_thread": {
            "command": "release-thread",
            "thread_id": thread_id,
            "read_only": False,
        },
        "history": {
            "command": "history",
            "thread_id": thread_id,
            "read_only": True,
        },
        "replay": {
            "command": "replay",
            "thread_id": thread_id,
            "requires_target_id": True,
            "read_only": True,
        },
        "recover_time_travel": {
            "command": "recover",
            "thread_id": thread_id,
            "mutation_intent": "explicit-recovery",
            "requires_target_id": True,
            "read_only": False,
        },
        "recover_update_state": {
            "command": "recover",
            "thread_id": thread_id,
            "mutation_intent": "explicit-recovery",
            "recoverable_thread_fields": RECOVERABLE_THREAD_FIELDS,
            "recoverable_interrupt_fields": RECOVERABLE_INTERRUPT_FIELDS,
            "supports_clear_interrupt": True,
            "read_only": False,
        },
        "resume": {
            "command": "resume",
            "thread_id": thread_id,
            "read_only": False,
        },
    }


def _history_targets_from_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    targets: list[dict[str, Any]] = []
    for record in records:
        base = {
            "history_id": record.get("history_id", ""),
            "checkpoint_id": record.get("checkpoint_id", ""),
            "phase": record.get("phase", ""),
            "status": record.get("status", ""),
            "checkpoint_kind": record.get("checkpoint_kind", ""),
            "event_kind": record.get("event_kind", ""),
            "lifecycle_posture": record.get("lifecycle_posture", ""),
            "created_at": record.get("created_at", ""),
            "fidelity": record.get("fidelity", "full"),
            "source_records": record.get("source_records", []),
        }
        if record.get("history_target_id"):
            targets.append(
                {
                    **base,
                    "target_id": record["history_target_id"],
                    "target_kind": "state_history",
                }
            )
        if record.get("checkpoint_target_id"):
            targets.append(
                {
                    **base,
                    "target_id": record["checkpoint_target_id"],
                    "target_kind": "checkpoint",
                }
            )
    return targets


def _history_projection(
    repo_root: Any,
    thread_id: str,
    thread: dict[str, Any],
    checkpoint: dict[str, Any],
    interrupt: dict[str, Any],
) -> dict[str, Any]:
    path = history_record_path(repo_root, thread_id)
    bundle = read_history(repo_root, thread_id)
    if isinstance(bundle, dict) and bundle.get("records"):
        records = bundle.get("records", [])
        targets = _history_targets_from_records(records)
        source_records = sorted(
            {
                source
                for record in records
                for source in record.get("source_records", [])
                if isinstance(source, str) and source
            }
        )
        return {
            "compatibility": "tracked_history",
            "history_path": str(path),
            "history_record_count": len(records),
            "target_count": len(targets),
            "available_targets": targets,
            "source_records": source_records,
        }

    source_records = [str(thread_record_path(repo_root, thread_id))]
    targets: list[dict[str, Any]] = []
    if thread:
        targets.append(
            {
                "target_id": "history:synthetic-latest",
                "target_kind": "state_history",
                "history_id": "synthetic-latest",
                "checkpoint_id": "synthetic-latest" if checkpoint else "",
                "phase": thread.get("phase", ""),
                "status": thread.get("status", ""),
                "checkpoint_kind": checkpoint.get("checkpoint_kind", ""),
                "event_kind": "synthetic_latest_only",
                "lifecycle_posture": _recovery_projection(thread)["posture"],
                "created_at": thread.get("updated_at", ""),
                "fidelity": "reduced",
                "source_records": source_records,
            }
        )
    if checkpoint:
        source_records.append(str(checkpoint_record_path(repo_root, thread_id)))
        targets.append(
            {
                "target_id": "checkpoint:synthetic-latest",
                "target_kind": "checkpoint",
                "history_id": "synthetic-latest",
                "checkpoint_id": "synthetic-latest",
                "phase": checkpoint.get("phase", ""),
                "status": thread.get("status", ""),
                "checkpoint_kind": checkpoint.get("checkpoint_kind", ""),
                "event_kind": "synthetic_latest_only",
                "lifecycle_posture": _recovery_projection(thread)["posture"],
                "created_at": checkpoint.get("updated_at", ""),
                "fidelity": "reduced",
                "source_records": source_records,
            }
        )
    if interrupt:
        source_records.append(str(interrupt_record_path(repo_root, thread_id)))

    if targets:
        compatibility = "synthetic_latest_only"
    else:
        compatibility = "no_history"
    return {
        "compatibility": compatibility,
        "history_path": str(path),
        "history_record_count": 0,
        "target_count": len(targets),
        "available_targets": targets,
        "source_records": sorted(set(source_records)),
    }


def _append_history_record(
    repo_root: Any,
    thread: dict[str, Any],
    checkpoint: dict[str, Any],
    interrupt: dict[str, Any],
    event_kind: str,
) -> dict[str, Any]:
    thread_id = thread["thread_id"]
    bundle = read_history(repo_root, thread_id)
    if not isinstance(bundle, dict) or not bundle:
        bundle = _default_history_bundle(thread_id)
    records = bundle.setdefault("records", [])
    ordinal = int(bundle.get("next_ordinal", len(records) + 1) or (len(records) + 1))
    history_id = f"state-{ordinal:04d}"
    checkpoint_id = checkpoint.get("checkpoint_id", "") if checkpoint else ""
    source_records = [str(thread_record_path(repo_root, thread_id))]
    if checkpoint:
        source_records.append(str(checkpoint_record_path(repo_root, thread_id)))
    if interrupt:
        source_records.append(str(interrupt_record_path(repo_root, thread_id)))
    record = {
        "history_id": history_id,
        "history_target_id": f"history:{history_id}",
        "checkpoint_id": checkpoint_id,
        "checkpoint_target_id": f"checkpoint:{checkpoint_id}" if checkpoint_id else "",
        "record_kind": "state_snapshot",
        "event_kind": event_kind,
        "checkpoint_kind": checkpoint.get("checkpoint_kind", "") if checkpoint else "",
        "phase": thread.get("phase", ""),
        "status": thread.get("status", ""),
        "lifecycle_posture": _recovery_projection(thread)["posture"],
        "created_at": _now(),
        "fidelity": "full",
        "source_records": source_records,
        "thread_snapshot": _clone_payload(thread),
        "checkpoint_snapshot": _clone_payload(checkpoint) if checkpoint else {},
        "interrupt_snapshot": _clone_payload(interrupt) if interrupt else {},
    }
    records.append(record)
    bundle["compatibility"] = "tracked_history"
    bundle["next_ordinal"] = ordinal + 1
    bundle["updated_at"] = record["created_at"]
    write_history(repo_root, bundle)
    return bundle


def _resolve_replay_target(
    repo_root: Any,
    thread_id: str,
    target_id: str,
    current_thread: dict[str, Any],
    current_checkpoint: dict[str, Any],
    current_interrupt: dict[str, Any],
) -> dict[str, Any]:
    history_bundle = read_history(repo_root, thread_id)
    if isinstance(history_bundle, dict):
        for record in history_bundle.get("records", []):
            if target_id in {record.get("history_target_id", ""), record.get("checkpoint_target_id", "")}:
                target_kind = "checkpoint" if target_id.startswith("checkpoint:") else "state_history"
                return {
                    "target_id": target_id,
                    "target_kind": target_kind,
                    "record": record,
                    "thread_snapshot": _clone_payload(record.get("thread_snapshot", {})),
                    "checkpoint_snapshot": _clone_payload(record.get("checkpoint_snapshot", {})),
                    "interrupt_snapshot": _clone_payload(record.get("interrupt_snapshot", {})),
                }
    if target_id == "history:synthetic-latest" and current_thread:
        return {
            "target_id": target_id,
            "target_kind": "state_history",
            "record": {
                "history_id": "synthetic-latest",
                "checkpoint_id": "synthetic-latest" if current_checkpoint else "",
                "source_records": [str(thread_record_path(repo_root, thread_id))],
                "fidelity": "reduced",
            },
            "thread_snapshot": _clone_payload(current_thread),
            "checkpoint_snapshot": _clone_payload(current_checkpoint),
            "interrupt_snapshot": _clone_payload(current_interrupt),
        }
    if target_id == "checkpoint:synthetic-latest" and current_checkpoint:
        return {
            "target_id": target_id,
            "target_kind": "checkpoint",
            "record": {
                "history_id": "synthetic-latest",
                "checkpoint_id": "synthetic-latest",
                "source_records": [str(checkpoint_record_path(repo_root, thread_id))],
                "fidelity": "reduced",
            },
            "thread_snapshot": _clone_payload(current_thread),
            "checkpoint_snapshot": _clone_payload(current_checkpoint),
            "interrupt_snapshot": _clone_payload(current_interrupt),
        }
    raise SystemExit(f"Replay target not found: {target_id}")


def _parse_assignment(raw_value: str) -> tuple[str, Any]:
    if "=" not in raw_value:
        raise SystemExit(f"Expected field=value assignment, got: {raw_value}")
    field_name, value = raw_value.split("=", 1)
    normalized_field = field_name.strip()
    if not normalized_field:
        raise SystemExit(f"Expected field=value assignment, got: {raw_value}")
    try:
        parsed_value = json.loads(value)
    except json.JSONDecodeError:
        parsed_value = value
    return normalized_field, parsed_value


def _coerce_thread_field(field_name: str, value: Any) -> Any:
    if field_name not in RECOVERABLE_THREAD_FIELDS:
        raise SystemExit(f"Out-of-scope recoverable thread field: {field_name}")
    if field_name == "phase":
        if value not in ROOT_PHASES:
            raise SystemExit(f"Invalid phase for recovery: {value}")
        return value
    if field_name == "active_loop":
        if value not in list(LOOP_CAPABLE_FLOWS.keys()) + [""]:
            raise SystemExit(f"Invalid active_loop for recovery: {value}")
        return value
    if field_name == "last_gate_verdict":
        if value not in GATE_VERDICTS + [""]:
            raise SystemExit(f"Invalid last_gate_verdict for recovery: {value}")
        return value
    if field_name in {"parallel_slices", "blocking_issues", "iteration_count", "iteration_budget"}:
        if not isinstance(value, int) or value < 0:
            raise SystemExit(f"Recovery field {field_name} must be a non-negative integer")
        return value
    if value is None:
        return ""
    if not isinstance(value, str):
        raise SystemExit(f"Recovery field {field_name} must be a string")
    return value


def _coerce_interrupt_field(field_name: str, value: Any) -> Any:
    if field_name not in RECOVERABLE_INTERRUPT_FIELDS:
        raise SystemExit(f"Out-of-scope recoverable interrupt field: {field_name}")
    if field_name == "interrupt_point":
        if value not in INTERRUPT_POINTS + [""]:
            raise SystemExit(f"Invalid interrupt_point for recovery: {value}")
        return value
    if value is None:
        return ""
    if not isinstance(value, str):
        raise SystemExit(f"Recovery interrupt field {field_name} must be a string")
    return value



def _survivor_queue_status(queue: dict[str, Any]) -> str:
    if not queue:
        return "missing"
    items = queue.get("items", []) if isinstance(queue, dict) else []
    if items:
        return "present"
    return "empty"


def _release_projection(repo_root: Any, thread_id: str, thread: dict[str, Any] | None = None) -> dict[str, Any]:
    thread = thread or {}
    receipt = read_release_receipt(repo_root, thread_id)
    release_action = str(receipt.get("release_action", thread.get("release_action", ""))) if isinstance(receipt, dict) else ""
    receipt_path = release_receipt_path(repo_root, thread_id)
    status = str(thread.get("status", ""))
    return {
        "release_receipt_present": bool(receipt),
        "release_receipt_path": str(receipt_path),
        "release_action": release_action,
        "released_at": str(receipt.get("released_at", thread.get("released_at", ""))) if isinstance(receipt, dict) else str(thread.get("released_at", "")),
        "released_by": str(receipt.get("released_by", thread.get("released_by", ""))) if isinstance(receipt, dict) else str(thread.get("released_by", "")),
        "completed_at": str(thread.get("completed_at", "")),
        "final_phase": str(thread.get("final_phase", "")),
        "result_summary": str(thread.get("result_summary", "")),
        "handoff_target": str(receipt.get("handoff_target", thread.get("handoff_target", ""))) if isinstance(receipt, dict) else str(thread.get("handoff_target", "")),
        "reason": str(receipt.get("reason", thread.get("reason", ""))) if isinstance(receipt, dict) else str(thread.get("reason", "")),
        "timeout_release": bool(receipt.get("timeout_release", False)) if isinstance(receipt, dict) else False,
        "active_running_state": status == "running" and not receipt,
    }


def _release_action_status(release_action: str) -> str:
    if release_action == "close":
        return "closed"
    if release_action == "release":
        return "released"
    if release_action == "handoff":
        return "handoff"
    raise SystemExit(f"Unsupported release_action: {release_action}")


def _save_backend_projection(repo_root: Any, layout: dict[str, str], thread: dict[str, Any]) -> None:
    checkpoint = read_checkpoint(repo_root, thread["thread_id"])
    interrupt = read_interrupt(repo_root, thread["thread_id"])
    backend_routing_projection = _backend_routing_projection(thread, thread["thread_id"])
    _persist_scoped_activation(repo_root, layout, thread, backend_routing_projection)
    save_backend_record(
        repo_root,
        {
            "backend": "langgraph",
            "thread_id": thread["thread_id"],
            "repo_root": str(repo_root),
            "phase": thread.get("phase", ""),
            "status": thread.get("status", ""),
            "updated_at": thread.get("updated_at", _now()),
            "layout": layout,
            **backend_routing_projection,
            **_release_projection(repo_root, thread["thread_id"], thread),
            "release_projection": _release_projection(repo_root, thread["thread_id"], thread),
            **_loop_projection(thread),
            "history_projection": _history_projection(repo_root, thread["thread_id"], thread, checkpoint, interrupt),
            "recovery_projection": _recovery_projection(thread),
            "reducer_projection": _reducer_projection(thread),
            "graph_kernel_projection": _graph_kernel_projection(thread, thread["thread_id"]),
            "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, thread["thread_id"]),
            "compiled_invocation_projection": _compiled_invocation_projection(thread, thread["thread_id"]),
            "live_execution_projection": _live_execution_projection(thread, thread["thread_id"]),
            "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(
                thread, thread["thread_id"]
            ),
            "deeper_live_primary_engine_projection": _deeper_live_primary_engine_projection(
                thread, thread["thread_id"]
            ),
            "superstep_live_primary_engine_projection": _superstep_live_primary_engine_projection(
                thread, thread["thread_id"]
            ),
            "stateful_live_primary_engine_projection": _stateful_live_primary_engine_projection(
                thread, thread["thread_id"]
            ),
            "boundary_state_live_primary_engine_projection": _boundary_state_live_primary_engine_projection(
                thread, thread["thread_id"]
            ),
            "handoff_state_live_primary_engine_projection": _handoff_state_live_primary_engine_projection(
                thread, thread["thread_id"]
            ),
            "approval_aware_live_primary_engine_projection": _approval_aware_live_primary_engine_projection(
                thread, thread["thread_id"]
            ),
            "provenance_state_live_primary_engine_projection": _provenance_state_live_primary_engine_projection(
                thread, thread["thread_id"]
            ),
            "durable_artifact_aware_live_primary_engine_projection": (
                _durable_artifact_aware_live_primary_engine_projection(thread, thread["thread_id"])
            ),
            "reducer_aware_live_primary_engine_projection": (
                _reducer_aware_live_primary_engine_projection(thread, thread["thread_id"])
            ),
            "command_aware_live_primary_engine_projection": (
                _command_aware_live_primary_engine_projection(thread, thread["thread_id"])
            ),
            "runtime_aware_live_primary_engine_projection": (
                _runtime_aware_live_primary_engine_projection(thread, thread["thread_id"])
            ),
            "memory_aware_live_primary_engine_projection": (
                _memory_aware_live_primary_engine_projection(thread, thread["thread_id"])
            ),
            "migration_aware_live_primary_engine_projection": (
                _migration_aware_live_primary_engine_projection(thread, thread["thread_id"])
            ),
            "generalized_live_routing_projection": _generalized_live_routing_projection(thread, thread["thread_id"]),
            "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(
                thread, thread["thread_id"]
            ),
            "approval_queue_projection": _approval_queue_projection(thread, thread["thread_id"]),
            "migration_projection": _migration_projection(thread, thread["thread_id"]),
            "subgraph_projection": _subgraph_projection(thread, thread["thread_id"]),
            "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(
                thread, thread["thread_id"]
            ),
            "command_projection": _command_projection(thread, thread["thread_id"]),
            "stream_projection": _stream_projection(thread, thread["thread_id"]),
            "runtime_injection_projection": _runtime_injection_projection(thread, thread["thread_id"]),
            "memory_projection": _memory_projection(thread, thread["thread_id"]),
        },
    )


def _artifact_presence_summary(
    repo_root: Any,
    thread_id: str,
) -> dict[str, Any]:
    brief = read_implementation_brief(repo_root, thread_id)
    queue = read_survivor_queue(repo_root, thread_id)
    receipt = read_release_receipt(repo_root, thread_id)
    items = queue.get("items", []) if isinstance(queue, dict) else []
    return {
        "implementation_brief_present": bool(brief),
        "implementation_brief_id": str(brief.get("brief_id", "")) if isinstance(brief, dict) else "",
        "implementation_brief_source_evidence_ref_count": (
            len(brief.get("source_evidence_refs", [])) if isinstance(brief, dict) else 0
        ),
        "survivor_queue_present": bool(queue),
        "survivor_queue_kind": str(queue.get("queue_kind", "")) if isinstance(queue, dict) else "",
        "survivor_count": len(items),
        "implementation_brief_path": str(implementation_brief_path(repo_root, thread_id)),
        "survivor_queue_path": str(survivor_queue_path(repo_root, thread_id)),
        "release_receipt_present": bool(receipt),
        "release_receipt_path": str(release_receipt_path(repo_root, thread_id)),
        "release_action": str(receipt.get("release_action", "")) if isinstance(receipt, dict) else "",
    }


def _refresh_backend_artifact_projection(repo_root: Any, thread_id: str) -> None:
    backend_record = load_backend_record(repo_root)
    if not backend_record or backend_record.get("thread_id") != thread_id:
        return
    backend_record.update(_artifact_presence_summary(repo_root, thread_id))
    thread = read_thread_record(repo_root, thread_id)
    if thread:
        backend_record.update(_backend_routing_projection(thread, thread_id))
        backend_record.update(_release_projection(repo_root, thread_id, thread))
        backend_record["release_projection"] = _release_projection(repo_root, thread_id, thread)
        backend_record["durable_artifact_aware_live_primary_engine_projection"] = (
            _durable_artifact_aware_live_primary_engine_projection(thread, thread_id)
        )
        backend_record["reducer_aware_live_primary_engine_projection"] = (
            _reducer_aware_live_primary_engine_projection(thread, thread_id)
        )
        backend_record["command_aware_live_primary_engine_projection"] = (
            _command_aware_live_primary_engine_projection(thread, thread_id)
        )
        backend_record["runtime_aware_live_primary_engine_projection"] = (
            _runtime_aware_live_primary_engine_projection(thread, thread_id)
        )
        backend_record["memory_aware_live_primary_engine_projection"] = (
            _memory_aware_live_primary_engine_projection(thread, thread_id)
        )
        backend_record["migration_aware_live_primary_engine_projection"] = (
            _migration_aware_live_primary_engine_projection(thread, thread_id)
        )
    else:
        backend_record.update(
            {
                "routing_posture": "missing_or_stale_selector",
                "routing_eligible": False,
            }
        )
    save_backend_record(repo_root, backend_record)


def _brief_id(thread_id: str) -> str:
    return f"brief-{thread_id.replace(':', '-')}-{uuid.uuid4().hex[:8]}"


def _queue_id(thread_id: str) -> str:
    return f"survivor-queue-{thread_id.replace(':', '-')}"


def _normalize_branch_items(channel_name: str, branch_id: str, raw_items: Any) -> list[dict[str, Any]]:
    contract = REDUCER_MERGE_CHANNELS[channel_name]
    identity_field = contract["identity_field"]
    values = raw_items if isinstance(raw_items, list) else [raw_items]
    items: list[dict[str, Any]] = []
    for raw_item in values:
        item = dict(raw_item) if isinstance(raw_item, dict) else {"value": raw_item}
        item.setdefault("branch_id", branch_id)
        if identity_field not in item or not item.get(identity_field):
            serialized = json.dumps(item, sort_keys=True, ensure_ascii=True)
            item[identity_field] = f"{branch_id}:{serialized}"
        items.append(item)
    return items


def _register_invalid_multi_writer(
    reducer_state: dict[str, Any],
    branch_id: str,
    field: str,
    reason: str,
    attempted_value: Any,
) -> None:
    updates = reducer_state.setdefault("invalid_multi_writer_updates", [])
    normalized_value = json.dumps(attempted_value, sort_keys=True, ensure_ascii=True)
    key = (branch_id, field, reason, normalized_value)
    existing_keys = {
        (
            update.get("branch_id", ""),
            update.get("field", ""),
            update.get("reason", ""),
            json.dumps(update.get("attempted_value"), sort_keys=True, ensure_ascii=True),
        )
        for update in updates
    }
    if key in existing_keys:
        return
    updates.append(
        {
            "branch_id": branch_id,
            "field": field,
            "reason": reason,
            "attempted_value": attempted_value,
            "updated_at": _now(),
        }
    )


def _merge_branch_payload(thread: dict[str, Any], payload: dict[str, Any]) -> None:
    reducer_state = _ensure_reducer_state(thread)
    branch_id = payload.get("branch_id", f"branch-{uuid.uuid4().hex[:8]}")
    reducer_state["compatibility"] = "reducer_aware"
    reducer_state.setdefault("source_records", [])
    source_record = f"branch:{branch_id}"
    if source_record not in reducer_state["source_records"]:
        reducer_state["source_records"].append(source_record)

    requested_fanout_state = payload.get("fanout_state")
    if requested_fanout_state:
        reducer_state["fanout_state"] = requested_fanout_state
    elif payload.get("reducer_channels"):
        reducer_state["fanout_state"] = "partial"

    reducer_channels = payload.get("reducer_channels", {})
    if isinstance(reducer_channels, dict):
        channels = reducer_state.setdefault("channels", {})
        for channel_name, raw_items in reducer_channels.items():
            contract = REDUCER_MERGE_CHANNELS.get(channel_name)
            if contract is None:
                _register_invalid_multi_writer(
                    reducer_state,
                    branch_id,
                    channel_name,
                    "unknown_merge_channel",
                    raw_items,
                )
                continue

            channel_state = channels.setdefault(
                channel_name,
                {
                    "reducer_kind": contract["reducer_kind"],
                    "identity_field": contract["identity_field"],
                    "items": [],
                    "source_branches": [],
                    "item_count": 0,
                },
            )

            normalized_items = _normalize_branch_items(channel_name, branch_id, raw_items)
            identity_field = contract["identity_field"]
            if contract["reducer_kind"] == "replace_by_branch":
                existing = {
                    str(item.get("branch_id", "")): item
                    for item in channel_state.get("items", [])
                    if isinstance(item, dict)
                }
                for item in normalized_items:
                    existing[str(item.get("branch_id", branch_id))] = item
                merged_items = sorted(
                    existing.values(),
                    key=lambda item: (
                        str(item.get("branch_id", "")),
                        json.dumps(item, sort_keys=True, ensure_ascii=True),
                    ),
                )
            else:
                existing = {
                    str(item.get(identity_field, "")): item
                    for item in channel_state.get("items", [])
                    if isinstance(item, dict)
                }
                for item in normalized_items:
                    existing[str(item.get(identity_field, ""))] = item
                merged_items = sorted(existing.values(), key=lambda item: str(item.get(identity_field, "")))

            source_branches = sorted(
                set([str(branch) for branch in channel_state.get("source_branches", [])] + [str(branch_id)])
            )
            channel_state.update(
                {
                    "reducer_kind": contract["reducer_kind"],
                    "identity_field": identity_field,
                    "items": merged_items,
                    "source_branches": source_branches,
                    "item_count": len(merged_items),
                    "updated_at": _now(),
                }
            )

    single_writer_updates = payload.get("single_writer_updates", {})
    if isinstance(single_writer_updates, dict):
        protected_fields = set(SINGLE_WRITER_FIELDS + LEADER_OWNED_SUMMARY_FIELDS)
        for field_name, attempted_value in single_writer_updates.items():
            if field_name in protected_fields:
                current_value = thread.get(field_name)
                if current_value != attempted_value:
                    _register_invalid_multi_writer(
                        reducer_state,
                        branch_id,
                        field_name,
                        "single_writer_field_conflict",
                        attempted_value,
                    )
            else:
                _register_invalid_multi_writer(
                    reducer_state,
                    branch_id,
                    field_name,
                    "unclassified_multi_writer_field",
                    attempted_value,
                )

    thread["reducer_state"] = reducer_state


def _seed_loop_state(thread: dict[str, Any], loop_kind: str | None, iteration_budget: int) -> None:
    if not loop_kind:
        return
    flow = LOOP_CAPABLE_FLOWS[loop_kind]
    if not thread.get("active_loop"):
        thread["active_loop"] = loop_kind
    if not thread.get("loop_stage"):
        thread["loop_stage"] = flow["initial_stage"]
    if not thread.get("entered_at"):
        thread["entered_at"] = _now()
    if not thread.get("iteration_budget"):
        thread["iteration_budget"] = iteration_budget
    thread.setdefault("iteration_count", 0)
    thread.setdefault("last_gate_verdict", "")
    thread.setdefault("last_gate_reason", "")
    thread.setdefault("stop_reason", "")
    _ensure_reducer_state(thread)


def _build_interrupt_payload(thread: dict[str, Any], interrupt_point: str, reason: str = "") -> dict[str, Any]:
    _set_approval_queue_state(
        thread,
        [
            {
                "interrupt_point": interrupt_point,
                "reason": reason,
                "value_summary": reason or interrupt_point,
            }
        ],
        default_interrupt_point=interrupt_point,
        default_reason=reason,
    )
    payload = _interrupt_payload_from_queue(thread)
    if not payload:
        return {}
    payload["phase"] = thread.get("phase", "")
    return payload


def _interrupt_point_for_thread(thread: dict[str, Any]) -> str:
    if thread.get("phase") == "freeze-plan":
        return "freeze-plan"
    if thread.get("phase") == "stabilize":
        return "stabilize-risk-review"
    return "verify-accept-failed"


def _apply_gate_verdict(thread: dict[str, Any], verdict: str, reason: str = "") -> dict[str, Any] | None:
    thread["last_gate_verdict"] = verdict
    thread["last_gate_reason"] = reason
    active_loop = thread.get("active_loop", "")
    flow = LOOP_CAPABLE_FLOWS.get(active_loop, {})
    interrupt_payload = None

    if verdict == "accept":
        thread["status"] = "accepted"
        thread["stop_reason"] = "accepted"
        thread["loop_stage"] = "accept"
        if flow.get("accept_phase"):
            thread["phase"] = flow["accept_phase"]
    elif verdict == "revise":
        next_count = int(thread.get("iteration_count", 0) or 0) + 1
        thread["iteration_count"] = next_count
        budget = int(thread.get("iteration_budget", 0) or 0)
        if budget and next_count >= budget:
            thread["status"] = "halted"
            thread["stop_reason"] = "iteration_budget_exhausted"
            thread["loop_stage"] = "halted"
        else:
            thread["status"] = "running"
            thread["stop_reason"] = ""
            thread["loop_stage"] = flow.get("resume_stage", thread.get("loop_stage", ""))
    elif verdict == "needs_human":
        thread["status"] = "waiting_for_approval"
        thread["stop_reason"] = "needs_human"
        thread["loop_stage"] = "needs_human"
        interrupt_payload = _build_interrupt_payload(thread, _interrupt_point_for_thread(thread), reason)
    elif verdict == "escalate":
        thread["status"] = "escalated"
        thread["stop_reason"] = "escalated"
        thread["loop_stage"] = "escalated"
    elif verdict == "halt":
        thread["status"] = "halted"
        thread["stop_reason"] = "non_repairable_failure"
        thread["loop_stage"] = "halted"

    return interrupt_payload


def cmd_run(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    layout = ensure_layout(repo_root)
    worktree_id = args.worktree_id or detect_worktree_id(repo_root)
    thread_id = args.thread_id or stable_thread_id(repo_root, worktree_id, args.task_id)
    command_update = _load_json_option(args.command_update_json, args.command_update_file)
    resume_payload = _load_json_option(args.resume_payload_json, args.resume_payload_file)
    runtime_context = _load_json_option(args.runtime_context_json, args.runtime_context_file)
    thread_payload = {
        "thread_id": thread_id,
        "repo_root": str(repo_root),
        "worktree_id": worktree_id,
        "task": args.task,
        "phase": args.phase,
        "parallel_slices": args.parallel_slices,
        "blocking_issues": args.blocking_issues,
        "backend": "langgraph",
        "langgraph_available": LANGGRAPH_AVAILABLE,
        "status": "running",
        "updated_at": _now(),
    }
    _ensure_scoped_activation_state(thread_payload)
    _ensure_graph_contract(
        thread_payload,
        graph_contract_id=args.thread_graph_contract_id,
        topology_version=args.thread_topology_version,
        state_schema_version=args.thread_state_schema_version,
    )
    _seed_loop_state(thread_payload, args.loop_kind, args.iteration_budget)
    _ensure_reducer_state(thread_payload)
    _ensure_subgraph_state(thread_payload)
    _ensure_stream_state(thread_payload)
    _ensure_runtime_injection_state(thread_payload)
    _ensure_memory_state(thread_payload)
    _ensure_approval_queue_state(thread_payload)
    _persist_migration_state(thread_payload)
    _persist_runtime_state_layers(thread_payload)
    _apply_runtime_injection_state(
        thread_payload,
        context_schema=args.context_schema,
        runtime_context=runtime_context,
        store_configured=(True if args.store_configured else None),
        store_access_expected=(True if args.store_access_expected else None),
        store_kind=args.store_kind,
    )
    _apply_memory_state(
        thread_payload,
        memory_store_configured=(True if args.memory_store_configured else None),
        memory_store_kind=args.memory_store_kind,
        memory_namespaces=args.memory_namespace if args.memory_namespace else None,
        semantic_memory_enabled=(True if args.semantic_memory_enabled else None),
        semantic_store_kind=args.semantic_store_kind,
        semantic_namespaces=args.semantic_namespace if args.semantic_namespace else None,
    )
    thread_payload["command_state"] = _build_command_state(
        thread_payload,
        transition_kind=args.command_kind,
        goto_target=args.command_goto,
        graph_scope=args.command_graph_scope,
        parent_handoff_target=args.parent_handoff_target,
        update_payload=command_update,
        resume_payload=resume_payload,
        await_command_resume=args.await_command_resume,
    )
    checkpoint_id = _checkpoint_id(thread_id)
    checkpoint_payload = {
        "thread_id": thread_id,
        "checkpoint_id": checkpoint_id,
        "phase": args.phase,
        "checkpoint_kind": "skeleton",
        "loop_projection": _loop_projection(thread_payload),
        "reducer_projection": _reducer_projection(thread_payload),
        "graph_kernel_projection": _graph_kernel_projection(thread_payload, thread_id),
        "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread_payload, thread_id),
        "compiled_invocation_projection": _compiled_invocation_projection(thread_payload, thread_id),
        "live_execution_projection": _live_execution_projection(thread_payload, thread_id),
        "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(
            thread_payload, thread_id
        ),
        "deeper_live_primary_engine_projection": _deeper_live_primary_engine_projection(
            thread_payload, thread_id
        ),
        "generalized_live_routing_projection": _generalized_live_routing_projection(thread_payload, thread_id),
        "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(thread_payload, thread_id),
        "approval_queue_projection": _approval_queue_projection(thread_payload, thread_id),
        "migration_projection": _migration_projection(thread_payload, thread_id),
        "subgraph_projection": _subgraph_projection(thread_payload, thread_id),
        "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread_payload, thread_id),
        "command_projection": _command_projection(thread_payload, thread_id),
        "stream_projection": _stream_projection(thread_payload, thread_id),
        "runtime_injection_projection": _runtime_injection_projection(thread_payload, thread_id),
        "memory_projection": _memory_projection(thread_payload, thread_id),
        "updated_at": _now(),
    }
    interrupt_payload = _build_interrupt_payload(thread_payload, "freeze-plan") if args.phase == "freeze-plan" else {}
    _persist_runtime_state_layers(thread_payload)
    checkpoint_payload["approval_queue_projection"] = _approval_queue_projection(thread_payload, thread_id)
    checkpoint_payload["graph_kernel_projection"] = _graph_kernel_projection(thread_payload, thread_id)
    checkpoint_payload["primary_runtime_engine_projection"] = _primary_runtime_engine_projection(thread_payload, thread_id)
    checkpoint_payload["compiled_invocation_projection"] = _compiled_invocation_projection(thread_payload, thread_id)
    checkpoint_payload["live_execution_projection"] = _live_execution_projection(thread_payload, thread_id)
    checkpoint_payload["fuller_live_primary_engine_projection"] = _fuller_live_primary_engine_projection(
        thread_payload, thread_id
    )
    checkpoint_payload["deeper_live_primary_engine_projection"] = _deeper_live_primary_engine_projection(
        thread_payload, thread_id
    )
    checkpoint_payload["generalized_live_routing_projection"] = _generalized_live_routing_projection(
        thread_payload, thread_id
    )
    checkpoint_payload["automatic_runtime_policy_projection"] = _automatic_runtime_policy_projection(
        thread_payload, thread_id
    )
    write_thread_record(repo_root, thread_payload)
    write_checkpoint(repo_root, checkpoint_payload)
    if interrupt_payload:
        write_interrupt(repo_root, interrupt_payload)
    else:
        delete_interrupt(repo_root, thread_id)
    _append_history_record(repo_root, thread_payload, checkpoint_payload, interrupt_payload, "run")
    _save_backend_projection(repo_root, layout, thread_payload)
    _emit(
        {
            "operation": "run",
            "thread_id": thread_id,
            "repo_root": str(repo_root),
            "layout": layout,
            "thread": thread_payload,
            "checkpoint": checkpoint_payload,
            "interrupt": interrupt_payload,
            "thread_path": str(thread_record_path(repo_root, thread_id)),
            "checkpoint_path": str(checkpoint_record_path(repo_root, thread_id)),
            "interrupt_path": str(interrupt_record_path(repo_root, thread_id)),
            "history_path": str(history_record_path(repo_root, thread_id)),
            "backend_record_path": str(backend_record_path(repo_root)),
            "langgraph_available": LANGGRAPH_AVAILABLE,
            "root_phases": ROOT_PHASES,
            "subgraphs": SUBGRAPHS,
            "loop_projection": _loop_projection(thread_payload),
            "graph_kernel_projection": _graph_kernel_projection(thread_payload, thread_id),
            "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread_payload, thread_id),
            "compiled_invocation_projection": _compiled_invocation_projection(thread_payload, thread_id),
            "live_execution_projection": _live_execution_projection(thread_payload, thread_id),
            "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(
                thread_payload, thread_id
            ),
            "deeper_live_primary_engine_projection": _deeper_live_primary_engine_projection(
                thread_payload, thread_id
            ),
            "generalized_live_routing_projection": _generalized_live_routing_projection(thread_payload, thread_id),
            "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(thread_payload, thread_id),
            "approval_queue_projection": _approval_queue_projection(thread_payload, thread_id),
            "migration_projection": _migration_projection(thread_payload, thread_id),
            "subgraph_projection": _subgraph_projection(thread_payload, thread_id),
            "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(
                thread_payload, thread_id
            ),
            "command_projection": _command_projection(thread_payload, thread_id),
            "stream_projection": _stream_projection(thread_payload, thread_id),
            "runtime_injection_projection": _runtime_injection_projection(thread_payload, thread_id),
            "memory_projection": _memory_projection(thread_payload, thread_id),
            "history_projection": _history_projection(
                repo_root,
                thread_id,
                thread_payload,
                checkpoint_payload,
                interrupt_payload,
            ),
            "recovery_projection": _recovery_projection(thread_payload),
            "helper_pointers": _helper_pointers(thread_id),
        }
    )


def cmd_status(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    checkpoint = read_checkpoint(repo_root, args.thread_id)
    interrupt = read_interrupt(repo_root, args.thread_id)
    history_projection = _history_projection(repo_root, args.thread_id, thread, checkpoint, interrupt)
    _emit(
        {
            "operation": "status",
            "thread": thread,
            "checkpoint": checkpoint,
            "interrupt": interrupt,
            "backend_record": load_backend_record(repo_root),
            "release_receipt": read_release_receipt(repo_root, args.thread_id),
            "release_projection": _release_projection(repo_root, args.thread_id, thread),
            "loop_projection": _loop_projection(thread),
            "history_projection": history_projection,
            "recovery_projection": _recovery_projection(thread),
            "helper_pointers": _helper_pointers(args.thread_id),
            "reducer_projection": _reducer_projection(thread),
            "graph_kernel_projection": _graph_kernel_projection(thread, args.thread_id),
            "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, args.thread_id),
            "compiled_invocation_projection": _compiled_invocation_projection(thread, args.thread_id),
            "live_execution_projection": _live_execution_projection(thread, args.thread_id),
            "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(thread, args.thread_id),
            "deeper_live_primary_engine_projection": _deeper_live_primary_engine_projection(thread, args.thread_id),
            "generalized_live_routing_projection": _generalized_live_routing_projection(thread, args.thread_id),
            "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(thread, args.thread_id),
            "approval_queue_projection": _approval_queue_projection(thread, args.thread_id),
            "migration_projection": _migration_projection(thread, args.thread_id),
            "subgraph_projection": _subgraph_projection(thread, args.thread_id),
            "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread, args.thread_id),
            "command_projection": _command_projection(thread, args.thread_id),
            "stream_projection": _stream_projection(thread, args.thread_id),
            "runtime_injection_projection": _runtime_injection_projection(thread, args.thread_id),
            "memory_projection": _memory_projection(thread, args.thread_id),
        }
    )


def cmd_resume(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    layout = ensure_layout(repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")
    prior_subgraph = str(thread.get("active_subgraph", ""))
    existing_command_state = thread.get("command_state")
    if not isinstance(existing_command_state, dict):
        existing_command_state = {}
    command_update = _load_json_option(args.command_update_json, args.command_update_file)
    resume_payload = _load_json_option(args.resume_payload_json, args.resume_payload_file)
    resume_map = _load_json_option(args.resume_map_json, args.resume_map_file)
    if resume_map is not None and not isinstance(resume_map, dict):
        raise SystemExit("resume-map must be a JSON object keyed by interrupt_id")
    runtime_context = _load_json_option(args.runtime_context_json, args.runtime_context_file)
    _seed_loop_state(thread, args.loop_kind or thread.get("active_loop", ""), args.iteration_budget)
    thread["status"] = "resumed"
    thread["phase"] = args.phase or thread.get("phase", "read-context")
    thread["updated_at"] = _now()
    thread.pop("recovery_state", None)
    _ensure_scoped_activation_state(thread)
    _ensure_graph_contract(thread)
    _ensure_subgraph_state(thread)
    _ensure_stream_state(thread)
    _ensure_runtime_injection_state(thread)
    _ensure_memory_state(thread)
    _ensure_approval_queue_state(thread)
    _persist_migration_state(thread)
    _persist_runtime_state_layers(thread)
    _apply_runtime_injection_state(
        thread,
        context_schema=args.context_schema,
        runtime_context=runtime_context,
        store_configured=(True if args.store_configured else None),
        store_access_expected=(True if args.store_access_expected else None),
        store_kind=args.store_kind,
    )
    _apply_memory_state(
        thread,
        memory_store_configured=(True if args.memory_store_configured else None),
        memory_store_kind=args.memory_store_kind,
        memory_namespaces=args.memory_namespace if args.memory_namespace else None,
        semantic_memory_enabled=(True if args.semantic_memory_enabled else None),
        semantic_store_kind=args.semantic_store_kind,
        semantic_namespaces=args.semantic_namespace if args.semantic_namespace else None,
    )
    thread["command_state"] = _build_command_state(
        thread,
        existing_state=existing_command_state,
        transition_kind=args.command_kind,
        goto_target=args.command_goto,
        graph_scope=args.command_graph_scope,
        parent_handoff_target=args.parent_handoff_target,
        update_payload=command_update,
        resume_payload=resume_payload,
        await_command_resume=args.await_command_resume,
        source_subgraph=prior_subgraph,
    )
    if resume_map is None and resume_payload is not None:
        resume_map = _approval_resume_map_from_payload(thread, resume_payload)
    if resume_map:
        _apply_approval_resume_map(thread, resume_map)
    interrupt = read_interrupt(repo_root, args.thread_id)
    if args.gate_verdict:
        interrupt = _apply_gate_verdict(thread, args.gate_verdict, args.gate_reason)
    elif resume_map:
        interrupt = _interrupt_payload_from_queue(thread)
        if interrupt:
            thread["status"] = "waiting_for_approval"
            thread["stop_reason"] = "needs_human"
        elif thread.get("stop_reason") == "needs_human":
            thread["stop_reason"] = ""
    elif interrupt:
        interrupt["status"] = "resumed"
        interrupt["updated_at"] = _now()
        if _approval_queue_projection(thread)["pending_count"] > 0:
            thread["approval_queue_state"] = _default_approval_queue_state()
            if thread.get("stop_reason") == "needs_human":
                thread["stop_reason"] = ""
            interrupt = {}
    _persist_runtime_state_layers(thread)
    checkpoint_payload = {
        "thread_id": args.thread_id,
        "checkpoint_id": _checkpoint_id(args.thread_id),
        "phase": thread["phase"],
        "checkpoint_kind": f"gate:{args.gate_verdict}" if args.gate_verdict else "resume",
        "loop_projection": _loop_projection(thread),
        "reducer_projection": _reducer_projection(thread),
        "graph_kernel_projection": _graph_kernel_projection(thread, args.thread_id),
        "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, args.thread_id),
        "compiled_invocation_projection": _compiled_invocation_projection(thread, args.thread_id),
        "live_execution_projection": _live_execution_projection(thread, args.thread_id),
        "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(thread, args.thread_id),
        "generalized_live_routing_projection": _generalized_live_routing_projection(thread, args.thread_id),
        "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(thread, args.thread_id),
        "approval_queue_projection": _approval_queue_projection(thread, args.thread_id),
        "migration_projection": _migration_projection(thread, args.thread_id),
        "subgraph_projection": _subgraph_projection(thread, args.thread_id),
        "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread, args.thread_id),
        "command_projection": _command_projection(thread, args.thread_id),
        "stream_projection": _stream_projection(thread, args.thread_id),
        "runtime_injection_projection": _runtime_injection_projection(thread, args.thread_id),
        "memory_projection": _memory_projection(thread, args.thread_id),
        "updated_at": _now(),
    }
    write_thread_record(repo_root, thread)
    if interrupt:
        write_interrupt(repo_root, interrupt)
    else:
        delete_interrupt(repo_root, args.thread_id)
    write_checkpoint(repo_root, checkpoint_payload)
    _append_history_record(repo_root, thread, checkpoint_payload, interrupt, "resume")
    _save_backend_projection(repo_root, layout, thread)
    _emit(
        {
            "operation": "resume",
            "thread": thread,
            "interrupt": interrupt,
            "checkpoint": checkpoint_payload,
            "loop_projection": _loop_projection(thread),
            "history_projection": _history_projection(repo_root, args.thread_id, thread, checkpoint_payload, interrupt),
            "recovery_projection": _recovery_projection(thread),
            "helper_pointers": _helper_pointers(args.thread_id),
            "reducer_projection": _reducer_projection(thread),
            "graph_kernel_projection": _graph_kernel_projection(thread, args.thread_id),
            "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, args.thread_id),
            "compiled_invocation_projection": _compiled_invocation_projection(thread, args.thread_id),
            "live_execution_projection": _live_execution_projection(thread, args.thread_id),
            "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(thread, args.thread_id),
            "generalized_live_routing_projection": _generalized_live_routing_projection(thread, args.thread_id),
            "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(thread, args.thread_id),
            "approval_queue_projection": _approval_queue_projection(thread, args.thread_id),
            "migration_projection": _migration_projection(thread, args.thread_id),
            "subgraph_projection": _subgraph_projection(thread, args.thread_id),
            "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread, args.thread_id),
            "command_projection": _command_projection(thread, args.thread_id),
            "stream_projection": _stream_projection(thread, args.thread_id),
            "runtime_injection_projection": _runtime_injection_projection(thread, args.thread_id),
            "memory_projection": _memory_projection(thread, args.thread_id),
        }
    )


def _load_branch_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.payload_file:
        raw_text = args.payload_file.read()
        return json.loads(raw_text.lstrip("\ufeff"))
    return json.loads(args.payload_json)


def cmd_merge_branch(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    layout = ensure_layout(repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    payload = _load_branch_payload(args)
    _merge_branch_payload(thread, payload)
    thread["updated_at"] = _now()
    _ensure_graph_contract(thread)
    _ensure_approval_queue_state(thread)
    _persist_migration_state(thread)
    _ensure_subgraph_state(thread)
    _persist_runtime_state_layers(thread)
    checkpoint_payload = {
        "thread_id": args.thread_id,
        "checkpoint_id": _checkpoint_id(args.thread_id),
        "phase": thread.get("phase", ""),
        "checkpoint_kind": "fanin_merge",
        "loop_projection": _loop_projection(thread),
        "reducer_projection": _reducer_projection(thread),
        "graph_kernel_projection": _graph_kernel_projection(thread, args.thread_id),
        "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, args.thread_id),
        "compiled_invocation_projection": _compiled_invocation_projection(thread, args.thread_id),
        "live_execution_projection": _live_execution_projection(thread, args.thread_id),
        "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(thread, args.thread_id),
        "generalized_live_routing_projection": _generalized_live_routing_projection(thread, args.thread_id),
        "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(thread, args.thread_id),
        "approval_queue_projection": _approval_queue_projection(thread, args.thread_id),
        "migration_projection": _migration_projection(thread, args.thread_id),
        "subgraph_projection": _subgraph_projection(thread, args.thread_id),
        "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread, args.thread_id),
        "updated_at": _now(),
    }
    interrupt = read_interrupt(repo_root, args.thread_id)
    write_thread_record(repo_root, thread)
    write_checkpoint(repo_root, checkpoint_payload)
    _append_history_record(repo_root, thread, checkpoint_payload, interrupt, "merge-branch")
    _save_backend_projection(repo_root, layout, thread)
    _emit(
        {
            "operation": "merge-branch",
            "thread": thread,
            "checkpoint": checkpoint_payload,
            "history_projection": _history_projection(repo_root, args.thread_id, thread, checkpoint_payload, interrupt),
            "recovery_projection": _recovery_projection(thread),
            "helper_pointers": _helper_pointers(args.thread_id),
            "reducer_projection": _reducer_projection(thread),
            "graph_kernel_projection": _graph_kernel_projection(thread, args.thread_id),
            "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, args.thread_id),
            "compiled_invocation_projection": _compiled_invocation_projection(thread, args.thread_id),
            "live_execution_projection": _live_execution_projection(thread, args.thread_id),
            "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(thread, args.thread_id),
            "generalized_live_routing_projection": _generalized_live_routing_projection(thread, args.thread_id),
            "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(thread, args.thread_id),
            "approval_queue_projection": _approval_queue_projection(thread, args.thread_id),
            "migration_projection": _migration_projection(thread, args.thread_id),
            "subgraph_projection": _subgraph_projection(thread, args.thread_id),
            "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread, args.thread_id),
            "command_projection": _command_projection(thread, args.thread_id),
            "stream_projection": _stream_projection(thread, args.thread_id),
            "runtime_injection_projection": _runtime_injection_projection(thread, args.thread_id),
            "memory_projection": _memory_projection(thread, args.thread_id),
        }
    )


def cmd_history(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    checkpoint = read_checkpoint(repo_root, args.thread_id)
    interrupt = read_interrupt(repo_root, args.thread_id)
    _emit(
        {
            "operation": "history",
            "thread_id": args.thread_id,
            "thread_exists": bool(thread),
            "history_projection": _history_projection(repo_root, args.thread_id, thread, checkpoint, interrupt),
            "recovery_projection": _recovery_projection(thread),
            "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, args.thread_id),
            "compiled_invocation_projection": _compiled_invocation_projection(thread, args.thread_id),
            "live_execution_projection": _live_execution_projection(thread, args.thread_id),
            "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(thread, args.thread_id),
            "deeper_live_primary_engine_projection": _deeper_live_primary_engine_projection(thread, args.thread_id),
            "generalized_live_routing_projection": _generalized_live_routing_projection(thread, args.thread_id),
            "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(thread, args.thread_id),
            "graph_kernel_projection": _graph_kernel_projection(thread, args.thread_id),
            "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread, args.thread_id),
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_replay(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    checkpoint = read_checkpoint(repo_root, args.thread_id)
    interrupt = read_interrupt(repo_root, args.thread_id)
    target = _resolve_replay_target(repo_root, args.thread_id, args.target_id, thread, checkpoint, interrupt)
    _emit(
        {
            "operation": "replay",
            "thread_id": args.thread_id,
            "target_id": args.target_id,
            "target_kind": target["target_kind"],
            "read_only": True,
            "source_records": target["record"].get("source_records", []),
            "fidelity": target["record"].get("fidelity", "full"),
            "thread_snapshot": target["thread_snapshot"],
            "checkpoint_snapshot": target["checkpoint_snapshot"],
            "interrupt_snapshot": target["interrupt_snapshot"],
            "history_projection": _history_projection(repo_root, args.thread_id, thread, checkpoint, interrupt),
            "recovery_projection": _recovery_projection(thread),
            "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, args.thread_id),
            "compiled_invocation_projection": _compiled_invocation_projection(thread, args.thread_id),
            "live_execution_projection": _live_execution_projection(thread, args.thread_id),
            "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(thread, args.thread_id),
            "deeper_live_primary_engine_projection": _deeper_live_primary_engine_projection(thread, args.thread_id),
            "generalized_live_routing_projection": _generalized_live_routing_projection(thread, args.thread_id),
            "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(thread, args.thread_id),
            "graph_kernel_projection": _graph_kernel_projection(thread, args.thread_id),
            "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread, args.thread_id),
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_recover(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    layout = ensure_layout(repo_root)
    if args.mutation_intent != "explicit-recovery":
        raise SystemExit(f"Unsupported mutation intent: {args.mutation_intent}")

    has_target = bool(args.target_id)
    has_updates = bool(args.thread_field or args.interrupt_field or args.clear_interrupt)
    if has_target and has_updates:
        raise SystemExit("Time-travel recovery and update-state recovery must not be combined in one command")
    if not has_target and not has_updates:
        raise SystemExit("Recovery requires either --target-id or update-state arguments")

    current_thread = read_thread_record(repo_root, args.thread_id)
    current_checkpoint = read_checkpoint(repo_root, args.thread_id)
    current_interrupt = read_interrupt(repo_root, args.thread_id)
    if not current_thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    thread = _clone_payload(current_thread)
    interrupt = _clone_payload(current_interrupt) if current_interrupt else {}
    touched_fields: list[str] = []
    action = "update-state"
    source_records = [str(thread_record_path(repo_root, args.thread_id))]

    if has_target:
        action = "time-travel"
        target = _resolve_replay_target(
            repo_root,
            args.thread_id,
            args.target_id,
            current_thread,
            current_checkpoint,
            current_interrupt,
        )
        thread = target["thread_snapshot"] or _clone_payload(current_thread)
        interrupt = target["interrupt_snapshot"] or {}
        thread["thread_id"] = args.thread_id
        thread["repo_root"] = str(repo_root)
        thread["updated_at"] = _now()
        source_records = target["record"].get("source_records", [])
    else:
        for raw_assignment in args.thread_field:
            field_name, parsed_value = _parse_assignment(raw_assignment)
            thread[field_name] = _coerce_thread_field(field_name, parsed_value)
            touched_fields.append(f"thread:{field_name}")
        if args.interrupt_field:
            if not interrupt:
                interrupt = {
                    "thread_id": args.thread_id,
                    "updated_at": _now(),
                }
            for raw_assignment in args.interrupt_field:
                field_name, parsed_value = _parse_assignment(raw_assignment)
                interrupt[field_name] = _coerce_interrupt_field(field_name, parsed_value)
                touched_fields.append(f"interrupt:{field_name}")
        if args.clear_interrupt:
            interrupt = {}
            thread["approval_queue_state"] = _default_approval_queue_state()
            touched_fields.append("interrupt:clear")
        thread["updated_at"] = _now()

    thread["recovery_state"] = {
        "posture": "recovered_pending_resume",
        "last_action": action,
        "target_id": args.target_id or "",
        "recovered_at": thread["updated_at"],
        "source_records": source_records,
        "recoverable_fields_touched": touched_fields,
    }
    _ensure_graph_contract(thread)
    _ensure_approval_queue_state(thread)
    _persist_migration_state(thread)
    _ensure_subgraph_state(thread)
    _persist_runtime_state_layers(thread)

    checkpoint_payload = {
        "thread_id": args.thread_id,
        "checkpoint_id": _checkpoint_id(args.thread_id),
        "phase": thread.get("phase", ""),
        "checkpoint_kind": f"recovery:{action}",
        "loop_projection": _loop_projection(thread),
        "reducer_projection": _reducer_projection(thread),
        "graph_kernel_projection": _graph_kernel_projection(thread, args.thread_id),
        "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, args.thread_id),
        "compiled_invocation_projection": _compiled_invocation_projection(thread, args.thread_id),
        "live_execution_projection": _live_execution_projection(thread, args.thread_id),
        "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(thread, args.thread_id),
        "approval_queue_projection": _approval_queue_projection(thread, args.thread_id),
        "migration_projection": _migration_projection(thread, args.thread_id),
        "subgraph_projection": _subgraph_projection(thread, args.thread_id),
        "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread, args.thread_id),
        "command_projection": _command_projection(thread, args.thread_id),
        "recovery_target_id": args.target_id or "",
        "updated_at": _now(),
    }

    write_thread_record(repo_root, thread)
    if interrupt:
        interrupt.setdefault("thread_id", args.thread_id)
        interrupt["updated_at"] = _now()
        write_interrupt(repo_root, interrupt)
    else:
        delete_interrupt(repo_root, args.thread_id)
    write_checkpoint(repo_root, checkpoint_payload)
    _append_history_record(repo_root, thread, checkpoint_payload, interrupt, f"recover:{action}")
    _save_backend_projection(repo_root, layout, thread)
    _emit(
        {
            "operation": "recover",
            "action": action,
            "mutation_intent": args.mutation_intent,
            "thread": thread,
            "interrupt": interrupt,
            "checkpoint": checkpoint_payload,
            "loop_projection": _loop_projection(thread),
            "history_projection": _history_projection(repo_root, args.thread_id, thread, checkpoint_payload, interrupt),
            "recovery_projection": _recovery_projection(thread),
            "helper_pointers": _helper_pointers(args.thread_id),
            "reducer_projection": _reducer_projection(thread),
            "graph_kernel_projection": _graph_kernel_projection(thread, args.thread_id),
            "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, args.thread_id),
            "compiled_invocation_projection": _compiled_invocation_projection(thread, args.thread_id),
            "live_execution_projection": _live_execution_projection(thread, args.thread_id),
            "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(thread, args.thread_id),
            "approval_queue_projection": _approval_queue_projection(thread, args.thread_id),
            "migration_projection": _migration_projection(thread, args.thread_id),
            "subgraph_projection": _subgraph_projection(thread, args.thread_id),
            "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread, args.thread_id),
            "command_projection": _command_projection(thread, args.thread_id),
            "stream_projection": _stream_projection(thread, args.thread_id),
            "runtime_injection_projection": _runtime_injection_projection(thread, args.thread_id),
            "memory_projection": _memory_projection(thread, args.thread_id),
        }
    )


def cmd_stream(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    layout = ensure_layout(repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    _ensure_graph_contract(thread)
    _ensure_approval_queue_state(thread)
    _persist_migration_state(thread)
    selected_modes = args.stream_mode if args.stream_mode else None
    latest_event_kind = args.event_kind or (selected_modes[-1] if selected_modes else "")
    _apply_stream_state(
        thread,
        selected_modes=selected_modes,
        subgraphs=args.subgraphs if args.stream_mode or args.subgraphs else None,
        latest_event_kind=latest_event_kind,
        latest_namespace=args.namespace or None,
        latest_checkpoint_kind=args.checkpoint_kind,
        latest_task_path=args.task_path,
        latest_task_status=args.task_status,
        latest_debug_summary=args.debug_summary,
    )
    thread["updated_at"] = _now()
    _persist_runtime_state_layers(thread)
    write_thread_record(repo_root, thread)
    _save_backend_projection(repo_root, layout, thread)
    _emit(
        {
            "operation": "stream",
            "thread": thread,
            "graph_kernel_projection": _graph_kernel_projection(thread, args.thread_id),
            "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, args.thread_id),
            "compiled_invocation_projection": _compiled_invocation_projection(thread, args.thread_id),
            "live_execution_projection": _live_execution_projection(thread, args.thread_id),
            "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(thread, args.thread_id),
            "generalized_live_routing_projection": _generalized_live_routing_projection(thread, args.thread_id),
            "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(thread, args.thread_id),
            "approval_queue_projection": _approval_queue_projection(thread, args.thread_id),
            "migration_projection": _migration_projection(thread, args.thread_id),
            "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread, args.thread_id),
            "stream_projection": _stream_projection(thread, args.thread_id),
            "runtime_injection_projection": _runtime_injection_projection(thread, args.thread_id),
            "memory_projection": _memory_projection(thread, args.thread_id),
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_runtime(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    layout = ensure_layout(repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    runtime_context = _load_json_option(args.runtime_context_json, args.runtime_context_file)
    _ensure_graph_contract(thread)
    _ensure_runtime_injection_state(thread)
    _ensure_approval_queue_state(thread)
    _persist_migration_state(thread)
    _apply_runtime_injection_state(
        thread,
        context_schema=args.context_schema,
        runtime_context=runtime_context,
        store_configured=(True if args.store_configured else None),
        store_access_expected=(True if args.store_access_expected else None),
        store_kind=args.store_kind,
    )
    thread["updated_at"] = _now()
    _persist_runtime_state_layers(thread)
    write_thread_record(repo_root, thread)
    _save_backend_projection(repo_root, layout, thread)
    _emit(
        {
            "operation": "runtime",
            "thread": thread,
            "graph_kernel_projection": _graph_kernel_projection(thread, args.thread_id),
            "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, args.thread_id),
            "compiled_invocation_projection": _compiled_invocation_projection(thread, args.thread_id),
            "live_execution_projection": _live_execution_projection(thread, args.thread_id),
            "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(thread, args.thread_id),
            "generalized_live_routing_projection": _generalized_live_routing_projection(thread, args.thread_id),
            "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(thread, args.thread_id),
            "approval_queue_projection": _approval_queue_projection(thread, args.thread_id),
            "migration_projection": _migration_projection(thread, args.thread_id),
            "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread, args.thread_id),
            "runtime_injection_projection": _runtime_injection_projection(thread, args.thread_id),
            "memory_projection": _memory_projection(thread, args.thread_id),
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_memory(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    layout = ensure_layout(repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    _ensure_graph_contract(thread)
    _ensure_memory_state(thread)
    _ensure_approval_queue_state(thread)
    _persist_migration_state(thread)
    _apply_memory_state(
        thread,
        memory_store_configured=(True if args.memory_store_configured else None),
        memory_store_kind=args.memory_store_kind,
        memory_namespaces=args.memory_namespace if args.memory_namespace else None,
        semantic_memory_enabled=(True if args.semantic_memory_enabled else None),
        semantic_store_kind=args.semantic_store_kind,
        semantic_namespaces=args.semantic_namespace if args.semantic_namespace else None,
    )
    thread["updated_at"] = _now()
    _persist_runtime_state_layers(thread)
    write_thread_record(repo_root, thread)
    _save_backend_projection(repo_root, layout, thread)
    _emit(
        {
            "operation": "memory",
            "thread": thread,
            "graph_kernel_projection": _graph_kernel_projection(thread, args.thread_id),
            "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, args.thread_id),
            "compiled_invocation_projection": _compiled_invocation_projection(thread, args.thread_id),
            "live_execution_projection": _live_execution_projection(thread, args.thread_id),
            "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(thread, args.thread_id),
            "generalized_live_routing_projection": _generalized_live_routing_projection(thread, args.thread_id),
            "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(thread, args.thread_id),
            "approval_queue_projection": _approval_queue_projection(thread, args.thread_id),
            "migration_projection": _migration_projection(thread, args.thread_id),
            "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread, args.thread_id),
            "memory_projection": _memory_projection(thread, args.thread_id),
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_migration(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    _ensure_graph_contract(thread)
    current_contract = _current_graph_contract(
        graph_contract_id=args.current_graph_contract_id,
        topology_version=args.current_topology_version,
        state_schema_version=args.current_state_schema_version,
    )
    _emit(
        {
            "operation": "migration",
            "thread": thread,
            "graph_kernel_projection": _graph_kernel_projection(thread, args.thread_id),
            "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, args.thread_id),
            "compiled_invocation_projection": _compiled_invocation_projection(thread, args.thread_id),
            "live_execution_projection": _live_execution_projection(thread, args.thread_id),
            "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(thread, args.thread_id),
            "generalized_live_routing_projection": _generalized_live_routing_projection(thread, args.thread_id),
            "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(thread, args.thread_id),
            "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread, args.thread_id),
            "migration_projection": _migration_projection(
                thread,
                args.thread_id,
                current_contract=current_contract,
            ),
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_approval_queue(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    layout = ensure_layout(repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    interrupt_items = _load_interrupt_items(args.interrupt_item_json, args.interrupt_item_file)
    resume_map = _load_json_option(args.resume_map_json, args.resume_map_file)
    if resume_map is not None and not isinstance(resume_map, dict):
        raise SystemExit("resume-map must be a JSON object keyed by interrupt_id")

    _ensure_graph_contract(thread)
    _ensure_approval_queue_state(thread)
    if args.clear_queue:
        thread["approval_queue_state"] = _default_approval_queue_state()
    elif interrupt_items:
        _set_approval_queue_state(
            thread,
            interrupt_items,
            default_interrupt_point=args.default_interrupt_point,
            default_reason=args.default_reason,
        )
    if resume_map:
        _apply_approval_resume_map(thread, resume_map)

    approval_queue_projection = _approval_queue_projection(thread, args.thread_id)
    interrupt = _interrupt_payload_from_queue(thread)
    if approval_queue_projection["pending_count"] > 0:
        thread["status"] = "waiting_for_approval"
        if not thread.get("stop_reason"):
            thread["stop_reason"] = "needs_human"
    elif thread.get("stop_reason") == "needs_human":
        thread["stop_reason"] = ""
        if thread.get("status") == "waiting_for_approval":
            thread["status"] = "resumed"
    thread["updated_at"] = _now()
    _persist_migration_state(thread)
    _persist_runtime_state_layers(thread)

    write_thread_record(repo_root, thread)
    if interrupt:
        write_interrupt(repo_root, interrupt)
    else:
        delete_interrupt(repo_root, args.thread_id)
    _save_backend_projection(repo_root, layout, thread)
    _emit(
        {
            "operation": "approval-queue",
            "thread": thread,
            "interrupt": interrupt,
            "graph_kernel_projection": _graph_kernel_projection(thread, args.thread_id),
            "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, args.thread_id),
            "compiled_invocation_projection": _compiled_invocation_projection(thread, args.thread_id),
            "live_execution_projection": _live_execution_projection(thread, args.thread_id),
            "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(thread, args.thread_id),
            "generalized_live_routing_projection": _generalized_live_routing_projection(thread, args.thread_id),
            "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(thread, args.thread_id),
            "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread, args.thread_id),
            "approval_queue_projection": approval_queue_projection,
            "migration_projection": _migration_projection(thread, args.thread_id),
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_kernel(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    _emit(
        {
            "operation": "kernel",
            "thread": thread,
            "graph_kernel_identity": GRAPH_KERNEL_IDENTITY,
            "graph_kernel_identity_fields": GRAPH_KERNEL_IDENTITY_FIELDS,
            "graph_kernel_node_postures": GRAPH_KERNEL_NODE_POSTURES,
            "graph_kernel_transition_kinds": GRAPH_KERNEL_TRANSITION_KINDS,
            "graph_kernel_node_fields": GRAPH_KERNEL_NODE_FIELDS,
            "graph_kernel_edge_fields": GRAPH_KERNEL_EDGE_FIELDS,
            "graph_kernel_projection_fields": GRAPH_KERNEL_PROJECTION_FIELDS,
            "graph_kernel_phase_to_node": GRAPH_KERNEL_PHASE_TO_NODE,
            "graph_kernel_nodes": GRAPH_KERNEL_NODES,
            "graph_kernel_edges": GRAPH_KERNEL_EDGES,
            "graph_kernel_projection": _graph_kernel_projection(thread, args.thread_id),
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_engine(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    _emit(
        {
            "operation": "engine",
            "thread": thread,
            "primary_runtime_engine_identity": PRIMARY_RUNTIME_ENGINE_IDENTITY,
            "primary_runtime_engine_identity_fields": PRIMARY_RUNTIME_ENGINE_IDENTITY_FIELDS,
            "primary_runtime_engine_postures": PRIMARY_RUNTIME_ENGINE_POSTURES,
            "primary_runtime_engine_projection_fields": PRIMARY_RUNTIME_ENGINE_PROJECTION_FIELDS,
            "primary_runtime_engine_projection": _primary_runtime_engine_projection(thread, args.thread_id),
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_invocation(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    if args.invoke_kind:
        thread["last_compiled_invoke_kind"] = args.invoke_kind
        thread["last_compiled_invoke_reason"] = f"requested:{args.invoke_kind}"
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    _emit(
        {
            "operation": "invocation",
            "thread": thread,
            "compiled_invocation_identity": COMPILED_INVOCATION_IDENTITY,
            "compiled_invocation_identity_fields": COMPILED_INVOCATION_IDENTITY_FIELDS,
            "compiled_invocation_postures": COMPILED_INVOCATION_POSTURES,
            "compiled_invocation_run_kinds": COMPILED_INVOCATION_RUN_KINDS,
            "compiled_invocation_projection_fields": COMPILED_INVOCATION_PROJECTION_FIELDS,
            "compiled_invocation_projection": _compiled_invocation_projection(thread, args.thread_id),
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_live_execution(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    if args.run_kind:
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread, live_run_kind=args.run_kind)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    _emit(
        {
            "operation": "live-execution",
            "thread": thread,
            "live_execution_identity": LIVE_EXECUTION_IDENTITY,
            "live_execution_identity_fields": LIVE_EXECUTION_IDENTITY_FIELDS,
            "live_execution_postures": LIVE_EXECUTION_POSTURES,
            "live_execution_run_kinds": LIVE_EXECUTION_RUN_KINDS,
            "live_execution_projection_fields": LIVE_EXECUTION_PROJECTION_FIELDS,
            "live_execution_projection": _live_execution_projection(thread, args.thread_id),
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_fuller_engine(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    if args.run_kind:
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread, live_run_kind=args.run_kind)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    _emit(
        {
            "operation": "fuller-engine",
            "thread": thread,
            "fuller_live_primary_engine_identity": FULLER_LIVE_PRIMARY_ENGINE_IDENTITY,
            "fuller_live_primary_engine_identity_fields": FULLER_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "fuller_live_primary_engine_postures": FULLER_LIVE_PRIMARY_ENGINE_POSTURES,
            "fuller_live_primary_engine_run_kinds": FULLER_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "fuller_live_primary_engine_transition_kinds": FULLER_LIVE_PRIMARY_ENGINE_TRANSITION_KINDS,
            "fuller_live_primary_engine_projection_fields": FULLER_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "fuller_live_primary_engine_projection": _fuller_live_primary_engine_projection(thread, args.thread_id),
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_deeper_engine(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    recursion_limit = int(args.recursion_limit or 8)
    run_kind = args.run_kind or str(thread.get("last_deeper_live_primary_engine_kind", "")) or "invoke"
    if args.run_kind:
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread, live_run_kind=args.run_kind)
        _persist_deeper_live_primary_engine_state(thread, args.run_kind, recursion_limit)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    projection = _deeper_live_primary_engine_projection(thread, args.thread_id)
    if args.run_kind or recursion_limit != int(thread.get("last_deeper_live_primary_engine_recursion_limit", 8) or 8):
        preview = _execute_deeper_live_primary_engine(thread, run_kind, recursion_limit)
        projection = {
            "engine_identity": _deeper_live_primary_engine_identity(),
            "compile_supported": preview["compile_supported"],
            "compiled_graph_present": preview["compiled_graph_present"],
            "invoke_supported": preview["invoke_supported"],
            "stream_supported": preview["stream_supported"],
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "projected_node_path": preview["projected_node_path"],
            "projected_phase_path": preview["projected_phase_path"],
            "planned_supersteps": preview["planned_supersteps"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": preview["recursion_limit"],
            "execution_posture": preview["execution_posture"],
            "last_run_kind": preview["last_run_kind"],
            "last_run_status": preview["last_run_status"],
            "last_run_reason": preview["last_run_reason"],
            "helper_pointer": projection["helper_pointer"],
        }

    _emit(
        {
            "operation": "deeper-engine",
            "thread": thread,
            "deeper_live_primary_engine_identity": DEEPER_LIVE_PRIMARY_ENGINE_IDENTITY,
            "deeper_live_primary_engine_identity_fields": DEEPER_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "deeper_live_primary_engine_postures": DEEPER_LIVE_PRIMARY_ENGINE_POSTURES,
            "deeper_live_primary_engine_run_kinds": DEEPER_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "deeper_live_primary_engine_stop_boundaries": DEEPER_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
            "deeper_live_primary_engine_projection_fields": DEEPER_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "deeper_live_primary_engine_projection": projection,
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_superstep_engine(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    recursion_limit = int(args.recursion_limit or 8)
    run_kind = args.run_kind or str(thread.get("last_superstep_live_primary_engine_kind", "")) or "invoke"
    if args.run_kind:
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread, live_run_kind=args.run_kind)
        _persist_superstep_live_primary_engine_state(thread, args.run_kind, recursion_limit)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    projection = _superstep_live_primary_engine_projection(thread, args.thread_id)
    if args.run_kind or recursion_limit != int(thread.get("last_superstep_live_primary_engine_recursion_limit", 8) or 8):
        preview = _execute_superstep_live_primary_engine(thread, run_kind, recursion_limit)
        projection = {
            "engine_identity": _superstep_live_primary_engine_identity(),
            "compile_supported": preview["compile_supported"],
            "compiled_graph_present": preview["compiled_graph_present"],
            "invoke_supported": preview["invoke_supported"],
            "stream_supported": preview["stream_supported"],
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "node_visit_path": preview["node_visit_path"],
            "phase_visit_path": preview["phase_visit_path"],
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": preview["recursion_limit"],
            "execution_posture": preview["execution_posture"],
            "last_run_kind": preview["last_run_kind"],
            "last_run_status": preview["last_run_status"],
            "last_run_reason": preview["last_run_reason"],
            "helper_pointer": projection["helper_pointer"],
        }

    _emit(
        {
            "operation": "superstep-engine",
            "thread": thread,
            "superstep_live_primary_engine_identity": SUPERSTEP_LIVE_PRIMARY_ENGINE_IDENTITY,
            "superstep_live_primary_engine_identity_fields": SUPERSTEP_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "superstep_live_primary_engine_postures": SUPERSTEP_LIVE_PRIMARY_ENGINE_POSTURES,
            "superstep_live_primary_engine_run_kinds": SUPERSTEP_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "superstep_live_primary_engine_stop_boundaries": SUPERSTEP_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
            "superstep_live_primary_engine_projection_fields": SUPERSTEP_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "superstep_live_primary_engine_projection": projection,
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_stateful_engine(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    recursion_limit = int(args.recursion_limit or 8)
    run_kind = args.run_kind or str(thread.get("last_stateful_live_primary_engine_kind", "")) or "invoke"
    if args.run_kind:
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread, live_run_kind=args.run_kind)
        _persist_stateful_live_primary_engine_state(thread, args.run_kind, recursion_limit)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    projection = _stateful_live_primary_engine_projection(thread, args.thread_id)
    if args.run_kind or recursion_limit != int(thread.get("last_stateful_live_primary_engine_recursion_limit", 8) or 8):
        preview = _execute_stateful_live_primary_engine(thread, run_kind, recursion_limit)
        projection = {
            "engine_identity": _stateful_live_primary_engine_identity(),
            "compile_supported": preview["compile_supported"],
            "compiled_graph_present": preview["compiled_graph_present"],
            "invoke_supported": preview["invoke_supported"],
            "stream_supported": preview["stream_supported"],
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "stateful_node_path": preview["stateful_node_path"],
            "stateful_phase_path": preview["stateful_phase_path"],
            "stateful_transition_log": preview["stateful_transition_log"],
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": preview["recursion_limit"],
            "execution_posture": preview["execution_posture"],
            "last_run_kind": preview["last_run_kind"],
            "last_run_status": preview["last_run_status"],
            "last_run_reason": preview["last_run_reason"],
            "helper_pointer": projection["helper_pointer"],
        }

    _emit(
        {
            "operation": "stateful-engine",
            "thread": thread,
            "stateful_live_primary_engine_identity": STATEFUL_LIVE_PRIMARY_ENGINE_IDENTITY,
            "stateful_live_primary_engine_identity_fields": STATEFUL_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "stateful_live_primary_engine_postures": STATEFUL_LIVE_PRIMARY_ENGINE_POSTURES,
            "stateful_live_primary_engine_run_kinds": STATEFUL_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "stateful_live_primary_engine_stop_boundaries": STATEFUL_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
            "stateful_live_primary_engine_projection_fields": STATEFUL_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "stateful_live_primary_engine_projection": projection,
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_boundary_engine(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    recursion_limit = int(args.recursion_limit or 8)
    run_kind = args.run_kind or str(thread.get("last_boundary_state_live_primary_engine_kind", "")) or "invoke"
    if args.run_kind:
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread, live_run_kind=args.run_kind)
        _persist_boundary_state_live_primary_engine_state(thread, args.run_kind, recursion_limit)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    projection = _boundary_state_live_primary_engine_projection(thread, args.thread_id)
    if args.run_kind or recursion_limit != int(thread.get("last_boundary_state_live_primary_engine_recursion_limit", 8) or 8):
        preview = _execute_boundary_state_live_primary_engine(thread, run_kind, recursion_limit)
        projection = {
            "engine_identity": _boundary_state_live_primary_engine_identity(),
            "compile_supported": preview["compile_supported"],
            "compiled_graph_present": preview["compiled_graph_present"],
            "invoke_supported": preview["invoke_supported"],
            "stream_supported": preview["stream_supported"],
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "boundary_node_path": preview["boundary_node_path"],
            "boundary_phase_path": preview["boundary_phase_path"],
            "boundary_transition_log": preview["boundary_transition_log"],
            "boundary_state_kind": preview["boundary_state_kind"],
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": preview["recursion_limit"],
            "execution_posture": preview["execution_posture"],
            "last_run_kind": preview["last_run_kind"],
            "last_run_status": preview["last_run_status"],
            "last_run_reason": preview["last_run_reason"],
            "helper_pointer": projection["helper_pointer"],
        }

    _emit(
        {
            "operation": "boundary-engine",
            "thread": thread,
            "boundary_state_live_primary_engine_identity": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "boundary_state_live_primary_engine_identity_fields": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "boundary_state_live_primary_engine_postures": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_POSTURES,
            "boundary_state_live_primary_engine_run_kinds": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "boundary_state_live_primary_engine_stop_boundaries": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
            "boundary_state_live_primary_engine_projection_fields": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "boundary_state_live_primary_engine_projection": projection,
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_handoff_engine(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    recursion_limit = int(args.recursion_limit or 8)
    run_kind = args.run_kind or str(thread.get("last_handoff_state_live_primary_engine_kind", "")) or "invoke"
    if args.run_kind:
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread, live_run_kind=args.run_kind)
        _persist_handoff_state_live_primary_engine_state(thread, args.run_kind, recursion_limit)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    projection = _handoff_state_live_primary_engine_projection(thread, args.thread_id)
    if args.run_kind or recursion_limit != int(thread.get("last_handoff_state_live_primary_engine_recursion_limit", 8) or 8):
        preview = _execute_handoff_state_live_primary_engine(thread, run_kind, recursion_limit)
        projection = {
            "engine_identity": _handoff_state_live_primary_engine_identity(),
            "compile_supported": preview["compile_supported"],
            "compiled_graph_present": preview["compiled_graph_present"],
            "invoke_supported": preview["invoke_supported"],
            "stream_supported": preview["stream_supported"],
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "handoff_node_path": preview["handoff_node_path"],
            "handoff_phase_path": preview["handoff_phase_path"],
            "handoff_subgraph_path": preview["handoff_subgraph_path"],
            "handoff_transition_log": preview["handoff_transition_log"],
            "handoff_state_kind": preview["handoff_state_kind"],
            "active_subgraph": preview["active_subgraph"],
            "source_subgraph": preview["source_subgraph"],
            "target_subgraph": preview["target_subgraph"],
            "parent_handoff_target": preview["parent_handoff_target"],
            "graph_scope": preview["graph_scope"],
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": preview["recursion_limit"],
            "execution_posture": preview["execution_posture"],
            "last_run_kind": preview["last_run_kind"],
            "last_run_status": preview["last_run_status"],
            "last_run_reason": preview["last_run_reason"],
            "helper_pointer": projection["helper_pointer"],
        }

    _emit(
        {
            "operation": "handoff-engine",
            "thread": thread,
            "handoff_state_live_primary_engine_identity": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "handoff_state_live_primary_engine_identity_fields": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "handoff_state_live_primary_engine_postures": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_POSTURES,
            "handoff_state_live_primary_engine_run_kinds": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "handoff_state_live_primary_engine_stop_boundaries": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
            "handoff_state_live_primary_engine_projection_fields": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "handoff_state_live_primary_engine_projection": projection,
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_approval_engine(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    recursion_limit = int(args.recursion_limit or 8)
    run_kind = args.run_kind or str(thread.get("last_approval_aware_live_primary_engine_kind", "")) or "invoke"
    if args.run_kind:
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread, live_run_kind=args.run_kind)
        _persist_approval_aware_live_primary_engine_state(thread, args.run_kind, recursion_limit)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    projection = _approval_aware_live_primary_engine_projection(thread, args.thread_id)
    if args.run_kind or recursion_limit != int(thread.get("last_approval_aware_live_primary_engine_recursion_limit", 8) or 8):
        preview = _execute_approval_aware_live_primary_engine(thread, run_kind, recursion_limit)
        projection = {
            "engine_identity": _approval_aware_live_primary_engine_identity(),
            "compile_supported": preview["compile_supported"],
            "compiled_graph_present": preview["compiled_graph_present"],
            "invoke_supported": preview["invoke_supported"],
            "stream_supported": preview["stream_supported"],
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "approval_node_path": preview["approval_node_path"],
            "approval_phase_path": preview["approval_phase_path"],
            "approval_transition_log": preview["approval_transition_log"],
            "resume_state_kind": preview["resume_state_kind"],
            "queue_posture": preview["queue_posture"],
            "pending_count": preview["pending_count"],
            "resolved_count": preview["resolved_count"],
            "current_interrupt_id": preview["current_interrupt_id"],
            "resume_map_keys": preview["resume_map_keys"],
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": preview["recursion_limit"],
            "execution_posture": preview["execution_posture"],
            "last_run_kind": preview["last_run_kind"],
            "last_run_status": preview["last_run_status"],
            "last_run_reason": preview["last_run_reason"],
            "helper_pointer": projection["helper_pointer"],
        }

    _emit(
        {
            "operation": "approval-engine",
            "thread": thread,
            "approval_aware_live_primary_engine_identity": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "approval_aware_live_primary_engine_identity_fields": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "approval_aware_live_primary_engine_postures": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
            "approval_aware_live_primary_engine_run_kinds": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "approval_aware_live_primary_engine_stop_boundaries": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
            "approval_aware_live_primary_engine_projection_fields": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "approval_aware_live_primary_engine_projection": projection,
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_provenance_engine(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    recursion_limit = int(args.recursion_limit or 8)
    run_kind = args.run_kind or str(thread.get("last_provenance_state_live_primary_engine_kind", "")) or "invoke"
    if args.run_kind:
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread, live_run_kind=args.run_kind)
        _persist_provenance_state_live_primary_engine_state(thread, args.run_kind, recursion_limit)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    projection = _provenance_state_live_primary_engine_projection(thread, args.thread_id)
    if args.run_kind or recursion_limit != int(thread.get("last_provenance_state_live_primary_engine_recursion_limit", 8) or 8):
        preview = _execute_provenance_state_live_primary_engine(thread, run_kind, recursion_limit)
        projection = {
            "engine_identity": _provenance_state_live_primary_engine_identity(),
            "compile_supported": preview["compile_supported"],
            "compiled_graph_present": preview["compiled_graph_present"],
            "invoke_supported": preview["invoke_supported"],
            "stream_supported": preview["stream_supported"],
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "provenance_node_path": preview["provenance_node_path"],
            "provenance_phase_path": preview["provenance_phase_path"],
            "provenance_transition_log": preview["provenance_transition_log"],
            "provenance_state_kind": preview["provenance_state_kind"],
            "recovery_posture": preview["recovery_posture"],
            "recovery_action": preview["recovery_action"],
            "recovery_target_id": preview["recovery_target_id"],
            "recovery_target_kind": preview["recovery_target_kind"],
            "source_records": preview["source_records"],
            "recoverable_fields_touched": preview["recoverable_fields_touched"],
            "history_compatibility": preview["history_compatibility"],
            "history_target_count": preview["history_target_count"],
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": preview["recursion_limit"],
            "execution_posture": preview["execution_posture"],
            "last_run_kind": preview["last_run_kind"],
            "last_run_status": preview["last_run_status"],
            "last_run_reason": preview["last_run_reason"],
            "helper_pointer": projection["helper_pointer"],
        }

    _emit(
        {
            "operation": "provenance-engine",
            "thread": thread,
            "provenance_state_live_primary_engine_identity": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "provenance_state_live_primary_engine_identity_fields": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "provenance_state_live_primary_engine_postures": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_POSTURES,
            "provenance_state_live_primary_engine_run_kinds": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "provenance_state_live_primary_engine_stop_boundaries": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
            "provenance_state_live_primary_engine_projection_fields": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "provenance_state_live_primary_engine_projection": projection,
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_artifact_engine(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    recursion_limit = int(args.recursion_limit or 8)
    run_kind = (
        args.run_kind or str(thread.get("last_durable_artifact_aware_live_primary_engine_kind", "")) or "invoke"
    )
    if args.run_kind:
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread, live_run_kind=args.run_kind)
        _persist_durable_artifact_aware_live_primary_engine_state(thread, args.run_kind, recursion_limit)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    projection = _durable_artifact_aware_live_primary_engine_projection(thread, args.thread_id)
    if args.run_kind or recursion_limit != int(
        thread.get("last_durable_artifact_aware_live_primary_engine_recursion_limit", 8) or 8
    ):
        preview = _execute_durable_artifact_aware_live_primary_engine(thread, run_kind, recursion_limit)
        projection = {
            "engine_identity": _durable_artifact_aware_live_primary_engine_identity(),
            "compile_supported": preview["compile_supported"],
            "compiled_graph_present": preview["compiled_graph_present"],
            "invoke_supported": preview["invoke_supported"],
            "stream_supported": preview["stream_supported"],
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "artifact_node_path": preview["artifact_node_path"],
            "artifact_phase_path": preview["artifact_phase_path"],
            "artifact_transition_log": preview["artifact_transition_log"],
            "artifact_state_kind": preview["artifact_state_kind"],
            "implementation_brief_present": preview["implementation_brief_present"],
            "implementation_brief_id": preview["implementation_brief_id"],
            "implementation_brief_source_evidence_ref_count": preview[
                "implementation_brief_source_evidence_ref_count"
            ],
            "survivor_queue_present": preview["survivor_queue_present"],
            "survivor_queue_kind": preview["survivor_queue_kind"],
            "survivor_count": preview["survivor_count"],
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": preview["recursion_limit"],
            "execution_posture": preview["execution_posture"],
            "last_run_kind": preview["last_run_kind"],
            "last_run_status": preview["last_run_status"],
            "last_run_reason": preview["last_run_reason"],
            "helper_pointer": projection["helper_pointer"],
        }

    _emit(
        {
            "operation": "artifact-engine",
            "thread": thread,
            "durable_artifact_aware_live_primary_engine_identity": (
                DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY
            ),
            "durable_artifact_aware_live_primary_engine_identity_fields": (
                DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS
            ),
            "durable_artifact_aware_live_primary_engine_postures": (
                DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_POSTURES
            ),
            "durable_artifact_aware_live_primary_engine_run_kinds": (
                DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS
            ),
            "durable_artifact_aware_live_primary_engine_stop_boundaries": (
                DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES
            ),
            "durable_artifact_aware_live_primary_engine_projection_fields": (
                DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS
            ),
            "durable_artifact_aware_live_primary_engine_projection": projection,
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_reducer_engine(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    recursion_limit = int(args.recursion_limit or 8)
    run_kind = args.run_kind or str(thread.get("last_reducer_aware_live_primary_engine_kind", "")) or "invoke"
    if args.run_kind:
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread, live_run_kind=args.run_kind)
        _persist_reducer_aware_live_primary_engine_state(thread, args.run_kind, recursion_limit)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    projection = _reducer_aware_live_primary_engine_projection(thread, args.thread_id)
    if args.run_kind or recursion_limit != int(
        thread.get("last_reducer_aware_live_primary_engine_recursion_limit", 8) or 8
    ):
        preview = _execute_reducer_aware_live_primary_engine(thread, run_kind, recursion_limit)
        projection = {
            "engine_identity": _reducer_aware_live_primary_engine_identity(),
            "compile_supported": preview["compile_supported"],
            "compiled_graph_present": preview["compiled_graph_present"],
            "invoke_supported": preview["invoke_supported"],
            "stream_supported": preview["stream_supported"],
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "merge_node_path": preview["merge_node_path"],
            "merge_phase_path": preview["merge_phase_path"],
            "merge_transition_log": preview["merge_transition_log"],
            "merge_state_kind": preview["merge_state_kind"],
            "reducer_compatibility": preview["reducer_compatibility"],
            "fanout_state": preview["fanout_state"],
            "invalid_multi_writer_detected": preview["invalid_multi_writer_detected"],
            "invalid_multi_writer_updates": preview["invalid_multi_writer_updates"],
            "merge_channels_updated": preview["merge_channels_updated"],
            "channel_item_counts": preview["channel_item_counts"],
            "source_records": preview["source_records"],
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": preview["recursion_limit"],
            "execution_posture": preview["execution_posture"],
            "last_run_kind": preview["last_run_kind"],
            "last_run_status": preview["last_run_status"],
            "last_run_reason": preview["last_run_reason"],
            "helper_pointer": projection["helper_pointer"],
        }

    _emit(
        {
            "operation": "reducer-engine",
            "thread": thread,
            "reducer_aware_live_primary_engine_identity": REDUCER_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "reducer_aware_live_primary_engine_identity_fields": (
                REDUCER_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS
            ),
            "reducer_aware_live_primary_engine_postures": REDUCER_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
            "reducer_aware_live_primary_engine_run_kinds": REDUCER_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "reducer_aware_live_primary_engine_stop_boundaries": (
                REDUCER_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES
            ),
            "reducer_aware_live_primary_engine_projection_fields": (
                REDUCER_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS
            ),
            "reducer_aware_live_primary_engine_projection": projection,
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_command_engine(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    recursion_limit = int(args.recursion_limit or 8)
    run_kind = args.run_kind or str(thread.get("last_command_aware_live_primary_engine_kind", "")) or "invoke"
    if args.run_kind:
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread, live_run_kind=args.run_kind)
        _persist_command_aware_live_primary_engine_state(thread, args.run_kind, recursion_limit)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    projection = _command_aware_live_primary_engine_projection(thread, args.thread_id)
    if args.run_kind or recursion_limit != int(
        thread.get("last_command_aware_live_primary_engine_recursion_limit", 8) or 8
    ):
        preview = _execute_command_aware_live_primary_engine(thread, run_kind, recursion_limit)
        projection = {
            "engine_identity": _command_aware_live_primary_engine_identity(),
            "compile_supported": preview["compile_supported"],
            "compiled_graph_present": preview["compiled_graph_present"],
            "invoke_supported": preview["invoke_supported"],
            "stream_supported": preview["stream_supported"],
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "command_node_path": preview["command_node_path"],
            "command_phase_path": preview["command_phase_path"],
            "command_transition_log": preview["command_transition_log"],
            "control_state_kind": preview["control_state_kind"],
            "transition_kind": preview["transition_kind"],
            "update_keys": preview["update_keys"],
            "goto_target": preview["goto_target"],
            "graph_scope": preview["graph_scope"],
            "source_subgraph": preview["source_subgraph"],
            "target_subgraph": preview["target_subgraph"],
            "parent_handoff_target": preview["parent_handoff_target"],
            "resume_posture": preview["resume_posture"],
            "resume_payload_present": preview["resume_payload_present"],
            "resume_payload_keys": preview["resume_payload_keys"],
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": preview["recursion_limit"],
            "execution_posture": preview["execution_posture"],
            "last_run_kind": preview["last_run_kind"],
            "last_run_status": preview["last_run_status"],
            "last_run_reason": preview["last_run_reason"],
            "helper_pointer": projection["helper_pointer"],
        }

    _emit(
        {
            "operation": "command-engine",
            "thread": thread,
            "command_aware_live_primary_engine_identity": COMMAND_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "command_aware_live_primary_engine_identity_fields": (
                COMMAND_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS
            ),
            "command_aware_live_primary_engine_postures": COMMAND_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
            "command_aware_live_primary_engine_run_kinds": COMMAND_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "command_aware_live_primary_engine_stop_boundaries": (
                COMMAND_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES
            ),
            "command_aware_live_primary_engine_projection_fields": (
                COMMAND_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS
            ),
            "command_aware_live_primary_engine_projection": projection,
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_runtime_engine(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    recursion_limit = int(args.recursion_limit or 8)
    run_kind = args.run_kind or str(thread.get("last_runtime_aware_live_primary_engine_kind", "")) or "invoke"
    if args.run_kind:
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread, live_run_kind=args.run_kind)
        _persist_runtime_aware_live_primary_engine_state(thread, args.run_kind, recursion_limit)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    projection = _runtime_aware_live_primary_engine_projection(thread, args.thread_id)
    if args.run_kind or recursion_limit != int(
        thread.get("last_runtime_aware_live_primary_engine_recursion_limit", 8) or 8
    ):
        preview = _execute_runtime_aware_live_primary_engine(thread, run_kind, recursion_limit)
        projection = {
            "engine_identity": _runtime_aware_live_primary_engine_identity(),
            "compile_supported": preview["compile_supported"],
            "compiled_graph_present": preview["compiled_graph_present"],
            "invoke_supported": preview["invoke_supported"],
            "stream_supported": preview["stream_supported"],
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "runtime_node_path": preview["runtime_node_path"],
            "runtime_phase_path": preview["runtime_phase_path"],
            "runtime_transition_log": preview["runtime_transition_log"],
            "runtime_state_kind": preview["runtime_state_kind"],
            "context_schema": preview["context_schema"],
            "runtime_context_present": preview["runtime_context_present"],
            "runtime_context_keys": preview["runtime_context_keys"],
            "runtime_context_kind_hints": preview["runtime_context_kind_hints"],
            "store_configured": preview["store_configured"],
            "store_access_expected": preview["store_access_expected"],
            "store_kind": preview["store_kind"],
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": preview["recursion_limit"],
            "execution_posture": preview["execution_posture"],
            "last_run_kind": preview["last_run_kind"],
            "last_run_status": preview["last_run_status"],
            "last_run_reason": preview["last_run_reason"],
            "helper_pointer": projection["helper_pointer"],
        }

    _emit(
        {
            "operation": "runtime-engine",
            "thread": thread,
            "runtime_aware_live_primary_engine_identity": RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "runtime_aware_live_primary_engine_identity_fields": (
                RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS
            ),
            "runtime_aware_live_primary_engine_postures": RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
            "runtime_aware_live_primary_engine_run_kinds": RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "runtime_aware_live_primary_engine_stop_boundaries": (
                RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES
            ),
            "runtime_aware_live_primary_engine_projection_fields": (
                RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS
            ),
            "runtime_aware_live_primary_engine_projection": projection,
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_memory_engine(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    recursion_limit = int(args.recursion_limit or 8)
    run_kind = args.run_kind or str(thread.get("last_memory_aware_live_primary_engine_kind", "")) or "invoke"
    if args.run_kind:
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread, live_run_kind=args.run_kind)
        _persist_memory_aware_live_primary_engine_state(thread, args.run_kind, recursion_limit)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    projection = _memory_aware_live_primary_engine_projection(thread, args.thread_id)
    if args.run_kind or recursion_limit != int(
        thread.get("last_memory_aware_live_primary_engine_recursion_limit", 8) or 8
    ):
        preview = _execute_memory_aware_live_primary_engine(thread, run_kind, recursion_limit)
        projection = {
            "engine_identity": _memory_aware_live_primary_engine_identity(),
            "compile_supported": preview["compile_supported"],
            "compiled_graph_present": preview["compiled_graph_present"],
            "invoke_supported": preview["invoke_supported"],
            "stream_supported": preview["stream_supported"],
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "memory_node_path": preview["memory_node_path"],
            "memory_phase_path": preview["memory_phase_path"],
            "memory_transition_log": preview["memory_transition_log"],
            "memory_state_kind": preview["memory_state_kind"],
            "memory_store_configured": preview["memory_store_configured"],
            "memory_store_kind": preview["memory_store_kind"],
            "memory_namespaces": preview["memory_namespaces"],
            "semantic_memory_enabled": preview["semantic_memory_enabled"],
            "semantic_store_kind": preview["semantic_store_kind"],
            "semantic_namespaces": preview["semantic_namespaces"],
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": preview["recursion_limit"],
            "execution_posture": preview["execution_posture"],
            "last_run_kind": preview["last_run_kind"],
            "last_run_status": preview["last_run_status"],
            "last_run_reason": preview["last_run_reason"],
            "helper_pointer": projection["helper_pointer"],
        }

    _emit(
        {
            "operation": "memory-engine",
            "thread": thread,
            "memory_aware_live_primary_engine_identity": MEMORY_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "memory_aware_live_primary_engine_identity_fields": (
                MEMORY_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS
            ),
            "memory_aware_live_primary_engine_postures": MEMORY_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
            "memory_aware_live_primary_engine_run_kinds": MEMORY_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "memory_aware_live_primary_engine_stop_boundaries": (
                MEMORY_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES
            ),
            "memory_aware_live_primary_engine_projection_fields": (
                MEMORY_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS
            ),
            "memory_aware_live_primary_engine_projection": projection,
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_migration_engine(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    recursion_limit = int(args.recursion_limit or 8)
    run_kind = args.run_kind or str(thread.get("last_migration_aware_live_primary_engine_kind", "")) or "invoke"
    if args.run_kind:
        thread["updated_at"] = _now()
        _persist_runtime_state_layers(thread, live_run_kind=args.run_kind)
        _persist_migration_aware_live_primary_engine_state(thread, args.run_kind, recursion_limit)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)

    projection = _migration_aware_live_primary_engine_projection(thread, args.thread_id)
    if args.run_kind or recursion_limit != int(
        thread.get("last_migration_aware_live_primary_engine_recursion_limit", 8) or 8
    ):
        preview = _execute_migration_aware_live_primary_engine(thread, run_kind, recursion_limit)
        projection = {
            "engine_identity": _migration_aware_live_primary_engine_identity(),
            "compile_supported": preview["compile_supported"],
            "compiled_graph_present": preview["compiled_graph_present"],
            "invoke_supported": preview["invoke_supported"],
            "stream_supported": preview["stream_supported"],
            "current_execution_node": preview["current_execution_node"],
            "mapped_phase": preview["mapped_phase"],
            "compatibility_node_path": preview["compatibility_node_path"],
            "compatibility_phase_path": preview["compatibility_phase_path"],
            "compatibility_transition_log": preview["compatibility_transition_log"],
            "compatibility_state_kind": preview["compatibility_state_kind"],
            "current_graph_contract": preview["current_graph_contract"],
            "thread_graph_contract": preview["thread_graph_contract"],
            "topology_compatibility": preview["topology_compatibility"],
            "state_schema_compatibility": preview["state_schema_compatibility"],
            "compatibility": preview["compatibility"],
            "reason_codes": preview["reason_codes"],
            "superstep_count": preview["superstep_count"],
            "stop_boundary": preview["stop_boundary"],
            "terminal_reached": preview["terminal_reached"],
            "recursion_limit_supported": preview["recursion_limit_supported"],
            "remaining_steps_supported": preview["remaining_steps_supported"],
            "recursion_limit": preview["recursion_limit"],
            "execution_posture": preview["execution_posture"],
            "last_run_kind": preview["last_run_kind"],
            "last_run_status": preview["last_run_status"],
            "last_run_reason": preview["last_run_reason"],
            "helper_pointer": projection["helper_pointer"],
        }

    _emit(
        {
            "operation": "migration-engine",
            "thread": thread,
            "migration_aware_live_primary_engine_identity": MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "migration_aware_live_primary_engine_identity_fields": (
                MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS
            ),
            "migration_aware_live_primary_engine_postures": MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
            "migration_aware_live_primary_engine_run_kinds": MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "migration_aware_live_primary_engine_stop_boundaries": (
                MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES
            ),
            "migration_aware_live_primary_engine_projection_fields": (
                MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS
            ),
            "migration_aware_live_primary_engine_projection": projection,
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_auto_policy(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    layout = ensure_layout(repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    interrupt = read_interrupt(repo_root, args.thread_id)
    if args.apply:
        thread["updated_at"] = _now()
        interrupt, _ = _apply_automatic_runtime_policy(thread, interrupt)
        _persist_runtime_state_layers(thread)
        write_thread_record(repo_root, thread)
        if interrupt:
            write_interrupt(repo_root, interrupt)
        else:
            delete_interrupt(repo_root, args.thread_id)
        _save_backend_projection(repo_root, layout, thread)

    _emit(
        {
            "operation": "auto-policy",
            "thread": thread,
            "interrupt": interrupt,
            "automatic_runtime_policy_identity": AUTOMATIC_RUNTIME_POLICY_IDENTITY,
            "automatic_runtime_policy_identity_fields": AUTOMATIC_RUNTIME_POLICY_IDENTITY_FIELDS,
            "automatic_runtime_policy_migration_postures": AUTOMATIC_RUNTIME_POLICY_MIGRATION_POSTURES,
            "automatic_runtime_policy_approval_postures": AUTOMATIC_RUNTIME_POLICY_APPROVAL_POSTURES,
            "automatic_runtime_policy_recovery_postures": AUTOMATIC_RUNTIME_POLICY_RECOVERY_POSTURES,
            "automatic_runtime_policy_actions": AUTOMATIC_RUNTIME_POLICY_ACTIONS,
            "automatic_runtime_policy_projection_fields": AUTOMATIC_RUNTIME_POLICY_PROJECTION_FIELDS,
            "automatic_runtime_policy_projection": _automatic_runtime_policy_projection(thread, args.thread_id),
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_subgraph_state(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    _emit(
        {
            "operation": "subgraph-state",
            "thread": thread,
            "subgraph_persistence_modes": SUBGRAPH_PERSISTENCE_MODES,
            "subgraph_checkpointer_modes": SUBGRAPH_CHECKPOINTER_MODES,
            "subgraph_state_inspection_scopes": SUBGRAPH_STATE_INSPECTION_SCOPES,
            "subgraph_state_inspection_fields": SUBGRAPH_STATE_INSPECTION_FIELDS,
            "subgraph_state_inspection_projection_fields": SUBGRAPH_STATE_INSPECTION_PROJECTION_FIELDS,
            "subgraph_state_inspection_projection": _subgraph_state_inspection_projection(thread, args.thread_id),
            "subgraph_projection": _subgraph_projection(thread, args.thread_id),
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_generalized_routing(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")

    _emit(
        {
            "operation": "generalized-routing",
            "thread": thread,
            "generalized_live_routing_identity": GENERALIZED_LIVE_ROUTING_IDENTITY,
            "generalized_live_routing_identity_fields": GENERALIZED_LIVE_ROUTING_IDENTITY_FIELDS,
            "generalized_live_routing_postures": GENERALIZED_LIVE_ROUTING_POSTURES,
            "generalized_live_routing_route_kinds": GENERALIZED_LIVE_ROUTING_ROUTE_KINDS,
            "generalized_live_routing_projection_fields": GENERALIZED_LIVE_ROUTING_PROJECTION_FIELDS,
            "generalized_live_routing_projection": _generalized_live_routing_projection(thread, args.thread_id),
            "helper_pointers": _helper_pointers(args.thread_id),
        }
    )


def cmd_subgraphs(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    payload: dict[str, Any] = {
        "operation": "subgraphs",
        "repo_root": str(repo_root),
        "current_graph_contract": CURRENT_GRAPH_CONTRACT,
        "graph_contract_fields": GRAPH_CONTRACT_FIELDS,
        "graph_kernel_identity": GRAPH_KERNEL_IDENTITY,
        "graph_kernel_identity_fields": GRAPH_KERNEL_IDENTITY_FIELDS,
        "graph_kernel_node_postures": GRAPH_KERNEL_NODE_POSTURES,
        "graph_kernel_transition_kinds": GRAPH_KERNEL_TRANSITION_KINDS,
        "graph_kernel_node_fields": GRAPH_KERNEL_NODE_FIELDS,
        "graph_kernel_edge_fields": GRAPH_KERNEL_EDGE_FIELDS,
        "graph_kernel_projection_fields": GRAPH_KERNEL_PROJECTION_FIELDS,
        "graph_kernel_phase_to_node": GRAPH_KERNEL_PHASE_TO_NODE,
        "graph_kernel_nodes": GRAPH_KERNEL_NODES,
        "graph_kernel_edges": GRAPH_KERNEL_EDGES,
        "primary_runtime_engine_identity": PRIMARY_RUNTIME_ENGINE_IDENTITY,
        "primary_runtime_engine_identity_fields": PRIMARY_RUNTIME_ENGINE_IDENTITY_FIELDS,
        "primary_runtime_engine_postures": PRIMARY_RUNTIME_ENGINE_POSTURES,
        "primary_runtime_engine_projection_fields": PRIMARY_RUNTIME_ENGINE_PROJECTION_FIELDS,
        "compiled_invocation_identity": COMPILED_INVOCATION_IDENTITY,
        "compiled_invocation_identity_fields": COMPILED_INVOCATION_IDENTITY_FIELDS,
        "compiled_invocation_postures": COMPILED_INVOCATION_POSTURES,
        "compiled_invocation_run_kinds": COMPILED_INVOCATION_RUN_KINDS,
        "compiled_invocation_projection_fields": COMPILED_INVOCATION_PROJECTION_FIELDS,
        "live_execution_identity": LIVE_EXECUTION_IDENTITY,
        "live_execution_identity_fields": LIVE_EXECUTION_IDENTITY_FIELDS,
        "live_execution_postures": LIVE_EXECUTION_POSTURES,
        "live_execution_run_kinds": LIVE_EXECUTION_RUN_KINDS,
        "live_execution_projection_fields": LIVE_EXECUTION_PROJECTION_FIELDS,
        "fuller_live_primary_engine_identity": FULLER_LIVE_PRIMARY_ENGINE_IDENTITY,
        "fuller_live_primary_engine_identity_fields": FULLER_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
        "fuller_live_primary_engine_postures": FULLER_LIVE_PRIMARY_ENGINE_POSTURES,
        "fuller_live_primary_engine_run_kinds": FULLER_LIVE_PRIMARY_ENGINE_RUN_KINDS,
        "fuller_live_primary_engine_transition_kinds": FULLER_LIVE_PRIMARY_ENGINE_TRANSITION_KINDS,
        "fuller_live_primary_engine_projection_fields": FULLER_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
        "superstep_live_primary_engine_identity": SUPERSTEP_LIVE_PRIMARY_ENGINE_IDENTITY,
        "superstep_live_primary_engine_identity_fields": SUPERSTEP_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
        "superstep_live_primary_engine_postures": SUPERSTEP_LIVE_PRIMARY_ENGINE_POSTURES,
        "superstep_live_primary_engine_run_kinds": SUPERSTEP_LIVE_PRIMARY_ENGINE_RUN_KINDS,
        "superstep_live_primary_engine_stop_boundaries": SUPERSTEP_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
        "superstep_live_primary_engine_projection_fields": SUPERSTEP_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
        "stateful_live_primary_engine_identity": STATEFUL_LIVE_PRIMARY_ENGINE_IDENTITY,
        "stateful_live_primary_engine_identity_fields": STATEFUL_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
        "stateful_live_primary_engine_postures": STATEFUL_LIVE_PRIMARY_ENGINE_POSTURES,
        "stateful_live_primary_engine_run_kinds": STATEFUL_LIVE_PRIMARY_ENGINE_RUN_KINDS,
        "stateful_live_primary_engine_stop_boundaries": STATEFUL_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
        "stateful_live_primary_engine_projection_fields": STATEFUL_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
        "boundary_state_live_primary_engine_identity": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_IDENTITY,
        "boundary_state_live_primary_engine_identity_fields": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
        "boundary_state_live_primary_engine_postures": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_POSTURES,
        "boundary_state_live_primary_engine_run_kinds": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
        "boundary_state_live_primary_engine_stop_boundaries": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
        "boundary_state_live_primary_engine_projection_fields": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
        "handoff_state_live_primary_engine_identity": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_IDENTITY,
        "handoff_state_live_primary_engine_identity_fields": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
        "handoff_state_live_primary_engine_postures": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_POSTURES,
        "handoff_state_live_primary_engine_run_kinds": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
        "handoff_state_live_primary_engine_stop_boundaries": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
        "handoff_state_live_primary_engine_projection_fields": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
        "approval_aware_live_primary_engine_identity": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
        "approval_aware_live_primary_engine_identity_fields": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
        "approval_aware_live_primary_engine_postures": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
        "approval_aware_live_primary_engine_run_kinds": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
        "approval_aware_live_primary_engine_stop_boundaries": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
        "approval_aware_live_primary_engine_projection_fields": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
        "provenance_state_live_primary_engine_identity": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_IDENTITY,
        "provenance_state_live_primary_engine_identity_fields": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
        "provenance_state_live_primary_engine_postures": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_POSTURES,
        "provenance_state_live_primary_engine_run_kinds": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
        "provenance_state_live_primary_engine_stop_boundaries": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
        "provenance_state_live_primary_engine_projection_fields": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
        "durable_artifact_aware_live_primary_engine_identity": DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
        "durable_artifact_aware_live_primary_engine_identity_fields": (
            DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS
        ),
        "durable_artifact_aware_live_primary_engine_postures": (
            DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_POSTURES
        ),
        "durable_artifact_aware_live_primary_engine_run_kinds": (
            DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS
        ),
        "durable_artifact_aware_live_primary_engine_stop_boundaries": (
            DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES
        ),
        "durable_artifact_aware_live_primary_engine_projection_fields": (
            DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS
        ),
        "reducer_aware_live_primary_engine_identity": REDUCER_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
        "reducer_aware_live_primary_engine_identity_fields": REDUCER_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
        "reducer_aware_live_primary_engine_postures": REDUCER_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
        "reducer_aware_live_primary_engine_run_kinds": REDUCER_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
        "reducer_aware_live_primary_engine_stop_boundaries": REDUCER_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
        "reducer_aware_live_primary_engine_projection_fields": REDUCER_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
        "command_aware_live_primary_engine_identity": COMMAND_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
        "command_aware_live_primary_engine_identity_fields": COMMAND_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
        "command_aware_live_primary_engine_postures": COMMAND_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
        "command_aware_live_primary_engine_run_kinds": COMMAND_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
        "command_aware_live_primary_engine_stop_boundaries": COMMAND_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
        "command_aware_live_primary_engine_projection_fields": COMMAND_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
        "runtime_aware_live_primary_engine_identity": RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
        "runtime_aware_live_primary_engine_identity_fields": RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
        "runtime_aware_live_primary_engine_postures": RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
        "runtime_aware_live_primary_engine_run_kinds": RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
        "runtime_aware_live_primary_engine_stop_boundaries": RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
        "runtime_aware_live_primary_engine_projection_fields": RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
        "memory_aware_live_primary_engine_identity": MEMORY_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
        "memory_aware_live_primary_engine_identity_fields": MEMORY_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
        "memory_aware_live_primary_engine_postures": MEMORY_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
        "memory_aware_live_primary_engine_run_kinds": MEMORY_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
        "memory_aware_live_primary_engine_stop_boundaries": MEMORY_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
        "memory_aware_live_primary_engine_projection_fields": MEMORY_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
        "migration_aware_live_primary_engine_identity": MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
        "migration_aware_live_primary_engine_identity_fields": (
            MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS
        ),
        "migration_aware_live_primary_engine_postures": MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
        "migration_aware_live_primary_engine_run_kinds": MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
        "migration_aware_live_primary_engine_stop_boundaries": (
            MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES
        ),
        "migration_aware_live_primary_engine_projection_fields": (
            MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS
        ),
        "automatic_runtime_policy_identity": AUTOMATIC_RUNTIME_POLICY_IDENTITY,
        "automatic_runtime_policy_identity_fields": AUTOMATIC_RUNTIME_POLICY_IDENTITY_FIELDS,
        "automatic_runtime_policy_migration_postures": AUTOMATIC_RUNTIME_POLICY_MIGRATION_POSTURES,
        "automatic_runtime_policy_approval_postures": AUTOMATIC_RUNTIME_POLICY_APPROVAL_POSTURES,
        "automatic_runtime_policy_recovery_postures": AUTOMATIC_RUNTIME_POLICY_RECOVERY_POSTURES,
        "automatic_runtime_policy_actions": AUTOMATIC_RUNTIME_POLICY_ACTIONS,
        "automatic_runtime_policy_projection_fields": AUTOMATIC_RUNTIME_POLICY_PROJECTION_FIELDS,
        "subgraph_persistence_modes": SUBGRAPH_PERSISTENCE_MODES,
        "subgraph_checkpointer_modes": SUBGRAPH_CHECKPOINTER_MODES,
        "subgraph_state_inspection_scopes": SUBGRAPH_STATE_INSPECTION_SCOPES,
        "subgraph_state_inspection_fields": SUBGRAPH_STATE_INSPECTION_FIELDS,
        "subgraph_state_inspection_projection_fields": SUBGRAPH_STATE_INSPECTION_PROJECTION_FIELDS,
        "generalized_live_routing_identity": GENERALIZED_LIVE_ROUTING_IDENTITY,
        "generalized_live_routing_identity_fields": GENERALIZED_LIVE_ROUTING_IDENTITY_FIELDS,
        "generalized_live_routing_postures": GENERALIZED_LIVE_ROUTING_POSTURES,
        "generalized_live_routing_route_kinds": GENERALIZED_LIVE_ROUTING_ROUTE_KINDS,
        "generalized_live_routing_projection_fields": GENERALIZED_LIVE_ROUTING_PROJECTION_FIELDS,
        "subgraph_library": SUBGRAPHS,
        "subgraph_library_fields": SUBGRAPH_LIBRARY_FIELDS,
        "approval_queue_item_fields": APPROVAL_QUEUE_ITEM_FIELDS,
        "approval_queue_item_statuses": APPROVAL_QUEUE_ITEM_STATUSES,
        "approval_queue_postures": APPROVAL_QUEUE_POSTURES,
        "approval_queue_projection_fields": APPROVAL_QUEUE_PROJECTION_FIELDS,
        "migration_projection_fields": MIGRATION_PROJECTION_FIELDS,
        "migration_reason_codes": MIGRATION_REASON_CODES,
        "subgraph_projection_fields": SUBGRAPH_PROJECTION_FIELDS,
        "command_state_fields": COMMAND_STATE_FIELDS,
        "command_projection_fields": COMMAND_PROJECTION_FIELDS,
        "stream_event_fields": STREAM_EVENT_FIELDS,
        "stream_projection_fields": STREAM_PROJECTION_FIELDS,
        "runtime_context_fields": RUNTIME_CONTEXT_FIELDS,
        "store_injection_fields": STORE_INJECTION_FIELDS,
        "runtime_injection_projection_fields": RUNTIME_INJECTION_PROJECTION_FIELDS,
        "memory_store_fields": MEMORY_STORE_FIELDS,
        "semantic_memory_fields": SEMANTIC_MEMORY_FIELDS,
        "memory_projection_fields": MEMORY_PROJECTION_FIELDS,
    }
    if args.thread_id:
        thread = read_thread_record(repo_root, args.thread_id)
        payload["thread_id"] = args.thread_id
        payload["thread"] = thread
        payload["graph_kernel_projection"] = _graph_kernel_projection(thread, args.thread_id)
        payload["primary_runtime_engine_projection"] = _primary_runtime_engine_projection(thread, args.thread_id)
        payload["compiled_invocation_projection"] = _compiled_invocation_projection(thread, args.thread_id)
        payload["live_execution_projection"] = _live_execution_projection(thread, args.thread_id)
        payload["fuller_live_primary_engine_projection"] = _fuller_live_primary_engine_projection(
            thread, args.thread_id
        )
        payload["deeper_live_primary_engine_projection"] = _deeper_live_primary_engine_projection(
            thread, args.thread_id
        )
        payload["superstep_live_primary_engine_projection"] = _superstep_live_primary_engine_projection(
            thread, args.thread_id
        )
        payload["stateful_live_primary_engine_projection"] = _stateful_live_primary_engine_projection(
            thread, args.thread_id
        )
        payload["boundary_state_live_primary_engine_projection"] = _boundary_state_live_primary_engine_projection(
            thread, args.thread_id
        )
        payload["handoff_state_live_primary_engine_projection"] = _handoff_state_live_primary_engine_projection(
            thread, args.thread_id
        )
        payload["approval_aware_live_primary_engine_projection"] = _approval_aware_live_primary_engine_projection(
            thread, args.thread_id
        )
        payload["provenance_state_live_primary_engine_projection"] = _provenance_state_live_primary_engine_projection(
            thread, args.thread_id
        )
        payload["durable_artifact_aware_live_primary_engine_projection"] = (
            _durable_artifact_aware_live_primary_engine_projection(thread, args.thread_id)
        )
        payload["reducer_aware_live_primary_engine_projection"] = _reducer_aware_live_primary_engine_projection(
            thread, args.thread_id
        )
        payload["command_aware_live_primary_engine_projection"] = _command_aware_live_primary_engine_projection(
            thread, args.thread_id
        )
        payload["runtime_aware_live_primary_engine_projection"] = _runtime_aware_live_primary_engine_projection(
            thread, args.thread_id
        )
        payload["memory_aware_live_primary_engine_projection"] = _memory_aware_live_primary_engine_projection(
            thread, args.thread_id
        )
        payload["migration_aware_live_primary_engine_projection"] = _migration_aware_live_primary_engine_projection(
            thread, args.thread_id
        )
        payload["automatic_runtime_policy_projection"] = _automatic_runtime_policy_projection(
            thread, args.thread_id
        )
        payload["subgraph_state_inspection_projection"] = _subgraph_state_inspection_projection(
            thread, args.thread_id
        )
        payload["generalized_live_routing_projection"] = _generalized_live_routing_projection(thread, args.thread_id)
        payload["approval_queue_projection"] = _approval_queue_projection(thread, args.thread_id)
        payload["migration_projection"] = _migration_projection(thread, args.thread_id)
        payload["subgraph_projection"] = _subgraph_projection(thread, args.thread_id)
        payload["helper_pointers"] = _helper_pointers(args.thread_id)
    _emit(payload)


def cmd_inspect(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    layout = ensure_layout(repo_root)
    thread_id = args.thread_id or load_backend_record(repo_root).get("thread_id", "")
    payload: dict[str, Any] = {
        "operation": "inspect",
        "repo_root": str(repo_root),
        "layout": layout,
        "backend_record": load_backend_record(repo_root),
        "contract": {
            "root_phases": ROOT_PHASES,
            "current_graph_contract": CURRENT_GRAPH_CONTRACT,
            "graph_contract_fields": GRAPH_CONTRACT_FIELDS,
            "graph_kernel_identity": GRAPH_KERNEL_IDENTITY,
            "graph_kernel_identity_fields": GRAPH_KERNEL_IDENTITY_FIELDS,
            "graph_kernel_node_postures": GRAPH_KERNEL_NODE_POSTURES,
            "graph_kernel_transition_kinds": GRAPH_KERNEL_TRANSITION_KINDS,
            "graph_kernel_node_fields": GRAPH_KERNEL_NODE_FIELDS,
            "graph_kernel_edge_fields": GRAPH_KERNEL_EDGE_FIELDS,
            "graph_kernel_projection_fields": GRAPH_KERNEL_PROJECTION_FIELDS,
            "graph_kernel_phase_to_node": GRAPH_KERNEL_PHASE_TO_NODE,
            "graph_kernel_nodes": GRAPH_KERNEL_NODES,
            "graph_kernel_edges": GRAPH_KERNEL_EDGES,
            "primary_runtime_engine_identity": PRIMARY_RUNTIME_ENGINE_IDENTITY,
            "primary_runtime_engine_identity_fields": PRIMARY_RUNTIME_ENGINE_IDENTITY_FIELDS,
            "primary_runtime_engine_postures": PRIMARY_RUNTIME_ENGINE_POSTURES,
            "primary_runtime_engine_projection_fields": PRIMARY_RUNTIME_ENGINE_PROJECTION_FIELDS,
            "compiled_invocation_identity": COMPILED_INVOCATION_IDENTITY,
            "compiled_invocation_identity_fields": COMPILED_INVOCATION_IDENTITY_FIELDS,
            "compiled_invocation_postures": COMPILED_INVOCATION_POSTURES,
            "compiled_invocation_run_kinds": COMPILED_INVOCATION_RUN_KINDS,
            "compiled_invocation_projection_fields": COMPILED_INVOCATION_PROJECTION_FIELDS,
            "live_execution_identity": LIVE_EXECUTION_IDENTITY,
            "live_execution_identity_fields": LIVE_EXECUTION_IDENTITY_FIELDS,
            "live_execution_postures": LIVE_EXECUTION_POSTURES,
            "live_execution_run_kinds": LIVE_EXECUTION_RUN_KINDS,
            "live_execution_projection_fields": LIVE_EXECUTION_PROJECTION_FIELDS,
            "fuller_live_primary_engine_identity": FULLER_LIVE_PRIMARY_ENGINE_IDENTITY,
            "fuller_live_primary_engine_identity_fields": FULLER_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "fuller_live_primary_engine_postures": FULLER_LIVE_PRIMARY_ENGINE_POSTURES,
            "fuller_live_primary_engine_run_kinds": FULLER_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "fuller_live_primary_engine_transition_kinds": FULLER_LIVE_PRIMARY_ENGINE_TRANSITION_KINDS,
            "fuller_live_primary_engine_projection_fields": FULLER_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "deeper_live_primary_engine_identity": DEEPER_LIVE_PRIMARY_ENGINE_IDENTITY,
            "deeper_live_primary_engine_identity_fields": DEEPER_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "deeper_live_primary_engine_postures": DEEPER_LIVE_PRIMARY_ENGINE_POSTURES,
            "deeper_live_primary_engine_run_kinds": DEEPER_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "deeper_live_primary_engine_stop_boundaries": DEEPER_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
            "deeper_live_primary_engine_projection_fields": DEEPER_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "superstep_live_primary_engine_identity": SUPERSTEP_LIVE_PRIMARY_ENGINE_IDENTITY,
            "superstep_live_primary_engine_identity_fields": SUPERSTEP_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "superstep_live_primary_engine_postures": SUPERSTEP_LIVE_PRIMARY_ENGINE_POSTURES,
            "superstep_live_primary_engine_run_kinds": SUPERSTEP_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "superstep_live_primary_engine_stop_boundaries": SUPERSTEP_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
            "superstep_live_primary_engine_projection_fields": SUPERSTEP_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "stateful_live_primary_engine_identity": STATEFUL_LIVE_PRIMARY_ENGINE_IDENTITY,
            "stateful_live_primary_engine_identity_fields": STATEFUL_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "stateful_live_primary_engine_postures": STATEFUL_LIVE_PRIMARY_ENGINE_POSTURES,
            "stateful_live_primary_engine_run_kinds": STATEFUL_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "stateful_live_primary_engine_stop_boundaries": STATEFUL_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
            "stateful_live_primary_engine_projection_fields": STATEFUL_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "boundary_state_live_primary_engine_identity": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "boundary_state_live_primary_engine_identity_fields": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "boundary_state_live_primary_engine_postures": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_POSTURES,
            "boundary_state_live_primary_engine_run_kinds": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "boundary_state_live_primary_engine_stop_boundaries": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
            "boundary_state_live_primary_engine_projection_fields": BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "handoff_state_live_primary_engine_identity": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "handoff_state_live_primary_engine_identity_fields": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "handoff_state_live_primary_engine_postures": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_POSTURES,
            "handoff_state_live_primary_engine_run_kinds": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "handoff_state_live_primary_engine_stop_boundaries": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
            "handoff_state_live_primary_engine_projection_fields": HANDOFF_STATE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "approval_aware_live_primary_engine_identity": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "approval_aware_live_primary_engine_identity_fields": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "approval_aware_live_primary_engine_postures": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
            "approval_aware_live_primary_engine_run_kinds": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "approval_aware_live_primary_engine_stop_boundaries": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
            "approval_aware_live_primary_engine_projection_fields": APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "provenance_state_live_primary_engine_identity": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "provenance_state_live_primary_engine_identity_fields": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "provenance_state_live_primary_engine_postures": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_POSTURES,
            "provenance_state_live_primary_engine_run_kinds": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "provenance_state_live_primary_engine_stop_boundaries": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES,
            "provenance_state_live_primary_engine_projection_fields": PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS,
            "durable_artifact_aware_live_primary_engine_identity": (
                DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY
            ),
            "durable_artifact_aware_live_primary_engine_identity_fields": (
                DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS
            ),
            "durable_artifact_aware_live_primary_engine_postures": (
                DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_POSTURES
            ),
            "durable_artifact_aware_live_primary_engine_run_kinds": (
                DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS
            ),
            "durable_artifact_aware_live_primary_engine_stop_boundaries": (
                DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES
            ),
            "durable_artifact_aware_live_primary_engine_projection_fields": (
                DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS
            ),
            "reducer_aware_live_primary_engine_identity": REDUCER_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "reducer_aware_live_primary_engine_identity_fields": (
                REDUCER_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS
            ),
            "reducer_aware_live_primary_engine_postures": REDUCER_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
            "reducer_aware_live_primary_engine_run_kinds": REDUCER_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "reducer_aware_live_primary_engine_stop_boundaries": (
                REDUCER_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES
            ),
            "reducer_aware_live_primary_engine_projection_fields": (
                REDUCER_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS
            ),
            "command_aware_live_primary_engine_identity": COMMAND_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "command_aware_live_primary_engine_identity_fields": (
                COMMAND_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS
            ),
            "command_aware_live_primary_engine_postures": COMMAND_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
            "command_aware_live_primary_engine_run_kinds": COMMAND_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "command_aware_live_primary_engine_stop_boundaries": (
                COMMAND_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES
            ),
            "command_aware_live_primary_engine_projection_fields": (
                COMMAND_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS
            ),
            "runtime_aware_live_primary_engine_identity": RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "runtime_aware_live_primary_engine_identity_fields": (
                RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS
            ),
            "runtime_aware_live_primary_engine_postures": RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
            "runtime_aware_live_primary_engine_run_kinds": RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "runtime_aware_live_primary_engine_stop_boundaries": (
                RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES
            ),
            "runtime_aware_live_primary_engine_projection_fields": (
                RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS
            ),
            "memory_aware_live_primary_engine_identity": MEMORY_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "memory_aware_live_primary_engine_identity_fields": MEMORY_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS,
            "memory_aware_live_primary_engine_postures": MEMORY_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
            "memory_aware_live_primary_engine_run_kinds": MEMORY_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "memory_aware_live_primary_engine_stop_boundaries": (
                MEMORY_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES
            ),
            "memory_aware_live_primary_engine_projection_fields": (
                MEMORY_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS
            ),
            "migration_aware_live_primary_engine_identity": MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY,
            "migration_aware_live_primary_engine_identity_fields": (
                MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_IDENTITY_FIELDS
            ),
            "migration_aware_live_primary_engine_postures": MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_POSTURES,
            "migration_aware_live_primary_engine_run_kinds": MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS,
            "migration_aware_live_primary_engine_stop_boundaries": (
                MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_STOP_BOUNDARIES
            ),
            "migration_aware_live_primary_engine_projection_fields": (
                MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_PROJECTION_FIELDS
            ),
            "automatic_runtime_policy_identity": AUTOMATIC_RUNTIME_POLICY_IDENTITY,
            "automatic_runtime_policy_identity_fields": AUTOMATIC_RUNTIME_POLICY_IDENTITY_FIELDS,
            "automatic_runtime_policy_migration_postures": AUTOMATIC_RUNTIME_POLICY_MIGRATION_POSTURES,
            "automatic_runtime_policy_approval_postures": AUTOMATIC_RUNTIME_POLICY_APPROVAL_POSTURES,
            "automatic_runtime_policy_recovery_postures": AUTOMATIC_RUNTIME_POLICY_RECOVERY_POSTURES,
            "automatic_runtime_policy_actions": AUTOMATIC_RUNTIME_POLICY_ACTIONS,
            "automatic_runtime_policy_projection_fields": AUTOMATIC_RUNTIME_POLICY_PROJECTION_FIELDS,
            "subgraph_persistence_modes": SUBGRAPH_PERSISTENCE_MODES,
            "subgraph_checkpointer_modes": SUBGRAPH_CHECKPOINTER_MODES,
            "subgraph_state_inspection_scopes": SUBGRAPH_STATE_INSPECTION_SCOPES,
            "subgraph_state_inspection_fields": SUBGRAPH_STATE_INSPECTION_FIELDS,
            "subgraph_state_inspection_projection_fields": SUBGRAPH_STATE_INSPECTION_PROJECTION_FIELDS,
            "generalized_live_routing_identity": GENERALIZED_LIVE_ROUTING_IDENTITY,
            "generalized_live_routing_identity_fields": GENERALIZED_LIVE_ROUTING_IDENTITY_FIELDS,
            "generalized_live_routing_postures": GENERALIZED_LIVE_ROUTING_POSTURES,
            "generalized_live_routing_route_kinds": GENERALIZED_LIVE_ROUTING_ROUTE_KINDS,
            "generalized_live_routing_projection_fields": GENERALIZED_LIVE_ROUTING_PROJECTION_FIELDS,
            "subgraphs": SUBGRAPHS,
            "subgraph_library_fields": SUBGRAPH_LIBRARY_FIELDS,
            "approval_queue_item_fields": APPROVAL_QUEUE_ITEM_FIELDS,
            "approval_queue_item_statuses": APPROVAL_QUEUE_ITEM_STATUSES,
            "approval_queue_postures": APPROVAL_QUEUE_POSTURES,
            "approval_queue_projection_fields": APPROVAL_QUEUE_PROJECTION_FIELDS,
            "migration_projection_fields": MIGRATION_PROJECTION_FIELDS,
            "migration_reason_codes": MIGRATION_REASON_CODES,
            "topology_compatibility_postures": TOPOLOGY_COMPATIBILITY_POSTURES,
            "state_schema_compatibility_postures": STATE_SCHEMA_COMPATIBILITY_POSTURES,
            "thread_compatibility_verdicts": THREAD_COMPATIBILITY_VERDICTS,
            "subgraph_projection_fields": SUBGRAPH_PROJECTION_FIELDS,
            "command_transition_kinds": COMMAND_TRANSITION_KINDS,
            "command_graph_scopes": COMMAND_GRAPH_SCOPES,
            "command_resume_postures": COMMAND_RESUME_POSTURES,
            "command_state_fields": COMMAND_STATE_FIELDS,
            "command_projection_fields": COMMAND_PROJECTION_FIELDS,
            "stream_observability_modes": STREAM_OBSERVABILITY_MODES,
            "stream_event_fields": STREAM_EVENT_FIELDS,
            "stream_projection_fields": STREAM_PROJECTION_FIELDS,
            "runtime_context_fields": RUNTIME_CONTEXT_FIELDS,
            "store_injection_fields": STORE_INJECTION_FIELDS,
            "runtime_injection_projection_fields": RUNTIME_INJECTION_PROJECTION_FIELDS,
            "memory_store_fields": MEMORY_STORE_FIELDS,
            "semantic_memory_fields": SEMANTIC_MEMORY_FIELDS,
            "memory_projection_fields": MEMORY_PROJECTION_FIELDS,
            "implementation_brief_fields": IMPLEMENTATION_BRIEF_FIELDS,
            "survivor_queue_fields": SURVIVOR_QUEUE_FIELDS,
            "interrupt_points": INTERRUPT_POINTS,
            "gate_verdicts": GATE_VERDICTS,
            "loop_capable_flows": LOOP_CAPABLE_FLOWS,
            "loop_projection_fields": LOOP_PROJECTION_FIELDS,
            "history_projection_fields": HISTORY_PROJECTION_FIELDS,
            "history_compatibility_states": HISTORY_COMPATIBILITY_STATES,
            "recovery_postures": RECOVERY_POSTURES,
            "recovery_mutation_intents": RECOVERY_MUTATION_INTENTS,
            "recoverable_thread_fields": RECOVERABLE_THREAD_FIELDS,
            "recoverable_interrupt_fields": RECOVERABLE_INTERRUPT_FIELDS,
            "recovery_projection_fields": RECOVERY_PROJECTION_FIELDS,
            "reducer_merge_channels": REDUCER_MERGE_CHANNELS,
            "single_writer_fields": SINGLE_WRITER_FIELDS,
            "leader_owned_summary_fields": LEADER_OWNED_SUMMARY_FIELDS,
            "reducer_projection_fields": REDUCER_PROJECTION_FIELDS,
            "reducer_compatibility_states": REDUCER_COMPATIBILITY_STATES,
            "thread_id_contract": "<repo-hash>:<worktree-id>:<task-id>",
        },
    }
    if thread_id:
        payload["thread_id"] = thread_id
        payload["thread"] = read_thread_record(repo_root, thread_id)
        payload["checkpoint"] = read_checkpoint(repo_root, thread_id)
        payload["interrupt"] = read_interrupt(repo_root, thread_id)
        payload["implementation_brief"] = read_implementation_brief(repo_root, thread_id)
        payload["survivor_queue"] = read_survivor_queue(repo_root, thread_id)
        payload["release_receipt"] = read_release_receipt(repo_root, thread_id)
        payload["release_projection"] = _release_projection(repo_root, thread_id, payload["thread"])
        payload["loop_projection"] = _loop_projection(payload["thread"])
        payload["reducer_projection"] = _reducer_projection(payload["thread"])
        payload["history_projection"] = _history_projection(
            repo_root,
            thread_id,
            payload["thread"],
            payload["checkpoint"],
            payload["interrupt"],
        )
        payload["recovery_projection"] = _recovery_projection(payload["thread"])
        payload["graph_kernel_projection"] = _graph_kernel_projection(payload["thread"], thread_id)
        payload["primary_runtime_engine_projection"] = _primary_runtime_engine_projection(payload["thread"], thread_id)
        payload["compiled_invocation_projection"] = _compiled_invocation_projection(payload["thread"], thread_id)
        payload["live_execution_projection"] = _live_execution_projection(payload["thread"], thread_id)
        payload["fuller_live_primary_engine_projection"] = _fuller_live_primary_engine_projection(
            payload["thread"], thread_id
        )
        payload["deeper_live_primary_engine_projection"] = _deeper_live_primary_engine_projection(
            payload["thread"], thread_id
        )
        payload["superstep_live_primary_engine_projection"] = _superstep_live_primary_engine_projection(
            payload["thread"], thread_id
        )
        payload["stateful_live_primary_engine_projection"] = _stateful_live_primary_engine_projection(
            payload["thread"], thread_id
        )
        payload["boundary_state_live_primary_engine_projection"] = _boundary_state_live_primary_engine_projection(
            payload["thread"], thread_id
        )
        payload["handoff_state_live_primary_engine_projection"] = _handoff_state_live_primary_engine_projection(
            payload["thread"], thread_id
        )
        payload["approval_aware_live_primary_engine_projection"] = _approval_aware_live_primary_engine_projection(
            payload["thread"], thread_id
        )
        payload["provenance_state_live_primary_engine_projection"] = _provenance_state_live_primary_engine_projection(
            payload["thread"], thread_id
        )
        payload["durable_artifact_aware_live_primary_engine_projection"] = (
            _durable_artifact_aware_live_primary_engine_projection(payload["thread"], thread_id)
        )
        payload["reducer_aware_live_primary_engine_projection"] = _reducer_aware_live_primary_engine_projection(
            payload["thread"], thread_id
        )
        payload["command_aware_live_primary_engine_projection"] = _command_aware_live_primary_engine_projection(
            payload["thread"], thread_id
        )
        payload["runtime_aware_live_primary_engine_projection"] = _runtime_aware_live_primary_engine_projection(
            payload["thread"], thread_id
        )
        payload["memory_aware_live_primary_engine_projection"] = _memory_aware_live_primary_engine_projection(
            payload["thread"], thread_id
        )
        payload["migration_aware_live_primary_engine_projection"] = (
            _migration_aware_live_primary_engine_projection(payload["thread"], thread_id)
        )
        payload["automatic_runtime_policy_projection"] = _automatic_runtime_policy_projection(
            payload["thread"], thread_id
        )
        payload["subgraph_state_inspection_projection"] = _subgraph_state_inspection_projection(
            payload["thread"], thread_id
        )
        payload["generalized_live_routing_projection"] = _generalized_live_routing_projection(
            payload["thread"], thread_id
        )
        payload["approval_queue_projection"] = _approval_queue_projection(payload["thread"], thread_id)
        payload["migration_projection"] = _migration_projection(payload["thread"], thread_id)
        payload["subgraph_projection"] = _subgraph_projection(payload["thread"], thread_id)
        payload["command_projection"] = _command_projection(payload["thread"], thread_id)
        payload["stream_projection"] = _stream_projection(payload["thread"], thread_id)
        payload["runtime_injection_projection"] = _runtime_injection_projection(payload["thread"], thread_id)
        payload["memory_projection"] = _memory_projection(payload["thread"], thread_id)
        payload["implementation_brief_path"] = str(implementation_brief_path(repo_root, thread_id))
        payload["survivor_queue_path"] = str(survivor_queue_path(repo_root, thread_id))
        payload["release_receipt_path"] = str(release_receipt_path(repo_root, thread_id))
        payload["history_path"] = str(history_record_path(repo_root, thread_id))
        payload["durable_artifacts"] = _artifact_presence_summary(repo_root, thread_id)
        payload["helper_pointers"] = _helper_pointers(thread_id)
    _emit(payload)



def cmd_release_thread(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    layout = ensure_layout(repo_root)
    thread = read_thread_record(repo_root, args.thread_id)
    if not thread:
        raise SystemExit(f"Thread not found: {args.thread_id}")
    if args.release_action == "handoff" and (not args.handoff_target or not args.reason):
        raise SystemExit("handoff release requires handoff_target and reason")

    previous_state = _clone_payload(thread)
    previous_status = str(previous_state.get("status", ""))
    checkpoint = read_checkpoint(repo_root, args.thread_id)
    queue = read_survivor_queue(repo_root, args.thread_id)
    now = _now()
    final_phase = args.final_phase or str(thread.get("phase", ""))
    release_status = _release_action_status(args.release_action)
    artifact_path = args.artifact_path or str(implementation_brief_path(repo_root, args.thread_id))
    if not Path(artifact_path).exists():
        artifact_path = str(thread_record_path(repo_root, args.thread_id))

    receipt = {
        "thread_id": args.thread_id,
        "backend_family": "langgraph",
        "previous_state": previous_state,
        "previous_status": previous_status,
        "release_action": args.release_action,
        "released_at": now,
        "released_by": args.released_by,
        "survivor_queue_path": str(survivor_queue_path(repo_root, args.thread_id)),
        "survivor_queue_status": _survivor_queue_status(queue),
        "handoff_target": args.handoff_target or "",
        "reason": args.reason or "",
        "checkpoint_path": str(checkpoint_record_path(repo_root, args.thread_id)),
        "artifact_path": artifact_path,
        "timeout_release": bool(args.timeout_release),
        "rollback_restore_note": args.rollback_restore_note,
        "redaction_status": args.redaction_status,
        "final_phase": final_phase,
        "result_summary": args.result_summary,
    }
    receipt_path = write_release_receipt(repo_root, args.thread_id, receipt)

    thread["status"] = release_status
    thread["phase"] = final_phase or thread.get("phase", "")
    thread["completed_at"] = thread.get("completed_at") or now
    thread["final_phase"] = final_phase
    thread["result_summary"] = args.result_summary
    thread["released_by"] = args.released_by
    thread["released_at"] = now
    thread["release_action"] = args.release_action
    thread["release_receipt_path"] = str(receipt_path)
    thread["timeout_release"] = bool(args.timeout_release)
    thread["rollback_restore_note"] = args.rollback_restore_note
    thread["redaction_status"] = args.redaction_status
    thread["updated_at"] = now
    if args.release_action == "handoff":
        thread["handoff_at"] = now
        thread["handoff_target"] = args.handoff_target
        thread["reason"] = args.reason
    else:
        thread["handoff_target"] = args.handoff_target or ""
        thread["reason"] = args.reason or ""
    _persist_runtime_state_layers(thread)
    write_thread_record(repo_root, thread)
    _append_history_record(repo_root, thread, checkpoint, read_interrupt(repo_root, args.thread_id), "release-thread")
    _save_backend_projection(repo_root, layout, thread)

    _emit(
        {
            "operation": "release-thread",
            "thread_id": args.thread_id,
            "thread": thread,
            "release_receipt": receipt,
            "release_receipt_path": str(receipt_path),
            "release_projection": _release_projection(repo_root, args.thread_id, thread),
            "backend_record": load_backend_record(repo_root),
            "checkpoint": checkpoint,
            "durable_artifacts": _artifact_presence_summary(repo_root, args.thread_id),
        }
    )


def cmd_write_brief(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    frozen_at = _now()
    payload = {
        "brief_id": args.brief_id or _brief_id(args.thread_id),
        "thread_id": args.thread_id,
        "brief_kind": "frozen_implementation_brief",
        "objective": args.objective,
        "non_goals": args.non_goals,
        "accepted_decisions": args.accepted_decisions,
        "constraints": args.constraints,
        "interfaces": args.interfaces,
        "ownership_boundaries": args.ownership_boundaries,
        "acceptance_criteria": args.acceptance_criteria,
        "validation_plan": args.validation_plan,
        "source_evidence_refs": args.source_evidence_refs,
        "frozen_at": frozen_at,
        "updated_at": frozen_at,
    }
    path = write_implementation_brief(repo_root, args.thread_id, payload)
    thread = read_thread_record(repo_root, args.thread_id)
    if thread:
        thread["updated_at"] = _now()
        _persist_durable_artifact_aware_live_primary_engine_state(thread)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)
    else:
        _refresh_backend_artifact_projection(repo_root, args.thread_id)
    _emit(
        {
            "operation": "write-brief",
            "path": str(path),
            "brief": payload,
            "durable_artifacts": _artifact_presence_summary(repo_root, args.thread_id),
        }
    )


def cmd_enqueue_survivor(args: argparse.Namespace) -> None:
    repo_root = resolve_repo_root(args.repo_root)
    queue = read_survivor_queue(repo_root, args.thread_id) or {
        "queue_id": _queue_id(args.thread_id),
        "queue_kind": "judge_approved_survivor_queue",
        "thread_id": args.thread_id,
        "items": [],
    }
    queue["items"].append(
        {
            "bug_id": args.bug_id,
            "title": args.title,
            "severity": args.severity,
            "evidence": args.evidence,
            "judge_verdict": args.judge_verdict,
            "owner_lane": args.owner_lane,
            "status": args.status,
            "verification_result": args.verification_result,
            "updated_at": _now(),
        }
    )
    queue["updated_at"] = _now()
    path = write_survivor_queue(repo_root, args.thread_id, queue)
    thread = read_thread_record(repo_root, args.thread_id)
    if thread:
        thread["updated_at"] = _now()
        _persist_durable_artifact_aware_live_primary_engine_state(thread)
        write_thread_record(repo_root, thread)
        _save_backend_projection(repo_root, ensure_layout(repo_root), thread)
    else:
        _refresh_backend_artifact_projection(repo_root, args.thread_id)
    _emit(
        {
            "operation": "enqueue-survivor",
            "path": str(path),
            "queue": queue,
            "queue_metadata_fields": SURVIVOR_QUEUE_METADATA_FIELDS,
            "durable_artifacts": _artifact_presence_summary(repo_root, args.thread_id),
        }
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LangGraph durable orchestration MVP")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run")
    run.add_argument("--repo-root")
    run.add_argument("--thread-id")
    run.add_argument("--task-id")
    run.add_argument("--worktree-id")
    run.add_argument("--task", required=True)
    run.add_argument("--phase", default="define-target", choices=ROOT_PHASES)
    run.add_argument("--parallel-slices", type=int, default=0)
    run.add_argument("--blocking-issues", type=int, default=0)
    run.add_argument("--loop-kind", choices=sorted(LOOP_CAPABLE_FLOWS.keys()))
    run.add_argument("--iteration-budget", type=int, default=0)
    run.add_argument("--command-kind", choices=COMMAND_TRANSITION_KINDS)
    run.add_argument("--command-goto")
    run.add_argument("--command-graph-scope", choices=COMMAND_GRAPH_SCOPES)
    run.add_argument("--parent-handoff-target")
    run.add_argument("--command-update-json")
    run.add_argument("--command-update-file")
    run.add_argument("--resume-payload-json")
    run.add_argument("--resume-payload-file")
    run.add_argument("--await-command-resume", action="store_true")
    run.add_argument("--context-schema")
    run.add_argument("--runtime-context-json")
    run.add_argument("--runtime-context-file")
    run.add_argument("--store-configured", action="store_true")
    run.add_argument("--store-access-expected", action="store_true")
    run.add_argument("--store-kind")
    run.add_argument("--memory-store-configured", action="store_true")
    run.add_argument("--memory-store-kind")
    run.add_argument("--memory-namespace", action="append", default=[])
    run.add_argument("--semantic-memory-enabled", action="store_true")
    run.add_argument("--semantic-store-kind")
    run.add_argument("--semantic-namespace", action="append", default=[])
    run.add_argument("--thread-graph-contract-id")
    run.add_argument("--thread-topology-version")
    run.add_argument("--thread-state-schema-version")
    run.set_defaults(func=cmd_run)

    status = subparsers.add_parser("status")
    status.add_argument("--repo-root")
    status.add_argument("--thread-id", required=True)
    status.set_defaults(func=cmd_status)

    history = subparsers.add_parser("history")
    history.add_argument("--repo-root")
    history.add_argument("--thread-id", required=True)
    history.set_defaults(func=cmd_history)

    replay = subparsers.add_parser("replay")
    replay.add_argument("--repo-root")
    replay.add_argument("--thread-id", required=True)
    replay.add_argument("--target-id", required=True)
    replay.set_defaults(func=cmd_replay)

    resume = subparsers.add_parser("resume")
    resume.add_argument("--repo-root")
    resume.add_argument("--thread-id", required=True)
    resume.add_argument("--phase", choices=ROOT_PHASES)
    resume.add_argument("--loop-kind", choices=sorted(LOOP_CAPABLE_FLOWS.keys()))
    resume.add_argument("--iteration-budget", type=int, default=0)
    resume.add_argument("--gate-verdict", choices=GATE_VERDICTS)
    resume.add_argument("--gate-reason", default="")
    resume.add_argument("--command-kind", choices=COMMAND_TRANSITION_KINDS)
    resume.add_argument("--command-goto")
    resume.add_argument("--command-graph-scope", choices=COMMAND_GRAPH_SCOPES)
    resume.add_argument("--parent-handoff-target")
    resume.add_argument("--command-update-json")
    resume.add_argument("--command-update-file")
    resume.add_argument("--resume-payload-json")
    resume.add_argument("--resume-payload-file")
    resume.add_argument("--resume-map-json")
    resume.add_argument("--resume-map-file")
    resume.add_argument("--await-command-resume", action="store_true")
    resume.add_argument("--context-schema")
    resume.add_argument("--runtime-context-json")
    resume.add_argument("--runtime-context-file")
    resume.add_argument("--store-configured", action="store_true")
    resume.add_argument("--store-access-expected", action="store_true")
    resume.add_argument("--store-kind")
    resume.add_argument("--memory-store-configured", action="store_true")
    resume.add_argument("--memory-store-kind")
    resume.add_argument("--memory-namespace", action="append", default=[])
    resume.add_argument("--semantic-memory-enabled", action="store_true")
    resume.add_argument("--semantic-store-kind")
    resume.add_argument("--semantic-namespace", action="append", default=[])
    resume.set_defaults(func=cmd_resume)

    recover = subparsers.add_parser("recover")
    recover.add_argument("--repo-root")
    recover.add_argument("--thread-id", required=True)
    recover.add_argument("--mutation-intent", required=True, choices=RECOVERY_MUTATION_INTENTS)
    recover.add_argument("--target-id")
    recover.add_argument("--thread-field", action="append", default=[])
    recover.add_argument("--interrupt-field", action="append", default=[])
    recover.add_argument("--clear-interrupt", action="store_true")
    recover.set_defaults(func=cmd_recover)

    merge_branch = subparsers.add_parser("merge-branch")
    merge_branch.add_argument("--repo-root")
    merge_branch.add_argument("--thread-id", required=True)
    payload_group = merge_branch.add_mutually_exclusive_group(required=True)
    payload_group.add_argument("--payload-json")
    payload_group.add_argument("--payload-file", type=argparse.FileType("r", encoding="utf-8"))
    merge_branch.set_defaults(func=cmd_merge_branch)

    inspect = subparsers.add_parser("inspect")
    inspect.add_argument("--repo-root")
    inspect.add_argument("--thread-id")
    inspect.set_defaults(func=cmd_inspect)

    migration = subparsers.add_parser("migration")
    migration.add_argument("--repo-root")
    migration.add_argument("--thread-id", required=True)
    migration.add_argument("--current-graph-contract-id")
    migration.add_argument("--current-topology-version")
    migration.add_argument("--current-state-schema-version")
    migration.set_defaults(func=cmd_migration)

    kernel = subparsers.add_parser("kernel")
    kernel.add_argument("--repo-root")
    kernel.add_argument("--thread-id", required=True)
    kernel.set_defaults(func=cmd_kernel)

    engine = subparsers.add_parser("engine")
    engine.add_argument("--repo-root")
    engine.add_argument("--thread-id", required=True)
    engine.set_defaults(func=cmd_engine)

    invocation = subparsers.add_parser("invocation")
    invocation.add_argument("--repo-root")
    invocation.add_argument("--thread-id", required=True)
    invocation.add_argument("--invoke-kind", choices=COMPILED_INVOCATION_RUN_KINDS)
    invocation.set_defaults(func=cmd_invocation)

    live_execution = subparsers.add_parser("live-execution")
    live_execution.add_argument("--repo-root")
    live_execution.add_argument("--thread-id", required=True)
    live_execution.add_argument("--run-kind", choices=LIVE_EXECUTION_RUN_KINDS)
    live_execution.set_defaults(func=cmd_live_execution)

    fuller_engine = subparsers.add_parser("fuller-engine")
    fuller_engine.add_argument("--repo-root")
    fuller_engine.add_argument("--thread-id", required=True)
    fuller_engine.add_argument("--run-kind", choices=FULLER_LIVE_PRIMARY_ENGINE_RUN_KINDS)
    fuller_engine.set_defaults(func=cmd_fuller_engine)

    deeper_engine = subparsers.add_parser("deeper-engine")
    deeper_engine.add_argument("--repo-root")
    deeper_engine.add_argument("--thread-id", required=True)
    deeper_engine.add_argument("--run-kind", choices=DEEPER_LIVE_PRIMARY_ENGINE_RUN_KINDS)
    deeper_engine.add_argument("--recursion-limit", type=int, default=8)
    deeper_engine.set_defaults(func=cmd_deeper_engine)

    superstep_engine = subparsers.add_parser("superstep-engine")
    superstep_engine.add_argument("--repo-root")
    superstep_engine.add_argument("--thread-id", required=True)
    superstep_engine.add_argument("--run-kind", choices=SUPERSTEP_LIVE_PRIMARY_ENGINE_RUN_KINDS)
    superstep_engine.add_argument("--recursion-limit", type=int, default=8)
    superstep_engine.set_defaults(func=cmd_superstep_engine)

    stateful_engine = subparsers.add_parser("stateful-engine")
    stateful_engine.add_argument("--repo-root")
    stateful_engine.add_argument("--thread-id", required=True)
    stateful_engine.add_argument("--run-kind", choices=STATEFUL_LIVE_PRIMARY_ENGINE_RUN_KINDS)
    stateful_engine.add_argument("--recursion-limit", type=int, default=8)
    stateful_engine.set_defaults(func=cmd_stateful_engine)

    boundary_engine = subparsers.add_parser("boundary-engine")
    boundary_engine.add_argument("--repo-root")
    boundary_engine.add_argument("--thread-id", required=True)
    boundary_engine.add_argument("--run-kind", choices=BOUNDARY_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS)
    boundary_engine.add_argument("--recursion-limit", type=int, default=8)
    boundary_engine.set_defaults(func=cmd_boundary_engine)

    handoff_engine = subparsers.add_parser("handoff-engine")
    handoff_engine.add_argument("--repo-root")
    handoff_engine.add_argument("--thread-id", required=True)
    handoff_engine.add_argument("--run-kind", choices=HANDOFF_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS)
    handoff_engine.add_argument("--recursion-limit", type=int, default=8)
    handoff_engine.set_defaults(func=cmd_handoff_engine)

    approval_engine = subparsers.add_parser("approval-engine")
    approval_engine.add_argument("--repo-root")
    approval_engine.add_argument("--thread-id", required=True)
    approval_engine.add_argument("--run-kind", choices=APPROVAL_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS)
    approval_engine.add_argument("--recursion-limit", type=int, default=8)
    approval_engine.set_defaults(func=cmd_approval_engine)

    provenance_engine = subparsers.add_parser("provenance-engine")
    provenance_engine.add_argument("--repo-root")
    provenance_engine.add_argument("--thread-id", required=True)
    provenance_engine.add_argument("--run-kind", choices=PROVENANCE_STATE_LIVE_PRIMARY_ENGINE_RUN_KINDS)
    provenance_engine.add_argument("--recursion-limit", type=int, default=8)
    provenance_engine.set_defaults(func=cmd_provenance_engine)

    artifact_engine = subparsers.add_parser("artifact-engine")
    artifact_engine.add_argument("--repo-root")
    artifact_engine.add_argument("--thread-id", required=True)
    artifact_engine.add_argument("--run-kind", choices=DURABLE_ARTIFACT_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS)
    artifact_engine.add_argument("--recursion-limit", type=int, default=8)
    artifact_engine.set_defaults(func=cmd_artifact_engine)

    reducer_engine = subparsers.add_parser("reducer-engine")
    reducer_engine.add_argument("--repo-root")
    reducer_engine.add_argument("--thread-id", required=True)
    reducer_engine.add_argument("--run-kind", choices=REDUCER_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS)
    reducer_engine.add_argument("--recursion-limit", type=int, default=8)
    reducer_engine.set_defaults(func=cmd_reducer_engine)

    command_engine = subparsers.add_parser("command-engine")
    command_engine.add_argument("--repo-root")
    command_engine.add_argument("--thread-id", required=True)
    command_engine.add_argument("--run-kind", choices=COMMAND_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS)
    command_engine.add_argument("--recursion-limit", type=int, default=8)
    command_engine.set_defaults(func=cmd_command_engine)

    runtime_engine = subparsers.add_parser("runtime-engine")
    runtime_engine.add_argument("--repo-root")
    runtime_engine.add_argument("--thread-id", required=True)
    runtime_engine.add_argument("--run-kind", choices=RUNTIME_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS)
    runtime_engine.add_argument("--recursion-limit", type=int, default=8)
    runtime_engine.set_defaults(func=cmd_runtime_engine)

    memory_engine = subparsers.add_parser("memory-engine")
    memory_engine.add_argument("--repo-root")
    memory_engine.add_argument("--thread-id", required=True)
    memory_engine.add_argument("--run-kind", choices=MEMORY_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS)
    memory_engine.add_argument("--recursion-limit", type=int, default=8)
    memory_engine.set_defaults(func=cmd_memory_engine)

    migration_engine = subparsers.add_parser("migration-engine")
    migration_engine.add_argument("--repo-root")
    migration_engine.add_argument("--thread-id", required=True)
    migration_engine.add_argument("--run-kind", choices=MIGRATION_AWARE_LIVE_PRIMARY_ENGINE_RUN_KINDS)
    migration_engine.add_argument("--recursion-limit", type=int, default=8)
    migration_engine.set_defaults(func=cmd_migration_engine)

    auto_policy = subparsers.add_parser("auto-policy")
    auto_policy.add_argument("--repo-root")
    auto_policy.add_argument("--thread-id", required=True)
    auto_policy.add_argument("--apply", action="store_true")
    auto_policy.set_defaults(func=cmd_auto_policy)

    subgraph_state = subparsers.add_parser("subgraph-state")
    subgraph_state.add_argument("--repo-root")
    subgraph_state.add_argument("--thread-id", required=True)
    subgraph_state.set_defaults(func=cmd_subgraph_state)

    generalized_routing = subparsers.add_parser("generalized-routing")
    generalized_routing.add_argument("--repo-root")
    generalized_routing.add_argument("--thread-id", required=True)
    generalized_routing.set_defaults(func=cmd_generalized_routing)

    approval_queue = subparsers.add_parser("approval-queue")
    approval_queue.add_argument("--repo-root")
    approval_queue.add_argument("--thread-id", required=True)
    approval_queue.add_argument("--interrupt-item-json", action="append", default=[])
    approval_queue.add_argument("--interrupt-item-file", action="append", default=[])
    approval_queue.add_argument("--default-interrupt-point", default="")
    approval_queue.add_argument("--default-reason", default="")
    approval_queue.add_argument("--resume-map-json")
    approval_queue.add_argument("--resume-map-file")
    approval_queue.add_argument("--clear-queue", action="store_true")
    approval_queue.set_defaults(func=cmd_approval_queue)

    subgraphs = subparsers.add_parser("subgraphs")
    subgraphs.add_argument("--repo-root")
    subgraphs.add_argument("--thread-id")
    subgraphs.set_defaults(func=cmd_subgraphs)

    stream = subparsers.add_parser("stream")
    stream.add_argument("--repo-root")
    stream.add_argument("--thread-id", required=True)
    stream.add_argument("--stream-mode", action="append", choices=STREAM_OBSERVABILITY_MODES, default=[])
    stream.add_argument("--subgraphs", action="store_true")
    stream.add_argument("--event-kind", choices=STREAM_OBSERVABILITY_MODES)
    stream.add_argument("--namespace", action="append", default=[])
    stream.add_argument("--checkpoint-kind", default="")
    stream.add_argument("--task-path", default="")
    stream.add_argument("--task-status", default="")
    stream.add_argument("--debug-summary", default="")
    stream.set_defaults(func=cmd_stream)

    runtime = subparsers.add_parser("runtime")
    runtime.add_argument("--repo-root")
    runtime.add_argument("--thread-id", required=True)
    runtime.add_argument("--context-schema")
    runtime.add_argument("--runtime-context-json")
    runtime.add_argument("--runtime-context-file")
    runtime.add_argument("--store-configured", action="store_true")
    runtime.add_argument("--store-access-expected", action="store_true")
    runtime.add_argument("--store-kind")
    runtime.set_defaults(func=cmd_runtime)

    memory = subparsers.add_parser("memory")
    memory.add_argument("--repo-root")
    memory.add_argument("--thread-id", required=True)
    memory.add_argument("--memory-store-configured", action="store_true")
    memory.add_argument("--memory-store-kind")
    memory.add_argument("--memory-namespace", action="append", default=[])
    memory.add_argument("--semantic-memory-enabled", action="store_true")
    memory.add_argument("--semantic-store-kind")
    memory.add_argument("--semantic-namespace", action="append", default=[])
    memory.set_defaults(func=cmd_memory)

    release = subparsers.add_parser("release-thread")
    release.add_argument("--repo-root")
    release.add_argument("--thread-id", required=True)
    release.add_argument("--release-action", required=True, choices=["close", "release", "handoff"])
    release.add_argument("--released-by", required=True)
    release.add_argument("--final-phase", default="")
    release.add_argument("--result-summary", default="")
    release.add_argument("--handoff-target", default="")
    release.add_argument("--reason", default="")
    release.add_argument("--timeout-release", action="store_true")
    release.add_argument("--rollback-restore-note", default="")
    release.add_argument("--redaction-status", default="unreviewed")
    release.add_argument("--artifact-path", default="")
    release.set_defaults(func=cmd_release_thread)

    brief = subparsers.add_parser("write-brief")
    brief.add_argument("--repo-root")
    brief.add_argument("--thread-id", required=True)
    brief.add_argument("--brief-id")
    brief.add_argument("--objective", default="")
    brief.add_argument("--non-goals", nargs="*", default=[])
    brief.add_argument("--accepted-decisions", nargs="*", default=[])
    brief.add_argument("--constraints", nargs="*", default=[])
    brief.add_argument("--interfaces", nargs="*", default=[])
    brief.add_argument("--ownership-boundaries", nargs="*", default=[])
    brief.add_argument("--acceptance-criteria", nargs="*", default=[])
    brief.add_argument("--validation-plan", nargs="*", default=[])
    brief.add_argument("--source-evidence-refs", nargs="*", default=[])
    brief.set_defaults(func=cmd_write_brief)

    survivor = subparsers.add_parser("enqueue-survivor")
    survivor.add_argument("--repo-root")
    survivor.add_argument("--thread-id", required=True)
    survivor.add_argument("--bug-id", required=True)
    survivor.add_argument("--title", required=True)
    survivor.add_argument("--severity", default="medium")
    survivor.add_argument("--evidence", default="")
    survivor.add_argument("--judge-verdict", default="survives")
    survivor.add_argument("--owner-lane", default="debugger")
    survivor.add_argument("--status", default="queued")
    survivor.add_argument("--verification-result", default="")
    survivor.set_defaults(func=cmd_enqueue_survivor)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
