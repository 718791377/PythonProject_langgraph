## 为什么

当前 mainline memory summary 仍把 MCP scope refresh 写成最新 handoff，但仓库后来已经落地并归档 Codex direct browser/design MCP policy 和 durable rollout status-sync 工作。冷启动会话需要读取最新发布状态，避免重新打开 MR 5 durable-state 工作或过期的 MCP-scope 后续任务。

## 变更内容

- 刷新 `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` 的英文与中文 mainline memory summaries。
- 记录最新落地增量：Codex direct browser/design MCP policy、durable rollout plan status sync、中文状态文本修复和归档 closeout。
- 更新发布与 active-change 交接文字，记录本刷新分支开始时 `main` / `gitlab/main` / `github/main` 均位于 `b822343`。
- 将安全下一步重述为 MR 6 readiness 或单独命名的后续 changes，而不是已经完成的 MR 5 工作。

## 能力

### 新增能力

- 无。

### 修改的能力

- `codex-user-level-mainline-memory-handoff`：澄清 durable rollout status-sync archive work 落地后也应刷新 mainline memory handoff，尤其是旧 implementation plan 不再指向真实下一步切片时。

## 影响

### 影响范围

- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` - 本 change 刷新的英文 mainline memory summary。
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md` - 本 change 刷新的中文 companion mainline memory summary。
- `openspec/changes/refresh-mainline-memory-after-durable-rollout-status-sync/` - 本 handoff refresh 的 OpenSpec change artifacts。

### 明确非目标

- 不修改 user-level skills、Vercel plugin skills、browser automation skills 或 `C:\Users\lenovo\.codex\config.toml`。
- 不修改 `.omx/state/`、MCP Router database state 或 user-level MCP configuration。
- 不在本 change 中实施 MR 6 automatic durable routing。
- 当另一个 active session 拥有 broad `openspec/specs` 范围时，不归档本 change；归档必须等该 ownership 清理后在串行 archive worktree 中执行。

### 发布顺序

1. 在隔离 feature worktree 中创建本 OpenSpec change。
2. 刷新双语 mainline memory summaries。
3. 运行 OpenSpec 和仓库治理验证。
4. 通过 GitLab-first workflow 发布。
5. 等 stable-spec ownership 清理后，再在串行 archive worktree 中归档。

### 回滚方案

合并前可 revert feature branch commit；合并后如 handoff 文案被证明不准确，可 revert GitLab merge commit。

### 验证路径

- `git diff --check` - 检查 whitespace 与 patch formatting。
- `openspec validate --all` - 验证 stable specs 与 active changes。
- `python tools/check_document_governance_rules.py --root . --json` - 验证双语 governance document registry 规则。
- `python tools/check_implementation_plan_rules.py --root . --json` - 验证 implementation-plan registry 规则。
- `python tools/run_openspec_guard.py --root . --json` - 运行仓库 OpenSpec guard bundle。

### 主线分类

既有主线：`sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`。
