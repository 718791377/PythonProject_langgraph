# codex-user-level-plugin-modules-profile-helper 规范

## 目的
定义用户级 `plugin-modules` skill 与 profile helper 契约，覆盖任务域 plugin soft-load、带备份保护的 hard-load profile 切换、advisory Skills2CLI profile suggestion、场景/task-module routing，以及显式安装到 Codex 用户级 skills 目录。

## 需求
### 需求：场景化 profile routing metadata

plugin-modules profile registry 必须保留现有 top-level canonical profile ID，同时允许每个非 `full` profile 和每个 scenario profile 声明场景 routing metadata。 主字段名必须是 `scene_description`；`scenario_description` 可以作为 existing consumers 的兼容别名保留。

#### 场景：非 full profile 声明 routing fields

- **给定** `profiles.json` 中存在一个非 `full` 的 top-level profile
- **当** profile routing checker 校验 registry
- **那么** 该 profile 具备 `scene_description`、兼容别名 `scenario_description`、正向 routing terms 或 examples、negative examples、ranking signal notes，并且至少有一个 task module，除非它被明确标记为 repo-local-only 且有理由说明。

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
- **那么** top recommendation 不是 `full`，包含 `web-saas`，包含 profile-level `plugin_hints` 与 `skill_doc_hints`，包含 `mobile-app` 与 `observability` task modules，并报告 `mutates_config=false`。

### 需求：Known plugins 不能只能通过 full 到达

当 known plugin 只能通过 `full` 到达且没有明确 allowlist reason 时，registry checker 必须 fail。

#### 场景：原 only-full plugins 具备 task routes

- **给定** known plugin list 包含 BioRender、ChatGPT Apps、Cloudinary、Expo、Fireflies、Linear 与 Temporal
- **当** profile routing checker 校验 registry
- **那么** 每个 plugin 都有非 `full` top-level profile 或 task-module route，除非明确 allowlist reason 表明它仅用于 troubleshooting。

### 需求：Shared profile-routing contract 保持集中且有边界

Python runtime 与 checker surface 必须通过一个 shared contract module 共享稳定 registry paths、canonical profile IDs、required routing-field names、profile/task hint accessors、plugin-coverage collection 与显式 `full` troubleshooting trigger aliases。该 contract module 不得拥有 scoring behavior、runtime ranking weights 或 checker black-box smoke matrix。

#### 场景：Contract module 不把 scoring 和 checker smoke 绑死

- **给定** `skills2cli.py`、`check_skills2cli_profile_routing.py` 与 `check_plugin_modules_skill.py` 都导入 shared contract module
- **当** profile suggestion scoring 或 checker smoke cases 发生变化
- **那么** 稳定 schema/path/accessor constants 可以复用，但 runtime scoring 与 checker expected examples 仍然可以被分别审查。

#### 场景：Installed skills2cli 携带 shared contract module

- **给定** user-level `skills2cli` facade 被安装或模拟安装到 `CODEX_HOME/tools/skills2cli`
- **当** 生成的 `skills2cli` wrapper 执行 `profile suggest --query ... --json`
- **那么** installed helper directory 必须包含 `skills2cli_profile_registry_contract.py`，install metadata 必须把它列为 support file，并且 install checks 必须报告该 support file presence，使 smoke 在依赖缺失时 fail closed。

### 需求：Profile suggestion matrix 覆盖普通 profiles 与显式 full 排障

profile routing checker 必须运行 black-box `skills2cli.py profile suggest` 矩阵，覆盖每个普通 profile family 和显式 all-plugin troubleshooting requests。矩阵行必须保持 preview-only safety flags，且普通行不得把 `full` 选为 top recommendation。

#### 场景：矩阵区分普通 routing 与显式 full

- **给定** 矩阵包含 repository development、browser verification、web/SaaS、customer communications、company operations、market research、creative content 与 PySide6 GUI work 的普通任务
- **当** checker 运行 profile suggestion matrix
- **那么** 普通行选择非 `full` target profiles，显式英文或中文 all-plugin troubleshooting 行可以选择 `full`，并且每行都报告 `mutates_config=false`、`edits_plugin_cache=false`、`profile_apply_performed=false` 与 `approval_required_for_apply=true`。

### 需求：Checker JSON output 保持 UTF-8 稳定

profile-routing checkers 在输出 JSON 时必须直接写入 UTF-8 bytes，使中文 query 和 evidence text 在 Windows terminal 上不依赖 process default console encoding 也能被机器读取。

#### 场景：中文 full troubleshooting 矩阵行可被 JSON 解码

- **给定** profile suggestion matrix 包含中文 query `排障所有插件`
- **当** 在 Windows 上执行 `check_skills2cli_profile_routing.py --json`
- **那么** JSON stream 可被下游测试以 UTF-8 解码，并包含没有 mojibake 或 replacement characters 的中文矩阵行。

### 需求：Scenario profiles 解析到 canonical target profiles

Scenario profiles 必须是 advisory recommendation entries，解析到现有 canonical `target_profile`；它们不得替代 audit candidate 或 hard-load target 语义。

#### 场景：Scenario suggestion 保留 target profile 语义

- **给定** 某 scenario profile 为仓库工作推荐 security review
- **当** 执行 `skills2cli.py profile suggest --query ... --json`
- **那么** 输出同时包含 scenario identifier 与 `target_profile=core-dev`，并报告未执行 profile apply。

### Requirement：Hidden skills are discoverable without global restore

`skills2cli` SHALL provide a hidden-skill command surface that can discover standalone user skills moved into the visibility-disabled library without restoring those skills to the default model-visible skill list.

#### Scenario：Hidden library can be indexed

- **GIVEN** `CODEX_HOME/state/skills2cli/visibility-disabled` contains hidden skill directories
- **WHEN** `skills2cli hidden index --json` is executed
- **THEN** the output reports hidden skill records with `visibility_state=hidden`
- **AND** the output reports `global_restore_performed=false`, `mutates_config=false`, `edits_plugin_cache=false`, and `profile_apply_performed=false`.

#### Scenario：Current visible skills and hidden skills are searched together

- **GIVEN** a query matches either a current visible skill or a hidden skill
- **WHEN** `skills2cli hidden search <query> --json` is executed
- **THEN** the output returns compact candidates from both sources
- **AND** each candidate states whether it is `visible` or `hidden`.

### Requirement：Hidden skill soft-load reads exactly one selected skill

`skills2cli hidden load` SHALL read a single selected hidden `SKILL.md` into the command output without moving the skill directory or making it globally visible.

#### Scenario：Hidden load is read-only

- **GIVEN** a hidden skill id resolves to one `SKILL.md`
- **WHEN** `skills2cli hidden load <hidden_skill_id> --json` is executed
- **THEN** the output includes that skill body or a bounded chunk
- **AND** no hidden skill directory is moved to the visible skills directory
- **AND** the output reports `global_restore_performed=false` and `mutates_config=false`.

#### Scenario：Hidden load records usage evidence

- **GIVEN** `skills2cli hidden load <hidden_skill_id> --json` succeeds
- **WHEN** the command completes
- **THEN** a JSONL usage event is appended under `CODEX_HOME/state/skills2cli/usage-events.jsonl`
- **AND** the event contains a timestamp, event type, hidden skill id, frontmatter name, content hash, byte count, and `raw_paths_retained=false`.

### Requirement：Hidden aliases resolve known task names

The hidden-skill search surface SHALL support deterministic aliases for known task terms that do not match installed skill names exactly.

#### Scenario：Grill-me alias resolves hidden upstream adapter

- **GIVEN** the hidden library contains `mattpocock-skills-skills-productivity-grill-me-skill-md`
- **WHEN** `skills2cli hidden search grill-me --json` is executed
- **THEN** that hidden skill is returned as a high-confidence candidate.

#### Scenario：Stop-slop alias resolves AI slop cleaner

- **GIVEN** the hidden library contains `ai-slop-cleaner`
- **WHEN** `skills2cli hidden search stop-slop --json` is executed
- **THEN** `ai-slop-cleaner` is returned as an alias candidate
- **AND** the output explains that `stop-slop` is an alias rather than the installed skill name.

### Requirement：Visibility recommendations are evidence-driven and manual-only

`skills2cli visibility recommend` SHALL classify standalone user skills into promote, demote, and keep-soft-load buckets using usage evidence. Applying recommendations SHALL require an explicit user/operator command and SHALL NOT run automatically.

#### Scenario：Recommendations are generated from usage events

- **GIVEN** hidden skill usage events exist for a selected time window
- **WHEN** `skills2cli visibility recommend --days 30 --json` is executed
- **THEN** the output contains promote candidates for high-frequency hidden loads, keep-soft-load candidates for low-frequency hidden loads, and demote candidates for unused visible standalone user skills when evidence is sufficient.

#### Scenario：Apply recommendations requires explicit command

- **GIVEN** a recommendation receipt exists
- **WHEN** no operator runs `skills2cli visibility apply-recommendations --receipt <id> --apply --operator-confirmation --json`
- **THEN** no skill directories are moved.

#### Scenario：Apply recommendations is daily-limited and rollback-backed

- **GIVEN** a recommendation receipt exists and the operator invokes `apply-recommendations` with the required apply flags
- **WHEN** no apply has run on the current local day
- **THEN** at most three standalone user skills are moved
- **AND** a rollback receipt is written before moving and updated after each move.

#### Scenario：Second daily apply fails closed

- **GIVEN** `apply-recommendations` has already completed or partially completed on the current local day
- **WHEN** it is invoked again on the same local day
- **THEN** it fails closed and moves no additional skills.
