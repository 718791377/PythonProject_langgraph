---
doc_id: codex_user_level_orchestration_activation_policy
lang: en
doc_class: governance
status: active
---

# Codex User-Level Orchestration Activation Policy

## Purpose

This policy makes automatic orchestration routing an enforceable user-level behavior instead of a reminder the operator must repeat in every prompt.

It applies to native Codex expert routing, oh-my-codex / OMX durable workflow, and LangGraph durable orchestration for this repository and consumer projects that reuse this user-level runtime.

## Capability chain

The capability chain is strict:

```text
subagent_routing != off
  -> oh_my_codex may be on
    -> langgraph may be on
      -> langgraph_ready may make LangGraph the default durable backend
```

If `subagent_routing=off`, higher orchestration layers are unavailable. If `oh_my_codex=off`, LangGraph availability is disabled. If `langgraph=on`, routing must not be off and oh-my-codex must be on.

When `subagent_routing!=off`, `oh_my_codex=on`, `langgraph=on`, and `langgraph_ready=true`, report `backend_default=langgraph` and `backend_ready=true`. Backend readiness does not mean a durable workflow or persistent team is already running.

## Activation triggers

Run an activation check on:

- first substantive turn of a new session;
- session reload, Codex restart, resume, or continue;
- task phase changes;
- expansion from one slice to two or more execution slices;
- `.omx` durable-state detection;
- user-level capability-state changes;
- key-path expert timeout or stall;
- explicit requests for `omx`, `LangGraph`, `parallel`, `experts`, `durable_team`, or `persistent team`.

## Required trace fields

Activation traces must include:

```text
phase=<phase>
capability_chain=subagent:<auto|manual|off> > omx:<on|off> > langgraph:<on|off>
backend_default=<langgraph|native_omx|none>
backend_ready=<true|false>
experts=<none|analystxN|architect|writer|verifier|blocked:<reason>|...>
durable_workflow=<not_needed|candidate|selected|blocked|running>
persistent_team=<not_needed|candidate|selected|blocked|running>
why=<concrete reason>
```

Do not use missing-reminder reasons such as "the user did not request parallelism" or "the user did not request subagents". Use task phase, scope, thresholds, blockers, or main-session takeover as the reason.

## Expert and durable evidence rules

Expert timeout, stalled workers, upstream pacing, or abandoned lanes are not verification evidence.

Final reports must label evidence sources explicitly, for example:

- `expert returned and absorbed`;
- `expert timed out; not used as evidence`;
- `main session took over verification`;
- `durable_team blocked by <reason>`;
- `backend_default=langgraph, backend_ready=true` - records the default durable backend and its readiness evidence.

## Team threshold rules

Do not auto-launch durable teams during startup, read-only inventory, or plan-freeze work.

Durable team selection requires a frozen plan plus at least two mostly independent execution slices, or a stabilization phase with named blocking issues. If selected, use the approved automatic helper such as `omx-team-auto.ps1`; do not adopt unmanaged teams from compatibility records alone.

On startup or first activation, the trace must say which durable-team threshold was not met, such as `threshold_not_met:no_frozen_plan` or `threshold_not_met:single_execution_slice`. If a durable team is selected, the trace must say which concrete threshold triggered it, such as a frozen plan with two or more independent slices or a stabilization phase with named blocking issues.

## Surface boundaries

Native Codex subagents, workflow skills, plugin-provided skills, profile helpers, durable workers, and LangGraph nodes are distinct execution surfaces. The current main Codex CLI session remains the leader and owns activation checks, role selection, fan-in, evidence labeling, final integration, and release recommendations.

## Script control

This policy is backed by `tools/check_orchestration_activation_policy.py` and registered in `tools/safety_rule_script_backing_registry.json`. Prompt reminders alone are not sufficient for this boundary.

## Active selector refresh reporting

The repo-local selector authority for automatic durable adoption is `.omx/state/selectors/active.json`. Compatibility records such as `.omx/state/langgraph/backend.json` and `.omx/state/team/codex-auto-managed-team.json` are inspection context only. When LangGraph is selected and ready but the active selector is missing, status helpers must report a selector refresh gap instead of treating LangGraph as unavailable or silently downgrading to `native_omx`.
