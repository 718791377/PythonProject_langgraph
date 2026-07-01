---
doc_id: recent_manual_workflow_packaging_shortlist_2026_06_13
lang: en
status: active
doc_class: memory
zh_cn_path: docs_bilingual/memory/recent_manual_workflow_packaging_shortlist_2026-06-13.zh-CN.md
---

# Recent Manual Workflow Packaging Shortlist

Generated at: `2026-06-13T12:12:20.363890+00:00`
Lookback window: `30` days
Chronicle: `not_enabled` (discovery only; no writes)

## Packaging Decision

- Project-level: implemented in this run because inputs depend on this repository's Git history, memory, implementation plans, and local gates.
- User-level: candidate only; install requires cross-project proof, redaction, rollback, smoke evidence, and separate authorization.
- Do not package: custom subagent, scheduler, Chronicle writes, and external live actions are skipped because existing roles cover them or the privilege/privacy surface is too large.

## Broad Category Scan

These categories correspond to the broad review scope requested by `reference_files/5.md`: coding, research, writing, planning, communication, operations, analysis, and personal administration.

- **Coding and implementation** (`coding`): decision=`covered_by_shortlist`, evidence_count=`289`, mapped=`r5-r6-live-runtime-evidence-gates`, `gui-browser-wxwork-live-actions`, `recent-manual-workflow-packaging`. Recent implementation work is represented by runtime/receipt gates, GUI/browser governance, and the packager implementation itself.
- **Research and source discovery** (`research`): decision=`separate_plan_required`, evidence_count=`21`, mapped=`gui-browser-wxwork-live-actions`. Research tooling appears in recent work, but browser/live-action pieces remain sensitive and are not packaged by this generic workflow.
- **Writing and documentation** (`writing`): decision=`covered_by_shortlist`, evidence_count=`349`, mapped=`local-main-first-governance-packaging`, `recent-manual-workflow-packaging`. Documentation and planning write-ups recur heavily and are covered by the project-level skill/CLI plus local-main-first packaging candidate.
- **Planning and roadmap control** (`planning`): decision=`covered_by_shortlist`, evidence_count=`164`, mapped=`local-main-first-governance-packaging`, `recent-manual-workflow-packaging`. Plan-first local integration is one of the strongest repeated workflows in the evidence window.
- **Communication and messaging** (`communication`): decision=`separate_plan_required`, evidence_count=`7`, mapped=`gui-browser-wxwork-live-actions`. Messaging work is detected, but it involves external live actions and therefore remains out of scope for this generic packager.
- **Operations, gates, installs, and releases** (`operations`): decision=`covered_by_shortlist`, evidence_count=`153`, mapped=`local-main-first-governance-packaging`, `r5-r6-live-runtime-evidence-gates`, `general-template-cross-project-sync`. Operational gates and release discipline recur frequently and map to existing helpers plus shortlist extensions.
- **Analysis, audit, and triage** (`analysis`): decision=`covered_by_existing_assets`, evidence_count=`275`, mapped=`skills-usage-audit-cadence`, `r5-r6-live-runtime-evidence-gates`. Audit/triage recurrence is strong, but existing checker-backed assets are adequate, so the packaging decision is extend/skip duplicate.
- **Personal administration** (`personal-administration`): decision=`scanned_no_packaging_candidate`, evidence_count=`0`, mapped=none. No strong committed recent-work evidence in this repository supports packaging a personal-administration workflow.

## Shortlist

### local-main-first-governance-packaging: Plan -> local gate/MR review -> local main integration packaging

- Recommended form: `extend-existing/project-level-skill`
- Frequency/confidence: 214 evidence hits in the lookback window / `high`
- Actionable now: `true`
- Why: The repository repeatedly freezes plans, validates them, commits, merges to local main, and stops at the remote-publication gate. Existing helpers cover the merge mechanics, but a narrow packaging skill/CLI makes the discovery and decision step repeatable.
- Supporting evidence:
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:5175a2e00d:6b58c1c:chars=18] (6b58c1c)
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:b713724b1a:85b648c:chars=15] (85b648c)
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:4a17ad8a61:5bfec68:chars=31] (5bfec68)
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:cd2a65c35f:5ba4dea:chars=16] (5ba4dea)
  - 2026-06-12 [git] [REDACTED_NON_ASCII_TEXT:b92d3bf3f0:ea9a442:chars=16] (ea9a442)
  - 2026-06-12 [git] [REDACTED_NON_ASCII_TEXT:43ae64a390:f3c2900:chars=12] (f3c2900)

### r5-r6-live-runtime-evidence-gates: R5/R6 live runtime evidence receipt gates

- Recommended form: `extend-existing/skip-duplicate`
- Frequency/confidence: 190 evidence hits in the lookback window / `high`
- Actionable now: `false`
- Why: Repeated R5/R6 work is already covered by checker-backed runtime and receipt gates, so the packaging action is to reuse and extend existing gates rather than create a new broad asset.
- Supporting evidence:
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:ad32bdd7d1:5473570:chars=22] (5473570)
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:5175a2e00d:6b58c1c:chars=18] (6b58c1c)
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:11c6b4aa38:cbedd71:chars=22] (cbedd71)
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:8d6d73f4af:ea092d9:chars=22] (ea092d9)
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:c4493e872e:a9b17c1:chars=21] (a9b17c1)
  - 2026-06-12 [git] [REDACTED_NON_ASCII_TEXT:d9065619d8:9493cde:chars=12] (9493cde)

### skills-usage-audit-cadence: Codex skills usage audit and warning-triage cadence

- Recommended form: `extend-existing`
- Frequency/confidence: 205 evidence hits in the lookback window / `high`
- Actionable now: `false`
- Why: Weekly summaries and triage files show recurrence, but the repository already has dedicated audit scripts and memory outputs. Keep using those and feed their sanitized signals into this report.
- Supporting evidence:
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:ad32bdd7d1:5473570:chars=22] (5473570)
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:11c6b4aa38:cbedd71:chars=22] (cbedd71)
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:8d6d73f4af:ea092d9:chars=22] (ea092d9)
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:c4493e872e:a9b17c1:chars=21] (a9b17c1)
  - 2026-06-09 [git] [REDACTED_NON_ASCII_TEXT:8825bb4748:5d37ffd:chars=11] (5d37ffd)
  - 2026-06-09 [git] [REDACTED_NON_ASCII_TEXT:d4646889b4:1455e87:chars=10] (1455e87)

### gui-browser-wxwork-live-actions: GUI/browser/WXWork live-action governance

- Recommended form: `needs-more-evidence/separate-plan`
- Frequency/confidence: 128 evidence hits in the lookback window / `high`
- Actionable now: `false`
- Why: The work recurs and is costly, but it includes sensitive external live actions. Keep it out of this generic packager and require separate explicit authorization, rollback, smoke, and privacy evidence.
- Supporting evidence:
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:ada223840e:5d2deff:chars=38] (5d2deff)
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:4a17ad8a61:5bfec68:chars=31] (5bfec68)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:0385e6cef0:838f256:chars=39] (838f256)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:79a6537f4a:41ca534:chars=39] (41ca534)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:1b42cdc8a7:94dd221:chars=35] (94dd221)
  - 2026-06-11 [git] [REDACTED_NON_ASCII_TEXT:5feee64ccf:66c9b1a:chars=37] (66c9b1a)

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
- Frequency/confidence: 22 evidence hits in the lookback window / `high`
- Actionable now: `true`
- Why: The prompt is a reusable meta-workflow with stable evidence order and stopping conditions. The high-confidence missing asset is this project-level skill plus manual CLI.
- Supporting evidence:
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:321074aa9d:1fb2710:chars=15] (1fb2710)
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:5175a2e00d:6b58c1c:chars=18] (6b58c1c)
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:b713724b1a:85b648c:chars=15] (85b648c)
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:807b25baf1:ca5adf1:chars=14] (ca5adf1)
  - 2026-06-13 [git] [REDACTED_NON_ASCII_TEXT:cd2a65c35f:5ba4dea:chars=16] (5ba4dea)
  - 2026-05-21 [git] [REDACTED_NON_ASCII_TEXT:83cfc6e719:57946d8:chars=17] (57946d8)

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
