# codex-user-level-safety-rule-script-backing 规格中文对照

## 新增需求：文档对与提交语言安全规则必须有脚本支撑

仓库必须登记 forward bilingual document pairs 与 Chinese local commit subjects 两条安全规则。

forward bilingual document-pair 规则要求 `docs_bilingual/`、`openspec/` 和 `docs/` 下发生变更的 Markdown 文件具备英文 ASCII 主版与中文对照版。该规则可以把未变更的历史文件视为 baseline，以避免 legacy archive 缺口阻断无关工作。

local commit-language 规则要求 feature commit 主题包含中文；当主题仍包含中文时，允许 ASCII conventional prefix。

### 场景：新 checker 规则已登记
- **WHEN** `python tools/check_safety_rule_script_backing.py --root . --json` 运行
- **THEN** 输出必须包含 forward bilingual document pairs 和 local Git commit Chinese subjects 的 implemented rules
- **AND** 每条规则必须指向 prompt reminders、executable script controls 和 aggregate guard steps

### 场景：Guard 运行新检查
- **WHEN** `python tools/run_openspec_guard.py --root . --json` 运行
- **THEN** aggregate guard 输出必须包含 `check_document_pair_policy` 和 `check_git_commit_language`
- **AND** 任一 checker 报错时 guard 必须失败

## 新增需求：实施前 implementation plan 必须 active

仓库要求被 active Comet change 在 build、verify 或 archive 阶段引用的任何 implementation plan，必须先在 registry 中标记为 `status: active`，然后才能继续实施。

### 场景：Comet build 引用 draft implementation plan
- **WHEN** active Comet change 的 phase 是 `build`、`verify` 或 `archive`
- **AND** 其 `.comet.yaml` 引用的 `docs_bilingual/implementation_plans/` 文件在 registry 中不是 `active`
- **THEN** implementation-plan checker 必须失败
- **AND** 必须指出需要激活或替换的 change 与 plan

### Requirement: `/plan` 后与完整本地流程规则必须脚本化
仓库必须在 safety-rule script backing registry 中登记 `/plan` 后执行治理与执行到远端发布门的完整本地流程两类规则。

registry 必须指向 prompt reminders、可执行脚本控制、aggregate guard 步骤、local MR review 接线，以及 local-flow checker 表面的测试。

#### 场景：local-flow 脚本支撑被检查
- **WHEN** `python tools/check_safety_rule_script_backing.py --root . --json` 运行
- **THEN** 必须存在 `post-plan-execution-governance-package` - 用于 `/plan` 退出后的治理 workflow 门禁规则 - 和 `complete-local-flow-to-remote-gate` - 用于本地 main 优先完成的 gate condition 规则 - 两条 implemented rules
- **AND** `python tools/run_openspec_guard.py --root . --json` 必须包含 `check_local_flow_scripted_enforcement`

### Requirement: Spec Kit authority guard SHALL validate generated surfaces and subordinate dry-run receipts / Spec Kit authority guard 必须校验生成表面和从属 dry-run 收据

仓库必须通过 generated-surface 与 runtime-receipt 检查，把 Spec Kit 严格保持在 Comet、OpenSpec、Superpowers、本地 main 优先门禁与远端发布门之下，避免任何 Spec Kit 表面被误当成仓库治理权威。

`tools/check_spec_kit_authority_guard.py` 必须对 `.specify/`、根目录 `specs/`、生成的 `.codex/commands/*speckit*`、`.codex/skills/*speckit*`、`.github/prompts/*speckit*`、`/speckit.*`、`$speckit-*`、extension、preset 与 workflow-output fail closed，除非单独的 active authority-migration plan 明确拥有该变更。任何 `specify init` 或 `specify self check` 命令证据都必须保持为 blocked subordinate command evidence，除非同一 authority-migration plan 明确拥有该命令边界。

仓库必须提供 `tools/spec_kit_subordinate_runtime.py` 作为 dry-run-only 的 subordinate helper。该 helper 只能支持 `source-refresh`、`probe`、`plan-dry-run`、`init-dry-run` 与 `self-check-dry-run`，必须拒绝 live 或 apply 模式名，不得运行 live `specify`，不得创建 `.specify/` 或根目录 `specs/`，也不得写入生成的 command、skill、prompt、extension、preset 或 workflow-output 表面。

Spec Kit subordinate runtime receipt 必须包含 `dry_run_only=true`、`source_url`、`source_pin`、`authority_decision` 与 `surface_status`。在 R4 中，`authority_decision.decision` 只能是 `blocked` 或 `subordinate`，必须记录胜出的 authority layer，并且必须保留精确优先级顺序 `Comet > OpenSpec/Superpowers > gstack > harness runtime safety > Spec Kit`。

#### 场景：生成的 Spec Kit command surface 被阻止

- **WHEN** 某个变更或现存仓库路径包含 `.codex/commands/speckit.plan.md`
- **AND** 没有 active Spec Kit authority-migration plan 拥有该生成 command surface
- **THEN** `python tools/check_spec_kit_authority_guard.py --root . --json` 必须失败

#### 场景：dry-run subordinate receipt 被接受

- **WHEN** `tools/spec_kit_subordinate_runtime.py probe --root <repo> --receipt-out <receipt>` 写出 dry-run receipt
- **AND** 该 receipt 记录了 `authority_decision.decision=subordinate`、`dry_run_only=true`、source evidence 与完整 surface status
- **THEN** `python tools/check_spec_kit_authority_guard.py --root <repo> --receipt <receipt> --json` 必须通过

#### 场景：live 或 apply mode 被拒绝

- **WHEN** 操作员请求 `tools/spec_kit_subordinate_runtime.py apply-live --root <repo>`
- **THEN** helper 必须在构建 runtime payload 前拒绝该模式
- **AND** 不得运行 live Spec Kit commands，也不得创建生成的 Spec Kit surfaces
