# Delta Spec：Codex 用户级 Plugin Modules Profile Helper

## 新增需求

### 需求：场景化 profile routing metadata

plugin-modules profile registry 必须保留现有 top-level canonical profile ID，同时允许每个非 `full` profile 和每个 scenario profile 声明场景 routing metadata。

#### 场景：非 full profile 声明 routing fields

- **给定** `profiles.json` 中存在一个非 `full` 的 top-level profile
- **当** profile routing checker 校验 registry
- **那么** 该 profile 具备场景描述、正向 routing terms 或 examples、negative examples、ranking signal notes，并且至少有一个 task module，除非它被明确标记为 repo-local-only 且有理由说明。

### 需求：Task modules 提供分层 routing

profile registry 必须支持 top-level profiles 下的 task modules，使当前会话 soft-load 可以定位到聚焦能力块。

#### 场景：Task module 可以被 soft-load

- **给定** registry entry 定义 `web-saas.mobile-app`
- **当** 执行 `load_module.ps1 web-saas.mobile-app -Json`
- **那么** 输出包含该 task module 的 focused plugin hints、skill document hints、load policy 与 routing explanation。

### 需求：Hard-load 保持 top-level only

当 nested task module 被作为 hard-load target 传入时，hard-load profile helper 必须 fail closed。

#### 场景：Nested module hard-load 被拒绝

- **给定** `web-saas.mobile-app` 是一个 task module
- **当** 执行 `set_plugin_profile.ps1 web-saas.mobile-app -Json`
- **那么** 命令报告 task modules 只是 soft-load guidance，hard-load 只适用于 top-level profiles。

### 需求：Profile suggestion 是 advisory 且可解释

`skills2cli.py` 必须提供 advisory profile suggestion command，用于解释 profile matches、task module matches、excluded candidates 与 soft/hard-load boundaries，且不得修改配置。

#### 场景：普通任务不选择 full

- **给定** query 是 `Expo mobile build and Sentry observability`
- **当** 执行 `skills2cli.py profile suggest --query ... --json`
- **那么** top recommendation 不是 `full`，包含 `web-saas`，包含 `mobile-app` 与 `observability` task modules，并报告 `mutates_config=false`。

### 需求：Known plugins 不能只能通过 full 到达

当 known plugin 只能通过 `full` 到达且没有明确 allowlist reason 时，registry checker 必须 fail。

#### 场景：原 only-full plugins 具备 task routes

- **给定** known plugin list 包含 BioRender、ChatGPT Apps、Cloudinary、Expo、Fireflies、Linear 与 Temporal
- **当** profile routing checker 校验 registry
- **那么** 每个 plugin 都有非 `full` top-level profile 或 task-module route，除非明确 allowlist reason 表明它仅用于 troubleshooting。

### 需求：Scenario profiles 解析到 canonical target profiles

Scenario profiles 必须是 advisory recommendation entries，解析到现有 canonical `target_profile`；它们不得替代 audit candidate 或 hard-load target 语义。

#### 场景：Scenario suggestion 保留 target profile 语义

- **给定** 某 scenario profile 为仓库工作推荐 security review
- **当** 执行 `skills2cli.py profile suggest --query ... --json`
- **那么** 输出同时包含 scenario identifier 与 `target_profile=core-dev`，并报告未执行 profile apply。
