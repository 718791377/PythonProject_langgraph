## Why（为什么）

当前主线 memory handoff 仍然把冷启动会话指向较早的 replay（重放） 和 task-ownership（任务所有权） 工作，但 MCP Router scope policy（MCP Router 范围策略） 与 mainline memory handoff（主线记忆交接） 归档工作已经落地。这样会误导新会话重新打开已完成工作，而不是从真实当前状态开始新的小步 OpenSpec change。

## What Changes（改什么）

- 刷新 startup-facing mainline memory summary（面向启动的主线记忆摘要），让它在列出下一步前先识别最新落地的 MCP scope 与 memory-handoff 增量。
- 把 MCP scope governance document（MCP 范围治理文档）加入启动阅读顺序和仓库指令路由，让 MCP Router 与 Codex 直连 MCP 的问题能落到正确政策上。
- 保持本次更新只改文档：不修改 runtime launcher（运行时启动器）、user-level configuration（用户级配置）、MCP Router database（MCP Router 数据库）或 durable state（持久化状态）。

## Capabilities（能力）

### New Capabilities（新增能力）

- 无。

### Modified Capabilities（修改能力）

- `codex-user-level-mainline-memory-handoff` - 现有 OpenSpec capability（能力），用于定义当前主线 memory summary 如何与最新落地的 governance、checker、tooling 或 workflow 增量保持一致。

## Impact（影响）

影响范围：

- `docs_bilingual/project_startup_summary.md` - 英文 startup summary（启动摘要），用于列出冷启动阅读顺序和当前仓库姿态。
- `docs_bilingual/project_startup_summary.zh-CN.md` - startup summary 的中文对照文件。
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` - 当前命名主线的英文 drift-prone memory handoff（易漂移记忆交接）。
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md` - 当前命名主线 memory handoff 的中文对照文件。
- `AGENTS.md` - 仓库指令入口，用于把后续 MCP scope 问题路由到稳定 policy 文档。
- `openspec/changes/refresh-mainline-memory-after-mcp-scope-policy/` - 本次文档刷新的 OpenSpec change 目录。

明确非目标：

- 不修改 `C:\Users\lenovo\.codex\config.toml`；该文件是用户级 Codex 配置，不属于本仓库变更范围。
- 不修改 MCP Router database 或 UI state；需要时由操作员手动调整 MCP Router 状态。
- 不启用、禁用、启动或删除任何 durable team、LangGraph state 或 native OMX state。
- 不改变 Codex-dedicated MCP server（Codex 专属 MCP 服务器） 安装；本次只澄清交接文本。

发布顺序：

1. 创建本 OpenSpec change 和双语 artifacts（工件）。
2. 刷新 startup summary、AGENTS 路由和当前主线 memory 文件。
3. 本地运行 OpenSpec 与仓库治理检查。
4. 按 GitLab-first MR 流程发布，然后把合并后的同一个 `main` 提交同步到 GitHub。

回滚方案：

- 回滚本次文档提交，或从 Git history（Git 历史）恢复旧的 startup 与 memory summary 文件。
- 因为本次不写仓库外 runtime 或 user-level state，所以不需要运行时状态回滚。

验证路径：

- `openspec validate --all` - 验证全部 OpenSpec changes 与 stable specs。
- `python tools/run_openspec_guard.py --root . --json` - 运行仓库 OpenSpec guard 与治理 checker 组合。
- `python tools/check_document_governance_rules.py --root . --json` - 检查 governance document（治理文档） 注册一致性。
- `python tools/check_name_clarity_rules.py --root . --json` - 检查 docs 中代码化名称是否带简短解释。
- `git diff --check` - 检查补丁空白字符与格式。

主线分类：

- 现有主线：`sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` - post-migration LangGraph capability-gap synchronization（迁移后 LangGraph 能力差距同步） 与相邻 operator-surface maintenance（操作员控制面维护） 的当前命名仓库主线。
