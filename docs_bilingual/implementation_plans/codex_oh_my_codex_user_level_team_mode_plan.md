---
doc_id: codex_oh_my_codex_user_level_team_mode_plan
lang: en
canonical: docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.md
status: active
doc_class: implementation_plan
---

# Codex / oh-my-codex User-Level Team Mode Plan

## Bilingual Alignment Status

- Completeness baseline: this English ASCII file is the complete structural baseline for the plan.
- Chinese companion: `docs_bilingual/implementation_plans/codex_oh_my_codex_user_level_team_mode_plan.zh-CN.md`.
- Companion mode: the Chinese file is a structured companion, not an equal-length line-by-line translation; it must preserve the complete major-section index plus Chinese implementation semantics.
- Alignment rule: keep the Chinese companion structurally aligned to every major section and appendix in this file. When detailed wording diverges, use this English ASCII file as the implementation source of truth.
- Current finding: before the 2026-04-25 alignment pass, this file was materially more complete than the Chinese companion; the Chinese companion was a summary plus Appendix C excerpt.

## 1. Goal

This plan defines a reusable user-level durable team workflow for `Codex CLI + oh-my-codex`.

It should now be read as a shared implementation plan that combines:

- a user-level control surface reused by all `PyCharm / Codex CLI` projects on the same machine, user account, and Codex home
- a shared cross-project runtime layer for launchers, role catalogs, shared venvs, and generated helper mirrors
- a project-level contract that keeps repo-local source, repo-local durable state, repository OpenSpec artifacts, and repository validation inside each repository

This is therefore not a user-level-only launcher note. It is a shared operating model that coordinates user-level control with project-level source-of-truth boundaries.

The target is not a repository-specific setup for any one downstream application repository. The target is a reusable operating model for the current Windows user and the shared `C:\Users\lenovo\.codex` home.

"Usable by all Codex CLI projects" means:

- the same machine
- the same user account
- the same Codex home

It does not automatically cover:

- other Windows users
- other machines
- a separate WSL user profile

## 2. Scope

This plan covers:

- user-level team-mode operating strategy
- the shared user-level control surface reused across repositories on the same machine, user account, and Codex home
- native Codex as the permanent base layer
- oh-my-codex as an optional user-level enhancement controlled by a global on/off switch
- subagent routing as a separate control surface with `auto / manual / off`
- clear separation between persistent panes and leader-side native subagents
- automatic leader-side role selection by Codex CLI based on task phase and task signals, regardless of oh-my-codex state
- research-first, implementation-second handoff discipline
- a homogeneous-persistent-team default
- hybrid heterogeneous orchestration using expert native subagents plus homogeneous durable workers
- a practical project-phase model for normal development
- multi-worktree anti-conflict rules
- safe coexistence between native Codex and Codex + oh-my-codex on the same machine and user profile
- install-time versioned backup snapshots plus rollback-on-error behavior for user-level assets
- a native Windows operating path that does not depend on WSL2
- the installed user-level assets, current operator-facing control surfaces, and optional later extensions
- the project-level rule that repo-local source, repo-local durable state, repository OpenSpec artifacts, and repository tests remain the authority for each individual project
- the shared boundary between user-level assets under `C:\Users\lenovo\.codex\...` and repo-local truth under each repository tree

This plan does not cover:

- downstream application-runtime configuration
- replacing repository-level `AGENTS.md`, OpenSpec, repo-local source, or repo-local durable state with user-level state
- replacing or breaking the native Codex entrypoint
- making mixed persistent panes the default team shape
- a WSL2-based team-mode path
- patching oh-my-codex package internals

## 3. Inputs

This plan is grounded in four fully read source artifacts:

1. `long-running subagents/Effective harnesses for long-running agents _ Anthropic.html` - local source artifact for long-running agent harness and checkpointing guidance.
2. `long-running subagents/How To Be A World-Class Agentic Engineer.html` - local source artifact for agentic engineering methodology.
3. `long-running subagents/<WeChat Chinese long-form article snapshot>.html` - local Chinese source snapshot for the same long-running-agent methodology.
4. `oh-my-codex/Codex Multi-Subagent Support and Open-Source Multi-Agent Tooling.md` - local research note on Codex/OMX multi-agent tooling constraints.

Interpretation:

- The Anthropic article is the main source for long-running harness, checkpointing, handoff, and incremental progress discipline.
- The X post and the WeChat long-form article express the same methodology in English and Chinese forms.
- The dedicated Codex/OMX research note provides the product-surface constraints that the long-running articles do not provide on their own.
- Together they support the same operating direction:
  - treat Codex native subagents as an official native capability with explicit spawning, bounded fan-out, and leader-side fan-in
  - keep persistent roles narrow and strong
  - separate research from implementation
  - use specialist review as short-burst expert calls instead of default always-on panes
  - make handoff discipline more important than role count
  - define automatic role routing in this plan as an explicit leader-side routing policy, not as a claim that raw Codex auto-spawns subagents by default
  - treat OMX as a workflow and durable-state layer around Codex rather than as a Codex replacement
  - prefer `OpenHands` over older `OpenDevin` terminology
  - treat `LangGraph`, `AutoGen`, and `CrewAI` as general programmable orchestration runtimes, not as synonyms for native Codex subagents

## 4. Role Layering

### 4.1 Roles recommended for persistent panes

The default persistent-pane pool should stay as narrow and homogeneous as practical:

- `team-executor` - conservative persistent worker role for normal durable delivery.
- `executor` - more aggressive implementation worker role for clear execution paths.
- `debugger` - repair and stabilization worker role for regressions or runtime failures.

Recommended order:

1. `team-executor` - first-choice conservative worker role for persistent panes.
2. `executor` - second-choice implementation worker role when the path is clear.
3. `debugger` - fallback worker role when the task is mostly repair or stabilization.

Meaning:

- `team-executor` - persistent worker role for local implementation and verification handoff.
  - conservative worker for normal `omx team` delivery
  - good default for most approved implementation plans
- `executor`
  - more aggressive implementation worker
  - use when the implementation path is already clear
- `debugger` - repair role threshold for blocking failures, regressions, or reproducible runtime defects.
  - use for regressions, runtime repair, and stabilization

Persistent teams should stay same-type within one durable execution wave whenever possible.

### 4.2 Roles recommended as leader-side native subagents

These should default to leader-side native Codex subagents, not long-lived panes:

- `analyst` - requirements and ambiguity clarification specialist role.
- `architect` - system design and interface-boundary specialist role.
- `planner` - task sequencing and execution-slice specialist role.
- `researcher` - external documentation and version-sensitive fact specialist role.
- `verifier` - final acceptance and evidence validation specialist role.
- `test-engineer` - test strategy and regression-risk specialist role.
- `security-reviewer` - security, trust-boundary, and permission-review specialist role.
- `writer` - documentation, migration-note, and operator-guidance specialist role.

Reason:

- they are judgment-heavy roles
- they benefit from clean invocation boundaries and fresh context
- they should guide or validate execution instead of becoming idle always-on panes
- they should be treated as official native Codex subagents, not as simulated pane roles
- the current main Codex CLI session should keep final fan-in, routing, and output ownership

### 4.3 Specialized burst roles

These are also leader-side native subagents or prompt aliases:

- `bug-finder` - recall-oriented burst role for generating an intentionally overinclusive candidate-bug set.
  - purpose: generate an intentionally overinclusive candidate-bug set
  - input: target scope, change summary, relevant tests, and stated constraints
  - output: numbered bug claims with severity, evidence, repro hint, and confidence
  - default scoring: low-impact claim `+1`, medium-impact claim `+5`, severe claim `+10`
  - operating bias: optimize recall, not precision
- `bug-rebutter` - skepticism-oriented burst role for disproving weak bug claims from `bug-finder`.
  - purpose: disprove weak bug claims from `bug-finder`
  - input: the bug-finder report plus the same code and test scope
  - output: one rebuttal result per claim: disproved, unresolved, or likely valid, with evidence
  - default scoring: gain the claim's score for a successful disproof and lose double that score for a failed rebuttal
  - operating bias: optimize skeptical falsification, not broad enumeration
- `bug-judge` - arbitration burst role for choosing evidence-backed survivors from finder and rebutter reports.
  - purpose: arbitrate between finder and rebutter
  - input: both reports, code evidence, and any local test results
  - output: a final survivor list ordered by evidence strength and implementation priority
  - operating bias: keep only evidence-backed survivors and drop unsupported noise

These roles are not default team members.
They are short-burst review operators and should stay read-only by default.
Only judged survivors may be promoted into `debugger`, `executor`, or other execution lanes.

### 4.4 Practical rule for "heterogeneous teams"

If the user wants a staffing shape such as:

- `a x architect` - requested architect count in a heterogeneous staffing shape.
- `b x planner` - requested planner count in a heterogeneous staffing shape.
- `c x executor` - requested executor count in a heterogeneous staffing shape.
- `d x verifier` - requested verifier count in a heterogeneous staffing shape.

the default implementation is:

- `a x architect` as leader-side native subagents
- `b x planner` as leader-side native subagents
- `c x team-executor` or `c x executor` as the durable pane team
- `d x verifier` as leader-side native subagents

This satisfies heterogeneous staffing at the orchestration layer while keeping persistent panes mostly homogeneous.

Only if this hybrid model later proves insufficient should a true mixed-pane compose layer be added.

### 4.5 What a mixed persistent pane compose layer would mean

This is an optional future layer, not the default team shape.

Use it only when one or more expert roles must stay resident across many checkpoints and bursty leader-side invocation is no longer sufficient.

Definition:

- the leader remains the current main Codex CLI session and is not part of the pane roster
- a compose manifest declares role counts, pane names, worktrees, mailboxes, and ownership boundaries
- each persistent pane gets its own role prompt, pane identity, mailbox, and dedicated worktree
- one shared team state root stores the manifest, pane roster, mailbox routing, lifecycle state, and recovery metadata
- hotspot files still require explicit serialization rules

Example mixed-pane roster:

- `architect-1` - example architect pane identity in a mixed roster.
- `planner-1` - example planner pane identity in a mixed roster.
- `executor-1` - first example executor pane identity in a mixed roster.
- `executor-2` - second example executor pane identity in a mixed roster.
- `verifier-1` - example verifier pane identity in a mixed roster.

Even in this mode, expert panes should remain read-mostly unless the manifest explicitly grants them a write slice.

### 4.6 Role selection should be automatic at the leader layer

Default rule:

- the user describes the objective, constraints, and acceptance target
- Codex CLI in the leader lane decides which expert roles need to be invoked
- the leader should not require the user to manually spell out every expert role on every task
- this automatic selection is an explicit leader-side routing strategy layered over native Codex, not a claim that raw Codex spawns subagents automatically by default

This applies mainly to bursty expert roles such as:

- `analyst` - burst role for requirements and ambiguity clarification.
- `architect` - burst role for design and interface-boundary review.
- `planner` - burst role for sequencing and task-slice planning.
- `researcher` - burst role for external documentation and version-sensitive checks.
- `verifier` - leader-side role for final evidence and acceptance validation.
- `test-engineer` - leader-side role for test adequacy and regression-risk review.
- `security-reviewer` - leader-side role for security and trust-boundary review.
- `writer` - leader-side role for user-facing documentation and operator guidance.

Manual role forcing remains an optional override, not the default operating posture.

### 4.7 Automatic role-routing principles and thresholds

General principles:

- route the smallest sufficient role set, not the largest possible set
- automatic role routing is available in both native Codex and Codex + oh-my-codex states because native Codex already provides subagents
- oh-my-codex-enabled state adds durable team and pane orchestration; it does not create role routing from scratch
- if `subagent_routing=off`, do not auto-route or manually orchestrate specialist roles at all
- raw native Codex subagents remain explicit-spawn capabilities; the automation in this plan lives in the leader routing layer
- keep `agents.max_threads` and `agents.max_depth` under explicit operator control because fan-out increases token usage, latency, and local resource pressure
- prefer parallel fan-out for read-heavy or otherwise tightly bounded work
- allow write-heavy parallelism only when file or worktree ownership is explicit, hotspot serialization rules are defined, and final integration returns to the leader

Default thresholds:

- `analyst` - role threshold for unclear outcomes, non-goals, or acceptance targets.
  - invoke when the outcome, non-goals, or acceptance target is unclear
  - invoke when at least two major ambiguities remain
- `researcher` - role threshold for external docs, dependency behavior, version-sensitive facts, or official-source verification.
  - invoke when external docs, dependency behavior, version-sensitive facts, or official-source verification are needed
  - invoke whenever external uncertainty is above a low confidence threshold
- `architect` - role threshold for cross-module design, trust boundaries, or shared interfaces.
  - invoke when the change crosses two or more modules, trust boundaries, or shared interfaces
  - invoke for migrations, shared contracts, or non-local design decisions
- `planner` - role threshold for multi-slice work, ordering, and dependency planning.
  - invoke when the work can be split into two or more execution slices
  - invoke when there are serial hotspots, rollout ordering, or explicit dependency chains
- `team-executor` or `executor` - execution worker role threshold after the plan is frozen.
  - launch only after the plan is frozen
  - launch only when there are at least two mostly independent execution slices
- `debugger`
  - invoke when there is at least one blocking failure, regression, or reproducible runtime defect
  - prefer it when implementation has shifted into repair and stabilization
- `verifier` - final acceptance role threshold for behavior-changing or multi-file work.
  - invoke before final acceptance for any behavior-changing or multi-file work
  - always invoke after multi-worker integration
- `test-engineer` - test strategy role threshold for critical-path changes, missing tests, flakiness, or broad regression risk.
  - invoke when critical-path behavior changed, tests are missing, flaky, or broad regression risk exists
- `security-reviewer` - security role threshold for auth, secrets, permissions, untrusted input, code execution, trust boundaries, or payments.
  - invoke whenever the scope touches auth, secrets, permissions, untrusted input, code execution, external network trust boundaries, or payments
- `writer` - documentation role threshold for user-facing behavior, setup, migration, or operator workflow changes.
  - invoke when user-facing behavior, setup, migration, or operator workflow changed
- `bug-finder / bug-rebutter / bug-judge` - burst-review triad threshold for contested, noisy, or high-volume bug triage.
  - invoke when bug triage is contested, noisy, or high-volume
  - preferred threshold: after one normal verification pass still leaves disagreement or a broad candidate bug set

Routing state matrix:

- `oh_my_codex=on`, `subagent_routing=auto` - enhanced auto-routing state with oh-my-codex enabled.
  - full enhanced mode
  - automatic role routing is enabled
  - durable team and pane orchestration are available
- `oh_my_codex=off`, `subagent_routing=auto` - native routed state with oh-my-codex durable features disabled.
  - native routed mode
  - automatic role routing is enabled through native Codex subagents
  - no oh-my-codex durable team features
- `oh_my_codex=off`, `subagent_routing=off` - plain single-agent debugging state with routing disabled.
  - pure debugging mode
  - no role orchestration, no expert routing, no specialist role pool in use
  - any globally installed role definitions or orchestration assets are treated as inactive and unavailable in this mode
  - operate as a plain single-agent Codex session

## 5. `team-executor` vs `team-leader`

Do not rename the built-in `team-executor` to `team-leader`.

Why:

- `team-executor` is a worker role today
- the actual team leader should be the current main Codex CLI session
- renaming the worker would make the name conflict with real behavior

Correct direction:

- keep built-in `team-executor`
- define `team-leader` as the leader prompt/profile used by the current main Codex CLI session
- do not launch a separate leader worker pane

Suggested split:

- `team-leader` - leader prompt/profile bound to the current main Codex CLI session.
  - current main Codex CLI session
  - decomposition
  - ownership assignment
  - state monitoring
  - conflict handling
  - final integration
- `team-executor`
  - local implementation
  - local verification
  - evidence handoff back to leader

## 6. Recommended Project Phases

Instead of a coarse four-stage model, durable team usage works better with seven phases:

1. define the target
2. read the context
3. freeze the plan
4. execute in parallel
5. integrate and converge
6. stabilize
7. verify and accept

### 6.1 Define the target

Goal:

- final outcome
- non-goals
- completion standard

Primary role:

- `analyst` - primary role for defining target, non-goals, and completion standard.

No `omx team` yet.

### 6.2 Read the context

Goal:

- inspect code
- inspect dependencies
- inspect tests
- identify hotspot files
- find safe parallel boundaries

Primary roles:

- `researcher` - primary role for external and dependency context gathering.
- `architect` - primary role for design boundaries and hotspot identification.
- `planner` - primary role for safe parallel-boundary planning.

Still no `omx team`.

### 6.3 Freeze the plan

Goal:

- freeze task slicing
- freeze ownership
- freeze interface boundaries
- mark serial-only hotspot files

Primary roles:

- `planner` - primary role for freezing task slicing and ordering.
- `architect` - primary role for freezing interface and ownership boundaries.

Minimum output:

- task slices
- file or directory ownership
- integration order
- verification checklist
- an implementation brief that can be handed to a fresh execution context

After this freeze point, start implementation in a fresh context instead of reusing the open-ended research context.
The research role and the implementation role should be different roles.

### 6.4 Execute in parallel

This is the main `omx team` phase.

Default:

- small project: `2:team-executor`
- medium project: `3:team-executor`
- high-intensity implementation: `2:executor` or `3:executor`

At this point the leader should mainly:

- watch team status
- resolve scope edges
- correct ownership
- provide follow-up instructions

### 6.5 Integrate and converge

Goal:

- merge worker results
- resolve interface edges
- resolve shared config and routing conflicts

The team may still stay alive, but the leader often needs more serial control here.

### 6.6 Stabilize

When the center of gravity moves from feature work to regressions and failure repair, switch modes:

- `2:debugger` - durable-team staffing shorthand for two debugger workers.
- optionally call native `test-engineer`

### 6.7 Verify and accept

Do not let persistent execution panes own the final judgment.

Use leader-side native subagents:

- `verifier` - final sign-off role for evidence and acceptance checks.
- `test-engineer` - final sign-off role for test adequacy and regression risk.
- `security-reviewer` - final sign-off role for security and trust-boundary risk.
- `writer` - final sign-off role for documentation and operator guidance.

### 6.8 P0-P7 to seven-phase mapping

The P-series implementation batches and the seven-phase development flow are related, but they are not the same numbering system.

- `P0` through `P7`
  - platform-capability rollout batches for Codex / oh-my-codex user-level team mode
- seven development phases
  - runtime project phases used by the leader to decide which roles or teams should be active

Use this mapping:

| Batch | Core capability | Main phases served | Status |
|---|---|---|---|
| `P0` | user-level controls, backup, rollback, native Codex preservation | all phases | implemented |
| `P1` | startup binding, wrapped `codex`, `codex-native` bypass | all phases | implemented |
| `P2` | `omx team` entrypoints and durable-team operator surface | mainly phases 4, 5, and 6; partly 7 | implemented |
| `P3` | routing thresholds and inspectable leader-side routing policy | mainly phases 1, 2, 3, 6, and 7; also cross-phase | implemented |
| `P4` | adversarial burst-review roles: `bug-finder`, `bug-rebutter`, `bug-judge` | mainly phases 6 and 7 | implemented |
| `P5` | Codex CLI automatically decides when to start, reuse, switch, or stop `omx team` through a tracked repo-local helper surface | mainly phases 4, 5, and 6 | implemented |
| `P6` | native Windows durable-team backend so `omx team` can run without WSL2 or `tmux` | mainly phases 4, 5, and 6 | implemented |
| `P7` | startup leader-protocol binding and first-turn routing trace for every new wrapped Codex session | all phases, especially 1 through 4 | implemented |

Practical reading rule:

- `P0` and `P1` are the foundation
- `P2` makes `omx team` usable
- `P3` makes role routing explicit
- `P4` closes the contested bug-triage loop
- `P5` closes the automatic durable-team loop for `oh_my_codex=on` plus `subagent_routing=auto`
- `P6` completed the native Windows durable-team backend so real durable-team execution now works on native Windows without depending on WSL2 or a Unix `tmux` runtime
- `P7` now makes every new wrapped session behave like a leader-first routed session and emit a first-turn routing trace before deep execution

### 6.9 Release train overlay after P0-P7

The P0-P7 implementation batches are already implemented baseline work. Future work should use small release slices instead of reopening completed P batches or jumping into the full production draft.

Release-slice rule:

- one subrelease should normally map to one OpenSpec change and one GitLab MR
- every subrelease must state its target repository, phase, task scope, validation path, rollback path, and operator consent boundary
- runtime mutation remains disabled until a reviewed change and the operator explicitly authorize it
- the draft production durable-team plan remains north-star material until one reviewed release slice promotes a bounded part of it

Detailed release train:

#### R0.6 Durable Routing Smoke Gate

`R0.6 Durable Routing Smoke Gate` is the read-first gate for future automatic durable routing exercise.

- `R0.6.0 Gate Template` - template slice that defines the smoke/adoption gate document shape and required fields.
- `R0.6.1 Gate Field Checker And Codex Native Rollback Gate` - checker slice that fails a future gate change when required fields are missing and blocks production marking when native Codex or rollback evidence is missing.
- `R0.6.2 Read-Only State Sampling` - inspection slice that runs status-only durable-state sampling against one target repository.
- `R0.6.3 Dry-Run Routing Decision` - planning slice that explains the no-team, native_omx, or langgraph decision without applying it.
- `R0.6.4 Expected-Result Fixture` - fixture slice that captures expected dry-run decisions as regression evidence.
- `R0.6.5 Cross-Project Read-Only Review` - cross-project slice that proves consumer repositories do not inherit this repository's durable truth.

Default R0.6 boundary:

- dry-run or read-only inspection only
- no `omx-team-auto.ps1 -Apply`; `-Apply` is the helper switch that executes a planned durable action
- no `.omx/state/` writes; `.omx/state/` is the repo-local durable-state directory
- no `omx team` launch or shutdown; `omx team` is the durable worker-team runtime command

R0.6.1 Codex native rollback gate evidence:

- `codex --version` - local smoke command proving the native Codex entrypoint still launches.
- `codex-raw --version` - local smoke command proving the stable raw bypass remains available.
- `codex-ohmy --version` or `codex-ohmy --help` - local smoke command proving the wrapped launcher does not fail immediately.
- `test/install-codex-user-level-team-mode.test.ps1` - PowerShell regression test proving backup snapshot and rollback-on-error behavior in temporary directories.
- `tools/codex_native_rollback_release_gate_template.json` - JSON template that records required release evidence before production marking.
- `tools/check_codex_native_rollback_release_gate_template.py` - static checker that validates the template and source evidence without mutating user-level Codex assets.

#### R0.7 Native OMX Adoption MVP

`R0.7 Native OMX Adoption MVP` is the first controlled native_omx adoption lane for a low-risk worker-centric task.

- `R0.7.0 Low-Risk Target Selection` - selection slice that names one repository and one task safe enough for native_omx adoption.
- `R0.7.1 Native OMX Dry-Run Stability` - planning slice that proves native_omx selection is stable before apply mode.
- `R0.7.2 Explicit Apply Consent` - consent slice that records the exact operator approval required before `-Apply`.
- `R0.7.3 Lifecycle Record Check` - lifecycle slice that validates launch, reuse, shutdown, and tracked-record reporting.
- `R0.7.4 Restart Recovery Check` - recovery slice that confirms a cold-start session can inspect the native_omx state safely.
- `R0.7.5 Native OMX Closeout Archive` - closeout slice that archives evidence and leaves no unmanaged active team residue.

#### R0.8 LangGraph Adoption MVP

`R0.8 LangGraph Adoption MVP` is the first controlled langgraph adoption lane for a graph-shaped task.

- `R0.8.0 Graph-Shaped Task Selection` - selection slice that requires checkpoint, approval gate, frozen brief, survivor queue, or equivalent graph signal.
- `R0.8.1 Checkpoint Smoke` - checkpoint slice that proves state can be saved and resumed.
- `R0.8.2 Approval Gate Smoke` - approval slice that proves execution can pause for explicit operator decision.
- `R0.8.3 Frozen Brief Smoke` - handoff slice that proves research can be frozen into an implementation brief.
- `R0.8.4 Survivor Queue Smoke` - triage slice that proves reviewed bug survivors can become debugger-lane work.
- `R0.8.5 LangGraph Closeout Archive` - closeout slice that archives evidence without making langgraph the default for unrelated future tasks.

#### R0.9 Lane Arbitration

`R0.9 Lane Arbitration` is the decision layer for choosing native_omx, langgraph, or no durable team when multiple lanes are enabled.

- `R0.9.0 Lane Rule Fixture` - fixture slice that covers worker-centric, graph-shaped, verify-only, and stabilize phases.
- `R0.9.1 Legacy State Non-Activation` - safety slice that proves legacy selectors or thread IDs do not dominate unrelated future sessions.
- `R0.9.2 Scoped Activation Selector` - selector slice that binds durable activation to the current repository and current task flow.
- `R0.9.3 Operator Report` - reporting slice that always distinguishes installed, enabled, selected, and ready.
- `R0.9.4 Cross-Lane Conflict Regression` - regression slice that checks native_omx and langgraph conflict cases.

#### R1.0 Personal Durable Team MVP

`R1.0 Personal Durable Team MVP` is the first single-user, multi-project usable MVP.

- `R1.0.0 Cold-Start Summary Stability` - startup slice that proves a new session can recover required context from startup summaries.
- `R1.0.1 Single-Repository End-to-End` - end-to-end slice that runs one repository through plan, execute, verify, and archive.
- `R1.0.2 Worker Write-Set Isolation` - isolation slice that proves workers only edit their assigned paths.
- `R1.0.3 Leader Fan-In Discipline` - fan-in slice that keeps final integration and acceptance in the leader session.
- `R1.0.4 Failure Recovery` - recovery slice that handles stalled workers, failed workers, and stale local residue.
- `R1.0.5 Script-Backed Safety Closure` - safety slice that proves critical boundaries have checker or guard backing.

#### R1.1 Multi-Project Consumer Rollout

`R1.1 Multi-Project Consumer Rollout` extends the MVP to consumer repositories without sharing repo-local durable truth.

- `R1.1.0 First Consumer Read-Only Onboarding` - onboarding slice for the first legacy consumer repository selected by an explicit future change.
- `R1.1.1 CLIProxyAPI Read-Only Onboarding` - onboarding slice for `D:\PythonProject_CLIProxyAPI`, the CLIProxyAPI consumer repository.
- `R1.1.2 Unknown Project Onboarding` - onboarding slice for `D:\project`, the generic unknown-project directory.
- `R1.1.3 Browser Capability Preservation` - capability slice that keeps browser automation available for projects that need it.
- `R1.1.4 Repo-Local Truth Separation` - isolation slice that proves each project keeps separate OpenSpec, `.omx/state/`, CI, and publication truth.

#### R1.2 Operational Hardening

`R1.2 Operational Hardening` reduces noise, accidental configuration drift, and unsafe cleanup.

- `R1.2.0 Wrapper Error-Only Logging` - logging slice that keeps wrapper noise out of normal conversations.
- `R1.2.1 MCP Scope Regression` - MCP slice that keeps Codex-dedicated omx_* MCP tools direct and shared MCP Router tools separate.
- `R1.2.2 Config Rewrite Sentinel` - sentinel slice that detects unwanted edits to `config.toml`, the user-level Codex config file.
- `R1.2.3 Helper Mirror Verification` - mirror slice that proves user-level helper copies are install artifacts, not source of truth.
- `R1.2.4 Cleanup And Rollback Scripts` - cleanup slice that provides safe rollback and residue cleanup helpers.

#### R2.0 Production Durable Team

`R2.0 Production Durable Team` is the north-star production track, not current implementation.

- `R2.0.0 Production Readiness Standard` - readiness slice that freezes production acceptance criteria.
- `R2.0.1 Durable Memory Model` - memory slice that defines durable memory boundaries and retention rules.
- `R2.0.2 Crash Recovery` - recovery slice that proves interrupted work can be inspected and resumed safely.
- `R2.0.3 Graph-Native Orchestration` - graph slice that promotes graph-shaped orchestration only when it is warranted.
- `R2.0.4 Security And Secrets Boundary` - security slice that protects credentials, permissions, and untrusted inputs.
- `R2.0.5 Performance And Concurrency Test` - scale slice that tests worker count, provider pacing, and long-running stability.
- `R2.0.6 Operator Dashboard` - observability slice that gives the operator a clear status surface.
- `R2.0.7 Multi-Project Maintenance Strategy` - maintenance slice that defines long-term support across repositories.
- `R2.0.8 Production Release And Rollback` - release slice that marks production release only after rollback evidence exists.

## 7. Recommended Invocation Rhythm

### 7.1 Early stage

Recommended default order when the leader auto-router decides they are needed:

1. `analyst` - first early-stage role for clarifying target and acceptance.
2. `planner` - second early-stage role for sequencing and slice boundaries.
3. `architect` - third early-stage role for design and interface boundaries.
4. `researcher` when needed

### 7.2 Middle stage

Once the plan is frozen, choose one durable team size:

- prefer `omx-team-auto.ps1` in enhanced auto mode so launch, reuse, switch, and shutdown stay consistent
- start with `omx team 2:team-executor "..."`
- move to `omx team 3:team-executor "..."` only when the work cleanly splits into three lanes

Use `executor` only when you want a more aggressive implementation lane.

### 7.3 Late stage

If the work becomes mostly troubleshooting:

- `omx team 2:debugger "..."` - durable-team command shape for launching two debugger workers.

For final sign-off:

- native `verifier`
- native `test-engineer`
- native `security-reviewer` when necessary

### 7.4 Research-to-implementation handoff

Use this when the task starts with open-ended option space.

Required split:

- research lane: `analyst`, `architect`, `planner`, or `researcher`
- implementation lane: `executor` or `debugger`

Required handoff:

- research lanes produce a frozen implementation brief
- implementation starts in a fresh context after that brief exists
- the same role should not own both open-ended solution search and final implementation in the same lane

### 7.5 Hybrid heterogeneous orchestration

Use this when the user wants mixed staffing such as:

- `1 x architect` - heterogeneous staffing request for one architect.
- `1 x planner` - heterogeneous staffing request for one planner.
- `2 x executor` - heterogeneous staffing request for two executors.
- `1 x verifier` - heterogeneous staffing request for one verifier.

Recommended mapping:

- the expert counts run as leader-side native subagents
- the implementation count runs as one homogeneous persistent pane team
- the verifier count runs at checkpoints or sign-off instead of idling as default persistent panes

Selection rule:

- the leader-side Codex CLI decides when to invoke `architect`, `planner`, `verifier`, and other expert roles
- the user may constrain or forbid certain roles, but should not have to manually micromanage normal routing

This means the workflow can satisfy heterogeneous staffing without forcing mixed persistent panes.
If a future mixed-pane compose layer is used, the leader still stays outside the pane roster and continues to route work from the main Codex CLI session.

### 7.6 Adversarial bug review

Use this for review-heavy debugging or bug triage.

Preferred pattern:

- one native subagent enumerates possible bugs aggressively
- one native subagent tries to rebut or disprove each bug claim
- one native subagent judges both sides and keeps only evidence-backed survivors
- finder output becomes the rebutter input, and both outputs become the judge input
- finder, rebutter, and judge stay read-only unless the workflow explicitly promotes survivors into execution
- only judged survivors move into `debugger`, `executor`, or other execution lanes

### 7.7 Stable default posture

Default operating posture:

- persistent teams stay as homogeneous as practical
- expert roles stay bursty on the leader side
- durable team type changes only when the project phase changes

### 7.8 Restart matrix after routing or role changes

Treat "what changed" and "what must be restarted" as separate decisions.

Restart the main `codex` session only when the change affects leader-side routing or the decision layer:

- add a new leader-side subagent role under `C:\Users\lenovo\.codex\agents\`
- change routing thresholds, developer instructions, or role-selection rules
- change `team-leader.toml`
- change `codex-routing-policy.ps1`
- change the meaning of `subagent_routing=auto / manual / off`

Why:

- the main Codex CLI session loads a routing posture at startup
- current sessions do not hot-reload newly added roles or updated routing instructions

Restart the durable team or persistent panes only when the change affects existing workers rather than leader routing:

- change `executor.toml`, `team-executor.toml`, or `debugger.toml`
- add a new worker role that should join a durable team
- change durable team presets such as `2:team-executor`, `3:executor`, or `2:debugger`
- change worktree, mailbox, or worker-lifecycle behavior

Why:

- already-running workers keep using the prompt and team shape they started with
- worker lanes do not hot-reload role definitions safely

Restart both the main `codex` session and the durable team when the change affects both routing and worker execution:

- add a new role that must both appear in routing and participate in a durable team
- change both routing policy and worker prompts in the same rollout
- move the project into a new phase such as:
  - planning -> execute in parallel
  - execute in parallel -> stabilize
  - stabilize -> verify and accept
- fix suspected stale-routing or stale-worker-state issues

Practical rule:

- change the leader brain -> restart `codex`
- change the workers -> restart `omx team`
- change both -> restart both

## 8. Multi-Worktree Anti-Conflict Rules

`omx team` already supports dedicated worker worktrees, but conflict-free operation depends on discipline, not just flags.

### 8.1 One worker, one worktree, one branch

Required:

- each worker edits only its own worktree
- no two workers share the same mutable worktree
- each worker gets its own branch or detached worktree path

### 8.2 Freeze ownership before launch

Before team launch, define:

- which worker may touch which directory or files
- which shared files are serial-only
- which task depends on which prerequisite

### 8.3 Hotspot files must be serialized

Treat these as default hotspots:

- `package.json` - root package manifest and default hotspot file.
- lockfiles
- root config
- central routing registration
- shared core interface files
- main DB migration chain
- global style entrypoints

Do not let multiple workers edit these in parallel.

### 8.4 Prefer directory slices or vertical slices

Preferred:

- worker-1 owns `src/api/*`
- worker-2 owns `src/ui/*`
- worker-3 owns `tests/*`

Not preferred:

- multiple workers editing the same entrypoint
- multiple workers editing the same router or schema hub

### 8.5 Leader owns integration

Recommended rule:

- workers implement and self-verify locally
- the leader integrates final results
- workers do not directly merge each other

### 8.6 Local verification first, integrated verification second

Each worker should provide:

- a short change summary
- local proof for the touched area

Then the leader performs:

- post-integration verification
- full or critical-path validation

## 9. Reusable Team Templates

### 9.1 Default development team

Use for:

- most normal project work
- feature implementation
- conservative default delivery

Shape:

- leader: current main session
- workers: `2~3 x team-executor`

Recommended launch:

Choose one team size, not both:

```powershell
omx team 2:team-executor "implement approved plan for feature X"
omx team 3:team-executor "implement approved plan for feature X"
```

### 9.2 High-throughput implementation team

Use for:

- very clear implementation path
- speed-biased delivery

Shape:

- leader: current main session
- workers: `2~3 x executor`

Recommended launch:

```powershell
omx team 2:executor "implement feature X quickly with local verification"
```

### 9.3 Debug / stabilization team

Use for:

- regression cleanup
- flaky tests
- runtime failure diagnosis

Shape:

- leader: current main session
- workers: `1~2 x debugger`

Recommended launch:

```powershell
omx team 2:debugger "stabilize failing tests and regressions for feature X"
```

### 9.4 Hybrid heterogeneous orchestration

Use for:

- staffing shapes such as `1 x architect + 1 x planner + 2 x executor + 1 x verifier`
- projects that need expert bursts around one homogeneous execution swarm

Shape:

- leader: current main Codex CLI session
- native subagents: explicit expert counts
- persistent workers: homogeneous `2~3 x team-executor` or `2~3 x executor`

Recommended launch surface:

```powershell
omx-team-hybrid.ps1 -Architect 1 -Planner 1 -Executor 2 -Verifier 1 -Task "implement approved feature X rollout"
```

Execution rule:

- expert counts run as leader-side native subagents
- only implementation or stabilization workers stay persistent
- if the task later becomes regression-heavy, switch the durable team to `debugger`

Optional future extension:

- add a true mixed-pane compose layer only if the hybrid model proves insufficient in real usage

### 9.5 Optional mixed persistent pane compose layer

Use for:

- expert roles themselves must remain resident across long-running checkpoints
- the hybrid model has already proven insufficient in real usage

Shape:

- leader: current main Codex CLI session, outside the pane roster
- persistent panes: explicit mixed-role roster
- manifest: role roster, pane names, worktree paths, mailbox paths, ownership rules, hotspot serialization list, and checkpoint policy

Example roster:

- `architect-1` - example architect pane identity in the hybrid roster.
- `planner-1` - example planner pane identity in the hybrid roster.
- `executor-1` - first example executor pane identity in the hybrid roster.
- `executor-2` - second example executor pane identity in the hybrid roster.
- `verifier-1` - example verifier pane identity in the hybrid roster.

Operating rule:

- the leader never becomes a worker pane
- expert panes remain read-mostly unless the manifest explicitly grants write ownership
- default back to the hybrid model unless there is evidence that this heavier mode is necessary

## 10. Operator Control Surface, Shared User-Level Assets, and Project Boundaries

### 10.0 Shared user-level layer versus project-level layer

This plan only works cleanly across multiple `PyCharm / Codex CLI` projects when the following split stays explicit:

- user-level shared layer
  - launcher entrypoints
  - capability switches
  - shared role catalog
  - shared LangGraph venv
  - generated helper mirrors
  - cross-project operator control surface

- project-level layer
  - repo-local orchestration source
  - repo-local durable state under `.omx/state/...`
  - repository OpenSpec artifacts
  - repository tests, fixtures, and migration evidence
  - repository-specific exceptions and acceptance criteria

Shared user-level assets may coordinate and launch work across many repositories, but they must not become the canonical durable truth for any single repository.

### 10.1 Direct leader control commands

Global mode rule:

- native Codex remains permanently installed and available
- oh-my-codex is an optional user-level layer controlled by a global on/off switch
- subagent routing is controlled separately from the oh-my-codex switch
- regardless of the oh-my-codex switch, Codex CLI may still auto-route expert roles through native subagents when routing is enabled
- when oh-my-codex is globally disabled and routing remains enabled, startup stays in wrapped native-routed Codex mode rather than raw unwrapped Codex
- only when both oh-my-codex and `subagent_routing` are off does startup reduce to a plain single-agent native Codex session
- when oh-my-codex is globally enabled, startup enters Codex + oh-my-codex mode and adds team-mode features on top of native role routing

The current runtime then provides the main control surface directly:

- automatic durable-team helper: `omx-team-auto.ps1`
- native-subagent limit surface: `codex-subagent-limits.ps1`
- launch: `omx team 2:team-executor "<task>"`
- inspect live state: `omx team status <team-name>`
- wait for terminal progress: `omx team await <team-name>`
- reattach to a live team: `omx team resume <team-name>`
- clean shutdown after completion: `omx team shutdown <team-name>`

These commands should remain the primary operator surface even if user-level wrappers are added later.

All follow-up commands depend on the resolved `<team-name>`.
Record the team name shown at launch time.
If it is forgotten, rediscover it from `<repo>/.omx/state/team/` before issuing follow-up commands.

Important:

- `N:agent-type` selects the worker role prompt, not the worker CLI backend
- advanced mailbox or dispatch control lives under `omx team api ...`, not under the basic `status` flow

### 10.2 Runtime state, mailbox, and worktree notes

- team runtime state lives under `<repo>/.omx/state/team/<team-name>/`
- tracked automatic durable-team state lives under `<repo>/.omx/state/team/codex-auto-managed-team.json`
- leader ACK and mailbox flow is visible under `<repo>/.omx/state/team/<team-name>/mailbox/`
- task records, worker inbox files, and recovery state stay inside the same team state root
- managed native-subagent defaults live under `<codex-home>/state/native-subagent-limits.json`
- dedicated worktrees are created automatically by current `omx team`; do not standardize new wrappers around `--worktree`
- the `omx` CLI binary remains a shared user-level installation; project directories do not carry separate `omx` program copies
- multi-project isolation comes from separate per-repository `.omx` state roots, not from separate per-project installers or services
- different repositories or different git worktree directories therefore keep separate runtime state, mailbox state, logs, and recovery state by default
- two sessions inside the same repository intentionally see the same repository `.omx` state unless they are split into different worktree directories
- this plan does not require project-scoped global switches; only runtime execution state must be repository-scoped to avoid cross-project bleed

Advanced operator note:

- use `omx team api --help` to inspect mailbox and dispatch operations when basic leader commands are not enough
- start with safe read-oriented operations such as `list-tasks`, `mailbox-list`, `get-summary`, and `read-manifest`
- prefer CLI and state inspection over manual pane typing; do not treat direct pane input as the default control path

### 10.3 Current installed and optional later user-level assets

Installed now:

1. `C:\Users\lenovo\.codex\agents\team-leader.toml` - user-level native-agent TOML for the leader prompt/profile.
   - leader prompt/profile bound to the current main Codex CLI session
   - not a separate persistent worker pane
2. `C:\Users\lenovo\.codex\agents\bug-finder.toml`, `bug-rebutter.toml`, `bug-judge.toml` - user-level native-agent TOMLs for the burst-review triad.
   - leader-side burst-review roles
   - keep them read-only by default
3. `C:\Users\lenovo\.codex\docs\team-mode-playbook.md` - operator-facing team-mode playbook document.
   - operator-facing playbook for modes, routing, backends, lifecycle, and thresholds
4. `C:\Users\lenovo\.codex\state\user-level-team-mode.json` - user-level state file for layered capability switches.
   - persists `oh_my_codex`, `subagent_routing`, `langgraph`, and the compatibility backend view `durable_orchestration_backend`
   - this is already part of the current implemented layered capability model rather than a placeholder for later work
5. `C:\Users\lenovo\.codex\state\native-subagent-limits.json` - user-level state file for managed native subagent limits.
   - persists managed defaults for `agents.max_threads` and `agents.max_depth`
6. `C:\Users\lenovo\.codex\bin\codex-omx-on.ps1`, `codex-omx-off.ps1`, `codex-omx-status.ps1` - user-level scripts for toggling or inspecting oh-my-codex state.
   - toggle or inspect the global oh-my-codex state
7. `C:\Users\lenovo\.codex\bin\codex-subagents-auto.ps1`, `codex-subagents-manual.ps1`, `codex-subagents-off.ps1` - user-level scripts for controlling automatic expert routing posture.
   - control automatic expert routing posture
8. `C:\Users\lenovo\.codex\bin\codex-routing-status.ps1`, `codex-routing-policy.ps1` - user-level scripts for inspecting routing status and policy.
   - inspect current routing posture, startup semantics, thresholds, and durable-team policy
9. `C:\Users\lenovo\.codex\bin\codex-subagent-limits.ps1` - user-level script for inspecting or updating native subagent limits.
   - inspects, and where supported updates, managed defaults for `agents.max_threads` and `agents.max_depth`
10. `C:\Users\lenovo\.codex\bin\codex-durable-backend-status.ps1`, `codex-durable-backend-native-omx.ps1`, `codex-durable-backend-langgraph.ps1` - user-level scripts for inspecting or switching durable backend selection.
    - inspect or switch the selected durable orchestration backend
11. `C:\Users\lenovo\.codex\bin\omx-team-dev.ps1`, `omx-team-debug.ps1`, `omx-team-verify.ps1`, `omx-team-ops.ps1`, `omx-team-auto.ps1`, `omx-team-hybrid.ps1` - user-level durable-team launcher scripts for common staffing modes.
    - durable-team entrypoints, operations, automatic routing helper, and hybrid staffing helper
12. `C:\Users\lenovo\.codex\bin\omx-langgraph-run.ps1`, `omx-langgraph-status.ps1`, `omx-langgraph-resume.ps1`, `omx-langgraph-inspect.ps1` - user-level LangGraph durable-thread control scripts.
    - LangGraph durable-thread control and inspection surfaces
13. `C:\Users\lenovo\.codex\backups\codex-user-level-team-mode\` - backup directory for generated user-level team-mode assets.
    - stores timestamped pre-change snapshots for generated user-level assets
    - exists to support install-time rollback and later operator inspection

Optional later extensions:

14. optionally a small user-level `AGENTS.md` addition for team operating rules
15. optionally, later, `C:\Users\lenovo\.codex\bin\omx-team-compose.ps1`
    - only if real usage proves that mixed persistent panes are necessary
    - should read a compose manifest instead of relying on ad hoc pane creation
16. optionally, later, `C:\Users\lenovo\.codex\teams\compose-manifest.schema.json`
    - defines pane roster, role types, worktrees, mailbox routing, ownership boundaries, and checkpoint policy

These should be user-level assets, not repository-specific assets.

Complementary location rule:

- keep cross-repository reusable role TOMLs under `C:\Users\lenovo\.codex\agents\`
- keep repository-specific role TOMLs under `<repo>/.codex/agents/`
- every standalone custom agent TOML should define `name`, `description`, and `developer_instructions`
- pin `model`, `reasoning_effort`, `sandbox_mode`, MCP servers, or similar settings only when the role really needs fixed behavior

### 10.4 Install safety, backup, and rollback

Required install rule:

- create a timestamped snapshot before writing any generated team-mode asset
- keep snapshots under a namespaced backup root inside `C:\Users\lenovo\.codex`
- if installation fails after writes begin, restore every targeted managed path immediately
- remove newly created managed files that did not exist before the failed install
- keep backup metadata after rollback so the operator can inspect what happened
- do not include native `codex`, `codex.cmd`, or `codex.ps1` in the generated write set or rollback set

## 11. Windows Preconditions

oh-my-codex explicitly says team mode works best on macOS/Linux with `tmux`.
This plan does not standardize on that path.
This plan standardizes on native Windows only.

Current observed reality after P6:

- WSL2 remains out of scope for this workflow
- native subagent routing works on Windows
- the automatic durable-team helper works at both the planning and apply layers
- real `omx team` execution now works on native Windows without WSL2
- worker runtime sidefiles are isolated away from worker worktrees through a dedicated runtime root instead of leaking local `.omx` session artifacts into worker cwd paths
- the earlier `psmux` placeholder assumption is no longer needed as the execution baseline

Native Windows preflight today:

```powershell
omx team --help
git rev-parse --is-inside-work-tree
```

Expected current result:

- planning and policy surfaces work
- actual durable-team execution is available through the native Windows backend

### 11.1 P6 Windows Native Backend Direction

`P6` should now be treated as a completed platform batch.

Its purpose was not to replace P5. Its purpose was to provide the missing runtime backend so the already-implemented P5 routing layer could actually execute durable teams on native Windows.

Recommended direction:

- add a backend abstraction under `omx team`
- keep `tmux` as the Unix backend
- add a native Windows backend instead of requiring WSL2
- prefer a controlled Windows process backend before attempting pane-automation tricks
- keep `.omx/state/team/...`, mailbox, worktree, heartbeat, status, await, resume, shutdown, and API semantics stable across backends

P6 success criteria:

- `omx team 2:team-executor "<task>"` runs on native Windows without WSL2
- `omx team status / await / resume / shutdown` work on native Windows
- `omx-team-auto.ps1 -Apply` can really launch, reuse, switch, and shut down tracked durable teams on native Windows
- worker session, hook, and notify sidefiles no longer have to land in worker worktrees
- native `codex` and `codex-native` remain unaffected

### 11.2 P7 Startup Leader Protocol Status

P7 is now implemented in the wrapped startup path.

Current observed behavior:

- new wrapped Codex sessions receive dynamic `developer_instructions`
- `C:\Users\lenovo\.codex\agents\team-leader.toml` exists as an installed user-level asset and formalizes the current main Codex CLI session as leader
- on the first substantive turn of a new wrapped session, and again on every session reload or Codex restart, the wrapped session performs an orchestration activation check:
  - classify the task phase
  - decide whether expert native subagents are needed now
  - decide whether durable-team thresholds are already met
  - emit a short routing trace that explains the decision
- during an active session, the same activation check should run again when:
  - the task phase changes
  - the work expands from one slice to two or more execution slices
  - tracked `.omx` durable state is detected
  - the user explicitly requests `omx`, `LangGraph`, resume, continue, or parallel execution
- startup does not auto-launch a durable team; it classifies first and explains why `omx team` was or was not selected
- automatic durable-team routing remains threshold-gated and repository-scoped through the tracked record at `.omx/state/team/codex-auto-managed-team.json`

Current P7 outcome:

- every new wrapped Codex session starts in a stable leader-first routing posture
- the session can proactively choose leader-side expert roles when the task shape clearly requires them
- the session can explicitly decide that `omx team` is not yet appropriate for early or acceptance phases
- when `omx team` is not selected, the session explains which threshold was not met
- when `omx team` is selected later in the session, the session can point to the exact threshold that triggered it
- the operator can inspect a first-turn routing trace instead of guessing whether routing happened

Optional later refinement:

- keep tightening the user-level routing policy and playbook surfaces so they remain aligned with real startup behavior after later capability changes

## 12. Global Usage Rules

### 12.0 Shared Provider Budget

Wrapped Codex sessions, leader-side native subagents, and durable-team workers do not have an unlimited shared provider budget.

Current runtime rule:

- the provider proxy is the single upstream egress path
- at most 10 true upstream provider forwards are allowed per rolling 1 minute
- overflow requests are delayed locally until a slot is available
- the local layer does not use this rule to mirror an immediate local 429 by default
- this pacing rule is backpressure, not a reason to disable or avoid `LangGraph`, `native_omx`, or native subagents by itself

Practical effect:

- early-stage exploration should prefer local context and bounded reads before spending provider budget
- durable-team concurrency does not imply unlimited upstream fanout
- multiple repositories and sessions still share the same upstream provider pacing budget while they target the same local provider proxy

### 12.1 When not to use `omx team`

Prefer native subagents when:

- requirements are still unclear
- the plan is not frozen
- the task is only exploration
- the task is only documentation research
- the task is only final acceptance judgment

### 12.2 When to start `omx team`

Launch only when:

- the outcome is clear
- ownership is frozen
- the work can be split into at least two mostly independent execution slices
- the task benefits from durable cross-context execution

### 12.3 When to switch team type

Recommended switching rule:

- feature work: `team-executor` or `executor`
- repeated failure cleanup: `debugger`
- final judgment: stop team mode and switch to `verifier` / `test-engineer`

### 12.4 Native Codex base-layer and global-switch rule

This workflow must preserve:

- native Codex as the permanent base layer
- Codex + oh-my-codex as an optional user-level enhancement controlled by a global switch

Required rule:

- development or configuration work for oh-my-codex must not leave native Codex unusable
- prefer additive user-level assets such as separate agent files, wrapper scripts, and playbooks
- do not replace the native `codex` executable, force a hard alias over it, or require native Codex users to enter team mode paths
- describe oh-my-codex as a workflow and durable-state layer around Codex, not as a replacement for Codex
- keep native subagents and durable teams as distinct layers: bounded in-session delegation vs long-running execution and recovery
- support an explicit global on/off switch for oh-my-codex
- support a separate explicit control surface for `subagent_routing`
- in PowerShell environments that load the user profile, including a normal PyCharm PowerShell terminal, typing `codex` should enter the installed user-level launcher rather than directly invoking raw `codex.cmd`
- that launcher should read the global `oh_my_codex` and `subagent_routing` state, then forward into native `codex.cmd` with the correct mode-specific settings
- `codex-native` must remain the explicit bypass path that directly invokes native Codex without the user-level launcher behavior
- `codex.openclaw` remains the explicit non-profile wrapped launcher path
- `codex-ohmy` is the preferred stable user-level wrapped command for multi-project daily use when `.venv` or shell startup behavior may shadow plain `codex`
- `codex-raw` is the preferred stable user-level native bypass command for multi-project daily use when `.venv` or shell startup behavior may shadow `codex-native`
- in CLM-sensitive or `.venv`-heavy environments, stable user-level command names should be treated as the primary operator workflow
- when omx is globally disabled and routing is `auto` or `manual`, startup must stay in wrapped native Codex mode with the corresponding routing posture
- only when omx is globally disabled and routing is `off` should startup become a plain single-agent native Codex session
- when omx is globally enabled, startup must enter Codex + oh-my-codex mode
- `oh_my_codex=off` with `subagent_routing=auto` means wrapped native-routed startup, not raw unwrapped startup and not omx-enhanced startup
- `oh_my_codex=on` changes the startup mode and omx-related capability flags, but it must not imply automatic durable-team launch on every `codex` start
- prefer `OpenHands` over archived `OpenDevin` terminology in documentation and operator guidance
- treat `LangGraph`, `AutoGen`, and `CrewAI` as general programmable orchestration runtimes rather than as native Codex-subagent equivalents
- every installer run that mutates user-level assets must create a backup snapshot first and roll back partial failures automatically
- if a change risks breaking plain native Codex startup, treat that change as out of bounds for this plan

### 12.5 Research and implementation must be different roles

Required rule:

- use `analyst`, `architect`, `planner`, or `researcher` for open-ended research and decision work
- use `executor` or `debugger` for final implementation or repair work
- do not let one role own both phases in the same lane when the task started open-ended

### 12.6 Persistent teams should stay homogeneous by default

Required rule:

- prefer `N:team-executor`, `N:executor`, or `N:debugger` for durable panes
- do not turn every expert role into an always-on pane by default
- add mixed persistent panes only if homogeneous durable lanes plus leader-side native subagents prove insufficient

### 12.7 Heterogeneous staffing is satisfied at the orchestration layer

Required rule:

- support staffing expressions such as `a x architect + b x planner + c x executor + d x verifier`
- default mapping is `architect / planner / verifier` as leader-side native subagents and `executor / debugger` as durable panes
- do not pretend every requested count must map to a persistent pane

### 12.8 Adversarial review is a native subagent workflow

Required rule:

- keep bug-finder, rebutter, and judge logic as short-burst native subagents or prompt aliases
- do not keep them as default persistent panes
- send only judged survivors into persistent execution lanes

### 12.9 `team-leader` is the current main Codex CLI session

Required rule:

- `team-leader` means the current main Codex CLI session
- `team-leader.toml` is a leader prompt/profile for that main session
- do not spin up an extra leader worker pane
- worker panes remain workers

### 12.10 Codex CLI should choose expert roles by default

Required rule:

- by default, the user specifies the task, constraints, and desired outcome
- the leader-side Codex CLI decides which expert native subagents to invoke and when
- manual expert-role selection is an override for special cases, not the standard path
- automatic selection must not violate the other rules in this plan, especially homogeneous persistent teams and separate research vs implementation roles

### 12.11 Subagent routing is independent from oh-my-codex

Required rule:

- `oh_my_codex` and `subagent_routing` are separate controls
- turning off oh-my-codex does not by itself turn off native Codex subagents
- turning off subagent routing disables role orchestration even if native Codex is still available

### 12.12 Automatic role routing exists in both native and omx-enabled states

Required rule:

- Codex CLI may auto-route expert roles in both native Codex and Codex + oh-my-codex states
- when oh-my-codex is globally disabled and routing is `auto`, only native subagent routing is assumed
- when oh-my-codex is globally enabled and routing is `auto`, native subagent routing remains available and oh-my-codex durable-team features are added
- when `subagent_routing=off`, role orchestration should be treated as unavailable
- both the global oh-my-codex state and the routing state should be explicit and operator-visible

### 12.13 Orchestration activation MUST be re-checked beyond first-turn startup

Required rule:

- do not limit orchestration activation to the first substantive turn of a new wrapped session
- re-run orchestration activation checks on every session reload
- re-run orchestration activation checks on every `codex` restart
- re-run orchestration activation checks when the task phase changes
- re-run orchestration activation checks when work expands from one slice to two or more execution slices
- re-run orchestration activation checks when tracked repo-local `.omx` durable state is detected
- re-run orchestration activation checks when the user explicitly requests `omx`, `LangGraph`, resume, continue, or parallel execution

### 12.14 Explicit user requests to use `omx` or `LangGraph` are hard routing directives

Required rule:

- an explicit user request to use `omx` or `LangGraph` is a hard routing directive, not a soft preference
- when such a directive is given, Codex CLI should actually adopt the corresponding orchestration path unless a concrete blocker exists
- do not respond with explanation-only behavior when the activation threshold is met and no blocker exists
- if orchestration is not adopted, explain the concrete blocker instead of silently continuing in burst-only mode

### 12.15 Existing projects and existing sessions MUST remain retrofit-capable

Required rule:

- existing projects with new sessions should automatically follow the current user-level orchestration policy
- existing live sessions should retrofit orchestration behavior on reload, restart, explicit user routing directive, or tracked durable-state detection
- the activation target is the current task flow, not whether the repository was newly created
- choose `native_omx` or `langgraph` based on the current task-flow characteristics rather than on project age

### 12.16 Pure debugging mode disables role orchestration

Required rule:

- `oh_my_codex=off` and `subagent_routing=off` defines pure debugging mode
- in this mode, do not auto-call roles
- in this mode, do not rely on specialist role orchestration
- in this mode, treat any globally installed role definitions, prompt aliases, or orchestration assets as inactive and unavailable
- treat the session as a plain single-agent Codex session

### 12.17 Mixed persistent pane compose is an opt-in advanced mode

Required rule:

- mixed persistent pane compose is not the default
- use it only after the hybrid model has proven insufficient
- keep the leader outside the pane roster even in mixed-pane mode
- require an explicit compose manifest before launching mixed persistent panes

### 12.18 Backup first, rollback on error

Required rule:

- before mutating any user-level Codex team-mode asset, create a timestamped backup snapshot
- if the install or update fails after writes begin, restore the pre-install managed state immediately
- keep the backup snapshot metadata after rollback for diagnosis and manual recovery
- treat missing backup-and-rollback coverage as a release blocker for user-level installers

### 12.19 Script-control plus prompt-reminder safety rule

Safety boundaries for `experts / durable_team / persistent team` must not rely on prompt memory alone.

For every system-level, user-level, or project-level rule that can cause data loss, cross-project state leakage, unwanted durable activation, or unsafe publication, the required control pattern is:

- script control - executable checks or guarded helper logic that fail closed even when a new cold-start model has no prior conversation context.
- prompt reminder - startup-summary and plan text that tells the model what the script is protecting and what recovery step to take when the reminder appears forgotten.

This means:

- high-risk state transitions must be encoded in scripts, tests, guards, or generated helper logic before they are treated as implemented behavior.
- prompt-only reminders may describe the desired operator behavior, but they do not count as enforcement.
- a cold-start model following only the repository read order and the documented commands must not be able to accidentally merge project-local durable truth across repositories, auto-adopt stale selectors, or launch a durable team before the routing thresholds are met.
- future changes that add or alter safety boundaries must include either a checker, a fixture, a guarded script path, or an explicit reason why no executable control is possible yet.

This implementation slice promotes the prompt-only safety warning into a user-level safety-rule registry and aggregate checker:

- `tools/check_safety_rule_script_backing.py` - repository source for the aggregate checker that verifies every registered safety rule has a script control, a prompt reminder, and guard linkage or an explicit tracked gap.
- `tools/safety_rule_script_backing_registry.json` - repository registry that lists each registered safety rule, owner layer, prompt reminder location, executable control, guard step, and implementation status.
- `codex-safety-rule-script-backing.ps1` - future optional user-level mirrored helper that can run the aggregate checker from a consumer project without making user-level state the source of truth.

The checker is user-level because it must protect shared Codex / OMX / LangGraph behavior across projects. General prompt reminder text remains project-level because each repository owns its own `AGENTS.md`, startup summary, durable truth, and recovery read order. The context-retention canary prompt is narrower: its literal prompt text must live only in `docs_bilingual/project_startup_summary.md` and `docs_bilingual/project_startup_summary.zh-CN.md`.

Startup summaries should also carry a lightweight context-retention canary. Other active instruction surfaces, including `AGENTS.md`, user-level startup summaries, implementation plans, generated wrappers, and launcher payloads, may point to the startup-summary canary source but must not duplicate its literal start/end phrase.

The canary convention is:

- startup summaries define the literal prompt for complete assistant responses in this orchestration repository, unless a higher-priority system or developer instruction prevents it.
- if the canary is missing from a complete response after the startup summary was supposed to be read, treat that as possible context-loss evidence.
- the recovery action is to re-enter cold-start mode: reread `AGENTS.md`, reread the `docs_bilingual/project_startup_summary.*` pair, follow the startup-summary read order, and then reread only the files required to continue the current task.

The future user-level canary checker should not inject the canary prompt into wrapper payloads. It should only verify, when a transcript or response text is provided, whether the response satisfies the startup-summary-defined canary; if not, it should report a cold-start recovery instruction to reread `AGENTS.md` and `docs_bilingual/project_startup_summary.*`.

## 13. Implementation Order

When this plan is later executed, the order should be:

1. define and validate the native Windows durable-team backend contract for `omx team`
2. replace that placeholder assumption with a real native Windows durable-team backend for `omx team`
3. validate launch, status, await, resume, and shutdown on native Windows without WSL2
4. keep install-time backup snapshots and rollback-on-error behavior for user-level assets
5. keep explicit global on/off controls for oh-my-codex
6. keep explicit controls for `subagent_routing`
7. validate `omx-team-auto.ps1 -Apply` against the Windows backend in one test repository
8. keep user-level `team-leader.toml`, routing policy, and playbook aligned with backend capability
9. verify that native Codex still launches and works after the oh-my-codex user-level additions
10. verify that the supported operating path remains native Windows, does not require WSL2, and no longer assumes a Unix `tmux` runtime or the earlier `psmux` placeholder
11. verify that the global oh-my-codex switch cleanly changes startup behavior
12. verify that routing mode cleanly switches between `auto`, `manual`, and `off`
13. validate research-to-implementation handoff, adversarial review flow, and automatic role routing thresholds in one test repository
14. validate hybrid staffing counts in one test repository
15. validate the same workflow in two different repositories
16. whenever one behavior change touches both repository source logic and generated user-level mirrors, update repository source and repository tests first, then regenerate and validate the user-level mirrors
17. before any live durable-routing smoke or adoption gate, define Release 0.6 fields: `target_repository`, `phase`, `task`, and `operator_consent_boundary`
18. keep Release 0.6 read-only by default until the operator explicitly permits `-Apply` or another mutating action
19. use a separate reviewed OpenSpec change for any controlled `native_omx` or `langgraph` adoption exercise
20. keep the production durable-team draft out of active implementation until a specific release slice is reviewed and accepted

## 14. Acceptance Criteria

Once implemented, the user-level solution should satisfy:

1. same team entrypoints work from arbitrary project directories
2. workers land in dedicated worktrees
3. leader can reliably use `status / await / resume / shutdown`
4. no dependency on downstream application-specific repository scripts
5. default team types and phase transitions are clear
6. multi-worker execution does not constantly fight over hotspot files
7. mailbox, task state, and recovery surfaces are documented and directly operable from the leader session
8. leader can rediscover the active team name and continue normal control flow without relying on manual pane typing
9. native Codex remains usable after oh-my-codex setup or development changes, and the user can switch the global oh-my-codex state without repair work
10. the supported operating path remains native Windows, does not require WSL2, and no longer assumes a Unix `tmux` runtime or the earlier `psmux` placeholder
11. open-ended research can be separated from execution and handed to a fresh implementation context
12. adversarial bug review works as short-burst native subagents without forcing persistent panes
13. staffing expressions such as `a x architect + b x planner + c x executor + d x verifier` can be satisfied without requiring every role to be a persistent pane
14. persistent teams remain mostly homogeneous by default
15. research and implementation are assigned to different roles when the task starts with open-ended option space
16. the leader-side Codex CLI can automatically choose which expert roles to invoke without requiring the user to micromanage role routing on normal tasks
17. `team-leader` is implemented as the current main Codex CLI session rather than as a separate persistent worker pane
18. if mixed persistent panes are later enabled, they are manifest-driven and explicitly treated as an advanced opt-in mode
19. omx-disabled startup uses wrapped native Codex when routing remains enabled, while omx-enabled startup enters Codex + oh-my-codex mode
20. automatic role routing follows the documented principles and thresholds in both native Codex and omx-enabled states
21. `subagent_routing=off` disables role orchestration and yields a plain single-agent Codex session
22. every mutating install creates a timestamped backup snapshot and automatically restores pre-install managed state if the install fails after writes begin
23. every new wrapped Codex session enters a stable leader-first routing posture instead of relying on a weak startup hint
24. on first turn, the session can explain why it did or did not invoke expert subagents or `omx team`
25. reusable role TOMLs can live under `C:\Users\lenovo\.codex\agents\` while repository-specific role TOMLs can live under `<repo>/.codex/agents/`
26. every standalone custom agent TOML used by the workflow satisfies the minimum schema of `name`, `description`, and `developer_instructions`
27. the operator can inspect or manage `agents.max_threads` and `agents.max_depth`, and write-heavy parallelism remains gated by explicit ownership isolation and leader-owned integration
28. when `langgraph` is selected, it remains an additive durable orchestration backend under Codex / oh-my-codex rather than replacing the current workflow
29. LangGraph runtime state can remain repo-local under `.omx/state/langgraph/`
30. research-to-implementation handoff can persist a frozen implementation brief and restart execution in a fresh context
31. adversarial bug review can persist a survivor queue without turning the bug triad into default persistent workers
32. many `PyCharm / Codex CLI` projects on the same machine can reuse the same user-level control surface without merging their canonical durable state into one shared pool
33. repo-local orchestration source and repo-local durable state remain the project-level authority even when user-level mirrors are installed
34. user-level mirrors and repository source contracts stay semantically aligned after rollout

## 15. Final Recommendation

Stable default:

- native base: always present
- omx switch: explicit global on/off state
- routing switch: explicit `auto / manual / off`
- leader: current main Codex CLI session, formalized by a user-level `team-leader` prompt/profile
- default durable worker: `team-executor`
- aggressive implementation worker: `executor`
- debug worker: `debugger`
- expert roles: leader-side native subagents chosen on demand by the leader-side Codex CLI in both native and omx-enabled states
- hybrid staffing: expert subagents plus one homogeneous durable execution team

Current implemented selection model:

- `subagent_routing`, `oh_my_codex`, and `langgraph` are the current user-level capability switches
- enabled capability layers are distinct from the per-task effective lane
- `durable_orchestration_backend` remains as a compatibility and operator-facing backend view derived from the layered state
- when the relevant layers are enabled, Codex CLI can choose the per-task effective lane among native subagents, `native_omx`, and `langgraph`
- when both durable capabilities are enabled, worker-centric flows default to `native_omx`, while graph-shaped flows default to `langgraph`

Recommended operating presets:

- enhanced mode: `oh_my_codex=on`, `subagent_routing=auto`
- native routed mode: `oh_my_codex=off`, `subagent_routing=auto`
- pure debugging mode: `oh_my_codex=off`, `subagent_routing=off`

The main optimization target is not "more roles". The main optimization target is:

- keep native Codex permanently available
- enable or disable oh-my-codex explicitly through a global switch
- control role routing explicitly through `subagent_routing`
- expose stable user-level command names that remain usable across repositories even when project `.venv` environments shadow plain `codex`
- add LangGraph only as an additive durable orchestration backend, not as a replacement for Codex or oh-my-codex
- freeze ownership first
- finish research before implementation starts
- keep durable workers inside their own worktrees
- let Codex CLI choose leader-side experts as bursty decision and review tools in both native and omx-enabled states
- let the leader own final integration and acceptance

## 16. LangGraph Direction

LangGraph is now an available additive durable orchestration backend under Codex / oh-my-codex. It is not the stable default backend family, but it is installed at user level and can be selected through the backend control surfaces.

Current shape:

- keep `Codex CLI` as leader and final integrator
- keep oh-my-codex as the user-level control and workflow layer
- add LangGraph under that layer as an optional durable orchestration backend
- use a Python sidecar and a seven-phase root graph
- keep repo-local runtime state under `.omx/state/langgraph/`

Recommended use:

- prefer LangGraph for graph-shaped multi-phase execution
- prefer LangGraph for checkpoint-driven recovery and interrupt/resume approval gates
- prefer LangGraph when a frozen implementation brief and persisted survivor queue are first-class durable artifacts
- do not treat LangGraph as a replacement for native Codex or oh-my-codex

Research handoff:

- persist a frozen implementation brief
- start implementation in a fresh execution context after the brief exists
- do not make the research roles themselves the default persistent workers

Adversarial review:

- keep `bug-finder / bug-rebutter / bug-judge` bursty by default
- persist only the judged survivor queue plus downstream repair ownership
- let a durable debugger lane consume that survivor queue when repair spans checkpoints

### 16.1 LangGraph Terms

`graph phase`

- a durable workflow stage with a clear goal, allowed actions, inputs, outputs, and entry or exit conditions
- in this plan the root phases are: `define-target`, `read-context`, `freeze-plan`, `execute-parallel`, `integrate-converge`, `stabilize`, and `verify-accept`
- its purpose is to make progress inspectable and recoverable as a state machine rather than as chat memory

`checkpoint gate`

- a controlled boundary where the workflow can safely persist state, stop, and resume later
- it is not just a log point; it is a durable pause or approval gate
- in the current LangGraph direction, typical gates include `freeze-plan`, `stabilize-risk-review`, and `verify-accept-failed`

`frozen implementation brief`

- a structured handoff artifact created after research but before implementation begins
- it should capture at least: `objective`, `non_goals`, `accepted_decisions`, `constraints`, `interfaces`, `ownership_boundaries`, `acceptance_criteria`, and `validation_plan`
- its purpose is to end open-ended research cleanly and let implementation start from a fresh execution context

`survivor queue`

- the persisted queue of bug or repair items that remain after adversarial review and judge arbitration
- it should persist judged survivors rather than every candidate report
- typical fields include: `bug_id`, `title`, `severity`, `evidence`, `judge_verdict`, `owner_lane`, `status`, and `verification_result`
- its purpose is to let debugger or repair lanes continue work across checkpoints without re-triaging from scratch

## 17. Backend Selection

Recommended durable backend policy:

- keep `native_omx` as the stable default durable backend
- keep the actual selected backend as explicit operator state in `C:\Users\lenovo\.codex\state\user-level-team-mode.json`
- inspect or switch backend family through `codex-durable-backend-status.ps1`, `codex-durable-backend-native-omx.ps1`, and `codex-durable-backend-langgraph.ps1`
- prefer `native_omx` for worker-centric durable execution, worktree isolation, mailbox flow, and direct worker lifecycle control
- prefer `langgraph` for graph-shaped multi-phase execution, checkpoint-driven recovery, interrupt/resume approval gates, frozen implementation briefs, and persisted survivor queues
- keep backend-family switching explicit by default
- automatic durable routing should honor the selected backend instead of silently switching backend family
- one durable task should use one backend family at a time
- keep backend-family selection in the shared user-level control layer while leaving each repository's canonical durable state repo-local

### 17.2 Current layered capability-switch model

The current implemented user-level model uses layered capability switches together with a compatibility backend view:

- `subagent_routing = auto | manual | off` - layered capability switch for expert routing posture.
- `oh_my_codex = on | off` - layered capability switch for the oh-my-codex workflow layer.
- `langgraph = on | off` - layered capability switch for LangGraph availability.
- `durable_orchestration_backend` remains as an operator-facing compatibility view derived from the layered state

Current behavior:

- `subagent_routing=off` disables higher orchestration layers
- `langgraph=on` requires `oh_my_codex=on`
- when the relevant capability layers are enabled, Codex CLI can choose the per-task effective lane rather than forcing one global durable backend family
- when both durable capabilities are enabled and no LangGraph-specific signals are present, worker-centric task flows default to `native_omx`
- when graph phases, checkpoint gates, frozen implementation briefs, survivor queues, or tracked LangGraph state are present, the effective lane can move to `langgraph`

This keeps backend-family choice inspectable while preserving the current layered capability model as implemented state rather than future direction.

### 17.1 What counts as long-running collaborative parallel execution for `native_omx`

`native_omx` is the preferred durable backend when the work is primarily worker-centric and the team needs long-running collaborative parallel execution rather than graph-first orchestration.

Treat a task as OMX-suited long-running collaborative parallel execution when most of the following conditions hold:

- at least two execution slices are expected to run in parallel for longer than one short session, typically 30 to 60 minutes or more
- the work is likely to cross sessions, pause, or interruption, and still needs a clean resume path later
- the leader needs inspectable team state such as current worker shape, tracked team identity, active blockers, and next step, rather than relying on chat memory alone
- the work will involve multiple handoffs or ongoing collaboration between lanes, rather than one one-shot delegated answer
- the work will still need integration, stabilization, or final acceptance after the parallel execution wave, rather than just a simple one-pass merge

Practical rule:

- if three or more of the five conditions above are true, and the main need is worker lifecycle control, worktree isolation, mailbox flow, and durable execution continuity, prefer `native_omx`
- if three or more are true but the primary need is graph phases, checkpoint gates, frozen implementation briefs, or persisted survivor queues, prefer `langgraph` instead

## Appendix A. Official LangGraph Capability Gap

After the archived migration-aware live primary-engine compatibility-state rollout, this appendix should describe the validated current user-level LangGraph surface truthfully and conservatively.

A fully realized LangGraph-native orchestration runtime is still stronger than the current local user-level integration.

At the official LangGraph capability ceiling, the user-level lane would support:

- real `StateGraph` execution as the primary orchestration model
- conditional edges and graph-native routing
- iterative loops and quality-gate loops such as `draft -> review -> revise -> review -> accept`
- execution loops such as `execute -> verify -> revise -> execute` until a quality threshold is met
- reducer-backed fan-out and fan-in state merging
- reusable subgraphs
- durable checkpoints and resumable thread state
- interrupts and approval-gated resume
- replay, time-travel, and state-history inspection
- explicit state update and recovery controls

The validated local user-level status should therefore be described in three buckets: already implemented, usable but still MVP-shaped, and still in plan or incremental retrofit.

Already implemented:

- layered user-level capability switches for `subagent_routing`, `oh_my_codex`, and `langgraph`
- repo-local LangGraph runtime state under `.omx/state/langgraph/`
- user-level entrypoints and backend-aware activation surfaces
- additive LangGraph selection under Codex / oh-my-codex instead of a separate replacement runtime
- a bounded seven-phase LangGraph durable shell with graph-native conditional routing and quality-gated loop posture for the currently supported loop families
- LangGraph loop projection fields such as `active_loop`, `iteration_count`, `iteration_budget`, `last_gate_verdict`, and `stop_reason`
- reusable subgraph-library contracts plus active-subgraph projection
- command-driven control flow, explicit parent handoffs, and command-aware resume posture
- additive streaming and debug observability with bounded latest-event projection
- runtime-context and injected-store projection surfaces
- durable memory-store and semantic-memory projection surfaces
- graph-migration and thread-compatibility guard posture
- multi-interrupt approval-queue posture with explicit resume mapping
- replay, time-travel, and bounded update-state recovery controls with source attribution
- stable frozen implementation brief artifacts with `brief_id`, `thread_id`, `source_evidence_refs`, and `frozen_at`
- stable judge-approved survivor queue artifacts with queue metadata, survivor counts, and read-oriented inspect pointers
- inspectable durable-state projection for LangGraph artifact presence and artifact-level summary status
- reducer-backed merge channels, single-writer protection, and reducer-aware fan-in / fan-out projection for LangGraph durable threads
- a bounded graph-kernel layer that maps the seven-phase durable shell into `StateGraph`-oriented node and transition posture with repo-local inspectability
- a bounded primary-runtime engine layer that projects compiled-engine identity and execution posture while remaining compatible with the current user-level operator model
- a bounded compiled-invocation layer that projects live compiled-path identity, invoke posture, and invocation helper surfaces while preserving the current operator model
- a bounded live-execution layer that can request or report compiled graph execution posture while preserving repo-local compatibility and current operator surfaces
- a bounded generalized live-routing layer that projects graph-native route selection and loop posture while preserving the seven-phase operator shell
- official subgraph persistence-mode defaults together with bounded subgraph-state inspection posture and helper surfaces for reusable subgraphs
- a fuller live `StateGraph` primary execution-engine layer that projects richer execution paths, resulting phase or status, and bounded primary execution semantics through the current user-level helper surfaces
- a bounded richer automatic runtime-policy layer that exposes inspectable automatic migration-handling posture and safe resolved-queue auto-resume behavior while remaining manual-first by default
- a deeper live primary-engine layer that projects multi-step phase or node paths, explicit stop boundaries, and recursion-limit-aware deeper execution posture through the current user-level helper surfaces
- a broader bounded automatic runtime-policy layer that now also covers safe recovery continuation and stale-interrupt clearing while remaining inspectable, additive, and manual-first by default
- a superstep-aware live primary-engine layer that traverses a bounded multi-node compiled graph path and projects node or phase visit traces, superstep counts, and bounded boundary posture through the current user-level helper surfaces
- a stateful live primary-engine layer that carries next-hop decisions and transition logs inside graph-native execution state while preserving the seven-phase operator shell and current durable artifacts
- a graph-resident live primary-engine boundary-state layer that carries interrupt, recovery, and terminal boundary posture through graph-native engine state instead of short-circuiting those boundaries before compiled execution begins
- a subgraph-aware live primary-engine handoff-state layer that carries active-subgraph, source-subgraph, target-subgraph, and parent-handoff continuation posture inside live-engine state instead of relying on adjacent projection surfaces alone
- an approval-aware live primary-engine resume-state layer that carries queue posture, pending-versus-resolved counts, current interrupt identity, and resume-map keys inside live-engine state instead of relying on adjacent approval projections alone
- a recovery-aware live primary-engine provenance-state layer that carries recovery action, recovery target identity, source-record provenance, recoverable field touches, and history-target availability inside live-engine state instead of relying on adjacent replay or recovery projections alone
- a durable-artifact-aware live primary-engine state layer that carries artifact-state kind, implementation-brief presence and identity, brief source-evidence reference counts, survivor-queue presence and kind, and survivor counts inside live-engine state instead of relying on adjacent artifact projections alone
- a reducer-aware live primary-engine merge-state layer that carries reducer compatibility, fanout state, invalid multi-writer posture, merge-channel updates, channel item counts, and reducer source attribution inside live-engine state instead of relying on adjacent reducer projections alone
- a command-aware live primary-engine control-state layer that carries transition kind, update keys, goto target, graph scope, source-subgraph and target-subgraph attribution, parent-handoff target, resume posture, and resume-payload keys inside live-engine state instead of relying on adjacent command projections alone
- a runtime-aware live primary-engine context-store-state layer that carries context schema, runtime-context presence and keys, runtime-context kind hints, store configuration posture, store access expectation, and store kind inside live-engine state instead of relying on adjacent runtime injection projections alone
- a memory-aware live primary-engine semantic-state layer that carries memory-store configuration, memory-store kind, memory namespaces, semantic-memory enablement, semantic-store kind, and semantic namespaces inside live-engine state instead of relying on adjacent memory projections alone

Usable but still MVP-shaped:

- the current lane still persists and projects LangGraph durable posture through a Python sidecar and repo-local state rather than a fully generalized official `StateGraph` runtime kernel
- several operator surfaces are intentionally bounded contract projections rather than raw full-fidelity engine-native traces
- backend-family coexistence with `native_omx` remains explicit and manual-first

Still in plan or incremental retrofit:

- any later subgraph or lane expansion that goes beyond the current reusable-library contract set and the current bounded persistence or inspection posture
- any later automatic-policy expansion that goes beyond the current bounded migration-handling, safe resolved-queue, safe recovery continuation, and stale-interrupt clearing posture
- any further live-engine expansion that goes beyond the current memory-aware semantic-state handling, runtime-aware context-store handling, command-aware control handling, reducer-aware merge handling, durable-artifact-aware handling, recovery-aware provenance-state handling, approval-aware resume-state handling, and bounded stop-boundary posture

The practical interpretation is:

- the current user-level LangGraph lane is real and usable
- it is not yet a fully realized LangGraph-native orchestration runtime
- documentation should describe it as an additive durable backend with a broad implemented contract surface, while still keeping the not-yet-fully-realized runtime boundary explicit

## Appendix B. Stable User-Level Command Names

The current installed user-level command surface now has three layers:

- `codex` - legacy or environment-dependent entry name.
  - a legacy or environment-dependent entry name
  - may still be shadowed by project-local `.venv` command directories or shell startup behavior
- `codex-ohmy` - preferred stable wrapped command for daily multi-project use.
  - the preferred stable wrapped command for multi-project daily use
  - enters the user-level oh-my-codex launcher without relying on a PowerShell profile binding
- `codex-raw` - preferred stable native bypass command for raw Codex use.
  - the preferred stable native bypass command for multi-project daily use
  - enters raw native Codex without relying on a PowerShell profile binding

Operational guidance:

- prefer `codex-ohmy` for day-to-day wrapped Codex usage across repositories
- prefer `codex-raw` when a clean native bypass is needed
- treat `codex.openclaw` and `codex-native` as explicit compatibility surfaces, but prefer the stable names above for routine operator use

## Appendix C. Standard Workflow for Official Update + Diff Check + Local Patch Replay

This appendix defines the current repository policy for keeping the upstream `oh-my-codex` install updateable while preserving the local Windows durability fixes.

Use this as the default maintenance sequence whenever the global npm-installed OMX build is refreshed.

Companion executable template:

- `tools/codex-official-update-patch-replay-template.ps1` - repository maintenance template for official update, diff, replay, and test stages.
- read-only inventory preview:
- `.\tools\codex-official-update-patch-replay-template.ps1 -Stage precheck -Json` - read-only inventory command that emits the precheck report as JSON.
- stage-based execution:
- `-Stage precheck` - stage flag for collecting pre-update inventory and checkpoint state.
- `-Stage update` - stage flag for refreshing the official npm-installed OMX package.
- `-Stage diff` - stage flag for comparing upstream files and local patch decisions.
- `-Stage replay` - stage flag for replaying retained local patches and regenerating wrappers.
- `-Stage test` - stage flag for running post-replay validation.
- `-Stage all` - stage flag for running the full maintenance sequence.
- checkpoint continuity:
  - `precheck`  -  the pre-update inventory stage, which creates a fresh checkpoint root by default
  - `update / diff / replay / test`  -  the later maintenance stages, which automatically continue the latest checkpoint unless `-SnapshotRoot` is supplied explicitly
  - current pointer file: `<repo>/.tmp/official-update-patch-replay-latest.json`  -  the latest-run locator file, which tells later stages which checkpoint root to continue
  - current checkpoint manifest: `<snapshot-root>/checkpoint.json`  -  the per-run state record, which stores stage history and generated artifact paths
  - stage gates:
    - no recorded `precheck` -> `update / diff / replay / test` are blocked; `precheck` is the required baseline inventory stage
    - no recorded `diff` -> `replay / test` are blocked; `diff` is the review stage that refreshes the patch decision artifacts
    - no recorded `replay` -> `test` is blocked; `replay` is the patch-application stage that tests must follow
- generated operator artifacts:
  - `report.json`  -  the machine-readable run summary file for the current checkpoint
  - `checklist.md`  -  the human-readable maintenance checklist for the current checkpoint
  - `patch-decision-table.md`  -  the Markdown decision view for human reading and review
  - `patch-decision-table.json`  -  the JSON decision table, which is the current machine-readable read-back file
  - `patch-decision-table.csv`  -  the CSV decision export, which is a spreadsheet-friendly view rather than the canonical re-import file
- patch decision table behavior:
  - `final_decision`  -  the selected disposition field, which is auto-prefilled with the default recommended action
  - `decision_reason`  -  the decision explanation field, which is auto-prefilled with the default rationale
  - `decision_status`  -  the machine-readable decision-state field, which records whether the row is still automatic or has been manually changed
    - `auto_prefilled`  -  the default automatic state, meaning the row still uses the script-generated recommendation
    - `manually_overridden`  -  the manual override state, meaning a human reviewer intentionally changed the generated decision
    - `unresolved`  -  the unresolved review state, meaning the row still needs an explicit human decision
  - current default heuristics:
- `runtime.js` - team runtime file that receives the default move-down heuristic.
- `windows-worker-controller.js` - Windows worker controller file that receives the default move-down heuristic.
- `worker-bootstrap.js` - worker bootstrap file that receives the default move-down heuristic.
    - `user_level_surface`  -  the local wrapper / skill / prompt layer -> `move-down`, which means the preferred home is outside the official npm install
- example replay lane:
  - `.\tools\codex-official-update-patch-replay-template.ps1 -Stage replay`  -  the replay-stage command, which applies retained patches and regenerates the user-level layer

### Appendix C. Implemented decision-lock and diff-approval additions

The following items have now landed in `tools/codex-official-update-patch-replay-template.ps1` and should be treated as implemented operator-surface behavior.

- patch decision rows now include:
  - `decision_locked`  -  the decision lock flag, which tells the script not to overwrite a manually frozen row
  - `decision_lock_reason`  -  the decision lock note, which explains why that row was intentionally frozen
- lock semantics:
  - when `decision_locked = true`, regenerated decision rows preserve the manually frozen decision fields instead of re-autofilling them; `decision_locked` is the no-autorefresh switch for a reviewed row
- decision-table authority order:
  - `patch-decision-table.json`  -  the JSON decision master file, which is the read-back source of truth
  - `patch-decision-table.csv` and `patch-decision-table.md`  -  the export views, which remain review-oriented outputs rather than the canonical re-import surface
- checkpoint manifest now includes an approval projection:

  - `checkpoint manifest`  -  the checkpoint state file at `<snapshot-root>/checkpoint.json`, which now includes an approval block for diff review state
  - `approvals.diff_review`  -  the diff-review approval block, which stores whether the diff stage has been explicitly approved
  - `approved`  -  the approval boolean, which stores whether diff review has passed
  - `approved_at`  -  the approval timestamp, which stores when diff review was approved
  - `approval_note`  -  the approval note text, which stores a short reviewer comment

```json
{
  "approvals": {
    "diff_review": {
      "approved": false,
      "approved_at": "",
      "approval_note": ""
    }
  }
}
```

- operator control surface now includes:
  - `-Stage diff -ApproveDiff`  -  the diff-approval command form, which will mark the diff stage as reviewed and approved
- replay gate is now strengthened:
  - `replay`  -  the patch replay stage, which requires `precheck`; `precheck` is the baseline inventory stage that starts the checkpoint
  - `replay` requires `diff`; `diff` is the review stage that refreshes the decision artifacts before patch application
  - `replay` requires `approvals.diff_review.approved = true`; `approvals.diff_review.approved` is the manifest field that means the diff review has been explicitly approved

### C.1 Scope buckets

Treat the local stack as four different layers and do not collapse them into one:

1. **Official upstream install**
   - current example path: `C:\Users\lenovo\AppData\Roaming\npm\node_modules\oh-my-codex\`
   - updated by upstream npm install or `omx update`
2. **User-level generated wrapper layer**
   - current example path: `C:\Users\lenovo\.codex\bin\`
   - generated from `tools/install-codex-user-level-team-mode.ps1`
3. **User-level prompts / skills / playbooks**
   - current example paths:
- `C:\Users\lenovo\.codex\skills\worker\SKILL.md` - user-level worker skill instructions generated or maintained outside the npm package.
- `C:\Users\lenovo\.codex\state\user-level-team-mode-model-instructions.md` - user-level model-instructions payload for team-mode workers.
4. **Repository source-of-truth patch and test layer**
   - current example paths:
- `tools/openclaw-omx-*.mjs` - repository patch scripts for legacy OMX compatibility fixes.
- `tools/install-codex-user-level-team-mode.ps1` - installer script that regenerates user-level wrappers and team-mode artifacts.
- `test/install-codex-user-level-team-mode.test.ps1` - PowerShell test suite for the team-mode installer.

The maintenance goal is:

- keep layer 1 as close to upstream as possible
- move as much behavior as practical into layers 2 through 4
- re-patch layer 1 only when the current upstream install does not expose a safe extension point

### C.2 Update-before checklist

Before any official update, do all of the following in order.

#### 1. Freeze the current local state

Record:

- current global `oh-my-codex` version
- current global `@openai/codex` version
- current upstream install root
- current repo commit for the local patch layer

Recommended read-only commands:

```powershell
npm root -g
npm ls -g oh-my-codex @openai/codex --depth=0
git -C D:\PythonProject_langgraph rev-parse HEAD
```

#### 2. Snapshot the currently patched upstream files

At minimum, snapshot the current contents of:

- `dist/team/runtime.js` - upstream team runtime file to snapshot before update.
- `dist/team/windows-worker-controller.js` - upstream Windows worker controller file to snapshot before update.
- `dist/team/worker-bootstrap.js` - upstream worker bootstrap file to snapshot before update.

Also capture a marker inventory:

```powershell
$npmRoot = npm root -g
$omxRoot = Join-Path $npmRoot 'oh-my-codex'
Get-ChildItem (Join-Path $omxRoot 'dist\\team') -Recurse -File |
  Select-String -Pattern 'OPENCLAW_' |
  Select-Object Path, LineNumber, Line
```

This pre-update inventory is the baseline for deciding which local patches survived upstreaming, which broke, and which should now be deleted.

#### 3. Snapshot the generated user-level layer

Read-only verify the generated Windows-safe surfaces before update:

- `C:\Users\lenovo\.codex\bin\omx-team-send-message.ps1` - user-level wrapper for sending worker mailbox messages safely on Windows.
- `C:\Users\lenovo\.codex\bin\omx-team-claim-task.ps1` - user-level wrapper for claiming a team task.
- `C:\Users\lenovo\.codex\bin\omx-team-transition-task-status.ps1` - user-level wrapper for changing task lifecycle status.
- `C:\Users\lenovo\.codex\bin\omx-team-release-task-claim.ps1` - user-level wrapper for releasing a task claim.
- `C:\Users\lenovo\.codex\bin\omx-team-report-progress.ps1` - user-level wrapper for reporting worker progress.
- `C:\Users\lenovo\.codex\bin\omx-team-complete-task.ps1` - user-level wrapper for marking a task complete.
- `C:\Users\lenovo\.codex\bin\omx-team-fail-task.ps1` - user-level wrapper for marking a task failed.

If these are already missing or stale before the official update, fix the generator layer first; do not blame the upcoming upstream refresh for a pre-existing local install problem.

#### 4. Avoid changing live worker code mid-launch

Existing already-started sessions typically continue running on their current process image, but new worker launches after a half-applied update can mix old and new assumptions.

Practical rule:

- do not start a new durable team while the npm update and local replay are in flight
- finish the update window first, then start new durable workers

### C.3 Official update step

Use the official upstream update path first, not the local patch scripts.

Current upstream README guidance says the default update path is global npm install, with `omx setup` or `omx update` as the refresh path when needed. Source: the upstream `oh-my-codex` README on GitHub.

Recommended sequence:

```powershell
npm install -g @openai/codex oh-my-codex
omx setup
```

If npm scripts were skipped or the install was non-interactive:

```powershell
omx update
```

Do **not** replay local patches until the official update has fully completed.

### C.4 First post-update diff pass

Immediately after the official update, compare in this order.

#### Diff pass 1: file and API shape

Check whether the upstream update changed any of these:

- `dist/team/runtime.js` - upstream team runtime file checked for file and API shape drift.
- `dist/team/windows-worker-controller.js` - upstream Windows worker controller file checked for file and API shape drift.
- `dist/team/worker-bootstrap.js` - upstream worker bootstrap file checked for file and API shape drift.
- exported helper names used by the local patch scripts
- CLI behavior assumed by the wrapper scripts

If a target file moved or was renamed, stop and repair the replay scripts before reapplying anything.

#### Diff pass 2: overlap with local functionality

Check whether upstream now provides native equivalents for any local additions, especially:

- Windows-safe worker lifecycle entrypoints
- better worker completion or failure instructions
- Windows stdin close or prompt handling
- startup status seeding
- worktree writable-root handling
- prompt-controller detach or teardown behavior
- worker guidance that already prefers wrapper commands over raw JSON payload construction

If upstream now covers the same behavior adequately, prefer the upstream implementation and delete the local patch instead of replaying it.

#### Diff pass 3: replayability of each local patch

Classify every local patch into one of four states:

1. **drop**
   - upstream already solved it cleanly
2. **move down**
   - keep the behavior, but implement it in wrappers / skills / playbooks / tests instead of patching upstream
3. **rebase**
   - same need still exists, but the patch script must be retargeted to the new upstream file shape
4. **replay unchanged**
   - upstream did not materially change the affected logic and the patch is still required

### C.5 Patches that should be pushed downward into the wrapper layer first

These are the first candidates to keep out of the upstream install whenever possible.

#### 1. Pure operator-surface wrappers

Keep these generated and owned locally:

- `omx-team-send-message.ps1` - local wrapper for sending worker mailbox messages.
- `omx-team-mailbox-list.ps1` - local wrapper for listing worker mailbox messages.
- `omx-team-mailbox-mark-delivered.ps1` - local wrapper for marking mailbox messages delivered.
- `omx-team-claim-task.ps1` - local wrapper for claiming a team task.
- `omx-team-transition-task-status.ps1` - local wrapper for changing task lifecycle status.
- `omx-team-release-task-claim.ps1` - local wrapper for releasing a task claim.
- `omx-team-report-progress.ps1` - local wrapper for reporting worker progress.
- `omx-team-complete-task.ps1` - local wrapper for marking a task complete.
- `omx-team-fail-task.ps1` - local wrapper for marking a task failed.

These are exactly the kind of Windows-safety and JSON-shaping logic that should live in user-level wrappers, not in upstream package internals.

#### 2. Prompt/playbook/documentation guidance

Prefer to keep these local:

- generated worker playbooks
- generated user-level model instructions
- wait-window and periodic check-in policy
- examples that teach workers to call wrapper scripts instead of hand-writing `omx team api --input ...`

If upstream later exposes a stable external prompt hook for workers, move even more of the Windows-specific worker guidance here and delete corresponding upstream prompt patches.

#### 3. Worker-visible raw-abstraction examples

Anything whose only job is:

- hiding raw JSON examples from Windows workers
- replacing unsafe PowerShell one-liners with wrapper examples
- documenting the preferred wrapper-first closure flow

should be pushed downward first into:

- wrapper docs
- worker skill content
- generated instructions
- installer tests

#### 4. Replay automation, diff automation, and assertions

These belong entirely in the repository layer:

- patch-application scripts
- replay validation scripts
- test assertions
- update checklists
- documentation about official-update handling

### C.6 Patches that still need to be replayed into the official install today

Under the current local architecture, the following classes still require direct patching of the official npm-installed package when upstream has not solved them.

#### 1. Runtime-behavior fixes inside the team engine

Keep replaying these when still needed:

- prompt-controller detach or teardown behavior in `runtime.js`
- Windows worktree writable-root fixes in `runtime.js`
- startup evidence or worker launch readiness handling in `runtime.js`
- Windows prompt-controller stdin-close / prompt-read behavior in `windows-worker-controller.js`
- startup status seeding in `windows-worker-controller.js`
- debug-root or observability hooks that are needed to inspect otherwise invisible Windows worker failures

Reason: these change actual runtime semantics of worker launch, teardown, IO, or writable path access; wrappers alone cannot fix them after the worker has already started incorrectly.

#### 2. Built-in worker-bootstrap text that is still upstream-owned

Even after wrapper-first scripts exist locally, replay may still be needed in `worker-bootstrap.js` when upstream still hardcodes problematic Windows guidance such as:

- raw `omx team api --input ...` examples shown directly to workers
- Windows-invalid shell examples
- completion/failure flows that do not point to the high-level wrapper scripts

This is not because prompt text belongs upstream conceptually; it is because the current upstream runtime still owns the built-in worker bootstrap surface.

Practical rule:

- if the needed change can be injected by local skill / prompt files alone, move it down
- if the bad example is still literally emitted from `worker-bootstrap.js`, replay the patch until upstream offers a stable hook or upstream fixes it directly

### C.7 Current replay priority for this repository

For the current Windows durable-team line, replay in this priority order after each official update:

1. **Critical runtime patches**
   - `runtime.js` - upstream team runtime file that owns core worker launch, IO, and task lifecycle semantics.
   - `windows-worker-controller.js` - upstream Windows worker controller file that owns process startup, status seeding, and worker supervision semantics.
2. **Worker bootstrap safety patches**
   - `worker-bootstrap.js` - upstream worker bootstrap file that emits built-in worker instructions and safety examples.
3. **Regenerate the local wrapper layer**
   - rerun `tools/install-codex-user-level-team-mode.ps1`
4. **Run local tests**
   - especially `test/install-codex-user-level-team-mode.test.ps1`
5. **Run a focused Windows durable-worker smoke test**
   - verify worker launch
   - verify worker remains alive
   - verify task completion converges to `completed`

### C.8 Definition of done after replay

An official update is not considered complete until all of the following are true:

- upstream update finished successfully
- post-update diff pass was completed
- each local patch was explicitly classified as drop / move-down / rebase / replay
- required upstream-install patches were replayed successfully
- the user-level wrapper layer was regenerated
- tests passed
- at least one focused Windows durable-worker smoke path passed

That is the repository-standard meaning of:

- **official update + diff check + local patch replay**
