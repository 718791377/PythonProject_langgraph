## 概览

本 change 是一次文档与交接刷新。它不改变 runtime orchestration、durable-state selection、OpenSpec guard 逻辑或发布流程行为。

关键设计选择是：稳定的仓库入口事实继续保留在 `docs_bilingual/project_startup_summary.md`，容易漂移的当前进展细节则放入当前 mainline memory summary。

## 当前状态

仓库当前没有 active OpenSpec changes，最新 mainline 工作已通过 `automate-task-ownership-precheck-checker` 落地。当前 mainline memory summary 仍以较早的 operator-surface replay 工作开头；该内容仍有效，但已经不是最新落地增量。

## 目标状态

当前 mainline memory summary 应当在靠前位置明确说明：

- `tools/check_session_ownership_claims.py` - 现在支持写入前 task ownership precheck signals 的 checker。
- `automate-task-ownership-precheck-checker` - 最新归档的 OpenSpec change，落地了 checker-backed task ownership precheck 增量。
- `openspec status` - 用于在选择新增量前确认没有 active OpenSpec changes 的命令。
- `doc-refresh-mainline-memory-task-ownership` - 本次 memory refresh 工作使用的 feature branch。

该 summary 应列出安全的下一步选择，而不是把较早的 replay 增量表现成唯一 active target。

## 边界

范围内：
- 更新当前 mainline memory summaries。
- 添加 OpenSpec artifacts，并增加 current-mainline handoff freshness 的稳定要求。

范围外：
- Runtime 代码变更。
- Durable team 启动或 backend selection。
- Consumer project 修改。
- GitLab/GitHub 发布自动化。

## 验证

本 change 依赖现有仓库验证：

- `openspec validate --all` - OpenSpec 结构验证。
- `python tools/run_openspec_guard.py --root . --json` - 聚合仓库 guard。
- `git diff --check` - 空白验证。
