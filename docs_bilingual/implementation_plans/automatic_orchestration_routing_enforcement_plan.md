---
doc_id: automatic_orchestration_routing_enforcement_plan
version: 0.22
status: active
owner: codex-orchestration
date: 2026-05-27
---

# Automatic Orchestration Routing Enforcement Plan

## 0. Full `/comet` refactor verdict

This version keeps the automatic orchestration rules unchanged while reshaping the plan into the newer implementation-plan structure used by `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md` and `comet_runtime_agile_focus_area_plan.zh-CN.md`. It is documentation-only: it does not implement Phase 4, start a durable or persistent team, create a LangGraph workflow, or prove that native experts ran.

Current status:

- Phase 0-3 are complete and archived as the historical baseline.
- Phase 4 `enforce-prompt-independent-collaboration-parity` remains a planned follow-up.
- This document is active policy and planning guidance, not runtime evidence.

## 1. Goals

- Ensure Codex sessions evaluate collaboration automatically without depending on user phrases such as "use experts / durable_team / persistent team".
- Separate policy expectation, runtime capability, adopted state, and auditable evidence.
- Make native experts, native_omx, LangGraph durable workflow, and persistent team adoption checker-backed.
- Define Phase 4 with a fixed change id, file map, evidence contracts, slices, validation, and rollback.

## 2. Non-goals

- Do not force every task into multi-worker execution.
- Do not treat skills, plugin profiles, profile helpers, or prompts as native experts.
- Do not auto-launch durable or persistent teams during startup, read-context, boundary-freeze, or low-risk single-file work.
- Do not treat `backend_default=langgraph` as proof that a persistent team is running.
- Do not push or publish remotely without explicit current-user authorization.

## 3. Authority and state terms

| State | Meaning | Not evidence for |
| --- | --- | --- |
| `active` | Current rule and acceptance baseline. | Runtime worker execution. |
| `complete` | A bounded slice has validation evidence. | No future gaps. |
| `planned follow-up` | Scope and tasks are defined but not built. | Existing checker/runtime behavior. |
| `documentation-only` | Text changed only. | Runtime state change. |

Capability chain:

```text
subagent_routing != off -> oh_my_codex = on -> langgraph = on -> backend_default=langgraph when ready
```

`backend_default=langgraph` means the durable backend is available; it does not mean durable workflow or persistent team is selected, running, or complete.

## 4. Runtime governance principles

- The main Codex session remains the leader for activation checks, role selection, fan-in, evidence labels, local integration, and final reporting.
- Explicit `omx` or `LangGraph` is a hard directive; non-adoption requires a named blocker or unmet threshold.
- Missing collaboration phrases are not a skip reason; present phrases cannot bypass frozen plans, evidence guards, or ownership.
- Expert timeout, stall, provider pacing, and silent waits are non-evidence.
- One durable task uses one backend family unless close or explicit handoff is recorded.

## 5. Activation trace contract

Activation runs on first substantive work, reload/restart/resume/continue, phase change, `.omx` state detection, capability-state change, expert timeout/stall, expansion to 2+ slices, or explicit collaboration/backend directives.

Minimum trace fields:

```text
phase=<...>
capability_chain=subagent_routing:<...> > oh_my_codex:<...> > langgraph:<...>
backend_default=<langgraph|native_omx|none>
backend_ready=<true|false|unknown>
experts=<none|role|blocked:reason>
durable_workflow=<not_needed|candidate|selected|running|complete|blocked>
persistent_team=<not_needed|candidate|selected|running|complete|blocked>
why=<task-shape|threshold|blocker|evidence>
```

Forbidden explanations include "the user did not ask for parallelism", "the user did not type experts", "LangGraph ready means persistent team running", and "skill invocation means native expert ran".

## 6. Routing matrix

| Scenario | Experts | Durable workflow | Persistent team | Leader action |
| --- | --- | --- | --- | --- |
| Single low-risk doc file | Usually none. | Not needed. | Not needed. | Edit, check, commit. |
| Large doc rewrite | Writer/verifier if useful. | Candidate when checkpoints are needed. | Only after frozen plan and 2+ independent slices. | Leader-owned integration. |
| Bounded multi-face research | Analyst-only first fan-out. | Re-evaluate after fan-in. | Not before plan freeze. | Freeze brief. |
| Cross-module design | Architect/security as needed. | Candidate. | Candidate after frozen plan and 2+ slices. | Define interfaces and ownership. |
| Blocking regression | Debugger. | Survivor queue if needed. | Stabilize may use debugger lanes. | Converge repair. |

## 7. Durable-team thresholds

Persistent teams require a frozen plan plus at least two mostly independent execution slices, except stabilize/debugger lanes where one blocking issue can justify debugger workers. Startup, read-context, freeze-plan, and verify-accept do not start new durable teams by default.

## 8. Expert lifecycle and wait discipline

Expert audit events are `spawn`, `wait`, `timeout`, `stall`, `provider_pacing_wait`, `result`, `absorbed`, and `close`. Results cited by final reports must have matching `absorbed`; timeout/stall/provider pacing may only be non-evidence. Completed experts are closed by default after absorption.

## 9. Agent / skill / profile boundary

| Surface | Evidence rule |
| --- | --- |
| Native Codex subagent | Requires spawn/wait/result/close/absorbed audit. |
| Skill from `SKILL.md` | Workflow instruction only; not expert evidence. |
| Plugin/profile helper | Procedural context only; not expert evidence. |
| LangGraph node | Durable workflow evidence, not native expert evidence. |
| OMX durable worker | Selector/manifest/heartbeat/lifecycle evidence, not native expert evidence. |

## 10. Effective lane choice

Use the main session for small single-slice work, native experts for bounded review/research/debug/verification, native_omx for worker-centric durable execution and mailbox/worktree control, LangGraph for graph-shaped checkpointed workflows, and persistent teams only after the team thresholds are met.

## 11. File responsibility map

| File or directory | Responsibility |
| --- | --- |
| `AGENTS.md` | Startup and orchestration authority. |
| `docs_bilingual/project_startup_summary.*` | Cold-start read order and repository posture. |
| `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.*` | Activation policy and evidence boundaries. |
| `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.*` | This active baseline and Phase 4 plan. |
| `openspec/specs/codex-user-level-orchestration-activation-policy/spec.md` | Stable OpenSpec requirements. |
| `tools/run_openspec_guard.py` | Repository guard entrypoint. |
| `tools/ci/ci_test_manifest.json` | Local gate test registration. |

## 12. Completed baseline

| Phase | Status | Result |
| --- | --- | --- |
| Phase 0 | complete | Registered and protected the plan. |
| Phase 1 | complete | Updated startup, governance, and policy surfaces. |
| Phase 2 | complete | Added script-backed enforcement for trace, capability, role, lifecycle, delegation, state, lane, and ownership rules. |
| Phase 3 | implemented | Generated user-level templates carry the automatic collaboration default. |

Archived slices include the automatic-routing baseline, active selector helper, hard directive adoption, capability chain, custom agent TOML schema, expert lifecycle evidence, trace evidence validator, agent/skill/profile boundaries, delegation wait discipline, durable artifact surfaces, lane fit, fan-out ownership, leader scope, checker CI coverage, role directive routing evidence, and global collaboration default hardening.

## 13. Phase 4 package

| Item | Decision |
| --- | --- |
| Change id | `enforce-prompt-independent-collaboration-parity` |
| Recommended branch | `enforce-prompt-independent-collaboration-parity` |
| Recommended worktree | `.worktrees/enforce-prompt-independent-collaboration-parity` |
| Goal | Prove routing parity with or without explicit collaboration phrases. |
| Evidence surfaces | Prompt-independent fixtures, cold-start ledger, durable/persistent evidenceguard, expert lifecycle JSONL, LangGraph release checker. |
| Exit | New checkers wired into `tools/run_openspec_guard.py` and `tools/ci/ci_test_manifest.json`; local gate and local MR review pass. |

## 14. Process-group model

| Group | Inputs | Tools and techniques | Outputs |
| --- | --- | --- | --- |
| Initiating | Review, policy, archived baseline. | Problem framing and evidence-gap analysis. | Proposal and non-claim boundary. |
| Planning | Change, file map, fixture needs. | Slicing, owner mapping, test-first design. | Frozen plan and validation matrix. |
| Executing | Worktree, delta spec, fixtures. | TDD, JSON/JSONL fixtures, guard wiring. | Checkers, tests, docs, changed paths. |
| Monitoring | Test and guard output. | Diff review, local CI, verifier review. | Fixes and risk list. |
| Closing | Passing gates and clean branch. | Local MR review and archive decision. | Merge-ready branch or deferral evidence. |

## 15. Evidence contracts

### 15.1 Cold-start read-order evidence

Fixtures live under `test/fixtures/cold_start_read_order_evidence/`. Required fields include `case_id`, `trigger`, `read_order_source.path`, `startup_summary_pair`, `read_order_evidence.items[]`, `summary_counts`, `openspec_list`, `worktree_preflight`, `activation_trace_ref`, `runtime_evidence_refs`, and `evidence_boundary`. Fail when startup-summary reads are missing, skipped files lack reasons, only activation trace exists, counts mismatch, or read-order evidence is used as runtime worker evidence.

### 15.2 Prompt-independent activation parity

Paired fixtures live under `test/fixtures/orchestration_prompt_independent_collaboration_parity/` and share `task_shape_id`. Compare phase, experts, durable workflow, persistent-team threshold, default backend, and claim boundary. The explicit phrase can only set `directive_seen=true`.

### 15.3 Durable / persistent evidenceguard

`not_needed` needs threshold trace. `candidate` needs slice analysis. `selected` needs selector/preflight/ownership. `running` needs selector, manifest, heartbeat, and lifecycle. `complete` also needs closed agent, result summary, and absorbed record. `blocked` needs blocker evidence and must not be claimed as success.

### 15.4 Expert lifecycle audit

Lifecycle JSONL must include event, timestamp, agent id, role, optional nickname, task summary, status, and evidence disposition. `result` cited by a final report requires `absorbed`. Timeout/stall/provider pacing is non-evidence.

### 15.5 LangGraph state release

LangGraph state must include thread id, workflow id, status, active work, heartbeat, completion marker, release marker, and continue reason. Completed work cannot remain `running` without release marker or continue reason.

## 16. Implementation slices

- Slice 0: create OpenSpec proposal, tasks, and delta spec for `enforce-prompt-independent-collaboration-parity`.
- Slice 1: implement cold-start read-order evidence guard and fixtures.
- Slice 2: implement prompt-independent parity checker and paired fixtures.
- Slice 3: implement durable/persistent evidenceguard.
- Slice 4: implement expert lifecycle audit.
- Slice 5: implement LangGraph state release checker.
- Slice 6: update governance docs, guard wiring, CI manifest, and closeout evidence.

## 17. Task-level backlog

- Task A: Freeze Phase 4 OpenSpec WHAT; output active change and acceptance criteria.
- Task B: Implement cold-start evidence guard; output checker, tests, fixtures, guard wiring.
- Task C: Implement prompt-independent parity checker; output paired fixtures and field comparison.
- Task D: Implement durable/persistent evidenceguard; output false-claim rejection.
- Task E: Implement expert lifecycle audit; output spawn/wait/timeout/result/close/absorbed checks.
- Task F: Implement LangGraph release checker; output stale-running failure.
- Task G: Update governance, validate, and integrate locally.

## 18. Validation plan

Minimum validation for documentation-only refactors:

```powershell
git diff --check
python .\tools\check_implementation_plan_rules.py --root . --json
python .\tools\check_precommit_update_archive.py --root . --json
python .\tools\run_openspec_guard.py --root .
```

Full integration validation also runs `openspec validate --all`, focused checker tests, `tools/ci/local_gate.ps1`, and `tools/ci/local_mr_review.ps1`.

## 19. Local integration order

Create a feature worktree from current local main, confirm local main is not behind gitlab/main, update paired documents, run validation, commit with a Chinese message, keep the worktree clean, merge into local main, and do not publish remotely without explicit authorization.

## 20. Completion checklist

- [ ] Newer implementation-plan structure is present.
- [ ] Phase 0-3 completion and Phase 4 planning are not mixed.
- [ ] No durable/persistent runtime is claimed without evidence.
- [ ] Agent/skill/profile/backend evidence boundaries are clear.
- [ ] Phase 4 checkers have files, fixtures, failure conditions, and validation commands.

## 21. Acceptance criteria

- Automatic collaboration rules map to checkers or evidence contracts.
- Same task shape produces the same decision with or without collaboration phrases.
- Cold-start evidence records reads, skips, OpenSpec state, worktree preflight, and evidence boundary.
- Durable/persistent claims fail without selector, manifest, heartbeat, lifecycle, closed/absorbed evidence.
- Expert results require `absorbed`; timeouts remain non-evidence.
- LangGraph completed work does not leave stale `running` state.
- Local validation, local gate, and local MR review pass before local main merge.

## 22. Evidence to retain

Keep this document pair diff, OpenSpec records, checker outputs, `run_openspec_guard.py` output, local gate output, local MR review output, feature worktree clean status, and local main merge record.

## 23. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Small tasks over-launch workers. | Separate backend readiness from team launch thresholds. |
| Read evidence becomes runtime evidence. | Enforce `evidence_boundary`. |
| Skills/profiles become expert evidence. | Accept only native lifecycle audit. |
| LangGraph `running` is overclaimed. | Require heartbeat, active work, release marker, or continue reason. |
| Parallel writes conflict. | Require ownership, disjoint write sets, serialization, and leader integration. |

## 24. Rollback rules

Revert documentation commits for text-only rollback. For checker false positives, temporarily remove guard wiring while preserving fixtures and governance requirements. Remote publication rollback is out of scope without separate authorization.

## 25. References

- `AGENTS.md` - repository and user-level instruction surface.
- `docs_bilingual/project_startup_summary.md` - cold-start read order.
- `docs_bilingual/project_startup_summary.zh-CN.md` - Chinese startup companion.
- `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` - activation policy.
- `docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md` - worktree safety policy.
- `docs_bilingual/governance/openspec_usage_convention.md` - OpenSpec usage convention.
