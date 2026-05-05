# 固化共享本地模型资产迁移

## 为什么

Codex CLI 个人开发者生产级持久化团队方案需要一条可执行的本地 llama 与 GGUF 模型资产迁移路径。操作者希望把 `Qwen3.5-9B-Q4_K_M-GGUF` 这个本地轻量判断与摘要模型资产，以及 `jina-embeddings-v5-text-small-retrieval-GGUF` 这个本地 embedding 与检索模型资产，集中管理在 `D:\PythonProject_langgraph` 这个 Codex 编排主仓库下，同时仍允许 OpenClaw 通过受控 provider profile 启动或调用同一组本地模型服务。

## 改什么

- 新增双语共享本地模型资产迁移方案。
- 新增双语本地模型 provider policy。
- 新增双语生产级持久化团队 playbook，把长期 draft 目标拆成可实施切片。
- 更新生产级持久化团队 draft，指向迁移方案、provider policy 和 playbook。
- 更新 active team-mode 方案，加入 expert fan-out 与 stalled subagent 处理规则。
- 登记新增双语文档。

## 非目标

- 不移动真实 GGUF 模型文件。
- 不启动模型服务。
- 不修改 `D:\PythonProject_OpenClaw` 这个消费方项目。
- 不修改 `C:\Users\lenovo\.codex\config.toml` 这个用户级 Codex 配置文件。
- 不写入 `.omx/state/` 这个仓库本地 durable state 目录。
- 不把任何本地模型 provider 变成 approval authority、durable truth 或 backend selector。
