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

- `tools/verify_official_openspec.py`
- `tools/check_current_repo_authority_language.py`
- `tools/check_document_governance_rules.py`
- `tools/check_implementation_plan_rules.py`
- `tools/check_name_clarity_rules.py` - enforces the OPSX name clarity rule for `docs_bilingual/` and `openspec/` without mutating documents.
- `tools/run_openspec_guard.py`
- later repository checks that expose a `--json` output and participate in the same guard surface

## 3. Output Classes

Use the following output classes:

1. `check report`
   - JSON emitted directly by one repository check script
2. `guard report`
   - aggregated JSON emitted by `run_openspec_guard.py`
3. `guard step record`
   - one step item under the guard report `steps` array

## 4. Common Top-Level Contract

All repository check JSON outputs must include the following top-level fields:

- `schema_version`
- `generated_at`
- `check_name`
- `ok`
- `errors`
- `warnings`
- `info`
- `root`
- `counts`

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

- `rules_path`
- `violations`
- `allowed_context_matches`
- `implementation_plan_entries`
- `tool`
- `skip_validate`

Additional script-specific fields must be additive.

Do not redefine the meaning of common top-level fields when adding script-specific fields.

## 6. Guard Report Contract

A `guard report` is the JSON emitted by `run_openspec_guard.py --json`.

It must use the common top-level contract.

It must also include:

- `tool`
- `refresh_managed_files`
- `require_clean_git`
- `skip_validate`
- `steps`

It may include:

- `failed_step`
- `error`

Rules:

- `steps` is the authoritative ordered list of executed guard steps
- `failed_step` is required when `ok` is `false`
- `error` is a summary string only and must not replace `errors`
- `counts` in the guard report must include at least:
  - `steps_total`
  - `steps_passed`
  - `steps_failed`

## 7. Guard Step Record Contract

Each item under `steps` must include:

- `step`
- `command`
- `returncode`
- `stdout`
- `stderr`
- `ok`

It may include:

- `data`
- `parse_error`

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

- `openspec-guard-report.json`

The guard report is the authoritative machine-readable CI report for repository OpenSpec enforcement.

Leaf-check reports may remain embedded under `steps[].data`.

## 11. Naming And Stability Rule

Keep these identifiers stable:

- `check_name`
- `step`
- keys under `counts`

Do not rename them for display reasons alone.

If a display-friendly label is needed later, add a new field instead of redefining the stable machine field.

## 12. Non-Drift Rule

When a new repository check adds `--json`, it must follow this policy.

When `run_openspec_guard.py` aggregates a child check, it must preserve the child check contract under `steps[].data` instead of inventing a conflicting structure.

Document, tests, and implementation must be updated in the same work batch when this JSON contract changes.
