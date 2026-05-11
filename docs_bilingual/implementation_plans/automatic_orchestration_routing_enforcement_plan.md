---
doc_id: automatic_orchestration_routing_enforcement_plan
version: 0.13
status: draft
owner: codex-orchestration
date: 2026-05-11
---

# Automatic Orchestration Routing Enforcement Plan

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

## 8. Durable-team threshold map

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

## 9. Expert lifecycle, bounded wait, and provider backpressure

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

## 10. Fan-out bounds, write ownership, and backend-family boundary

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

## 11. Handoff, adversarial review, and adjacent-runtime boundaries

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

## 12. Backend, workflow, and team semantics

These terms must not be collapsed:

- `backend_default` - the default durable backend selected by user-level capability state.
- `backend_ready` - whether the selected backend is installed, enabled, selected, and ready.
- `durable_workflow` - whether this task should use checkpointed or graph-shaped durable execution.
- `persistent_team` - whether a multi-worker persistent team should be launched for this task.

When LangGraph is ready, it is the default backend. A small task may still have `durable_workflow=not_needed` and `persistent_team=not_needed`. That means the task does not need those execution surfaces; it does not mean LangGraph is off.

## 13. Current local inspection result

Read-only inspection on 2026-05-11 showed:

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

Interpretation: the user-level LangGraph backend is available and should be treated as the default backend. A missing repo-local active selector is a state-refresh or reporting gap; it must not be interpreted as LangGraph backend unavailability.

## 14. Active selector handling

When `.omx/state/selectors/active.json` is missing but the user-level capability state says `durable_orchestration_backend=langgraph` and `langgraph_ready=true`, the session must not silently downgrade to `native_omx` or `none`.

Required behavior:

1. report `backend_default=langgraph` and `backend_ready=true`;
2. report `active_selector=missing` as a repo-local state-refresh gap;
3. refresh or create the selector through the approved helper when implementation work requires a tracked durable thread;
4. if no helper exists yet, record the missing helper as an implementation gap, not as backend unavailability.

## 15. Low-risk iteration and local integration boundary

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

## 16. Higher-authority and runtime-surface blockers

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

## 17. Implementation phases

### Phase 0 - Record and protect the plan

- Add this bilingual plan.
- Ignore local transcript logs such as `log202605111306.md`.
- Ensure canary guard ignores root `.gitignore` local logs so ignored transcripts do not break local gate.

### Phase 1 - Policy surfaces

- Update `AGENTS.md`.
- Update `docs_bilingual/project_startup_summary.*`.
- Add or update an orchestration activation policy document.
- Update team-mode and LangGraph runtime policy surfaces.

### Phase 2 - Script-backed enforcement

- Add checker coverage for forbidden routing reasons.
- Add checker coverage for durable-team phase thresholds and first-turn threshold explanations.
- Add checker coverage for capability-chain consistency.
- Add checker coverage for expert-timeout evidence claims.
- Add checker coverage for completed-agent closure, bounded wait windows, liveness/stall handling, and upstream pacing labels.
- Add checker coverage for fan-out bounds, write ownership isolation, leader-side spawning language, and one-backend-family durable tasks.
- Add checker coverage for frozen research handoff briefs, adversarial-review survivor queues, and adjacent-runtime terminology boundaries.
- Add checker coverage for hard routing directives, actual adoption versus explanation-only mode, and smallest-sufficient role selection.
- Add checker coverage for native-agent versus skill/profile/plugin boundaries, custom agent TOML fields, fresh follow-up agent use, and selector-source handling.
- Add checker coverage for main-session leader ownership, no separate persistent leader pane, startup non-autolaunch, task-flow scoped adoption, and legacy-session compatibility boundaries.
- Add or update selector refresh/status helper behavior.

### Phase 3 - Runtime integration

- Ensure new sessions, session reloads, Codex restarts, and resumed sessions print the required trace fields.
- Ensure existing sessions re-run activation checks on session reload, Codex restart, phase change, resume, continue, `.omx` state detection, and expert timeout.
- Ensure LangGraph-ready sessions use LangGraph as the default durable backend.

## 18. Proposed implementation scope

After this plan is confirmed, implement it through OpenSpec change `enforce-automatic-orchestration-routing`:

1. Update `AGENTS.md` orchestration activation rules.
2. Update `docs_bilingual/project_startup_summary.*` cold-start reminders.
3. Update team-mode and LangGraph runtime governance or implementation-plan documents.
4. Add or update an orchestration activation policy document.
5. Add checker/test coverage to prevent these regressions:
   - using "the user did not request parallelism/subagents" as a reason not to start experts;
   - treating LangGraph as optional or unavailable when it is ready;
   - treating expert timeout as verification evidence;
   - routing trace failing to distinguish backend-on from persistent-team launch thresholds;
   - tool/runtime blockers being misreported as user preference or as `not_needed`;
   - durable team selected without a frozen plan, independent slices, or a named stabilization blocker;
   - bounded multi-face research skipping analyst-only first fan-out;
   - completed expert threads left open after fan-in without explicit preservation request;
   - provider upstream pacing reported as a reason to disable orchestration;
   - fan-out exceeding `agents.max_threads=6` or `agents.max_depth=1` without explicit override;
   - write-heavy parallel work without disjoint ownership and leader-owned final integration;
   - one durable task mixing `native_omx` and LangGraph state without an explicit handoff;
   - implementation starting from open-ended research without a frozen implementation brief;
   - bug triad roles kept alive as persistent workers instead of persisting survivors to debugger-lane queue;
   - treating AutoGen, CrewAI, or LangGraph as native Codex-subagent equivalents;
   - explicit `omx` or `LangGraph` directives being handled as optional preferences;
   - thresholds being met while the session stays in explanation-only mode;
   - roles being added without a smallest-sufficient trigger;
   - skills or plugin profiles being treated as native subagents or expert evidence;
   - custom agent TOMLs missing `name`, `description`, or `developer_instructions`;
   - follow-up work reusing a closed/completed expert thread without an explicit preservation reason;
   - unmanaged team adoption based only on compatibility records rather than `.omx/state/selectors/active.json`;
   - orchestration decisions depending on whether a repository is newly created rather than the current task flow;
   - Codex startup being treated as an automatic durable-team launch;
   - a separate persistent leader pane replacing the main Codex session;
   - resumed legacy sessions overriding current repository governance.
6. Evaluate and fix the refresh/reporting rule for missing repo-local `.omx/state/selectors/active.json`.

## 19. Evidence and test mapping

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

## 20. Risks and rollback

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
- Rollback: revert checker/runtime enforcement while keeping this plan as a record if implementation causes excessive false positives.

## 21. Non-goals

- Do not force every small task into multi-worker execution.
- Do not install the official LangGraph package into the repository `.venv`; the repository rule remains to use the user-level shared LangGraph venv.
- Do not bypass OpenSpec, local gate, or local MR review.
- Do not pretend pane-style persistent team was launched when tmux is unavailable.
- Do not use this plan as proof that runtime enforcement is already complete.

## 22. Acceptance criteria

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

## 23. Scope and authority boundary

This plan is an implementation-plan record. It is not the final runtime contract until the follow-up OpenSpec change updates policy surfaces, helper scripts, and checks.

Authority order:

1. system and developer instructions remain highest authority for the live session;
2. `AGENTS.md` and startup summaries define repository startup behavior;
3. governance policy documents define durable repository rules;
4. this plan records the intended implementation package and acceptance targets.

If this plan conflicts with a current higher-authority surface, the implementation change must update that surface rather than relying on this plan alone.

## 24. State vocabulary

Use these terms consistently:

- `installed` - required runtime or helper files exist.
- `enabled` - user-level capability switches allow the lane.
- `selected` - user-level or repo-local state chooses the lane as the active backend family.
- `ready` - installed, enabled, selected, and not blocked by preflight.
- `running` - a concrete durable workflow or team execution is currently active.
- `blocked` - the lane was eligible or requested but cannot proceed because of a named blocker.
- `not_needed` - the current task does not require that execution surface.

`ready` does not mean `running`, and `not_needed` does not mean disabled.

## 25. Existing-session retrofit rule

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
