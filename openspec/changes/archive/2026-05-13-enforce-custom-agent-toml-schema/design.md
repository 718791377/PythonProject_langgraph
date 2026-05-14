## Context

The current policy already states that native Codex subagents, skills, profile helpers, durable workers, and LangGraph nodes are separate execution surfaces. The native-subagent boundary spec also states that standalone custom-agent TOMLs must include `name`, `description`, and `developer_instructions`.

This change turns that documented boundary into an executable local checker. It deliberately validates only the minimum standalone TOML schema needed for reliable native-agent discovery and role loading.

## Decisions

- Implement a standalone Python checker at `tools/check_custom_agent_toml_schema.py`.
- Use Python 3.11+ `tomllib` so no new dependency is required.
- Scan two locations by default:
  - repo-local `<root>/.codex/agents/*.toml`
  - user-level `<home>/.codex/agents/*.toml`, overrideable with `--user-agents-dir`
- Treat missing scan directories as warnings rather than failures, because CI runners and clean clones may not have user-level agents installed.
- Treat an existing malformed TOML or any missing/empty required field as an error.
- Emit stable JSON with `schema_version`, `check_name`, `ok`, `checked`, `errors`, `warnings`, and `counts`.
- Register the checker in `tools/safety_rule_script_backing_registry.json` and run it from both JSON and text paths in `tools/run_openspec_guard.py`.
- Keep `tools/ci/ci_test_manifest.json` unchanged in this slice because another active claim owns that hotspot.

## Risks

- The checker may fail on future non-standalone agent TOMLs that intentionally use another structure. Mitigation: this requirement is explicitly for standalone custom-agent TOMLs; future structured variants should update the checker and spec together.
- User-level agents may be absent in CI. Mitigation: missing directories warn rather than fail.
- User-level agents may contain local experiments. Mitigation: failures point to exact files and fields; users can pass `--user-agents-dir` during tests, and local production surfaces should be fixed rather than hidden.

## Rollout

1. Add checker and tests in the feature worktree.
2. Wire the checker into the safety registry and OpenSpec guard.
3. Update AGENTS.md, governance policy, and OpenSpec specs.
4. Run targeted tests, OpenSpec validation, guard, local gate, and local MR review before recommending local main integration.
