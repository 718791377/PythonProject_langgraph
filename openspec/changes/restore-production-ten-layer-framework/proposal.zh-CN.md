# 恢复生产级持久化团队十层框架

## 为什么

当前 draft 版生产级持久化团队 implementation plan 仍然引用白皮书十层模型，但详细落地映射没有在方案正文中直接可见。冷启动维护者必须能在本方案里直接看到十层框架，再判断下一步哪个 release slice 可以安全实施。

## 改什么

- 在英文 ASCII 主版 implementation plan 中恢复独立的十层框架落地映射章节。
- 在 UTF-8 中文对照版中恢复表达一致的十层框架章节，并保持相同约束与 release 解释。
- 保持生产级持久化团队方案的 `status: draft`；本次只恢复文档，不宣称 runtime 已实现。

## 非目标

- 不实现任何 durable runtime 行为。
- 不启动 `native_omx` 或 `langgraph`。
- 不写入 `.omx/state/`。
- 不修改用户级 Codex 配置。
