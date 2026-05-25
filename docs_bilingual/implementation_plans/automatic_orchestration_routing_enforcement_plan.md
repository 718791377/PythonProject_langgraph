---
doc_id: automatic_orchestration_routing_enforcement_plan
version: 0.17
status: active
owner: codex-orchestration
date: 2026-05-15
---

# Automatic Orchestration Routing Enforcement Plan

## Active status note

This document is the active baseline for automatic orchestration-routing enforcement. `status: active` means the plan remains the adopted rule and verification checklist for current and future sessions. It is not, by itself, a completion claim.

As of 2026-05-15, the originally planned enforcement package has been implemented and archived locally across the OpenSpec changes listed in Section 0. Future regressions or newly discovered gaps should open a new bounded change against this active baseline rather than reopening the already archived implementation slices.

## 0. 2026-05-15 completion-status snapshot

Current local conclusion: this plan is complete for the agreed repository source-of-truth surfaces, generated user-level templates, checker-backed policy guards, and regression tests. The plan remains active because it defines the default behavior and acceptance criteria that later work must preserve.

Completion evidence currently consists of:

- active OpenSpec changes: none (`openspec list --json` returned an empty change list during this review);
- stable policy and startup surfaces: updated in `AGENTS.md`, `docs_bilingual/project_startup_summary.*`, `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.*`, and related OpenSpec stable specs;
- script-backed enforcement: covered by `tools/check_orchestration_activation_policy.py`, `tools/check_orchestration_trace_evidence.py`, `tools/check_capability_switch_chain.py`, `tools/check_expert_lifecycle_wait_pacing_evidence.py`, `tools/check_role_routing_directive_evidence.py`, `tools/check_agent_skill_profile_surface_boundaries.py`, `tools/check_custom_agent_toml_schema.py`, `tools/check_leader_session_scope_evidence.py`, `tools/check_delegation_wait_discipline_evidence.py`, `tools/check_durable_artifact_state_surfaces.py`, `tools/check_effective_lane_fit_evidence.py`, `tools/check_fanout_write_ownership_evidence.py`, and the OpenSpec guard wiring;
- generated user-level source templates: hardened in `tools/install-codex-user-level-team-mode.ps1`, with regression coverage in `test/install-codex-user-level-team-mode.test.ps1`;
- archived implementation slices:
  - `openspec/changes/archive/2026-05-11-enforce-automatic-orchestration-routing/`;
  - `openspec/changes/archive/2026-05-11-enforce-active-selector-status-helper/`;
  - `openspec/changes/archive/2026-05-12-enforce-hard-routing-directive-adoption/`;
  - `openspec/changes/archive/2026-05-13-enforce-capability-switch-chain/`;
  - `openspec/changes/archive/2026-05-13-enforce-custom-agent-toml-schema/`;
  - `openspec/changes/archive/2026-05-13-enforce-expert-lifecycle-wait-pacing-evidence/`;
  - `openspec/changes/archive/2026-05-13-enforce-orchestration-trace-evidence-validator/`;
  - `openspec/changes/archive/2026-05-13-extend-orchestration-activation-checker-coverage/`;
  - `openspec/changes/archive/2026-05-14-enforce-agent-skill-profile-surface-boundaries/`;
  - `openspec/changes/archive/2026-05-14-enforce-delegation-wait-discipline/`;
  - `openspec/changes/archive/2026-05-14-enforce-durable-artifact-state-surfaces/`;
  - `openspec/changes/archive/2026-05-14-enforce-effective-lane-fit-evidence/`;
  - `openspec/changes/archive/2026-05-14-enforce-fanout-write-ownership-evidence/`;
  - `openspec/changes/archive/2026-05-14-enforce-leader-session-scope-evidence/`;
  - `openspec/changes/archive/2026-05-14-enforce-orchestration-checker-ci-coverage/`;
  - `openspec/changes/archive/2026-05-14-enforce-role-directive-routing-evidence/`;
  - `openspec/changes/archive/2026-05-15-harden-global-automatic-collaboration-default/`;
- remote publication: separate from local plan completeness and still subject to explicit GitLab/GitHub publication authorization.

Residual boundaries that remain true after completion:

1. native `spawn_agent` is still subject to the live platform/tool contract; when blocked, the trace must say `experts=blocked:platform_subagent_invocation_constraint` and then use a valid durable lane or main-session takeover;
2. LangGraph being the ready default backend does not mean a persistent team is running; durable workflow and team launch remain threshold-gated;
3. generated files under the user-level Codex directory can still require an installer refresh to pick up source-template changes, and repository templates remain the source of truth;
4. future task-specific orchestration decisions still need activation traces, threshold evidence, and checker-backed evidence where applicable.

## 1. Background

This repository already expects the main Codex session to automatically decide whether to use native experts, durable workflow, persistent team, `native_omx`, and LangGraph. The user should not need to repeat "use experts / durable_team / persistent team as much as possible" at the start of every task.

Recent log review exposed three issues:

1. A routing trace used "the user did not request parallelism/subagents" as a reason not to launch experts or durable team. That is an invalid reason.
2. After expert/subagent timeout, the log did not preserve a clear enough evidence chain between "continued without the result" and later "result absorbed" wording.
3. LangGraph is already installed/enabled/selected/ready in user-level state, but task traces can still mix up "backend is on" with "this task needs a team".

## 2. User-confirmed hard rules

### 2.1 Capability dependency chain

The capability chain is a hard dependency chain, not a soft preference:

```text
subagent_routing enabled/available
  -> only then may oh-my-codex / OMX be enabled
    -> only then may LangGraph be enabled
      -> when LangGraph is ready, it remains the default durable backend
```

Rule expression:

```text
if subagent_routing == off:
    oh_my_codex = off
    langgraph = off

if oh_my_codex == off:
    langgraph = off

if langgraph == on:
    require subagent_routing != off
    require oh_my_codex == on

if durable_orchestration_backend == langgraph:
    require langgraph == on
```

### 2.2 LangGraph default backend stays on

When user-level state satisfies:

```text
subagent_routing != off
oh_my_codex = on
langgraph = on
langgraph_ready = true
```

LangGraph is the default durable backend. Task complexity decides whether to start a durable workflow or persistent team; it does not decide whether the LangGraph backend is enabled.

### 2.3 Automatic collaboration does not depend on a user reminder

The following reasons are forbidden as justification for not using experts / durable_team / persistent team:

```text
the user did not request parallelism
the user did not request subagents
the user did not mention experts/durable_team/persistent team
```

Correct decision inputs are:

- task phase;
- whether the task is bounded multi-face research;
- whether it crosses modules, interfaces, or trust boundaries;
- whether there are two or more independent execution slices;
- whether the plan is frozen;
- whether backend and preflight are ready;
- whether a higher-authority or runtime-surface blocker exists;
- whether the main session can safely take over locally.

### 2.4 Expert timeout handling

A timed-out key-path expert/subagent must not be treated as evidence. The main session must choose one of these paths:

1. continue bounded waiting when there is progress evidence;
2. respawn a narrower and more explicit expert task;
3. when eligible, hand off to LangGraph durable workflow / durable lane;
4. when durable/persistent team is unsuitable or blocked, explicitly take over the missing review in the main session.

The final report must distinguish:

- `expert returned and absorbed` - the expert result is available and was used as evidence;
- `expert timed out; not used as evidence` - the expert result did not return and must not support final claims;
- `main session took over verification` - the leader completed the missing review directly;
- `durable_team blocked by <reason>` - a durable or persistent team was considered but could not launch;
- `backend_default=langgraph, backend_ready=true` - records that LangGraph is the default ready backend, not proof that a persistent team was launched.

### 2.5 2026-05-24 prompt-independent parity and evidenceguard gap

The 2026-05-24 session retrospective confirmed that Section 2.3 already says automatic collaboration does not depend on a user reminder, but the implemented evidence surface is still not enough to prove that the same complex task always produces the same collaboration path with and without the phrase "use experts / durable_team / persistent team". This section therefore records a hardening gap, not a user-prompt problem.

Handling principles:

- When an explicit collaboration phrase is present, treat it as a hard routing directive or strong reminder; when absent, never use that absence as a reason to skip the activation check.
- Do not claim prompt-independent parity from policy text alone; require fixtures, checkers, or persisted audit evidence.
- Durable/persistent team runtime claims require active selector, team manifest, worker heartbeat, worker lifecycle record, and close/absorb record.
- Expert/subagent use must be traceable through `spawn / wait / timeout / result / close / absorbed`.
- After a LangGraph workflow is completed or submitted, repo-local state must not keep an unexplained stale `running` state.
- Until these checkers exist, final reports must distinguish policy expectation from actual runtime evidence.

The detailed Phase 4 implementation content has been merged into section 20 of this document; the standalone parity plan has been deleted. This document is the only implementation-plan source of truth for that hardening work, and Phase 4 is still not evidence that a durable or persistent team is currently running.

## 3. Activation trace format

Activation check must re-run on new session, session reload, Codex restart, resume, phase change, user "continue", expert timeout, `.omx` durable-state detection, or expansion to two or more execution slices.

Required trace fields:

```text
Routing trace:
phase=<phase>
capability_chain=subagent:<auto|manual|off> > omx:<on|off> > langgraph:<on|off>
backend_default=<langgraph|native_omx|none>
backend_ready=<true|false>
experts=<none|analystxN|architect|writer|verifier|blocked:<reason>|...>
durable_workflow=<not_needed|candidate|selected|blocked|running>
persistent_team=<not_needed|candidate|selected|blocked|running>
why=<concrete reason>
```

Use ASCII `analystxN` in the canonical English file; localized documents may render it as `analyst x N` or another localized form.

## 4. Automatic routing decision matrix

| Trigger | Experts | Durable workflow | Persistent team | Main-session fallback |
| --- | --- | --- | --- | --- |
| Single low-risk file edit | none unless specialized review is needed | not needed | not needed | edit and verify locally |
| Bounded multi-face research | analystxN first | candidate only after research fan-in creates phased execution | not before plan freeze | synthesize fan-in locally |
| Cross-module architecture or shared interface | architect, optionally security-reviewer | candidate | after frozen plan and two or more independent slices | leader writes integration contract |
| Large documentation rewrite | analyst/writer/verifier as needed | candidate if multi-phase or checkpointed | only with independent write slices | leader-owned integration |
| Behavior-changing multi-file work | test-engineer and verifier | candidate | after slice isolation | local gate and direct review |
| Security, permissions, secrets, payments, untrusted input | security-reviewer | candidate | only after trust boundaries are mapped | leader blocks release until reviewed |
| Key-path expert timeout | respawn narrower expert or alternate role | selected when LangGraph-ready checkpointed handoff is useful | only if preflight passes | main session takes over and states evidence source |

## 5. Hard routing directives and smallest-sufficient role selection

Explicit routing directives are hard inputs to the activation check, not soft preferences.

Directive rules:

- user requests for `omx`, `LangGraph`, `resume`, `continue`, `parallel`, `experts`, `durable_team`, or `persistent team` must trigger an activation check;
- explicit `omx` or `LangGraph` requests must be treated as hard routing directives for the current task flow;
- when the capability chain, preflight, and task threshold are satisfied, the session must actually adopt the selected lane (`selected` or `running`) instead of staying in explanation-only mode;
- when the requested lane is not adopted, the trace must state the concrete blocker or unmet threshold in `why`, such as `blocked:backend_not_ready`, `blocked:platform_subagent_invocation_constraint`, or `threshold_not_met:no_frozen_plan`;
- `resume` and `continue` trigger retrofit and state re-read; they do not by themselves force a durable team launch unless thresholds are met.

Smallest-sufficient expert role selection:

| Role | Select when | Default boundary |
| --- | --- | --- |
| `analyst` | outcome, non-goals, or acceptance target is unclear; two or more major ambiguities remain; bounded multi-face research needs first-round fan-out | analyst-only first round for bounded multi-face research |
| `researcher` | external docs, dependency behavior, version-sensitive facts, or official-source verification are needed | separate from implementation when the task starts open-ended |
| `architect` | two or more modules, trust boundaries, shared interfaces, migrations, or non-local design decisions are involved | after analyst fan-in for bounded multi-face research |
| `planner` | two or more execution slices, serial hotspots, rollout ordering, or dependency chains exist | after architecture/context is clear |
| `debugger` | blocking failure, regression, reproducible defect, or stabilization-heavy repair exists | stabilization lane; do not use as a generic executor |
| `verifier` | final acceptance, behavior-changing work, multi-file integration, or multi-worker integration needs validation | always after multi-worker integration |
| `test-engineer` | critical-path behavior changed, tests are missing, flaky, or broad regression risk exists | test strategy and evidence, not product ownership |
| `security-reviewer` | auth, secrets, permissions, untrusted input, code execution, external trust boundaries, or payments are touched | blocks release until reviewed |
| `writer` | user-facing behavior, setup, migration, operator workflow, or document-finalization work is needed | after analyst fan-in for bounded multi-face research |
| `bug-finder` / `bug-rebutter` / `bug-judge` | contested, noisy, or high-volume bug triage remains after normal verification | burst, read-only, leader-side; persist survivors instead of workers |

Use the smallest sufficient expert set. Do not add roles because they are available; add them only when the trigger is present and the output will materially advance the current phase.

## 6. Native agents, skills, profiles, and follow-up thread boundaries

Native Codex subagents, workflow skills, plugin-provided skills, and profile helpers are different surfaces and must not be collapsed.

Registry and loading rules:

- native reusable role definitions live under the user-level agents directory or repo-local `.codex/agents/`;
- every standalone custom agent TOML must define at least `name`, `description`, and `developer_instructions`;
- skills load from installed `SKILL.md` files and are invoked through `$name` or AGENTS.md routing; skills are not native subagents;
- plugin modules and profile helper hard-load/soft-load change which procedural instructions are visible, but they do not by themselves start durable workers or satisfy persistent-team thresholds;
- when long generated instructions are needed for launcher or profile surfaces, prefer file-backed references such as `model_instructions_file` rather than long inline `-c developer_instructions=...` payloads.

Follow-up thread rules:

- if later follow-up work is needed after a completed expert was absorbed and closed, spawn a fresh agent and pass the needed context;
- reuse a preserved thread only when the user explicitly asked to preserve that thread or when the plan records an intentional preserved-thread reason;
- do not treat a skill invocation, plugin profile, or preserved transcript as evidence that an expert result was returned; evidence must come from an explicit expert result, durable checkpoint, local verification, or cited source.

Selector source rule:

- automatic durable-team routing reads `.omx/state/selectors/active.json` as the shared repo-local activation selector;
- compatibility records may be inspected for context, but they do not authorize unmanaged team adoption by themselves.

## 7. Leader session and adoption-scope boundaries

The current main Codex CLI session remains the leader for the task flow. The orchestration design must not create or require a separate persistent leader pane to replace the current main session.

Leader-session rules:

- the main session owns activation checks, role selection, worker brief quality, fan-in, evidence labeling, final integration, and final user reporting;
- subagents, durable workers, skills, plugin profiles, and LangGraph nodes are execution surfaces under leader control, not independent release authorities;
- local mainline or publication decisions remain user-authorized release decisions, not automatic worker decisions;
- if multiple workers are used, the leader owns conflict resolution, evidence sufficiency, and final acceptance claims.

Adoption-scope rules:

- the orchestration decision target is the current task flow, not whether the repository is newly created;
- existing projects with new sessions should follow the current user-level orchestration policy;
- existing live sessions must retrofit on reload, restart, resume, continue, phase change, durable-state detection, or capability-state change;
- Codex startup itself does not auto-launch a durable team; durable launch remains a threshold-gated later action inside the session;
- resumed legacy Codex sessions are compatibility-scoped: they may continue follow-up discussion but must not override current repository governance or current capability-chain policy.

Trace requirement: when a session chooses not to adopt durable workflow or persistent team during startup or first activation, the trace must say which threshold was not met rather than implying that startup cannot use orchestration at all.

## 8. Base layer, wrapper layer, and effective lane choice

Native Codex remains the base layer. oh-my-codex, native OMX, skills, profile helpers, and LangGraph add workflow and durable-state behavior around Codex; they do not replace Codex.

Layer and switch rules:

- user-level capability switches must be read as a chain: `subagent_routing=auto`, `oh_my_codex=on`, `langgraph=on` in the current intended state;
- `langgraph=on` requires `oh_my_codex=on` and routing availability;
- `oh_my_codex=off` disables LangGraph availability;
- `subagent_routing=off` disables higher orchestration layers;
- when `durable_orchestration_backend=langgraph` and `langgraph_ready=true`, LangGraph is the default durable backend state.

Effective lane rules:

- the default backend state does not remove task-level lane choice;
- prefer `native_omx` for worker-centric durable execution, worktree isolation, mailbox flow, and direct worker lifecycle control;
- prefer LangGraph for graph-shaped multi-phase execution, checkpoint-driven recovery, interrupt/resume approval gates, frozen briefs, and persisted survivor queues;
- effective lane choice may vary per task flow, but one durable task still uses one backend family at a time;
- backend-family switching remains explicit and must be recorded as a close/handoff, not hidden as a silent lane change.

## 9. Durable-team threshold map

Durable team launch is threshold-gated. The presence of `backend_default=langgraph` and `backend_ready=true` means the durable backend is available; it does not mean a persistent team must be running.

Phase map:

| Phase | Durable team decision | Worker shape | Required trace reason |
| --- | --- | --- | --- |
| define-target | `persistent_team=not_needed` | none | target and acceptance boundary are still being defined |
| read-context | `persistent_team=not_needed` | none | context gathering is still leader-owned or analyst-only |
| freeze-plan | `persistent_team=not_needed` | none | plan is not frozen yet |
| verify-accept | `persistent_team=not_needed` by default | verifier/test-engineer experts as needed | acceptance verification is not itself a multi-worker execution slice |
| execute-parallel | `persistent_team=selected` when the plan is frozen and there are 2+ independent execution slices | 2 `team-executor` workers; scale to 3 workers at 3+ slices | the named slice count and ownership boundaries triggered team launch |
| integrate-converge | `persistent_team=selected` when there are 2+ independent integration/convergence slices | 2 `team-executor` workers; leader owns final integration | the named convergence slices are independent enough to parallelize |
| stabilize | `persistent_team=selected` when there is at least 1 blocking failure, regression, or stabilization issue | 2 `debugger` workers by default | the named blocking issue triggered debugger-lane stabilization |

First-turn reporting rule:

- if `omx team` / durable team is not selected on the first activation check, the trace must state which threshold was not met;
- if it is selected, the trace must state which threshold triggered it;
- use the approved automatic durable-team launcher, such as `omx-team-auto.ps1`, instead of raw `omx team` when the threshold is met and no blocker exists;
- do not auto-adopt unmanaged existing teams; report them as existing state requiring explicit adoption or cleanup.

Bounded multi-face research remains analyst-fanout-first: first round uses homogeneous `analystxN`; do not include `architect`, `planner`, or `writer` in the default first round. Escalate to those roles only after analyst fan-in shows an architecture, execution-ordering, or document-finalization layer.

## 10. Delegation design and leader wait discipline

Delegation must shorten the path to a correct result; it must not become a reflexive background wait.

Before delegating:

- identify the immediate critical-path task that the leader should do locally now;
- delegate only concrete, bounded, self-contained sidecar work that materially advances the main task;
- do not delegate urgent blocking work when the next leader action depends on that result;
- do not duplicate work between leader and experts, or between experts;
- avoid multiple delegate calls on the same unresolved thread unless the follow-up is genuinely different and necessary.

While delegated work is running:

- continue meaningful non-overlapping leader work immediately;
- do not redo the delegated task locally unless the delegated lane is timed out, stalled, or explicitly abandoned and the leader records takeover;
- call `wait_agent` sparingly and only when the leader is blocked on that result for the next critical-path step;
- if a worker returns code or documents, quickly review, integrate, or refine rather than treating the result as automatically accepted.

For coding delegation:

- assign explicit file/module ownership and expected output;
- tell workers they are not alone in the codebase and must not revert others' edits;
- require workers to list changed paths in their final answer;
- keep delegated write sets disjoint unless the leader serializes the hotspot.

## 11. Codebase exploration, code-change delegation, and durable state surfaces

Read-only exploration, code-changing worker execution, and durable-state persistence have different evidence and ownership rules.

Exploration and coding delegation rules:

- use `explorer`-style codebase search for specific, well-scoped read-only questions, symbol mapping, or file discovery;
- do not use read-only exploration as a substitute for an implementation worker when a bounded code change is clear and safe to delegate;
- for coding tasks, prefer delegating concrete code-change worker subtasks over read-only explorer analysis when the worker can make a bounded patch in an isolated ownership area;
- when the leader already has enough local context for the critical path, keep the work local rather than delegating a blocking read-only exploration task;
- explorer results can inform routing and briefs, but final implementation evidence still needs local verification, tests, or reviewed worker patches.

LangGraph entrypoint and repo-local state rules:

- when the task needs graph phases, checkpoint gates, frozen briefs, survivor queues, or tracked LangGraph thread state, use LangGraph entrypoints and repo-local `.omx/state/langgraph/` runtime state;
- repo-local `.omx/state/langgraph/backend.json` may be inspected as backend context;
- `.omx/state/team/codex-auto-managed-team.json` may be inspected as compatibility context;
- `.omx/state/selectors/active.json` remains the active selector authority for automatic durable-team adoption;
- durable artifacts, frozen briefs, and persisted survivor queues must be written to repo-local state or documented artifact paths, not only kept in transient chat context.

## 12. Expert lifecycle, bounded wait, and provider backpressure

Expert and subagent use must be leader-owned from launch through fan-in and cleanup.

Lifecycle rules:

- wait in bounded windows, not indefinitely;
- start with about 30 seconds for the first wait window;
- extend to about 60 seconds for bounded reviews;
- extend to about 120 seconds for deeper architect, verifier, or researcher work;
- keep total wait for a single expert bounded at about 180 seconds unless the user explicitly asks to preserve or continue that thread;
- require concise progress/liveness updates about every 30 seconds or at major milestones, including current step, completed work, next step, and blockers;
- if two consecutive progress checks stay quiet, treat the expert as stalled and inspect, redirect, respawn a narrower task, hand off to a durable lane, or have the main session take over;
- after `wait_agent` returns a completed result and the leader absorbs it, close the completed agent by default;
- keep a completed agent open only when the user explicitly asks to preserve that thread.

A timeout, stall, or upstream wait is not evidence. Final reports must say which lane supplied evidence and which lane timed out, stalled, was closed after absorption, or was taken over by the main session.

Provider pacing and backpressure rules:

- the provider proxy enforces a shared upstream pacing budget of at most 10 true upstream provider forwards per rolling 1-minute window;
- when the budget is saturated, upstream-bound requests wait for a slot instead of treating the condition as a local fatal error;
- upstream pacing alone is not a reason to avoid LangGraph, native OMX, or native experts;
- prefer local-first phases, deterministic local checks, and bounded fan-out when many agent steps may hit the provider;
- if pacing materially affects execution, report it as `backpressure:upstream_pacing` or an equivalent named condition, not as missing user intent.

## 13. Fan-out bounds, write ownership, and backend-family boundary

Native expert use is explicit leader-side spawning and leader-owned fan-in. Do not imply that raw Codex automatically spawns specialist roles by default.

Fan-out bounds:

- keep native subagent fan-out bounded; managed defaults are `agents.max_threads=6` and `agents.max_depth=1`;
- prefer parallel fan-out for read-heavy, bounded, independent work;
- keep implementation local when the next critical-path step depends on the result;
- for write-heavy parallel execution, require explicit file/module ownership, disjoint write sets, hotspot serialization, and leader-owned final integration;
- workers must be told they are not alone in the codebase and must not revert or overwrite other active owners' changes.

Backend-family boundary:

- one durable task uses one backend family at a time;
- backend-family switching must be explicit and recorded in trace or handoff notes;
- when LangGraph is ready and selected as default, using `native_omx` for a durable lane requires a named reason, such as worker-centric durable execution, worktree isolation, mailbox flow, or direct worker lifecycle control;
- prefer LangGraph for graph-shaped multi-phase execution, checkpoint-driven recovery, interrupt/resume approval gates, frozen briefs, and persisted survivor queues;
- do not mix `native_omx` worker lifecycle and LangGraph checkpoint state inside the same durable task without closing or explicitly handing off the previous backend family.

Open-ended work keeps research and implementation separate: use analyst/research roles for discovery and only move to executor/team execution after the plan, ownership, and acceptance evidence are frozen.

## 14. Handoff, adversarial review, and adjacent-runtime boundaries

Open-ended research and contested bug review need explicit handoff boundaries so that temporary expert lanes do not become unmanaged persistent workers.

Research handoff rules:

- keep research and implementation in different roles when the task starts open-ended;
- after research fan-in, persist the result as a frozen implementation brief before implementation starts;
- continue implementation in a fresh execution context or clearly marked execution phase, using the frozen brief as the contract;
- the brief must include scope, non-goals, acceptance evidence, ownership boundaries, and unresolved risks.

Adversarial review rules:

- `bug-finder`, `bug-rebutter`, and `bug-judge` are burst-review roles, leader-side and read-only by default;
- use them for contested, noisy, or high-volume bug triage only after normal verification still leaves disagreement or a broad candidate bug set;
- do not keep the bug triad alive as persistent workers;
- persist remaining candidate issues as an adversarial-review survivor queue and route them to a debugger lane when repair work is needed;
- final reports must distinguish confirmed bugs, rebutted candidates, unresolved survivors, and debugger-lane follow-up.

Durable-state and adjacent-runtime boundaries:

- use `codex-durable-state-status.ps1` as the canonical read-only cross-backend durable-state summary for this repository or worktree;
- do not treat compatibility records alone as permission to auto-adopt unmanaged teams;
- prefer the term OpenHands over archived OpenDevin terminology;
- treat LangGraph, AutoGen, and CrewAI as general programmable orchestration runtimes, not as native Codex-subagent equivalents;
- a LangGraph graph may coordinate phases, checkpoints, approvals, and survivor queues, but native Codex experts still require explicit leader-side spawning and fan-in.

## 15. Backend, workflow, and team semantics

These terms must not be collapsed:

- `backend_default` - the default durable backend selected by user-level capability state.
- `backend_ready` - whether the selected backend is installed, enabled, selected, and ready.
- `durable_workflow` - whether this task should use checkpointed or graph-shaped durable execution.
- `persistent_team` - whether a multi-worker persistent team should be launched for this task.

When LangGraph is ready, it is the default backend. A small task may still have `durable_workflow=not_needed` and `persistent_team=not_needed`. That means the task does not need those execution surfaces; it does not mean LangGraph is off.

## 16. Inspection baseline and current review result

Read-only inspection on 2026-05-11 established the original capability baseline:

```text
C:\Users\lenovo\.codex\state\user-level-team-mode.json:
  subagent_routing = auto
  oh_my_codex = on
  langgraph = on
  durable_orchestration_backend = langgraph
  langgraph_ready = true

C:\Users\lenovo\.codex\venvs\langgraph-py312:
  exists
  langgraph importable
  langgraph_cli available

D:\PythonProject_langgraph\.omx\state\langgraph\backend.json:
  backend = langgraph
  status = running

D:\PythonProject_langgraph\.omx\state\selectors\active.json:
  missing at inspection time
```

Interpretation: the user-level LangGraph backend was available and should be treated as the default backend. A missing repo-local active selector is a state-refresh or reporting gap; it must not be interpreted as LangGraph backend unavailability.

Current 2026-05-15 review result:

- The implementation-plan frontmatter is `version: 0.17`, `status: active`, and `date: 2026-05-15`.
- Section 0 records the plan-completion snapshot and lists the archived implementation slices.
- Section 20 marks the planned implementation phases as complete for the agreed baseline.
- Section 21 records the implemented scope and closure evidence.
- `tools/check_implementation_plan_rules.py --root . --json` passes for the bilingual implementation-plan registry.
- `tools/run_openspec_guard.py --root . --tool codex --json` and `tools/check_worktree_session_hygiene.py --root . --json` passed after the 2026-05-15 local-main integration of version 0.17.

Conclusion: this plan is complete for the currently agreed baseline. It remains active as a living governance and acceptance surface; future gaps should be handled through new bounded changes.

## 17. Active selector handling

When `.omx/state/selectors/active.json` is missing but the user-level capability state says `durable_orchestration_backend=langgraph` and `langgraph_ready=true`, the session must not silently downgrade to `native_omx` or `none`.

Required behavior:

1. report `backend_default=langgraph` and `backend_ready=true`;
2. report `active_selector=missing` as a repo-local state-refresh gap;
3. refresh or create the selector through the approved helper when implementation work requires a tracked durable thread;
4. if no helper exists yet, record the missing helper as an implementation gap, not as backend unavailability.

## 18. Low-risk iteration and local integration boundary

For repeated low-risk refinements inside an already confirmed scope, the main session may proceed without asking for per-iteration approval when all of the following are true:

- the change is limited to documentation, governance text, local check metadata, or equivalent non-runtime surfaces;
- the affected files are already inside the agreed topic boundary;
- `experts=none`, `durable_workflow=not_needed`, and `persistent_team=not_needed` are justified by the activation check;
- local gate and local MR review pass after the intended commit;
- the feature worktree is clean and local `main` is not behind `gitlab/main`.

In that case, the session may commit the refinement and fast-forward or merge it into local `main` as part of the same low-risk loop. This avoids forcing the user to approve the same simple iteration repeatedly, including repeated review/update requests against this plan.

Explicit user approval is still required for:

1. pushing to GitLab or GitHub;
2. creating, updating for publication, or merging a GitLab MR;
3. syncing GitHub from GitLab or local `main`;
4. destructive actions such as hard reset, force push, broad deletion, or cleanup outside the agreed workspace;
5. scope expansion into runtime code, launcher behavior, CI wiring, security boundaries, or broad multi-file implementation;
6. integrating when local gate or local MR review failed;
7. write-heavy parallel execution with potential ownership conflicts.

This local-merge permission does not weaken the publication workflow. It only defines the local execution boundary for simple, already-authorized iterations. Remote publication remains a separate decision.

## 19. Higher-authority and runtime-surface blockers

Automatic orchestration is the default policy, but live execution must still obey higher-authority instructions, the current tool contract, and actual runtime-surface availability. If a task would normally select an expert, durable workflow, or persistent team but the surface cannot be invoked, the trace must report a named blocker rather than rephrasing the decision as user preference.

Valid blocker examples include:

- `blocked:platform_subagent_invocation_constraint` - the live tool contract does not allow the session to spawn native subagents for this turn;
- `blocked:helper_missing` - the approved durable or selector helper has not been implemented or installed;
- `blocked:preflight_failed` - the lane was selected but a concrete preflight check failed;
- `blocked:write_ownership_conflict` - write-heavy parallel execution would overlap with another active owner;
- `blocked:backend_not_ready` - the required backend is not installed, enabled, selected, or ready.

Required fallback behavior:

1. if the execution surface is genuinely not needed, report `not_needed` and keep the task local;
2. if the surface is needed but blocked, report `blocked:<reason>` and choose respawn through an available surface, durable handoff, or explicit main-session takeover;
3. never turn a platform or helper blocker into the forbidden reason "the user did not request subagents/parallelism";
4. final reports must separate `not_needed`, `selected/running`, `blocked`, and `main_session_takeover` evidence.

The canonical activation trace therefore permits expert blockers:

```text
experts=<none|analystxN|architect|writer|verifier|blocked:<reason>|...>
```

## 20. Implementation phases

### Phase 0 - Record and protect the plan - status: complete

Completed outcomes:

- Added this bilingual plan and registered it as an active implementation plan.
- Ignored local transcript logs such as `log202605111306.md`.
- Kept the canary guard aligned with root `.gitignore` local-log exclusions so ignored transcripts do not break local gate.

### Phase 1 - Policy surfaces - status: complete

Completed outcomes:

- Updated `AGENTS.md`.
- Updated `docs_bilingual/project_startup_summary.*`.
- Added and iterated bilingual orchestration activation policy documents.
- Updated team-mode, quick-reference, and LangGraph-related policy surfaces where needed.
- Added the global automatic-collaboration default to generated user-level team-mode source templates so future installer refreshes preserve it.

### Phase 2 - Script-backed enforcement - status: complete for the planned baseline

Completed outcomes include checker or test coverage for:

- forbidden missing-reminder routing reasons;
- durable-team phase thresholds and first-activation threshold explanations;
- capability-chain consistency;
- expert-timeout evidence claims, completed-agent closure, bounded wait windows, liveness/stall handling, and upstream pacing labels;
- fan-out bounds, write ownership isolation, leader-side spawning language, and one-backend-family durable tasks;
- frozen research handoff briefs, adversarial-review survivor queues, adjacent-runtime terminology boundaries, and durable artifact/state surfaces;
- hard routing directives, actual adoption versus explanation-only mode, and smallest-sufficient role selection;
- native-agent versus skill/profile/plugin boundaries, custom agent TOML fields, fresh follow-up agent use, and selector-source handling;
- main-session leader ownership, no separate persistent leader pane, startup non-autolaunch, task-flow scoped adoption, and legacy-session compatibility boundaries;
- native Codex as base layer, oh-my-codex as wrapper/workflow layer, capability-switch chain values, and effective lane choice between `native_omx` and LangGraph;
- delegation design quality, critical-path local work, non-overlapping leader work while waiting, duplicate-work prevention, and sparse `wait_agent` use;
- explorer versus code-change worker boundaries, LangGraph entrypoints, repo-local `.omx/state/langgraph/` state, compatibility record usage, and durable artifact persistence;
- selector refresh/status reporting when repo-local `.omx/state/selectors/active.json` is missing.

### Phase 3 - Runtime integration - status: implemented as source-of-truth and generated-template enforcement

Completed outcomes:

- Startup and governance surfaces require activation traces on new sessions, session reloads, Codex restarts, resumed sessions, phase changes, `continue`, `.omx` state detection, and expert timeout/stall events.
- LangGraph-ready sessions must report LangGraph as the default durable backend.
- Managed user-level team-mode templates now carry the global automatic-collaboration default.

Operational caveat: live platform constraints can still block native expert spawning, and durable/persistent-team launch still requires task thresholds. The completed implementation enforces reporting and fallback behavior; it does not bypass tool contracts or force every task into a team.

### Phase 4 - Prompt-independent collaboration parity hardening - status: planned follow-up

Phase 4 does not reopen the completed Phase 0-3 baseline; it only addresses the gap found during the 2026-05-24 retrospective. The former standalone Phase 4 subplan has been merged into this section and deleted, making this document the only Phase 4 implementation-plan source of truth.

#### Current Session Finding

Two user instructions had the same business scope. One included the explicit phrase "use experts / durable_team / persistent team"; the other did not. The final document result is now aligned, but the session evidence does not prove that the no-phrase instruction independently produced the same collaboration path. The repository policy already says automatic collaboration must not depend on that phrase, so the missing piece is an executable parity guard and lifecycle audit surface.

This plan is a future implementation plan, not runtime evidence. It does not prove that a durable team or persistent team is running.

#### 2026-05-25 Granularity Review Conclusion

This plan needed refinement. The previous draft covered the major direction, but was not implementation-ready because:

1. It used placeholder paths such as `openspec/changes/unfixed-change-id/...`.
2. The four checker input fixtures, output fields, failure semantics, and pass semantics were underspecified.
3. It did not encode "the prompt phrase may only mark a hard directive, not change the task-shape threshold decision" as a testable contract.
4. Durable/persistent evidenceguard did not distinguish evidence needs for `selected`, `running`, `complete`, `not_needed`, and `blocked`.
5. Expert lifecycle listed event names without defining JSONL fields, result references, and timeout-as-evidence failures.
6. LangGraph `running` release rules lacked minimum fields for thread/workflow/job state surfaces.
7. The verification matrix did not specify how each new tool is wired into `tools/run_openspec_guard.py`, `tools/ci/ci_test_manifest.json`, and local MR review.

This revision turns those gaps into executable granularity. It is still an implementation plan, not runtime evidence; it does not prove that a durable team or persistent team is currently running.

#### Scope

In scope:

- Prompt-independent routing parity fixtures.
- Durable/persistent team evidence guard.
- Expert lifecycle audit records for `spawn / wait / timeout / result / close / absorbed`.
- LangGraph state completion/release checks so `running` does not remain after submitted work is complete.
- Timeout and provider-pacing treatment as non-evidence.
- Documentation and guard wiring updates.

Out of scope:

- Replacing native Codex subagents.
- Treating skills or plugin profiles as native experts.
- Auto-launching durable teams at startup.
- Remote publication without explicit user approval.

#### Planned File Map

Use this fixed OpenSpec change id for later implementation:

- change id: `enforce-prompt-independent-collaboration-parity`
- recommended implementation branch: `enforce-prompt-independent-collaboration-parity`
- recommended worktree: `.worktrees/enforce-prompt-independent-collaboration-parity`

| Path | Action | Responsibility |
| --- | --- | --- |
| `openspec/changes/enforce-prompt-independent-collaboration-parity/proposal.md` | Create | Define the bounded change, non-goals, and acceptance criteria. |
| `openspec/changes/enforce-prompt-independent-collaboration-parity/tasks.md` | Create | Track implementation completion. |
| `openspec/changes/enforce-prompt-independent-collaboration-parity/specs/codex-user-level-orchestration-activation-policy/spec.md` | Create | Add prompt-independent parity, evidenceguard, lifecycle audit, and LangGraph release requirements. |
| `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md` | Modify | Explain prompt-independent collaboration and evidence boundaries. |
| `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md` | Modify | Chinese companion update. |
| `tools/check_orchestration_prompt_independent_collaboration_parity.py` | Create | Validate phrase/no-phrase routing parity fixtures. |
| `tools/check_durable_persistent_evidence_guard.py` | Create | Reject durable/persistent claims without selector/manifest/heartbeat/worker evidence. |
| `tools/check_expert_lifecycle_audit.py` | Create | Validate expert lifecycle audit records. |
| `tools/check_langgraph_state_release.py` | Create | Detect stale `running` state after completion/release. |
| `test/check_orchestration_prompt_independent_collaboration_parity.test.py` | Create | Unit tests for parity checker. |
| `test/check_durable_persistent_evidence_guard.test.py` | Create | Unit tests for evidenceguard. |
| `test/check_expert_lifecycle_audit.test.py` | Create | Unit tests for lifecycle audit. |
| `test/check_langgraph_state_release.test.py` | Create | Unit tests for LangGraph release checks. |
| `test/fixtures/orchestration_prompt_independent_collaboration_parity/` | Create | Paired fixtures with and without explicit collaboration phrases. |
| `test/fixtures/durable_persistent_evidence_guard/` | Create | Durable/persistent claim and evidence fixtures. |
| `test/fixtures/expert_lifecycle_audit/` | Create | Expert lifecycle JSONL fixtures. |
| `test/fixtures/langgraph_state_release/` | Create | LangGraph state fixtures. |
| `tools/run_openspec_guard.py` | Modify | Wire the new checkers into the guard sequence. |
| `tools/ci/ci_test_manifest.json` | Modify | Register new unit tests. |
| `docs_bilingual/docs_registry.yaml` | Modify | Register this plan and any new governance companions if needed. |

#### Process-Group Operating Model

| Process group | Inputs | Tools and Techniques | Outputs |
| --- | --- | --- | --- |
| Initiating | Session retrospective, current governance policy, user requirement for automatic collaboration | Problem framing, evidence gap analysis, non-goal review | Change proposal, acceptance criteria, explicit non-claims |
| Planning | OpenSpec change, file map, current checker patterns, fixture requirements | Slice decomposition, owner mapping, test-first design, timeout budget review | Frozen implementation plan, disjoint tasks, validation matrix |
| Executing | Frozen plan, worktree, OpenSpec delta, tests | TDD, Python checkers, JSON fixtures, local guard wiring, bounded expert review when useful | Checkers, tests, docs updates, changed-path list |
| Monitoring and Controlling | Test output, guard output, routing fixtures, lifecycle records | Diff review, OpenSpec guard, local CI, expert verifier review, defect triage | Accepted fixes, rejected false claims, residual risk list |
| Closing | Passing gates, clean branch, updated docs registry, archived OpenSpec when complete | Closeout review, local MR review, archive decision, lessons learned | Merge-ready branch, archive or deferral evidence, follow-up backlog |

#### Evidence Contracts

##### Activation Parity Fixture Contract

Paired fixtures must share the same `task_shape_id`; only `prompt_features.explicit_collaboration_phrase` may differ. Recommended paths:

```text
test/fixtures/orchestration_prompt_independent_collaboration_parity/
  same_task_without_phrase.json
  same_task_with_phrase.json
```

Minimum JSON fields:

```json
{
  "case_id": "same_product_lifecycle_refresh_without_phrase",
  "task_shape_id": "product_lifecycle_refresh_business_pmp_multi_doc",
  "prompt_features": {
    "explicit_collaboration_phrase": false,
    "explicit_omx_directive": false,
    "explicit_langgraph_directive": false
  },
  "expected_decision": {
    "phase": "read-context-or-execute-parallel",
    "experts_now": "candidate_or_selected",
    "durable_workflow": "candidate_or_selected_when_threshold_met",
    "persistent_team_threshold": "requires_frozen_plan_and_2plus_slices",
    "backend_default": "langgraph",
    "claim_boundary": "do_not_claim_team_without_evidence"
  }
}
```

Pass condition: fixtures with the same `task_shape_id` agree on `phase`, `experts_now`, `durable_workflow`, `persistent_team_threshold`, `backend_default`, and `claim_boundary`. The explicit phrase may only mark `directive_seen=true`; it must not allow a below-threshold task to be reported as an already-running persistent team.

Fail condition: the explicit phrase causes `persistent_team=running`, skips frozen plan, skips evidenceguard, treats timeout as evidence, or changes backend family without a task-fit reason.

##### Durable/Persistent Evidenceguard Contract

Evidence requirements are state-specific:

| Claimed state | Minimum evidence |
| --- | --- |
| `not_needed` | Activation trace explains the unmet threshold, such as `threshold_not_met:single_execution_slice`. |
| `candidate` | Frozen plan or slice analysis, plus why it has not started. |
| `selected` | Active selector, backend family, passed preflight record, worker ownership plan. |
| `running` | Active selector, team manifest, worker heartbeat, worker lifecycle `started/running` record. |
| `complete` | All `running` evidence plus closed agent record, result summary, and leader absorbed record. |
| `blocked` | Blocker name, evidence for three repeated blocks, and no use of blocked output as completion evidence. |

Recommended fixture structure:

```text
test/fixtures/durable_persistent_evidence_guard/
  invalid_running_missing_heartbeat/
    transcript.json
    .omx/state/selectors/active.json
    .omx/state/team/manifest.json
  valid_complete_team/
    transcript.json
    .omx/state/selectors/active.json
    .omx/state/team/manifest.json
    .omx/state/team/worker-heartbeats/worker-1.json
    .omx/state/team/lifecycle.jsonl
    .omx/state/team/closed-agents/worker-1.json
    .omx/state/team/absorbed-results.jsonl
```

##### Expert Lifecycle Audit Contract

Each expert lifecycle record uses JSONL. Recommended path: `.omx/state/experts/lifecycle.jsonl`, or the same path inside a test fixture. Minimum fields per line:

```json
{
  "event": "spawn",
  "timestamp": "2026-05-25T00:00:00+08:00",
  "agent_id": "agent-001",
  "role": "verifier",
  "nickname": "Bernoulli",
  "task_summary": "review routing parity checker fixtures",
  "status": "started",
  "evidence_disposition": "not_evidence_yet"
}
```

Event ordering requirements:

1. `spawn` must precede `wait`, `timeout`, `result`, `close`, and `absorbed` for the same `agent_id`.
2. A `result` referenced by the final report must have an `absorbed` event for the same `agent_id`.
3. `timeout`, `stall`, and `provider_pacing_wait` may only produce a non-evidence disposition.
4. No new `result` may appear after `close` unless a fresh `spawn` uses a new `agent_id`.

##### LangGraph State Release Contract

Repo-local LangGraph state must not remain unexplained `running` after completion. Minimum state:

```json
{
  "thread_id": "lg-thread-001",
  "workflow_id": "prompt-independent-parity",
  "status": "running",
  "active_work": true,
  "last_heartbeat_at": "2026-05-25T00:00:00+08:00",
  "completion_marker": null,
  "release_marker": null,
  "continue_reason": "worker still processing task 2"
}
```

Fail condition: `completion_marker` exists, or closeout evidence says work is complete, but `status=running`, `release_marker=null`, and `continue_reason` is empty.

Pass condition:

- Active work is still running with a fresh heartbeat; or
- work is completed and state is `complete/released/closed`; or
- state remains `running` with explicit release deferral and unfinished-work evidence.

#### Task 1: OpenSpec Change and Evidence Contract

**Files:**
- Create: `openspec/changes/enforce-prompt-independent-collaboration-parity/proposal.md`
- Create: `openspec/changes/enforce-prompt-independent-collaboration-parity/tasks.md`
- Create: `openspec/changes/enforce-prompt-independent-collaboration-parity/specs/codex-user-level-orchestration-activation-policy/spec.md`

- [ ] **Step 1: Create the OpenSpec proposal**

  Write a proposal that states: automatic collaboration is mandatory by task threshold, not by prompt phrase. The proposal must name four evidence contracts: prompt-independent parity, durable/persistent evidenceguard, expert lifecycle audit, and LangGraph state release.

- [ ] **Step 2: Add normative requirements**

  Add requirements that:
  - phrase/no-phrase fixtures with the same task shape must produce the same activation decision class;
  - durable/persistent team claims require selector, manifest, heartbeat, worker lifecycle, and close/absorb evidence;
  - expert timeout is non-evidence;
  - LangGraph `running` state must be released or completed after submit/close.

- [ ] **Step 3: Validate the change**

  Run:

  ```powershell
  openspec validate enforce-prompt-independent-collaboration-parity --strict
  ```

  Expected: the change validates with no failed requirements.

#### Task 2: Prompt-Independent Routing Parity Checker

**Files:**
- Create: `tools/check_orchestration_prompt_independent_collaboration_parity.py`
- Create: `test/check_orchestration_prompt_independent_collaboration_parity.test.py`
- Create: `test/fixtures/orchestration_prompt_independent_collaboration_parity/same_task_without_phrase.json`
- Create: `test/fixtures/orchestration_prompt_independent_collaboration_parity/same_task_with_phrase.json`
- Modify: `tools/run_openspec_guard.py`
- Modify: `tools/ci/ci_test_manifest.json`

- [ ] **Step 1: Write failing tests**

  Add fixtures for the same task in two forms:
  - without explicit collaboration phrase;
  - with "use experts / durable_team / persistent team".

  Expected behavior: both fixtures classify the same phase, expert need, durable threshold result, and persistent-team evidence state.

- [ ] **Step 2: Implement checker**

  Implement a checker that reads JSON fixtures, groups by `task_shape_id`, and compares `expected_decision.phase`, `experts_now`, `durable_workflow`, `persistent_team_threshold`, `backend_default`, and `claim_boundary`. It fails when the explicit phrase changes the activation decision class without a task-shape difference. Failure output must include `case_id`, `task_shape_id`, field name, left value, and right value.

- [ ] **Step 3: Register guard and tests**

  Add the checker to `tools/run_openspec_guard.py` and the test file to `tools/ci/ci_test_manifest.json`.

- [ ] **Step 4: Run focused tests**

  ```powershell
  python .\test\check_orchestration_prompt_independent_collaboration_parity.test.py
  python .\tools\check_orchestration_prompt_independent_collaboration_parity.py --root . --json
  ```

  Expected: tests and checker pass.

#### Task 3: Durable/Persistent Evidenceguard

**Files:**
- Create: `tools/check_durable_persistent_evidence_guard.py`
- Create: `test/check_durable_persistent_evidence_guard.test.py`
- Create: `test/fixtures/durable_persistent_evidence_guard/invalid_running_missing_heartbeat/`
- Create: `test/fixtures/durable_persistent_evidence_guard/valid_complete_team/`
- Modify: `tools/run_openspec_guard.py`
- Modify: `tools/ci/ci_test_manifest.json`

- [ ] **Step 1: Write failing tests**

  Add negative fixtures where a transcript claims `durable_team=running` or `persistent_team=running` but lacks one or more required evidence files. The checker must fail these fixtures.

- [ ] **Step 2: Implement evidence validation**

  Require evidence for:
  - active selector;
  - team manifest;
  - worker heartbeat;
  - worker lifecycle record;
  - closed agent record, result summary, and final close/absorb record when work is claimed complete.

- [ ] **Step 3: Run focused tests**

  ```powershell
  python .\test\check_durable_persistent_evidence_guard.test.py
  python .\tools\check_durable_persistent_evidence_guard.py --root . --json
  ```

  Expected: false durable/persistent claims fail closed; valid evidence fixtures pass.

#### Task 4: Expert Lifecycle Audit

**Files:**
- Create: `tools/check_expert_lifecycle_audit.py`
- Create: `test/check_expert_lifecycle_audit.test.py`
- Create: `test/fixtures/expert_lifecycle_audit/valid_absorbed_result/lifecycle.jsonl`
- Create: `test/fixtures/expert_lifecycle_audit/invalid_timeout_as_evidence/lifecycle.jsonl`
- Modify: `tools/run_openspec_guard.py`
- Modify: `tools/ci/ci_test_manifest.json`

- [ ] **Step 1: Define lifecycle schema**

  Define required event fields for `spawn`, `wait`, `timeout`, `result`, `close`, and `absorbed`: timestamp, role, agent id, nickname when available, task summary, status, and evidence disposition.

- [ ] **Step 2: Implement checker**

  Fail when a completed expert result is referenced by `final_report_refs.json` without a matching `absorbed` event, when a timed-out/stalled/provider-paced expert is used as accepted evidence, or when the same `agent_id` emits a new `result` after `close`.

- [ ] **Step 3: Run focused tests**

  ```powershell
  python .\test\check_expert_lifecycle_audit.test.py
  python .\tools\check_expert_lifecycle_audit.py --root . --json
  ```

  Expected: complete lifecycle fixtures pass; timeout-as-evidence fixtures fail.

#### Task 5: LangGraph Completion and Release State

**Files:**
- Create: `tools/check_langgraph_state_release.py`
- Create: `test/check_langgraph_state_release.test.py`
- Create: `test/fixtures/langgraph_state_release/valid_active_running/`
- Create: `test/fixtures/langgraph_state_release/valid_released_complete/`
- Create: `test/fixtures/langgraph_state_release/invalid_completed_still_running/`
- Modify: `tools/run_openspec_guard.py`
- Modify: `tools/ci/ci_test_manifest.json`

- [ ] **Step 1: Add state fixtures**

  Add fixtures for:
  - valid running thread with active work;
  - completed thread with released state;
  - invalid completed work still marked `running`.

- [ ] **Step 2: Implement release checker**

  Fail when a thread is marked complete in handoff or closeout evidence but repo-local LangGraph state remains `running` without a release marker or continue reason. Active running state must have active work, a fresh heartbeat, and a continue reason.

- [ ] **Step 3: Run focused tests**

  ```powershell
  python .\test\check_langgraph_state_release.test.py
  python .\tools\check_langgraph_state_release.py --root . --json
  ```

  Expected: stale running state fails; active running state with live work passes.

#### Task 6: Documentation, Validation, and Closeout

**Files:**
- Modify: `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md`
- Modify: `docs_bilingual/governance/codex_user_level_orchestration_activation_policy.zh-CN.md`
- Modify: `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.md`
- Modify: `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md`
- Modify: `docs_bilingual/docs_registry.yaml`

- [ ] **Step 1: Update governance text**

  Add a section that says explicit collaboration phrases are routing directives when present, but their absence is not a reason to skip the activation check.

- [ ] **Step 2: Run validation**

  ```powershell
  git diff --check
  openspec validate --all
  python .\tools\check_precommit_update_archive.py --root . --json
  python .\tools\run_openspec_guard.py --root .
  .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600
  .\tools\ci\local_mr_review.ps1
  ```

  Expected: all checks pass, or unrelated external worktree/state blockers are reported without being used as completion evidence.

- [ ] **Step 3: Closeout evidence**

  Final report must distinguish:
  - native experts used and closed;
  - durable/persistent team not launched unless evidence exists;
  - timed-out experts not used as evidence;
  - LangGraph backend readiness not equal to persistent-team runtime.

#### Verification Matrix

| Requirement | Verification command | Required failing counterexample | Required passing example |
| --- | --- | --- | --- |
| Routing parity with/without collaboration phrase | `python .\tools\check_orchestration_prompt_independent_collaboration_parity.py --root . --json` | Phrase causes `persistent_team=running` | Same task shape has identical decision fields |
| Durable/persistent evidenceguard | `python .\tools\check_durable_persistent_evidence_guard.py --root . --json` | Running claim lacks heartbeat | Complete has selector, manifest, heartbeat, lifecycle, closed, absorbed |
| Expert lifecycle audit | `python .\tools\check_expert_lifecycle_audit.py --root . --json` | Timeout is referenced as evidence | Result is absorbed before final reference |
| LangGraph release | `python .\tools\check_langgraph_state_release.py --root . --json` | Completed still running with no release marker | Active running has heartbeat, or completed is released |
| Guard wiring | `python .\tools\run_openspec_guard.py --root .` | Checker not registered | Guard output includes new checker |
| CI manifest | `.\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` | Test not registered | Local gate runs the new tests |

#### Risks and Rollback

- Risk: checker depends too heavily on chat transcript text. Mitigation: use structured fixtures and repo-local state as primary evidence; transcript is only the claim source.
- Risk: LangGraph backend ready is mistaken for persistent team running. Mitigation: separate backend readiness from team evidence.
- Risk: real running work is blocked. Mitigation: allow active running state with heartbeat, active work, and continue reason.
- Risk: skills/profiles are mistaken for experts. Mitigation: expert lifecycle accepts only native spawn/wait/result/close/absorbed events.
- Rollback: if a new checker is too noisy, temporarily remove it from `tools/run_openspec_guard.py` while preserving fixtures for repair; do not delete the governance requirement or allow false team claims.

#### Acceptance Criteria

- Same task shape with and without explicit collaboration phrase produces the same routing decision class.
- No durable/persistent running claim passes without selector, manifest, heartbeat, worker lifecycle, closed agent record, and close/absorb evidence.
- Expert lifecycle audit distinguishes completed/absorbed results from timeout/stall/provider pacing non-evidence.
- LangGraph completed work does not leave stale `running` state; if still running, it has active work, heartbeat, and continue reason.
- Repository guard and local CI include the new checks.
- Final user-facing reports distinguish policy expectation, actual evidence, blocked/non-evidence, and main-session takeover; prompt text is never treated as runtime proof.
- This plan itself does not claim a durable/persistent team has run; only later repo-local evidence can support that claim.

## 21. Implemented scope and closure evidence

The original OpenSpec change `enforce-automatic-orchestration-routing` has been implemented, archived, and extended by follow-up enforcement slices. The implemented scope is now:

1. `AGENTS.md` orchestration activation rules are updated.
2. `docs_bilingual/project_startup_summary.*` cold-start reminders are updated.
3. Team-mode, quick-reference, LangGraph, and orchestration activation governance surfaces are updated.
4. Generated user-level team-mode source templates preserve the global automatic-collaboration default.
5. Checker/test coverage prevents regressions for:
   - using a missing user reminder as the reason not to start experts;
   - treating LangGraph as optional or unavailable when it is ready;
   - treating expert timeout as verification evidence;
   - routing traces that fail to distinguish backend-on from persistent-team launch thresholds;
   - tool/runtime blockers being misreported as user preference or as `not_needed`;
   - durable team selection without a frozen plan, independent slices, or a named stabilization blocker;
   - bounded multi-face research skipping analyst-only first fan-out;
   - completed expert threads left open after fan-in without explicit preservation request;
   - provider upstream pacing being reported as a reason to disable orchestration;
   - fan-out exceeding `agents.max_threads=6` or `agents.max_depth=1` without explicit override;
   - write-heavy parallel work without disjoint ownership and leader-owned final integration;
   - one durable task mixing `native_omx` and LangGraph state without an explicit handoff;
   - implementation starting from open-ended research without a frozen implementation brief;
   - bug triad roles being kept alive as persistent workers instead of persisting survivors to a debugger-lane queue;
   - treating AutoGen, CrewAI, or LangGraph as native Codex-subagent equivalents;
   - explicit `omx` or `LangGraph` directives being handled as optional preferences;
   - thresholds being met while the session stays in explanation-only mode;
   - roles being added without a smallest-sufficient trigger;
   - skills or plugin profiles being treated as native subagents or expert evidence;
   - custom agent TOMLs missing `name`, `description`, or `developer_instructions`;
   - follow-up work reusing a closed/completed expert thread without an explicit preservation reason;
   - unmanaged team adoption based only on compatibility records rather than `.omx/state/selectors/active.json`;
   - orchestration decisions depending on repository age rather than current task flow;
   - Codex startup being treated as an automatic durable-team launch;
   - a separate persistent leader pane replacing the main Codex session;
   - resumed legacy sessions overriding current repository governance;
   - oh-my-codex or LangGraph being described as a Codex replacement instead of an additive layer;
   - capability switches being read outside the dependency chain;
   - worker-centric durable execution defaulting to LangGraph without considering `native_omx` lane fit;
   - graph-shaped checkpoint work defaulting to `native_omx` without considering LangGraph lane fit;
   - delegation of blocking critical-path work when the leader should do it locally;
   - duplicate leader/expert work or duplicate expert/expert work;
   - leader waiting silently while no non-overlapping local work is attempted;
   - read-only explorer work replacing a clear bounded code-change worker task;
   - LangGraph checkpoint work not using LangGraph entrypoints or repo-local `.omx/state/langgraph/` state;
   - durable artifacts, frozen briefs, or survivor queues existing only in transient chat context.
6. Missing repo-local `.omx/state/selectors/active.json` is treated as a selector refresh/reporting gap, not as proof that LangGraph is unavailable.

If a future review finds a new gap, open a new bounded OpenSpec change. Do not reinterpret this active plan as unfinished merely because it remains the active baseline.

## 22. Evidence and test mapping

| Rule | Minimum evidence | Candidate test/check |
| --- | --- | --- |
| Capability chain is enforced | state file normalization examples | unit test for invalid state combinations |
| LangGraph ready means default backend | status output includes backend_default and backend_ready | status helper golden output test |
| User reminder is not required | routing trace has no forbidden reason | static trace text checker |
| Expert timeout is not evidence | final report separates timeout from absorbed result | log/report pattern checker |
| Ignored local logs do not break canary guard | ignored transcript with canary markers passes guard | context-retention canary test |
| Missing active selector is a refresh gap | status reports selector missing without backend downgrade | selector status helper test |
| Tool/runtime blocker is explicit | trace reports `blocked:<reason>` instead of a user-reminder reason | activation trace blocker test |
| Reload and restart trigger activation | reload/restart transcript includes capability chain and backend default | startup/reload trace smoke test |
| Durable-team threshold map is enforced | trace explains threshold met or unmet on first activation | durable-team threshold checker |
| Bounded multi-face research is analyst-first | first fan-out is `analystxN` without default architect/planner/writer | role-routing golden test |
| Completed experts are closed | completed agent is closed after result absorption unless explicitly preserved | agent lifecycle checker |
| Expert waits are bounded | wait transcript shows 30s/60s/120s windows and about 180s total bound | wait/liveness trace checker |
| Provider backpressure does not disable orchestration | pacing is reported as named backpressure, not as a skip reason | upstream pacing trace checker |
| Fan-out bounds are enforced | trace and worker briefs stay within max_threads/max_depth unless explicitly overridden | fan-out bounds checker |
| Write ownership is isolated | worker briefs declare disjoint file/module ownership and hotspot serialization | ownership isolation checker |
| Durable backend family is single per task | handoff notes show one backend family or explicit close/handoff before switching | backend-family consistency checker |
| Research handoff is frozen | implementation starts from a frozen brief with scope, non-goals, acceptance evidence, ownership, and risks | frozen-brief checker |
| Bug triad does not persist | bug-finder/rebutter/judge results are absorbed and survivors are queued for debugger lane | adversarial survivor queue checker |
| Adjacent runtime terminology is correct | OpenHands is used; AutoGen/CrewAI/LangGraph are not described as native Codex-subagent equivalents | terminology checker |
| Hard routing directives are honored | explicit `omx`/`LangGraph` directives lead to selected/running lane or named blocker | directive adoption checker |
| Explanation-only mode is blocked when thresholds are met | trace shows actual adoption when chain, preflight, and threshold pass | adoption trace checker |
| Role set is smallest sufficient | selected roles map to trigger table and no default extra roles are present | role-minimality checker |
| Agent and skill surfaces stay distinct | native agents live in agents directories; skills load from `SKILL.md`; profiles do not imply workers | agent-skill-boundary checker |
| Custom agent TOMLs are minimally valid | TOMLs include `name`, `description`, and `developer_instructions` | agent-toml schema checker |
| Follow-up uses fresh agent unless preserved | later work spawns fresh agent or cites explicit preserved-thread reason | follow-up-thread checker |
| Selector source is authoritative | automatic durable routing reads `.omx/state/selectors/active.json`; compatibility records are context only | selector-source checker |
| Main session remains leader | trace and final report show leader-owned fan-in, evidence labeling, and integration | leader-ownership checker |
| Startup does not auto-launch teams | startup trace shows threshold met/unmet rather than automatic durable-team launch | startup-team-threshold checker |
| Adoption is task-flow scoped | routing decisions are based on current task phase and thresholds, not repo newness | task-flow-scope checker |
| Legacy resume is compatibility-scoped | legacy sessions cannot override current governance or capability-chain policy | legacy-session boundary checker |
| Native Codex remains the base layer | docs describe oh-my-codex/LangGraph as additive workflow layers, not replacements | base-layer terminology checker |
| Capability switches are chain-consistent | state uses subagent_routing -> oh_my_codex -> langgraph dependency order | capability-switch chain checker |
| Effective lane choice is task-fit based | native_omx and LangGraph choices map to worker-centric or graph-shaped criteria | lane-fit checker |
| Delegation is concrete and non-duplicative | delegated tasks are bounded, self-contained, materially advancing, and not duplicative | delegation-design checker |
| Leader works while experts run | trace shows non-overlapping leader work or a stated blocker before waiting | leader-wait discipline checker |
| Critical-path blocking work stays local | leader does not delegate the immediate blocking step unless handoff is explicitly justified | critical-path delegation checker |
| Explorer and code-change worker boundaries are preserved | read-only explorer work is limited to specific mapping questions; bounded patches use workers | explorer-worker-boundary checker |
| LangGraph state surfaces are used | graph/checkpoint tasks use LangGraph entrypoints and `.omx/state/langgraph/` state | langgraph-state-surface checker |
| Durable artifacts are persisted | frozen briefs, survivor queues, and durable artifacts have repo-local state or documented paths | durable-artifact-persistence checker |

## 23. Risks and rollback

- Risk: automatically launching too many workers for small tasks. Mitigation: keep backend-on separate from workflow/team launch thresholds.
- Risk: hiding real canary leakage by ignoring too much. Mitigation: only root `.gitignore` patterns are honored by the canary guard, and startup summary sources remain explicitly checked.
- Risk: final reports overclaim expert evidence. Mitigation: require explicit evidence source labels.
- Risk: completed expert threads remain open and leak context or attention. Mitigation: close completed agents after absorption by default.
- Risk: upstream pacing is misread as orchestration unavailability. Mitigation: report named backpressure and prefer local-first bounded fan-out.
- Risk: parallel workers overwrite each other. Mitigation: require disjoint ownership, hotspot serialization, and leader-owned integration.
- Risk: backend-family state is mixed. Mitigation: enforce one durable backend family per task unless an explicit handoff is recorded.
- Risk: research conclusions drift during implementation. Mitigation: require a frozen implementation brief before execution.
- Risk: adversarial review lanes become unmanaged workers. Mitigation: close burst roles after fan-in and persist only survivor queues for debugger-lane follow-up.
- Risk: adjacent orchestration runtimes are confused with native Codex subagents. Mitigation: enforce terminology and role-boundary checks.
- Risk: explicit routing directives are treated as optional preferences. Mitigation: require selected/running state or a named blocker.
- Risk: too many experts are launched by default. Mitigation: enforce smallest-sufficient role selection.
- Risk: skills or profile helpers are mistaken for subagent evidence. Mitigation: enforce agent/skill/profile surface separation.
- Risk: follow-up work reuses stale context. Mitigation: spawn fresh agents unless the thread was explicitly preserved.
- Risk: unmanaged durable teams are adopted accidentally. Mitigation: use the active selector as the authority and treat compatibility records as context only.
- Risk: a separate leader pane fragments accountability. Mitigation: keep the main session as leader and workers as execution surfaces.
- Risk: startup is mistaken for durable-team launch. Mitigation: require threshold evidence before any team launch.
- Risk: legacy resume carries stale assumptions. Mitigation: treat legacy sessions as compatibility-scoped and reapply current governance.
- Risk: wrapper layers are described as Codex replacements. Mitigation: enforce base-layer terminology.
- Risk: effective lane choice ignores task fit. Mitigation: check native_omx worker-centric criteria and LangGraph graph-shaped criteria before durable adoption.
- Risk: delegation becomes passive waiting. Mitigation: require immediate leader-side critical-path planning and non-overlapping work while experts run.
- Risk: duplicate work wastes context and creates conflicting evidence. Mitigation: require non-duplicative bounded sidecar tasks and explicit takeover records.
- Risk: read-only exploration delays obvious bounded implementation. Mitigation: prefer code-change workers for isolated patches and keep blocking reads local.
- Risk: durable decisions are lost in chat context. Mitigation: persist LangGraph state, frozen briefs, survivor queues, and durable artifacts to repo-local paths.
- Rollback: revert checker/runtime enforcement while keeping this plan as a record if implementation causes excessive false positives.

## 24. Non-goals

- Do not force every small task into multi-worker execution.
- Do not install the official LangGraph package into the repository `.venv`; the repository rule remains to use the user-level shared LangGraph venv.
- Do not bypass OpenSpec, local gate, or local MR review.
- Do not pretend pane-style persistent team was launched when tmux is unavailable.
- Do not use `status: active` alone as proof of completion; use the archived-change list, stable policy surfaces, and checker/test evidence in this document.

## 25. Acceptance criteria

- New sessions, session reloads, Codex restarts, and resumed sessions report capability chain and backend default.
- When LangGraph is ready, default backend is reported as `langgraph`.
- No routing trace uses "the user did not request parallelism/subagents" as the reason for not using experts.
- Final reports do not claim expert verification when the expert timed out and did not return evidence.
- Checker or tests cover at least three of the key regressions above.
- Missing repo-local active selector is reported as a selector refresh gap, not LangGraph backend unavailability.
- Tool or higher-authority blockers are reported as `blocked:<reason>`, not as missing user instruction.
- First activation explains why durable team was selected or which durable-team threshold was not met.
- Bounded multi-face research starts with analyst-only fan-out unless a later fan-in justifies escalation.
- Completed experts are closed after absorption unless the user explicitly asks to preserve the thread.
- Expert wait behavior is bounded and liveness/stall handling is visible in trace or final report.
- Provider upstream pacing is treated as backpressure, not as a reason to disable orchestration.
- Fan-out stays within managed bounds unless an explicit override is recorded.
- Write-heavy parallel execution declares disjoint ownership and leader-owned final integration.
- Each durable task uses one backend family at a time, or records an explicit close/handoff before switching.
- Open-ended research hands off through a frozen implementation brief before execution starts.
- Bug triad roles are burst, read-only, leader-side roles; unresolved survivors are queued for debugger-lane follow-up.
- Adjacent runtime terminology stays correct: OpenHands is preferred, and AutoGen/CrewAI/LangGraph are not described as native Codex-subagent equivalents.
- Explicit `omx` or `LangGraph` directives result in actual lane adoption or a named blocker/unmet threshold.
- When thresholds are met, the session does not remain in explanation-only mode.
- Expert roles are selected from the smallest-sufficient trigger table.
- Native agents, skills, plugin profiles, and profile helpers are not collapsed into one surface.
- Follow-up work uses a fresh agent unless an explicit preserved-thread reason exists.
- Automatic durable-team routing treats `.omx/state/selectors/active.json` as the selector source and does not auto-adopt unmanaged teams from compatibility records alone.
- The current main Codex CLI session remains the leader; no separate persistent leader pane replaces it.
- Startup and first activation do not auto-launch durable teams; they report threshold met/unmet and adopt only when conditions are satisfied.
- Orchestration adoption is scoped to the current task flow, including existing projects and live-session retrofit, not to repository age.
- Native Codex remains the base layer; oh-my-codex and LangGraph are additive workflow/durable-state layers, not replacements.
- Effective lane choice distinguishes worker-centric `native_omx` fit from graph-shaped LangGraph fit while preserving one backend family per durable task.
- Delegated work is concrete, bounded, self-contained, non-duplicative, and materially advances the current phase.
- Leader continues non-overlapping work while experts run and uses `wait_agent` only when blocked on the next critical-path step.
- Read-only explorer work is used for specific mapping questions; bounded implementation changes prefer code-change workers with isolated ownership.
- LangGraph graph/checkpoint work uses LangGraph entrypoints and repo-local `.omx/state/langgraph/` state, while compatibility records remain context only.
- Durable artifacts, frozen briefs, and survivor queues are persisted to repo-local state or documented artifact paths.
- Plan-completion claims cite archived OpenSpec changes plus current checker/test evidence, not `status: active` alone.

## 26. Scope and authority boundary

This plan is an active implementation-plan record and the baseline for future enforcement reviews. The original follow-up OpenSpec implementation package has now updated policy surfaces, helper scripts, generated source templates, and checks; those higher-authority surfaces are the runtime contract. This plan remains the acceptance checklist and change-history index for that contract.

Authority order:

1. system and developer instructions remain highest authority for the live session;
2. `AGENTS.md` and startup summaries define repository startup behavior;
3. governance policy documents define durable repository rules;
4. this plan records the intended implementation package and acceptance targets.

If this plan conflicts with a current higher-authority surface, the implementation change must update that surface rather than relying on this plan alone.

## 27. State vocabulary

Use these terms consistently:

- `installed` - required runtime or helper files exist.
- `enabled` - user-level capability switches allow the lane.
- `selected` - user-level or repo-local state chooses the lane as the active backend family.
- `ready` - installed, enabled, selected, and not blocked by preflight.
- `running` - a concrete durable workflow or team execution is currently active.
- `blocked` - the lane was eligible or requested but cannot proceed because of a named blocker.
- `not_needed` - the current task does not require that execution surface.

`ready` does not mean `running`, and `not_needed` does not mean disabled.

## 28. Existing-session retrofit rule

Existing sessions must adopt this policy when any retrofit trigger occurs:

- the session reloads or Codex restarts;
- the user says continue or asks to resume;
- the task phase changes;
- the task expands to two or more execution slices;
- a key-path expert times out or stalls;
- `.omx` durable state is detected;
- user-level capability state changes;
- the session emits an orchestration trace.

On retrofit, including reload or restart, the session must re-read user-level capability state and repo-local backend/selector state before making backend or team claims. Cached or stale routing assumptions from the previous process are not sufficient evidence.
