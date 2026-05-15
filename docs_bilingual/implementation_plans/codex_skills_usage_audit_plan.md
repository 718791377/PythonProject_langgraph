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
.\.venv\Scripts\python.exe .\tools\audit_codex_skills_usage.py --root . --days 30 --json --output .\.tmp\skills-usage-audit-30d.json
```

## 6. Decision rules

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

## 8. Relationship to soft-load

If a session emits another `2% skills context budget` warning, that does not mean soft-load failed. The runtime is still constructing the model-visible skills surface for the turn, while soft-load is outside that budget surface. Soft-load answers “how do we read needed task knowledge now,” not “how do we shrink the global automatic visible list.”

## 9. Next actions

Before the audit ends, only generate reports and preview profiles. After the audit, if evidence supports a change, open a bounded change or use the approved profile helper for hard-load apply. Remote publication still follows this repository's local-main-first and GitLab/GitHub authorization workflow.
