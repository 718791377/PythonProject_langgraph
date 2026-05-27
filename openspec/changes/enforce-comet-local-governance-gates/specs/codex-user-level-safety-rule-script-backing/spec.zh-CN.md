## 新增需求

### Requirement: 文档对与提交语言安全规则必须有脚本支撑
仓库必须登记 forward bilingual document pairs 与 Chinese local commit subjects 两条安全规则。

forward bilingual document-pair 规则要求 `docs_bilingual/`、`openspec/` 和 `docs/` 下发生变更的 Markdown 文件具备英文 ASCII 主版与中文对照版。该规则可以把未变更的历史文件视为 baseline，以避免 legacy archive 缺口阻断无关工作。

local commit-language 规则要求 feature commit 主题包含中文；当主题仍包含中文时，允许 ASCII conventional prefix。

#### 场景：新 checker 规则已登记
- **WHEN** `python tools/check_safety_rule_script_backing.py --root . --json` 运行
- **THEN** 输出必须包含 forward bilingual document pairs 和 local Git commit Chinese subjects 的 implemented rules
- **AND** 每条规则必须指向 prompt reminders、executable script controls 和 aggregate guard steps

#### 场景：Guard 运行新检查
- **WHEN** `python tools/run_openspec_guard.py --root . --json` 运行
- **THEN** aggregate guard 输出必须包含 `check_document_pair_policy` 和 `check_git_commit_language`
- **AND** 任一 checker 报错时 guard 必须失败

### Requirement: 实施前 implementation plan 必须 active
仓库要求被 active Comet change 在 build、verify 或 archive 阶段引用的任何 implementation plan，必须先在 registry 中标记为 `status: active`，然后才能继续实施。

#### 场景：Comet build 引用 draft implementation plan
- **WHEN** active Comet change 的 phase 是 `build`、`verify` 或 `archive`
- **AND** 其 `.comet.yaml` 引用的 `docs_bilingual/implementation_plans/` 文件在 registry 中不是 `active`
- **THEN** implementation-plan checker 必须失败
- **AND** 必须指出需要激活或替换的 change 与 plan

### Requirement: `/plan` 后与完整本地流程规则必须脚本化
仓库必须在 safety-rule script backing registry 中登记 `/plan` 后执行治理与执行到远端发布门的完整本地流程两类规则。

registry 必须指向 prompt reminders、可执行脚本控制、aggregate guard 步骤、local MR review 接线，以及 local-flow checker 表面的测试。

#### 场景：local-flow 脚本支撑被检查
- **WHEN** `python tools/check_safety_rule_script_backing.py --root . --json` 运行
- **THEN** 必须存在 `post-plan-execution-governance-package` 和 `complete-local-flow-to-remote-gate` 两条 implemented rules
- **AND** `python tools/run_openspec_guard.py --root . --json` 必须包含 `check_local_flow_scripted_enforcement`
