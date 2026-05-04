# 细化生产级业务能力 Profile

## 为什么

个人开发者生产级持久化团队 draft 方案需要更清楚地区分 Codex CLI durable-team 通用工具和具体业务运行时。方案也需要一套抽象业务能力 profile，这样未来新增 workload 时，可以按十层框架评估，而不把具体业务名称写进生产级总方案正文。

## 改什么

- 在 draft 版生产级持久化团队方案中加入共享依赖与运行时归属规则。
- 明确评测、GUI、队列、embedding、vector store 等第三方依赖默认属于 Codex CLI durable-team 控制面，不属于具体业务运行时。
- 为本地 Llama 模型部署保留窄例外，但必须通过 provider adapter 使用，并隔离日志、权限和数据边界。
- 增加抽象业务能力 profile，把 workload class 映射到十层框架，但不在方案正文中写具体业务名称。
- 新增一份双语参考表，用来记录具体 workload example 与抽象 capability profile 的对应关系。

## 非目标

- 不实现 durable runtime 行为。
- 不启动 `native_omx` 或 `langgraph`。
- 不写入 `.omx/state/`。
- 不修改用户级 Codex 配置。
- 不把具体业务项目依赖迁入本仓库。
