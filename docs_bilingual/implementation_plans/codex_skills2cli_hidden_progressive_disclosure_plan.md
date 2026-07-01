---
doc_id: codex_skills2cli_hidden_progressive_disclosure_plan
lang: en
canonical: docs_bilingual/implementation_plans/codex_skills2cli_hidden_progressive_disclosure_plan.md
translation: docs_bilingual/implementation_plans/codex_skills2cli_hidden_progressive_disclosure_plan.zh-CN.md
status: active
doc_class: implementation_plan
change: implement-skills2cli-hidden-progressive-disclosure
created_at: 2026-06-30
plan_readiness: implemented-local-runtime
implementation_lane: local-main-first
---

# Skills2CLI Hidden Skill Progressive Disclosure Plan

> For agentic workers: keep the current main Codex CLI session as leader. Use native experts or a durable lane only for disjoint implementation slices; skill/profile helper usage is procedural context, not native expert evidence.

**Goal:** let Codex discover and load hidden standalone user skills on demand without restoring the whole hidden library to the model-visible skill list, while using actual usage evidence to recommend and manually execute high-confidence visibility changes.

**Architecture:** Phase A freezes this OpenSpec-backed plan. Phase B extends `skills2cli` with a hidden-skill index/search/show/load surface, usage-event recording, visibility recommendations, and a manual `apply-recommendations` command that is limited to once per local day and is receipt-backed.

**Tech Stack:** Python `skills2cli.py`, JSONL usage events under the user-level Codex state directory, receipt-backed standalone user-skill moves, OpenSpec, local CI, and local MR review.

---

## Current Status

<!-- CURRENT_STATUS_START -->

- This plan has completed local runtime implementation for `implement-skills2cli-hidden-progressive-disclosure` and its OpenSpec change is archived locally.
- User-selected defaults:
  - hidden skill loading boundary: read-only soft-load;
  - dynamic visibility adjustment: high-confidence automatic selection, but only after a user manually triggers the command;
  - progressive disclosure search scope: current visible skills plus the `skills2cli` hidden library.
- Baseline hidden library observed on 2026-06-30: 989 hidden `SKILL.md` files under `C:\Users\lenovo\.codex\state\skills2cli\visibility-disabled`.
- `grill-me` exists in the hidden library as `mattpocock-skills-skills-productivity-grill-me-skill-md`.
- `stop-slop` is not an installed skill name; it is treated as an alias for `ai-slop-cleaner`.
- Runtime implementation and archive are local-only; remote publication is not authorized.

<!-- CURRENT_STATUS_END -->

## 1. Intent and safety boundaries

The hidden library is a reversible visibility library, not a trash directory. A hidden skill can be used without being made globally visible by reading exactly one selected `SKILL.md` into the current task context.

Non-goals:

- Do not restore all hidden skills.
- Do not edit plugin cache or vendor `SKILL.md` files.
- Do not edit `C:\Users\lenovo\.codex\config.toml`.
- Do not treat hidden skill loading as native expert or subagent evidence.
- Do not run promote/demote in the background or on a timer.
- Do not push GitLab/GitHub in this implementation flow.

Required safety flags for every hidden and recommendation command:

- `mutates_config=false` - states that the command does not edit Codex configuration.
- `edits_plugin_cache=false` - states that the command does not edit plugin or vendor cache files.
- `profile_apply_performed=false` - states that the command did not apply a profile or hard-load change.
- `global_restore_performed=false` - states that the command did not restore the hidden library globally.

## 2. Hidden skill progressive disclosure runtime

Add a `hidden` command group to `skills2cli`:

```powershell
skills2cli hidden index --json
skills2cli hidden search <query> --json
skills2cli hidden suggest --query "<task summary>" --json
skills2cli hidden show <hidden_skill_id> --json
skills2cli hidden load <hidden_skill_id> --json
```

Behavior:

- `hidden index`, `hidden search`, `hidden suggest`, and `hidden show` return compact metadata only.
- `hidden load` returns one selected `SKILL.md` body and records a usage event.
- If a body exceeds the CLI body limit, `hidden load` returns a chunk plus a `next_chunk_command`.
- Hidden commands search current visible skills and hidden skills together, but hidden records must be clearly marked as `visibility_state=hidden`, meaning the candidate still lives in the hidden library and was not restored globally.
- The runtime must never add hidden skills back to `C:\Users\lenovo\.codex\skills` during soft-load.

Initial aliases:

- `grill-me` -> `mattpocock-skills-skills-productivity-grill-me-skill-md`
- `stop-slop`, `deslop`, `anti-slop` -> `ai-slop-cleaner`

## 3. Usage evidence and visibility recommendations

Each `hidden load` writes one JSONL event to:

```text
C:\Users\lenovo\.codex\state\skills2cli\usage-events.jsonl
```

Event fields:

- `schema_version` - version of the usage-event schema.
- `event_id` - unique identifier for the usage event.
- `timestamp` - time when the hidden soft-load happened.
- `event_type=hidden_load` - classifies the record as one hidden skill soft-load event.
- `hidden_skill_id` - stable hidden-library identifier for the loaded skill.
- `frontmatter_name` - skill name parsed from YAML frontmatter when available.
- `query_hash` - hash of the triggering query or task text when supplied.
- `matched_alias` - alias that caused the match, if any.
- `confidence` - routing confidence for the selected hidden skill.
- `batch_id` - optional batch identifier for related usage events.
- `body_sha256` - hash of the returned skill body or chunk.
- `body_bytes` - byte size of the returned skill body or chunk.
- `raw_paths_retained=false` - records that raw local paths are not retained in the usage event.

Add recommendation commands:

```powershell
skills2cli visibility recommend --days 30 --json
skills2cli visibility apply-recommendations --receipt <recommendation_id> --apply --operator-confirmation --json
```

Recommendation rules:

- Promote candidate: 30-day hidden load count is at least 10, or two consecutive weeks each have at least 3 loads, or the operator explicitly pins the skill in the future.
- Demote candidate: a current standalone user skill has zero strong usage evidence for the selected window, is not protected/core, and can be moved to the visibility library.
- Keep-soft-load: hidden skill has 1-9 recent loads and does not meet the promote threshold.

Apply rules:

- The operator must manually invoke `apply-recommendations`; reminders may be shown, but no background auto-trigger is allowed.
- Apply can run at most once per local day.
- Each run moves at most 3 standalone user skills.
- Each run writes a rollback receipt before moving and updates it after each move.
- Any move failure stops the run and reports partial state.


<!-- TASK_BACKLOG_START -->

- [x] Freeze the bilingual implementation plan.
- [x] Create the OpenSpec proposal/design/tasks/management/spec package.
- [x] Register the bilingual plan in docs registry.
- [x] Validate Phase A and integrate into local main.
- [x] Implement hidden progressive disclosure runtime.
- [x] Add usage events and manual recommendation apply runtime.
- [x] Validate Phase B, archive OpenSpec, and integrate into local main.

<!-- TASK_BACKLOG_END -->

## 4. Implementation slices

Phase A plan-freeze slice:

- Create this bilingual plan.
- Create OpenSpec proposal, design, tasks, management, and delta spec.
- Register the plan in `docs_bilingual/docs_registry.yaml`.
- Validate and integrate the plan-freeze package into local `main`.

Phase B runtime slice:

- Implement hidden index/search/show/load and alias routing.
- Implement JSONL usage events and visibility recommendations.
- Implement manual, once-per-day `apply-recommendations` with rollback receipts.
- Add tests and checker coverage.
- Archive the OpenSpec change and integrate the runtime package into local `main`.

## 5. Acceptance criteria

- `skills2cli hidden search grill-me --json` finds the hidden `grill-me` adapter.
- `skills2cli hidden search stop-slop --json` resolves to `ai-slop-cleaner` by alias.
- `skills2cli hidden load <id> --json` returns one skill body, writes a usage event, and does not restore the skill globally.
- `skills2cli visibility recommend --days 30 --json` reports promote, keep-soft-load, and demote buckets with sanitized evidence.
- `skills2cli visibility apply-recommendations --receipt <id> --apply --operator-confirmation --json` is manual-only, once per local day, limited to 3 moves, and rollback-receipt backed.
- Local validation, OpenSpec guard, local CI, and local MR review pass before each local `main` integration.

## Evidence index

<!-- EVIDENCE_INDEX_START -->

- `openspec/changes/archive/2026-06-30-implement-skills2cli-hidden-progressive-disclosure/` - archived OpenSpec change for this plan.
- `tools/skills2cli.py` - runtime implementation target.
- `test/skills2cli.test.py` - focused test target for hidden commands and recommendation behavior.
- `docs_bilingual/docs_registry.yaml` - bilingual plan registration.

<!-- EVIDENCE_INDEX_END -->
