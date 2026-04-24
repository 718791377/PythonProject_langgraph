## Context

P3 already made the routing thresholds, research-to-implementation split, and adversarial bug-review rules visible in generated policy output.

Current reality after P3:

- `codex-routing-policy.ps1` exposes the bug-review triad only as a documented threshold
- `team-leader.toml` and `team-mode-playbook.md` mention the triad, but only as guidance text
- the real user-level agent roster still lacks `bug-finder`, `bug-rebutter`, and `bug-judge`
- this means Codex CLI can see the threshold, but the strongest review lane is not yet materially callable

The P4 slice is to close that gap without changing the core startup model:

- native Codex stays the permanent base layer
- oh-my-codex remains a global feature switch, not a per-session mutation
- burst-review roles stay leader-side short bursts, not durable panes

## Goals / Non-Goals

**Goals:**

- generate real user-level agent profiles for `bug-finder`, `bug-rebutter`, and `bug-judge`
- keep those roles leader-side, bursty, and read-only by default
- expose those roles through the routing-policy inspection surface as installed callable assets
- align generated `team-leader.toml` and `team-mode-playbook.md` with the now-real burst-review roles
- keep the new files inside the same additive-only backup and rollback transaction
- make the new role layer testable in a temporary Codex home before touching the real user install

**Non-Goals:**

- creating a persistent bug-review team or compose manifest
- auto-invoking burst-review roles on every `codex` launch
- changing the global switch model
- changing native `codex.cmd`, native `omx.cmd`, or OpenClaw runtime behavior
- forcing every project to use the burst-review triad

## Decisions

### Decision 1: Generate stable user-level agent profiles with the exact callable names

The installer will generate:

- `agents/bug-finder.toml`
- `agents/bug-rebutter.toml`
- `agents/bug-judge.toml`

These exact names are the contract used by routing policy, playbook guidance, and real `omx agents list --scope user` verification.

Why:

- the routing threshold already names these roles explicitly
- stable names make the roles callable across repositories
- user-level generation keeps the feature additive and reversible

### Decision 2: Keep the burst-review triad leader-side and read-only by default

The three roles are not durable worker panes.

Their default posture is:

- inspect code, tests, diffs, and evidence
- do not edit files by default
- pass only judged survivors into `executor` or `debugger`

Why:

- this preserves the approved split between burst experts and durable workers
- it matches the user requirement that research and adjudication stay separate from implementation
- it reduces accidental cross-role mutation during contested bug triage

### Decision 3: Encode the incentive structure directly into the generated role prompts

`bug-finder` will be optimized for recall:

- low-impact bug: `+1`
- medium bug: `+5`
- severe bug: `+10`

`bug-rebutter` will be optimized to falsify weak claims:

- disproving a claim earns the corresponding score
- failing to disprove a real claim costs double that score

`bug-judge` will arbitrate the two reports using a correctness-first posture:

- act as if a hidden ground truth exists
- correct verdicts are rewarded, wrong verdicts penalized
- output only the survivor set that deserves escalation

Why:

- the user explicitly asked for this stronger adversarial-review loop
- the incentive structure is part of the operating contract, not just optional wording

### Decision 4: Extend the shared support runtime with burst-role metadata and availability detection

P0 through P3 already rely on `bin/_codex-user-level-team-mode.ps1` as the generated shared runtime.

P4 extends that runtime with:

- a helper that resolves the user-level `agents/` directory
- structured burst-review role metadata
- installation-availability checks for each generated role
- routing-policy output that includes the installed burst-role set

Why:

- routing policy should describe the real callable surface, not only conceptual guidance
- tests need a direct inspection surface that proves the roles are installed
- the launcher, policy script, playbook, and tests should share one runtime source of truth

### Decision 5: Keep the stronger loop visible in the generated operator-facing assets

`team-leader.toml` and `team-mode-playbook.md` will be updated so they say:

- the burst-review triad is generated as user-level callable roles
- the triad stays bursty and leader-side
- only judged survivors are escalated into execution or debugging lanes

Why:

- operators need an accurate explanation layer
- the new roles must be understandable outside this repository as reusable user-level assets

## Risks / Trade-offs

- [Risk] More generated agent files increase install surface area.
  Mitigation: keep them additive-only and inside the existing backup-and-rollback transaction.

- [Risk] The burst-review roles could be mistaken for persistent panes.
  Mitigation: mark them leader-side burst roles in routing policy, team-leader, and playbook.

- [Risk] The incentive prompts could encourage noise without evidence.
  Mitigation: require concrete file, test, diff, or runtime evidence for every claim or rebuttal.

- [Risk] Routing policy could claim the roles exist when installation failed.
  Mitigation: derive installed-role visibility from file existence in the generated `agents/` directory.

## Migration Plan

1. Create proposal, design, tasks, and spec artifacts for P4.
2. Extend the installer with generated burst-review agent profiles.
3. Extend the shared support runtime, leader profile, and playbook with installed burst-role metadata.
4. Extend the PowerShell test for generation, policy visibility, and rollback.
5. Validate OpenSpec and repo guard health.
6. Reinstall into the real user Codex home and verify the live user-level agent roster.
