## Context

The active durable-state isolation queue intentionally moved through small MR slices. MR 1 through MR 5 are already complete. The queue now asks for an MR 6 readiness review or automatic durable routing hookup.

Repository evidence shows that the runtime hookup already exists in the older team-mode P5 line:

- `openspec/specs/codex-user-level-team-mode-automatic-team-routing/spec.md` - stable spec for the automatic durable-team routing helper and backend-aware routing decisions.
- `tools/install-codex-user-level-team-mode.ps1` - repository source that generates `omx-team-auto.ps1`, the user-level automatic durable-team helper.
- `test/install-codex-user-level-team-mode.test.ps1` - tests covering `effective_lane`, legacy selector rejection, empty unmanaged residue handling, native_omx launch/reuse/switch/shutdown, and LangGraph graph-signal selection.
- `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md` - active team-mode plan that already marks P5 automatic durable-team routing as implemented.

## Goals / Non-Goals

**Goals:**

- Reconcile the MR 6 queue against existing runtime evidence before opening new runtime work.
- Keep the current MR as documentation and spec-status synchronization only.
- Make the next action explicit for cold-start sessions: do not duplicate P5; only plan a future live smoke/adoption gate if the user asks for runtime exercise.

**Non-Goals:**

- Do not launch, reuse, switch, or shut down durable teams.
- Do not edit user-level Codex config or generated user-level helper files.
- Do not mutate repo-local durable state.
- Do not change MCP Router or direct MCP configuration.

## Decisions

1. Treat MR 6 as a readiness-review closeout for this queue.
   - Rationale: the automatic durable routing helper, stable specs, and tests already exist. A second runtime hookup would duplicate work.
   - Alternative considered: implement another automatic routing helper. Rejected because `omx-team-auto.ps1` is already generated and tested.

2. Update plan-status synchronization rather than runtime code.
   - Rationale: the defect is stale rollout wording, not missing runtime behavior.
   - Alternative considered: archive no-op without plan changes. Rejected because cold-start sessions would still see MR 6 as pending hookup work.

3. Keep a future live smoke/adoption gate separate.
   - Rationale: actually starting durable teams is a runtime action and should only happen under an explicit task with safe project selection and operator consent.

## Risks / Trade-offs

- Risk: calling MR 6 complete may be misunderstood as completing the final production-grade persistent team draft. Mitigation: explicitly state that the final draft remains a north-star and that this only closes the small-step MR 6 queue item.
- Risk: skipping runtime changes could miss a real current install drift. Mitigation: cite tests and helper generation as source evidence, and leave future live smoke as a separate explicit step.
