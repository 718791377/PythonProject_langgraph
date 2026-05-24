---
doc_id: project_moe_paper_suggest_static_readiness_evidence_2026_05_24
lang: en
status: active
doc_class: memory_evidence
created_at: 2026-05-24
related_plan: docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.md
---

# Project MOE paper_suggest static readiness evidence - 2026-05-24

## Scope

This evidence records a read-only/static-only readiness check for `D:\PythonProject_paper_suggest`. It does not read or copy the project-private `MOE.md` body and does not write target-project files.

## Command

```powershell
python .\tools\project_moe_gui_toolchain\check_project_moe_phase1_readiness.py --target-project D:\PythonProject_paper_suggest --agent-name thesis-moe-mentor --state-namespace thesis_moe --static-only --json
```

- Exit code: `1`
- Target project root: `D:\PythonProject_paper_suggest`
- Read-only: `True`
- Writes target project: `False`
- CLI execution mode: `static-only`

## Result

- Readiness status: `blocked`
- Adaptation lane: `repair`
- Control mode allowed: `False`

Conclusion: this is a **static-only no-go / repair-lane result**, not Ready Lane control approval. The MOE GUI must not control `paper_suggest` until the blockers below are fixed and a later readiness check passes.

## Read-only Git preflight evidence

- `git_status.token`: `blocked:dirty_target_project`
- `git_status.dirty`: `True`
- `git_status.dirty_count`: `4`
- `git_status.read_only_git_optional_locks`: `True`
- `git_status.git_optional_locks`: `0`
- Dirty sample:
  - ` M docs_bilingual/operations/cad_fem_api_automation_usage.md` - target-project operations documentation is dirty.
  - ` M docs_bilingual/operations/cad_fem_api_automation_usage.zh-CN.md` - target-project bilingual operations documentation is dirty.
  - ` M test/test_cad_fem_automation_contract.py` - target-project automation contract test is dirty.
  - ` M tools/cad_fem_automation/cad_fem_orchestrator.py` - target-project automation orchestrator code is dirty.

## Surface evidence

- Agent TOML exists: `True`
- Agent TOML standard profile ready: `False`
- Agent TOML required fields OK: `True`
- Private prompt source exists: `True`
- Private prompt boundary OK: `True`
- Mode CLI exists: `True`
- Read command tokens seen: `project-status, list-sessions, status, assert-on`
- Write command tokens seen: `project-on, project-off, on, off, assert-on`
- CLI contract execution skipped: `True`
- CLI contract skip reason: `static_only_no_exec_cli`
- Startup activation hook found: `True`
- Operator docs ready: `True`

| Wrapper | Exists | References CLI | References command | Passes `--json` | Unsafe tokens |
| --- | --- | --- | --- | --- | --- |
| on | yes | yes | yes | no | `>` |
| off | yes | yes | yes | no | `>` |

## Blocker codes

- `blocked:dirty_target_project` - target project has unclassified dirty files.
- `blocked:agent_toml_missing_extension_sections` - Agent TOML is missing the Project MOE standard extension sections.
- `blocked:agent_project_boundary_invalid` - Agent TOML project boundary fields do not match the standard.
- `blocked:agent_state_namespace_mismatch` - Agent TOML state namespace is missing or mismatched.
- `blocked:agent_moe_boundary_invalid` - Agent TOML MOE state-boundary fields do not match the standard.
- `blocked:agent_dispatch_boundary_incomplete` - Agent TOML dispatch mode, forbid list, or fallbacks are incomplete.
- `blocked:phase1_wrapper_json_output_missing` - wrapper does not pass `--json` for machine-readable output.
- `blocked:phase1_wrapper_unsafe_shell_surface` - wrapper exposes a shell-surface token that must be removed or justified.

## Boundary note

Static-only evidence is intentionally conservative. It proves only file-surface observations plus the read-only Git preflight. It does not prove the target CLI read contract can execute without side effects, and it does not authorize GUI install/control.
