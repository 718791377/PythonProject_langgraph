# 设计：OpenCLI 自动端口治理

## 边界

本变更仅限 repo-local。它只建模 OpenCLI pre-dispatch 治理，不安装 OpenCLI、不打开浏览器、不绑定端口，也不修改用户级配置。

## 方法

`opencli_governance.py` 在允许 dispatch 前评估三个相互独立的门禁：

1. adapter gate：OpenCLI 保持 `on-demand`；
2. port gate：请求的端口模式必须是 `auto`，并且已清洗的 `codex-port` lease receipt 必须证明 Codex 拥有 `39300-39499` 范围内的租约；
3. target/action gate：面向目标的操作必须提供 browser owner lease，敏感操作必须提供 authorization receipt。

port gate 在测试中有意接受 fixture receipt，而不是直接调用 `codex-port`，因为该 guard 必须保持确定性且不产生运行时副作用。

## 验收证据

- `python test/cdp_bridge_governance.test.py`：验证 CDP Bridge / OpenCLI 治理路径的目标单元测试。
- `python tools/check_user_level_mcp_skills_browser_cli_baseline.py --root . --json`：验证用户级 MCP/skills/browser/CLI 治理基线。
- `python tools/run_openspec_guard.py --root . --json`：验证 OpenSpec 与仓库治理门禁。
- local gate 与 local MR review：在合入本地 `main` 前提供完整本地质量证据。
