## Context

P2 already made `omx team` callable through generated wrappers, and P3 already made expert-routing thresholds inspectable. P4 added the adversarial bug-review triad as real user-level callable roles.

Current gap after P4:

- enhanced mode can see that durable team features exist, but it still lacks a first-class automatic durable-team routing surface
- the leader has no reusable helper for deciding `launch` vs `reuse` vs `switch` vs `shutdown`
- a repository can contain an existing team state root, but there is no safe tracked-team contract for automatic reuse

P5 closes that gap without changing the base startup model:

- native Codex remains the permanent base layer
- wrapped `codex` startup still does not auto-launch a durable team on every startup
- durable-team automation is session-directed and threshold-gated, not launcher-forced

## Goals / Non-Goals

**Goals:**

- generate a reusable `omx-team-auto.ps1` helper into the user-level Codex home
- expose an inspectable automatic durable-team routing model through shared runtime policy output
- make enhanced auto mode tell Codex CLI when to prefer durable-team automation over raw `omx team` commands
- add a repo-local tracked-team record so automatic reuse or switch decisions stay inside the current repository boundary
- keep unmanaged pre-existing teams safe from accidental automatic adoption
- make launch or reuse or switch or shutdown behavior testable in a temporary Codex home with a fake `omx`

**Non-Goals:**

- auto-launching a durable team on every wrapped `codex` startup
- replacing native `codex.cmd`, native `omx.cmd`, or PowerShell host behavior
- implementing a mixed persistent pane compose layer
- auto-adopting arbitrary unmanaged teams that were not created by the helper
- changing OpenClaw runtime config or repository-local OpenClaw startup behavior

## Decisions

### Decision 1: Automatic durable-team routing will live in shared runtime plus one generated helper

The installer will generate:

- `bin/omx-team-auto.ps1`

The shared runtime will also expose a structured automatic durable-team routing model through `Get-CodexUserLevelRoutingPolicy`.

Why:

- the routing decision rules must stay inspectable and testable
- wrapped startup, routing policy, team-leader guidance, playbook guidance, and the helper itself should share one source of truth
- keeping the behavior in generated user-level assets preserves cross-repository reuse

### Decision 2: The helper will use the approved seven-phase model, not ad hoc task wording

The helper will route durable-team behavior from explicit project phases:

- `define-target`
- `read-context`
- `freeze-plan`
- `execute-parallel`
- `integrate-converge`
- `stabilize`
- `verify-accept`

Default durable-team rules:

- no durable team in `define-target`, `read-context`, `freeze-plan`, or `verify-accept`
- `execute-parallel` and `integrate-converge`
  - launch or reuse `2:team-executor` when parallel slices are at least `2`
  - scale to `3:team-executor` when parallel slices are at least `3`
- `stabilize`
  - switch to or reuse `2:debugger` when blocking issues are at least `1`

Why:

- this follows the already approved seven-phase operating model
- it keeps durable teams tied to concrete execution and stabilization phases instead of vague heuristics

### Decision 3: Automatic reuse and switch behavior will only manage tracked repo-local teams

The helper will maintain a repo-local tracked-team record at:

- `.omx/state/team/codex-auto-managed-team.json`

Automatic behavior may manage a team only when:

- the tracked record exists
- the recorded team directory still exists in the current repo `.omx` state root

If the repository contains a latest team directory but no tracked record, the helper will return a safe non-mutating decision such as `manual-inspection-required` instead of auto-adopting that team.

Why:

- this preserves the user requirement that projects do not interfere with each other
- it prevents automatic shutdown or switch behavior from touching unknown unmanaged teams
- it makes automatic routing reversible and auditable

### Decision 4: Apply mode will distinguish launch, reuse, switch, and shutdown

`omx-team-auto.ps1` will support a planning surface by default and an explicit apply surface with `-Apply`.

Apply behavior:

- `launch`
  - call the resolved native `omx` path with the derived `team` launch arguments
  - detect the created team directory
  - write the tracked-team record
- `reuse`
  - call `omx team api create-task` against the tracked team
  - keep the tracked-team record
- `switch`
  - shut down the tracked team
  - launch the new desired team
  - update the tracked-team record
- `shutdown`
  - shut down the tracked team
  - remove the tracked-team record

Why:

- P5 is specifically about whether Codex CLI should start or reuse or switch or stop the durable team
- apply mode must be explicit so planning remains safe and inspectable

### Decision 5: Startup semantics remain conservative, but developer instructions become stronger

Wrapped startup will continue to preserve the rule:

- startup itself does not auto-launch a durable team

But in `oh_my_codex=on` plus `subagent_routing=auto`, developer instructions, `team-leader.toml`, and the generated playbook will now say:

- automatic durable-team routing is available in enhanced auto mode
- prefer `omx-team-auto.ps1` over raw `omx team` when durable-team thresholds are met
- use raw `omx team` only for intentional manual overrides

Why:

- this gives Codex CLI a stronger execution contract without hiding the mutation step
- it respects the user's preference that Codex CLI decides whether durable teams should actually be called

## Risks / Trade-offs

- [Risk] Automatic shutdown could terminate the wrong team.
  Mitigation: only manage teams with a matching tracked-team record in the current repository.

- [Risk] Automatic reuse could silently dispatch work into a stale team.
  Mitigation: require the tracked team directory to exist and keep phase or role or worker-count metadata in the tracked record.

- [Risk] Operators may assume startup now launches durable teams on every session start.
  Mitigation: keep `automatic_durable_team_launch=false` and document the stronger distinction in policy, leader profile, and playbook.

- [Risk] The helper could become an OpenClaw-specific workflow artifact.
  Mitigation: keep generated assets user-level, additive-only, and based only on native Codex plus native `omx` semantics.

## Migration Plan

1. Create proposal, design, tasks, and capability specs for P5.
2. Extend the installer and shared support runtime with automatic durable-team routing metadata and helper functions.
3. Generate `omx-team-auto.ps1` and update policy, leader, and playbook guidance.
4. Extend the PowerShell test to validate plan, launch, reuse, switch, and shutdown behavior with a fake `omx`.
5. Validate OpenSpec and repo guard health.
6. Reinstall into the real user Codex home only after repo validation passes.
