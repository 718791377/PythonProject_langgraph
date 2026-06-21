---
doc_id: codex_skills_usage_audit_plan
lang: en
canonical: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
translation: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
status: active
doc_class: implementation_plan
created_at: 2026-05-16
last_reviewed: 2026-06-21
plan_readiness: final-review-pending
implementation_lane: audit_only_profile_decision_support
related_docs:
  - docs_bilingual/implementation_plans/codex_user_level_skills_governance_and_profiles_plan.md
  - docs_bilingual/governance/codex_user_level_orchestration_activation_policy.md
  - docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.md
runtime_sources:
  - tools/audit_codex_skills_usage.py
  - tools/skills2cli.py
  - tools/check_skills_audit_output_retention.py
  - tools/check_skills_audit_final_review_state.py
  - tools/check_skills_audit_final_review_precheck.py
  - tools/check_skills_audit_human_review_decision_record.py
  - tools/check_skills_audit_cadence_contract.py
  - tools/check_skills_audit_frontmatter_resolution.py
  - tools/check_skills_audit_zh_evidence_encoding.py
  - tools/check_precommit_update_archive.py
---
# Codex Skills Usage Audit Plan

> **For agentic workers:** This is an audit-only implementation plan. Use the smallest sufficient local implementation surface, keep all profile changes preview-only, and verify every report with the field contract before using it as evidence. Do not edit Codex `config.toml`, plugin cache, or hard-load profiles unless a later task has explicit apply authorization.

**Goal:** Run a 30-day, evidence-based audit of Codex skills/plugin usage and live `2% skills context budget` warnings so default profile decisions are safe, reversible, and not based on assumptions.

**Architecture:** A repo-local Python audit script reads user-level Codex sessions, runtime logs, user-level plugin state, profile registries, manual notes, and repository guard outputs. It emits local JSON reports, sanitized Markdown summaries, preview-only candidate records, and embedded field contracts. Retention and pre-commit gates prevent raw audit artifacts or incomplete reports from becoming commit evidence.

**Tech Stack:** Python audit CLI, JSON report schema, sanitized Markdown renderer, SQLite runtime-log reader, Codex session JSONL reader, profile registry reader, manual-note parser, privacy redactor, output-retention checker, final-review state/precheck/decision-record checkers, pre-commit update/archive checker, CI manifest, OpenSpec guard.

---

## 0. Review conclusion

The plan is active and remains audit-only. This Comet-style refactor does not authorize a hard-load/profile apply and does not change the implementation boundary: existing script, checker, report-contract, retention, and candidate-preview rules remain the source of truth for execution. The refactor makes the plan easier to execute by separating governance principles, runtime/data-source architecture, CLI contracts, field contracts, implementation slices, task-level backlog, local integration, acceptance evidence, and long-running monitoring items.

A clean Codex startup after `soft-load` is useful evidence that startup pressure improved, but it is not proof that live-turn skills-budget warnings cannot reappear. Live warnings must be triaged through the audit script, not by deleting plugin cache or prematurely shrinking the default profile.

Cadence finalization: the original 30-day observation window is locked to 2026-05-16 through 2026-06-15. The standard scheduled audit run count is Day 0 baseline once, weekly 7-day evidence four times, and Day 30 final evidence once. Warning triage is event-driven and has no fixed repeat count. After 2026-06-15, any additional runs are post-final monitoring evidence and must not extend the original audit window or authorize profile apply.

Completeness review:

| Check item | Verdict | Plan location |
| --- | --- | --- |
| Live-turn warning explanation | Complete | Sections 3, 10 |
| Soft-load / hard-load / vendor-cache boundary | Complete | Sections 3, 10 |
| Evidence levels and decision thresholds | Complete | Section 4 |
| Audit-only safety and no profile apply | Complete | Sections 3, 10 |
| JSON report field contract | Complete | Section 7 |
| Privacy, retention, and output gates | Complete | Section 9 |
| Candidate preview and rollback path | Complete | Section 10 |
| Concrete implementation backlog | Complete | Section 12 |
| Long-running monitoring items | Still open by design | Section 17 |

## 1. Goal and non-goals

This plan defines a 30-day audit-only process so later profile decisions are evidence-based and do not accidentally make useful plugin skills dormant.

The audit answers four questions:

1. Which skills/plugins have strong usage evidence in the last 30 days?
2. Which modules were only mentioned but not actually read or invoked?
3. When and where did the `2% skills context budget` warnings occur?
4. Which capabilities should be always-on, project hard-load, soft-load on demand, or kept only in the `full` troubleshooting profile?

Non-goals:

- Do not apply a hard-load profile during the 30-day audit.
- Do not edit user-level Codex `config.toml` as part of an audit report run.
- Do not bulk-edit vendor/plugin `SKILL.md` files to reduce warning pressure.
- Do not treat disabled plugins as deleted; dormant capabilities must remain restorable.
- Do not use weak mentions or static registry entries as apply evidence.
- Do not publish raw audit JSON, raw transcripts, private paths, or vendor cache content.

## 2. Comet workflow mapping

This plan uses Comet as a control model without turning the audit into a profile-apply workflow.

| Comet focus | Audit interpretation | Exit evidence |
| --- | --- | --- |
| Open / Initiating | Freeze the audit target: skills-budget warning pressure and usage evidence. | Baseline command, data-source list, audit-only safety statement. |
| Design / Planning | Define evidence levels, field contracts, privacy boundaries, and decision thresholds. | This plan plus matching bilingual companion. |
| Build / Executing | Implement or refine audit script/checkers/tests in small local branches. | Local commits, tests, field contracts, and guard outputs. |
| Verify / Controlling | Run reports, retention checks, precommit update/archive checks, CI, and local MR review. | Passing report field contract and gate outputs. |
| Archive / Closing | Close or candidate-gate the audit after the real observation window. | `closed-no-change` or preview-only profile candidate evidence. |
| Monitoring | Handle live warnings, missed weekly reports, privacy failures, and exceptions. | Narrow triage report, cadence markers, pause/closure blockers, or rollback plan. |

Monitoring is not a sixth implementation phase. It is the control loop that can return the audit to planning or execution when evidence, privacy, warning pressure, or cadence changes.

## 3. Runtime governance principles

The `Exceeded skills context budget of 2%` warning is not guaranteed to appear only when the Codex process starts. In live sessions, the runtime may rebuild the model-visible skills surface when preparing a turn, resuming a thread, repacking context, or applying context truncation. A clean startup therefore does not prove that later turns cannot emit the warning.

`soft-load` does not mutate the startup-visible skills list and does not restore skills that were omitted from the model-visible list by the 2% budget. It only reads task-relevant SKILL.md or reference files into normal conversation context. Therefore:

- soft-load is a current-session remediation and on-demand knowledge loading path;
- hard-load/profile apply changes the plugin/skills surface for the next launch or resume;
- the default profile should not be reduced to `core-dev` without usage evidence;
- `company-ops`, `market-research`, `web-saas`, `customer-comms`, and `creative-content` should be observed for one month before deciding whether they are always-on, project-scoped, or on-demand only.

During the 30-day audit, do not run `set_plugin_profile.ps1 <module> -Apply` by default. Allowed actions:

- `load_module.ps1 <module> -Json` soft-load;
- `set_plugin_profile.ps1 <module> -Json` preview;
- read inventory and session/log data;
- generate local audit reports.

Forbidden actions:

- deleting plugin cache to reduce warnings;
- bulk-editing vendor/plugin `SKILL.md` files;
- applying hard-load without explicit approval;
- treating capabilities with no 30-day strong evidence as useless;
- treating disabled plugins as deleted. Disabled means dormant and restorable.

If a session emits another `2% skills context budget` warning, that does not mean soft-load failed. The runtime is still constructing the model-visible skills surface for the turn, while soft-load is outside that budget surface. Soft-load answers "how do we read needed task knowledge now," not "how do we shrink the global automatic visible list."

## 4. Evidence model

### 3.1 Strong evidence

Strong evidence can support keeping or profile-gating a capability:

- the assistant explicitly announced `Using skill: xxx` or `Using skill: xxx / Chinese skill announcement`;
- a session read a `SKILL.md` file;
- a plugin helper such as `load_module.ps1 <module>` or `set_plugin_profile.ps1 <module>` was invoked;
- a plugin/MCP/tool surface was invoked;
- logs contain a concrete budget warning that can be tied to a session or turn.

### 3.2 Medium evidence

Medium evidence means a capability may be needed but is not enough by itself to make it always-on:

- the user explicitly requested a plugin family such as Gmail, Slack, Twilio, Figma, Vercel, Cloudflare, or Notion;
- the task clearly belongs to a module such as `web-saas`, `company-ops`, `market-research`, `customer-comms`, or `creative-content`;
- project history says browser/web capabilities must be preserved.

### 3.3 Weak evidence

Weak evidence is only trend context:

- a plugin name appears in docs or logs;
- the model discussed a plugin without reading, invoking, or announcing it;
- a static registry lists the plugin.

After 30 days, decide using the following rules. All thresholds are based primarily on strong evidence; weak evidence can only explain trends.

| Measurement | Default threshold | Meaning |
| --- | --- | --- |
| Frequent strong evidence | 30-day `strong_helper_calls + strong_skill_path_reads >= 10`, or >= 3 per week for two consecutive weeks | Candidate for the default profile, after confirming cross-project utility |
| Low-frequency strong evidence | 1-9 strong-evidence events in 30 days | Keep soft-load / hard-load profile, but not always-on |
| Project-specific strong evidence | Evidence is concentrated in one project, directory, or task type | Use a project or task profile, not the global default |
| High warning severity | 7-day `budget_warning_count >= 3`, or `All skill descriptions were removed` appears | Prefer a smaller default profile and avoid keeping `full` always-on |
| Medium warning severity | Any 30-day warning, but fewer than 3 in the last 7 days | Continue audit and interpret with task context |
| No strong evidence | 0 strong-evidence events in 30 days | Remove from default candidates, but keep a restore path |

| Evidence | Decision |
| --- | --- |
| Frequent strong evidence and cross-project utility | Keep in the default profile |
| Low-frequency strong evidence but business-critical | Keep as soft-load and hard-load profile, not always-on |
| Project-specific strong evidence | Use a project profile such as `browser`, `web-saas`, or `company-ops` |
| Medium evidence only | Keep the module, but do not make it always-on |
| Weak evidence only | Do not use as apply evidence |
| No 30-day strong evidence but strategic | Dormant, not deleted, with restore path |
| No 30-day strong evidence and non-strategic | Remove from default profile only through profile preview/apply |

## 5. Runtime and data-source architecture

Runtime responsibilities:

- `tools/audit_codex_skills_usage.py` collects evidence and emits JSON/Markdown reports.
- `tools/skills2cli.py audit warnings` provides compact, sanitized foreground warning triage over both session JSONL and `logs_2.sqlite`; it is read-only and does not mutate Codex config, plugin cache, hard-load profiles, or skill bodies.
- `tools/check_skills_audit_output_retention.py` proves raw audit artifacts stay local-only.
- `tools/check_skills_audit_final_review_state.py` verifies the final human-review, closure, candidate, and apply-gate state without mutating config or profiles.
- `tools/check_skills_audit_final_review_precheck.py` verifies machine-level precheck evidence for final-summary noise and manual-conflict items while keeping human-review, candidate, and profile-apply gates closed.
- `tools/check_skills_audit_human_review_decision_record.py` verifies optional future human-review decision records: no record is a valid pending state, exactly one allowed outcome is required when a record exists, candidate artifacts before review are blocked, preview-only candidate decisions require `target_profile` plus rollback/validation/candidate-review notes, profile apply remains unauthorized unless a later receipt exists, and raw paths/secrets/transcripts/log excerpts are rejected.
- `tools/check_skills_audit_cadence_contract.py` verifies the locked repeat count, weekly frequency, original end date, event-triggered warning-triage rule, and post-final monitoring-only boundary.
- `tools/check_precommit_update_archive.py` proves existing-file update review and OpenSpec archive gates were checked before local commits.
- `tools/run_openspec_guard.py` aggregates repository-level guard evidence.
- Tests under `test/` and entries in `tools/ci/ci_test_manifest.json` keep the audit behavior reproducible.

The audit helper is evidence collection, not an apply engine. It can prepare preview-only records and recommendations, but it must not mutate Codex config, plugin cache, or hard-load profiles.

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 30 --json --output .\.tmp\skills-usage-audit-latest.json
```

Default sources:

- `C:\Users\lenovo\.codex\sessions/**/*.jsonl` - session transcripts used to detect explicit skill announcements, SKILL.md reads, and foreground warning text for compact `skills2cli` triage.
- `C:\Users\lenovo\.codex\logs_2.sqlite` - runtime log database used to count skills-budget warnings; `skills2cli audit warnings` now reads it as a second sanitized source so live-turn warnings are not missed when they appear only in runtime logs.
- `C:\Users\lenovo\.codex\config.toml` - user-level plugin enabled-state source for audit-only reporting.
- `C:\Users\lenovo\.codex\skills\plugin-modules\references\profiles.json` - module registry used to aggregate plugin evidence by profile.

## 6. CLI contract and cadence commands

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 0 --baseline --json --output .\.tmp\skills-usage-baseline-2026-05-16.json
```

The baseline records enabled plugins, profile modules, warning counters, and inventory summary. It does not mutate `config.toml`.


Canonical cadence contract:

| Item | Locked value | Execution meaning |
| --- | --- | --- |
| Observation window | `2026-05-16` through `2026-06-15` | The original 30-day audit window is closed and must not be extended by later monitoring runs. |
| Scheduled repeat count | `6` total scheduled audit runs | 1 Day 0 baseline, 4 weekly evidence runs, and 1 Day 30 final evidence run. |
| Scheduled frequency | Day 0 once, then every 7 days for weekly evidence, then Day 30 once | Weekly evidence dates are 2026-05-23, 2026-05-30, 2026-06-06, and 2026-06-13; final evidence is 2026-06-15. |
| Warning triage frequency | Event-triggered only | Run a narrow-window triage only after a new `2% skills context budget` warning; no fixed repeat count. |
| Post-final runs | Monitoring evidence only | Runs after 2026-06-15 can update review-pending evidence or warning triage, but cannot reopen the 30-day window or authorize profile apply. |
| Apply boundary | Not authorized by cadence | Profile apply still requires a later explicit `approved-to-apply` authorization. |

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 7 --json --output .\.tmp\skills-usage-audit-7d.json
```

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 30 --json --output .\.tmp\skills-usage-audit-30d.json --summary-output .\.tmp\skills-usage-audit-30d-summary.md --manual-notes .\.tmp\skills-usage-audit-notes-YYYY-MM-DD.md
```

`--summary-output` writes the sanitized Markdown decision summary. It is review evidence only and must not mutate `config.toml`, plugin cache, or hard-load profiles.

To prepare a later reversible candidate without applying it, add `--target-profile`, `--candidate-output`, `--summary-reviewed`, and optionally `--candidate-summary-output`:

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 30 --json --output .\.tmp\skills-usage-audit-30d.json --summary-output .\.tmp\skills-usage-audit-30d-summary.md --summary-reviewed --target-profile core-dev --candidate-output .\.tmp\skills-profile-candidate.json --candidate-summary-output .\.tmp\skills-profile-candidate.md
```

Candidate output is always `approval_state=preview-only` and must not modify `config.toml`, plugin cache, or hard-load profiles. `--candidate-output` or `--candidate-summary-output` must be paired with an explicit `--target-profile`; the script must not infer a target profile from the current profile, filename, or generic continuation. Without `--summary-reviewed`, a 30-day audit window, `--output`, `--summary-output`, or `--target-profile`, the candidate generation gate is recorded as blocked.

The script must still support `--json` on non-UTF-8 Windows consoles. If stdout cannot encode characters such as `[WARNING]`, stdout may fall back to JSON-safe backslash escapes; the `--output` report file must still preserve the original UTF-8 text.

Regression tests must cover:

- stdout fallback for `[WARNING] Exceeded skills context budget of 2%`;
- explicit skill-announcement detection for Chinese `Chinese skill announcement prefix` and English `Using skill:`;
- extraction of `omitted_additional_skills` and `all_descriptions_removed` from `logs_2.sqlite` budget warnings;
- `skills2cli audit warnings --since ... --json` must report separate `sessions_jsonl` and `logs_2.sqlite` sources, aggregate counts, redact private paths/secrets, expose current `frontmatter_compatibility.invalid_total`, and keep `raw_log_paths_retained=false` plus `raw_skill_bodies_retained=false`;
- `plugins: "all_known_plugins"` in the `full` profile must not be split into individual characters;
- the script must fall back to `tools/skill_sources/plugin-modules/references/profiles.json` when the user-level plugin-modules profile is absent.

Use a fixed cadence so the one-month audit does not drift. This cadence is now locked as a completed original audit window, not an open-ended loop.

| Cadence item | Date or trigger | Repeat count | Command | Output file | Purpose |
| --- | --- | ---: | --- | --- | --- |
| Day 0 baseline | 2026-05-16 | 1 | `--days 0 --baseline` | `.tmp/skills-usage-baseline-YYYY-MM-DD.json` | Freeze initial enabled plugins, inventory, and warning state |
| Weekly audit | 2026-05-23, 2026-05-30, 2026-06-06, 2026-06-13 | 4 | `--days 7` | `.tmp/skills-usage-audit-7d-YYYY-MM-DD.json` | Detect new live-session warnings and module trends |
| Late weekly recovery | Only when a weekly run is missed | Event-driven, no fixed count | `--days 7 --late-run --missed-weekly-runs N` | `.tmp/skills-usage-audit-7d-late-YYYY-MM-DD.json` | Preserve an explicit cadence-drift marker instead of fabricating the missed run |
| Day 30 final audit | 2026-06-15 | 1 | `--days 30` | `.tmp/skills-usage-audit-30d-YYYY-MM-DD.json` | Build the evidence package for default-profile decisions |
| Warning triage | After each new `2% skills context budget` warning | Event-driven, one narrow run per new warning | `--warning-triage --days 1` or `--warning-triage --since` | `.tmp/skills-usage-warning-triage-YYYY-MM-DD.json` | Locate whether the warning came from current-session repacking |
| Final human review | After the Day 30 summary exists | 1 decision review | Review sanitized final summary and decision template | Tracked sanitized review record if a decision is made | Choose `summary-reviewed + closed-no-change`, `summary-reviewed + preview-only candidate`, or `review-pending + continue monitoring` |

Standard scheduled audit repeats are therefore fixed at 6 runs total: 1 baseline, 4 weekly runs, and 1 final 30-day run. The final human review is a separate decision step, not another audit run. Warning triage and late recovery are exception/event-triggered paths and are not assigned a fixed repeat count.

The original audit end date is 2026-06-15. Runs after that date are post-final monitoring only: they may update review-pending evidence or warning-triage evidence, but they must not move the original end date, restart the 30-day clock, mark the summary reviewed, generate a profile candidate, or apply a profile without an explicit later decision.

Reports under `.tmp/` are not committed by default. If long-term evidence is needed, commit only a sanitized Markdown summary, not full session transcripts, tokens, private paths, or vendor cache content.

`--warning-triage` is an audit-only marker for a post-warning follow-up run. It must use a narrow window: either `--days 1` or an explicit `--since` value that covers the warning time. If `--warning-triage` is used with a broad window such as `--days 7` or `--days 30`, the generated report must set `warning_triage.status=blocked`, add `warning_triage_window_not_narrow`, and keep `audit_state.reason=warning_triage_window_too_broad`. The triage report must also summarize `Skipped loading` warning counts, expose bounded sanitized skipped-loading sample excerpts, and record a review policy to capture the source first without bulk-editing vendor cache. `warning_triage.status` may only be `not_requested`, `blocked`, `log_source_unavailable`, `warning_found`, or `no_warning_found_in_triage_window`; `blockers` may only contain known string blockers, currently `warning_triage_window_not_narrow`. This marker must not edit `config.toml`, plugin cache, or hard-load profiles.

During the one-month audit, handle cadence drift or data-source failures with the table below so incomplete evidence is not treated as a final decision package.

| Drift or exception | Recovery action | Disallowed action |
| --- | --- | --- |
| A weekly summary was missed | Run `--days 7` immediately and mark `late_run: true` in the summary | Fabricate historical reports to fill the cadence |
| A warning was not triaged promptly | Run `--days 1`; if more than 24 hours passed, also run `--since` across the warning time | Decide from memory whether soft-load failed |
| `logs_2.sqlite` is missing or unreadable | Keep `log_evidence.available=false` in the report and use session transcripts only as supporting evidence | Treat zero logged warnings as proof that no warning happened |
| Session transcripts are incomplete or privacy-sensitive | Commit only aggregate fields and a sanitized summary; keep raw JSON local under `.tmp/` if needed | Commit full transcripts, tokens, or private paths |
| A report misses required contract fields | Fix the script or rerun the report before profile decisions | Use an incomplete report for hard-load/profile apply decisions |
| Explicit-skill false-positive noise contains path fragments, secrets, or long mojibake text | Fix the script to redact and truncate, add regression tests, and rerun until the `noise_review` contract passes | Retain raw noise tokens in long-term reports or count them as strong evidence |
| An urgent task genuinely needs a plugin during the audit | Allow task-scoped soft-load or preview; require explicit approval and an exception note for hard-load | Use the urgent task as a reason to end the 30-day audit early |

Day 30 must not ship only raw JSON. It must produce a sanitized Markdown summary that is reviewable by a human and includes at least:

1. Audit window: start/end time, missed weekly runs, and late-run status.
2. Current configuration surface: enabled/disabled/unknown plugin counts, `current_profile.inferred_profile`, exact module matches, and whether manual review is required.
3. Warning conclusion: 30-day warning count, 7-day warning count, highest severity, and whether `All skill descriptions were removed` appeared.
4. Evidence table: per-module strong evidence count, `medium_evidence_rationale`, weak-evidence count, `cross_project_utility`, and the recommendation.
5. Noise review: list obvious false-positive tokens removed from evidence, such as `and`, `from`, or `draft`, state they were not counted as strong evidence, and show the retained-token privacy fields: `raw_noise_tokens_retained`, `max_noise_token_length`, and `token_privacy_policy`. The Markdown summary must render a bounded sanitized sample list and must render `none` when no tokens were removed.
6. Decision recommendation: render advisory buckets for default/project profile review candidates, on-demand soft-load modules, manual-review medium/weak modules, dormant-but-restorable modules, or `full` troubleshooting profile only. These buckets are review inputs only and must not apply a profile.
7. Manual conflict review: render whether manual notes contain exceptions or approved hard-load exceptions, the conflict/exception count, the non-override policy, and the required disposition before any profile decision.
8. Risks and restore path: if a plugin is disabled or removed from the default profile, document how to restore it, which helper to use such as `set_plugin_profile.ps1 -RestoreLatest -Apply`, and whether a `codex-ohmy` restart/new session is required.
9. Non-action list: explicitly state what the report did not do, such as not modifying `config.toml`, not editing plugin cache, and not performing hard-load apply.

Only when this summary and the JSON field contract both pass may the work move into hard-load/profile apply discussion.

The script primarily captures strong evidence and log evidence. Medium evidence, business criticality, project specificity, and urgent exceptions need manual notes. Manual notes must be sanitized Markdown, preferably `.tmp/skills-usage-audit-notes-YYYY-MM-DD.md`, and are not committed by default. If long-term evidence is needed, commit only a sanitized summary excerpt.

Each manual note must include at least:

| Field | Required | Description |
| --- | --- | --- |
| `time` | Yes | Note time or task time |
| `project` | Yes | Project or repository name; do not include sensitive customer details |
| `task_type` | Yes | For example `web-saas`, `company-ops`, `customer-comms`, or `creative-content` |
| `requested_capability` | Yes | Capability explicitly requested by the user or clearly required by the task |
| `evidence_level` | Yes | `medium`, `exception`, or `noise_removed` |
| `reason` | Yes | Why the capability matters, or why a token was treated as a false positive |
| `action_taken` | Yes | `none`, `soft-load`, `preview`, or `approved hard-load exception` |
| `restore_or_followup` | No | How to restore, re-review, or add script filtering later |

Manual notes cannot override script evidence. If manual judgment conflicts with the JSON report, or if the note records an `exception` / `approved hard-load exception`, the JSON report must set `manual_evidence.conflict_review.status=manual_conflict_or_exception_review_required` and the 30-day summary must list the conflict/exception count, non-override policy, and required disposition.

Manual note source paths are readable for local audit execution but are not retainable as raw evidence. Any path stored in `manual_evidence.invalid_notes` or candidate source references must be redacted and bounded before report retention, and the field contract must fail if manual evidence still contains raw private paths, secret assignments, standalone tokens, or a marker that source paths were retained. Sanitized Markdown summaries must also show `source_paths_retained`, `max_path_length`, and `path_privacy_policy` so human reviewers can verify the source-path privacy gate without opening raw JSON.

## 7. JSON report field contract

The report generated by `--json` and `--output` must include at least these top-level fields. If any field is missing, the report must not be used for profile decisions.

| Field | Purpose | Decision impact |
| --- | --- | --- |
| `schema_version` | Report structure version | Allows later scripts to parse compatibly |
| `generated_at` | Report generation time | Shows whether the report is stale |
| `audit_state` | Audit state-machine state, reason, next action, and profile-apply allowance | Prevents incomplete or paused audit state from entering profile decisions |
| `audit_window` | `since` / `until` / `days` | Prevents 30-day decisions from using the wrong window |
| `safety` | Config mutation, plugin cache edit, and hard-load apply flags | Must prove audit-only behavior |
| `config_summary` | enabled / disabled / unknown plugins plus `current_profile` inference | Shows whether the current profile surface is too large and whether it exactly matches a known module |
| `inventory_summary` | user/repo/plugin skill counts | Helps locate 2% budget pressure |
| `log_evidence` | budget warning, 7-day warning count, sanitized recent budget-warning sample excerpts, `All skill descriptions were removed`, omitted-skill maximum, and skipped-loading evidence | Shows whether warnings still occur during live turns and whether severity crosses the plan threshold without forcing reviewers to open raw log databases |
| `warning_severity` | Warning pressure level, reason, and handling action derived from `log_evidence` | Makes warning pressure a decision-critical profile field so reviewers do not rely on raw warning counts alone or miss `full` / oversized-profile risk |
| `warning_triage` | Post-warning triage marker, narrow-window gate, warning counts in the triage window, and recommended follow-up | Prevents broad weekly/monthly reports from being mistaken for a turn-level warning triage |
| `session_evidence` | explicit skills, SKILL.md reads, helper calls, tool calls | Feeds strong/medium/weak evidence classification |
| `manual_evidence` | sanitized manual-note counts, invalid-note validation, and medium/exception/noise summaries | Preserves human review evidence without retaining raw transcripts |
| `noise_review` | sanitized, truncated explicit-skill noise tokens, false-positive counts, and strong-evidence exclusion policy | Prevents false-positive tokens, path fragments, or mojibake text from becoming strong evidence or retained raw evidence |
| `script_capability_boundaries` | reliable coverage, human-review boundaries, known limitations, script-enhancement triggers, and the stable tool-call alias registry | Prevents the audit helper from being treated as an omniscient source of truth and keeps alias evidence visible as medium-only evidence |
| `output_retention` | status from `tools/check_skills_audit_output_retention.py`, including `.tmp/` local-only policy, raw JSON local-only policy, long-term evidence format, and violation count | Prevents a report from hiding whether raw audit artifacts are accidentally retained in Git |
| `precommit_update_archive` | status from `tools/check_precommit_update_archive.py`, including existing-file update review, completed OpenSpec archive gate, error count, warning count, changed path count, and active change review count | Prevents the audit report from bypassing the repository rule that existing files must be checked for update/archive needs before local commits |
| `runtime_paths` | sanitized runtime path placeholders and path-kind labels for repo root, Codex home, and `config.toml`, with `raw_paths_retained=false` | Prevents JSON and Markdown reports from retaining raw local user paths while still showing which runtime inputs were scanned |
| `module_evidence` | profile-module-level strong, medium-rationale, weak, and cross-project review fields | Produces profile decision candidates without treating medium evidence as strong evidence |
| `decision_recommendation` | advisory decision buckets derived from module evidence | Lets reviewers see profile-review, on-demand, manual-review, and dormant modules without allowing profile apply |
| `cadence_review` | late-run and missed-weekly-run markers | Prevents cadence drift from being hidden in a 30-day decision summary |
| `recommendations` | Audit recommendations | Advisory only; never auto-apply |

The audit script must also validate runtime path privacy: top-level `root`, top-level `codex_home`, `config_summary.config_path`, and `runtime_paths.root/codex_home/config_path` MUST NOT contain raw Windows, POSIX home, UNC, token, cookie, or secret-bearing paths. Reports MUST retain placeholders such as `[REPO_ROOT]`, `[CODEX_HOME]`, and `[CODEX_HOME]/config.toml` instead of raw absolute paths, and `runtime_paths.raw_paths_retained` MUST remain `false`.

The audit script must compute a `field_contract` result for every generated report. The result records `status`, `passed`, required fields, missing fields, invalid field types, safety violations, and decision-critical nested-field violations. The `audit_state` contract must require `state`, `reason`, `next_action`, and `profile_apply_allowed` so reports cannot lose state-machine context. It must also reject unknown audit states, reject `profile_apply_allowed=true` or non-false values, and require any state blocker field (`close_blockers`, `candidate_blockers`, `summary_review_blockers`, `pause_blockers`, or `warning_triage_blockers`) to be a list of strings when present. Sanitized Markdown summaries must also render the audit state's next action, profile-apply allowance, and any blockers from those fields, using `none` when no blocker is present. The `warning_triage` contract must require `requested`, `status`, `blockers`, `window_policy`, `window_ok`, `budget_warning_count`, `skipped_loading_count`, `recent_skipped_loading_samples`, `recent_skipped_loading_sample_excerpts`, `skipped_loading_review`, and `recommended_action` so a warning follow-up report cannot omit its triage state, narrow-window policy, sanitized skipped-loading samples, skipped-loading source review, or next action. Its value-level contract must also reject unknown `status` values, any `window_policy` other than `use_days_1_or_since_for_warning_triage`, any `skipped_loading_review` outside `none` / `record_source_and_do_not_edit_vendor_cache_without_authorization`, non-string or unknown blockers, `status=blocked` without blockers, blockers on a non-`blocked` status, negative warning or skipped-loading count fields, and skipped-loading sample excerpts that are not strings or still contain raw private paths, secrets, or tokens. A report with `field_contract.status != passed` is incomplete evidence: it must be fixed or regenerated before any profile decision. Candidate generation must require the report's embedded `field_contract`; reports from older scripts or manually edited reports with a missing or stale embedded contract must be blocked until regenerated.
The `log_evidence` contract must require `budget_warning_count`, `last_7d_budget_warning_count`, `recent_budget_warning_samples`, and `recent_budget_warning_sample_excerpts`. Count fields must be non-negative integers, and each retained budget-warning excerpt must be a sanitized string with no raw private path, secret assignment, cookie/access-token value, or standalone secret token. Sanitized Markdown summaries and human stdout must render the sample count plus bounded excerpts, using `none` when no sample exists, so reviewers can confirm the warning shape without opening `logs_2.sqlite`.

The `warning_severity` contract must require `level`, `reason`, and `recommended_action`. `level` may only be `unknown`, `high`, `medium`, or `none`; `reason` and `recommended_action` must be sanitized strings with no raw private paths, secret assignments, cookie/access-token values, or standalone secret tokens. Sanitized Markdown summaries and human stdout must render severity level, reason, and handling action, and Markdown must explicitly render `Severity recommended action`; the field contract must expose `warning_severity_violations` as a separate violation group. Candidate generation and profile decisions must not use a report whose warning severity is missing, has an unsupported level, or retains unsanitized text.

Default human stdout and sanitized Markdown summaries must also render `field_contract` details, not only `status`. They must at least show `passed`, blocker count, required-field count, missing-field count, invalid-type count, whether an embedded contract is required, and violation-group counts for safety, audit_state, log_evidence, warning_severity, warning_triage, cadence_review, manual_evidence, noise_review, script_capability_boundaries, output_retention, precommit_update_archive, runtime_paths, module_evidence, decision_recommendation, and embedded field contract. This lets reviewers locate the failing contract group from terminal output or the sanitized summary without opening raw JSON.
The `noise_review` contract must require `raw_noise_tokens_retained=false`, `max_noise_token_length`, `token_privacy_policy`, and sanitized `explicit_skill_noise_removed`. Noise tokens must redact private paths, secrets, cookies, and tokens before entering reports, then be truncated to a fixed length; if raw private paths, secrets, or overlong tokens remain, the field contract must fail.
The `script_capability_boundaries` contract must require `policy`, `reliable_coverage`, `human_review_required_for`, `enhancement_triggers`, and `stable_tool_call_alias_registry`. The three boundary lists must be present and non-empty so a report cannot imply that the audit helper is an omniscient source of truth. The stable alias registry must expose `policy`, `evidence_level`, `counts_as_strong_evidence`, `plugin_aliases`, and `module_aliases`; it must declare `evidence_level=medium` and `counts_as_strong_evidence=false`, and each alias target must contain a non-empty list of stable tool-call prefixes. Markdown summaries must render the registry policy and alias targets so 30-day reviewers can see which stable tool names were aggregated as medium evidence without opening raw JSON.
The `output_retention` contract must require `status`, `ok`, `checker`, `tmp_outputs_local_only`, `raw_audit_json_local_only`, `long_term_evidence_format`, and `violation_count`. It must pass only when the retention checker itself passes, `.tmp/` outputs and raw audit JSON are marked local-only, and the long-term evidence format is `sanitized_markdown_summary`.

The `precommit_update_archive` contract must require `status`, `ok`, `checker`, `before_local_git_commit`, `review_existing_files_for_required_updates`, `archive_completed_openspec_changes_before_commit`, `error_count`, `warning_count`, `changed_path_count`, and `active_change_review_count`. It must pass only when the pre-commit update/archive checker itself passes and the report explicitly shows that existing-file update review and completed OpenSpec archive gates are enabled; if the checker fails or is unavailable, the audit report must not be treated as local-commit evidence.
The `cadence_review` contract must require `late_run`, `missed_weekly_runs`, and `weekly_report_review`; `missed_weekly_runs` must be either `null` or a non-negative integer, and `late_run=true` must include an explicit missed-run count. The sanitized Markdown summary must render these cadence fields in the audit-window section so a 30-day reviewer can see cadence drift without opening raw JSON.
The `module_evidence` contract must validate every row before it can feed `decision_recommendation` or candidate generation. Each row must include module name, plugin list, strong-helper counts, strong skill-path counts, strong total, default-candidate threshold, mapped-tool medium-evidence count and policy, medium-evidence rationale, weak mentions, cross-project utility, and recommendation. Numeric counts must be non-negative integers, `strong_total` must equal helper calls plus skill-path reads, plugin entries must be strings, mapped tool calls must remain medium evidence, cross-project utility must require manual review, and recommendations must stay within the approved advisory values. The recommendation must also match the threshold rule: `strong_total >= default_candidate_threshold` is a profile-review candidate, `0 < strong_total < threshold` stays on-demand, `strong_total == 0` with weak mentions is mentioned-only, and no strong or weak evidence stays dormant/restorable.
The `decision_recommendation` contract must require advisory-only status, the non-apply policy, `profile_apply_allowed=false`, the four bucket lists (`profile_review_candidates`, `on_demand_soft_load`, `manual_review_medium_or_weak`, and `dormant_restorable`), and matching `bucket_counts`. If the buckets are missing, wrong-typed, contain non-string module names, mark profile apply as allowed, or have stale counts, the field contract must fail before any profile decision or candidate generation.
The `manual_evidence.conflict_review` contract must require status, policy, conflict/exception count, disposition-required flag, and disposition text. Manual exception notes and approved hard-load exception notes must be surfaced as `manual_conflict_or_exception_review_required` so a 30-day reviewer cannot miss manual evidence that conflicts with or exceeds script evidence.

## 8. Audit state machine and stop conditions

To prevent month-long audit drift, the audit itself must have explicit state. The state describes the audit workflow only; it does not mean a plugin/profile has been applied.

| State | Meaning | Allowed actions | Forbidden actions |
| --- | --- | --- | --- |
| `planned` | The plan exists, but the Day 0 baseline has not been generated | Review the plan and run baseline preview | Claim 30-day evidence already exists |
| `running` | Day 0 baseline exists and 30-day evidence is being collected | Weekly reports, warning triage, manual notes, script fixes | Hard-load apply unless separately and explicitly approved |
| `paused` | Missing data source, privacy issue, or script defect paused the audit | Fix data sources, add tests, rerun reports | Use missing paused-period data for final decisions |
| `ready-for-summary` | Day 30 has arrived and field contract, weekly reports, triage, and manual notes are mostly complete | Generate the sanitized 30-day Markdown summary | Directly modify the default profile |
| `summary-reviewed` | The 30-day summary has been human-reviewed and noise/conflicts are dispositioned | Create a profile apply candidate change gate | Skip rollback or validation planning |
| `apply-candidate` | A candidate change record exists and is still preview-only or awaiting approval | Preview, risk review, request explicit authorization | Treat generic "continue" as apply authorization |
| `closed-no-change` | 30-day evidence does not support changing the default profile | Keep dormant/soft-load paths and close this audit round | Extend the same audit round just to force a result |
| `closed-with-candidate` | This audit round is closed and produced an approval-pending candidate | Move to a separate profile apply change | Execute configuration changes inside the audit plan file |

The script must be able to record closure states without applying any profile change:

- `--planned-audit` records `planned` before the Day 0 baseline is generated and blocks profile-apply candidate generation with `audit_state_planned`. It exists only to make the pre-baseline plan state explicit.
- `--pause-audit data-source-missing|privacy-review|script-defect` records `paused` and blocks profile-apply candidate generation with `audit_state_paused`. Use it only to make an audit interruption explicit while the data source, privacy review, or script defect is fixed and the report is rerun.
- `--summary-reviewed` with an elapsed 30-day window plus both `--output` and `--summary-output` source-report paths records `summary-reviewed` when no candidate or closure flag is requested. If the source-report paths are missing, the report stays `ready-for-summary` and records `source_report_paths_missing`.
- `--close-audit no-change` may record `closed-no-change` only when the 30-day window has elapsed, `--summary-reviewed` is present, and both `--output` and `--summary-output` source-report paths are present.
- `--close-audit with-candidate` may record `closed-with-candidate` only when the same evidence gates pass, a candidate output path is requested, and `--target-profile` is present.
- If these gates are not met, the report must remain `running` or `ready-for-summary` and list closure blockers such as `audit_window_shorter_than_30_days`, `summary_not_marked_reviewed`, `source_report_paths_missing`, `candidate_output_missing`, or `target_profile_missing`.

Stop conditions:

- after `closed-no-change`, the next step is only a new audit round if needed or continued soft-load usage; do not keep appending to this round;
- after `closed-with-candidate`, follow-up work must move into the profile apply candidate change and must not treat this audit plan as the execution surface;
- if two consecutive reviews add only explanatory prose and no verifiable rule, field, state, or test requirement, stop expanding the plan and commit the current refined result;
- audit state changes must be recorded in the 30-day summary or candidate change record, not only in chat context.

## 9. Privacy, retention, and output gates

The usage audit reads user-level Codex sessions, logs, and configuration state, so "readable data" and "retainable data" must be managed separately.

| Data source | Allowed read purpose | Retainable content | Forbidden retained or external content |
| --- | --- | --- | --- |
| `sessions/**/*.jsonl` | Identify explicit skill announcements, `SKILL.md` reads, and helper calls | Aggregate counts, sanitized task type, sanitized project name | Full transcripts, private user input, tokens, secrets, customer information |
| `logs_2.sqlite` | Count budget warnings, skipped loading, and warning time windows | Warning counts, time windows, sanitized message excerpts | Full log database, raw messages containing paths/accounts/secrets |
| `config.toml` | Read plugin enabled/disabled/unknown state | Plugin-state summary and profile names | Full user-level configuration, credentials, unrelated settings |
| manual note files | Read sanitized human medium evidence, exceptions, and noise-removal notes | Parsed note fields, aggregate counts, redacted/bounded invalid-note source placeholders | Raw local note paths, raw manual-note files, secrets, customer information, raw transcripts |
| plugin/vendor cache | Count `SKILL.md` inventory or locate invalid skills | Skill counts, path categories, invalid-skill summary | Full vendor files or bulk-copied `SKILL.md` content |
| `.tmp/` audit report | Local temporary review | Local JSON and sanitized Markdown summary | Unsanitized reports committed to Git or sent to remotes |
| profile candidate records | Preview a reversible profile change after summary review | Candidate ID, sanitized source-report references, plugin diff, rollback path, validation plan | Raw absolute user paths, UNC shares, tokens, cookies, raw manual notes, raw transcripts |

Retention rules:

- Runtime paths retained in any report must use placeholders and kind labels only; raw repository, user home, Codex home, or user-level `config.toml` paths must not be retained in JSON, Markdown, or candidate records;
- `.tmp/*.json` is local temporary evidence by default and is not committed to Git;
- long-term evidence must be a sanitized Markdown summary only;
- before any report enters Git, verify it contains no API keys, access tokens, cookies, private customer names, or full local user-directory inventories;
- sanitized log `message_excerpt` values must preserve complete `[REDACTED_PATH]` and `[REDACTED_SECRET]` markers when truncated, instead of retaining ambiguous partial marker fragments;
- before any candidate record is written or rendered, verify `source_reports_privacy.status=passed` and treat any `raw_private_path`, `raw_secret_assignment`, or `raw_standalone_token` violation as a script defect;
- remote publication must not upload raw audit JSON as an attachment;
- if a generated report contains sensitive content, delete that local report and regenerate a sanitized summary instead of manually redacting the same report in place and continuing to use it.

Before any implementation related to `docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md` is committed to the local Git repository, the audit report must run and expose `tools/check_precommit_update_archive.py`. This turns the rule "check existing files for required updates and archive needs before local git commit" into script-visible evidence instead of transient chat context.

Report field requirements:

- the top-level report must contain `precommit_update_archive`;
- `precommit_update_archive.status` may only be `passed`, `failed`, or `unavailable`;
- `before_local_git_commit` must be `true` to show this is a pre-commit gate;
- `review_existing_files_for_required_updates` must be `true` to show existing-file update review is enabled;
- `archive_completed_openspec_changes_before_commit` must be `true` to show completed OpenSpec changes must be archived or explicitly deferred;
- `error_count`, `warning_count`, `changed_path_count`, and `active_change_review_count` must be non-negative integers;
- if the checker fails or is unavailable, `field_contract` must fail and block treating the audit report as commit-ready evidence.

The sanitized Markdown summary must render:

- pre-commit update/archive gate status;
- checker path;
- error count;
- whether existing-file update review is enabled;
- whether the OpenSpec archive gate is enabled;
- changed path count and active change review count.

This gate does not automatically edit files or archive changes, and it does not replace human judgment. It fails closed before commit so the operator must update files, archive completed changes, or record a compliant deferred-archive reason first.

Audit output retention is now script-backed by `tools/check_skills_audit_output_retention.py` and is part of `tools/run_openspec_guard.py` as `check_skills_audit_output_retention`.

The retention gate MUST fail before commit, local integration, or publication when either of these paths is tracked, staged, changed, or untracked in a commit-visible location:

- any `.tmp/` artifact, including `.tmp/skills-usage-audit-30d.json` even if it was forced into Git;
- raw Skills usage audit JSON whose filename starts with `skills-usage-audit`, `skills-usage-baseline`, `skills-usage-warning`, or `skills-usage-report`, even when it is outside `.tmp/`.

Long-term evidence MUST be a sanitized Markdown summary or another explicitly reviewed sanitized document. Raw JSON reports remain local working files for reproduction and review only. If a reviewer needs durable evidence, regenerate the Markdown summary from the raw JSON, review it for privacy, and commit the sanitized summary instead of the raw report.

Regression coverage lives in `test/check_skills_audit_output_retention.test.py` and MUST stay registered in `tools/ci/ci_test_manifest.json`. The guard JSON aggregation test also MUST include `check_skills_audit_output_retention` so the CI-visible guard order cannot silently drop the retention gate.

## 10. Profile candidate gate and rollback

After the 30-day audit, evidence that supports changing the default profile still must not be applied directly. First create a candidate change-gate record that turns the audit conclusion into a reversible configuration change.

The candidate record must include at least:

| Field | Description |
| --- | --- |
| `candidate_id` | Candidate change ID, for example `skills-profile-2026-06-core-dev-plus-browser` |
| `source_reports` | Sanitized references to the 30-day JSON report, sanitized Markdown summary, and manual-note summary |
| `source_reports_privacy` | Contract result proving the candidate record no longer contains raw private paths or secrets |
| `current_profile` | Current default profile and enabled-plugin summary |
| `target_profile` | Candidate target profile, or the profile name to create/update |
| `plugin_diff` | Plugins/modules to add, remove from default, or keep dormant |
| `evidence_basis` | Strong evidence, medium evidence, strategic retention, or warning pressure for each change item |
| `risk_review` | Capabilities that might be mistakenly disabled, affected projects, and restore cost |
| `rollback_path` | Helper command to restore the old profile and restart/new-session requirements |
| `validation_plan` | Preview, local check, startup validation, and warning retest steps |
| `approval_state` | `preview-only`, `approved-to-apply`, `applied`, or `rolled-back` |
| `candidate_record_contract` | Self-validation result for the retained candidate record shape, preview-only safety flags, privacy contract, rollback path, validation plan, and candidate gate structure |

Gate rules:

- the audit script may generate candidate JSON/Markdown via `--candidate-output` and `--candidate-summary-output`, but those outputs are preview records only;
- candidate generation must record a gate result that requires a 30-day audit window and `--summary-reviewed`;
- candidate generation must require source-report paths for the 30-day JSON report and sanitized Markdown summary, so a reviewed candidate cannot be detached from its review evidence;
- candidate generation must require an explicit `--target-profile`; if it is missing, the audit state stays `ready-for-summary`, records `target_profile_missing`, and any candidate preview must stay blocked rather than raising an unstructured exception or implying a usable target;
- candidate generation must require the report `audit_state.state` to be candidate-ready: `summary-reviewed`, `apply-candidate`, or `closed-with-candidate`; `planned`, `paused`, `running`, `ready-for-summary`, and `closed-no-change` must block candidate generation so ordinary summary flags or a no-change closure cannot be mistaken for profile-apply candidate authorization;
- candidate `source_reports` must be sanitized before JSON or Markdown candidate records are written; raw Windows paths, POSIX home paths, UNC shares, API keys, access tokens, cookies, and standalone secret tokens must be redacted;
- a candidate record must include `source_reports_privacy.status=passed`; if the privacy contract fails, the candidate must stay blocked until the report paths are regenerated or the sanitizer is fixed;
- candidate Markdown summaries must render the source-report privacy status and privacy violations/blockers, using `none` when there are no violations, so the preview record is self-reviewable without exposing raw source paths;
- candidate generation must also validate the report field contract and block with `field_contract:<reason>` when required top-level fields, audit-only safety flags, decision-critical nested fields, or the embedded `field_contract` itself are missing, stale, or invalid;
- candidate generation must also attach and render a `candidate_record_contract`; if required candidate fields, preview-only safety flags, `source_reports_privacy.status=passed`, `candidate_generation_gate.allowed/blockers`, `rollback_path.restore_command` / `restart_required`, or a non-empty `validation_plan` are missing or invalid, the contract must fail and the candidate must not be treated as apply-ready evidence. Candidate Markdown must render the candidate contract's passed flag, blocker count, required/missing/invalid-type field counts, preview-safety violation count, source-report-privacy violation count, gate-shape violation count, rollback-path violation count, validation-plan violation count, sanitization violation count, approval policy, and bounded blocker details so reviewers can diagnose a blocked candidate without opening raw JSON;
- `approval_state=preview-only` may run preview only and must not modify `config.toml`;
- `approved-to-apply` requires explicit user authorization and cannot be inferred from "continue" or generic confirmation;
- after apply, save sanitized before/after diff summaries;
- if warnings continue or key capabilities are missing after apply, restore through `rollback_path` first instead of stacking multiple profile changes in the same round.

| Symptom | Interpretation | Handling action |
| --- | --- | --- |
| No startup warning, but a live-session warning appears | soft-load may still be working; the runtime rebuilt the model-visible skills surface for a turn | Run `--warning-triage --days 1` or `--warning-triage --since ...` and record the turn; do not immediately hard-load apply |
| `All skill descriptions were removed` | The current skills surface is severely over budget | Avoid `full` on the next launch; use `core-dev` or a task profile; still do not delete plugin cache during the audit |
| `additional skills were not included` keeps rising | The automatic visible list is still too large | Shrink the default profile based on 30-day strong evidence and keep dormant restore paths |
| `Skipped loading` points to invalid SKILL.md | A specific skill metadata or vendor cache issue exists | Record the source through `warning_triage.skipped_loading_*` fields first; do not bulk-edit vendor cache without explicit user approval |

Before the audit ends, only generate reports and preview profiles. After the audit, if evidence supports a change, open a bounded change or use the approved profile helper for hard-load apply. Remote publication still follows this repository's local-main-first and GitLab/GitHub authorization workflow.

## 11. Implementation slices

### Slice 1: Audit source inventory and baseline capture
Scope:
- [x] Implement the audit CLI, data-source readers, inventory counters, JSON output, Markdown output, and Windows-safe stdout.
Completion criteria:
- [x] Day 0 baseline can be generated without mutating Codex config or plugin cache.
Tests:
- [x] CLI smoke, profile-registry fallback, and stdout encoding are covered.

### Slice 2: Live warning triage and warning severity
Scope:
- [x] Count budget warnings and skipped-loading warnings, enforce narrow warning-triage windows, and compute warning severity.
Completion criteria:
- [x] Broad-window triage is blocked and sanitized warning excerpts are rendered.
Tests:
- [x] Warning parsing, skipped-loading parsing, triage blocking, and severity rendering are covered.

### Slice 3: Field contract, privacy contract, and retention gates
Scope:
- [x] Validate report fields, audit-only safety, runtime path privacy, output retention, and pre-commit update/archive state.
Completion criteria:
- [x] Incomplete, unsafe, stale, or privacy-leaking reports cannot become profile-decision evidence.
Tests:
- [x] Field-contract, privacy, output-retention, and pre-commit gate tests are covered.

### Slice 4: Evidence aggregation and candidate preview
Scope:
- [x] Aggregate module evidence, manual evidence, noise review, decision buckets, audit states, and preview-only candidate records.
Completion criteria:
- [x] Candidate generation is blocked until a reviewed 30-day evidence package exists.
Tests:
- [x] Module-evidence, manual-evidence, decision-recommendation, audit-state, and candidate-contract tests are covered.

### Slice 5: Long-running monitoring cycle
Scope:
- [x] Run the real 30-day observation window from 2026-05-16 through 2026-06-15.
- [x] Lock the standard repeat count and frequency: Day 0 once, weekly four times, Day 30 once, and warning triage as event-driven one-off runs.
- [ ] Complete final human review and, only if explicitly chosen, optional preview-only candidate generation.
Completion criteria:
- [x] Final JSON and sanitized Markdown evidence exist for the closed 30-day window and pass embedded contracts.
- [x] Final summary is explicitly kept in `human_review_pending` with a `review-pending + continue monitoring` decision record and post-final monitoring evidence.
Tests:
- [x] Final observation-window evidence is verified when the calendar window closes.
- [x] Human-review decision evidence is verified before any candidate generation or closure path is trusted.

## 12. Task-level execution backlog

The detailed implementation work is complete except for final human review and any optional preview-only candidate. Concrete work items:

- [x] Audit CLI foundation.
- [x] Skills usage evidence collection.
- [x] Warning and log evidence collection.
- [x] Warning triage.
- [x] Warning severity.
- [x] Field contract and safety contract.
- [x] Privacy, sanitization, and retention.
- [x] Module evidence and decision recommendations.
- [x] Manual evidence and exceptions.
- [x] Audit state machine.
- [x] Candidate preview gate.
- [x] Cadence and recovery.
- [x] Human-readable outputs.
- [x] Output-retention gate.
- [x] Pre-commit update/archive gate.
- [x] Tests and CI coverage.
- [x] `tools/check_skills_audit_zh_evidence_encoding.py` implemented and registered in OpenSpec guard, safety-rule backing, and CI manifest.
- [x] Real 30-day usage audit observation window: 2026-05-16 through 2026-06-15.
- [x] Standard scheduled repeat count fixed: 1 Day 0 baseline, 4 weekly runs, and 1 Day 30 final run.
- [x] Standard scheduled frequency fixed: weekly `--days 7` during the audit, Day 30 final once, and warning triage only after new warnings.
- [x] Original audit end date fixed: 2026-06-15.
- [x] Script-backed cadence contract checker verifies the fixed repeat count, frequency, end date, event-triggered warning triage, and post-final monitoring boundary.
- [x] Script-backed zh-CN evidence encoding checker verifies current, future, changed, or explicitly protected Skills audit zh-CN evidence and reports untouched historical mojibake as warning-only.
- [x] Final 30-day evidence package generated and retained as sanitized Markdown evidence.
- [ ] Final human review of the 30-day evidence package.
- [x] Explicit current decision outcome recorded: `review-pending + continue monitoring`.
- [ ] Optional preview-only profile candidate after explicit target-profile review.

## 13. Local integration order

- [ ] Work in an isolated feature worktree when the primary main directory has unrelated dirty files.
- [ ] Keep the feature branch clean before local integration.
- [ ] Run `python tools/check_precommit_update_archive.py --root . --json` before every local commit.
- [ ] Run implementation-plan and document-pair checks after editing this plan pair.
- [ ] Run `python tools/run_openspec_guard.py --root .` before claiming repository guard health.
- [ ] Run `tools/ci/local_mr_review.ps1` after the feature branch is committed and clean.
- [ ] Run `tools/ci/local_gate.ps1` before local `main` integration.
- [ ] Fast-forward local `main` only after local evidence is clean.
- [ ] Do not push GitLab/GitHub unless the current user message explicitly approves remote publication.

## 14. Acceptance criteria and verification

Each audit run must report:

- audit window;
- enabled plugins summary;
- budget warning count and recent samples;
- warning triage status, narrow-window policy, and post-warning recommended action;
- explicit skill usage counts;
- SKILL.md read counts;
- profile helper invocation counts;
- plugin/module aggregated evidence;
- script capability boundaries, including reliable coverage, human-review needs, and enhancement triggers;
- recommendations, without applying them automatically.
- output retention status from `tools/check_skills_audit_output_retention.py`, proving `.tmp/` artifacts and raw Skills usage JSON are not retained in Git.
- final review state from `tools/check_skills_audit_final_review_state.py`, proving whether the audit is still `review-pending + continue monitoring`, `summary-reviewed + closed-no-change`, or `summary-reviewed + preview-only candidate`, while keeping profile apply blocked until a later explicit `approved-to-apply` receipt.
- final review precheck state from `tools/check_skills_audit_final_review_precheck.py`, proving noise/manual-conflict script-level prechecks are evidence-backed without marking the summary reviewed, generating candidates, or applying profiles.
- human-review decision-record state from `tools/check_skills_audit_human_review_decision_record.py`, proving a missing decision record remains pending, a present record has exactly one allowed outcome, candidate artifacts are blocked before the reviewed decision, preview-only candidate records include `target_profile` and review notes, and raw paths/secrets/transcripts/log excerpts are not retained.
- cadence contract state from `tools/check_skills_audit_cadence_contract.py`, proving the original observation window remains 2026-05-16 through 2026-06-15, planned audit repeats remain 6 total runs, weekly evidence dates remain fixed, warning triage remains event-triggered, and post-final runs remain monitoring-only.
- frontmatter-resolution state from `tools/check_skills_audit_frontmatter_resolution.py`, proving historical invalid `SKILL.md` skipped-loading warnings are bridged to the current frontmatter inventory and current `invalid_total=0` without mutating config, plugin cache, skill bodies, or profiles.
- zh-CN evidence encoding state from `tools/check_skills_audit_zh_evidence_encoding.py`, proving current, future, changed, or explicitly protected Skills usage audit zh-CN evidence is valid UTF-8 and does not retain replacement characters, placeholder question-mark runs, or high-signal mojibake markers; untouched legacy evidence remains warning-only.
- pre-commit update/archive status from `tools/check_precommit_update_archive.py`, proving existing-file update review and OpenSpec archive gates have passed before local commit.
- default human stdout must also render the audit state, enabled-plugin matched/unmatched summary, current-profile inference, inventory summary, frontmatter-compatibility summary and safety flags, log-evidence availability, recent budget-warning sample count, bounded sanitized budget-warning sample excerpts, and 7-day counts, warning-severity level, reason, and action, all-descriptions-removed / omitted-additional-skills pressure metrics, cadence review late-run / missed-weekly-runs / weekly-report-review state, warning triage status, warning triage window policy, warning/skipped-loading counts, sanitized skipped-loading sample excerpts, skipped-loading review action, warning triage frontmatter resolution, warning triage recommended action and blockers, explicit-skill total and unique-skill counts, SKILL.md read count, profile helper call count, script capability boundary counts, decision recommendation, recommendation count plus the first few recommendations, field-contract status and violation groups including `warning_severity`, output-retention gate, and pre-commit update/archive gate, so a non-JSON run is still safe to review.
- `test/audit_codex_skills_usage.test.py` must cover stdout encoding, warning parsing, warning-triage marker and narrow-window blocking, warning-triage Markdown output, cadence-review field-contract and Markdown output, Chinese announcements, repo profile fallback, `all_known_plugins` expansion, sanitized log-excerpt redaction marker integrity, sanitized manual-note ingestion, invalid manual-note validation, manual-note source-path privacy, report field-contract validation, missing/stale embedded field-contract candidate-gate blocking, source-report-path candidate-gate blocking, source-report privacy sanitization, audit closure-state gates and Markdown blocker output, preview-only candidate generation, 30-day/summary-reviewed candidate gate blocking, candidate rollback/validation fields, candidate-record contract failures for unsafe or incomplete candidate records, and candidate Markdown non-action text.
- Regression tests must also cover explicit-skill false-positive token path/secret redaction, length truncation, `noise_review` field-contract blocking for unsanitized or missing privacy fields, and `script_capability_boundaries` field-contract blocking for missing or empty boundary lists and missing or unsafe stable tool-call alias registry fields.
- Regression tests must cover `decision_recommendation` field-contract blocking for missing or non-advisory status, profile-apply allowance, incomplete bucket lists, non-string bucket entries, and stale `bucket_counts`.
- Regression tests must cover `module_evidence` row-contract blocking for missing/wrong-typed fields, non-string plugin entries, negative or stale strong counts, mapped-tool evidence being counted as strong, non-manual cross-project utility, and unsupported recommendations.
- Regression tests must cover `module_evidence` recommendation-threshold mismatches so stale rows cannot claim an on-demand, dormant, or candidate recommendation that contradicts their strong/weak evidence counts.
- Regression tests must cover output-retention blocking for forced `.tmp/` raw reports, raw `skills-usage-*.json` reports outside `.tmp/`, and allowed sanitized Markdown summaries.
- Regression tests must cover the final review state checker: pending continuation is allowed without candidate/apply, candidate artifacts before `summary-reviewed` are blocked, reviewed summaries require an explicit outcome, and profile apply remains unauthorized.
- Regression tests must cover the human-review decision-record checker: no record is a valid pending state, candidate artifacts before a decision record are blocked, pending/closed/preview-only outcomes are validated, preview-only candidate decisions require `target_profile` plus review notes, raw paths/secrets/transcripts/log excerpts are blocked, and multiple active decision records fail closed.
- Regression tests must cover the cadence contract checker: locked 6-run cadence passes, missing repeat-count language fails, wrong final end date fails, and missing post-final monitoring-only evidence fails.
- Regression tests must cover the frontmatter-resolution checker: historical `reference_files/10.md` warning markers plus current `invalid_total=0` pass, current invalid frontmatter fails closed, and missing historical markers fail closed.
- Regression tests must cover the zh-CN evidence encoding checker: clean current evidence passes, untouched legacy mojibake warns only, current `???` fails, `\ufffd` fails, active-current mojibake fails, edited legacy target files fail, and non-target Markdown remains unaffected.
- Regression tests must cover the pre-commit update/archive gate: reports must embed `precommit_update_archive`, field contracts must block missing, non-passing, or disabled existing-file update / OpenSpec archive gate status, and sanitized Markdown summaries must render the gate status.
- Regression tests must cover `output_retention` field-contract blocking for missing or non-passing retention status, and the sanitized Markdown summary must render the output-retention status and long-term evidence format.
- Regression tests must cover `manual_evidence.conflict_review` field-contract blocking plus sanitized Markdown rendering for manual exception / approved hard-load exception notes.
- Regression tests must cover skipped-loading warning triage counts, sanitized skipped-loading samples, field-contract blocking for missing skipped-loading triage fields, value-contract blocking for `warning_triage` status / window_policy / skipped_loading_review / blockers / non-negative counts, and Markdown rendering.
- Regression tests must cover the `warning_severity` field contract: missing `level` / `reason` / `recommended_action`, unsupported severity levels, and severity text containing raw private paths, secrets, or standalone tokens must all block; default stdout and sanitized Markdown summaries must render the `warning_severity` violation-group count.
- `tools/ci/ci_test_manifest.json` must include those regression tests so local and remote CI reuse the same checks.

Each human report review must also check false-positive noise:

- if `explicit_skills` contains obvious non-skill generic words such as `and`, `from`, or `draft`, those tokens must not count as strong evidence;
- tokens that cannot be mapped to the current available skills, profile modules, plugin names, or concrete `SKILL.md` paths are treated only as weak evidence or pending-cleanup noise;
- if the same false-positive pattern repeats, fix the script filter and regression tests before using the report for 30-day profile decisions;
- the final 30-day report must include a noise/false-positive review conclusion, even when the conclusion is "no obvious false positives found."

## 15. Evidence to retain

- [ ] Updated English canonical plan and Chinese companion.
- [ ] Local `git diff` proving only the plan pair changed unless a checker requires related files.
- [ ] `check_implementation_plan_rules` output.
- [ ] `check_document_pair_policy` output.
- [ ] `check_precommit_update_archive` output.
- [ ] `run_openspec_guard` output.
- [ ] Local MR review output.
- [ ] Local gate output.
- [ ] Feature branch commit hash and final local `main` hash.
- [ ] Worktree cleanup receipt if a disposable worktree was used.

## 16. Risks and mitigations

- [ ] Risk: A live warning is interpreted as proof that `soft-load` failed. Mitigation: run narrow warning triage and review runtime rebuild context.
- [ ] Risk: A profile is shrunk before enough evidence exists. Mitigation: require 30-day evidence, reviewed summary, and preview-only candidate gate.
- [ ] Risk: Useful but low-frequency plugins are mistaken for useless plugins. Mitigation: classify as on-demand or project-scoped, not deleted.
- [ ] Risk: Raw transcripts, paths, or secrets enter Git. Mitigation: retention checker, redaction contract, and sanitized Markdown long-term evidence only.
- [ ] Risk: Manual exceptions override script evidence. Mitigation: require conflict review and explicit disposition before profile decisions.
- [ ] Risk: Candidate preview is mistaken for apply authorization. Mitigation: `approval_state=preview-only` and explicit `approved-to-apply` gate.
- [ ] Risk: Completed but active OpenSpec changes are ignored before commit. Mitigation: precommit update/archive checker is part of audit report and commit flow.

## 17. Current open monitoring items

The original 30-day audit window is closed. These items now distinguish completed calendar-observation work from post-final review and monitoring work.

- [x] Complete the real 30-day usage audit observation window: 2026-05-16 through 2026-06-15.
- [x] Generate local 7-day weekly evidence during the audit window.
- [x] Generate the final 30-day JSON report after the window ends, retained local-only under `.tmp/`.
- [x] Generate the final sanitized Markdown summary after the window ends.
- [x] Lock the original audit end date to 2026-06-15.
- [x] Lock the fixed standard run count to 6 scheduled audit runs: 1 Day 0 baseline, 4 weekly runs, and 1 Day 30 final run.
- [x] Record that warning triage is event-triggered and has no fixed repeat count.
- [x] Script-backed final review state checker verifies the current pending/closed/candidate/apply-gate state.
- [x] Script-backed final review precheck checker verifies noise/manual-conflict machine evidence while preserving final human-review and apply gates.
- [x] Script-backed human-review decision-record checker verifies future optional decision records while preserving the current pending state and apply gate.
- [x] Script-backed cadence contract checker verifies the repeat count, weekly cadence, end date, warning-triage frequency, and post-final boundary.
- [x] Script-backed frontmatter-resolution checker bridges `reference_files/10.md` historical invalid `SKILL.md` warning markers to current `invalid_total=0` evidence.
- [ ] Manually review the final 30-day summary.
- [x] Explicitly record `review-pending + continue monitoring` while keeping the final summary `human_review_pending`.
- [x] Close the `reference_files/10.md` invalid `SKILL.md` runtime repair loop: post-repair audit reports `invalid_total=0`.
- [x] Close the `mcp2cli` / `skills2cli` R3/R4 user-level runtime evidence loop: install/update receipts, smoke receipts, and rollback pointer exist.
- [ ] Resolve final-summary noise false positives.
- [ ] Resolve final-summary manual conflicts or exceptions.
- [ ] Decide whether this audit closes as `closed-no-change`.
- [ ] If evidence supports a change, generate a profile apply candidate.
- [ ] Specify an explicit `target_profile` for the candidate.
- [ ] Generate candidate JSON preview.
- [ ] Generate candidate Markdown preview.
- [ ] Review candidate rollback path.
- [ ] Review candidate validation plan.
- [x] Add `skills2cli audit warnings` as a compact read-only post-final warning source over session JSONL and `logs_2.sqlite`.
- [x] Add current frontmatter compatibility summary and mtime-bounded session scanning to `skills2cli audit warnings`.
- [ ] Run narrow-window warning triage after each new post-final `2% skills context budget` warning.
- [ ] Manually review each new post-final warning triage result.
- [ ] Manually review each new post-final skipped-loading source sample.
- [ ] Do not run profile apply before explicit `approved-to-apply` authorization.
- [ ] If profile apply is authorized later, save sanitized before/after diffs.
- [ ] If warnings persist after apply, roll back through the rollback path.
- [ ] If critical capability is missing after apply, roll back through the rollback path.

## 18. Granularity completion checklist

This plan is granular enough only when all of the following are true:

- it explains why warnings may appear during live turns rather than only at startup;
- it distinguishes soft-load, hard-load/profile apply, and plugin cache edits;
- it defines strong / medium / weak evidence boundaries;
- it defines 7-day, 30-day, and warning-triage cadence;
- it requires `--warning-triage` to use `--days 1` or `--since`, records a top-level `warning_triage` field, and blocks broad-window triage reports;
- it defines the JSON report field contract and requires the script to expose `field_contract` plus block incomplete, missing-contract, or stale-contract reports at candidate-generation time;
- it validates decision-critical `audit_state` nested fields, including allowed state values, reason, next action, profile-apply denial, and blocker-list shape;
- it renders audit-state next action, profile-apply allowance, and blocker lists in the sanitized Markdown summary;
- it validates decision-critical `log_evidence` nested fields, including non-negative budget-warning counts, recent budget-warning sample counts, and sanitized bounded sample excerpts that do not retain raw paths, secrets, cookies, access tokens, or standalone tokens;
- it validates decision-critical `warning_severity` nested fields, including required `level` / `reason` / `recommended_action`, allowed `unknown` / `high` / `medium` / `none` levels, and sanitized reason/action text that does not retain raw paths, secrets, cookies, access tokens, or standalone tokens;
- default human-readable stdout and sanitized Markdown summaries render `field_contract` passed status, blocker count, required/missing/invalid-type field counts, embedded-contract requirement, and nested violation-group counts including `warning_severity` so reviewers can locate contract gaps without relying on raw JSON;
- it validates decision-critical `warning_triage` nested fields, including allowed states, string-only known blocker values, blocked/blocker consistency, fixed narrow-window policy, non-negative warning/skipped-loading counts, sanitized skipped-loading sample excerpts, skipped-loading source-review values, and recommended action;
- it validates decision-critical `cadence_review` nested fields and renders late-run plus missed-weekly-run status in the sanitized Markdown summary;
- it validates decision-critical `module_evidence` row fields, including string plugin lists, non-negative strong/weak counts, strong-total consistency, mapped-tool medium-evidence policy, manual cross-project review, allowed advisory recommendations, and recommendation-threshold consistency;
- it validates decision-critical `decision_recommendation` nested fields, including advisory-only status, profile-apply denial, required bucket names, string-only bucket entries, and bucket-count consistency;
- it validates decision-critical `output_retention` nested fields, including checker identity, `.tmp/` local-only policy, raw audit JSON local-only policy, sanitized Markdown long-term evidence format, and violation count;
- it validates decision-critical `precommit_update_archive` nested fields, including checker identity, pre-commit gate flag, existing-file update review, completed OpenSpec archive gate, error count, warning count, changed path count, and active change review count;
- it defines recovery rules for missed runs, delayed warning triage, unreadable logs, privacy sanitization, and urgent exceptions;
- it defines the final 30-day decision summary template;
- it defines the manual note format for medium evidence, urgent exceptions, and removed false positives;
- it defines the candidate change gate and rollback path before any post-audit hard-load/profile apply;
- it requires candidate generation to stay attached to a JSON report path and sanitized Markdown summary path;
- it requires candidate generation to accept only `summary-reviewed`, `apply-candidate`, or `closed-with-candidate` audit states and block not-ready or `closed-no-change` states;
- it requires candidate `source_reports` to pass a privacy contract before candidate JSON or Markdown is written;
- it requires generated candidate JSON and Markdown to expose a passing `candidate_record_contract` covering preview-only safety flags, gate shape, rollback path, validation-plan completeness, sanitization, and source-report privacy; candidate Markdown must show the same bounded contract counts and blocker details needed for non-JSON review;
- it defines data minimization, sanitization, retention, and no-externalization boundaries for audit data sources;
- it defines the audit script capability boundaries, known limitations, and conditions that trigger script enhancement;
- it exposes those script capability boundaries in JSON field contracts and sanitized Markdown summaries;
- it defines the audit run state machine, stop conditions, and the boundary between audit closure and profile apply candidate changes;
- it exposes planned-state recording through an audit-only script flag and blocks profile-apply candidates before the Day 0 baseline exists;
- it exposes paused-state recording through an audit-only script flag and blocks profile-apply candidates while paused;
- it exposes `summary-reviewed` as a script state only when the reviewed 30-day summary remains attached to JSON and Markdown source-report paths;
- it exposes closure-state recording through explicit audit-only script flags and reports blocked closure reasons instead of silently closing;
- it defines thresholds for frequent, low-frequency, and no-strong-evidence cases;
- it states that explicit-skill false-positive noise must not enter strong evidence;
- it defines warning severity and handling actions;
- it states that `.tmp/` output is not committed by default and long-term evidence must be sanitized;
- it requires `tools/check_skills_audit_output_retention.py` to block `.tmp/` artifacts and raw `skills-usage-*.json` reports from Git while allowing sanitized Markdown summaries;
- it requires `tools/check_skills_audit_final_review_state.py` to verify final review, closure, candidate, and apply-gate state before future continuation, closure, or candidate decisions;
- it requires `tools/check_skills_audit_human_review_decision_record.py` to validate optional human-review decision records, exact outcome selection, preview-only target-profile/review-note evidence, apply-authorization separation, and raw-retention blocking before closure or candidate decisions are trusted;
- it requires `tools/check_skills_audit_zh_evidence_encoding.py` to fail closed on invalid UTF-8, `\ufffd`, repeated question-mark placeholders, and high-signal mojibake markers in current, future, changed, or explicitly protected zh-CN evidence while keeping untouched historical legacy findings warning-only;
- it requires `tools/check_skills_audit_cadence_contract.py` to verify the fixed repeat count, weekly cadence, original end date, event-triggered warning triage, and post-final monitoring boundary;
- it requires `tools/check_precommit_update_archive.py` status to enter the audit JSON field contract and Markdown summary, blocking reports where existing-file update review was not checked or completed OpenSpec changes were not archived before commit;
- it states regression-test, OpenSpec guard, and CI manifest requirements;
- it states that remote publication still requires GitLab/GitHub authorization gates.
