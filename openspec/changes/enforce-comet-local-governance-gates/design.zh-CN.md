# 设计：强制 Comet 本地治理门禁

## 决策
- 保持 `docs_bilingual/` 作为第一持久化决策面，但不把每个决策都强制放入 `implementation_plans/`。
- 将 `openspec/` 和 `docs/` 作为派生表面：只有任务自身需要 stable spec lifecycle evidence 或 Superpowers runtime artifacts 时才更新。
- 只对已变更文件执行 Markdown 双语成对门禁，使 legacy archive 缺口不阻断无关工作。
- 使用独立 checker 与 commit-msg hook 强制中文提交主题；当主题包含中文时仍允许 ASCII conventional prefix。
- 复用既有 implementation-plan checker 执行 active-plan 规则，因为该脚本已经负责 registry 完整性。

- 新增静态 local-flow checker，并把 `/plan` 后范围 checker 接入 local MR review。

## 验证
- 单元测试覆盖文档对策略、提交语言和 active-plan 引用。
- aggregate guard 运行新检查。
- local MR review 针对 feature branch range 运行提交语言检查。
