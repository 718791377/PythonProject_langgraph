# codex-user-level-comet-controlled-openspec-superpowers 规格中文对照

## 新增需求：`/plan` 后执行必须先进入 docs_bilingual 治理包

当已确认的 `/plan` 退出并进入非纯文档任务执行时，仓库必须先创建或更新本地治理包，再开始 runtime 或代码实现。

治理包必须先更新 `docs_bilingual/`，并按最合适的 doc_class 与目录选择落点；有合适既有文件时优先更新既有文件，不得把 `implementation_plans/` 当成唯一目标。

`openspec/` 与 `docs/` 更新必须由 `docs_bilingual/` 决策派生：只有需要 durable capability、spec lifecycle、structural governance 或 stable requirement evidence 时才更新 `openspec/`；只有需要 Superpowers runtime artifacts 或改变 `docs/` 目录契约本身时才更新 `docs/`。

### 场景：非文档实施跟随 `/plan`
- **WHEN** 用户要求会话实施已确认的非纯文档方案
- **THEN** 会话必须先更新合适的 `docs_bilingual/` governance、guide、memory、product-lifecycle 或 implementation-plan 表面
- **AND** 必须先把本地治理包合入本地 `main`，再继续代码或 runtime 实施

### 场景：docs_bilingual 更新不自动意味着 OpenSpec 或 docs 文件
- **WHEN** `docs_bilingual/` 更新已经完整承载本地治理决策
- **THEN** 会话不得仅因为 `docs_bilingual/` 变更就创建 `openspec/` 或 `docs/` artifacts
- **AND** 额外 `openspec/` 或 `docs/` 文件必须由任务内容自身证明需要
