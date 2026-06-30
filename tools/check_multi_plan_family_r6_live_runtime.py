#!/usr/bin/env python3
"""Check strict multi-plan-family R6 live-runtime completion evidence.

This checker is read-only. It discovers the implementation-plan family
governed by ``multi_plan_parallel_session_orchestration_plan`` and assigns
exactly one completion classification to every member:

* ``direct-r6-lane``
* ``successor-owned-migration-source``
* ``governance-checker-runtime``
* ``no-live-runtime-scope``

When ``--require-coverage`` is supplied, every direct R6 lane must have
accepted evidence from ``check_r6_live_runtime_receipts.py``. The checker never
launches GUI tools, sends messages, starts harness jobs, applies Spec Kit,
mutates user-level state, or publishes remotes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import check_r6_live_runtime_receipts as r6_receipts  # noqa: E402
from user_level_receipt_governance import REQUIRED_PRIORITY_ORDER  # noqa: E402


CHECK_NAME = "multi_plan_family_r6_live_runtime"
DEFAULT_PARENT_PLAN = "docs_bilingual/implementation_plans/multi_plan_parallel_session_orchestration_plan.md"
IMPLEMENTATION_PLAN_DIR = Path("docs_bilingual/implementation_plans")

DIRECT_PLAN_TO_LANE: dict[str, str] = {profile.plan_id: lane for lane, profile in r6_receipts.LANE_PROFILES.items()}

DEFAULT_MIGRATION_SOURCES: dict[str, tuple[str, str]] = {
    "user_level_mcp_skills_discovery_facade_plan": (
        "user_level_mcp_skills_cli_runtime_plan",
        "user-level-mcp-skills-cli-runtime",
    ),
    "user_level_mcp_skills_browser_cli_governance_plan": (
        "user_level_browser_cli_adapter_boundary_plan",
        "user-level-browser-cli-adapter-boundary",
    ),
}

NO_LIVE_RUNTIME_SCOPE = {
    "multi_plan_parallel_session_orchestration_plan",
    "parent_parallel_orchestration_index_plan",
    "plan_inventory_registry_alignment_plan",
    "parallel_plan_docs_registry_integration_plan",
    "parallel_plan_checker_ci_integration_plan",
    "parallel_plan_openspec_comet_archive_plan",
    "pi_plugin_codex_user_level_sidecar_plan",
    "r6_live_runtime_promotion_plan",
}

PLAN_ID_RE = re.compile(r"\b([A-Za-z0-9]+(?:_[A-Za-z0-9]+)*_plan)\b")
STATUS_RE = re.compile(r"^Status:\s*(?P<status>.+)$", re.MULTILINE)
STALE_TOP_PATTERNS = (
    re.compile(r"Status:\s*R5\b", re.IGNORECASE),
    re.compile(r"real sensitive live actions remain blocked", re.IGNORECASE),
    re.compile(r"pending Stage D runtime work", re.IGNORECASE),
    re.compile(r"real-runtime gap update", re.IGNORECASE),
)


@dataclass(frozen=True)
class PlanFile:
    plan_id: str
    path: Path
    relpath: str
    front_matter: dict[str, str]
    text: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def parse_front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    metadata: dict[str, str] = {}
    for raw_line in parts[1].splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("'\"")
    return metadata


def load_plan(root: Path, plan_id: str) -> PlanFile | None:
    path = root / IMPLEMENTATION_PLAN_DIR / f"{plan_id}.md"
    if not path.exists():
        return None
    text = read_text(path)
    return PlanFile(
        plan_id=plan_id,
        path=path,
        relpath=(IMPLEMENTATION_PLAN_DIR / f"{plan_id}.md").as_posix(),
        front_matter=parse_front_matter(text),
        text=text,
    )


def english_primary_plans(root: Path) -> list[PlanFile]:
    result: list[PlanFile] = []
    plan_dir = root / IMPLEMENTATION_PLAN_DIR
    for path in sorted(plan_dir.glob("*.md")):
        if path.name.endswith(".zh-CN.md"):
            continue
        text = read_text(path)
        result.append(
            PlanFile(
                plan_id=path.stem,
                path=path,
                relpath=(IMPLEMENTATION_PLAN_DIR / path.name).as_posix(),
                front_matter=parse_front_matter(text),
                text=text,
            )
        )
    return result


def discover_family_ids(root: Path, parent_plan_rel: str, migration_sources: dict[str, tuple[str, str]]) -> tuple[set[str], list[str]]:
    parent_path = root / parent_plan_rel
    if not parent_path.exists():
        return set(), [f"parent_plan_missing:{parent_plan_rel}"]
    parent_text = read_text(parent_path)
    family_ids: set[str] = {parent_path.stem}

    for plan in english_primary_plans(root):
        if plan.front_matter.get("parent_plan") == parent_plan_rel:
            family_ids.add(plan.plan_id)

    for plan_id in PLAN_ID_RE.findall(parent_text):
        if (root / IMPLEMENTATION_PLAN_DIR / f"{plan_id}.md").exists() or plan_id in migration_sources:
            family_ids.add(plan_id)
    return family_ids, []


def parse_migration_source(raw: str) -> tuple[str, tuple[str, str]]:
    parts = [part.strip() for part in raw.split(":")]
    if len(parts) != 3 or not all(parts):
        raise argparse.ArgumentTypeError("--migration-source must be source_plan:successor_plan:successor_lane")
    return parts[0], (parts[1], r6_receipts.normalize_lane(parts[2]))


def effective_receipt_dir(root: Path, requested: Path | None) -> Path:
    if requested is not None:
        return requested
    # Share the same fallback policy as check_r6_live_runtime_receipts.py so
    # clean GitLab checkouts can verify R6 coverage from tracked fixture receipts
    # while developer worktrees still prefer private ignored .omx live evidence.
    return r6_receipts.effective_receipt_dir(root, None)


def top_prelude(text: str, max_lines: int = 80) -> str:
    return "\n".join(text.splitlines()[:max_lines])


def status_line(text: str) -> str:
    match = STATUS_RE.search(top_prelude(text))
    return match.group("status").strip() if match else ""


def status_lines(text: str) -> list[str]:
    return [match.group("status").strip() for match in STATUS_RE.finditer(top_prelude(text))]


def stale_status_findings(plan: PlanFile, *, accepted_mode: str) -> list[str]:
    if accepted_mode != "live-executed":
        return []
    prelude = top_prelude(plan.text)
    findings: list[str] = []
    statuses = status_lines(plan.text)
    if not any(status.lower().startswith("r6") or "r6 live" in status.lower() for status in statuses):
        findings.append("status_line_not_r6")
    for pattern in STALE_TOP_PATTERNS:
        if pattern.search(prelude):
            findings.append(f"stale_phrase:{pattern.pattern}")
    return sorted(set(findings))


def classify_governance_plan(plan: PlanFile) -> tuple[str, str]:
    if plan.plan_id in NO_LIVE_RUNTIME_SCOPE:
        return "no-live-runtime-scope", "index,parent,draft,archive,or R6 coordination surface; no external live action lane"
    status = plan.front_matter.get("status", "")
    if status and status != "active":
        return "no-live-runtime-scope", f"front_matter_status={status}; not an active execution owner"
    return "governance-checker-runtime", "repository-local governance/checker/helper/CI runtime; no external action lane"


def classify_family(
    root: Path,
    *,
    parent_plan_rel: str,
    receipt_dir: Path,
    require_coverage: bool,
    migration_sources: dict[str, tuple[str, str]],
) -> dict[str, Any]:
    family_ids, discovery_errors = discover_family_ids(root, parent_plan_rel, migration_sources)
    errors: list[str] = list(discovery_errors)
    warnings: list[str] = []

    coverage = r6_receipts.audit_receipt_dir(root, receipt_dir)
    if require_coverage and not coverage.get("coverage_ok"):
        for lane in coverage.get("missing_lanes", []):
            errors.append(f"coverage_missing_lane:{lane}")
        for item in coverage.get("invalid_receipts", []):
            errors.append(f"coverage_invalid_receipt:{item.get('path_hash')}")

    classifications: dict[str, dict[str, Any]] = {}
    stale_count = 0
    restored_deleted = 0
    missing_classification = 0

    for plan_id in sorted(family_ids):
        plan = load_plan(root, plan_id)
        if plan_id in migration_sources:
            successor_plan, successor_lane = migration_sources[plan_id]
            successor = load_plan(root, successor_plan)
            source_path = root / IMPLEMENTATION_PLAN_DIR / f"{plan_id}.md"
            restored = source_path.exists()
            if restored:
                restored_deleted += 1
                errors.append(f"restored_deleted_migration_source:{plan_id}")
            if successor is None:
                errors.append(f"migration_source_successor_missing:{plan_id}")
            lane_record = coverage.get("lane_evidence", {}).get(successor_lane, {})
            if require_coverage and not lane_record.get("accepted"):
                errors.append(f"migration_source_successor_lane_missing_accepted_receipt:{plan_id}:{successor_lane}")
            classifications[plan_id] = {
                "classification": "successor-owned-migration-source",
                "plan_path": (IMPLEMENTATION_PLAN_DIR / f"{plan_id}.md").as_posix(),
                "plan_exists": restored,
                "successor_plan": successor_plan,
                "successor_plan_path": (IMPLEMENTATION_PLAN_DIR / f"{successor_plan}.md").as_posix(),
                "successor_plan_exists": successor is not None,
                "successor_lane": successor_lane,
                "r6_receipt_accepted": bool(lane_record.get("accepted")),
                "r6_receipt_mode": lane_record.get("accepted_mode", ""),
                "rationale": "deleted migration source remains covered by active successor owner",
            }
            continue

        if plan is None:
            missing_classification += 1
            errors.append(f"family_plan_missing:{plan_id}")
            classifications[plan_id] = {"classification": "missing", "plan_exists": False}
            continue

        if plan_id in DIRECT_PLAN_TO_LANE:
            lane = DIRECT_PLAN_TO_LANE[plan_id]
            lane_record = coverage.get("lane_evidence", {}).get(lane, {})
            accepted = bool(lane_record.get("accepted"))
            accepted_mode = str(lane_record.get("accepted_mode") or "")
            if require_coverage and not accepted:
                errors.append(f"direct_lane_missing_accepted_receipt:{plan_id}:{lane}")
            stale = stale_status_findings(plan, accepted_mode=accepted_mode) if accepted else []
            if stale:
                stale_count += len(stale)
                for finding in stale:
                    errors.append(f"stale_status:{plan_id}:{finding}")
            if REQUIRED_PRIORITY_ORDER not in plan.text:
                errors.append(f"priority_order_missing:{plan_id}")
            classifications[plan_id] = {
                "classification": "direct-r6-lane",
                "plan_path": plan.relpath,
                "plan_exists": True,
                "lane": lane,
                "r6_receipt_accepted": accepted,
                "r6_receipt_mode": accepted_mode,
                "r6_live_executed": bool(lane_record.get("live_executed")),
                "external_side_effects": lane_record.get("external_side_effects", ""),
                "status_line": status_line(plan.text),
                "stale_status_findings": stale,
                "rationale": "plan maps directly to a known R6 live-runtime lane",
            }
            continue

        classification, rationale = classify_governance_plan(plan)
        classifications[plan_id] = {
            "classification": classification,
            "plan_path": plan.relpath,
            "plan_exists": True,
            "status": plan.front_matter.get("status", ""),
            "rationale": rationale,
        }

    class_counts: dict[str, int] = {
        "direct_r6_lane": 0,
        "successor_owned_migration_source": 0,
        "governance_checker_runtime": 0,
        "no_live_runtime_scope": 0,
        "missing": 0,
    }
    for item in classifications.values():
        key = str(item.get("classification", "missing")).replace("-", "_")
        class_counts[key] = class_counts.get(key, 0) + 1

    return {
        "schema_version": 1,
        "generated_at": now_iso(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "parent_plan": parent_plan_rel,
        "priority_order": REQUIRED_PRIORITY_ORDER,
        "receipt_dir": str(receipt_dir),
        "require_coverage": require_coverage,
        "classifications": classifications,
        "coverage_summary": coverage,
        "errors": sorted(set(errors)),
        "warnings": warnings,
        "mutates_user_level_state": False,
        "runs_external_tool": False,
        "starts_browser_or_gui": False,
        "sends_external_message": False,
        "mutates_remote_publication": False,
        "counts": {
            "family_members": len(classifications),
            "missing_classification": missing_classification,
            "stale_status_findings": stale_count,
            "restored_deleted_migration_sources": restored_deleted,
            "errors": len(set(errors)),
            "warnings": len(warnings),
            **class_counts,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check strict multi-plan family R6 live-runtime completion evidence.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--parent-plan", default=DEFAULT_PARENT_PLAN)
    parser.add_argument("--receipt-dir", default=None)
    parser.add_argument("--require-coverage", action="store_true")
    parser.add_argument(
        "--migration-source",
        action="append",
        default=[],
        help="Override/add source_plan:successor_plan:successor_lane mapping for deleted migration sources.",
    )
    parser.add_argument("--json", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    migration_sources = dict(DEFAULT_MIGRATION_SOURCES)
    try:
        for raw in args.migration_source:
            source, target = parse_migration_source(raw)
            migration_sources[source] = target
    except argparse.ArgumentTypeError as exc:
        payload = {
            "schema_version": 1,
            "generated_at": now_iso(),
            "check_name": CHECK_NAME,
            "ok": False,
            "errors": [str(exc)],
            "warnings": [],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) if args.json else str(exc))
        return 1
    requested = Path(args.receipt_dir) if args.receipt_dir else None
    receipt_dir = effective_receipt_dir(root, requested)
    payload = classify_family(
        root,
        parent_plan_rel=args.parent_plan,
        receipt_dir=receipt_dir,
        require_coverage=args.require_coverage,
        migration_sources=migration_sources,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"{CHECK_NAME}: {'ok' if payload['ok'] else 'failed'}")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
