## 1. 策略工件

- [x] 1.1 新增英文 ASCII MCP 范围治理策略。
- [x] 1.2 新增 UTF-8 中文对照策略。
- [x] 1.3 在 `docs_bilingual/docs_registry.yaml` 中注册该策略；该文件是双语文档注册表。

## 2. Checker 与 guard 集成

- [x] 2.1 新增 `tools/check_mcp_router_scope_policy.py`；该脚本检查 Codex 直连 MCP 范围并报告 MCP Router drift。
- [x] 2.2 新增通过和失败场景的 checker 单元测试。
- [x] 2.3 将 checker 集成到 `tools/run_openspec_guard.py`；该脚本是仓库聚合 OpenSpec guard。
- [x] 2.4 在 `tools/safety_rule_script_backing_registry.json` 中注册安全规则；该文件记录安全规则的脚本支撑关系。

## 3. 验证

- [x] 3.1 运行 `python tools/check_mcp_router_scope_policy.py --root . --json`；该命令执行 MCP 范围 checker 并输出 JSON。
- [x] 3.2 运行 `python test/check_mcp_router_scope_policy.test.py`；该命令执行 checker 单元测试。
- [x] 3.3 运行 `openspec validate --all`；该命令验证全部 OpenSpec spec 和 active change。
- [x] 3.4 运行 `python tools/run_openspec_guard.py --root . --json`；该命令执行仓库聚合 guard。
- [x] 3.5 运行 `git diff --check`；该命令检查 diff 空白字符安全。
