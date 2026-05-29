# Proposal: 强制 OpenCLI live-start receipt 与 owner evidence 门禁

## Why

用户级 MCP、skills、browser 与 CLI 治理方案中 Task 5 仍保留一项未完成内容：live OpenCLI start 需要 install receipt 与 owner evidence。现有 repo-local OpenCLI guard 已检查 target action、on-demand 模式、browser owner lease、authorization receipt 与 `--port auto` lease evidence，但尚未建模 live-start 自身的 preflight。

## What

- 扩展 `tools/opencli_governance.py`，新增非变更型 `start` preflight 命令。
- live-start 继续前必须有有效 OpenCLI install/update receipt。
- 必须有 active browser-owner lease evidence 与 sanitized `codex-port --port auto` lease evidence。
- repo-local MVP 继续保持不启动：证据齐全时仍 fail closed 为 `live_start_not_implemented_repo_local_mvp`。
- 增加缺 install receipt、缺 owner evidence、证据齐全后仍 deferral 的单元测试。
- 同步到稳定 user-level MCP/skills/browser/CLI governance spec。

## Non-goals

- 不安装、更新或启动 OpenCLI。
- 不启动浏览器，不连接 browser target。
- 不修改 `C:\Users\lenovo\.codex`。
- 不读取 cookies，不执行 JavaScript，不 click/type/navigate，不触碰 human-owned browser assets。
- 不推送远端分支，不开远端 MR。

## Rollback

通过 revert 本地 feature commit，或回到本地集成前创建的 local `main` rollback ref。该小步不修改用户级 runtime state。
