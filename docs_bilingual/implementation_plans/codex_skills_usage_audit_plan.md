---
doc_id: codex_skills_usage_audit_plan
lang: en
canonical: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.md
translation_of: docs_bilingual/implementation_plans/codex_skills_usage_audit_plan.zh-CN.md
status: active
doc_class: implementation_plan
created_at: 2026-05-16
---

# Codex Skills Usage Audit Plan

## 1. Background

The `Exceeded skills context budget of 2%` warning is not guaranteed to appear only when the Codex process starts. In live sessions, the runtime may rebuild the model-visible skills surface when preparing a turn, resuming a thread, repacking context, or applying context truncation. A clean startup therefore does not prove that later turns cannot emit the warning.

`soft-load` does not mutate the startup-visible skills list and does not restore skills that were omitted from the model-visible list by the 2% budget. It only reads task-relevant SKILL.md or reference files into normal conversation context. Therefore:

- soft-load is a current-session remediation and on-demand knowledge loading path;
- hard-load/profile apply changes the plugin/skills surface for the next launch or resume;
- the default profile should not be reduced to `core-dev` without usage evidence;
- `company-ops`, `market-research`, `web-saas`, `customer-comms`, and `creative-content` should be observed for one month before deciding whether they are always-on, project-scoped, or on-demand only.

## 2. Audit goal

This plan defines a 30-day audit-only process so later profile decisions are evidence-based and do not accidentally make useful plugin skills dormant.

The audit answers four questions:

1. Which skills/plugins have strong usage evidence in the last 30 days?
2. Which modules were only mentioned but not actually read or invoked?
3. When and where did the `2% skills context budget` warnings occur?
4. Which capabilities should be always-on, project hard-load, soft-load on demand, or kept only in the `full` troubleshooting profile?

## 3. Evidence levels

### 3.1 Strong evidence

Strong evidence can support keeping or profile-gating a capability:

- the assistant explicitly announced `Using skill: xxx` or `使用技能：xxx`;
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

## 4. Audit-only rules

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

## 5. Required scripts

### 5.1 Collection script

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 30 --json --output .\.tmp\skills-usage-audit-latest.json
```

Default sources:

- `C:\Users\lenovo\.codex\sessions/**/*.jsonl` - session transcripts used to detect explicit skill announcements and SKILL.md reads.
- `C:\Users\lenovo\.codex\logs_2.sqlite` - runtime log database used to count skills-budget warnings.
- `C:\Users\lenovo\.codex\config.toml` - user-level plugin enabled-state source for audit-only reporting.
- `C:\Users\lenovo\.codex\skills\plugin-modules\references\profiles.json` - module registry used to aggregate plugin evidence by profile.

### 5.2 Baseline snapshot

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 0 --baseline --json --output .\.tmp\skills-usage-baseline-2026-05-16.json
```

The baseline records enabled plugins, profile modules, warning counters, and inventory summary. It does not mutate `config.toml`.

### 5.3 Weekly summary

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 7 --json --output .\.tmp\skills-usage-audit-7d.json
```

### 5.4 30-day decision report

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 30 --json --output .\.tmp\skills-usage-audit-30d.json --summary-output .\.tmp\skills-usage-audit-30d-summary.md --manual-notes .\.tmp\skills-usage-audit-notes-YYYY-MM-DD.md
```

`--summary-output` writes the sanitized Markdown decision summary. It is review evidence only and must not mutate `config.toml`, plugin cache, or hard-load profiles.

To prepare a later reversible candidate without applying it, add `--target-profile`, `--candidate-output`, `--summary-reviewed`, and optionally `--candidate-summary-output`:

```powershell
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 30 --json --output .\.tmp\skills-usage-audit-30d.json --summary-output .\.tmp\skills-usage-audit-30d-summary.md --summary-reviewed --target-profile core-dev --candidate-output .\.tmp\skills-profile-candidate.json --candidate-summary-output .\.tmp\skills-profile-candidate.md
```

Candidate output is always `approval_state=preview-only` and must not modify `config.toml`, plugin cache, or hard-load profiles. Without `--summary-reviewed`, a 30-day audit window, `--output`, and `--summary-output`, the candidate generation gate is recorded as blocked.

### 5.5 Windows stdout and regression tests

The script must still support `--json` on non-UTF-8 Windows consoles. If stdout cannot encode characters such as `⚠`, stdout may fall back to JSON-safe backslash escapes; the `--output` report file must still preserve the original UTF-8 text.

Regression tests must cover:

- stdout fallback for `⚠ Exceeded skills context budget of 2%`;
- explicit skill-announcement detection for Chinese `使用技能：` and English `Using skill:`;
- extraction of `omitted_additional_skills` and `all_descriptions_removed` from `logs_2.sqlite` budget warnings;
- `plugins: "all_known_plugins"` in the `full` profile must not be split into individual characters;
- the script must fall back to `tools/skill_sources/plugin-modules/references/profiles.json` when the user-level plugin-modules profile is absent.

### 5.6 Report field contract

The report generated by `--json` and `--output` must include at least these top-level fields. If any field is missing, the report must not be used for profile decisions.

| Field | Purpose | Decision impact |
| --- | --- | --- |
| `schema_version` | Report structure version | Allows later scripts to parse compatibly |
| `generated_at` | Report generation time | Shows whether the report is stale |
| `audit_window` | `since` / `until` / `days` | Prevents 30-day decisions from using the wrong window |
| `safety` | Config mutation, plugin cache edit, and hard-load apply flags | Must prove audit-only behavior |
| `config_summary` | enabled / disabled / unknown plugins plus `current_profile` inference | Shows whether the current profile surface is too large and whether it exactly matches a known module |
| `inventory_summary` | user/repo/plugin skill counts | Helps locate 2% budget pressure |
| `log_evidence` | budget warning, 7-day warning count, `All skill descriptions were removed`, omitted-skill maximum, and skipped-loading evidence | Shows whether warnings still occur during live turns and whether severity crosses the plan threshold |
| `session_evidence` | explicit skills, SKILL.md reads, helper calls, tool calls | Feeds strong/medium/weak evidence classification |
| `manual_evidence` | sanitized manual-note counts, invalid-note validation, and medium/exception/noise summaries | Preserves human review evidence without retaining raw transcripts |
| `module_evidence` | profile-module-level strong, medium-rationale, weak, and cross-project review fields | Produces profile decision candidates without treating medium evidence as strong evidence |
| `cadence_review` | late-run and missed-weekly-run markers | Prevents cadence drift from being hidden in a 30-day decision summary |
| `recommendations` | Audit recommendations | Advisory only; never auto-apply |

The audit script must compute a `field_contract` result for every generated report. The result records `status`, `passed`, required fields, missing fields, invalid field types, safety violations, and decision-critical nested-field violations. A report with `field_contract.status != passed` is incomplete evidence: it must be fixed or regenerated before any profile decision. Candidate generation must require the report's embedded `field_contract`; reports from older scripts or manually edited reports with a missing or stale embedded contract must be blocked until regenerated.

### 5.7 Audit cadence, retention, and report naming

Use a fixed cadence so the one-month audit does not drift.

| Time | Command | Output file | Purpose |
| --- | --- | --- | --- |
| Day 0 | `--days 0 --baseline` | `.tmp/skills-usage-baseline-YYYY-MM-DD.json` | Freeze initial enabled plugins, inventory, and warning state |
| Weekly | `--days 7` | `.tmp/skills-usage-audit-7d-YYYY-MM-DD.json` | Detect new live-session warnings and module trends |
| Late weekly recovery | `--days 7 --late-run --missed-weekly-runs N` | `.tmp/skills-usage-audit-7d-late-YYYY-MM-DD.json` | Preserve an explicit cadence-drift marker instead of fabricating the missed run |
| Day 30 | `--days 30` | `.tmp/skills-usage-audit-30d-YYYY-MM-DD.json` | Build the evidence package for default-profile decisions |
| After a warning | `--days 1` or `--since` | `.tmp/skills-usage-warning-triage-YYYY-MM-DD.json` | Locate whether the warning came from current-session repacking |

Reports under `.tmp/` are not committed by default. If long-term evidence is needed, commit only a sanitized Markdown summary, not full session transcripts, tokens, private paths, or vendor cache content.

### 5.8 Drift control and exception recovery

During the one-month audit, handle cadence drift or data-source failures with the table below so incomplete evidence is not treated as a final decision package.

| Drift or exception | Recovery action | Disallowed action |
| --- | --- | --- |
| A weekly summary was missed | Run `--days 7` immediately and mark `late_run: true` in the summary | Fabricate historical reports to fill the cadence |
| A warning was not triaged promptly | Run `--days 1`; if more than 24 hours passed, also run `--since` across the warning time | Decide from memory whether soft-load failed |
| `logs_2.sqlite` is missing or unreadable | Keep `log_evidence.available=false` in the report and use session transcripts only as supporting evidence | Treat zero logged warnings as proof that no warning happened |
| Session transcripts are incomplete or privacy-sensitive | Commit only aggregate fields and a sanitized summary; keep raw JSON local under `.tmp/` if needed | Commit full transcripts, tokens, or private paths |
| A report misses required contract fields | Fix the script or rerun the report before profile decisions | Use an incomplete report for hard-load/profile apply decisions |
| An urgent task genuinely needs a plugin during the audit | Allow task-scoped soft-load or preview; require explicit approval and an exception note for hard-load | Use the urgent task as a reason to end the 30-day audit early |

### 5.9 30-day decision summary template

Day 30 must not ship only raw JSON. It must produce a sanitized Markdown summary that is reviewable by a human and includes at least:

1. Audit window: start/end time, missed weekly runs, and late-run status.
2. Current configuration surface: enabled/disabled/unknown plugin counts, `current_profile.inferred_profile`, exact module matches, and whether manual review is required.
3. Warning conclusion: 30-day warning count, 7-day warning count, highest severity, and whether `All skill descriptions were removed` appeared.
4. Evidence table: per-module strong evidence count, `medium_evidence_rationale`, weak-evidence count, `cross_project_utility`, and the recommendation.
5. Noise review: list obvious false-positive tokens removed from evidence, such as `and`, `from`, or `draft`, and state they were not counted as strong evidence.
6. Decision recommendation: default-always-on, project profile, on-demand soft-load, dormant but restorable, or `full` troubleshooting profile only.
7. Risks and restore path: if a plugin is disabled or removed from the default profile, document how to restore it, which helper to use such as `set_plugin_profile.ps1 -RestoreLatest -Apply`, and whether a `codex-ohmy` restart/new session is required.
8. Non-action list: explicitly state what the report did not do, such as not modifying `config.toml`, not editing plugin cache, and not performing hard-load apply.

Only when this summary and the JSON field contract both pass may the work move into hard-load/profile apply discussion.

### 5.10 Manual evidence and exception note format

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

Manual notes cannot override script evidence. If manual judgment conflicts with the JSON report, the 30-day summary must list both the conflict and the disposition.

### 5.11 Profile apply candidate change gate

After the 30-day audit, evidence that supports changing the default profile still must not be applied directly. First create a candidate change-gate record that turns the audit conclusion into a reversible configuration change.

The candidate record must include at least:

| Field | Description |
| --- | --- |
| `candidate_id` | Candidate change ID, for example `skills-profile-2026-06-core-dev-plus-browser` |
| `source_reports` | Paths to the 30-day JSON report, sanitized Markdown summary, and manual-note summary |
| `current_profile` | Current default profile and enabled-plugin summary |
| `target_profile` | Candidate target profile, or the profile name to create/update |
| `plugin_diff` | Plugins/modules to add, remove from default, or keep dormant |
| `evidence_basis` | Strong evidence, medium evidence, strategic retention, or warning pressure for each change item |
| `risk_review` | Capabilities that might be mistakenly disabled, affected projects, and restore cost |
| `rollback_path` | Helper command to restore the old profile and restart/new-session requirements |
| `validation_plan` | Preview, local check, startup validation, and warning retest steps |
| `approval_state` | `preview-only`, `approved-to-apply`, `applied`, or `rolled-back` |

Gate rules:

- the audit script may generate candidate JSON/Markdown via `--candidate-output` and `--candidate-summary-output`, but those outputs are preview records only;
- candidate generation must record a gate result that requires a 30-day audit window and `--summary-reviewed`;
- candidate generation must require source-report paths for the 30-day JSON report and sanitized Markdown summary, so a reviewed candidate cannot be detached from its review evidence;
- candidate generation must also validate the report field contract and block with `field_contract:<reason>` when required top-level fields, audit-only safety flags, decision-critical nested fields, or the embedded `field_contract` itself are missing, stale, or invalid;
- `approval_state=preview-only` may run preview only and must not modify `config.toml`;
- `approved-to-apply` requires explicit user authorization and cannot be inferred from “continue” or generic confirmation;
- after apply, save sanitized before/after diff summaries;
- if warnings continue or key capabilities are missing after apply, restore through `rollback_path` first instead of stacking multiple profile changes in the same round.

### 5.12 Data minimization, sanitization, and retention boundaries

The usage audit reads user-level Codex sessions, logs, and configuration state, so “readable data” and “retainable data” must be managed separately.

| Data source | Allowed read purpose | Retainable content | Forbidden retained or external content |
| --- | --- | --- | --- |
| `sessions/**/*.jsonl` | Identify explicit skill announcements, `SKILL.md` reads, and helper calls | Aggregate counts, sanitized task type, sanitized project name | Full transcripts, private user input, tokens, secrets, customer information |
| `logs_2.sqlite` | Count budget warnings, skipped loading, and warning time windows | Warning counts, time windows, sanitized message excerpts | Full log database, raw messages containing paths/accounts/secrets |
| `config.toml` | Read plugin enabled/disabled/unknown state | Plugin-state summary and profile names | Full user-level configuration, credentials, unrelated settings |
| plugin/vendor cache | Count `SKILL.md` inventory or locate invalid skills | Skill counts, path categories, invalid-skill summary | Full vendor files or bulk-copied `SKILL.md` content |
| `.tmp/` audit report | Local temporary review | Local JSON and sanitized Markdown summary | Unsanitized reports committed to Git or sent to remotes |

Retention rules:

- `.tmp/*.json` is local temporary evidence by default and is not committed to Git;
- long-term evidence must be a sanitized Markdown summary only;
- before any report enters Git, verify it contains no API keys, access tokens, cookies, private customer names, or full local user-directory inventories;
- remote publication must not upload raw audit JSON as an attachment;
- if a generated report contains sensitive content, delete that local report and regenerate a sanitized summary instead of manually redacting the same report in place and continuing to use it.

### 5.13 Script capability boundaries and enhancement triggers

`tools/audit_codex_skills_usage.py` is an audit helper, not an omniscient source of truth. The 30-day report must state both “what the script reliably covers” and “what still needs human review.”

Current script capability boundaries:

- it can count plugin enabled/disabled/unknown state in `config.toml`;
- it can count user/repo/plugin `SKILL.md` inventory;
- it can extract explicit skill announcements, `SKILL.md` path reads, profile helper calls, and tool-call names from session transcripts;
- it can extract skills budget warnings, `All skill descriptions were removed`, `additional skills` counts, and skipped-loading samples from `logs_2.sqlite`;
- it can aggregate helper calls and plugin skill-path reads by profile module to produce preliminary recommendations.

Known limitations:

- `weak_plugin_mentions` shows text trends only and does not prove real invocation;
- `explicit_skills` can include natural-language or example-token false positives and must go through noise review;
- `tool_call_names` is not the same as plugin/module usage unless it can be mapped to a concrete capability surface;
- if the log database is unreadable, rotated, or missing old sessions, warning counts may be underreported;
- profile-module aggregation depends on the registry, so missing or stale registry data makes the report incomplete evidence.

Prefer script enhancement over manual workaround when:

- the same false-positive pattern appears in two weekly reports;
- the 30-day summary needs a class of evidence but the script only reports weak mentions;
- `tool_call_names` shows a stable pattern that maps to a plugin/module but the script does not aggregate it;
- warnings occur during a session but `logs_2.sqlite` cannot localize them, requiring another reviewable data source;
- the profile registry and actual enabled-plugin surface diverge enough to make module evidence visibly wrong.

When the script is enhanced, update regression tests and this plan together. Until tests are added, new parsing rules must not be used as final 30-day decision evidence.

### 5.14 Audit run state machine and stop conditions

To prevent month-long audit drift, the audit itself must have explicit state. The state describes the audit workflow only; it does not mean a plugin/profile has been applied.

| State | Meaning | Allowed actions | Forbidden actions |
| --- | --- | --- | --- |
| `planned` | The plan exists, but the Day 0 baseline has not been generated | Review the plan and run baseline preview | Claim 30-day evidence already exists |
| `running` | Day 0 baseline exists and 30-day evidence is being collected | Weekly reports, warning triage, manual notes, script fixes | Hard-load apply unless separately and explicitly approved |
| `paused` | Missing data source, privacy issue, or script defect paused the audit | Fix data sources, add tests, rerun reports | Use missing paused-period data for final decisions |
| `ready-for-summary` | Day 30 has arrived and field contract, weekly reports, triage, and manual notes are mostly complete | Generate the sanitized 30-day Markdown summary | Directly modify the default profile |
| `summary-reviewed` | The 30-day summary has been human-reviewed and noise/conflicts are dispositioned | Create a profile apply candidate change gate | Skip rollback or validation planning |
| `apply-candidate` | A candidate change record exists and is still preview-only or awaiting approval | Preview, risk review, request explicit authorization | Treat generic “continue” as apply authorization |
| `closed-no-change` | 30-day evidence does not support changing the default profile | Keep dormant/soft-load paths and close this audit round | Extend the same audit round just to force a result |
| `closed-with-candidate` | This audit round is closed and produced an approval-pending candidate | Move to a separate profile apply change | Execute configuration changes inside the audit plan file |

Stop conditions:

- after `closed-no-change`, the next step is only a new audit round if needed or continued soft-load usage; do not keep appending to this round;
- after `closed-with-candidate`, follow-up work must move into the profile apply candidate change and must not treat this audit plan as the execution surface;
- if two consecutive reviews add only explanatory prose and no verifiable rule, field, state, or test requirement, stop expanding the plan and commit the current refined result;
- audit state changes must be recorded in the 30-day summary or candidate change record, not only in chat context.

## 6. Decision rules

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

## 7. Acceptance criteria

Each audit run must report:

- audit window;
- enabled plugins summary;
- budget warning count and recent samples;
- explicit skill usage counts;
- SKILL.md read counts;
- profile helper invocation counts;
- plugin/module aggregated evidence;
- recommendations, without applying them automatically.
- `test/audit_codex_skills_usage.test.py` must cover stdout encoding, warning parsing, Chinese announcements, repo profile fallback, `all_known_plugins` expansion, sanitized manual-note ingestion, invalid manual-note validation, report field-contract validation, missing/stale embedded field-contract candidate-gate blocking, source-report-path candidate-gate blocking, preview-only candidate generation, 30-day/summary-reviewed candidate gate blocking, candidate rollback/validation fields, and candidate Markdown non-action text.
- `tools/ci/ci_test_manifest.json` must include that regression test so local and remote CI reuse the same check.

Each human report review must also check false-positive noise:

- if `explicit_skills` contains obvious non-skill generic words such as `and`, `from`, or `draft`, those tokens must not count as strong evidence;
- tokens that cannot be mapped to the current available skills, profile modules, plugin names, or concrete `SKILL.md` paths are treated only as weak evidence or pending-cleanup noise;
- if the same false-positive pattern repeats, fix the script filter and regression tests before using the report for 30-day profile decisions;
- the final 30-day report must include a noise/false-positive review conclusion, even when the conclusion is “no obvious false positives found.”

## 8. Warning severity and handling actions

| Symptom | Interpretation | Handling action |
| --- | --- | --- |
| No startup warning, but a live-session warning appears | soft-load may still be working; the runtime rebuilt the model-visible skills surface for a turn | Run a 1-day triage report and record the turn; do not immediately hard-load apply |
| `All skill descriptions were removed` | The current skills surface is severely over budget | Avoid `full` on the next launch; use `core-dev` or a task profile; still do not delete plugin cache during the audit |
| `additional skills were not included` keeps rising | The automatic visible list is still too large | Shrink the default profile based on 30-day strong evidence and keep dormant restore paths |
| `Skipped loading` points to invalid SKILL.md | A specific skill metadata or vendor cache issue exists | Record the source first; do not bulk-edit vendor cache without explicit user approval |

## 9. Relationship to soft-load

If a session emits another `2% skills context budget` warning, that does not mean soft-load failed. The runtime is still constructing the model-visible skills surface for the turn, while soft-load is outside that budget surface. Soft-load answers “how do we read needed task knowledge now,” not “how do we shrink the global automatic visible list.”

## 10. Next actions

Before the audit ends, only generate reports and preview profiles. After the audit, if evidence supports a change, open a bounded change or use the approved profile helper for hard-load apply. Remote publication still follows this repository's local-main-first and GitLab/GitHub authorization workflow.

## 11. Granularity completion checklist

This plan is granular enough only when all of the following are true:

- it explains why warnings may appear during live turns rather than only at startup;
- it distinguishes soft-load, hard-load/profile apply, and plugin cache edits;
- it defines strong / medium / weak evidence boundaries;
- it defines 7-day, 30-day, and warning-triage cadence;
- it defines the JSON report field contract and requires the script to expose `field_contract` plus block incomplete, missing-contract, or stale-contract reports at candidate-generation time;
- it defines recovery rules for missed runs, delayed warning triage, unreadable logs, privacy sanitization, and urgent exceptions;
- it defines the final 30-day decision summary template;
- it defines the manual note format for medium evidence, urgent exceptions, and removed false positives;
- it defines the candidate change gate and rollback path before any post-audit hard-load/profile apply;
- it requires candidate generation to stay attached to a JSON report path and sanitized Markdown summary path;
- it defines data minimization, sanitization, retention, and no-externalization boundaries for audit data sources;
- it defines the audit script capability boundaries, known limitations, and conditions that trigger script enhancement;
- it defines the audit run state machine, stop conditions, and the boundary between audit closure and profile apply candidate changes;
- it defines thresholds for frequent, low-frequency, and no-strong-evidence cases;
- it states that explicit-skill false-positive noise must not enter strong evidence;
- it defines warning severity and handling actions;
- it states that `.tmp/` output is not committed by default and long-term evidence must be sanitized;
- it states regression-test and CI manifest requirements;
- it states that remote publication still requires GitLab/GitHub authorization gates.
