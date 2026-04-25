---
doc_id: openspec_usage_convention
lang: en
canonical: docs_bilingual/governance/openspec_usage_convention.md
translation_of: null
doc_class: governance
status: active
---

# OpenSpec Usage Convention

## 0. OpenSpec Governance Alignment

This governance document remains the repository-level usage convention for day-to-day OpenSpec practice.

The reusable authority form for documentation layering and bilingual OpenSpec governance is now carried in:
`openspec/specs/documentation-layering-and-bilingual-openspec-governance/spec.md`

The reusable authority form for shared runtime guardrails, runtime-state naming, and official upstream-source baselines is now carried in:
`openspec/changes/runtime-guardrails-and-official-source-baselines/`

The repository-local authority form for official OpenSpec authority order, bootstrap refresh, and enforcement surfaces is now carried in:
`docs_bilingual/governance/openspec_official_workflow_policy.md`

That authority form does not replace this document. This file remains the usage convention companion for repository practice, rollout discipline, and operator-facing interpretation.

## 1. Purpose

This document defines the project-level working convention for how OpenSpec should be used inside this repository.

OpenSpec governance in this repository should be read through one additional boundary:

- user-level shared runtime and control surfaces may be reused across many `PyCharm / Codex CLI` projects on the same machine
- this repository remains the project-level handoff layer for repo-local source, repo-local durable state, and repository-scoped structural change
- repo-local durable truth must not be lifted into user-level shared runtime or user-level state directories

## 1A. New Session Entry Rule

For new sessions, do not use this document as the first read by default.

Read these project startup summaries first:

- [project_startup_summary.zh-CN.md](/D:/PythonProject_langgraph/docs_bilingual/project_startup_summary.zh-CN.md)
- [project_startup_summary.md](/D:/PythonProject_langgraph/docs_bilingual/project_startup_summary.md)

Only after that should the model decide whether this governance document is needed for the current task.

## 1B. Official Workflow And Enforcement Surface

Use [openspec_official_workflow_policy.md](/D:/PythonProject_langgraph/docs_bilingual/governance/openspec_official_workflow_policy.md) when the question is:

- official OpenSpec authority order
- bootstrap or refresh behavior
- repository guard, hook, or CI enforcement surfaces

This usage convention remains the companion for repository practice and document boundaries. It does not replace the official workflow policy.

## 2. Current Deployment State

OpenSpec is already deployed and usable in the repository. The remaining goal is disciplined ongoing use rather than re-initialization.

## 3. Scope

This convention applies to:

- project-level OpenSpec usage
- relation between specs, implementation plans, and governance documents
- the project-level handoff boundary between shared user-level surfaces and repo-local source-of-truth
- the pre-implementation confirmation rule
- the rule for promoting reusable lessons into stable specifications

## 4. Pre-Implementation Confirmation Rule

### 4.1 Document First, Then Execute

Before implementation:

1. create a new plan file or update an existing plan file
2. confirm the plan with the user
3. implement according to the confirmed plan

### 4.2 When The User Asks To Add Or Update Spec

When the user asks to add or update a spec or document:

1. prepare the intended content first
2. confirm that the content is complete enough
3. only then create or update the target file

## 5. Standard For Promoting Reusable Experience Into Spec

Only promote content into stable common specs when it:

- does not depend on one temporary task
- is not bound to one specific run or identifier
- is not limited to one implementation detail
- has long-term maintenance and debugging value

## 6. Division Of Responsibility Across Document Types

### 6.1 OpenSpec

OpenSpec should carry long-term reusable rules, common architecture boundaries, and stable change structures.

OpenSpec is also the preferred destination for project-level rules promoted out of `docs_bilingual/` when those rules are:

- cross-mainline
- long-lived
- reusable
- intended to remain authoritative during execution

This includes structural rules for how this repository consumes shared user-level runtime or control surfaces while keeping repo-local source and repo-local durable truth authoritative.

### 6.2 Implementation Plan Documents

Implementation plans should carry current mainline work, phase details, bottlenecks, and current rollout steps.

### 6.2A Startup Summary

`project_startup_summary.*` should carry only stable project-entry content:

- startup iron rules
- project-level overview
- one-line mainline status
- read-order guidance

It should not expand into a detailed running progress ledger.

### 6.2B Memory Documents

`docs_bilingual/memory/` should carry session-level and mainline-level active progress, including:

- latest findings
- current blockers
- unresolved branches
- next verification targets

Memory documents extend startup summaries but do not replace OpenSpec authority.

### 6.3 Experience Ledger

The experience ledger should carry reusable lessons that may later be promoted into specs.

### 6.4 Governance And Operations Documents

Governance and operations documents should remain authoritative in their own areas without forcing everything into `openspec/specs`.

Governance documents should define document-layer boundaries, promotion standards, bilingual maintenance rules, and cross-layer synchronization rules.

Operations manuals should remain user-facing and operator-facing, not spec replacements.

### 6.4A Relationship To The Feature Validation Workflow

The project-wide feature validation workflow remains a separate execution-layer companion rather than part of OpenSpec usage governance itself.

Use:

- `docs_bilingual/operations/feature_validation_workflow.md`

when work needs:

- feature-slice identification
- targeted validation selection
- structured result, gap, and next-step reporting

OpenSpec and OPSX define how structural work should be proposed, applied, verified, and promoted.

The feature validation workflow defines how to validate a concrete multi-slice change honestly once work exists.

They are complementary:

- OpenSpec / OPSX governs structural change flow and artifact authority
- `feature_validation_workflow.*` governs repository-level verification execution and reporting discipline

Neither should be used to silently replace the other.

### 6.5 Existing Authority First, Deduplicate Before Adding Governance Text

When a new reusable lesson, rule, or governance clarification is discovered, maintainers should first check whether an existing authority surface already covers the same concern.

Preferred update order:

1. update the existing authoritative file that already owns the concern
2. remove overlap or restate only the delta
3. add new governance text only if no existing authority surface can absorb it cleanly

Do not create a new parallel governance explanation when an existing OpenSpec artifact, governance document, methodology document, or experience ledger can be updated with a smaller delta.

This rule applies especially to:

- OpenSpec change/design/spec/task artifacts
- `docs_bilingual/governance/*`
- `docs_bilingual/methodology/*`
- `docs_bilingual/experience_ledgers/*`

The goal is to keep authority layered, deduplicated, and easier to keep synchronized across later repository updates.

## 7. Current Suggested OpenSpec Themes

The project currently benefits most from OpenSpec in themes such as:

- agent architecture
- normalized judgment and light-model assistance
- candidate selection and online correction
- official sub-agent rollout branches

## 7A. Mandatory First-Choice Closed-Loop Rule

For future repository work, one governance rule is now mandatory:

- whenever a case still requires multi-factor judgment after direct rules or simple deterministic checks, maintainers must first choose one of the governed closed-loop patterns below

Those patterns are:

- `candidate pool + normalization + bounded light-model gray-zone arbitration`
- `candidate pool + normalization + bounded light-model gray-zone arbitration + online correction + experience accumulation`

The shorter pattern must be used first for bounded gray-zone selection or arbitration.

The fuller pattern must be used first when repeated drift, later correction, or reusable sample accumulation is likely.

Before those governed patterns are considered, maintainers must not default to:

- prompt-only heuristics
- one-off local patches
- ad hoc terminology that bypasses the shared closed-loop vocabulary

## 8. Acceptance Logic

OpenSpec work is structurally complete only after:

- relevant change and spec artifacts are consistent
- validation is complete
- related implementation or governance documents are synchronized

Artifact completeness alone does not mean runtime completion, rollout completion, or live acceptance.

Maintainers must distinguish at least three different closure states:

- artifact/spec completeness
- implementation or wiring completeness
- real runtime rollout or live acceptance completeness

Archive decisions must use the strongest relevant closure state rather than the weakest one.

### 8.1 Runtime-Rollout And Migration Archive Gate

Changes that depend on real runtime rollout, active-gateway reachability, end-to-end child-session behavior, live family enablement, or other live-path evidence SHALL NOT be archived merely because:

- `openspec status --change ...` reports `isComplete: true`
- proposal/design/specs/tasks are all present
- repo-local regression tests pass
- stable-spec sync is finished

For such changes, archive requires the real runtime or live rollout evidence promised by the change itself.

This applies especially to:

- migration changes
- official-sub-agent rollout changes
- family-scoped bounded-live rollout changes
- any change whose acceptance text requires runtime evidence, live reachability, live-family comparison, or end-to-end rollout proof

If a change was archived using artifact closure or repo-local regressions as a stand-in for required live/runtime acceptance, it should be returned from `archive/` to active `openspec/changes/` until the missing rollout gate is honestly closed.

Governance- or spec-promotion-oriented changes may archive once their own non-runtime acceptance gates are satisfied, as long as they do not claim unfinished runtime rollout as already complete.

### 8.2 Runtime Backup And Restore Authority Boundary

When runtime recovery or acceptance work depends on preserved Local Control state, maintainers SHALL distinguish among:

- historical cold-start snapshots
- canonical pre-cold-start restore anchors
- current live runtime sidecars

Historical cold-start snapshot directories are preserved evidence packages and SHALL NOT be overwritten during routine refresh or later rollout validation.

Canonical pre-cold-start backup files are restore anchors and SHALL NOT be overwritten by later live sidecar refreshes unless the repository explicitly redefines the canonical restore policy.

Current live runtime sidecars MAY be refreshed by new runtime runs, but maintainers SHALL NOT confuse those mutable targets with preserved historical snapshots or canonical restore anchors.

If a recovery or acceptance conclusion depends on a preserved cold-start or pre-cold-start artifact, maintainers SHALL cite the preserved source explicitly rather than assuming the current live sidecar still reflects that earlier state.

For Local Control cold-start acceptance work, maintainers SHALL refresh mutable retained-state sidecars before taking the new cold-start sample.

That refresh SHALL preserve:

- historical cold-start snapshot directories
- canonical pre-cold-start restore anchors

That refresh SHALL NOT be skipped merely because the current live runtime sidecars still look readable or recent.

## 8A. Bilingual OpenSpec Authority Rule

Project-level OpenSpec artifacts should follow a bilingual authority rule:

- English ASCII artifacts are primary
- Chinese artifacts are companion translations
- updates should proceed English first, then Chinese

This rule applies whenever repository content is promoted from `docs_bilingual/` into reusable OpenSpec artifacts.

For governance artifacts under `docs_bilingual/` and `openspec/`, the rule is stricter:

- every bilingual governance authority surface should be maintained as an English `.md` primary plus a Chinese `.zh-CN.md` companion
- the English `.md` file is the normative primary and should keep ASCII body text
- the Chinese `.zh-CN.md` file is the UTF-8 companion and should be updated in the same work batch
- once a governance authority surface is declared bilingual, the Chinese companion is not optional

## 9. Current Recommendation

Use OpenSpec as the stable specification and change-management layer for this repository, while keeping dynamic implementation work in dedicated implementation documents.

## 10. Prompt Governance For Child Sub-agents

All child sub-agents introduced into the repository should follow a common prompt-completeness governance rule.

This includes:

- `Research child run`
- `Judge child run`
- `Implement child run`
- future custom child roles

The governance boundary is:

- prompt completeness is governed at the orchestrator side
- review-side child sub-agents review results, not prompt templates
- prompt review must not recurse into reviewer-of-reviewer chains

When prompt incompleteness is caused mainly by missing user-side information, the system should ask for clarification in concise, friendly, group-chat-appropriate language and should not expose backend implementation terms.

For the current official-sub-agent rollout branches, this review-side boundary must remain explicit:

- `prompt-governor` stays internal to the orchestrator governance layer
- `prompt-governor` is never promoted into a live official child role
- `Judge child run` remains an output, evidence, readiness, and risk reviewer only
- `Judge child run` must not review child prompt templates or prompt-governor instructions

The current rollout state should therefore be read as:

- `Research child run`: current live official child target
- `Judge child run`: not yet live-childized; still evidence-only or replay-report oriented
- `Implement child run`: not yet live-childized; still evidence-only or replay-report oriented
- `prompt-governor`: internal-only and outside the live official child rollout

The current `sessions_spawn unknown method` condition belongs to change-level runtime-blocker tracking, not to stable architecture redefinition.

For the same reason, later migrations such as `local` must not begin merely because repository code and static docs already align to official spawn semantics. The active gateway runtime must first prove that the official spawn surface is actually reachable end-to-end.

## 11. Unified Leakage And Cross-Talk Terminology

When governance documents, implementation plans, or experience records describe leakage or cross-talk issues, they should default to the shared terminology defined in the experience ledger.

Do not create overlapping ad hoc terms when one of the following already applies:

- `self_leakage`
- `cross_talk`
- `inter_agent_cross_talk`
- `cross_message_cross_talk`
- `cross_conversation_cross_talk`
- `misrouted_return`
- `state_contamination`
- `template_misapplication`
- `overflow_induced_leakage`

If a new subtype is genuinely needed, first decide whether it is:

- a result type
- a cross-talk subtype
- or a cause label

Only then should the shared terminology be extended.

## 12. High-Concurrency, Anti-Cross-Talk, And Anti-Leakage Requirements

All `user -> orchestrator -> sub-agent` chains in this repository must satisfy three hard requirements:

- high-concurrency controllability
- anti-cross-talk
- anti-leakage

Anti-cross-talk must at minimum cover:

- `inter_agent_cross_talk`
- `cross_message_cross_talk`
- `cross_conversation_cross_talk`
- `misrouted_return`
- `state_contamination`
- `template_misapplication`

Anti-leakage must at minimum cover:

- `self_leakage`
- leakage across agent, message, or conversation boundaries
- `overflow_induced_leakage`

A chain is not accepted merely because it runs or produces one successful reply.

It must also show that:

- concurrency remains controlled
- cross-talk is prevented
- leakage is prevented

## 13. Runtime State Naming Standard

Runtime-state directories should use a stable, ASCII-only naming convention before more channel agents and runtime branches are introduced.

The standard format is:

- `channel__agent_identity__runtime_role`

This rule exists to prevent long-term ambiguity once the repository contains multiple agents under one channel.

Runtime-state naming must therefore:

- distinguish the channel
- distinguish a stable agent identity
- distinguish the runtime role or function
- avoid temporary identifiers such as task ids, message ids, or session-specific labels

Current generic names may continue temporarily as migration sources, but future standardization and onboarding should treat the new format as the default target.

## 14. Historical External OpenClaw References

The following links may still be used as historical external OpenClaw references when maintainers need migration or product-context comparison:

- `https://github.com/openclaw/openclaw`
- `https://docs.openclaw.ai/start/getting-started`

They are not the authoritative source for this repository's current orchestration line.

Use them only when the repository needs:

- historical comparison against earlier OpenClaw product assumptions
- migration notes
- external product-context checks that are explicitly outside this repository's repo-local orchestration source of truth

In particular:

- the GitHub repository remains an external product reference for OpenClaw itself
- the official documentation remains an external product or documentation reference for OpenClaw itself
- neither should override this repository's repo-local orchestration source, repo-local durable-state contract, or current governance stack

Branch-specific implementation plans may quote these links, but they must not redefine them as branch-local sources.

## 15. Project-Level OpenSpec Sources

The following should be treated as the project-level OpenSpec sources:

- official upstream baseline:
  - `https://github.com/Fission-AI/OpenSpec`
- project-local companion source:
  - `D:\PythonProject_langgraph`

When the repository needs to align OpenSpec usage, terminology, change structure, or later OpenSpec update work, the upstream repository should be treated as the authoritative upstream baseline before branch-local notes or temporary conventions.

The local companion source may be used for:

- project onboarding
- local teaching material
- repository-specific OpenSpec workflow explanation

In particular:

- the GitHub repository remains the official upstream source for future OpenSpec update and alignment work
- the local companion source may support repository practice, project-level handoff rules, and onboarding, but must not redefine the upstream baseline as a branch-local or task-local authority

## 15A. Read-Only OpenSpec-Aware Control Layer

When a repository-local control layer is explicitly configured as read-only, it should connect to OpenSpec as:

- a read-only authority reader
- a consistency-audit and phase-routing advisor
- a post-execution validation and feedback layer

It should not be treated as:

- a repository writer
- an OpenSpec artifact maintainer
- a delegated write executor
- a launcher for write-capable executors on the repository's behalf

Its recommended working order is:

1. read stable OpenSpec authority
2. read active changes
3. read companion governance, methodology, and implementation documents
4. read runtime evidence such as traces, logs, and worker-debug artifacts
5. produce routing, scope, and acceptance guidance for a separate write-capable execution path
6. return after execution to validate alignment, synchronization, and blocker movement

In this repository, actual write work should remain with separate execution paths such as PyCharm or Codex CLI, while the read-only control layer remains limited to analysis, audit, validation, and feedback.

## 16. Project-Level Official Skills Sources

The following sources should be treated as project-level official skills sources:

- `https://github.com/openclaw/clawhub`
- `https://clawhub.ai/skills?sort=downloads&nonSuspicious=true`
- Skillhub store installation source:
  - `https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/skillhub.md`

When the repository needs to align skills discovery, installation, onboarding, or later skills update work, these sources should be treated as the official baseline before branch-local notes or temporary conventions.

These sources do not change the existing governance rule:

- installation does not equal promotion
- availability does not equal live-routing authority

## 17. Mandatory User Authorization For Skill Installation

All skill installation in this repository must follow a project-level hard rule:

- installation requires the user's explicit instruction
- installation requires a second confirmation immediately before execution
- Codex and all agents may suggest or recommend skills, but must not install them autonomously

This rule applies even when the candidate skill comes from a project-level official skills source.

## 18. Same-Batch Bilingual Update Rule

When a repository authority artifact already has both English and Chinese forms, maintainers should update both in the same work batch.

Default practice is:

- update the English primary artifact
- update the Chinese companion artifact in the same batch
- do not stop after the English update unless the user explicitly authorizes a temporary exception

For governance artifacts under `docs_bilingual/` and `openspec/`, maintainers shall also follow these requirements:

- the English `.md` primary remains the normative source
- the English primary should use ASCII body text
- the Chinese companion shall be saved as UTF-8
- the Chinese companion shall not be omitted once that governance surface is bilingual

Before editing a Chinese companion file, first confirm that the current file can be read correctly enough for a safe update.

If the Chinese file appears unreadable because of mojibake, encoding corruption, or unreliable terminal rendering:

- do not continue incremental patching against unreadable text
- re-read it through an explicit UTF-8 path first
- restore or reconstruct a readable baseline if needed
- only then apply the intended Chinese update

## 19. Explicit UTF-8 Rule For Chinese And Bilingual Authority Reads

For Chinese or bilingual authority artifacts in this repository, maintainers shall treat explicit UTF-8 reading as the default first-party read path rather than as an optional recovery step.

This rule applies to:

- `openspec/changes/*` Chinese companions
- `openspec/specs/*` Chinese companions
- `docs_bilingual/*`
- other repository authority artifacts whose primary or companion text is Chinese

For governance artifacts specifically, the read order is mandatory:

1. first read the Chinese companion through an explicit UTF-8 path
2. only if that explicit UTF-8 read still fails should maintainers consider other fallback explanations or repair steps

Before maintainers conclude that a Chinese or bilingual artifact is corrupted, mojibake, or otherwise unreadable, they shall first:

1. re-read the artifact through an explicit UTF-8 path
2. distinguish source-file corruption from terminal or console rendering problems
3. only then decide whether the problem belongs to:
   - the source file
   - the read path
   - or the display layer

Maintainers shall not treat terminal-rendered garbling alone as proof that the repository file itself is damaged.

Rationale:

- Chinese authority files may be stored correctly while a constrained shell or terminal still renders them incorrectly.
- A forced explicit UTF-8 read prevents false diagnosis and unnecessary document repair.
