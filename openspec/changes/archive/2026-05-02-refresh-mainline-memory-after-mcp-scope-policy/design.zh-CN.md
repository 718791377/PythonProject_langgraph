## Overview（概览）

本 change 是一次 documentation and handoff refresh（文档与交接刷新）。它会更新新 Codex 会话在实施前读取的冷启动表面，避免继续把已经完成的 replay（重放） 或 task-ownership（任务所有权） 工作描述成下一步。

## Design（设计）

刷新沿用现有 handoff layering（交接分层）：

- `AGENTS.md` - 仓库指令入口，用来把 MCP scope 问题路由到稳定 governance policy。
- `docs_bilingual/project_startup_summary.md` - 英文仓库级 startup summary，用来保持稳定入口并把易漂移细节指向其他文件。
- `docs_bilingual/project_startup_summary.zh-CN.md` - 仓库级 startup summary 的中文对照文件。
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` - 当前主线英文 memory handoff，用来承载快速变化的执行细节。
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md` - 当前主线 memory handoff 的中文对照文件。

memory handoff 将先识别最新落地的增量：

- `formalize-mcp-router-scope-policy` - 已归档的 OpenSpec change，用来引入 MCP Router 与 Codex 直连 MCP 的范围策略。
- `codex-user-level-mcp-scope-policy` - 稳定 OpenSpec spec，用来记录 MCP Router scope requirements。
- `refresh-mainline-memory-after-task-ownership-precheck` - 已归档的 OpenSpec change，用来引入 mainline memory handoff requirement。
- current publication refs（当前发布引用） - 继续前应检查本地 `main`、`gitlab/main` 与 `github/main`，并在 memory handoff 中描述。

## Safety Boundaries（安全边界）

- 不允许写 user-level configuration（用户级配置）。尤其是 `C:\Users\lenovo\.codex\config.toml` 不由本 change 修改。
- 不允许写 MCP Router database（MCP Router 数据库）。仓库可以记录和检查策略，但 MCP Router UI 与数据库状态由操作员控制。
- 不启动 durable backend（持久化后端）。本 change 不启动 native OMX、LangGraph 或 durable team。
- 不生成 runtime helper（运行时辅助脚本）。本 change 只更新仓库文档与 OpenSpec artifacts。

## Validation（验证）

验证以本地只读为主，只允许常规测试在仓库 checkout 内生成必要产物：

- `openspec validate --all` - 验证 OpenSpec change 与 stable spec 语法。
- `python tools/run_openspec_guard.py --root . --json` - 运行仓库 guard bundle（门禁检查组合）。
- `python tools/check_name_clarity_rules.py --root . --json` - 检查 `docs_bilingual/` 与 `openspec/` 中的名称解释覆盖。
- `git diff --check` - 检查补丁格式。
