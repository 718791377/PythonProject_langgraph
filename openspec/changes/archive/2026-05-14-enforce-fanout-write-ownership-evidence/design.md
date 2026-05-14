# Design: Fan-out and write-ownership evidence enforcement

## Approach

Implement one Python checker with two modes:

1. Repository mode validates that core policy surfaces explicitly require:
   - native Codex subagents to be leader-side spawned with leader-owned fan-in;
   - raw Codex to not be described as auto-spawning specialist roles;
   - managed fan-out defaults of `agents.max_threads=6` and `agents.max_depth=1` unless an explicit override is recorded;
   - read-heavy fan-out to stay bounded, independent, and materially useful;
   - write-heavy parallel execution to declare file/module ownership, disjoint write sets, hotspot serialization, and leader-owned final integration;
   - workers to be told they are not alone in the codebase and must not revert or overwrite other active owners.
2. Evidence mode validates saved traces, run summaries, or worker briefs:
   - fan-out claims above the managed defaults fail unless the evidence records an explicit override and approval/reason;
   - raw Codex auto-spawn wording fails;
   - read-heavy parallel fan-out must show bounded, independent sidecar work and leader-owned fan-in;
   - write-heavy parallel execution must show file/module ownership, disjoint write sets, hotspot serialization, leader-owned final integration, not-alone/do-not-revert language, and changed-path reporting;
   - overlapping write sets fail unless the evidence names serialized hotspots or sequential ownership transfer;
   - delegated urgent blocking critical-path work fails unless an explicit handoff/takeover reason is recorded.

The checker complements existing checks:

- `check_role_routing_directive_evidence.py` proves hard-directive adoption and smallest-sufficient roles.
- `check_delegation_wait_discipline_evidence.py` proves general delegation design and wait discipline.
- This checker proves managed fan-out bounds, raw-Codex terminology, and write-heavy parallel ownership isolation.

## CI and guard wiring

- Add `tools/check_fanout_write_ownership_evidence.py`.
- Add `test/check_fanout_write_ownership_evidence.test.py`.
- Add the test to `tools/ci/ci_test_manifest.json`.
- Add a no-input guard step in `tools/run_openspec_guard.py`.
- Add the checker to `tools/safety_rule_script_backing_registry.json` as a separate implemented safety rule and as supporting script control for the orchestration activation policy.

## Policy synchronization

- Update the English and Chinese orchestration activation policy documents.
- Update the English and Chinese startup summaries.
- Update `AGENTS.md` with the checker-backed fan-out/write-ownership reminder.
- Promote the requirement into `openspec/specs/codex-user-level-orchestration-activation-policy/spec.md` during archive.

## Non-goals

- Do not launch persistent workers for this implementation slice.
- Do not modify user-level runtime state or installed wrappers.
- Do not push to GitLab or GitHub.
