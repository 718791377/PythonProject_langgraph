## Why（原因）

当前 mainline memory summary 仍把较早的 memory-refresh handoff 描述为 active，并且没有记录已完成的 MR 6 readiness review 或之后的 Windows cleanup-output control closeout。冷启动新会话在选择未来 durable routing smoke 或 adoption-gate 工作前，需要先看到最新发布状态。

## What Changes（变更内容）

- 刷新 `sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state` 的英文和中文 mainline memory summaries。
- 记录最新落地增量：MR 6 automatic durable routing readiness、Windows cleanup-output control implementation，以及该 cleanup-output control 的 OpenSpec archive。
- 说明本刷新分支打开前没有 active OpenSpec changes，并且两个本地 archive worktrees 已清理。
- 将下一步 active team-mode / durable-state 工作重述为单独 reviewed smoke 或 adoption-gate change；只有明确 target repository、phase、task 和 operator consent boundary 后才能执行。
- 修复 `openspec/specs/codex-user-level-mainline-memory-handoff/spec.zh-CN.md` 的 UTF-8 中文对照版。该文件英文主版可读，但中文对照版此前存在 mojibake（乱码）。

## Capabilities（能力）

### New Capabilities（新增能力）

- 无。

### Modified Capabilities（修改能力）

- `codex-user-level-mainline-memory-handoff`：说明 cleanup-output closeout 和 durable routing readiness 落地后，当前 mainline memory handoff 必须刷新，并且不得暗示已完成的 MR 6 工作仍需要实施。

## Impact（影响）

### Impact Scope（影响范围）

- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` - 本 change 刷新的英文 mainline memory summary。
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md` - 本 change 刷新的中文 mainline memory summary。
- `openspec/specs/codex-user-level-mainline-memory-handoff/spec.zh-CN.md` - 修复为可读 UTF-8 中文的 stable-spec 中文对照文件。
- `openspec/changes/refresh-mainline-memory-after-cleanup-output-closeout/` - 本次 handoff refresh 的 OpenSpec change artifacts。

### Explicit Non-Goals（明确非目标）

- 本 change 不启动 durable team，也不运行 live `omx-team-auto.ps1`。
- 不修改 `C:\Users\lenovo\.codex\config.toml`；这是用户级 Codex 配置文件。
- 不修改 `.omx/state/`、MCP Router database state、user-level skills、Vercel plugin skills 或 browser automation skills。
- 不把最终的个人生产级持久化 Codex CLI 团队 draft 当成已实现 runtime behavior。

### Rollout Sequence（发布顺序）

1. 在隔离 feature worktree 中创建本 OpenSpec change。
2. 刷新双语 mainline memory summaries。
3. 修复 mainline memory handoff stable spec 的中文对照乱码。
4. 运行 OpenSpec 和仓库治理检查。
5. 按 GitLab-first workflow 发布。

### Rollback Plan（回滚方案）

如果刷新后的 handoff 文本不准确，在合并前回退 feature-branch commit；如果已经合并，则回退对应 GitLab merge commit。

### Validation Path（验证路径）

- `git diff --check` - 检查补丁空白和格式。
- `openspec validate --all` - 验证 stable specs 和 active changes。
- `python tools/check_document_governance_rules.py --root . --json` - 验证双语治理文档注册规则。
- `python tools/check_implementation_plan_rules.py --root . --json` - 验证 implementation-plan 注册规则。
- `python tools/check_name_clarity_rules.py --root . --json` - 验证脚本、路径、命令、变量、profile 和角色名附近有解释。
- `python tools/run_openspec_guard.py --root . --tool codex --json` - 运行仓库 OpenSpec guard bundle。

### Mainline Classification（主线分类）

现有主线：`sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`。