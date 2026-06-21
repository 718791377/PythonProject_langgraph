# 任务：改进 Skills2CLI Profile 路由

## Stage A：冻结方案

- [x] 创建场景化 profile routing 双语 implementation plan。
- [x] 创建本 OpenSpec change，包含 proposal、design、tasks 与 delta spec。
- [x] 将 skills usage audit plan 链接为 advisory routing/rerank 输入。
- [x] 在 docs registry 中登记新的双语方案。
- [x] 验证并提交 Stage A 方案冻结包。
- [ ] 将 Stage A 方案冻结包集成到本地 `main`。

## Stage B：实现 live runtime

- [ ] 扩展 `profiles.json`，加入场景 metadata、negative examples、ranking signals 与 task modules。
- [ ] 扩展 plugin-modules scripts，支持 `profile.task_module` soft-load 与 top-level-only hard-load。
- [ ] 添加 `skills2cli.py profile suggest`，输出可解释的 recall/rerank 结果。
- [ ] 添加 checker 与测试，覆盖 schema、only-`full` coverage、`full` fallback discipline 和 installed-copy drift reporting。
- [ ] 用代表性 suggestions、OpenSpec guard、local CI 和 local MR review 验证 runtime behavior。
- [ ] Stage B 验证通过后 archive 本 OpenSpec change，并把 runtime package 合入本地 `main`。
