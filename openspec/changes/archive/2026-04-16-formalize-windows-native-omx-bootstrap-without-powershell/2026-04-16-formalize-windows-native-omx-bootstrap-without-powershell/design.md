## Context

The user-level capability-switch model now works: worker-centric flows select `native_omx`, graph-signaled flows select `langgraph`, and both lanes are available under the same enabled capability set. The remaining fragility is not in routing policy anymore. It is in the globally installed `oh-my-codex` runtime.

The current upstream Windows prompt-worker bootstrap path uses `spawnSync('powershell.exe', ...)` to create a detached Node controller. In this environment, Node cannot spawn `powershell.exe` or `cmd.exe` without hitting `EPERM`. However, direct Node child process creation still works. A local experiment also showed that a child `node.exe` process can outlive its parent shell without requiring the PowerShell bootstrap path.

## Goals / Non-Goals

**Goals:**

- make the Windows native_omx prompt-worker bootstrap formally independent from `powershell.exe`
- define a repeatable repo-managed way to preserve that repair across reinstall or upgrade events
- keep validation focused on real native_omx worker startup

**Non-Goals:**

- changing the routing policy itself
- redesigning LangGraph behavior
- introducing a new background service only for this fix unless proven necessary

## Decisions

### Decision 1: Treat the current manual global patch as evidence, not as the final process

The current patched global `runtime.js` proves the fix direction, but it is not itself the long-term delivery mechanism.

Alternative considered:

- keep hand-patching the global install when needed
  - rejected because it is not durable across upgrades and is hard to audit

### Decision 2: The Windows bootstrap contract should become direct Node controller launch

The Windows bootstrap contract should be formalized as direct Node launch of the worker controller instead of a PowerShell-mediated bootstrap.

Alternative considered:

- keep PowerShell and try to work around EPERM with different flags
  - rejected because direct experiments showed Node cannot spawn `powershell.exe` or `cmd.exe` successfully in this environment at all

### Decision 3: The repository should own a repair or verification path for the global install

The repository should own one or both of:

- a repeatable repair script
- a verification or reapply script

so that the fix can be checked and restored after `oh-my-codex` reinstall or upgrade.

## Risks / Trade-offs

- [Risk] The global install may change structure on upgrade. -> Mitigation: keep the repair process version-aware and verify the target block before patching.
- [Risk] Direct Node bootstrap may have lifecycle edge cases different from PowerShell Start-Process. -> Mitigation: validate real worker startup, resume, and shutdown.
- [Risk] A repo-managed repair flow could drift from the installed runtime version. -> Mitigation: keep the repair narrowly scoped and anchored to the observed runtime block.

## Migration Plan

1. Capture the repaired runtime behavior as a formal contract.
2. Implement a repo-managed repair or verification script.
3. Validate native_omx worker startup after repair.
4. Keep backup or rollback instructions explicit.

## Open Questions

- Should the repo-managed solution patch the installed runtime automatically, or should it expose a verified operator command that the user runs explicitly after upgrades?
