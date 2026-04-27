---
doc_id: openspec_check_and_guard_json_output_policy
lang: en
doc_class: governance
status: active
---

# OpenSpec Check And Guard JSON Output Policy

## 1. Purpose

This document defines the repository JSON output contract for:

- repository check scripts that support `--json`
- the aggregated `run_openspec_guard.py --json` output
- CI artifact consumers that read those reports

The goal is to keep machine-readable repository checks stable, explicit, and forward-compatible.

## 2. Scope

This policy applies to:

- `tools/verify_official_openspec.py` - verifies that official OpenSpec workflow bootstrap and generated artifacts are healthy for this repository.
- `tools/check_current_repo_authority_language.py` - checks documentation language that defines this repository as the current authority for orchestration work.
- `tools/check_document_governance_rules.py` - checks governance docs for required policy patterns and forbidden drift.
- `tools/check_implementation_plan_rules.py` - checks implementation plan documents against repository planning rules.
- `tools/check_name_clarity_rules.py` - enforces the OPSX name clarity rule for `docs_bilingual/` and `openspec/` without mutating documents; the aggregated guard runs it in strict no-baseline mode.
- `tools/run_openspec_guard.py` - aggregates repository OpenSpec checks into one local guard command and JSON report.
- later repository checks that expose a `--json` output and participate in the same guard surface

## 3. Output Classes

Use the following output classes:

1. `check report` - JSON emitted directly by one repository check script.
2. `guard report` - aggregated JSON emitted by `run_openspec_guard.py`.
3. `guard step record` - one step item under the guard report `steps` array.

## 4. Common Top-Level Contract

All repository check JSON outputs must include the following top-level fields:

- `schema_version` - integer schema version used by consumers to interpret the report contract.
- `generated_at` - UTC ISO 8601 timestamp for when the report was generated.
- `check_name` - stable machine-readable identifier for the check that emitted the report.
- `ok` - boolean success flag for the whole report.
- `errors` - array of blocking problems, empty when no blocking problems exist.
- `warnings` - array of non-blocking advisory messages, empty when none exist.
- `info` - array of informational messages for humans and log consumers.
- `root` - repository root path used by the check run.
- `counts` - object containing numeric summary metrics for the report.

Required rules:

- `schema_version` must be an integer
- `generated_at` must be a UTC ISO 8601 timestamp
- `check_name` must be a stable machine-readable identifier
- `ok` must be boolean
- `errors`, `warnings`, and `info` must always be arrays, even when empty
- `counts` must always be an object, even when small

## 5. Check Report Contract

A `check report` is the JSON emitted by one leaf repository check.

It must use the common top-level contract.

It may add script-specific fields such as:

- `rules_path` - path to the governance rule file used by the check.
- `violations` - list of rule violations found by the check.
- `allowed_context_matches` - matches that were accepted because they fit an allowed context.
- `implementation_plan_entries` - implementation-plan records inspected by the check.
- `tool` - tool or entrypoint name that produced or controls the report.
- `skip_validate` - flag showing whether OpenSpec validation was intentionally skipped.

Additional script-specific fields must be additive.

Do not redefine the meaning of common top-level fields when adding script-specific fields.

## 6. Guard Report Contract

A `guard report` is the JSON emitted by `run_openspec_guard.py --json`.

It must use the common top-level contract.

It must also include:

- `tool` - guard entrypoint name for the aggregated report.
- `refresh_managed_files` - boolean flag showing whether managed OpenSpec files were refreshed before checks.
- `require_clean_git` - boolean flag showing whether the guard enforces a clean Git worktree.
- `skip_validate` - boolean flag showing whether official OpenSpec validation was skipped.
- `steps` - ordered guard step records executed in the run.

It may include:

- `failed_step` - stable name of the guard step that failed when `ok` is `false`.
- `error` - short summary string for the guard-level failure.

Rules:

- `steps` is the authoritative ordered list of executed guard steps
- `failed_step` is required when `ok` is `false`
- `error` is a summary string only and must not replace `errors`
- `counts` in the guard report must include at least:
  - `steps_total` - total number of guard steps scheduled for the run.
  - `steps_passed` - number of guard steps that completed successfully.
  - `steps_failed` - number of guard steps that failed or blocked completion.

## 7. Guard Step Record Contract

Each item under `steps` must include:

- `step` - stable internal name for the guard step.
- `command` - command line invoked for the guard step.
- `returncode` - process exit code returned by the command.
- `stdout` - captured standard output from the command.
- `stderr` - captured standard error from the command.
- `ok` - boolean success flag for this guard step.

It may include:

- `data` - parsed child JSON output when the child output is valid JSON.
- `parse_error` - parse failure message when `stdout` exists but is not valid JSON.

Rules:

- `step` must be a stable internal step name
- `data` should contain the parsed child JSON when the child output is valid JSON
- consumers should prefer `data` over reparsing `stdout`
- `parse_error` should be used only when `stdout` exists but is not valid JSON

## 8. Success, Failure, And Exit Code Rule

Required rules:

- a script must exit with code `0` when `ok` is `true`
- a script must exit with non-zero when `ok` is `false`
- `errors` must remain the canonical blocking-problem list
- `warnings` must not by themselves force `ok=false`

## 9. Compatibility And Evolution Rule

Required rules:

- `schema_version` must be present in every report
- additive field growth is allowed
- existing field meanings must not silently change
- consumers must ignore unknown fields
- breaking output changes require a schema-version bump

## 10. CI Artifact Rule

The repository CI guard surface should persist the aggregated guard JSON as an artifact.

The current canonical artifact name is:

- `openspec-guard-report.json` - canonical CI artifact file name for the aggregated guard JSON report.

The guard report is the authoritative machine-readable CI report for repository OpenSpec enforcement.

Leaf-check reports may remain embedded under `steps[].data`.

## 11. Naming And Stability Rule

Keep these identifiers stable:

- `check_name` - stable check identifier used by consumers for routing and aggregation.
- `step` - stable guard step identifier used in guard `steps` records.
- keys under `counts` - stable metric names used by consumers for summary reporting.

Do not rename them for display reasons alone.

If a display-friendly label is needed later, add a new field instead of redefining the stable machine field.

## 12. Non-Drift Rule

When a new repository check adds `--json`, it must follow this policy.

When `run_openspec_guard.py` aggregates a child check, it must preserve the child check contract under `steps[].data` instead of inventing a conflicting structure.

Document, tests, and implementation must be updated in the same work batch when this JSON contract changes.
