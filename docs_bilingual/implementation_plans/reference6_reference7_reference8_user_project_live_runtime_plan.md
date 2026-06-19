---
doc_id: reference6_reference7_reference8_user_project_live_runtime_plan
lang: en
status: active
plan_stage: R6-live-runtime
priority_order: Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit
remote_publication_allowed: false
browserbase_policy: disabled_by_user
---

# Reference 6/7/8 User-Level and Project-Template Live Runtime Plan

## Goal

Install or adapt the capabilities listed in `reference_files/6.md`, `reference_files/7.md`, and `reference_files/8.md` into Codex-usable user-level and project-template surfaces, then prove them with hash-redacted live runtime receipts. Reference 6 and Reference 7 are already checker-backed live-runtime baselines; this plan adds Reference 8 while preserving those baselines and keeping Browserbase disabled.

## Field Glossary

- `ok=true` means the checker finished successfully with no blocking errors.
- `live_executed_count` means the number of required capabilities whose Codex adapter smoke ran and produced a hash-redacted live runtime receipt.
- `disabled_count` means the number of optional capabilities intentionally excluded by policy; in this plan only Browserbase may use this state.
- `optional_disabled:user_disabled_browserbase_service_lane` means Browserbase is intentionally disabled by user policy and does not block the Reference 6/7/8 acceptance gate.
- `dedupe` means a duplicate source URL is represented by validating an existing strict live receipt instead of installing the same upstream twice.

## Current Evidence Baseline

- Reference 6 source list has 9 links. Current strict checker evidence reports a successful result, eight required live-runtime receipts, one optional disabled lane, and Browserbase disabled by explicit user policy, which means Browserbase does not block this acceptance gate.
- Reference 6 MinerU lanes are live-executed with `MINERU_API_KEY` presence and redacted MinerU/site/limit service probe receipts.
- Reference 7 source list has 25 links. Current strict checker evidence reports a successful result and twenty-five live-runtime receipts, including duplicate-source reuse of Reference 6 receipts for `html-anything` and `open-design`.
- `reference_files/8.md` has 16 links and no committed Reference 8 runtime/checker/test surface yet.
- Existing template roots are `D:/PythonProject_General` for active reusable adapters and `D:/PythonProject_General_2` for inert/opt-in heavy adapters.

## Non-Negotiable Policies

- Governance priority order is `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`.
- Raw upstream install or source-reference-only copies never count as Codex live-executed evidence.
- Every non-Codex upstream must get a local Codex adapter/fork surface before it can be marked live-executed. The default fork mode is local adapter/fork artifacts only; do not create or push remote forks.
- Do not mutate native Codex program files. User-level installation may write Codex-home skills/tools/agents/state artifacts, but must not copy secret values from `C:/Users/<user>/.codex/config.toml`.
- Browserbase remains disabled. Its disabled receipt is expected and must not block Reference 6/7/8 completion.
- Receipts must be hash-redacted and human-checkable: include tool/capability id, source URL, stage, smoke kind, command hash, artifact hash, rollback pointer hash, and a short label that lets an operator recognize the result without raw secrets or raw private paths.
- External GUI/commercial software lanes must perform real launch/probe receipts when required; if a desktop product/license is missing, record exact install/provision/resume steps and continue all independent lanes. Do not fake live-executed status.

## Reference 8 Capability Matrix

| Capability id | Source URL | Target layer | Adapter strategy | Live smoke requirement |
| --- | --- | --- | --- | --- |
| `codex-visio-paper-figure-skill` | `https://github.com/pengjunchi0/codex-visio-paper-figure-skill` | user-level + General_2 inert | Codex skill adapter plus Visio desktop probe wrapper | Real Microsoft Visio COM/process launch or explicit executable/license receipt; fixture writes a paper-figure receipt. |
| `fireworks-tech-graph` | `https://github.com/yizhiyanhua-ai/fireworks-tech-graph` | General active | diagram/runtime wrapper adapter | Generate SVG/PNG technical graph fixture and record artifact hash. |
| `open-design-ref8` | `https://github.com/nexu-io/open-design` | General active | dedupe to Reference 6 | Validate Reference 6 strict live receipt and record Reference 8 alias receipt. |
| `remotion` | `https://github.com/remotion-dev/remotion` | General active | Node/Remotion runtime wrapper adapter | Produce a tiny render manifest/frame/video-placeholder artifact; if Node package install is unavailable, use deterministic local fixture with package probe receipt. |
| `cae-agent-hub` | `https://github.com/Cai-aa/CAE-Agent-Hub/tree/main` | General_2 inert | local Codex fork/adapter for CAE workflows | Real CAE executable/license probe when available; otherwise exact provision/resume receipt, not live-executed. |
| `ansys-mcp-server` | `https://github.com/knewnothing-git/ansys-mcp-server` | General_2 inert | MCP adapter with Codex boundary wrapper | Real Ansys executable/license/MCP-server probe when available; otherwise exact provision/resume receipt, not live-executed. |
| `planning-with-files` | `https://github.com/OthmanAdi/planning-with-files` | user-level | Codex skill adapter | Plan-from-files fixture under user-level state. |
| `compound-engineering-plugin` | `https://github.com/EveryInc/compound-engineering-plugin` | General active | Codex plugin/skill boundary adapter | Engineering-plugin fixture producing a deterministic plan artifact. |
| `pm-skills` | `https://github.com/phuryn/pm-skills` | user-level | Codex skill adapter | PM roadmap/task/spec artifact fixture. |
| `scientific-agent-skills` | `https://github.com/K-Dense-AI/scientific-agent-skills` | user-level | Codex skill collection adapter | Scientific workflow fixture with literature/experiment artifact hash. |
| `agency-agents-zh` | `https://github.com/jnMetaCode/agency-agents-zh` | user-level | Codex native-agent TOML adapter | Generate/validate Chinese agent TOML entries with required top-level fields. |
| `understand-anything` | `https://github.com/Egonex-AI/Understand-Anything` | user-level + General active | multimodal/document skill adapter | Document-understanding fixture with redacted content/path hashes. |
| `zvec` | `https://github.com/alibaba/zvec` | General active | vector/search wrapper adapter | Local vector/index/query fixture and hash receipt. |
| `system-prompts-and-models-of-ai-tools` | `https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools` | General_2 inert | redacted reference-index adapter | Index metadata only; do not copy restricted prompt bodies or secrets. |
| `markitdown` | `https://github.com/microsoft/markitdown` | user-level + General active | document-conversion runtime wrapper | Convert a tiny fixture into Markdown and record output hash. |
| `headroom` | `https://github.com/chopratejas/headroom` | user-level + General active | context-budget analyzer adapter | Analyze a small fixture and record budget/report hash. |

## Current Status

<!-- CURRENT_STATUS_START -->
Status: Stage A governance package is active and frozen for Stage B implementation. The plan file is registered so Reference 8 runtime/checker/template work can cite this local-main governance package.
<!-- CURRENT_STATUS_END -->

## Task Backlog

<!-- TASK_BACKLOG_START -->
- Stage B: add Reference 8 manifest, runtime CLI, checker, and tests.
- Stage C: run user-level adapter install and hash-redacted smoke receipts.
- Stage D: sync `D:/PythonProject_General` and `D:/PythonProject_General_2` template surfaces.
- Stage E: run Reference 6/7/8 strict checks, repository gates, local MR review, and local-main integration.
<!-- TASK_BACKLOG_END -->

## Evidence Index

<!-- EVIDENCE_INDEX_START -->
- Stage A plan commit: `57c44ecb70fbf2f7aea4aa30dc200dc12d9acdcf`.
- Stage A registry fix: this docs-only governance package registers the plan as active before non-document implementation.
- Runtime evidence target: `.omx/worktree-task-receipt.json` and Reference 8 install receipts under user-level Codex state.
<!-- EVIDENCE_INDEX_END -->

## Implementation Stages

### Stage A: Freeze this implementation plan

1. Create/update this English plan and the Chinese mirror.
2. Record the Reference 6/7 live-runtime baseline and Reference 8 per-link matrix.
3. Run repository plan/precommit/OpenSpec guards that do not require Reference 8 implementation.
4. Commit the plan on an isolated branch/worktree.
5. Run local gate and local MR review if practical for documentation-only change, then fast-forward/local-merge into `main` with the project local-flow helper.
6. Stop at remote-publication gate.

### Stage B: Build Reference 8 source of truth

1. Add `tools/reference8_capability_install/manifest.json` with the 16 capabilities, dedupe policy, target layers, live runtime targets, disabled/blocked protocol, and generated policy.
2. Add `tools/reference8_capability_install/runtime.py` with `plan`, `apply`, `check`, and `smoke` subcommands following Reference 6/7 conventions.
3. Add `tools/reference8_capability_install.py` as a thin CLI wrapper.
4. Add `tools/check_reference8_capability_install.py` that verifies manifest, runtime plan, registry/CI wiring, user-level install receipts, smoke receipts, live-executed status, and template sync when requested.
5. Add `test/reference8_capability_install.test.py` covering manifest policy, disabled/non-blocking behavior, dedupe to Reference 6, receipt redaction, and template sync checks.

### Stage C: Install user-level adapters and generate receipts

1. Run Reference 8 `apply --apply --operator-confirmation` with `--codex-home` defaulting to the current user Codex home and `--sync-templates` only when template roots are present.
2. Write user-level Codex skills for user-level capabilities and agent TOML for `agency-agents-zh`.
3. Write user-level tools/state/receipts under `state/reference8-capability-install` and `tools/reference8-capability-install`.
4. Run Reference 8 smoke for every capability.
5. For Visio/CAE/Ansys, record real desktop/process/license/MCP evidence if present; otherwise record exact user provision commands/paths and keep those lanes blocked rather than claiming live-executed.

### Stage D: Sync project templates

1. Update `D:/PythonProject_General` with active reusable Reference 8 adapters and checker/local-gate registration.
2. Update `D:/PythonProject_General_2` with inert/opt-in Reference 8 adapters for heavyweight, commercial, or sensitive lanes.
3. Commit template updates in each template repository if their local governance requires commits.
4. Preserve unrelated dirty files in template repositories; do not overwrite consumer-project state.

### Stage E: Verification, integration, and cleanup

1. Run strict Reference 6, Reference 7, and Reference 8 checkers with live-executed and template-sync flags.
2. Run `python tools/run_openspec_guard.py --root .`.
3. Run `tools/ci/local_gate.ps1` and `tools/ci/local_mr_review.ps1`.
4. Commit implementation changes, run local-flow helper to merge into local `main`, preserve rollback/completed-claim evidence, and clean integrated worktree/branch.
5. Report local `main` ahead/behind remote state and stop before remote publication.

## Collaboration Plan

- Native experts: use explorer/researcher/verifier/test-engineer/code-reviewer roles for read-only mapping, external-source classification, test adequacy, and final review when platform tools allow. Do not claim expert evidence unless a native agent was actually spawned and fan-in was absorbed.
- Durable team: after Stage A is frozen, split Stage B-D into mostly independent execution slices: Reference 8 runtime/checker, tests/CI, user-level install receipts, template sync, and external desktop probes.
- Persistent team: use only if a frozen plan exists and two or more independent execution slices are active; otherwise main session remains leader and owner of integration.
- Main session remains final fan-in owner, resolves merge conflicts, runs final gates, and performs local-main integration.

## Acceptance Criteria

- Reference 6 strict checker remains `ok=true`, with Browserbase disabled by user policy and all non-disabled capabilities live-executed.
- Reference 7 strict checker remains `ok=true` and template sync is verified.
- Reference 8 checker reports all non-external-missing capabilities installed, smoke-tested, and live-executed; external commercial desktop lanes either have real launch/probe receipts or explicit provision/resume records and are not falsely marked complete.
- `D:/PythonProject_General` and `D:/PythonProject_General_2` contain the intended Reference 8 template surfaces and checker registrations.
- All receipts are hash-redacted, no secret values are copied, and remote publication remains untouched.
- Implementation and template changes are committed and integrated into local `main` according to the local-main-first workflow.


