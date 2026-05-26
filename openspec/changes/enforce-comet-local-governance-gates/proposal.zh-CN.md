# 变更：强制 Comet 本地治理门禁

## 原因
仓库需要为更正后的 Comet 治理规则提供可执行控制：已确认 `/plan` 后，非文档类实施必须先落地本地治理包，以 `docs_bilingual/` 作为第一持久化决策面，再按需要派生 `openspec/` 和 `docs/`，并强制 Markdown 中英文对、中文提交主题，以及实施前 implementation plan 为 active。

## 变更内容
- 更新仓库治理文档，明确 docs_bilingual-first 路由和完整本地提交流程行为。
- 新增对 `docs_bilingual/`、`openspec/`、`docs/` 下已变更 Markdown 文件的前向双语成对检查。
- 新增本地 commit 与 local MR review 的中文提交主题检查。
- 扩展 implementation-plan 检查，使 Comet build/verify/archive 阶段引用的 implementation plan 必须为 active。
- 记录新的稳定 OpenSpec 需求。

## 影响
- 本地 feature branch 在合入本地 `main` 前会受到更严格门禁。
- 未变更的历史 Markdown 缺口作为 baseline，不阻断无关工作。
- 远端发布仍单独门控。
