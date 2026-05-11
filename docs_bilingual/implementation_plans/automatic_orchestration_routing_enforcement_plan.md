---
doc_id: automatic_orchestration_routing_enforcement_plan
version: 0.1
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

- `expert returned and absorbed`;
- `expert timed out; not used as evidence`;
- `main session took over verification`;
- `durable_team blocked by <reason>`;
- `backend_default=langgraph, backend_ready=true` - records that LangGraph is the default ready backend, not proof that a persistent team was launched.

## 3. Activation trace format

Activation check must re-run on new session, resume, phase change, user "continue", expert timeout, `.omx` durable-state detection, or expansion to two or more execution slices.

Recommended trace fields:

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

## 4. Current local inspection result

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

## 5. Proposed implementation scope

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

## 6. Non-goals

- Do not force every small task into multi-worker execution.
- Do not install the official LangGraph package into the repository `.venv`; the repository rule remains to use the user-level shared LangGraph venv.
- Do not bypass OpenSpec, local gate, or local MR review.
- Do not pretend pane-style persistent team was launched when tmux is unavailable.

## 7. Acceptance criteria

- New sessions and resumed sessions report capability chain and backend default.
- When LangGraph is ready, default backend is reported as `langgraph`.
- No routing trace uses "the user did not request parallelism/subagents" as the reason for not using experts.
- Final reports do not claim expert verification when the expert timed out and did not return evidence.
- Checker or tests cover at least three of the key regressions above.
