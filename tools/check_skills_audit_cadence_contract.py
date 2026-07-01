#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "skills_audit_cadence_contract"

PLAN_EN = Path("docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md")
PLAN_ZH = Path("docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md")
FINAL_SUMMARY = Path("docs_bilingual/memory/skills_usage_audit_30d_summary_2026-06-15-1059.md")
MEMORY_DIR = Path("docs_bilingual/memory")

WINDOW_START = "2026-05-16"
WINDOW_END = "2026-06-15"
SCHEDULED_TOTAL_RUNS = 6
BASELINE_RUNS = 1
WEEKLY_RUNS = 4
FINAL_RUNS = 1
WEEKLY_DATES = ("2026-05-23", "2026-05-30", "2026-06-06", "2026-06-13")


def norm(path: Path | str) -> str:
    return str(path).replace("\\", "/")


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def latest_path(root: Path, pattern: str) -> Path | None:
    candidates = [
        path
        for path in (root / MEMORY_DIR).glob(pattern)
        if not path.name.endswith(".zh-CN.md")
    ]
    return sorted(candidates, key=lambda item: item.name)[-1] if candidates else None


def has_regex(text: str, pattern: str) -> bool:
    return re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE) is not None


def require_regex(
    errors: list[str],
    *,
    path: Path,
    text: str,
    field: str,
    pattern: str,
    message: str,
) -> None:
    if not has_regex(text, pattern):
        errors.append(f"{norm(path)}: missing cadence contract field {field}: {message}")


def require_tokens(
    errors: list[str],
    *,
    path: Path,
    text: str,
    field: str,
    tokens: tuple[str, ...],
) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        errors.append(
            f"{norm(path)}: missing cadence contract field {field}: "
            + ", ".join(missing)
        )


def check_plan_en(path: Path, text: str, errors: list[str]) -> None:
    require_tokens(errors, path=path, text=text, field="original_window", tokens=(WINDOW_START, WINDOW_END))
    require_regex(
        errors,
        path=path,
        text=text,
        field="scheduled_repeat_count",
        pattern=rf"fixed at\s+{SCHEDULED_TOTAL_RUNS}\s+runs total",
        message="standard scheduled audit repeats must be fixed at 6 total runs",
    )
    require_regex(
        errors,
        path=path,
        text=text,
        field="run_shape",
        pattern=rf"{BASELINE_RUNS}\s+baseline,\s+{WEEKLY_RUNS}\s+weekly runs,\s+and\s+{FINAL_RUNS}\s+final",
        message="run shape must stay 1 baseline, 4 weekly runs, and 1 final run",
    )
    require_tokens(errors, path=path, text=text, field="weekly_dates", tokens=WEEKLY_DATES)
    require_regex(
        errors,
        path=path,
        text=text,
        field="warning_triage_frequency",
        pattern=r"Warning triage .*event[- /]triggered.*(?:no fixed repeat count|not assigned a fixed repeat count)",
        message="warning triage must remain event-triggered with no fixed repeat count",
    )
    require_regex(
        errors,
        path=path,
        text=text,
        field="post_final_boundary",
        pattern=r"Runs after that date are post-final monitoring only",
        message="post-final runs must not extend or reopen the original window",
    )


def check_plan_zh(path: Path, text: str, errors: list[str]) -> None:
    require_tokens(errors, path=path, text=text, field="original_window", tokens=(WINDOW_START, WINDOW_END))
    require_regex(
        errors,
        path=path,
        text=text,
        field="scheduled_repeat_count",
        pattern=rf"标准计划内审计重复次数固定为\s*{SCHEDULED_TOTAL_RUNS}\s*次",
        message="中文 companion 必须锁定 6 次标准计划内审计运行",
    )
    require_regex(
        errors,
        path=path,
        text=text,
        field="run_shape",
        pattern=rf"{BASELINE_RUNS}\s*次\s*baseline.*{WEEKLY_RUNS}\s*次\s*weekly.*{FINAL_RUNS}\s*次\s*final",
        message="中文 companion 必须保留 1/4/1 运行形态",
    )
    require_tokens(errors, path=path, text=text, field="weekly_dates", tokens=WEEKLY_DATES)
    require_regex(
        errors,
        path=path,
        text=text,
        field="warning_triage_frequency",
        pattern=r"Warning triage.*事件触发.*不分配固定重复次数",
        message="中文 companion 必须说明 warning triage 事件触发且不分配固定次数",
    )
    require_regex(
        errors,
        path=path,
        text=text,
        field="post_final_boundary",
        pattern=r"仅属于 post-final monitoring",
        message="中文 companion 必须说明 2026-06-15 之后仅属 post-final monitoring",
    )


def check_final_summary(path: Path, text: str, errors: list[str]) -> None:
    require_regex(
        errors,
        path=path,
        text=text,
        field="since_date",
        pattern=rf"Since:\s*`{WINDOW_START}T",
        message="final summary must start on the locked audit start date",
    )
    require_regex(
        errors,
        path=path,
        text=text,
        field="until_date",
        pattern=rf"Until:\s*`{WINDOW_END}T",
        message="final summary must end on the locked audit end date",
    )
    require_regex(
        errors,
        path=path,
        text=text,
        field="days",
        pattern=r"Days:\s*`30`",
        message="final summary must remain a 30-day report",
    )
    require_regex(
        errors,
        path=path,
        text=text,
        field="profile_apply_allowed",
        pattern=r"Profile apply allowed:\s*`False`",
        message="cadence evidence must not authorize profile apply",
    )


def check_evidence_index(path: Path, text: str, errors: list[str]) -> None:
    require_tokens(errors, path=path, text=text, field="original_window", tokens=(WINDOW_START, WINDOW_END))
    require_regex(
        errors,
        path=path,
        text=text,
        field="scheduled_repeat_count",
        pattern=rf"Scheduled repeat count:\s*`{SCHEDULED_TOTAL_RUNS}`\s+total planned runs",
        message="latest evidence index must expose 6 planned runs",
    )
    require_regex(
        errors,
        path=path,
        text=text,
        field="run_shape",
        pattern=rf"Day 0 baseline\s*`{BASELINE_RUNS}`,\s*weekly evidence\s*`{WEEKLY_RUNS}`,\s*Day 30 final evidence\s*`{FINAL_RUNS}`",
        message="latest evidence index must expose 1/4/1 run shape",
    )
    require_tokens(errors, path=path, text=text, field="weekly_dates", tokens=WEEKLY_DATES)
    require_regex(
        errors,
        path=path,
        text=text,
        field="warning_triage_frequency",
        pattern=r"Warning triage cadence:\s*event-triggered only.*no fixed repeat count",
        message="latest evidence index must keep warning triage event-triggered",
    )
    require_regex(
        errors,
        path=path,
        text=text,
        field="post_final_boundary",
        pattern=rf"Post-final runs after {WINDOW_END}:\s*monitoring evidence only",
        message="latest evidence index must keep post-final runs monitoring-only",
    )


def build_report(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    required_paths = [PLAN_EN, PLAN_ZH, FINAL_SUMMARY]
    missing_required = [path for path in required_paths if not (root / path).exists()]
    for path in missing_required:
        errors.append(f"{norm(path)}: required cadence evidence file is missing.")

    latest_index = latest_path(root, "skills_usage_audit_evidence_index_*.md")
    if latest_index is None:
        errors.append("docs_bilingual/memory: no skills usage audit evidence index was found.")

    plan_en_text = read_text(root / PLAN_EN)
    plan_zh_text = read_text(root / PLAN_ZH)
    final_summary_text = read_text(root / FINAL_SUMMARY)
    latest_index_text = read_text(latest_index) if latest_index else ""

    if plan_en_text:
        check_plan_en(PLAN_EN, plan_en_text, errors)
    if plan_zh_text:
        check_plan_zh(PLAN_ZH, plan_zh_text, errors)
    if final_summary_text:
        check_final_summary(FINAL_SUMMARY, final_summary_text, errors)
    if latest_index_text and latest_index:
        check_evidence_index(latest_index.relative_to(root), latest_index_text, errors)

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "cadence_contract": {
            "original_window_start": WINDOW_START,
            "original_window_end": WINDOW_END,
            "scheduled_repeat_count": SCHEDULED_TOTAL_RUNS,
            "scheduled_run_shape": {
                "day_0_baseline": BASELINE_RUNS,
                "weekly_evidence": WEEKLY_RUNS,
                "day_30_final": FINAL_RUNS,
            },
            "weekly_evidence_dates": list(WEEKLY_DATES),
            "warning_triage_frequency": "event_triggered_only_no_fixed_repeat_count",
            "post_final_runs": "monitoring_evidence_only_no_window_extension_no_profile_apply_authorization",
        },
        "evidence_paths": {
            "plan_en": norm(PLAN_EN),
            "plan_zh": norm(PLAN_ZH),
            "final_summary": norm(FINAL_SUMMARY),
            "latest_evidence_index": norm(latest_index.relative_to(root)) if latest_index else None,
        },
        "errors": errors,
        "warnings": warnings,
        "counts": {
            "errors": len(errors),
            "warnings": len(warnings),
            "weekly_evidence_dates": len(WEEKLY_DATES),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify the Codex Skills usage audit cadence, repeat-count, frequency, and end-date contract."
    )
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    report = build_report(Path(args.root))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif report["ok"]:
        contract = report["cadence_contract"]
        shape = contract["scheduled_run_shape"]
        print(
            f"{CHECK_NAME}: ok "
            f"window={contract['original_window_start']}..{contract['original_window_end']} "
            f"runs={contract['scheduled_repeat_count']} "
            f"shape={shape['day_0_baseline']}/{shape['weekly_evidence']}/{shape['day_30_final']} "
            f"warning_triage={contract['warning_triage_frequency']}"
        )
    else:
        print(f"{CHECK_NAME}: failed")
        for error in report["errors"]:
            print(f"ERROR: {error}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
