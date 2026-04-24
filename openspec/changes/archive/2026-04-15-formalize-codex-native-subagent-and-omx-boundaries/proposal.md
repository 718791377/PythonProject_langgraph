## Why

The user-level Codex / oh-my-codex team-mode stack now has working controls, startup binding, leader routing, and native Windows durable-team execution, but the spec layer still does not formally define the native-subagent contract that those layers rely on. This gap now matters because the updated bilingual implementation plan already encodes stricter rules about native Codex subagents, routing semantics, agent TOML placement, concurrency limits, and OMX layering, and those rules can drift unless they are promoted into OpenSpec requirements.

## What Changes

- Add a formal capability for native Codex subagent boundaries in the user-level team-mode workflow.
- Define native Codex subagents as an official native capability with explicit spawning, bounded fan-out, and leader-side fan-in rather than as a simulated pane system or an always-automatic runtime.
- Extend the generated user-level control surface to cover reusable user-level agent TOMLs, repository-scoped agent TOMLs, the minimum standalone custom-agent schema, and explicit management or inspection of `agents.max_threads` and `agents.max_depth`.
- Clarify that automatic expert-role routing is a leader-side routing policy layered over native Codex subagents, not a claim that raw Codex auto-spawns specialist roles by default.
- Add explicit execution-safety rules that prefer read-heavy fan-out and allow write-heavy parallelism only when ownership isolation, hotspot serialization, and leader-owned final integration are all defined.
- Align generated leader, playbook, and operator guidance with the boundary between native Codex subagents, durable `omx team`, and general programmable orchestration runtimes.
- Preserve the already approved startup semantics: `oh_my_codex=off` with routing enabled remains wrapped native-routed startup, while `oh_my_codex=off` with routing disabled remains the plain single-agent path.

## Capabilities

### New Capabilities
- `codex-user-level-team-mode-native-subagent-boundaries`: formalize native Codex subagent semantics, custom-agent configuration boundaries, concurrency limits, write-isolation rules, and OMX terminology boundaries for the reusable user-level team-mode workflow

### Modified Capabilities
- `codex-user-level-team-mode-controls`: extend generated control assets to cover native-subagent limit surfaces and user-level vs repository-scoped agent TOML placement rules
- `codex-user-level-team-mode-routing-thresholds`: clarify that automatic role routing is a leader-side policy layered over explicit native Codex subagent spawning, with bounded fan-out and write-safety constraints

## Impact

- impact_scope:
  - user-level Codex team-mode control assets
  - wrapped startup and routing-policy contracts
  - generated leader/playbook/operator guidance
  - OpenSpec capability definitions for Codex / oh-my-codex user-level team mode
- explicit_non_goals:
  - no replacement of native `codex`, `codex.cmd`, or `codex.ps1`
  - no new durable-team backend or worker lifecycle implementation
  - no default mixed-pane compose layer
  - no WSL2 path
  - no OpenClaw runtime configuration change
- rollout_sequence:
  - define proposal, design, and spec deltas for the native-subagent contract
  - extend controls and routing-policy requirements
  - update generated user-level assets and validation coverage in a later implementation step
  - sync plan, playbook, and operator-facing documentation after implementation stabilizes
- rollback_plan:
  - revert only the additive control assets, routing-policy surfaces, and generated documentation touched by the implementation
  - preserve the native Codex base layer unchanged throughout
  - if managed limit-writing proves unstable, fall back to read-only limit inspection while keeping the boundary contract intact
- validation_path:
  - run `openspec validate --all`
  - validate installer generation into a repo-local Codex home target
  - verify wrapped native-routed startup vs plain single-agent startup semantics
  - verify the generated control surface can inspect or manage `agents.max_threads` and `agents.max_depth`
  - verify generated guidance distinguishes user-level `~/.codex/agents` roles from repository `.codex/agents` roles
  - verify write-heavy parallelism guidance requires explicit ownership isolation and leader-side integration
- mainline_classification:
  - existing mainline continuation
  - specifically a contract-tightening change across the Codex user-level team-mode controls and routing surfaces
