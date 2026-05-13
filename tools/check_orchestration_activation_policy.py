#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CHECK_NAME = "orchestration_activation_policy"

REQUIRED_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "codex_user_level_orchestration_activation_policy",
        "Run an orchestration activation check",
        "phase, capability chain, backend default/readiness, experts, durable workflow, persistent team",
        "Do not cite missing user reminders",
        "expert timeout/stall/upstream pacing as non-evidence",
        "backend_default=langgraph",
        "persistent team is running",
        "threshold_not_met:no_frozen_plan",
        "threshold_not_met:single_execution_slice",
        "concrete threshold trigger",
        "hard routing directives",
        "explanation-only mode",
        "blocked:backend_not_ready",
        "blocked:preflight_failed",
        "blocked:helper_missing",
        "blocked:write_ownership_conflict",
        "optional preference",
        "custom agent TOML",
        "tools/check_custom_agent_toml_schema.py",
        "developer_instructions",
        "subagent_routing=off",
        "oh_my_codex=off",
        "langgraph=on",
        "durable_orchestration_backend=langgraph",
        "tools/check_capability_switch_chain.py",
    ],
    "docs_bilingual/project_startup_summary.md": [
        "codex_user_level_orchestration_activation_policy.md",
        "Automatic orchestration activation reminders",
        "capability_chain",
        "durable_workflow",
        "persistent_team",
        "missing user reminders",
        "LangGraph is ready",
    ],
    "docs_bilingual/project_startup_summary.zh-CN.md": [
        "codex_user_level_orchestration_activation_policy.zh-CN.md",
        "自动 orchestration activation 提醒",
        "capability_chain",
        "durable_workflow",
        "persistent_team",
        "用户没有要求并行/子代理",
        "LangGraph ready",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md": [
        "subagent_routing != off",
        "backend_default=langgraph",
        "backend_ready=true",
        "`subagent_routing=off` requires `oh_my_codex=off`",
        "`oh_my_codex=off` requires `langgraph=off`",
        "`durable_orchestration_backend=langgraph`, then `langgraph=on`",
        "tools/check_capability_switch_chain.py",
        "Activation triggers",
        "Required trace fields",
        "the user did not request parallelism",
        "expert timed out; not used as evidence",
        "main session took over verification",
        "tools/check_orchestration_activation_policy.py",
        "tools/check_orchestration_trace_evidence.py",
        ".omx/state/selectors/active.json",
        "selector refresh gap",
        "threshold_not_met:no_frozen_plan",
        "threshold_not_met:single_execution_slice",
        "concrete threshold triggered",
        "hard routing directives",
        "explanation-only mode",
        "blocked:backend_not_ready",
        "blocked:preflight_failed",
        "blocked:helper_missing",
        "blocked:write_ownership_conflict",
        "optional preference",
        "custom agent TOML",
        "tools/check_custom_agent_toml_schema.py",
        "developer_instructions",
        "Smallest-sufficient role selection",
        "Bounded multi-face research",
        "Skills are not native subagents",
        "spawn a fresh agent",
        "current main Codex CLI session remains the leader",
        "Native Codex remains the base layer",
        "one backend family at a time",
        "concrete, bounded, self-contained sidecar work",
        "meaningful non-overlapping leader work",
        "Read-only exploration",
        "LangGraph entrypoints",
        "frozen implementation brief",
        "adversarial-review survivor queue",
        "AutoGen and CrewAI",
        "Native-agent TOML schema is checked",
        "native-agent TOMLs",
    ],
    "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md": [
        "subagent_routing != off",
        "backend_default=langgraph",
        "backend_ready=true",
        "Activation 触发条件",
        "必填 trace 字段",
        "用户没有要求并行",
        "expert timed out; not used as evidence",
        "main session took over verification",
        "tools/check_orchestration_activation_policy.py",
        "tools/check_orchestration_trace_evidence.py",
        ".omx/state/selectors/active.json",
        "selector refresh gap",
        "threshold_not_met:no_frozen_plan",
        "threshold_not_met:single_execution_slice",
        "triggered_threshold",
        "hard routing directives",
        "explanation-only mode",
        "blocked:backend_not_ready",
        "blocked:preflight_failed",
        "blocked:helper_missing",
        "blocked:write_ownership_conflict",
        "optional preference",
        "custom agent TOML",
        "tools/check_custom_agent_toml_schema.py",
        "developer_instructions",
        "Smallest-sufficient role selection",
        "bounded multi-face research",
        "spawn fresh agent",
        "current main Codex CLI session",
        "Native Codex remains the base layer",
        "one backend family",
        "meaningful non-overlapping leader work",
        "read-only exploration",
        "LangGraph entrypoints",
        "frozen implementation brief",
        "adversarial-review survivor queue",
        "Standalone native-agent TOMLs",
    ],
    "openspec/specs/codex-user-level-orchestration-activation-policy/spec.md": [
        "orchestration-activation policy",
        "hard routing directive",
        "retrofit rules",
        "Capability switch chains SHALL be executable-policy checked",
        "tools/check_capability_switch_chain.py",
        "subagent_routing=off",
        "durable_orchestration_backend=langgraph",
        "Activation traces SHALL expose full orchestration state",
        "trace-evidence validator",
        "Missing user reminders SHALL NOT be a routing reason",
        "Expert timeout SHALL NOT be accepted as verification evidence",
        "Existing sessions SHALL retrofit activation policy",
        "threshold_not_met:no_frozen_plan",
        "threshold_not_met:single_execution_slice",
        "First activation does not select a durable team",
        "Hard routing directives SHALL require adoption or named blockers",
        "Explicit directive is adopted",
        "Explicit directive is blocked",
        "explanation-only mode",
        "blocked:backend_not_ready",
        "blocked:preflight_failed",
        "blocked:helper_missing",
        "blocked:write_ownership_conflict",
        "optional preference",
        "custom agent TOML",
        "tools/check_custom_agent_toml_schema.py",
        "developer_instructions",
        "Smallest-sufficient role selection SHALL stay trigger-based",
        "Agent, skill, profile, and follow-up surfaces SHALL stay distinct",
        "The main Codex CLI session SHALL remain the leader",
        "Native Codex SHALL remain the base layer",
        "Delegation SHALL preserve critical-path leader work",
        "Exploration, code-change delegation, and durable artifact persistence SHALL stay distinct",
        "Research handoff and adversarial review SHALL persist bounded handoffs",
        "analystxN",
        "skills are not native subagents",
        "fresh agent",
        "one backend family",
        "meaningful non-overlapping leader work",
        ".omx/state/langgraph/",
        "AutoGen and CrewAI",
        "Native-agent TOML schema is checked",
        "native-agent TOMLs",
    ],
    "openspec/specs/codex-user-level-team-mode-native-subagent-boundaries/spec.md": [
        "Custom native-subagent TOMLs SHALL use layered locations and a minimum standalone schema",
        "tools/check_custom_agent_toml_schema.py",
        "name",
        "description",
        "developer_instructions",
        "Custom agent TOML schema checker runs",
    ],

    "openspec/specs/codex-user-level-capability-switches/spec.md": [
        "Capability switches SHALL be read as a dependency chain",
        "subagent_routing",
        "oh_my_codex",
        "langgraph",
        "durable_orchestration_backend=langgraph",
        "tools/check_capability_switch_chain.py",
        "langgraph_ready=true",
        "persistent team is already running",
    ],
    "openspec/specs/codex-user-level-capability-switches/spec.zh-CN.md": [
        "Capability switches",
        "subagent_routing",
        "oh_my_codex",
        "langgraph",
        "durable_orchestration_backend=langgraph",
        "tools/check_capability_switch_chain.py",
        "langgraph_ready=true",
        "persistent team",
    ],
    "openspec/specs/codex-user-level-team-mode-automatic-team-routing/spec.md": [
        ".omx/state/selectors/active.json",
        "selector refresh gap",
        "SHALL NOT downgrade the backend to unavailable",
        "SHALL NOT auto-adopt unmanaged compatibility records",
    ],
}

FORBIDDEN_SNIPPETS: dict[str, list[str]] = {
    "AGENTS.md": [
        "user did not ask for parallelism",
        "user did not ask for subagents",
    ],
}

REGISTRY_RULE_ID = "orchestration-activation-policy"
GUARD_STEP = "check_orchestration_activation_policy"


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError:
        return None



def run_capability_switch_chain_subcheck(root: Path, errors: list[str], warnings: list[str]) -> None:
    checker_path = root / "tools" / "check_capability_switch_chain.py"
    if not checker_path.exists():
        errors.append("Missing capability switch chain checker: tools/check_capability_switch_chain.py")
        return
    spec = importlib.util.spec_from_file_location("check_capability_switch_chain", checker_path)
    if spec is None or spec.loader is None:
        errors.append("Unable to load capability switch chain checker: tools/check_capability_switch_chain.py")
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    payload = module.run_check(root, require_state=False, require_backend=False)
    for warning in payload.get("warnings", []):
        warnings.append(f"capability_switch_chain: {warning}")
    if not payload.get("ok", False):
        for error in payload.get("errors", []):
            errors.append(f"capability_switch_chain: {error}")

def run_check(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[dict[str, Any]] = []

    for rel, snippets in REQUIRED_SNIPPETS.items():
        path = root / rel
        text = read_text(path)
        if text is None:
            errors.append(f"Missing required orchestration activation surface: {rel}")
            continue
        missing = [snippet for snippet in snippets if snippet not in text]
        if missing:
            for snippet in missing:
                errors.append(f"{rel} missing required snippet: {snippet}")
        checked.append({"path": rel, "required_snippets": len(snippets), "missing": missing})

    for rel, snippets in FORBIDDEN_SNIPPETS.items():
        path = root / rel
        text = read_text(path) or ""
        for snippet in snippets:
            if snippet in text:
                errors.append(f"{rel} contains forbidden missing-reminder wording: {snippet}")

    guard_text = read_text(root / "tools/run_openspec_guard.py") or ""
    if GUARD_STEP not in guard_text:
        errors.append(f"tools/run_openspec_guard.py must run {GUARD_STEP}")

    run_capability_switch_chain_subcheck(root, errors, warnings)

    registry_text = read_text(root / "tools/safety_rule_script_backing_registry.json")
    if registry_text is None:
        errors.append("Missing safety rule registry")
    else:
        try:
            registry = json.loads(registry_text)
        except json.JSONDecodeError as exc:
            errors.append(f"Invalid safety rule registry JSON: {exc}")
        else:
            rules = registry.get("rules", []) if isinstance(registry, dict) else []
            matching = [rule for rule in rules if isinstance(rule, dict) and rule.get("id") == REGISTRY_RULE_ID]
            if not matching:
                errors.append(f"Safety rule registry missing rule id: {REGISTRY_RULE_ID}")
            else:
                rule = matching[0]
                for field, expected in {
                    "prompt_reminders": "docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md",
                    "script_controls": "tools/check_orchestration_activation_policy.py",
                    "guard_steps": GUARD_STEP,
                }.items():
                    values = rule.get(field, [])
                    if expected not in values:
                        errors.append(f"Safety rule {REGISTRY_RULE_ID} missing {field} entry: {expected}")

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "check_name": CHECK_NAME,
        "ok": not errors,
        "root": str(root),
        "checked": checked,
        "errors": errors,
        "warnings": warnings,
        "counts": {"checked_files": len(checked), "errors": len(errors), "warnings": len(warnings)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify script-backed orchestration activation policy surfaces.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    payload = run_check(Path(args.root))
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        if payload["ok"]:
            print("orchestration_activation_policy: ok")
        for warning in payload["warnings"]:
            print(f"WARNING: {warning}")
        for error in payload["errors"]:
            print(f"ERROR: {error}")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
