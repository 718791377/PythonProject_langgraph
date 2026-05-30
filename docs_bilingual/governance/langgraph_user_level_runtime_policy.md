---
doc_id: langgraph_user_level_runtime_policy
lang: en
doc_class: governance
status: active
---

# LangGraph User-Level Runtime Policy

## 1. Purpose

This document defines the standard repository rule for where the official `langgraph` runtime lives, where repo-local LangGraph compatibility code lives, and how LangGraph installs should be performed for this Codex orchestration line.

## 2. Boundary Model

- The user-level shared runtime layer may be reused across many `PyCharm / Codex CLI` projects on the same machine, user account, and Codex home.
- The official `langgraph` Python package is an upstream dependency, not a repository-local implementation.
- The optional `langgraph-cli[inmem]` package is a user-level tool dependency for local server or CLI workflows, not part of the repo-local compatibility source.
- This repository owns the repo-local compatibility and orchestration source under `tools/langgraph_durable_orchestrator/`.
- This repository also owns the repo-local durable runtime state under `.omx/state/langgraph/`.
- Any generated user-level helper copy under `C:\Users\lenovo\.codex\python\...` is an install artifact only. The repository source remains the authority.
- The shared venv and generated helper layer must not host or centralize any repository's canonical durable state.

## 3. Standard Paths

Use the following standard layout unless a later governance change explicitly replaces it:

1. user-level shared LangGraph venv:
   `C:\Users\lenovo\.codex\venvs\langgraph-py312\`
2. optional generated user-level helper artifact root:
   `C:\Users\lenovo\.codex\python\langgraph_durable_orchestrator\`
3. UTF-8-safe user-level official LangGraph CLI wrapper:
   `C:\Users\lenovo\.codex\bin\omx-langgraph-cli.ps1`
4. repo-local compatibility and orchestration source:
   `D:\PythonProject_langgraph\tools\langgraph_durable_orchestrator\`
5. repo-local LangGraph durable state:
   `D:\PythonProject_langgraph\.omx\state\langgraph\`

The shared venv is for user-level Codex or OMX runtime access across projects. The repo-local source tree is for implementation and tests. The repo-local `.omx/state/langgraph/` tree is for per-repository durable state.

## 4. Standard Install Commands

Prefer a shared Python 3.12 venv on this machine. Python 3.11 or newer is required when `langgraph-cli[inmem]` is needed for local server workflows.

Create the shared venv:

```powershell
py -3.12 -m venv C:\Users\lenovo\.codex\venvs\langgraph-py312
```

Upgrade pip in that venv through the Aliyun mirror:

```powershell
C:\Users\lenovo\.codex\venvs\langgraph-py312\Scripts\python.exe -m pip --isolated install --upgrade pip --index-url https://mirrors.aliyun.com/pypi/simple/
```

Install or upgrade the official LangGraph package:

```powershell
C:\Users\lenovo\.codex\venvs\langgraph-py312\Scripts\python.exe -m pip --isolated install --upgrade --index-url https://mirrors.aliyun.com/pypi/simple/ langgraph
```

Install the optional local-server CLI only when needed:

```powershell
C:\Users\lenovo\.codex\venvs\langgraph-py312\Scripts\python.exe -m pip --isolated install --upgrade --index-url https://mirrors.aliyun.com/pypi/simple/ "langgraph-cli[inmem]"
```

When the official CLI is installed and the Windows terminal is not already UTF-8 clean, prefer the user-level wrapper:

```powershell
omx-langgraph-cli.ps1 --help
omx-langgraph-cli.ps1 dev --help
```

## 5. Pip Mirror Rule

- Use `python.exe -m pip`, not bare `pip`.
- Pass the Aliyun mirror through `--index-url https://mirrors.aliyun.com/pypi/simple/` per command.
- Do not make persistent global `pip config` changes as the default repository rule.
- Do not use `--extra-index-url` for this mirror.
- Do not use `--trusted-host` unless certificate validation is actually broken and a temporary exception is documented.

## 6. Repository Rules

- Do not install the official `langgraph` package into this repository tree as the primary shared runtime location.
- Do not treat the global Python site-packages directory as the stable long-term home for the LangGraph runtime.
- Do not move repo-local `.omx/state/langgraph/` state into the user-level shared venv or another shared runtime directory.
- Do not treat the user-level shared runtime as a cross-project durable-state pool.
- Do not treat generated helper copies under `C:\Users\lenovo\.codex\python\` as the source of truth.
- Do not vendor or fork the official LangGraph package into `tools/langgraph_durable_orchestrator/`.
- Keep user-facing state language explicit: `installed`, `enabled`, `selected`, and `ready` are different states.
- Durable capability readiness projections must publish `readiness_fields = [installed, enabled, selected, ready]` and must not collapse those fields into one availability flag.
  - `installed` means the lane's required helper or runtime artifact is present.
  - `enabled` means the user-level capability switches allow that lane.
  - `selected` means the user-level backend selector or repo-local tracked state points at that lane.
  - `ready` means `installed && enabled && selected` for that lane; selected-but-not-installed and enabled-but-not-selected remain not ready.
- `backend_default` is the user-level selected backend compatibility view, and `backend_ready` is the readiness result for that selected backend only. `backend_ready=true` does not mean a durable workflow, tracked LangGraph thread, or persistent team is already running or adopted for the current task.
- On Windows terminals that still default to a non-UTF-8 console encoding, do not rely on direct `langgraph.exe --help` or `langgraph.exe dev --help`; use `omx-langgraph-cli.ps1` instead.

## 7. Project-Level Exception Rule

If a separate PyCharm or Codex CLI project directly imports `langgraph` in its own application code, that project must still declare and install its own dependency set in its own project environment. The user-level shared venv does not replace project-local dependency management for application code.

## 8. Startup Read Hint

Read this document when a task asks any of the following:

- where LangGraph should be installed
- where repo-local compatibility code belongs
- where repo-local durable state belongs
- how to install or upgrade LangGraph with the Aliyun pip mirror
- how to use the UTF-8-safe official LangGraph CLI wrapper on Windows
