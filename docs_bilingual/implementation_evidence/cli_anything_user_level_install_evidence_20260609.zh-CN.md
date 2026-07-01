# CLI-Anything 用户级安装证据 - 2026-06-09

## 摘要

- Source：`https://github.com/HKUDS/CLI-Anything`。
- 已安装用户级 Codex skills：`cli-anything` 与 `cli-hub-meta-skill`。
- 已安装 Python package：`cli-anything-hub==0.3.0`。
- Smoke command：`cli-hub --help`。
- Version command：`cli-hub --version` 返回 `cli-hub 0.3.0`。
- Receipt：ignored local receipt `.omx/cli-anything/cli-anything.lock.json`。
- Receipt status：`installed-user-level`。
- Remote publication mutated：`false`。

## Receipt 验证

`python tools\cli_anything_governance.py validate --receipt .omx\cli-anything\cli-anything.lock.json --json` 已通过，关键字段为：

- `install_performed=true` - receipt 记录用户级 CLI-Anything 安装已经执行。
- `network_fetch_performed=true` - receipt 记录安装使用了网络 fetch/install 步骤。
- `user_level_config_mutated=false` - 安装未修改用户级 Codex 配置文件。
- `wxwork_cli_installed=false` - 本仓库 package 未安装 WXWork_CLI surface。
- `wxwork_cli_controlled=false` - 本仓库 package 未启动或控制 WXWork_CLI / WXWork.exe。
- `source_url=https://github.com/HKUDS/CLI-Anything` - source URL 保持可见，因为它不是 private path。
- Smoke result: pass - bounded `cli-hub --help` smoke evidence completed successfully.

脱敏后的 receipt hashes：

- receipt path hash：`c48f3b6f51f0a146`
- install path hash：`9c9e532db9c4773c`
- wrapper path hash：`ba63c2f93d4be132`
- state path hash：`f0744b4573cbb903`
- rollback pointer hash：`5fd81dfe573883dd`

## WXWork_CLI 边界

本仓库 package 未安装、启动或控制 `WXWork_CLI`。后续 `WXWork_CLI` 接入交给 `D:\PythonProject_OpenClaw` / PythonProject_OpenClaw。此 package 未启动、控制或发送 `WXWork.exe` / WXWork 消息。

## 官方 Codex Skill 安装补充

- 本次补齐安装使用的官方 source commit：`0a19072f8810afea6f00089226f9f7d06bd2de04`。
- 使用的官方 Codex installer：`codex-skill/scripts/install.ps1`，来源 `https://github.com/HKUDS/CLI-Anything`。
- 已确认官方 Codex skill 安装位置：`C:\Users\lenovo\.codex\skills\cli-anything`。
- 已确认官方 CLI-Hub meta-skill 安装位置：`C:\Users\lenovo\.codex\skills\cli-hub-meta-skill`。
- `C:\Users\lenovo\.agents\skills` 下保留兼容副本，但当前 Codex 用户级 skill surface 是 `.codex\skills`。
- Git for Windows `bash` 可用，路径为 `D:\Program Files\Git\bin\bash.exe`，匹配 upstream Windows 工作流提示。
- WXWork_CLI 仍交由 `D:\PythonProject_OpenClaw` 接入；本仓库 package 仍不安装、启动、控制或通过 WXWork_CLI 发送消息。
