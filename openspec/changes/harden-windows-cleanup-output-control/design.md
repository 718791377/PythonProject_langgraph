# Design: Harden Windows cleanup output control

## Context

The repository already generates a scoped `win-shims` directory for wrapped `codex-ohmy` launches. The launcher prepends that directory to PATH while native Codex runs, then restores PATH and PATHEXT. The generated `taskkill.cmd` and `taskkill.ps1` shims suppress successful Windows `taskkill` output while preserving non-zero failure diagnostics.

The observed remaining leak appears after native subagent or `/resume` cleanup. That means the current CMD shim is necessary but not sufficient for every cleanup path. The likely bottleneck is command resolution: some cleanup caller may explicitly invoke `taskkill.exe`, may not use PATHEXT lookup, or may be spawned with a narrower environment than the initial wrapped process.

Stakeholders:

- The operator, who wants clean conversations and error-only cleanup diagnostics.
- The main Codex session, which remains the leader and should not lose `omx_*` MCP tools.
- Native subagents and `/resume` paths, which may spawn and clean up Windows child process trees.
- Future installers, which must preserve native Codex bypass behavior and avoid mutating `config.toml`.

## Goals / Non-Goals

**Goals:**

- Keep the default cleanup-output control scoped and conservative.
- Preserve direct `omx_state`, `omx_memory`, `omx_code_intel`, and `omx_trace` MCP availability.
- Add an explicit opt-in route for `.exe`-level `taskkill` interception when evidence shows CMD shimming is bypassed.
- Make the opt-in path script-backed, test-backed, and visible in installer JSON output.
- Preserve rollback safety through existing managed installer backups.

**Non-Goals:**

- Do not globally filter Codex TUI output.
- Do not disable native subagents, omx, LangGraph, or MCP tools to hide logs.
- Do not move Codex-dedicated MCP tools into MCP Router.
- Do not install `taskkill.exe` interception by default.
- Do not edit the user-level `config.toml`.

## Decisions

### Decision 1: Keep CMD shimming as the default

Default wrapped launch continues to prioritize `taskkill.cmd` through PATH/PATHEXT. This keeps the existing behavior minimal and avoids surprising environments that should not see a shadow `taskkill.exe`.

Alternative considered: always install `taskkill.exe`. Rejected because executable shadowing is broader than CMD command lookup and should require explicit opt-in.

### Decision 2: Add an opt-in `InstallTaskkillExeShim` switch

The installer gets an explicit `InstallTaskkillExeShim` switch. When set, it compiles the managed C# shim source into `win-shims\taskkill.exe`, reports the compile result in JSON, and generated launchers prioritize `.EXE` in PATHEXT for the wrapped child process tree.

Alternative considered: ship a prebuilt binary in the repository. Rejected because the repository should remain source-first and avoid committing local binary build artifacts.

### Decision 3: Compile from managed C# source at install time

The existing `taskkill-shim-source.cs` source remains the authoritative executable shim source. The installer attempts to find `csc.exe` from PATH or the Windows .NET Framework directories and fails fast if explicit EXE shim installation was requested but compilation is unavailable.

Alternative considered: silently skip EXE shim compilation when no compiler is found. Rejected because an explicit opt-in should be deterministic and visible.

### Decision 4: Scope `.EXE` PATHEXT mutation to wrapped launches only

The generated startup launcher only prepends `.EXE` to PATHEXT when the opt-in EXE shim is enabled. As with the existing CMD shim, PATH/PATHEXT are restored in `finally`.

Alternative considered: modify the user shell profile or global PATH. Rejected because cleanup-output control must not leak into other terminals or projects.

### Decision 5: Strengthen checker evidence

The checker must verify the optional EXE switch, compile function, report fields, and scoped PATHEXT behavior markers. This turns the safety rule into script-backed governance instead of a prompt reminder.

Alternative considered: rely only on installer tests. Rejected because the repository guard needs a fast static contract check.

## Risks / Trade-offs

- [Risk] Some cleanup path invokes an absolute `C:\Windows\System32\taskkill.exe` path. → Mitigation: this change documents and tests opt-in EXE command-name interception, but absolute system paths remain outside scope; if found, the next fix should target that caller or upstream behavior rather than global binary replacement.
- [Risk] `csc.exe` is unavailable on a target Windows machine. → Mitigation: default behavior does not need compilation; explicit EXE opt-in fails with a clear reason.
- [Risk] `.EXE` PATHEXT precedence could affect unrelated child commands. → Mitigation: enabled only by explicit switch and only inside the wrapped native Codex child process tree.
- [Risk] Optional EXE shim could mask a real cleanup failure. → Mitigation: the shim suppresses only zero-exit success output and forwards non-zero diagnostics to stderr.

## Migration Plan

1. Land repository source, tests, and OpenSpec updates.
2. Run local validation.
3. Publish by GitLab-first MR only after local validation passes and the model recommends release timing to the user.
4. After merge, reinstall user-level team-mode assets normally to keep default CMD shimming.
5. If PID success lines still appear, rerun the installer with the explicit `InstallTaskkillExeShim` switch and verify whether the optional `taskkill.exe` shim removes the remaining leak.

## Open Questions

- Does native Codex subagent cleanup call `taskkill.exe` by command name, by PATHEXT resolution, or by absolute system path? This change covers command-name and PATHEXT interception; absolute path interception remains an upstream/caller-specific investigation.
- Should a later release add a diagnostic mode that records which cleanup command path was resolved without printing to the Codex conversation? This is useful but not required for the current hardening.
