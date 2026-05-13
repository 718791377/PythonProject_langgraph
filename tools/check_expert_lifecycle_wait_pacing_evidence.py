#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "expert_lifecycle_wait_pacing_evidence"

COMPLETED_MARKERS = (
    "expert returned and absorbed",
    "expert result absorbed",
    "completed expert",
    "agent completed",
    "expert completed",
    "absorbed expert",
    "专家返回并吸收",
    "专家已返回并吸收",
    "已吸收专家结果",
)

CLOSURE_MARKERS = (
    "close_agent",
    "agent closed",
    "closed agent",
    "thread closed",
    "completed agent closed",
    "closed after absorption",
    "关闭 agent",
    "已关闭 agent",
    "关闭线程",
    "吸收后关闭",
)

PRESERVED_MARKERS = (
    "preserved-thread reason",
    "preserved thread reason",
    "explicitly preserved",
    "user explicitly asked to preserve",
    "preserve thread",
    "preserved by request",
    "保留线程原因",
    "显式保留",
    "用户明确要求保留",
)

FOLLOW_UP_MARKERS = (
    "follow-up",
    "follow up",
    "later work",
    "subsequent work",
    "后续工作",
    "后续 follow-up",
)

FRESH_AGENT_MARKERS = (
    "fresh agent",
    "spawn fresh",
    "spawned fresh",
    "new agent",
    "fresh expert",
    "新开 expert",
    "新建 agent",
    "重新 spawn",
)

WAIT_MARKERS = (
    "wait_agent",
    "waited",
    "wait window",
    "bounded wait",
    "progress check",
    "liveness check",
    "等待 expert",
    "有界等待",
    "进展检查",
    "活性检查",
)

BOUNDED_WAIT_MARKERS = (
    "bounded wait",
    "wait window",
    "30s",
    "60s",
    "120s",
    "180s",
    "timeout_ms",
    "total wait bound",
    "total wait bounded",
    "bounded dynamic windows",
    "有界等待",
    "等待窗口",
    "总等待上限",
)

TOTAL_BOUND_MARKERS = (
    "total wait bound",
    "total wait bounded",
    "total_wait_bound",
    "total wait <=",
    "about 180s",
    "180s total",
    "180 seconds",
    "max 180s",
    "总等待上限",
    "总等待不超过",
)

INDEFINITE_WAIT_MARKERS = (
    "wait indefinitely",
    "blocked indefinitely",
    "keep waiting forever",
    "silent wait",
    "wait silently forever",
    "unbounded wait",
    "无限等待",
    "一直等",
    "静默等待",
    "无界等待",
)

STALL_MARKERS = (
    "stalled",
    "stall",
    "quiet progress checks",
    "two consecutive progress checks",
    "2 consecutive progress checks",
    "liveness quiet",
    "卡住",
    "停滞",
    "连续两次",
)

STALL_ACTION_MARKERS = (
    "inspect",
    "redirect",
    "respawn",
    "durable handoff",
    "durable lane",
    "main session took over",
    "main-session takeover",
    "main session takeover",
    "main session took over verification",
    "narrower expert",
    "recorded takeover",
    "检查",
    "重定向",
    "重新派生",
    "重新启动",
    "接管",
    "主会话接管",
    "durable 接管",
)

PACING_MARKERS = (
    "provider pacing",
    "upstream pacing",
    "upstream provider",
    "shared upstream pacing",
    "pacing budget",
    "provider budget",
    "upstream-bound requests",
    "上游节奏",
    "上游 pacing",
    "供应商 pacing",
)

BACKPRESSURE_MARKERS = (
    "backpressure",
    "back pressure",
    "bounded fan-out",
    "local-first",
    "wait for a slot",
    "等待 slot",
    "背压",
    "有界 fan-out",
    "本地优先",
)

PACING_DISABLEMENT_PATTERNS = (
    re.compile(
        r"pacing[^\n.]{0,80}(disable|disabled|avoid|skip|forbid|not use)[^\n.]{0,80}"
        r"(orchestration|langgraph|omx|subagent|expert)",
        re.IGNORECASE,
    ),
    re.compile(
        r"(disable|disabled|avoid|skip|forbid|not use)[^\n.]{0,80}"
        r"(orchestration|langgraph|omx|subagent|expert)[^\n.]{0,80}pacing",
        re.IGNORECASE,
    ),
    re.compile(
        r"(because|due to)[^\n.]{0,80}pacing[^\n.]{0,80}(do not|don't|cannot|can't)"
        r"[^\n.]{0,80}(orchestrate|use langgraph|use omx|spawn)",
        re.IGNORECASE,
    ),
    re.compile(
        r"因为[^\n。]{0,40}pacing[^\n。]{0,80}(禁用|不使用|跳过)[^\n。]{0,40}"
        r"(编排|LangGraph|OMX|subagent|expert)",
        re.IGNORECASE,
    ),
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


def contains_any(text: str, markers: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(marker.lower() in lowered for marker in markers)


def matches_any(text: str, patterns: tuple[re.Pattern[str], ...]) -> bool:
    return any(pattern.search(text) for pattern in patterns)


def run_check(evidence_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []
    detected: list[str] = []

    text = read_text(evidence_path)
    if text is None:
        errors.append(f"Missing or unreadable expert lifecycle/wait/pacing evidence file: {evidence_path}")
        text = ""

    has_completed = contains_any(text, COMPLETED_MARKERS)
    has_closure = contains_any(text, CLOSURE_MARKERS)
    has_preserved = contains_any(text, PRESERVED_MARKERS)
    has_follow_up = contains_any(text, FOLLOW_UP_MARKERS)
    has_fresh_agent = contains_any(text, FRESH_AGENT_MARKERS)
    has_wait = contains_any(text, WAIT_MARKERS)
    has_bounded_wait = contains_any(text, BOUNDED_WAIT_MARKERS)
    has_total_bound = contains_any(text, TOTAL_BOUND_MARKERS)
    has_indefinite_wait = contains_any(text, INDEFINITE_WAIT_MARKERS)
    has_stall = contains_any(text, STALL_MARKERS)
    has_stall_action = contains_any(text, STALL_ACTION_MARKERS)
    has_pacing = contains_any(text, PACING_MARKERS)
    has_backpressure = contains_any(text, BACKPRESSURE_MARKERS)
    has_pacing_disablement = matches_any(text, PACING_DISABLEMENT_PATTERNS)

    if has_completed:
        detected.append("completed_expert")
        if not (has_closure or has_preserved):
            errors.append(
                "Completed expert evidence must show completed-agent closure after absorption "
                "or an explicit preserved-thread reason."
            )

    if has_follow_up:
        detected.append("follow_up")
        if not (has_fresh_agent or has_preserved):
            errors.append(
                "Follow-up expert work must use a fresh agent unless an explicit preserved-thread reason is recorded."
            )

    if has_wait:
        detected.append("wait")
        if has_indefinite_wait:
            errors.append("Wait evidence must not describe indefinite, silent, or unbounded waiting.")
        if not has_bounded_wait:
            errors.append("Wait evidence must include bounded wait windows such as 30s/60s/120s or bounded wait wording.")
        if not has_total_bound:
            errors.append("Wait evidence must include a total wait bound such as about 180s or an equivalent total bound.")

    if has_stall:
        detected.append("stall")
        if not has_stall_action:
            errors.append(
                "Stall or quiet-progress evidence must name a handling action such as inspect, redirect, respawn, "
                "durable handoff, or main-session takeover."
            )

    if has_pacing:
        detected.append("provider_pacing")
        if has_pacing_disablement:
            errors.append(
                "Provider/upstream pacing must be treated as backpressure, not as a reason to disable orchestration, "
                "LangGraph, OMX, subagents, or experts."
            )
        if not has_backpressure:
            errors.append("Provider/upstream pacing evidence must label pacing as backpressure or local-first bounded fan-out.")

    if not errors:
        if detected:
            info.append("Expert lifecycle, wait, and pacing evidence labels are acceptable.")
        else:
            warnings.append("No expert lifecycle, wait, stall, or provider pacing markers were detected in the evidence file.")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "evidence_path": str(evidence_path),
        "detected": detected,
        "errors": errors,
        "warnings": warnings,
        "info": info,
        "counts": {"detected": len(detected), "errors": len(errors), "warnings": len(warnings)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate saved expert lifecycle, wait, liveness, and provider pacing evidence."
    )
    parser.add_argument("--evidence", required=True, help="Path to a saved evidence text file.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = run_check(Path(args.evidence))
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
