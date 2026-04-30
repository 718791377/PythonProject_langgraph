## 为什么

当前 mainline memory summary 仍然把较早的 official-update replay 增量放在最前面，但最新合入的仓库状态已经包含 task ownership precheck checker。这会误导冷启动会话重新打开已经完成的工作，或漏掉最新的 checker-backed 写入安全边界。

本 change 刷新 mainline 交接信息，让新会话从真实当前状态开始：当前没有 active OpenSpec change，task ownership precheck 已落地，下一步工作需要有意识地重新选择。

## 变更内容

- 更新当前 mainline memory summary，记录 task ownership precheck checker 已落地并归档。
- 增加一条可复用要求：current mainline memory handoff 必须先识别最新落地的 governance、checker 或 tooling 增量，再列出下一步候选动作。
- 保持 repository startup summary 稳定；本 change 只更新容易漂移的 mainline memory 细节。
- 本 change 仅做文档与交接刷新，不引入 runtime 行为变化。

## Capabilities

### New Capabilities
- `codex-user-level-mainline-memory-handoff`：定义 current mainline memory summary 如何记录最新落地增量、active-change 状态和冷启动会话的安全下一步选择。

### Modified Capabilities
- 无。

## 影响范围

影响范围：
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.md` - 英文 current-mainline memory handoff。
- `docs_bilingual/memory/mainline_sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state_startup_summary.zh-CN.md` - 中文 current-mainline memory handoff。
- `openspec/changes/refresh-mainline-memory-after-task-ownership-precheck/` - 本次 documentation-only 更新的 OpenSpec change artifacts。

明确非目标：
- 不改变 `tools/check_session_ownership_claims.py` 行为。
- 不修改 `tools/codex-official-update-patch-replay-template.ps1` runtime 行为。
- 不启动 durable team。
- 不改变 GitLab/GitHub 发布策略。
- 不修改 consumer projects；本 change 仅限当前仓库内的文档与 OpenSpec artifacts。

发布顺序：
1. 创建本 OpenSpec change 及其中英文 artifacts。
2. 更新当前 mainline memory summary 中英文文件。
3. 运行 OpenSpec 与仓库治理检查。
4. 如果用户要求发布，再提交到 feature branch 并遵循 GitLab-first 发布流程。

回滚计划：
- 如果交接措辞不正确，在合并前 revert 本 feature branch。
- 如果已经合并，则在 GitLab main revert 该 merge commit，再同步 GitHub main。

验证路径：
- `openspec validate --all` - 验证 active OpenSpec changes 与 stable specs。
- `python tools/check_document_governance_rules.py --root . --json` - 验证双语 governance/document 规则。
- `python tools/check_implementation_plan_rules.py --root . --json` - 验证 implementation-plan registry 规则。
- `python tools/run_openspec_guard.py --root . --json` - 运行聚合 OpenSpec guard。
- `git diff --check` - 验证 diff 没有空白问题。

主线分类：
- 现有 mainline maintenance：`sync-langgraph-capability-gap-after-migration-aware-live-primary-engine-compatibility-state`。
