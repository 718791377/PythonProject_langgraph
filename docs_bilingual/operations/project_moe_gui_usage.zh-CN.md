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

## 回滚

回滚依赖目标项目 Git 历史和 `project_moe_gui.install-manifest.json`。回滚 GUI 产物时不得删除 `.omx/state`、私有 `MOE.md` 或 Agent TOML。
