---
doc_id: openspec_comet_superpowers_workflow_policy
lang: en
doc_class: governance
status: active
---

# OpenSpec Comet Superpowers Workflow Policy

## 1. Purpose

This policy defines the repository target for a Comet-controlled OpenSpec + Superpowers workflow.

The target is an additive control model:

- OpenSpec is the WHAT layer: proposal, requirements, delta specs, tasks, validation, lifecycle, archive, and sync.
- Superpowers is the HOW layer: brainstorming, technical design, implementation planning, test-driven development, subagent-driven development, code review, and branch finishing.
- Comet is the control layer: phase dispatch, workflow state, transition guards, resume, and evidence gates.

Comet does not replace OpenSpec, Superpowers, native Codex subagents, native_omx, or LangGraph. It coordinates OpenSpec and Superpowers as a workflow surface.

## 2. Evidence Basis

This policy is based on the local reference list in `reference_files/2.md` and the Comet, OpenSpec, and Superpowers upstream project descriptions.

The local mp4 reference names the same Comet + OpenSpec + Superpowers topic. Detailed video transcript evidence was not available in the current session, so this policy uses the upstream README behavior as the concrete source for the first repository upgrade.

## 3. Layer Contract

Use this layer map for all Comet-style OpenSpec work:

| Layer | Owner | Responsibility |
| --- | --- | --- |
| WHAT | OpenSpec | Change proposal, requirements, scenarios, tasks, spec lifecycle, validation, archive, and delta-to-main spec sync. |
| HOW | Superpowers | Brainstorming, design document, implementation plan, TDD, subagent-driven development, code review, and finishing a development branch. |
| CONTROL | Comet | `/comet` entry routing, phase detection, workflow state, guard scripts, resume, and archive evidence checks. |

Skills remain workflow instruction surfaces. A Comet skill, OpenSpec skill, Superpowers skill, or profile is not native subagent evidence. Native subagents remain leader-side spawned roles under the repository orchestration policy.

## 4. Five-Phase Workflow

The full Comet-controlled workflow is:

```text
Open -> Design -> Build -> Verify -> Archive
```

Phase ownership:

1. Open: OpenSpec owns the proposal, initial design, and task breakdown.
2. Design: Superpowers owns deep design, brainstorming, and design-document refinement.
3. Build: Superpowers owns implementation planning, TDD, subagent-driven development, code review, and branch/worktree execution discipline.
4. Verify: OpenSpec and Superpowers both contribute. Verification must produce evidence, not just a claim.
5. Archive: OpenSpec owns delta-to-main spec sync, archive movement, and archive status.

Preset workflows such as hotfix or tweak may skip brainstorming or full planning only when the skipped steps are explicit. Verify and Archive remain evidence-gated.

## 5. State and Resume Contract

A Comet-style workflow must not depend only on chat history or unchecked markdown inference.

The state model is decoupled:

- `.openspec.yaml` or the installed OpenSpec equivalent owns spec lifecycle and change metadata.
- `.comet.yaml` or a repository-approved equivalent owns workflow phase, preset, design document path, plan path, build_mode, isolation, verify_mode, verify_result, verification_report, branch_status, verified_at, and archived state.

Resume behavior:

- `/comet` or an equivalent entry point detects the active change and current phase.
- `/comet continue` or an equivalent resume path restores from persisted state.
- If multiple active changes exist, the operator must select the intended change before execution continues.

## 6. Guard and Evidence Contract

Phase transitions must be guarded by executable checks.

A guard must fail closed for:

- missing proposal, spec, design, task, plan, or report artifacts;
- invalid phase values or illegal phase jumps;
- missing build_mode or isolation decisions before leaving Build;
- `build_mode: direct` in the full workflow without `direct_override` or an equivalent explicit exception;
- missing `verification_report` before Verify passes;
- `branch_status` not handled before Verify passes;
- archive attempts before verification evidence exists.

Guard failures should use a hard-stop style such as `[HARD STOP]` plus actionable remediation.

Archive requires completed tasks, validation evidence, an existing verification report, handled branch state, and delta-to-main spec sync.

## 7. Installation and Mutation Boundary

This repository does not treat this governance policy as permission to mutate runtime assets.

The following actions require explicit operator approval or a later OpenSpec change with a scoped write plan and rollback path:

- `npm install -g @rpamis/comet` - global Comet package installation.
- `comet init` - Comet workflow initialization that may write platform skills and scripts.
- `comet update` - Comet package or installed skill update.
- `comet doctor` - diagnostic command when paired with repair or mutation actions.
- installing Superpowers plugin files;
- overwriting `.codex/skills` content;
- editing `C:\Users\lenovo\.codex\config.toml`.

Read-only commands such as `comet status --json` may be used after Comet is already installed and scoped to the target repository.

## 8. Repository Scope Boundary

`D:\PythonProject_langgraph` owns this policy and the repository-local OpenSpec artifacts for the Codex orchestration line.

This policy does not authorize writes to:

- consumer repositories outside `D:\PythonProject_langgraph`;
- generic project-root workspaces outside this repository;
- any consumer project's `.omx/state` directory.

Consumer-project adoption must happen in that consumer repository with its own OpenSpec artifacts, repo-local state, validation, and publication decision.

## 9. Validation

The policy is backed by `tools/check_openspec_comet_superpowers_policy.py` - validates this bilingual governance surface, the registry entry, and core Comet/OpenSpec/Superpowers boundary terms.

Before treating this upgrade as complete, run:

```powershell
python tools/check_openspec_comet_superpowers_policy.py --root . --json
python test/run_openspec_guard_json.test.py
python tools/check_document_governance_rules.py --root . --json
openspec validate --all
```

If the checker fails, repair the policy, registry, or OpenSpec change before continuing.
