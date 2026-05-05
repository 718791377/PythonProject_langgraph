# 设计：共享本地模型资产迁移

## 边界

本 change 只做文档和治理更新。它记录后续如何迁移本地模型资产，同时避免让任意 Git 仓库产生意外 dirty work。

## 模型资产所有权

`D:\PythonProject_langgraph` 是 Codex 编排主仓库。它可以拥有被 Git 忽略的本地模型资产目录、provider profile 模板、健康检查和 adapter contract。

`D:\PythonProject_OpenClaw` 是消费方和领域 Agent 平台。它可以通过显式 profile 启动或调用共享本地模型服务，但不能拥有权威模型资产 policy，也不能拥有 Codex durable-team state。

## Provider Profiles

本迁移方案标准化两个 advisory profile：

- `local-judge-qwen` - 由 `Qwen3.5-9B-Q4_K_M-GGUF` 支撑的本地轻量判断与摘要 provider profile。
- `local-embed-jina` - 由 `jina-embeddings-v5-text-small-retrieval-GGUF` 支撑的本地 embedding provider profile。

两个 profile 都只是 provider。它们不是 durable backend、approval authority、routing selector 或 project truth source。

## Git 卫生

真实 GGUF 文件应放在 `.local/models/` 或 `.runtime/models/` 这类被 Git 忽略的路径下。Git 只应跟踪脚本、模板、校验和、manifest 与文档。

## Expert Routing

有界多面研究的第一轮应使用同质 `analyst` fan-out。`architect` 或 `planner` 这类 specialist role 只应在 analyst fan-in 显示确实需要架构设计或执行排序时再调用。

如果某个 specialist subagent 没有完成，leader 必须先诊断它是仍在工作、被启动阻塞，还是疑似 stalled，再决定是否关闭。leader 不得静默跳过这个分析步骤。
