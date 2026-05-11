---
doc_id: automatic_orchestration_routing_enforcement_plan
version: 0.3
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

Activation check must re-run on new session, resume, phase change, user "continue", expert timeout, `.omx` durable-state detection, or expansion to two or more execution slices.

Required trace fields:

```text
Routing trace:
phase=<phase>
capability_chain=subagent:<auto|manual|off> > omx:<on|off> > langgraph:<on|off>
backend_default=<langgraph|native_omx|none>
backend_ready=<true|false>
experts=<none|analystxN|architect|writer|verifier|...>
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

## 5. Backend, workflow, and team semantics

These terms must not be collapsed:

- `backend_default` - the default durable backend selected by user-level capability state.
- `backend_ready` - whether the selected backend is installed, enabled, selected, and ready.
- `durable_workflow` - whether this task should use checkpointed or graph-shaped durable execution.
- `persistent_team` - whether a multi-worker persistent team should be launched for this task.

When LangGraph is ready, it is the default backend. A small task may still have `durable_workflow=not_needed` and `persistent_team=not_needed`. That means the task does not need those execution surfaces; it does not mean LangGraph is off.

## 6. Current local inspection result

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

## 7. Active selector handling

When `.omx/state/selectors/active.json` is missing but the user-level capability state says `durable_orchestration_backend=langgraph` and `langgraph_ready=true`, the session must not silently downgrade to `native_omx` or `none`.

Required behavior:

1. report `backend_default=langgraph` and `backend_ready=true`;
2. report `active_selector=missing` as a repo-local state-refresh gap;
3. refresh or create the selector through the approved helper when implementation work requires a tracked durable thread;
4. if no helper exists yet, record the missing helper as an implementation gap, not as backend unavailability.

## 8. Implementation phases

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
- Add checker coverage for capability-chain consistency.
- Add checker coverage for expert-timeout evidence claims.
- Add or update selector refresh/status helper behavior.

### Phase 3 - Runtime integration

- Ensure new sessions and resumed sessions print the required trace fields.
- Ensure existing sessions re-run activation checks on phase change, resume, continue, `.omx` state detection, and expert timeout.
- Ensure LangGraph-ready sessions use LangGraph as the default durable backend.

## 9. Proposed implementation scope

After this plan is confirmed, implement it through OpenSpec change `enforce-automatic-orchestration-routing`:

1. Update `AGENTS.md` orchestration activation rules.
2. Update `docs_bilingual/project_startup_summary.*` cold-start reminders.
3. Update team-mode and LangGraph runtime governance or implementation-plan documents.
4. Add or update an orchestration activation policy document.
5. Add checker/test coverage to prevent these regressions:
   - using "the user did not request parallelism/subagents" as a reason not to start experts;
   - treating LangGraph as optional or unavailable when it is ready;
   - treating expert timeout as verification evidence;
   - routing trace failing to distinguish backend-on from persistent-team launch thresholds.
6. Evaluate and fix the refresh/reporting rule for missing repo-local `.omx/state/selectors/active.json`.

## 10. Evidence and test mapping

| Rule | Minimum evidence | Candidate test/check |
| --- | --- | --- |
| Capability chain is enforced | state file normalization examples | unit test for invalid state combinations |
| LangGraph ready means default backend | status output includes backend_default and backend_ready | status helper golden output test |
| User reminder is not required | routing trace has no forbidden reason | static trace text checker |
| Expert timeout is not evidence | final report separates timeout from absorbed result | log/report pattern checker |
| Ignored local logs do not break canary guard | ignored transcript with canary markers passes guard | context-retention canary test |
| Missing active selector is a refresh gap | status reports selector missing without backend downgrade | selector status helper test |

## 11. Risks and rollback

- Risk: automatically launching too many workers for small tasks. Mitigation: keep backend-on separate from workflow/team launch thresholds.
- Risk: hiding real canary leakage by ignoring too much. Mitigation: only root `.gitignore` patterns are honored by the canary guard, and startup summary sources remain explicitly checked.
- Risk: final reports overclaim expert evidence. Mitigation: require explicit evidence source labels.
- Rollback: revert checker/runtime enforcement while keeping this plan as a record if implementation causes excessive false positives.

## 12. Non-goals

- Do not force every small task into multi-worker execution.
- Do not install the official LangGraph package into the repository `.venv`; the repository rule remains to use the user-level shared LangGraph venv.
- Do not bypass OpenSpec, local gate, or local MR review.
- Do not pretend pane-style persistent team was launched when tmux is unavailable.
- Do not use this plan as proof that runtime enforcement is already complete.

## 13. Acceptance criteria

- New sessions and resumed sessions report capability chain and backend default.
- When LangGraph is ready, default backend is reported as `langgraph`.
- No routing trace uses "the user did not request parallelism/subagents" as the reason for not using experts.
- Final reports do not claim expert verification when the expert timed out and did not return evidence.
- Checker or tests cover at least three of the key regressions above.
- Missing repo-local active selector is reported as a selector refresh gap, not LangGraph backend unavailability.

## 14. Scope and authority boundary

This plan is an implementation-plan record. It is not the final runtime contract until the follow-up OpenSpec change updates policy surfaces, helper scripts, and checks.

Authority order:

1. system and developer instructions remain highest authority for the live session;
2. `AGENTS.md` and startup summaries define repository startup behavior;
3. governance policy documents define durable repository rules;
4. this plan records the intended implementation package and acceptance targets.

If this plan conflicts with a current higher-authority surface, the implementation change must update that surface rather than relying on this plan alone.

## 15. State vocabulary

Use these terms consistently:

- `installed` - required runtime or helper files exist.
- `enabled` - user-level capability switches allow the lane.
- `selected` - user-level or repo-local state chooses the lane as the active backend family.
- `ready` - installed, enabled, selected, and not blocked by preflight.
- `running` - a concrete durable workflow or team execution is currently active.
- `blocked` - the lane was eligible or requested but cannot proceed because of a named blocker.
- `not_needed` - the current task does not require that execution surface.

`ready` does not mean `running`, and `not_needed` does not mean disabled.

## 16. Existing-session retrofit rule

Existing sessions must adopt this policy when any retrofit trigger occurs:

- the user says continue or asks to resume;
- the task phase changes;
- the task expands to two or more execution slices;
- a key-path expert times out or stalls;
- `.omx` durable state is detected;
- user-level capability state changes;
- the session emits an orchestration trace.

On retrofit, the session must re-read user-level capability state and repo-local backend/selector state before making backend or team claims.
