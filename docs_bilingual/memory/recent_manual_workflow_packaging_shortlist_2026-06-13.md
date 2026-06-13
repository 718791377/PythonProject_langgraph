---
doc_id: recent_manual_workflow_packaging_shortlist_2026_06_13
lang: en
status: active
doc_class: memory
zh_cn_path: docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.zh-CN.md
---

# Recent Manual Workflow Packaging Shortlist

Generated at: `2026-06-13T03:32:14.934671+00:00`
Lookback window: `30` days
Chronicle: `not_enabled` (discovery only; no writes)

## Packaging Decision

- Project-level: implemented in this run because inputs depend on this repository's Git history, memory, implementation plans, and local gates.
- User-level: candidate only; install requires cross-project proof, redaction, rollback, smoke evidence, and separate authorization.
- Do not package: custom subagent, scheduler, Chronicle writes, and external live actions are skipped because existing roles cover them or the privilege/privacy surface is too large.

## Shortlist

### local-main-first-governance-packaging: Plan -> local gate/MR review -> local main integration packaging

- Recommended form: `extend-existing/project-level-skill`
- Frequency/confidence: 213 evidence hits in the lookback window / `high`
- Actionable now: `true`
- Why: The repository repeatedly freezes plans, validates them, commits, merges to local main, and stops at the remote-publication gate. Existing helpers cover the merge mechanics, but a narrow packaging skill/CLI makes the discovery and decision step repeatable.
- Supporting evidence:
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:cd2a65c35f:5ba4dea:chars=16] (5ba4dea)
  - 2026-06-12 [git] [REDACTED_NON_ASCII_TEXT:b92d3bf3f0:ea9a442:chars=16] (ea9a442)
  - 2026-06-12 [git] [REDACTED_NON_ASCII_TEXT:43ae64a390:f3c2900:chars=12] (f3c2900)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:9fcbf9804b:d401cf9:chars=13] (d401cf9)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:f331e827e2:72c657a:chars=14] (72c657a)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:378a3021bb:f911dd7:chars=13] (f911dd7)

### r5-r6-live-runtime-evidence-gates: R5/R6 live runtime evidence receipt gates

- Recommended form: `extend-existing/skip-duplicate`
- Frequency/confidence: 193 evidence hits in the lookback window / `high`
- Actionable now: `false`
- Why: Repeated R5/R6 work is already covered by checker-backed runtime and receipt gates, so the packaging action is to reuse and extend existing gates rather than create a new broad asset.
- Supporting evidence:
  - 2026-06-12 [git] [REDACTED_NON_ASCII_TEXT:d9065619d8:9493cde:chars=12] (9493cde)
  - 2026-06-12 [git] [REDACTED_NON_ASCII_TEXT:e0f021bb30:b67b94f:chars=12] (b67b94f)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:9fcbf9804b:d401cf9:chars=13] (d401cf9)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:f331e827e2:72c657a:chars=14] (72c657a)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:378a3021bb:f911dd7:chars=13] (f911dd7)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:1b42cdc8a7:94dd221:chars=35] (94dd221)

### skills-usage-audit-cadence: Codex skills usage audit and warning-triage cadence

- Recommended form: `extend-existing`
- Frequency/confidence: 177 evidence hits in the lookback window / `high`
- Actionable now: `false`
- Why: Weekly summaries and triage files show recurrence, but the repository already has dedicated audit scripts and memory outputs. Keep using those and feed their sanitized signals into this report.
- Supporting evidence:
  - 2026-06-09 [git] [REDACTED_NON_ASCII_TEXT:8825bb4748:5d37ffd:chars=11] (5d37ffd)
  - 2026-06-09 [git] [REDACTED_NON_ASCII_TEXT:d4646889b4:1455e87:chars=10] (1455e87)
  - 2026-06-07 [git] [REDACTED_NON_ASCII_TEXT:b082a35a75:43dda79:chars=20] (43dda79)
  - 2026-06-06 [git] [REDACTED_NON_ASCII_TEXT:d1d9057589:bee9791:chars=29] (bee9791)
  - 2026-06-04 [git] [REDACTED_NON_ASCII_TEXT:9c74b491b8:98cc08b:chars=27] (98cc08b)
  - 2026-06-03 [git] [REDACTED_NON_ASCII_TEXT:1c46d504c1:dc9e620:chars=33] (dc9e620)

### gui-browser-wxwork-live-actions: GUI/browser/WXWork live-action governance

- Recommended form: `needs-more-evidence/separate-plan`
- Frequency/confidence: 126 evidence hits in the lookback window / `high`
- Actionable now: `false`
- Why: The work recurs and is costly, but it includes sensitive external live actions. Keep it out of this generic packager and require separate explicit authorization, rollback, smoke, and privacy evidence.
- Supporting evidence:
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:0385e6cef0:838f256:chars=39] (838f256)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:79a6537f4a:41ca534:chars=39] (41ca534)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:1b42cdc8a7:94dd221:chars=35] (94dd221)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:5feee64ccf:66c9b1a:chars=37] (66c9b1a)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:c8e403d97b:99bd7fc:chars=33] (99bd7fc)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:4f196ad79e:f969454:chars=29] (f969454)

### general-template-cross-project-sync: General/General_2 template propagation for cross-project reuse

- Recommended form: `extend-existing/project-template`
- Frequency/confidence: 14 evidence hits in the lookback window / `high`
- Actionable now: `false`
- Why: Template propagation recurs, but it is a project-template concern with existing plans and evidence. This report should list it as a recurring workflow, not mutate template folders.
- Supporting evidence:
  - 2026-06-12 [git] [REDACTED_NON_ASCII_TEXT:d9065619d8:9493cde:chars=12] (9493cde)
  - 2026-06-12 [git] [REDACTED_NON_ASCII_TEXT:e0f021bb30:b67b94f:chars=12] (b67b94f)
  - 2026-06-12 [git] [REDACTED_NON_ASCII_TEXT:43ae64a390:f3c2900:chars=12] (f3c2900)
  - 2026-06-09 [git] [REDACTED_NON_ASCII_TEXT:819f412cca:5866f3e:chars=11] (5866f3e)
  - 2026-06-08 [git] [REDACTED_NON_ASCII_TEXT:72c1b6f56f:fd6403f:chars=13] (fd6403f)
  - 2026-05-30 [git] [REDACTED_NON_ASCII_TEXT:ca753632bd:58de0d8:chars=26] (58de0d8)

### recent-manual-workflow-packaging: Recent manual workflow packaging itself

- Recommended form: `project-level-skill-and-manual-cli`
- Frequency/confidence: 18 evidence hits in the lookback window / `high`
- Actionable now: `true`
- Why: The prompt is a reusable meta-workflow with stable evidence order and stopping conditions. The high-confidence missing asset is this project-level skill plus manual CLI.
- Supporting evidence:
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:cd2a65c35f:5ba4dea:chars=16] (5ba4dea)
  - 2026-05-21 [git] [REDACTED_NON_ASCII_TEXT:83cfc6e719:57946d8:chars=17] (57946d8)
  - 2026-05-21 [git] [REDACTED_NON_ASCII_TEXT:b37edba095:8c2ad00:chars=24] (8c2ad00)
  - 2026-05-19 [git] [REDACTED_NON_ASCII_TEXT:c701294d47:58e984b:chars=16] (58e984b)
  - 2026-06-13 [memory] recent_manual_workflow_packaging_shortlist_2026-06-13 (docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.md)
  - 2026-06-13 [memory] recent_manual_workflow_packaging_shortlist_2026-06-13.zh-CN (docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.zh-CN.md)

## Created Or Extended

- `repo-local-recent-workflow-packaging-skill` - project-level skill - `.agents/skills/recent-workflow-packaging/SKILL.md` - `present`
- `recent-workflow-packaging-cli` - project-level manual CLI - `tools/report_recent_manual_workflow_candidates.py` - `present`

## User-Level Candidates

- `extend-user-level-wrapper` - Thin user-level wrapper/config for the project CLI - `user-level-candidate-only` - Promote only after the project CLI is stable across two or more projects and has rollback plus smoke evidence. No user-level install is performed by this run.

## Deliberately Skipped

- `custom-subagent-for-packaging` - Custom subagent for workflow packaging: Existing analyst/planner/writer/verifier roles already cover bounded investigation and write-up needs.
- `scheduled-packaging-audit` - Scheduled packaging audit: Scheduling expands the automation and approval surface; keep this as a manual CLI until a separate scheduled-automation plan exists.
- `chronicle-write-integration` - Chronicle write or mutation integration: Chronicle is discovery-only here. The report records not_enabled or discovery signals but never writes external state.
- `external-live-action-automation` - External live-action automation: Browser, GUI, WXWork, and similar live actions are sensitive and require their own explicit authorization and receipts.

## Needs More Evidence

- `extend-user-level-wrapper` - Thin user-level wrapper/config for the project CLI: Promote only after the project CLI is stable across two or more projects and has rollback plus smoke evidence. No user-level install is performed by this run.
- `external-action-packagers` - Generic browser/GUI/WXWork live-action packagers: Needs per-system authorization, rollback, privacy review, and live smoke evidence before packaging.

## Safety And Redaction

- `raw_sessions_read`: `False`
- `raw_runtime_logs_read`: `False`
- `chronicle_mutated`: `False`
- `user_level_config_mutated`: `False`
- `scheduler_created`: `False`
- `external_actions_performed`: `False`
- `path_redaction`: `repo-relative paths only; user-level paths reduced to names/counts; unreadable legacy text is hashed`
