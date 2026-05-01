## 为什么

Codex 现在同时使用直连 MCP server 和 MCP Router。没有书面范围规则时，Codex 专属 MCP server 可能被导入 MCP Router 并作为共享工具暴露，从而带来重复工具面、递归 router entry，以及意外跨客户端访问 Codex 编排状态的风险。

本 change 明确划分边界：Codex 专属 MCP server 保持 Codex 直连；MCP Router 只管理跨客户端通用 MCP server。

## 改动内容

- 新增一份双语 MCP 范围治理策略，用于用户级 Codex 和 MCP Router 配置。
- 新增一个 checker；该 checker 在本地用户级配置可用时验证 Codex 直连 MCP 划分。
- 把 MCP Router 中 Codex 专属 server 或 router 自引用记录报告为 drift。
- 将 checker 集成到仓库聚合 OpenSpec guard。
- 注册安全规则，使该策略由脚本控制支撑，而不是只依赖 prompt 提醒。

## 能力

### 新增能力

- `codex-user-level-mcp-scope-policy`：定义 Codex 专属 MCP server 与 MCP Router 共享 MCP server 的边界。

### 修改能力

- `codex-user-level-safety-rule-script-backing`：把 MCP 范围策略 checker 增加为一个已实现的安全规则脚本控制。

## 影响

影响范围：

- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md`：MCP 范围的英文 ASCII 治理策略。
- `docs_bilingual/governance/codex_user_level_mcp_scope_policy.zh-CN.md`：MCP 范围的 UTF-8 中文对照治理策略。
- `docs_bilingual/docs_registry.yaml`：新策略的文档注册表 entry。
- `tools/check_mcp_router_scope_policy.py`：检查 Codex 直连 MCP 范围并报告 MCP Router drift 的 checker。
- `tools/run_openspec_guard.py`：聚合 guard，用来接入新的 checker。
- `tools/safety_rule_script_backing_registry.json`：安全规则注册表，用来声明该策略已有脚本支撑。
- `test/check_mcp_router_scope_policy.test.py`：checker 的单元测试。
- `openspec/changes/formalize-mcp-router-scope-policy/`：本 change 的 OpenSpec 工件目录。

明确非目标：

- 不从本仓库 change 修改 `C:\Users\lenovo\.codex\config.toml`；该文件是用户级 Codex 配置文件。
- 不从仓库代码编辑 MCP Router 数据库或 UI 状态。
- 不移除浏览器或设计能力。
- 不改变 durable team、LangGraph 或 OpenSpec runtime 行为。
- 不修改消费项目。

发布顺序：

1. 新增双语治理策略和 docs registry entry。
2. 新增 checker 和测试。
3. 将 checker 接入聚合 guard 与安全规则注册表。
4. 本地验证。
5. 通过 GitLab-first workflow 发布。

回滚计划：

- 如果策略或 checker 行为不正确，在合并前回滚本分支。
- 如果已经合并，则回滚 GitLab merge commit，并重新同步 GitHub main。

验证路径：

- `python tools/check_mcp_router_scope_policy.py --root . --json`：验证 MCP 范围 checker 输出。
- `python test/check_mcp_router_scope_policy.test.py`：运行 checker 单元测试。
- `python tools/run_openspec_guard.py --root . --json`：运行仓库聚合 guard。
- `openspec validate --all`：验证 OpenSpec 工件。
- `git diff --check`：验证 diff 没有空白字符问题。
