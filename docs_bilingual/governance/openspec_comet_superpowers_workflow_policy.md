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

This policy is based on the local reference list in `reference_files/2.md`, the Comet, OpenSpec, and Superpowers upstream project descriptions, and the repository-local PMBOK8 notes under `PMP/PMP_MD/`.

The local mp4 reference names the same Comet + OpenSpec + Superpowers topic. Detailed video transcript evidence was not available in the current session, so this policy uses the upstream README behavior as the concrete source for the first repository upgrade.

## 3. Layer Contract

Use this layer map for all Comet-style OpenSpec work:

| Layer | Owner | Responsibility |
| --- | --- | --- |
| WHAT | OpenSpec | Change proposal, requirements, scenarios, tasks, spec lifecycle, validation, archive, and delta-to-main spec sync. |
| HOW | Superpowers | Brainstorming, design document, implementation plan, TDD, subagent-driven development, code review, and finishing a development branch. |
| CONTROL | Comet | `/comet` entry routing, phase detection, workflow state, guard scripts, resume, and archive evidence checks. |

Skills remain workflow instruction surfaces. A Comet skill, OpenSpec skill, Superpowers skill, or profile is not native subagent evidence. Native subagents remain leader-side spawned roles under the repository orchestration policy.

Document directory boundary:

- `docs_bilingual/` is the formal durable documentation library for governance, implementation plans, product notes, startup summaries, and registered bilingual document pairs.
- `docs/superpowers/` is reserved for Superpowers runtime artifacts referenced by Comet state, such as design documents under `docs/superpowers/specs/` and implementation plans under `docs/superpowers/plans/`.
- Do not duplicate `docs_bilingual/` documents into `docs/`; only place Superpowers runtime artifacts under `docs/superpowers/` when the workflow explicitly records those paths.

## 3A. Post-Plan Local Governance Package

When a session exits `/plan` and the next task is not a documentation-only task, the first executable slice is a local governance package, not direct runtime or code implementation.

The governance package must start in `docs_bilingual/`:

- choose the most suitable existing `docs_bilingual/` directory and document class, such as governance, implementation plans, guides, memory, or product lifecycle notes;
- update an existing file first when a suitable file exists;
- create a new bilingual pair only when no suitable existing file can carry the decision;
- do not treat `implementation_plans/` as the only valid `docs_bilingual/` destination.

After the `docs_bilingual/` update is clear, derive any additional artifact needs from that content:

- update `openspec/` only when the task needs durable capability/spec lifecycle evidence, stable requirements, or a Comet/OpenSpec change;
- update `docs/` only when the task needs Superpowers runtime artifacts or a change to the `docs/` directory contract itself;
- never create `openspec/` or `docs/` files merely because a `docs_bilingual/` file was updated.

The package then follows the repository complete local commit flow through local `main` integration and stops at the remote publication gate. No GitLab push, GitLab MR mutation, or GitHub sync is authorized by this local package rule.

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

PMBOK8 Project Management Focus Areas mapping:

| Comet phase | PMBOK8 focus area | Repository interpretation |
| --- | --- | --- |
| Open | Initiating | Confirm why the change is worth doing, what success means, and which stakeholders or constraints matter before opening durable OpenSpec artifacts. |
| Design | Planning | Tailor the delivery approach, scope, risks, acceptance evidence, and Superpowers design or plan artifacts without treating planning as a one-time waterfall step. |
| Build | Executing | Coordinate implementation, TDD, review, and branch or worktree execution discipline. |
| Verify | Controlling | Compare results against requirements, validation evidence, risks, branch state, and acceptance expectations before allowing completion claims. |
| Archive | Closing | Close the change by syncing delta specs, preserving verification evidence, archiving history, and making the result discoverable for later work. |

Monitoring is a cross-cutting focus area, not a sixth Comet phase. It is implemented through phase detection, transition guards, evidence gates, verify-fail feedback, archive readiness checks, and explicit operator decisions. This keeps the PMBOK8 process guidance non-prescriptive: focus areas may recur, overlap, and be tailored across predictive, adaptive, and hybrid work, while the Comet state machine remains `Open -> Design -> Build -> Verify -> Archive`.

Runtime Monitoring is more than a passive check. If current work shows that an earlier focus area is incomplete, Comet may record a control decision and return the active change to `open`, `design`, `build`, or `verify` for rework. The return path must preserve the reason and iteration count so the workflow behaves like an adaptive or hybrid control loop rather than a one-way waterfall.

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
