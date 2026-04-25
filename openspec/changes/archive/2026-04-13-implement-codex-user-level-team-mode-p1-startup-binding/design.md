## Context

The P0 slice already provides:

- additive user-level control assets
- separate persisted `oh_my_codex` and `subagent_routing` state
- install-time backup snapshots and rollback-on-error
- validation that does not touch the native `codex` entrypoint

What is still missing is a runtime bridge between that state and ordinary `codex` launches.

The current real user environment shows:

- native Codex resolves to the npm-installed `C:\Users\lenovo\AppData\Roaming\npm\codex.cmd`
- the user's PowerShell profile is light and currently does not wrap `codex`
- `codex-cli 0.120.0` supports runtime overrides through `-c key=value` and `--disable <feature>`
- current `~/.codex/config.toml` already contains oh-my-codex-biased configuration

This means the safest reversible binding surface is a managed PowerShell profile block that wraps `codex` while leaving the native executable untouched.

## Goals / Non-Goals

**Goals:**

- bind normal PowerShell `codex` launches to the persisted team-mode state
- preserve the native npm-installed `codex` files unchanged
- provide an explicit `codex-native` bypass for raw native behavior
- disable omx-specific startup behavior when `oh_my_codex=off`
- disable multi-agent startup routing when `subagent_routing=off`
- extend backup and rollback to include the PowerShell profile path

**Non-Goals:**

- binding `cmd.exe` launches in this phase
- replacing the npm-installed `codex` command
- changing OpenClaw runtime settings
- implementing mixed-pane orchestration here

## Decisions

### Decision 1: Use a managed PowerShell profile block instead of replacing the native executable

The startup binding will be installed by adding a managed block to the user's PowerShell profile.

That block will define:

- `codex`
  - a thin function that forwards to the generated launcher script
- `codex-native`
  - a thin function that forwards directly to the native npm-installed Codex command

Why:

- function precedence lets PowerShell intercept `codex` without modifying the npm-installed files
- the binding remains additive and reversible
- `codex-native` gives an immediate escape hatch if the wrapper misbehaves

### Decision 2: The launcher will translate state to Codex CLI overrides

The generated launcher script will read `state/user-level-team-mode.json` and map it to runtime arguments.

Core mapping:

- `oh_my_codex=on`
  - use team-mode developer instructions
  - keep omx-specific MCP servers enabled
- `oh_my_codex=off`
  - use native-mode developer instructions
  - disable omx-specific MCP servers
  - disable the omx notify hook
- `subagent_routing=auto`
  - keep multi-agent available
  - use automatic-routing instructions
- `subagent_routing=manual`
  - keep multi-agent available
  - use manual-routing instructions
- `subagent_routing=off`
  - disable multi-agent with `--disable multi_agent`
  - use no-routing instructions

Why:

- `codex-cli 0.120.0` already supports `-c` and `--disable`
- runtime overrides avoid destructive edits to the native Codex installation
- state-to-args mapping is testable with a fake native Codex target

### Decision 3: Generate launcher-owned developer-instruction presets

The launcher will not depend on the top-level `developer_instructions` value from `config.toml`.

Instead it will generate and own small instruction presets for:

- omx-enabled auto routing
- omx-enabled manual routing
- native auto routing
- native manual routing
- no-routing / pure debugging

Why:

- the wrapper needs deterministic behavior that matches the team-mode state
- relying on pre-existing config text would make startup behavior drift across machines
- owning the preset text keeps behavior consistent across projects

Trade-off:

- wrapped PowerShell `codex` sessions become launcher-governed rather than raw-config-governed
- this is mitigated by the `codex-native` bypass entrypoint

### Decision 4: Backup and rollback must cover external profile paths as first-class targets

P0 backup logic already snapshots files inside the target Codex home.

P1 extends the same transaction to include:

- the generated launcher script
- the PowerShell profile file outside the Codex home

Why:

- the profile is the new critical mutation surface
- a partial profile write would be more disruptive than a missing helper script
- the user explicitly asked for timely restoration after errors

### Decision 5: Supported startup binding is PowerShell only in this phase

The installer will bind PowerShell-based `codex` launches only.

It will not attempt to alter:

- `cmd.exe`
- npm-installed `codex.cmd`
- npm-installed `codex.ps1`

Why:

- PowerShell is the current user-facing shell and the supported Windows path in the plan
- this keeps the binding narrow and reversible
- it avoids cross-shell ambiguity and PATH-level breakage

## Risks / Trade-offs

- [Risk] Wrapped PowerShell launches may behave differently from raw `codex.cmd`.
  Mitigation: provide `codex-native` and keep the native executable untouched.

- [Risk] The launcher-owned developer instructions may drift from future Codex or oh-my-codex expectations.
  Mitigation: keep the instruction presets narrow and centered on routing mode only.

- [Risk] Users launching from `cmd.exe` will not get the startup binding.
  Mitigation: document PowerShell as the supported shell for this phase.

- [Risk] Editing the profile creates a higher-stakes mutation surface.
  Mitigation: extend timestamped backup snapshots and rollback to cover the profile file.

## Migration Plan

1. Create the P1 proposal, design, spec, and tasks artifacts.
2. Extend the installer with launcher generation and managed profile-block insertion.
3. Add a fake-native-Codex test path to validate runtime argument mapping.
4. Validate profile rollback and the `codex-native` bypass behavior.
5. Run OpenSpec validation and repository guard validation.
6. Reinstall into the real user home only after repository validation passes.
