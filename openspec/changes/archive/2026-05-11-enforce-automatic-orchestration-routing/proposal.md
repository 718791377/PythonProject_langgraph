## Why

The repository already documents the desired automatic orchestration posture, but the rule is still too easy to regress in live sessions: traces may cite missing user requests as a skip reason, expert timeouts may be overclaimed as evidence, and LangGraph backend readiness can be confused with persistent-team launch thresholds.

## What Changes

- Promote the automatic orchestration routing enforcement plan into an OpenSpec implementation change.
- Add a user-level orchestration activation governance policy and startup reminders.
- Add checker-backed enforcement for activation trace fields, capability-chain wording, timeout evidence boundaries, blocker reporting, leader ownership, and backend/team state vocabulary.
- Keep durable-team launch threshold-gated: backend ready is not the same as team running.

## Capabilities

### Modified Capabilities

- `codex-user-level-orchestration-activation-policy`: adds full activation trace, hard routing directive, timeout-evidence, and retrofit requirements.
- `codex-user-level-team-mode-routing-thresholds`: clarifies durable-team threshold reasons and automatic expert routing boundaries.
- `codex-user-level-capability-switches`: clarifies `subagent_routing -> oh_my_codex -> langgraph` dependency-chain semantics and LangGraph default-backend readiness.
- `codex-user-level-team-mode-automatic-team-routing`: clarifies selector-source authority and backend-ready versus team-running state boundaries.

## Impact

- `AGENTS.md`: adds repository startup routing reminders that cannot be replaced by prompt memory alone.
- `docs_bilingual/project_startup_summary.*`: adds cold-start reminders and read-order entries for the new activation policy.
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.*`: new bilingual governance policy.
- `tools/check_orchestration_activation_policy.py`: new checker for key policy and startup surfaces.
- `tools/run_openspec_guard.py`: runs the new checker.
- `tools/safety_rule_script_backing_registry.json`: registers the new safety rule.
- `test/check_orchestration_activation_policy.test.py`: direct regression tests for the checker.

## Non-goals

- Do not force every small task into durable-team execution.
- Do not install or upgrade the official LangGraph package.
- Do not mutate user-level `C:\Users\lenovo\.codex\config.toml`.
- Do not delete old `.omx/state` artifacts.
- Do not treat this change as the final production-grade persistent team implementation.

## Validation

- Activation policy checker: `python tools/check_orchestration_activation_policy.py --root . --json`
- Activation policy unit tests: `python test/check_orchestration_activation_policy.test.py`
- Repository OpenSpec guard: `python tools/run_openspec_guard.py --root . --tool codex --json`
- Local CI gate: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1`
- Local MR review gate: `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1`
