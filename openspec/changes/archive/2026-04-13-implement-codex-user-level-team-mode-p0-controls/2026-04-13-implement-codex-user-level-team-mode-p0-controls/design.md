## Context

The bilingual implementation plan is already complete and defines the long-term operating model:

- native Codex remains the permanent base layer
- `oh_my_codex` is an optional global switch
- `subagent_routing` is a separate global switch with `auto / manual / off`
- `team-leader` means the current main Codex CLI session, not a worker pane
- pure debugging mode is `oh_my_codex=off` plus `subagent_routing=off`

What is still missing is a safe first implementation slice.

Current state:

- there is no repo-local generator for user-level Codex team-mode assets
- there is no state file that separates `oh_my_codex` from `subagent_routing`
- there is no generated `team-leader.toml`
- there is no tested wrapper set for toggling the two global controls

The main bottleneck is not orchestration complexity. The main bottleneck is the absence of a safe control surface that can be generated, tested, and evolved without writing directly into the user's real Codex home during development.

## Goals / Non-Goals

**Goals:**

- implement a repo-local installer/generator for user-level team-mode control assets
- generate additive assets into an explicit target Codex home
- keep `oh_my_codex` and `subagent_routing` as separate persisted controls
- create install-time backup snapshots before any managed write begins
- restore the previous managed state automatically if the install fails after writing starts
- generate a `team-leader.toml` that encodes the "main session is the leader" rule
- prove that native `codex` remains untouched
- make the P0 slice testable in a temporary directory

**Non-Goals:**

- directly enabling full team execution from the generated assets
- implementing hybrid staffing wrappers such as `omx-team-hybrid.ps1`
- implementing compose-manifest mixed persistent panes
- modifying OpenClaw runtime or proxy launchers
- patching real user assets under `C:\Users\lenovo\.codex` as part of repository development

## Decisions

### Decision 1: Implement a repo-local installer/generator instead of mutating the real user home during development

The repository will provide a script that accepts an explicit `-CodexHome` target path and renders the user-level assets there.

Why:

- it keeps development and tests reversible
- it allows cross-project reuse without binding the logic to this repository's own runtime
- it avoids accidental damage to the user's active Codex home while the control model is still being proven

Alternatives considered:

- Write directly into `C:\Users\lenovo\.codex` from the repository.
  Rejected because it is too risky for iterative development and too hard to validate safely.
- Modify the native `codex` launcher in place.
  Rejected because it violates the plan's safety boundary.

### Decision 2: The generated surface SHALL be additive only

The installer will generate only new namespaced assets:

- `agents/team-leader.toml`
- `bin/_codex-user-level-team-mode.ps1`
- `bin/codex-omx-*.ps1`
- `bin/codex-subagents-*.ps1`
- `bin/codex-routing-status.ps1`
- `state/user-level-team-mode.json`

It will never generate or overwrite:

- `codex`
- `codex.cmd`
- `codex.ps1`

Why:

- preserving the native Codex base layer is a hard requirement
- additive assets are easier to reason about and easier to roll back

### Decision 3: Persist one shared JSON state file with separate `oh_my_codex` and `subagent_routing` fields

The P0 slice needs one simple, explicit state source that all generated scripts can read and update.

State shape:

- `schema_version`
- `oh_my_codex`
- `subagent_routing`
- `updated_at`

Default values:

- `oh_my_codex = off`
- `subagent_routing = auto`

Why:

- it matches the plan's rule that the two switches are independent
- it keeps pure debugging mode derivable instead of hidden
- JSON is easy to inspect in tests and simple for PowerShell wrappers

Alternatives considered:

- Environment variables only.
  Rejected because they are not durable enough for a global user-level mode.
- Multiple small flag files.
  Rejected because that creates drift between related state transitions.

### Decision 4: Generate one shared support script plus thin command wrappers

The installer will generate a shared PowerShell support file under `bin/` and keep the individual entry scripts thin.

Why:

- it avoids duplicating state logic across many wrappers
- it keeps later expansion possible without rewriting every wrapper
- it makes status rendering and mode computation consistent

### Decision 5: `team-leader.toml` will formalize the current main session as leader

The generated leader profile will describe the current main Codex CLI session as the leader lane and explicitly reject the idea of spawning a separate leader pane.

Why:

- this is the core governance decision from the approved plan
- it preserves native subagent routing authority in the main session
- it keeps `team-executor` separate from leadership semantics

### Decision 6: Generated files will use managed markers and reject unmanaged collisions by default

Each generated `.ps1` and `.toml` file will carry a managed marker header.

Installer behavior:

- overwrite managed files on reinstall
- refuse to overwrite an unmanaged file unless `-Force` is given

Why:

- it preserves user trust
- it prevents the repository from silently deleting or replacing hand-maintained user assets

### Decision 7: Installation writes will be wrapped in a versioned backup-and-rollback transaction

Before the installer writes any managed asset or creates the shared state file, it will capture a timestamped snapshot under:

- `<CodexHome>\backups\codex-user-level-team-mode\<timestamp>\`

The snapshot will record:

- every targeted generated file path
- whether the path existed before the install
- a copy of the pre-install file content for each existing target
- backup manifest metadata so operators can inspect what would be restored

If any failure happens after writes begin, the installer will:

- restore each targeted path to its pre-install content if it previously existed
- remove newly created managed files that did not exist before the failed install
- keep the backup snapshot for diagnosis and possible later manual rollback

Why:

- it gives the user a concrete rollback boundary instead of a promise
- it reduces the risk of leaving the user's Codex home half-mutated after partial failure
- it strengthens the "native Codex must remain usable" rule with transactional behavior

Alternatives considered:

- Best-effort writes with no rollback.
  Rejected because that leaves a partial-install failure window.
- Only document a manual backup step.
  Rejected because the user explicitly asked for timely restoration on failure.

## Risks / Trade-offs

- [Risk] The P0 slice does not yet change actual startup behavior for native Codex or oh-my-codex.
  Mitigation: treat P0 explicitly as the control-layer foundation; leave startup binding to a later phase.

- [Risk] A generated `team-leader.toml` may drift from future oh-my-codex schema expectations.
  Mitigation: keep the profile narrow and text-only, and validate shape against existing agent TOML patterns.

- [Risk] Users may assume `oh_my_codex=on` means durable teams are fully ready.
  Mitigation: keep scope clear in the generated status output and in the spec; P0 only persists the control state.

- [Risk] PowerShell JSON parsing differences across versions can create subtle failures.
  Mitigation: use simple JSON shapes and Windows PowerShell-compatible parsing paths.

- [Risk] Backup snapshots can accumulate over time.
  Mitigation: keep them namespaced under one backup root and treat retention cleanup as a later operator command, not as part of the install transaction.

## Migration Plan

1. Create proposal, design, spec, and task artifacts for the P0 slice.
2. Implement the installer/generator and the generated support/wrapper assets.
3. Add versioned backup snapshot creation and rollback-on-error logic to the installer.
4. Add a dedicated PowerShell test that installs into a temporary Codex home.
5. Validate default mode, mode transitions, pure debugging mode, unmanaged collision rejection, and rollback behavior.
6. Run OpenSpec validation and repository guard validation.
7. Leave direct user-home installation and richer orchestration wrappers for later phases.

## Open Questions

- Whether the next phase should add a generated playbook and hybrid wrapper before binding the global switch into real startup behavior.
