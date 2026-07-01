#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "orchestration_trace_evidence"

REQUIRED_FIELDS = (
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

FIELD_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_])("
    + "|".join(re.escape(field) for field in REQUIRED_FIELDS)
    + r")\s*=",
    re.IGNORECASE,
)

CAPABILITY_CHAIN_PATTERN = re.compile(
    r"(?:subagent|subagent_routing):(?P<subagent>auto|manual|off)\s*>\s*"
    r"(?:omx|oh_my_codex):(?P<omx>on|off)\s*>\s*"
    r"langgraph:(?P<langgraph>on|off)",
    re.IGNORECASE,
)
LABEL_PREFIX_CHARS = r"\s*(?:[\u2022\u2514\u251c\u2502>+\-*]+\s*)*"
ROUTING_TRACE_LABEL_PATTERN = re.compile(rf"(?im)^{LABEL_PREFIX_CHARS}Routing trace\b")
LEGACY_SHORT_FIELD_PATTERN = re.compile(r"(?<![A-Za-z0-9_])(experts_now|durable_team)\s*=", re.IGNORECASE)

BACKEND_DEFAULT_VALUES = {"langgraph", "native_omx", "none"}
BOOLEAN_VALUES = {"true", "false"}
LANE_STATE_VALUES = {"not_needed", "candidate", "selected", "blocked", "running", "complete"}
MAIN_SESSION_ESCALATION_VALUES = {
    "not_needed",
    "preflight",
    "pending_approval",
    "granted",
    "timed_out",
    "blocked",
}
APPROVAL_TIMEOUT_RISK_VALUES = {"none", "low", "medium", "high", "expired"}
NO_APPROVAL_RECEIPT_VALUES = {"", "none", "not_needed", "n/a", "na", "-"}

PENDING_APPROVAL_MARKERS = (
    "pending approval",
    "approval pending",
    "pending_approval",
    "approval_wait",
    "waiting_for_approval",
    "human_approval_required",
    "needs_human",
    "awaiting_manual_approval",
)

APPROVAL_TIMEOUT_MARKERS = (
    "approval timeout",
    "approval timed out",
    "approval_timeout",
    "approval_timed_out",
    "timed_out",
    "expired",
)

UNMET_THRESHOLD_MARKERS = (
    "threshold_not_met:",
    "threshold not met",
    "unmet threshold",
    "no_frozen_plan",
    "single_execution_slice",
    "single execution slice",
    "read-context",
    "freeze-plan",
    "verify-accept",
    "未满足阈值",
    "阈值未满足",
    "无冻结计划",
    "单切片",
)

BLOCKER_MARKERS = (
    "blocked:",
    "blocked by",
    "blocker",
    "backend_not_ready",
    "preflight_failed",
    "helper_missing",
    "write_ownership_conflict",
    "被阻塞",
    "阻塞",
)

TRIGGERED_THRESHOLD_MARKERS = (
    "triggered_threshold:",
    "threshold_triggered:",
    "threshold_met:",
    "triggered threshold",
    "threshold triggered",
    "threshold met",
    "frozen plan",
    "2+ independent execution slices",
    "two or more independent execution slices",
    "parallel slices",
    "execute-parallel",
    "integrate-converge",
    "stabilize",
    "blocking issues",
    "触发阈值",
    "阈值已满足",
    "已冻结计划",
    "两个以上独立执行切片",
    "2+ 独立执行切片",
    "阻塞问题",
)

FORBIDDEN_MISSING_REMINDER_REASONS = (
    "the user did not request parallelism",
    "the user did not request subagents",
    "user did not request parallelism",
    "user did not request subagents",
    "user did not ask for parallelism",
    "user did not ask for subagents",
    "用户没有要求并行",
    "用户没要求并行",
    "用户没有要求子代理",
    "用户没要求子代理",
    "用户没有要求 subagent",
    "用户没要求 subagent",
)

TIMEOUT_TRIGGERS = (
    "expert timeout",
    "expert timed out",
    "subagent timeout",
    "subagent timed out",
    "worker timeout",
    "worker timed out",
    "expert stalled",
    "subagent stalled",
    "worker stalled",
    "expert 超时",
    "subagent 超时",
    "worker 超时",
    "专家超时",
    "子代理超时",
)

TIMEOUT_ALLOWED_LABELS = (
    "expert timed out; not used as evidence",
    "expert timed out; not used as verification evidence",
    "not used as evidence",
    "not verification evidence",
    "main session took over verification",
    "main-session takeover",
    "main session takeover",
    "bounded wait",
    "respawn",
    "durable handoff",
    "durable lane",
    "not used as evidence",
    "不是验证证据",
    "不作为证据",
    "主会话接管",
    "有界等待",
    "重新派生",
    "重新启动 expert",
    "durable 接管",
)


def read_text(path: Path) -> str | None:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None
    return None


def parse_trace_fields(text: str) -> dict[str, str]:
    matches = list(FIELD_PATTERN.finditer(text))
    fields: dict[str, str] = {}
    for index, match in enumerate(matches):
        field = match.group(1).lower()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        value = text[start:end].strip()
        value = value.strip(" \t\r\n,;")
        fields[field] = value
    return fields


def parse_capability_chain(value: str) -> dict[str, str] | None:
    match = CAPABILITY_CHAIN_PATTERN.search(value)
    if not match:
        return None
    return {key: match.group(key).lower() for key in ("subagent", "omx", "langgraph")}


def contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(needle.lower() in lowered for needle in needles)


def validate_fields(fields: dict[str, str], full_text: str) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for field in REQUIRED_FIELDS:
        value = fields.get(field)
        if value is None:
            errors.append(f"Missing required activation trace field: {field}")
        elif not value.strip():
            errors.append(f"Activation trace field `{field}` must not be empty.")

    if errors:
        return errors, warnings

    capability_chain = parse_capability_chain(fields["capability_chain"])
    if capability_chain is None:
        errors.append(
            "capability_chain must use `subagent_routing:<auto|manual|off> > oh_my_codex:<on|off> > langgraph:<on|off>` or the accepted `subagent`/`omx` aliases."
        )
    else:
        subagent = capability_chain["subagent"]
        omx = capability_chain["omx"]
        langgraph = capability_chain["langgraph"]
        if subagent == "off" and (omx != "off" or langgraph != "off"):
            errors.append("capability_chain is inconsistent: subagent:off requires omx:off and langgraph:off.")
        if omx == "off" and langgraph != "off":
            errors.append("capability_chain is inconsistent: omx:off requires langgraph:off.")
        if langgraph == "on" and (subagent == "off" or omx != "on"):
            errors.append("capability_chain is inconsistent: langgraph:on requires subagent routing and omx:on.")

    backend_default = fields["backend_default"].lower()
    if backend_default not in BACKEND_DEFAULT_VALUES:
        errors.append(
            "backend_default must be one of: "
            + ", ".join(sorted(BACKEND_DEFAULT_VALUES))
            + "."
        )

    backend_ready = fields["backend_ready"].lower()
    if backend_ready not in BOOLEAN_VALUES:
        errors.append("backend_ready must be `true` or `false`.")

    if capability_chain is not None:
        if backend_default == "langgraph" and capability_chain["langgraph"] != "on":
            errors.append("backend_default=langgraph requires langgraph:on in capability_chain.")
        if (
            capability_chain["subagent"] != "off"
            and capability_chain["omx"] == "on"
            and capability_chain["langgraph"] == "on"
            and backend_ready == "true"
            and backend_default != "langgraph"
        ):
            errors.append(
                "When subagent routing, omx, and LangGraph are enabled and backend_ready=true, "
                "backend_default must be langgraph."
            )

    for field in ("durable_workflow", "persistent_team"):
        value = fields[field].lower()
        if value not in LANE_STATE_VALUES:
            errors.append(
                f"{field} must be one of: " + ", ".join(sorted(LANE_STATE_VALUES)) + "."
            )

    main_session_escalation = fields["main_session_escalation"].lower()
    if main_session_escalation not in MAIN_SESSION_ESCALATION_VALUES:
        errors.append(
            "main_session_escalation must be one of: "
            + ", ".join(sorted(MAIN_SESSION_ESCALATION_VALUES))
            + "."
        )

    approval_timeout_risk = fields["approval_timeout_risk"].lower()
    if approval_timeout_risk not in APPROVAL_TIMEOUT_RISK_VALUES:
        errors.append(
            "approval_timeout_risk must be one of: "
            + ", ".join(sorted(APPROVAL_TIMEOUT_RISK_VALUES))
            + "."
        )

    approval_receipt = fields["approval_receipt"].strip()
    receipt_missing = approval_receipt.lower() in NO_APPROVAL_RECEIPT_VALUES

    why = fields["why"].strip()
    if why in {"...", "<concrete reason>", "<reason>", "todo", "tbd"}:
        errors.append("why must contain a concrete reason, not a placeholder.")

    why_and_text = f"{why}\n{full_text}"
    if contains_any(why_and_text, FORBIDDEN_MISSING_REMINDER_REASONS):
        errors.append(
            "Activation trace must not cite missing user reminders such as not requesting parallelism or subagents."
        )

    if main_session_escalation == "not_needed":
        if approval_timeout_risk != "none":
            errors.append("main_session_escalation=not_needed requires approval_timeout_risk=none.")
        if not receipt_missing:
            errors.append("main_session_escalation=not_needed requires approval_receipt=none.")
    elif main_session_escalation in {"pending_approval", "granted", "timed_out", "blocked"} and receipt_missing:
        errors.append(f"main_session_escalation={main_session_escalation} requires a visible approval_receipt.")

    if main_session_escalation == "pending_approval" and approval_timeout_risk in {"none", "expired"}:
        errors.append("main_session_escalation=pending_approval requires approval_timeout_risk=low, medium, or high.")

    if approval_timeout_risk == "expired" and main_session_escalation not in {"timed_out", "blocked"}:
        errors.append("approval_timeout_risk=expired requires main_session_escalation=timed_out or blocked.")

    if main_session_escalation in {"timed_out", "blocked"} and not contains_any(
        why,
        BLOCKER_MARKERS + APPROVAL_TIMEOUT_MARKERS + ("human_approval_required",),
    ):
        errors.append(
            f"main_session_escalation={main_session_escalation} must cite a named blocker or approval timeout in why."
        )

    if contains_any(full_text, PENDING_APPROVAL_MARKERS) and main_session_escalation == "not_needed":
        errors.append(
            "Pending approval or approval-wait language must be visible through main_session_escalation, "
            "approval_timeout_risk, and approval_receipt fields."
        )

    for field in ("durable_workflow", "persistent_team"):
        value = fields[field].lower()
        if value == "not_needed" and not contains_any(why, UNMET_THRESHOLD_MARKERS):
            errors.append(
                f"{field}=not_needed must cite a concrete unmet threshold such as "
                "`threshold_not_met:no_frozen_plan` or `threshold_not_met:single_execution_slice`."
            )
        elif value == "blocked" and not contains_any(why, UNMET_THRESHOLD_MARKERS + BLOCKER_MARKERS):
            errors.append(
                f"{field}=blocked must cite a named blocker or unmet threshold such as "
                "`blocked:preflight_failed` or `threshold_not_met:no_frozen_plan`."
            )
        elif value in {"selected", "running"} and not contains_any(why, TRIGGERED_THRESHOLD_MARKERS):
            errors.append(
                f"{field}={value} must cite the concrete triggered threshold such as "
                "`triggered_threshold:frozen_plan_with_2+_independent_slices` or a stabilization blocker trigger."
            )

    if contains_any(full_text, TIMEOUT_TRIGGERS) and not contains_any(full_text, TIMEOUT_ALLOWED_LABELS):
        errors.append(
            "Expert/subagent timeout or stall language must be labeled as non-evidence, bounded wait, respawn, "
            "durable handoff, or main-session takeover."
        )

    return errors, warnings


def run_check(trace_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    text = read_text(trace_path)
    if text is None:
        errors.append(f"Missing or unreadable activation trace evidence file: {trace_path}")
        fields: dict[str, str] = {}
    else:
        label_count = len(ROUTING_TRACE_LABEL_PATTERN.findall(text))
        if label_count == 0:
            errors.append("Activation trace evidence must include the literal `Routing trace` label.")
        elif label_count > 1:
            errors.append("Activation trace evidence must include exactly one `Routing trace` label, not duplicate trace panels.")
        legacy_fields = sorted({match.group(1).lower() for match in LEGACY_SHORT_FIELD_PATTERN.finditer(text)})
        for legacy_field in legacy_fields:
            errors.append(f"Activation trace evidence must not use legacy short field `{legacy_field}=...`.")
        fields = parse_trace_fields(text)
        field_errors, field_warnings = validate_fields(fields, text)
        errors.extend(field_errors)
        warnings.extend(field_warnings)

    if not errors:
        info.append("Activation trace evidence satisfies required orchestration fields and evidence labels.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "trace_path": str(trace_path),
        "fields": fields,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {
            "fields": len(fields),
            "errors": len(errors),
            "warnings": len(warnings),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate saved orchestration activation trace evidence.")
    parser.add_argument("--trace", required=True, help="Path to a saved activation trace text file.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = run_check(Path(args.trace))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for message in payload["info"]:
            print(message)
        for message in payload["warnings"]:
            print(f"WARNING: {message}")
        for message in payload["errors"]:
            print(f"ERROR: {message}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
