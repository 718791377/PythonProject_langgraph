---
doc_id: general_2_local_git_openspec_subagents_only_bootstrap_plan
lang: en
canonical: docs_bilingual/implementation_plans/general_2_local_git_openspec_subagents_only_bootstrap_plan.md
zh_cn_path: docs_bilingual/implementation_plans/general_2_local_git_openspec_subagents_only_bootstrap_plan.zh-CN.md
status: active-local-plan
updated_at: 2026-05-27
target_template: D:\PythonProject_General_2
comet_change: refactor-general-template-plans-comet
capability_tier: local-git-openspec-superpowers-native-subagents-only
---

# D:\PythonProject_General_2 Local Git + OpenSpec + Superpowers + native Codex subagents Template Plan

## 1. Goal

`D:\PythonProject_General_2` is the lightweight local template for projects that do not need a remote repository or durable orchestration. It provides local Git, OpenSpec, Superpowers governance practices, and native Codex subagent configuration only. It does not enable oh-my-codex, native_omx, LangGraph durable backend, remote CI/MR, or `.omx/state/` runtime state.

Success means a future cold-start session can read this plan and generate or repair the target template without mistaking `D:\PythonProject_langgraph` live session facts, user-level configuration, remote publication workflow, or LangGraph runtime state for current General_2 capabilities.

## 2. Capability Boundary

### 2.1 Enabled Capabilities

- Local Git: `git init -b main` creates local history and does not configure `origin`, `gitlab`, or `github` remotes by default.
- OpenSpec: `openspec/` stores local proposal, design, spec, and tasks files as the WHAT and lifecycle governance layer.
- Superpowers: Superpowers skills provide HOW practices such as brainstorming, writing-plans, executing-plans, and verification-before-completion.
- Comet: `/comet` means the OpenSpec + Superpowers governance workflow for Open, Design, Build, Verify, and Archive evidence. It is not a native subagent, oh-my-codex, native_omx, LangGraph, or a durable-team backend.
- native Codex subagents: `.codex/agents/` stores project-local native agent TOML files; every TOML must define `name`, `description`, and `developer_instructions`.

### 2.2 Disabled Capabilities

- Do not configure GitLab/GitHub remotes, `.gitlab-ci.yml`, or `.github/workflows/`.
- Do not install or call oh-my-codex, native_omx, LangGraph durable backend, a LangGraph CLI wrapper, or `.omx/state/`.
- Do not copy `C:\Users\lenovo\.codex\config.toml`, tokens, `.env`, credential caches, `.venv/`, `node_modules/`, or `.git/`.
- Do not turn `D:\PythonProject_langgraph` current mainline, active worktree claims, Comet state, LangGraph state, or literal prompt-sentinel text into template defaults.

## 3. Target Directory Shape

```text
D:\PythonProject_General_2
|-- AGENTS.md
|-- README.md
|-- TEMPLATE_MANIFEST.md
|-- .gitignore
|-- .codex\agents\
|-- template_assets\codex-agents\
|-- docs_bilingual\project_startup_summary.md
|-- docs_bilingual\project_startup_summary.zh-CN.md
|-- docs_bilingual\governance\
|-- openspec\changes\
|-- openspec\specs\
`-- tools\
```

Key meanings:

- `.codex\agents\` is the project-level native subagent TOML directory read by Codex.
- `template_assets\codex-agents\` is the distributable copy used for compare, restore, or user-level installation.
- `docs_bilingual\project_startup_summary.md` and `.zh-CN.md` are the cold-start summary pair; any future literal context sentinel belongs only there.
- `openspec\changes\` and `openspec\specs\` are local OpenSpec governance directories and do not require a remote repository.
- `tools\` stores bootstrap, checker, and local gate scripts; scripts must use `$env:USERPROFILE` or parameters instead of hard-coding `C:\Users\lenovo`.

## 4. Implementation Sequence

1. Back up the target directory: if `D:\PythonProject_General_2` already exists, run `git status --short`; stop and report when local changes exist.
2. Write base documents: update `AGENTS.md`, `README.md`, `TEMPLATE_MANIFEST.md`, startup summaries, and governance documents with the local-only boundary.
3. Initialize OpenSpec: create `openspec/changes/`, `openspec/specs/`, and a local example change; do not copy this repository's active changes or archive history.
4. Sync native agents: keep `.codex/agents/` and `template_assets/codex-agents/` aligned by file name and TOML schema; back up same-name user-level agents before installation.
5. Write local scripts: provide bootstrap, subagent install, template health, subagent-only, TOML schema, bilingual-pair, and local-Git-only checkers.
6. Initialize local Git only after user confirmation: run `git init -b main`, `git add .`, and a local initial commit without adding remotes.

## 5. Validation Commands

Run from `D:\PythonProject_General_2`:

```powershell
python .\tools\check_template_health.py --root .
python .\tools\check_subagent_only_policy.py --root .
python .\tools\check_custom_agent_toml_schema.py --root .
python .\tools\check_bilingual_pairs.py --root .
python .\tools\check_local_git_only_policy.py --root .
openspec validate --all
git diff --check
git status --short
```

## 6. Acceptance Criteria

- General_2 remains local Git + OpenSpec + Superpowers + native Codex subagents only.
- `.codex/agents/` and `template_assets/codex-agents/` stay paired, and every agent TOML has required fields.
- The target directory has no `.omx/state/`, `.omx/session-claims/`, LangGraph runtime, oh-my-codex launcher, GitLab/GitHub remote, or remote CI configuration.
- Scripts are idempotent and report before overwriting existing targets or user-level agents.
- Chinese documents are UTF-8 clean and contain no mojibake copied from terminal output.

## 7. Rollback

- Rename a bad target directory to `D:\PythonProject_General_2.backup.<timestamp>` before manual cleanup.
- Restore user-level agents from `%USERPROFILE%\.codex\agents.backup.<timestamp>\`.
- Undo pip user mirror settings with `python -m pip config --user unset global.index-url` and `python -m pip config --user unset global.timeout`.
- Delete `.git/` only manually after confirming there are no commits to keep.
- Recover OpenSpec files by inspecting `git status --short` and reverting the listed files, not by automatically clearing `openspec/`.
