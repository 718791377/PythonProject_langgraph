---
doc_id: project_moe_gui_usage
lang: zh-CN
status: draft
doc_class: operations
related_plan: docs_bilingual/implementation_plans/project_moe_agent_gui_toolchain_plan.zh-CN.md
---

# Project MOE GUI 工具链使用说明

本文覆盖 Phase 2A 的安装器、更新器和检查器。Phase 2A 只安装项目本地 launcher、config、manifest 等受管产物；交互式 PySide6 GUI 属于 Phase 2B。

## 前置条件

目标项目必须先拥有：

- `.codex/agents/<agent>.toml`，且 TOML 顶层 `name` 与安装参数一致；
- 项目本地 MOE CLI，默认 `tools/thesis_moe_mode.py`；
- CLI 支持 `project-status --json`、`list-sessions --json` 和 `status --json`；
- `project-status --json` 返回 `cli_contract = project-moe-cli-v1`。

安装器不会读取或复制目标项目私有 `MOE.md`，不会覆盖 `.codex/agents/*.toml`，也不会写入 `.omx/state`。

## Phase 1 只读 readiness 检查

在对真实目标项目写入 CLI、wrapper 或 GUI 安装产物前，先运行只读 readiness checker。它只读取目标项目，不写文件：

```powershell
python tools/project_moe_gui_toolchain/check_project_moe_phase1_readiness.py `
  --target-project D:\SomeProject `
  --agent-name thesis-moe-mentor `
  --state-namespace thesis_moe `
  --json
```

该检查会验证：

- 目标项目 Git 状态是否干净；
- `.codex/agents/<agent>.toml` 是否存在且核心字段匹配；
- 私有提示源 `MOE.md` 是否留在目标项目内；
- `tools/thesis_moe_mode.py` 是否具备读取契约：`project-status --json`、`list-sessions --json`、`status --json`；
- CLI 文本是否暴露 Phase 1 写命令 surface：`project-on`、`project-off`、`on`、`off`、`assert-on`；
- `thesis-moe-on.cmd` 与 `thesis-moe-off.cmd` 是否分别调用 `project-on` / `project-off`；
- `AGENTS.md` 或启动摘要等入口是否包含 `status --json` 激活检查点。

返回 `read_only = true` 与 `writes_target_project = false` 才能作为只读证据。若返回 `blocked:dirty_target_project`、`blocked:missing_phase1_wrapper` 或 `blocked:missing_moe_activation_hook` 等 token，应先在目标项目内修复或单独授权写入后再继续。

默认 execute-read-contract 模式只会在静态 surface 全部通过后执行目标 CLI。只要目标项目 dirty，或 wrapper、startup、操作者文档、Agent TOML、私有提示源等静态检查仍有 blocker，checker 就会跳过目标 CLI 执行，并在 `cli_contract_check` 中返回 `execution_skipped = true`、`skip_reason = static_surface_blockers_present` 和 `static_surface_blocking_codes`。这可以避免在静态门未通过前触发可能带有 last-seen 或状态副作用的读命令。

## 预览安装

```powershell
python tools/project_moe_gui_toolchain/install_project_moe_gui.py `
  --target-project D:\SomeProject `
  --agent-name thesis-moe-mentor `
  --state-namespace thesis_moe `
  --dry-run --json
```

预览输出包含 `planned_writes`、`planned_skips`、`planned_migrations`、`blockers` 和 `rollback_hint`。`--dry-run` 不写目标项目文件。

## 执行安装

```powershell
python tools/project_moe_gui_toolchain/install_project_moe_gui.py `
  --target-project D:\SomeProject `
  --agent-name thesis-moe-mentor `
  --state-namespace thesis_moe `
  --json
```

安装产物位于目标项目内：

```text
tools/project_moe_gui/launcher.py
tools/project_moe_gui/project_moe_gui.config.json
tools/project_moe_gui/project_moe_gui.install-manifest.json
tools/project_moe_gui/README.md
project-moe-gui.cmd
```

`project-moe-gui.cmd --preflight --json` 只做 launcher 与目标 CLI 预检。完整窗口 GUI 在 Phase 2B 添加。

## 检查和更新

```powershell
python tools/project_moe_gui_toolchain/check_project_moe_gui_install.py --target-project D:\SomeProject --json
python tools/project_moe_gui_toolchain/update_project_moe_gui.py --target-project D:\SomeProject --dry-run --json
python tools/project_moe_gui_toolchain/update_project_moe_gui.py --target-project D:\SomeProject --json
```

检查器会验证 managed files 的 manifest hash。若目标项目手改了受管文件，返回 `blocked:managed_file_hash_mismatch`，更新器不得静默覆盖。

## 预览卸载 / 清理计划

卸载或清理 Project MOE GUI 时，先只生成计划，不直接删除目标项目文件：

```powershell
python tools/project_moe_gui_toolchain/plan_project_moe_gui_uninstall.py `
  --target-project D:\SomeProject `
  --json
```

该命令只读取 `project_moe_gui.install-manifest.json` 和 managed file hash，返回 `planned_deletes` 与 `protected_paths_preserved`。它必须满足：

- `read_only = true`；
- `writes_target_project = false`；
- `apply_supported = true`；
- `state_deletion_allowed = false`；
- `private_files_deletion_allowed = false` - 表示卸载计划不得删除 `MOE.md` 或 `.codex/agents/*.toml` 等目标项目私有文件。

如果 managed file hash 不匹配，返回 `blocked:managed_file_hash_mismatch`，不得把本地改动过的 managed file 当作可删除对象。该计划不删除 `.omx/state`、私有 `MOE.md` 或 `.codex/agents/*.toml`。

确认 `planned_deletes` 后，可以显式传入 `--apply` 执行真正卸载：

```powershell
python tools/project_moe_gui_toolchain/plan_project_moe_gui_uninstall.py `
  --target-project D:\SomeProject `
  --apply --json
```

`--apply` 只会删除 manifest 白名单内、hash 已验证的 Project MOE GUI 受管文件；如果 manifest 试图声明 `MOE.md`、`.codex/agents/*.toml`、`.omx/state` 或其他白名单外路径，命令返回 `blocked:uninstall_path_not_in_managed_allowlist` 并且 `delete_executed = false`。成功时返回 `delete_executed = true`、`applied_file_changes` 和 `uninstall_receipt`。

## 回滚

回滚依赖目标项目 Git 历史和 `project_moe_gui.install-manifest.json`。回滚 GUI 产物时不得删除 `.omx/state`、私有 `MOE.md` 或 Agent TOML。

`project-moe-gui.cmd --preflight --json` 会先执行 Phase 1 readiness gate。若静态 surface 仍有 blocker，launcher 会在 `phase1_readiness_gate`、`remediation_plan` 与 `operator_next_steps` 中返回修复顺序，并跳过目标 CLI 执行，避免在 `.omx/state/<namespace>/` 中产生副作用；launcher 只有在 GUI 控制前提满足时才进入控制路径，遇到 `blocked:dirty_target_project` 等 blocker 必须 fail closed。
