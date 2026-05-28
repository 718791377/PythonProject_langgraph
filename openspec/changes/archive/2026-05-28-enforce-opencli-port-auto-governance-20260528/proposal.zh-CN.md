# 提案：强制 OpenCLI 自动端口治理

## 为什么

用户级 MCP、skills、browser 与 CLI 治理方案要求 OpenCLI 使用分配器驱动的 `--port auto`，并提供 `codex-port` 租约证据。仓库本地 OpenCLI 治理门禁已经强制执行按需模式、浏览器 owner 证据与敏感操作授权 receipt，但在收到硬编码 OpenCLI 端口或缺失端口租约时还没有 fail closed。

## 做什么

- 扩展 `tools/opencli_governance.py`，增加显式端口策略门禁。
- 要求 OpenCLI pre-dispatch 检查必须使用 `--port auto`。
- 要求提供已清洗的 `codex-port` 租约 receipt，并且端口必须位于 Codex browser/OpenCLI 范围 `39300-39499`。
- 增加单元测试，证明缺失端口租约、硬编码端口、错误端口范围都会 fail closed。
- 在归档时把该行为提升到稳定的用户级 MCP/skills/browser/CLI 治理 spec。

## 非目标

- 不安装、启动或更新 OpenCLI。
- 不在 fixture receipt 之外分配真实用户级端口。
- 不修改 `C:\Users\lenovo\.codex`。
- 不推送远端分支，也不创建远端 MR。

## 回滚

通过 revert 本地 feature commit，或把本地 `main` reset 到合入前创建的 rollback ref 来回滚。本变更不修改任何用户级运行时状态。
