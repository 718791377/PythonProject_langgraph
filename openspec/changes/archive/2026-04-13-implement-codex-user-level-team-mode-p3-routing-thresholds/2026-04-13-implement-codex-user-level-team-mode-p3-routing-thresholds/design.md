## Context

The plan already defines automatic role-routing principles, state semantics, and project-isolation rules, but the generated user-level assets do not yet encode them in a structured way.

Current reality after P2:

- wrapped `codex` startup already reads `oh_my_codex` and `subagent_routing`
- startup still injects only a short developer-instruction summary
- there is no direct user-level inspection command for the routing policy
- generated `team-leader.toml` and `team-mode-playbook.md` do not yet fully mirror the documented thresholds

This makes the leader-side routing behavior harder to validate and easier to drift from the approved plan.

## Goals / Non-Goals

**Goals:**

- encode the documented routing thresholds in one generated runtime source of truth
- make wrapped `codex` startup inject richer, mode-aware developer instructions
- expose an operator-visible policy surface through a small user-level script
- align generated `team-leader.toml` and `team-mode-playbook.md` with the approved routing rules
- keep all new assets additive-only and inside the existing backup-and-rollback transaction
- make the policy testable in a temporary Codex home without touching the real user install

**Non-Goals:**

- building a mixed-pane compose manifest
- auto-launching durable teams from normal `codex` startup
- turning the global switch into a project-scoped switch
- changing native `codex.cmd` or native `omx.cmd`
- changing OpenClaw runtime or service behavior

## Decisions

### Decision 1: Put routing thresholds into the generated shared support script

P0/P1/P2 already use `bin/_codex-user-level-team-mode.ps1` as the generated shared runtime.

P3 extends that runtime with:

- structured routing-threshold definitions
- a routing-policy snapshot function
- developer-instruction rendering from the structured policy
- startup-argument derivation from the current mode

Why:

- it keeps one generated runtime source of truth
- it reduces drift between startup behavior, inspection scripts, and tests
- it lets future scripts reuse the same policy model

### Decision 2: Add `codex-routing-policy.ps1` as a read-only inspection surface

The installer will generate a small user-level script that reports the current routing policy in JSON or text form.

The inspection output will include:

- current mode and switch state
- whether automatic routing is enabled
- startup-path semantics for `codex` and `codex-native`
- repository-scoped runtime-isolation notes
- default role thresholds
- research-to-implementation handoff rules
- adversarial bug-review rules

Why:

- it gives operators and tests a direct way to inspect the intended routing behavior
- it avoids relying on the injected developer-instruction string as the only validation surface

### Decision 3: The launcher will derive developer instructions from the routing-policy model

The generated launcher will no longer carry an independent handwritten routing summary.

Instead, it will:

1. read the current state
2. derive the current routing policy
3. render developer instructions from that policy
4. pass those instructions into native `codex.cmd`

Why:

- it ensures the launcher follows the same routing rules that the inspection script exposes
- it keeps `auto`, `manual`, and `off` semantics consistent

### Decision 4: Generated leader profile and playbook must mirror the approved routing rules

`team-leader.toml` and `team-mode-playbook.md` will be updated so they explicitly cover:

- wrapped `codex` vs `codex-native`
- native-routed vs enhanced vs pure-debugging startup
- routing thresholds for the core expert roles
- research-to-implementation handoff
- adversarial bug-review usage
- repository-scoped runtime isolation through per-repository `.omx`

Why:

- these assets are the operator-facing explanation layer
- the user explicitly asked for the rules to be stated clearly

## Risks / Trade-offs

- [Risk] The developer-instruction payload could become too verbose.
  Mitigation: keep each role threshold to one compact bullet and keep mode-specific wording concise.

- [Risk] A separate inspection script could drift from launcher behavior.
  Mitigation: generate both from the same shared support-script functions.

- [Risk] Operators may misunderstand `oh_my_codex=on` as automatic durable-team launch.
  Mitigation: state explicitly in both policy output and playbook that enhanced startup enables durable-team features but does not auto-launch a team.

- [Risk] The new inspection surface could be mistaken for a project-level policy file.
  Mitigation: keep it as a user-level generated script and explicitly describe project isolation as repository-scoped runtime state, not project-scoped global switches.

## Migration Plan

1. Create proposal, design, spec, and tasks artifacts for P3.
2. Extend the installer support runtime with routing-policy and developer-instruction helpers.
3. Generate `codex-routing-policy.ps1` and update the launcher, leader profile, and playbook.
4. Extend the PowerShell test for policy inspection and developer-instruction injection.
5. Validate OpenSpec and repo guard health.
6. Reinstall into the real user Codex home after repository validation passes.
