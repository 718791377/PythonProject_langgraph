# 任务：改进 Skills2CLI Profile 路由

## Stage A：冻结方案

- [x] 创建基于场景的 profile routing 双语 implementation plan。
- [x] 创建 OpenSpec change，包含 proposal、design、tasks 和 delta spec。
- [x] 将 skills usage audit plan 关联为 advisory routing/rerank 输入。
- [x] 在 docs registry 中登记本双语方案。
- [x] 验证并提交 Stage A 方案冻结包。
- [x] 将 Stage A 集成到本地 `main`。

## Stage B：实现 live runtime

- [x] 扩展 `profiles.json`，加入场景 metadata、negative examples、ranking signals 和 task modules。
- [x] 扩展 plugin-modules scripts，支持 `profile.task_module` soft-load 和 top-level-only hard-load。
- [x] 添加 `skills2cli.py profile suggest`，输出可解释的 recall/rerank 结果。
- [x] 添加 checker 和测试，覆盖 schema、only-`full` coverage、`full` fallback discipline 和 installed-copy drift reporting。
- [x] 通过代表性 suggestions、OpenSpec guard、local CI 和 local MR review 验证 runtime behavior。
- [x] Stage B 验证通过后归档 OpenSpec change，并准备 runtime package 交由 local-main-first helper 集成。
