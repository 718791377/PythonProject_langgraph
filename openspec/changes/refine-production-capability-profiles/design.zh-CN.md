# 设计

## 放置位置

生产级方案在工具复用章节下新增依赖归属小节，并在具体 release stage 之前新增抽象 capability profile 小节。具体 workload example 被有意放进单独参考文件，确保主方案保持稳定和抽象。

## 运行时边界

规则区分三个面：

1. Codex CLI durable-team runtime：共享编排、检查、评测、恢复和操作员控制工具。
2. concrete business runtime：由各业务项目自己拥有的依赖、状态和最终用户行为。
3. shared local model service：本地 Llama 部署可以服务两类运行面，但只能通过 provider adapter 使用，并隔离策略、日志和数据边界。

## Capability Profiles

Capability profile 是覆盖十层框架的横向分类，不是第十一层。新增 workload 应映射到一个或多个 profile，并继承这些 profile 要求的通用控制能力。
