# Delta Spec：硬化 Skills2CLI Profile Routing 契约

## 修改需求

### 需求：场景化 profile routing metadata

plugin-modules profile registry 必须保留现有 top-level canonical profile ID，同时允许每个非 `full` profile、每个 scenario profile 与每个 task module 声明场景 routing metadata。主字段名必须是 `scene_description`；`scenario_description` 可以作为 existing consumers 的兼容别名保留。

每个可路由 entry 必须 fail closed，除非它至少具备一个非空正向场景来源：`scene_description` 加 `route_when` 或 `positive_examples`。普通 routing entry 必须提供 negative examples，并且 suggestion 阶段必须把它们用作排除或降权证据。

#### 场景：非 full profile 声明 routing fields

- **给定** `profiles.json` 中存在一个非 `full` 的 top-level profile
- **当** profile routing checker 校验 registry
- **那么** 该 profile 具备 `scene_description`、兼容别名 `scenario_description`、正向 routing terms 或 examples、negative examples、ranking signal notes，并且至少有一个 task module，除非它被明确标记为 repo-local-only 且有理由说明。

#### 场景：正向场景质量 fail closed

- **给定** 某 top-level profile、scenario profile 或 task module 没有非空 `scene_description`，也没有 `route_when` 或 `positive_examples`
- **当** `check_skills2cli_profile_routing.py --json` 校验 registry
- **那么** checker 失败，并报告 qualified entry name 与缺失的正向场景证据。

### 需求：Task modules 提供分层 routing

profile registry 必须支持 top-level profiles 下的 task modules，使当前会话 soft-load 可以定位到聚焦能力块。task module 的 canonical logical identifier 必须是 `qualified_name=<profile>.<task_module>`。本地 task-module 名只在所属 top-level profile 内有效。

Task modules 只能作为 soft-load guidance。它们不得定义独立 hard-load 行为，不得作为 hard-load target 接收；只有存在显式 inheritance marker 时才可以继承 parent hints。

#### 场景：Task module 可以被 soft-load

- **给定** registry entry 定义 `web-saas.mobile-app`
- **当** 执行 `load_module.ps1 web-saas.mobile-app -Json`
- **那么** 输出包含该 task module 的 focused plugin hints、skill document hints、load policy、routing explanation、`entry_kind=task_module`、`target_profile=web-saas` 与 `task_module=mobile-app`。

#### 场景：Task module identity 是一等身份

- **给定** 两个 top-level profiles 都定义了本地 task module 名 `browser-verification`
- **当** registry contract 收集 task-module routes
- **那么** 每个 module 都按唯一 `qualified_name` 报告，并且没有 route 只用本地 task-module 名作为 key。

### 需求：Hard-load 保持 top-level only

当 nested task module 或 scenario profile 被作为 hard-load target 传入时，hard-load profile helper 必须 fail closed。

#### 场景：Nested module hard-load 被拒绝

- **给定** `web-saas.mobile-app` 是一个 task module
- **当** 执行 `set_plugin_profile.ps1 web-saas.mobile-app -Json`
- **那么** 命令报告 task modules 只是 soft-load guidance，hard-load 只适用于 top-level profiles。

#### 场景：Scenario profile hard-load 被拒绝

- **给定** `repo-dev` 是解析到 `core-dev` 的 scenario alias
- **当** 执行 `set_plugin_profile.ps1 repo-dev -Json`
- **那么** 命令 fail closed，并报告 `core-dev` 的 canonical preview command，而不是把 scenario alias 当成独立 profile preview 或 apply。

### 需求：Profile suggestion 是 advisory 且可解释

`skills2cli.py` 必须提供 advisory profile suggestion command，用于解释 profile matches、task module matches、excluded candidates 与 soft/hard-load boundaries，且不得修改配置。

Suggestion 输出必须包含行为证据 flags：`mutates_config=false`、`edits_plugin_cache=false`、`profile_apply_performed=false` 与 `approval_required_for_apply=true`。这些 flags 必须由测试支撑：在代表性 suggestion 与 soft-load 命令前后 snapshot 相关 config/cache state。

#### 场景：普通任务不选择 full

- **给定** query 是 `Expo mobile build and Sentry observability`
- **当** 执行 `skills2cli.py profile suggest --query ... --json`
- **那么** top recommendation 不是 `full`，包含 `web-saas`，包含 profile-level `plugin_hints` 与 `skill_doc_hints`，包含 `mobile-app` 与 `observability` task modules，并报告 `mutates_config=false`。

#### 场景：Suggestion 与 soft-load 不 apply profiles

- **给定** 一个测试 fixture 包含用户级 `config.toml` 与 plugin cache marker files
- **当** `skills2cli.py profile suggest --query ... --json` 与 `load_module.ps1 core-dev.security-review -Json` 针对该 fixture 运行
- **那么** fixture hash 保持不变，输出报告未发生 profile apply、config edit 或 plugin-cache edit。

### 需求：Known plugins 不能只能通过 full 到达

当 known plugin 只能通过 `full` 到达且没有明确 allowlist reason 时，registry checker 必须 fail。

#### 场景：原 only-full plugins 具备 task routes

- **给定** known plugin list 包含 BioRender、ChatGPT Apps、Cloudinary、Expo、Fireflies、Linear 与 Temporal
- **当** profile routing checker 校验 registry
- **那么** 每个 plugin 都有非 `full` top-level profile 或 task-module route，除非明确 allowlist reason 表明它仅用于 troubleshooting。

### 需求：Shared profile-routing contract 保持集中且有边界

Python runtime 与 checker surfaces 必须通过一个 shared contract module 共享 stable registry paths、canonical profile IDs、required routing-field names、profile/task hint accessors、plugin-coverage collection 与显式 `full` troubleshooting trigger aliases。该 contract module 不得拥有 scoring behavior、runtime ranking weights 或 checker black-box smoke matrix。

Shared contract 必须定义 `routing_scope`、`activation_scope`、`governance_scope` 与 `evidence_scope` 四类正交字段。兼容字段 `load_policy` 的取值必须与这些正交字段保持一致映射。

#### 场景：Contract module 不把 scoring 与 checker smoke 耦合

- **给定** shared contract module 被 `skills2cli.py`、`check_skills2cli_profile_routing.py` 与 `check_plugin_modules_skill.py` 导入
- **当** profile suggestion scoring 或 checker smoke cases 被修改
- **那么** 可以复用 stable schema/path/accessor constants，但 runtime scoring 与 checker expected examples 必须保持可独立 review。

#### 场景：正交 routing fields 存在

- **给定** 某 profile 或 task module 声明兼容 `load_policy`
- **当** registry checker 校验该 entry
- **那么** entry 同时声明 `routing_scope`、`activation_scope`、`governance_scope` 与 `evidence_scope`，且 checker 校验兼容映射。

#### 场景：Installed skills2cli 携带 shared contract module

- **给定** user-level `skills2cli` facade 安装或模拟在 `CODEX_HOME/tools/skills2cli` 下
- **当** generated `skills2cli` wrapper 运行 `profile suggest --query ... --json`
- **那么** installed helper directory 包含 `skills2cli_profile_registry_contract.py`，install metadata 将其列为 support file，install checks 报告该 support file 存在，使依赖缺失时 smoke fail closed。

### 需求：Profile suggestion matrix 覆盖普通 profiles 与显式 full 排障

profile routing checker 必须运行 black-box `skills2cli.py profile suggest` matrix，覆盖每个普通 profile family 与显式 all-plugin troubleshooting request。Matrix rows 必须保留 preview-only safety flags，并且普通 rows 不得选择 `full` 作为 top recommendation。

`full` 与 `troubleshooting` scenario 必须是 explicit-only。当 `explicit_full_request=false` 时，`full` 不得出现在 selected recommendations，只能在 `excluded_candidates` 中出现，并附带 eligibility reason。当 `explicit_full_request=true` 时，选择 `full` 必须包含 `why_full_selected`，取值为 `explicit_all_plugins`、`explicit_broad_discovery` 或 `explicit_missing_plugin_capability` 之一。

#### 场景：Matrix 区分普通 routing 与显式 full

- **给定** matrix 包含 repository development、browser verification、web/SaaS、customer communications、company operations、market research、creative content 与 PySide6 GUI work 的普通任务
- **当** checker 运行 profile suggestion matrix
- **那么** 普通 rows 选择非 `full` target profiles，显式英文或中文 all-plugin troubleshooting rows 可以选择 `full`，且每一行都报告 `mutates_config=false`、`edits_plugin_cache=false`、`profile_apply_performed=false` 与 `approval_required_for_apply=true`。

#### 场景：Full 除非显式请求否则被排除

- **给定** query wording 较宽泛，但没有显式要求 all plugins、full profile 或 missing-plugin troubleshooting
- **当** `skills2cli.py profile suggest --query ... --json` 运行
- **那么** `full` 不被选择，`explicit_full_request=false`，并且 `excluded_candidates` 包含 `full` 与 explicit-only eligibility reason。

## 新增需求

### 需求：Recall/rerank 可解释并 fail closed

Profile suggestion 必须区分 recall 与 rerank。Recall 可以从场景字段、query terms、repository/task context 与 audit strong evidence 收集 candidate top-level profiles、scenario profiles 与 task modules。Rerank 可以用 strong audit evidence 提升候选，也可以对 oversized 或 warning-pressure-heavy candidates 降权，但不得覆盖 explicit-only `full` eligibility 或 profile apply approval 等硬安全门。

#### 场景：Rerank 不能绕过 eligibility

- **给定** audit evidence 或 broad plugin coverage 原本可能提升 `full`
- **当** `explicit_full_request=false`
- **那么** rerank 仍排除 `full`，记录 warning-pressure 或 eligibility reason，并选择排名最高的 eligible non-`full` profile。

#### 场景：Rerank evidence 可见

- **给定** 某 candidate profile 获得 audit-evidence boost 或 warning-pressure penalty
- **当** `skills2cli.py profile suggest --query ... --json` 运行
- **那么** 输出包含脱敏 evidence source labels、rank factors、适用时的 excluded candidates，并且不包含 raw transcript 或 private path 内容。

## 修改需求

### 需求：Checker JSON output UTF-8 稳定

输出 JSON 的 profile-routing checkers 必须直接写入 UTF-8 bytes，使中文 queries 与 evidence text 在 Windows terminals 上无需依赖 process default console encoding 即可 machine-readable。

#### 场景：中文 full troubleshooting matrix row 可 JSON-decode

- **给定** profile suggestion matrix 包含用 codepoints `U+6392 U+969C U+6240 U+6709 U+63D2 U+4EF6` 表示的中文 query
- **当** 在 Windows 上执行 `check_skills2cli_profile_routing.py --json`
- **那么** JSON stream 可由 downstream tests 以 UTF-8 decode，且包含没有 mojibake 或 replacement characters 的中文 matrix row。

### 需求：Scenario profiles 解析到 canonical target profiles

Scenario profiles 必须是 advisory recommendation entries，解析到现有 canonical `target_profile`；它们不得替代 audit candidate 或 hard-load target 语义。

#### 场景：Scenario suggestion 保留 target profile 语义

- **给定** 某 scenario profile 为仓库工作推荐 security review
- **当** 执行 `skills2cli.py profile suggest --query ... --json`
- **那么** 输出同时包含 scenario identifier 与 `target_profile=core-dev`，并报告未执行 profile apply。

## 新增需求

### 需求：Installed artifact drift reporting 覆盖完整 routing surface

installed-copy checker 必须报告 Skills2CLI profile routing 所需全部 installed artifacts 的 drift，而不只是 `profiles.json`。报告必须覆盖 `skills2cli.py`、`skills2cli_profile_registry_contract.py` 与 `profiles.json` 的 repository 与 installed copies。

#### 场景：Installed artifact drift 可见

- **给定** installed user-level `skills2cli` helper 缺少 `skills2cli_profile_registry_contract.py`，或其 `profiles.json` hash 与 repo source 不同
- **当** `check_plugin_modules_skill.py --json` 在启用 installed-copy reporting 时运行
- **那么** 输出命名 drift artifact，报告 repo 和 installed paths，并且不把 installed copy 当成 source of truth。
