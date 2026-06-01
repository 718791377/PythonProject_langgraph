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

## Global default rule

Automatic collaboration is the default for all projects and all Codex sessions launched through the user-level workflow. The operator does not need to repeat phrases such as "use experts", "use durable_team", "use persistent team", "parallel", or "subagents" for orchestration routing to apply.

For any task that qualifies by scope, risk, multi-document work, multi-stage workflow, independent execution slices, or stabilization need, the session must automatically evaluate and adopt the smallest sufficient collaboration surface among native experts, `native_omx`, LangGraph durable workflow, and persistent team.

If native `spawn_agent` invocation is blocked by the current platform/tool contract, report `experts=blocked:platform_subagent_invocation_constraint` and continue with an eligible durable lane, a narrower respawn path if available, or explicit main-session takeover. Do not recast that blocker as "the user did not request subagents" or any other missing-reminder reason.

## Capability chain

The capability chain is strict:

```text
subagent_routing != off
  -> oh_my_codex may be on
    -> langgraph may be on
      -> langgraph_ready may make LangGraph the default durable backend
```

If `subagent_routing=off`, higher orchestration layers are unavailable. In executable terms, `subagent_routing=off` requires `oh_my_codex=off` and `langgraph=off`. If `oh_my_codex=off`, LangGraph availability is disabled and `oh_my_codex=off` requires `langgraph=off`. If `langgraph=on`, routing must not be off and oh-my-codex must be on.

If `durable_orchestration_backend=langgraph`, then `langgraph=on`, `oh_my_codex=on`, and `subagent_routing!=off` must all hold. The dependency chain is checked by `tools/check_capability_switch_chain.py`, which reads the user-level capability state and optional repo-local `.omx/state/langgraph/backend.json` context.

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
main_session_escalation=<not_needed|preflight|pending_approval|granted|timed_out|blocked>
approval_timeout_risk=<none|low|medium|high|expired>
approval_receipt=<none|receipt id or repo-local artifact path>
why=<concrete reason>
```

User-facing conversation surfaces SHALL keep the literal labels `Routing trace` and `Updated Plan` stable. Explanatory content under those labels MAY be Chinese. `Routing trace` is a plain text diagnostic line or short block with fixed key=value fields; it is not a progress panel. `Updated Plan` is the progress panel and SHALL remain a user-visible CLI/tree status-list surface using checkmark/open-square semantics rather than prose-only text. Markdown checkbox syntax remains implementation-plan-internal and MUST NOT be used as the user-visible `Updated Plan` conversation surface. Saved structured evidence keeps canonical field names and threshold or blocker tokens for checker compatibility.

Do not use missing-reminder reasons such as "the user did not request parallelism" or "the user did not request subagents". Use task phase, scope, thresholds, blockers, or main-session takeover as the reason.

Prompt-independent activation parity is checker-backed evidence, not only prose. Qualified tasks with and without collaboration keywords such as experts, parallel, subagents, durable_team, or persistent team must resolve to the same routing decision when the task shape is otherwise identical. Evidence fixtures must also reject missing-user-reminder excuses and require concrete blockers, unmet thresholds, or explicit main-session takeover instead.

Main-session escalation visibility is mandatory whenever an OMX, LangGraph, durable-worker, or local shell flow may need operator approval. `main_session_escalation` records whether the current main Codex CLI session has no escalation need, is running preflight, is waiting for approval, has received approval, has timed out, or is blocked. `approval_timeout_risk` records the visible risk level before a hidden worker wait can go stale. `approval_receipt` records `none` when no approval is needed, or a repo-local receipt, interrupt, checkpoint, or pending-approval artifact path when approval is pending, granted, timed out, or blocked. Worker contexts may record the receipt, but only the main session may request or receive escalation approval.

Explicit `omx` and `LangGraph` requests are hard routing directives for the current task flow. If the capability chain, preflight, and task thresholds are satisfied, the trace must report the selected lane as `selected` or `running` and must not remain in explanation-only mode. If the requested lane is not adopted, the trace must report a named blocker or unmet threshold such as `blocked:backend_not_ready`, `blocked:preflight_failed`, `blocked:helper_missing`, `blocked:write_ownership_conflict`, or `threshold_not_met:no_frozen_plan`. The trace must not describe an explicit directive as an optional preference. Saved hard-directive adoption evidence is checked by `tools/check_role_routing_directive_evidence.py`.

## Expert and durable evidence rules

Expert timeout, stalled workers, upstream pacing, or abandoned lanes are not verification evidence. Provider pacing is backpressure, not a reason to disable orchestration. Completed experts must be closed after their result is absorbed unless the user explicitly asks to preserve the thread or a plan records a preserved-thread reason. Waits must use bounded windows and a visible total bound; stalled or quiet experts require inspect, redirect, respawn, durable handoff, or main-session takeover. Structured lifecycle evidence must keep wait, timeout, result, absorption, closure, and handling events tied to the same `agent_id`; a timeout requires a prior bounded wait and a handling event for that agent, two quiet `progress_check` events require handling, and `provider_pacing` must be classified as `backpressure` without disabling LangGraph, OMX, subagents, experts, or orchestration.

Final reports must label evidence sources explicitly, for example:

- `expert returned and absorbed`;
- `expert timed out; not used as evidence`;
- `main session took over verification`;
- `durable_team blocked by <reason>`;
- `backend_default=langgraph, backend_ready=true` - records the default durable backend and its readiness evidence.

Saved activation trace evidence can be checked with `tools/check_orchestration_trace_evidence.py`. The checker validates required trace fields, capability-chain dependency consistency, backend readiness semantics, durable workflow and persistent-team vocabulary, forbidden missing-reminder reasons, expert timeout labels, and durable-team threshold evidence in `why`. Use it for local transcript snippets, run summaries, or other saved trace evidence before treating an activation trace as accepted evidence. Expert lifecycle, wait, liveness, and provider pacing evidence can be checked with `tools/check_expert_lifecycle_wait_pacing_evidence.py`; this checker enforces completed-agent closure or explicit preservation, fresh-agent follow-up, bounded wait windows, stall handling actions, and upstream pacing as backpressure rather than an orchestration disablement reason.

Prompt-independent collaboration parity, cold-start read-order evidence, durable/persistent evidenceguard records, expert lifecycle audit events, and LangGraph state release are checked together by `tools/check_orchestration_collaboration_evidenceguard.py`. The checker uses fixture pairs to prove that equivalent prompts with and without collaboration phrases produce the same routing decision, rejects durable/persistent team claims without active selector, manifest or thread state, heartbeat, close, and leader absorption evidence, and rejects completed LangGraph work that remains in stale `running` state instead of recording `completed_at`, `final_phase`, `result_summary`, and `released_by`. Structured LangGraph state-release evidence is also accepted by `tools/check_durable_artifact_state_surfaces.py`: completed thread state must not keep active statuses such as `running`, released or closed state must include `released_at` and `released_by`, and backend-family handoff must include `handoff_at`, `handoff_target`, and `reason` before another durable backend family is treated as the safe continuation surface.

## Team threshold rules

Do not auto-launch durable teams during startup, read-only inventory, or plan-freeze work.

Durable team selection requires a frozen plan plus at least two mostly independent execution slices, or a stabilization phase with named blocking issues. If selected, use the approved automatic helper such as `omx-team-auto.ps1`; do not adopt unmanaged teams from compatibility records alone.

On startup or first activation, the trace must say which durable-team threshold was not met, such as `threshold_not_met:no_frozen_plan` or `threshold_not_met:single_execution_slice`. If a durable lane is blocked, the trace must say the named blocker or unmet threshold. If a durable team is selected or running, the trace must say which concrete threshold triggered it, preferably with a stable token such as `triggered_threshold:frozen_plan_with_2+_independent_slices`, or with equivalent frozen-plan / stabilization blocking-issue language. The saved trace-evidence validator enforces these labels in `why` so vague explanations such as "small task" or "using team now" do not pass as threshold evidence.

## Surface boundaries

Native Codex subagents, workflow skills, plugin-provided skills, profile helpers, durable workers, and LangGraph nodes are distinct execution surfaces. The current main Codex CLI session remains the leader and owns activation checks, role selection, fan-in, evidence labeling, final integration, and release recommendations.


## Advanced routing enforcement boundaries

Smallest-sufficient role selection is mandatory. Add expert roles only when the trigger is present and the output materially advances the current phase. Bounded multi-face research remains analyst-fanout-first with homogeneous `analystxN`; escalate to `architect`, `planner`, or `writer` only after analyst fan-in shows architecture, execution-ordering, or document-finalization work. Saved role-routing evidence is checked by `tools/check_role_routing_directive_evidence.py`.

Native agents, skills, and profile helpers are distinct orchestration surfaces. Native reusable role definitions live in user-level or repo-local agents directories, and Native Codex subagents, workflow skills, plugin-provided skills, plugin modules, profile helpers, durable workers, and LangGraph nodes remain separate surfaces. Skills are not native subagents. Skills are loaded from installed `SKILL.md` files and route procedural instructions, but they do not count as expert evidence by themselves. Skill invocation, plugin profile loading, or profile helper hard-load/soft-load is not expert evidence. Profile helper hard-load or soft-load changes visible instructions; it does not start durable workers or satisfy persistent-team thresholds. If follow-up is needed after a completed expert was absorbed and closed, spawn a fresh agent unless the user explicitly requested preservation or the plan records a preserved-thread reason. Saved evidence for this boundary is checker-backed by `tools/check_agent_skill_profile_surface_boundaries.py` and `tools/check_expert_lifecycle_wait_pacing_evidence.py`.

Standalone native-agent TOMLs and every custom agent TOML in the user-level agents directory or repo-local `.codex/agents/` must pass `tools/check_custom_agent_toml_schema.py`: each present TOML must parse and define non-empty top-level `name`, `description`, and `developer_instructions`. Native-agent TOML schema is checked separately from skill `SKILL.md` validation so native agents, skills, and plugin profiles remain distinct surfaces.

The current main Codex CLI session remains the leader. It owns activation checks, role selection, worker brief quality, fan-in, evidence labeling, final integration, and release recommendations. Do not replace it with a separate persistent leader pane. Orchestration adoption is scoped to the current task flow, not to whether a repository is new or old.

Leader session and task-flow scope evidence is checked by `tools/check_leader_session_scope_evidence.py`. The checker requires evidence that the current main Codex CLI session remains the leader, owns leader-owned fan-in, evidence labeling, final integration, and release recommendations; it rejects any separate persistent leader pane replacing the main session; it treats startup non-autolaunch as mandatory unless startup or first activation cites a concrete unmet or triggered durable-team threshold; it requires task-flow scoped adoption instead of repository-age based routing; and it requires that legacy resumed sessions are compatibility-scoped and cannot override current repository governance or capability-chain policy. reload, restart, resume, continue, and durable-state detection evidence must show an activation check rerun.

### Session replay context filtering

Session replay context filtering is required before a resumed legacy session, compacted transcript, or replayed thread fragment can be used as current prompt authority. Replay inputs include assistant-visible transcript messages, tool/function output, raw startup-summary copies, and old runtime workaround text recovered from `/resume` context. Filtered outputs must separate accepted assistant-visible context from filtered replay fragments and blocked authority candidates.

The filter must drop or block stale canary text, mojibake, raw startup-summary copies, and stale MCP assumptions before any prompt-authority handoff. Tool/function output remains diagnostic evidence only; it must not become current authority. Current authority remains `AGENTS.md`, the UTF-8 startup summary pair, and current repository governance documents. For a single old thread with an MCP startup problem, use a per-invocation override such as `-c "mcp_servers.omx_code_intel.enabled=false"`; that workaround is one-launch compatibility handling and must not become a permanent edit to user-level `config.toml` or a global disablement of `omx_*` MCP servers.

Saved replay-filtering evidence is checked by `tools/session_replay_context_filtering.py`. The checker reports `accepted_context_items`, `filtered_context_items`, `blocked_authority_items`, and `replay_diagnostics`, and fails closed when stale replay content would re-enter prompts as current authority.

Native Codex remains the base layer. oh-my-codex, native_omx, skills, profile helpers, and LangGraph are additive workflow or durable-state layers, not Codex replacements. Effective lane choice is task-fit based: use `native_omx` for worker-centric durable execution, worktree isolation, mailbox flow, or direct worker lifecycle control; use LangGraph for graph-shaped multi-phase execution, checkpoint-driven recovery, interrupt/resume approval gates, frozen briefs, or persisted survivor queues. One durable task uses one backend family at a time, and backend-family switching requires explicit close or handoff. Saved lane-fit evidence is checker-backed by `tools/check_effective_lane_fit_evidence.py`, which requires native_omx worker-centric fit, LangGraph graph-shaped fit, default-backend-not-enough evidence, and explicit close/handoff before backend-family switching.

Delegation must be concrete, bounded, self-contained sidecar work that materially advances the main task. The leader must identify the immediate critical-path local work before delegating, avoid delegating urgent blocking work when the next leader action depends on the result, avoid duplicate work, continue meaningful non-overlapping leader work while experts run, and use `wait_agent` sparingly. Code-changing worker briefs must include file/module ownership or disjoint write sets, tell workers they are not alone in the codebase and must not revert other edits, and require final changed paths. Saved delegation and wait evidence is checked by `tools/check_delegation_wait_discipline_evidence.py`.
Fan-out and write-heavy parallel execution are bounded and ownership-isolated. Native subagent fan-out must use leader-side spawning with leader-owned fan-in and stay within `agents.max_threads=6` and `agents.max_depth=1` unless an explicit override, reason, and approval are recorded. Raw Codex does not auto-spawn specialist roles. Prefer parallel fan-out for read-heavy, bounded, independent work. Write-heavy parallel execution requires file/module ownership, disjoint write sets, hotspot serialization or a no-shared-hotspot statement, leader-owned final integration, not alone in the codebase worker instructions, must not revert or overwrite instructions, and changed-path reporting. Saved fan-out/write-ownership evidence is checked by `tools/check_fanout_write_ownership_evidence.py`.

Read-only exploration is for specific codebase questions, symbol mapping, and file discovery. It must not replace a bounded code-changing worker task when the implementation patch is clear and safe. When graph phases, checkpoint gates, frozen briefs, survivor queues, or tracked LangGraph thread state are required, use LangGraph entrypoints and repo-local `.omx/state/langgraph/` state. `.omx/state/selectors/active.json` remains the active selector authority for automatic durable-team adoption; compatibility records are context only. Durable artifacts, frozen briefs, and survivor queues must be written to repo-local state or documented artifact paths, not only transient chat context. Saved durable artifact/state-surface evidence is checked by `tools/check_durable_artifact_state_surfaces.py`.

Open-ended work must keep research and implementation in different roles. Research fan-in must become a frozen implementation brief with scope, non-goals, acceptance evidence, ownership boundaries, and unresolved risks before implementation starts. `bug-finder`, `bug-rebutter`, and `bug-judge` are burst, read-only, leader-side roles; persist remaining candidates as an adversarial-review survivor queue for debugger-lane follow-up instead of keeping the bug triad alive as persistent workers. Treat LangGraph, AutoGen and CrewAI as general programmable orchestration runtimes, not native Codex-subagent equivalents.

## Script control

This policy is backed by `tools/check_orchestration_activation_policy.py`, `tools/check_capability_switch_chain.py`, the saved-trace evidence validator `tools/check_orchestration_trace_evidence.py`, the role/directive evidence checker `tools/check_role_routing_directive_evidence.py`, the leader/session scope evidence checker `tools/check_leader_session_scope_evidence.py`, the expert lifecycle/wait/pacing evidence checker `tools/check_expert_lifecycle_wait_pacing_evidence.py`, the delegation/wait discipline evidence checker `tools/check_delegation_wait_discipline_evidence.py`, the durable artifact/state-surface evidence checker `tools/check_durable_artifact_state_surfaces.py`, the repo-local selector ownership checker `tools/check_repo_local_selector_ownership.py`, the agent/skill/profile surface checker `tools/check_agent_skill_profile_surface_boundaries.py`, the effective lane-fit evidence checker `tools/check_effective_lane_fit_evidence.py`, and the native custom-agent TOML schema checker `tools/check_custom_agent_toml_schema.py`; the policy boundary is registered in `tools/safety_rule_script_backing_registry.json`. Prompt reminders alone are not sufficient for this boundary.

## Active selector refresh reporting

The repo-local selector authority for automatic durable adoption is `.omx/state/selectors/active.json`. Compatibility records such as `.omx/state/langgraph/backend.json` and `.omx/state/team/codex-auto-managed-team.json` are inspection context only. `tools/check_repo_local_selector_ownership.py` verifies that the active selector and selector leases belong to the current repository/worktree root, fail closed on cross-repository selector adoption, and treat stale selectors as no-auto-adoption unless refreshed. When LangGraph is selected and ready but the active selector is missing, status helpers must report a selector refresh gap instead of treating LangGraph as unavailable or silently downgrading to `native_omx`.
