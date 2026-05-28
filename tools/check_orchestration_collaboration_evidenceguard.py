#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CHECK_NAME = "orchestration_collaboration_evidenceguard"
REGISTRY_RULE_ID = "orchestration-collaboration-evidenceguard"
GUARD_STEP = "check_orchestration_collaboration_evidenceguard"
DEFAULT_FIXTURE_DIR = Path("test/fixtures/orchestration_prompt_independent_collaboration_parity")

REQUIRED_FIXTURES = {
    "doc_update_without_collaboration_phrase.json",
    "doc_update_with_collaboration_phrase.json",
    "multi_slice_without_collaboration_phrase.json",
    "multi_slice_with_collaboration_phrase.json",
    "explicit_omx_without_threshold.json",
    "explicit_langgraph_single_slice.json",
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
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md": [
        "tools/check_orchestration_collaboration_evidenceguard.py",
        "Prompt-independent collaboration parity",
        "durable/persistent evidenceguard",
        "LangGraph state release",
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
        "durable/persistent evidenceguard",
        "LangGraph state release",
        "tools/check_orchestration_collaboration_evidenceguard.py",
    ],
    "openspec/specs/codex-user-level-orchestration-activation-policy/spec.zh-CN.md": [
        "prompt-independent collaboration parity",
        "durable/persistent evidenceguard",
        "LangGraph state release",
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
    "why",
)
LANE_STATES = {"not_needed", "candidate", "selected", "running", "complete", "blocked"}
FORBIDDEN_MISSING_REMINDERS = (
    "the user did not request parallelism",
    "the user did not request subagents",
    "user did not request parallelism",
    "user did not request subagents",
    "user did not ask for parallelism",
    "user did not ask for subagents",
)
COLLABORATION_PHRASES = ("experts", "durable_team", "persistent team", "subagents", "parallel")


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


def lower(value: Any) -> str:
    return str(value or "").strip().lower()


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


def validate_expert_lifecycle_case(case: dict[str, Any], errors: list[str], label: str) -> None:
    events = case.get("events")
    if not isinstance(events, list) or not events:
        errors.append(f"{label} missing non-empty events list.")
        return
    names: list[str] = []
    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            errors.append(f"{label}.events[{index}] must be an object.")
            continue
        name = lower(event.get("event"))
        if not name:
            errors.append(f"{label}.events[{index}] missing event name.")
        names.append(name)
        if name == "timeout" and lower(event.get("classification")) != "non-evidence":
            errors.append(f"{label}.events[{index}] timeout must be classified as non-evidence.")
    if "result" in names and "absorbed" not in names:
        errors.append(f"{label} result event requires absorbed event.")
    if "absorbed" in names and "close" not in names and not case.get("preserved_thread_reason"):
        errors.append(f"{label} absorbed expert requires close event or preserved_thread_reason.")
    if "wait" in names:
        waits = [event for event in events if isinstance(event, dict) and lower(event.get("event")) == "wait"]
        if any(not isinstance(event.get("wait_seconds"), int) or event.get("wait_seconds") <= 0 for event in waits):
            errors.append(f"{label} wait events must include positive integer wait_seconds.")
        if not isinstance(case.get("total_wait_bound_seconds"), int) or int(case.get("total_wait_bound_seconds")) <= 0:
            errors.append(f"{label} wait evidence requires total_wait_bound_seconds.")


CASE_VALIDATORS = {
    "activation_parity": validate_activation_parity_case,
    "cold_start_read_order": validate_cold_start_case,
    "durable_persistent_claim": validate_durable_claim_case,
    "langgraph_state_release": validate_langgraph_release_case,
    "expert_lifecycle_audit": validate_expert_lifecycle_case,
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
        before = len(errors)
        route = validate_case(payload, errors, path.name)
        if route is not None and lower(payload.get("case_type")) == "activation_parity":
            group = str(payload.get("parity_group")).strip()
            if not group.startswith("explicit_"):
                parity_routes.setdefault(group, []).append((bool(payload.get("collaboration_phrase_present")), route, path.name))
        if len(errors) == before and payload.get("expected_failure") is True:
            errors.append(f"{path.name} is marked expected_failure but passed validation.")

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
            if key in {"phase", "backend_default", "backend_ready", "experts", "durable_workflow", "persistent_team", "why"}
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
    payload = load_json(path, errors)
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
    parser.add_argument("--evidence", default=None, help="Validate one JSON evidence case instead of repository surfaces.")
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
