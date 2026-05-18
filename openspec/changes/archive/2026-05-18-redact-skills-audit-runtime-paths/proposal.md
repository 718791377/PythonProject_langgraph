# Proposal: redact Skills audit runtime paths

## Why

The Skills usage audit reads repo-local and user-level runtime inputs, including the repository root, Codex home, and `config.toml`. Previous reports exposed raw absolute paths for these inputs through `root`, `codex_home`, and `config_summary.config_path`. That conflicted with the audit plan's data-minimization rule that raw private paths should not be retained in long-lived JSON, Markdown, or candidate evidence.

## What changes

- Add a `runtime_paths` report field with sanitized placeholders and path-kind labels.
- Replace top-level `root`, top-level `codex_home`, and `config_summary.config_path` report values with `[REPO_ROOT]`, `[CODEX_HOME]`, and `[CODEX_HOME]/config.toml` placeholders.
- Extend the report field contract to fail if runtime path fields retain raw private paths or mark raw paths as retained.
- Render runtime-path privacy status in sanitized Markdown summaries.
- Add regression coverage for runtime path redaction and field-contract blocking.
- Update the bilingual Skills usage audit plan and stable lifecycle spec.

## Safety

This is audit-only. It does not mutate `config.toml`, plugin cache, user-level profiles, hard-load settings, remote refs, or live plugin state. It only reduces retained path detail in generated audit reports.
