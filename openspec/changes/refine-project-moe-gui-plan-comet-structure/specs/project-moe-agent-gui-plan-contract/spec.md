## ADDED Requirements

### Requirement: Project MOE GUI Plan Uses Full Comet Executable Structure

The Project MOE Agent GUI implementation plan SHALL use a full Comet executable-plan structure that separates documentation readiness, target-project readiness, GUI runtime completion, local integration, and remote publication authorization.

#### Scenario: Plan structure is implementation-slicing ready

- **GIVEN** an implementer opens `docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md`
- **WHEN** they review the plan before code implementation
- **THEN** the plan exposes goal, architecture, relationship model, source-of-truth, install artifacts, CLI contract, GUI contract, JSON state model, readiness lanes, safety rules, rollback rules, verification path, implementation tasks, risk decisions and self-checks
- **AND** it does not claim target projects are GUI-ready without readiness evidence.

#### Scenario: Runtime capability is not overstated

- **GIVEN** the plan is structurally ready
- **WHEN** a target project only has static Phase 1 evidence or blockers
- **THEN** the plan keeps that target project in Ready-candidate or Repair Lane
- **AND** `control_mode_allowed` remains false until the target project's readiness checker proves ready.

#### Scenario: Comet script evidence is honest

- **GIVEN** the current Windows shell cannot run Comet `.sh` scripts
- **WHEN** the change records Comet state
- **THEN** the state records the script blocker and uses OpenSpec/repository gates as fallback evidence
- **AND** it does not claim `comet-state.sh` or `comet-guard.sh` passed.

### Requirement: Project MOE GUI Uninstall Apply Deletes Only Verified Managed Artifacts

The Project MOE GUI uninstall command SHALL support an explicit `--apply` path that deletes only Project MOE GUI managed artifacts after manifest allowlist and hash verification pass, while preserving target-project private prompts, Agent TOMLs, and `.omx/state` runtime state.

#### Scenario: Successful apply removes only managed GUI artifacts

- **GIVEN** a target project has a Project MOE GUI install manifest produced by this toolchain
- **AND** every planned managed-file path is in the Project MOE GUI managed artifact allowlist
- **AND** every non-manifest managed file hash matches the manifest
- **WHEN** the operator runs `plan_project_moe_gui_uninstall.py --apply --json`
- **THEN** the command deletes only the verified managed GUI files
- **AND** the JSON payload reports `apply_supported=true`, `delete_executed=true`, `applied_file_changes`, and an `uninstall_receipt`
- **AND** target-project `MOE.md`, `.codex/agents/*.toml`, and `.omx/state` are preserved.

#### Scenario: Unsafe manifest fails closed before deletion

- **GIVEN** a target install manifest lists a path outside the Project MOE GUI managed artifact allowlist
- **OR** a non-manifest managed file has a missing or mismatched hash
- **OR** a managed entry resolves to a directory
- **WHEN** the operator runs the uninstall command with `--apply`
- **THEN** the command fails closed before deleting any file
- **AND** it reports a stable blocker such as `blocked:uninstall_path_not_in_managed_allowlist`, `blocked:managed_file_hash_missing`, `blocked:managed_file_hash_mismatch`, or `blocked:managed_path_is_directory`.
