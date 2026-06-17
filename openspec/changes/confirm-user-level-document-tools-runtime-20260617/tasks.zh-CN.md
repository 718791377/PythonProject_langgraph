# 任务：确认用户级文档工具运行时

## Stage 1：冻结确认方案

- [x] 创建 follow-up OpenSpec change。
- [x] 用明确的 Stage 1 / Stage 2 拆分冻结可复用工具计划对。
- [x] 将 `D:\project` 记录为受保护的来源/消费方，并要求 dirty-file 保护。
- [x] 验证 OpenSpec change 结构和双语计划配对。
- [ ] 提交 Stage 1 冻结包并集成到本地 `main`。

## Stage 2：实施 live runtime 确认

- [ ] 在 `.local/user_level_document_tools/poppler-25.07.0-0/` 下填充本地 Poppler cache，且不在 Git 中跟踪二进制。
- [ ] 修复文档流水线 PowerShell parser/runtime failures。
- [ ] 在不迁移 live vector data 的前提下确认向量/检索框架 smoke 行为。
- [ ] 更新共享 docs/config 示例，使其指向新的主运行时路径。
- [ ] 在任何 consumer-doc cleanup 之前收集 `D:\project` no-drift 证据。
- [ ] 验证 runtime 行为并集成 Stage 2 实现包。
