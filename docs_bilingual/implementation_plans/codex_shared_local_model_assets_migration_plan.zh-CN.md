---
doc_id: codex_shared_local_model_assets_migration_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/codex_shared_local_model_assets_migration_plan.md
translation_of: docs_bilingual/implementation_plans/codex_shared_local_model_assets_migration_plan.md
doc_class: implementation_plan
status: draft
---

# 共享本地模型资产迁移方案

## 范围

本方案说明如何把本地 llama 与 GGUF 模型资产迁移到 `D:\PythonProject_langgraph` 这个 Codex CLI 持久化团队编排主仓库下，同时避免让 `D:\PythonProject_langgraph` 或 `D:\PythonProject_OpenClaw` 这两个 Git 仓库意外产生 dirty work。

本方案优先处理文档和治理。它不移动真实 GGUF 文件，不启动模型服务，也不修改 OpenClaw。

## 目标

目标是在 `D:\PythonProject_langgraph` 下使用被 Git 忽略的本地目录集中管理模型资产，同时保留 OpenClaw 和其他消费方仓库通过显式 provider profile 启动或调用这些模型服务的能力。

目标模型资产：

- `Qwen3.5-9B-Q4_K_M-GGUF` - 本地轻量判断与摘要模型资产。
- `jina-embeddings-v5-text-small-retrieval-GGUF` - 本地 embedding 与检索模型资产。

推荐本地根目录：

- `D:\PythonProject_langgraph\.local\models\` - 被 Git 忽略的大模型文件本地资产目录。
- `D:\PythonProject_langgraph\.runtime\models\` - 被 Git 忽略的临时 runtime 模型资产目录。

## 非目标

- 不把 GGUF 文件提交到普通 Git。
- 不重写 Git 历史。
- 不修改 `C:\Users\lenovo\.codex\config.toml` 这个用户级 Codex 配置文件。
- 不写入 `.omx/state/` 这个仓库本地 durable state 目录。
- 不修改 OpenClaw 的业务状态或领域 Agent 状态。
- 不把本地模型 provider 变成 durable backend、approval authority 或 routing selector。

## Git 卫生规则

仓库应忽略本地模型资产和 runtime 缓存：

```gitignore
.local/
.runtime/
*.gguf
*.GGUF
```

`git check-ignore -v` 是解释某个路径被哪条 ignore 规则命中的 Git 命令，应在复制大文件前使用。

`git status --short --branch` 是查看分支与 dirty work 状态的 Git 命令，应在迁移步骤前后运行。

如果 GGUF 文件已经被 Git 跟踪，必须使用单独 cleanup 方案。安全默认做法是先备份文件，加入 ignore 规则，运行 `git rm --cached` 这个只从 Git index 移除文件但保留本地文件的命令，然后提交 index 移除。本迁移切片不得重写历史。

## 所有权拆分

`D:\PythonProject_langgraph` 这个编排仓库拥有：

- model asset directory conventions - 模型资产目录约定。
- provider profile templates - provider profile 模板。
- launcher templates - 启动器模板。
- health-check scripts - 健康检查脚本。
- adapter contracts - provider adapter 的输入输出与边界契约。
- Codex durable-team usage policy - Codex 持久化团队使用策略。

`D:\PythonProject_OpenClaw` 这个消费方领域 Agent 平台拥有：

- its own adapter or profile references - 它自己的 adapter 或 profile 引用。
- its own business runtime configuration - 它自己的业务 runtime 配置。
- its own domain-agent state - 它自己的领域 Agent 状态。
- its own release validation - 它自己的发布验证。

OpenClaw 可以在使用显式 provider profile 且不声明模型资产权威所有权的前提下，启动共享模型服务。

## 可共享与必须隔离

允许共享：

- GGUF model files - 大模型二进制文件。
- local model server process definitions - 本地模型服务进程定义。
- provider endpoint names - provider 端点名称。
- provider profile IDs - provider profile 标识。
- health checks - 健康检查。
- checksum manifests - 校验和 manifest。

禁止共享：

- Codex durable-team state - Codex 持久化团队状态。
- OpenClaw domain-agent state - OpenClaw 领域 Agent 状态。
- approval state - 审批状态。
- recovery evidence - 恢复证据。
- customer data - 客户数据。
- unredacted prompt or response logs - 未脱敏 prompt 或 response 日志。
- `.omx/state/` - 仓库本地 durable state 目录。

## Provider Profiles

`local-judge-qwen` 是面向 `Qwen3.5-9B-Q4_K_M-GGUF` 的 provider profile。它只提供 advisory 能力，可用于轻量判断、bug triage、summary compression 与低风险 draft review。

`local-embed-jina` 是面向 `jina-embeddings-v5-text-small-retrieval-GGUF` 的 provider profile。它可用于 documents、OpenSpec artifacts、plans、reports 与 evidence 的本地 embedding。

两个 profile 都必须放在 provider adapter 后面。Provider adapter 是限定输入、输出、日志、健康检查与数据边界的代码层。

## 环境变量

`CODEX_LOCAL_MODEL_ROOT` 是共享本地模型根目录的环境变量。通常应指向：

```powershell
$env:CODEX_LOCAL_MODEL_ROOT="D:\PythonProject_langgraph\.local\models"
```

这个变量让 OpenClaw 或其他消费方仓库无需把路径硬编码到 tracked business code 中，也能找到共享本地模型资产。

## 迁移阶段

### Phase 0: 只读盘点

在两个仓库中运行 `git status --short --branch` 这个 Git dirty-work 检查命令。

运行 `git ls-files` 这个 Git tracked-file 列表命令，检查是否已有 GGUF 文件被跟踪。

### Phase 1: 在编排仓库新增治理

在 `D:\PythonProject_langgraph` 中新增或更新 ignore 规则、provider policy、profile templates、health-check design 与本方案。不要在同一 commit 中复制模型文件。

### Phase 2: 本地复制模型文件

把模型目录复制到 `.local/models/` 这个被 Git 忽略的本地模型根目录。复制后运行 `git status --short --branch`，确认 GGUF 文件没有作为 untracked work 出现。

### Phase 3: 在 OpenClaw 增加消费方接线

在 `D:\PythonProject_OpenClaw` 中只增加 profile examples、adapter references、`.env.example` 与 startup documentation 这类消费方接线。不要把模型文件复制进 OpenClaw。

### Phase 4: 验证两个仓库

验证 Codex durable-team tooling 与 OpenClaw 都能发现共享 provider profiles，同时两个 Git 仓库在本地模型文件就位后仍保持 clean。

## 回滚

文档和脚本的回滚使用普通 Git revert 或删除分支。

本地模型文件的回滚是删除或移动 `.local/models/` 这个被 Git 忽略的本地模型根目录下的文件。因为这些文件不受 Git 跟踪，这个操作必须谨慎执行，不得作为自动仓库清理脚本的一部分。

## 验收标准

- 迁移方案同时存在英文 ASCII 主版和 UTF-8 中文对照版。
- 本地模型 provider policy 存在，并声明模型服务可共享，但状态不可共享。
- 仓库 ignore policy 能让 GGUF 文件不进入普通 Git。
- OpenSpec guard 与文档治理检查通过。
- 本 documentation change 不移动真实 GGUF 文件。
