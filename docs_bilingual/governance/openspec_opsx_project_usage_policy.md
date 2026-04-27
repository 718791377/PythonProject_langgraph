---
doc_id: openspec_opsx_project_usage_policy
lang: en
canonical: docs_bilingual/governance/openspec_opsx_project_usage_policy.md
translation_of: null
doc_class: governance
status: active
---

# OpenSpec OPSX Project Usage Policy

## 1. Purpose

This document defines how this repository should use the current official OpenSpec OPSX workflow in Codex-driven work.

The goal is not to replace OpenSpec with a repository-local workflow. The goal is to align repository practice with the official OpenSpec workflow surface, while keeping repository-specific routing and document boundaries explicit.

In this repository, OPSX should also be read as the project-level handoff workflow between:

- user-level shared runtime or control surfaces that may be reused across projects
- repo-local source, repo-local durable truth, and repository-scoped structural change that must remain authoritative inside this repository

## 1A. New Session Entry Rule

For new sessions, do not start from this policy by default.

Read these project startup summaries first:

- [project_startup_summary.zh-CN.md](/D:/PythonProject_langgraph/docs_bilingual/project_startup_summary.zh-CN.md)
- [project_startup_summary.md](/D:/PythonProject_langgraph/docs_bilingual/project_startup_summary.md)

Only after that should the model decide whether this OPSX policy is relevant to the current task.

## 2. Authority Boundary

The authority order is:

1. official OpenSpec upstream behavior and workflow model
2. locally installed OpenSpec CLI capabilities
3. repository-level OPSX entry rules and routing

This means:

- the OpenSpec CLI remains the authoritative execution layer
- project-level `/opsx:*` usage in this repository is a repository-scoped workflow convention
- repository documentation must not describe repository-local wrappers as Codex-native built-ins
- repository OPSX flows may consume shared user-level runtime surfaces, but they must not treat user-level state or shared runtime directories as the canonical durable truth for this repository

## 3. Current Repository State

OpenSpec is already active in the repository at the artifact layer:

- `openspec/config.yaml` - repository OpenSpec configuration file.
- `openspec/changes/...` - directory tree for active and proposed OpenSpec change artifacts.
- `openspec/specs/...` - directory tree for stable OpenSpec capability specifications.

The repository also already materializes the official Codex OpenSpec instruction surface and the required enforcement surfaces:

- official Codex OpenSpec skills under `.codex/skills/`
- `tools/bootstrap-official-openspec.ps1` - PowerShell script that materializes or refreshes the official Codex OpenSpec instruction surface.
- `tools/verify_official_openspec.py` - verification script that checks the official OpenSpec bootstrap and generated artifacts.
- `tools/run_openspec_guard.py` - aggregate guard script that runs repository OpenSpec checks.
- `.githooks/pre-commit` - local Git hook that runs repository checks before commits.
- `.github/workflows/openspec-guard.yml` - GitHub Actions workflow for the OpenSpec guard.
- `.gitlab-ci.yml` - GitLab CI pipeline configuration for repository guard jobs.

Therefore:

- OpenSpec is already in use at both the artifact and enforcement layers
- current repository usage is aligned to the current official OPSX workflow surface at the repository workflow level
- repository `/opsx:*` routing remains repository-scoped guidance rather than a claim of Codex-native built-ins

## 4. Official OPSX Command Surface To Align With

Based on the currently installed OpenSpec package and its workflow templates, the repository should align to the following OPSX command set:

- `/opsx:onboard` - project-level workflow route for reading startup context and current OpenSpec state.
- `/opsx:new` - project-level workflow route for starting a new OpenSpec-backed change.
- `/opsx:continue` - project-level workflow route for resuming an active OpenSpec change.
- `/opsx:ff` - project-level workflow route for fast-forwarding missing OpenSpec artifacts.
- `/opsx:propose` - project-level workflow route for creating proposal, design, and task artifacts.
- `/opsx:explore` - project-level workflow route for pre-change exploration and scope clarification.
- `/opsx:apply` - project-level workflow route for implementing tasks from an active change.
- `/opsx:verify` - project-level workflow route for checking structural readiness and validation.
- `/opsx:sync` - project-level workflow route for syncing approved deltas into stable specs.
- `/opsx:archive` - project-level workflow route for archiving a completed change.

The repository should expose these through project-level workflow guidance backed by the official CLI, repository bootstrap or refresh, verification, hooks, and CI guard surfaces. If the official CLI surface changes later, rerun the repository refresh path instead of preserving stale repository wording.

## 5. Command Mapping Model

### 5.1 `/opsx:onboard`

Use for:

- first entry into the repository
- re-entry after long context loss
- onboarding into an unfamiliar mainline

Expected behavior:

- review project startup summary
- review relevant session summary if one exists
- inspect current OpenSpec state

Minimum CLI baseline:

- `openspec list --json` - official OpenSpec CLI command for listing OpenSpec state in machine-readable form.
- `openspec status` - official OpenSpec CLI command for showing the current repository OpenSpec status.
- repository startup documents

### 5.2 `/opsx:new`

Use for:

- starting a new structural change
- starting a new repository change that should produce OpenSpec artifacts

Minimum CLI baseline:

- `openspec new change "<name>"` - official OpenSpec CLI command for creating a named change.
- `openspec status --change "<name>" --json` - official OpenSpec CLI command for reading a named change status as JSON.

### 5.3 `/opsx:continue`

Use for:

- continuing an already active change
- resuming incomplete proposal, design, spec, or task work

Minimum CLI baseline:

- `openspec list --json` - official OpenSpec CLI command for listing OpenSpec state in machine-readable form.
- `openspec status --change "<name>"` - official OpenSpec CLI command for reading a named change status.

### 5.4 `/opsx:ff`

Use for:

- fast-forwarding artifact completion when a change exists but required artifacts are incomplete
- preparing a change so implementation can start cleanly

Repository rule:

- do not use `/opsx:ff` as a shortcut around missing design thinking
- use it only when the intent is already clear and artifact completion is the bottleneck

### 5.5 `/opsx:propose`

Use for:

- quickly creating proposal, design, tasks, and other apply-required artifacts in one step

Minimum CLI baseline:

- `openspec new change "<name>"` - official OpenSpec CLI command for creating a named change.
- `openspec status --change "<name>" --json` - official OpenSpec CLI command for reading a named change status as JSON.
- `openspec instructions <artifact> --change "<name>" --json` - official OpenSpec CLI command for generating instructions for a named artifact.

### 5.6 `/opsx:explore`

Use for:

- exploring a problem before deciding the exact change shape
- clarifying requirements, scope, and mainline ownership

Repository rule:

- explore mode may investigate code and artifacts
- explore mode should not silently jump to implementation

### 5.7 `/opsx:apply`

Use for:

- implementing tasks from an active change

Minimum CLI baseline:

- `openspec status --change "<name>" --json` - official OpenSpec CLI command for reading a named change status as JSON.
- `openspec instructions apply --change "<name>" --json` - official OpenSpec CLI command for generating apply instructions for a named change.

### 5.8 `/opsx:verify`

Use for:

- checking whether the current change is structurally ready to proceed or complete

Minimum CLI baseline:

- `openspec status` - official OpenSpec CLI command for showing the current repository OpenSpec status.
- `openspec validate --all` - official OpenSpec CLI command for validating all specs and changes.
- repository tests relevant to the change

### 5.9 `/opsx:sync`

Use for:

- syncing stable delta-spec conclusions back into main specs when appropriate

Repository rule:

- do not treat every implementation note as spec-sync material
- only reusable, cross-scenario, long-term rules should be synced into stable specs

### 5.10 `/opsx:archive`

Use for:

- archiving a completed change after artifacts, implementation, and validation are stable

Minimum CLI baseline:

- `openspec status --change "<name>"` - official OpenSpec CLI command for reading a named change status.
- `openspec archive <name>` - official OpenSpec CLI command for moving a completed change into archive history and promoting its delta specs into stable specs, or an equivalent archive flow that preserves the same repository-local result.

Repository archive gate:

- do not archive a change that still has an explicit archive blocker in its own artifacts
- do not archive a change that still lacks core artifacts such as `proposal.md`, `design.md`, or `tasks.md`
- do not archive a metadata-only or smoke-test placeholder directory as if it were a normal completed change
- if later work is still needed but the original archive was valid, prefer a forward follow-up change rather than silently normalizing an invalid archive

Repository archive isolation flow:

- Use this flow for changes that alter source code, scripts, tests, CI, checkers, runtime behavior, stable specs, startup instructions, `AGENTS.md` as the repository instruction surface, or structural governance rules. Purely explanatory text edits may use the lighter archive flow when they do not change enforceable behavior, but uncertain cases should use the dedicated archive worktree flow.
- In a dedicated archive worktree, run the archive operation for the completed change. A dedicated archive worktree is a separate Git worktree created only for the archive branch so archive-generated file moves do not mix with the main workspace.
- Verify inside that archive worktree before publication. Worktree-local verification must include the repository guard commands required by the change so archive-generated specs are checked before integration.
- Commit the archive branch after worktree-local verification passes. The archive branch is the Git branch that carries the archive result and its stable-spec updates.
- Merge the archive branch back into the main workspace through the normal GitLab-first flow. The main workspace is the repository checkout used by the session leader after the branch is integrated.
- Verify again in the main workspace after integration. The core rule is: verify first in the archive worktree, then verify again after the archive branch is integrated into the main workspace.

## 6. When OPSX Is Required In This Repository

OPSX should be treated as required for:

- new feature work with lasting repository impact
- architecture or workflow changes
- changes to reusable rules, specs, or long-term governance
- multi-file implementation with explicit rollout logic
- work expected to produce or update OpenSpec change artifacts

This requirement applies especially when work changes:

- the boundary between the user-level shared layer and this repository's project-level handoff layer
- repo-local source contracts
- repo-local durable-state semantics
- repository OpenSpec artifacts
- repository validation or acceptance meaning

In those cases, `/opsx:new`, `/opsx:propose`, or `/opsx:continue` should be treated as the structural entrypoint instead of relying on governance-only wording updates.

OPSX may be skipped for:

- one-off runtime investigation
- temporary log inspection
- narrow bug confirmation with no structural change
- minor documentation correction that does not change repository policy or workflow

If a task begins as a runtime investigation but evolves into reusable or structural work, it should be re-routed into OPSX flow explicitly.

## 7. Division Of Responsibility Between OpenSpec And docs_bilingual

### 7.1 OpenSpec

OpenSpec should carry:

- stable change artifacts
- proposal/design/tasks structure
- reusable specs
- validation-oriented change state

### 7.2 `docs_bilingual/`

`docs_bilingual/` should carry:

- project startup summaries
- session summaries
- governance policies
- methodology explanations
- implementation rollout plans
- operations manuals

### 7.3 Synchronization Rule

When both layers are affected:

- OpenSpec change artifacts must remain structurally correct
- `docs_bilingual/` documents must remain route-correct and role-correct
- neither layer should silently replace the other

### 7.4 Name Clarity Rule

When OPSX artifacts or OPSX-facing governance documents list a script, path, command, variable, profile, skill name, or other code-like name, the item must include a short purpose explanation.

The goal is cold-start readability: a new session with no chat context should know what the named item is for without searching the whole repository first.

Repository rule:

- do not leave bare code-name lists when the name is not self-explanatory
- add a brief phrase after the name that explains its role or when to use it
- keep examples concise; the explanation should aid routing, not become a full manual

Example pattern:

- `tools/example-check.py` - validates one concrete repository invariant before CI accepts the change.

## 8. Repository Entry Rule

For Codex work in this repository, the default OPSX entry should be:

1. `/opsx:onboard` for cold start or long-gap return
2. `/opsx:explore` when problem shape is still unclear
3. `/opsx:new` or `/opsx:propose` when a new change should be created
4. `/opsx:continue` when continuing an existing change
5. `/opsx:apply` for implementation
6. `/opsx:verify` before completion
7. `/opsx:sync` when reusable spec changes should be promoted
8. `/opsx:archive` when the change is truly complete

`/opsx:ff` is a change-preparation shortcut inside that sequence, not a replacement for the sequence.

## 9. Validation Gate

Repository-level OpenSpec work should not be considered complete until:

- the relevant change artifacts are consistent
- `openspec status` shows the expected state
- `openspec validate --all` has been run when structural OpenSpec work changed
- implementation and related repository documents are synchronized

## 10. Current Gap And Next Alignment Step

Current repository state is:

- aligned to the current official OPSX workflow surface at the repository workflow level
- backed by repository-local bootstrap, verification, hook, and CI enforcement surfaces

The next alignment step is:

- keep repository guidance aligned to later official OPSX surface changes
- keep project-level Codex guidance explicit
- do not misdescribe repository `/opsx:*` routing as Codex-native built-ins
- only change the local or global OpenSpec profile through explicit user-approved configuration work

## 11. Non-Goals

This policy does not:

- redefine OpenSpec upstream behavior
- claim Codex CLI has native built-in support for every `/opsx:*` command in this repository
- force all repository documents into `openspec/specs`
- authorize silent changes to global OpenSpec configuration
