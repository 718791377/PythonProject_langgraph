---
doc_id: codex_local_model_provider_policy
lang: zh-CN
canonical: docs_bilingual/governance/codex_local_model_provider_policy.md
translation_of: docs_bilingual/governance/codex_local_model_provider_policy.md
doc_class: governance
status: active
---

# Codex 本地模型 Provider Policy

## 目的

本 policy 定义 Codex CLI durable-team tooling 与消费方仓库如何共享本地模型服务，同时不共享 durable state、business data、approval authority 或 routing truth。

## Provider 不是 Truth

本地模型 provider 是放在 bounded adapter 后面的模型服务端点。它可以生成文本、embedding、判断摘要或检索向量。它不能成为：

- durable truth - 持久化工作流真相。
- approval authority - 审批权威。
- backend routing selector - durable backend 路由选择器。
- persistent team identity - 持久化团队身份。
- project memory authority - 项目记忆权威。
- business runtime state - 业务 runtime 状态。

## 标准 Provider Profiles

`local-judge-qwen` 是本地轻量判断 provider profile。它可以使用 `Qwen3.5-9B-Q4_K_M-GGUF` 执行低成本判断、bug triage、summary compression 与 evidence ordering。

`local-embed-jina` 是本地 embedding provider profile。它可以使用 `jina-embeddings-v5-text-small-retrieval-GGUF` 对 documents、OpenSpec artifacts、implementation plans、reports 与 evidence 做本地 embedding。

## Light Judge 策略

`Light Judge` 是一种策略，不是必需外部依赖。它可用于 candidate bug triage、survivor-queue generation、低成本 quality gates 与 inspect-summary hints。

`Light Judge` 不得决定 final approval，不得拥有 durable state，不得启动 persistent workers，也不得选择 durable backend families。

## 共享服务边界

`D:\PythonProject_langgraph` 可以集中管理 model assets、provider profile templates、health checks 与 adapter contracts。OpenClaw 和其他消费方仓库可以通过显式 profiles 调用或启动服务。

共享服务资产可以包括 model files、endpoints、health checks 与 checksums。共享服务资产不得包括 project durable state、OpenClaw domain-agent state、customer data 或未脱敏 prompt logs。

## Adapter 要求

Provider adapter 必须定义：

- `profile_id` - 脚本和文档使用的稳定 profile 名称。
- `model_asset` - 模型资产名称或 manifest 引用。
- `health_check` - 报告 provider 是否能回答的只读检查。
- `allowed_use` - 允许用途，例如 judgement 或 embeddings。
- `forbidden_use` - 禁止用途，例如 approval authority 或 durable truth。
- `data_boundary` - 说明 logs、prompts 与 outputs 是否可保存以及保存边界。

## Git 与 Runtime 规则

真实 GGUF 文件应保留在 `.local/models/` 或 `.runtime/models/` 这类被 Git 忽略的本地根目录下。Git 应跟踪 manifests、checksums、docs、scripts 与 templates，而不是大模型二进制文件。

## 失败规则

如果 provider 不可用，Codex durable-team tooling 必须 fail closed，或者退回到文档化的 non-provider path。它不得静默把 provider 不可用解释为 approval、readiness 或 routing 成功。
