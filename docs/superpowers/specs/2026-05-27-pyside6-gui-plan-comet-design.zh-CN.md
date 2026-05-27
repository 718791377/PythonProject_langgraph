# PySide6 GUI 方案完整 Comet 重构设计

## 背景

PySide6 跨项目 GUI 能力方案约束可复用共享 runtime 和未来消费项目 GUI 接入。它需要与新版实施方案一致的可执行 Comet 结构。

## 设计目标

- 让方案不依赖聊天历史即可阅读。
- 保留共享 runtime 默认路径和本地-only 规则。
- 区分共享 runtime readiness 与消费项目 GUI readiness。
- 将 project-local override、可见 GUI 验证和可执行文件打包保留为显式触发门。
- 诚实记录 Windows Comet bash 不可用。

## 选择的结构

方案现在包含：

- 带 readiness 和 Comet change metadata 的 frontmatter；
- 复核结论；
- 关系模型与命名边界；
- 目标与非目标；
- Comet/OpenSpec 工作边界；
- 运行时架构；
- helper 与 JSON contract；
- 能力状态模型；
- 有序实施事项；
- 文件职责图；
- 本地集成顺序和验证路径；
- 风险与自检。

## 验收标准

- 目标方案没有含糊声称每个项目都 GUI-ready。
- 方案命名当前 Comet change。
- 高影响门禁保持显式。
- OpenSpec change 可以 validate。
- 本地集成前 precommit 和本地验证通过。
