## Why

自动协同路由强制化实施计划是 Codex 用户级协同默认行为的 active baseline，但历史补充内容使读取路径变长。上一次 change 使用 Comet tweak 级方式，为文档增加清晰的阅读路径、状态矩阵和 Phase 4 入口。

## What Changes

- 重构 `docs_bilingual/implementation_plans/automatic_orchestration_routing_enforcement_plan.zh-CN.md` 的开头阅读路径。
- 保留 Phase 0-3 已完成、Phase 4 仍 planned follow-up、本文档不是 runtime evidence 的事实。
- 不修改 runtime、checker、用户级资产、本地 main 或远端引用。

## Impact

影响范围仅限中文 implementation plan 与本归档 OpenSpec trace。该 tweak 不证明 experts、durable team 或 persistent team 已运行。

## Validation Path

- `git diff --check` - 检查空白与补丁格式。
- `openspec validate --all` - 验证 OpenSpec 工件。
- `python .\tools\run_openspec_guard.py --root .` - 运行仓库 OpenSpec guard。
- `.\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` - 运行本地 CI gate。
