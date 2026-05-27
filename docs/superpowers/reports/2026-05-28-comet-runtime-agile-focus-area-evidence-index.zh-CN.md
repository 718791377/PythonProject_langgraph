---
doc_id: comet_runtime_agile_focus_area_evidence_index
lang: zh-CN
source_plan: docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md
generated_at: 2026-05-28
---

# Comet Runtime 敏捷关注领域证据索引

本报告外部化保存过去直接追加在 active implementation plan 中的历史证据包。

Source plan: `docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.zh-CN.md`

## 术语说明

- `monitor-return-open` - transition that moves the control loop back to Open；用于 Monitoring 发现启动/范围缺口时回退。
- `monitor-return-design` - transition that moves the control loop back to Design；用于 Monitoring 发现规划缺口时回退。
- `monitor-return-build` - transition that moves the control loop back to Build；用于 Monitoring 发现执行缺口时回退。
- `monitor-return-verify` - transition that moves the control loop back to Verify；用于 Monitoring 发现验证或验收缺口时回退。
- `iteration_count` - runtime state field；用于记录 Monitoring 回退循环已经发生的次数。


## 2026-05-27 Runtime 证据批次

- [x] 已在非文档 runtime 执行前记录治理顺序包。
- [x] 本批次归类为 script-plus-test 实施，不是新的 OpenSpec 范围。
- [x] 本批次不需要派生更新 `openspec/` 或 `docs/`，因为当前 active stable spec 与治理 policy 已经要求管理勾选证据、Monitoring 回退 transition 与 runtime 字段校验。
- [x] 预期 runtime 文件：`.codex/skills/comet/scripts/comet-state.sh`、`.codex/skills/comet/scripts/comet-guard.sh`、`.codex/skills/comet/scripts/comet-yaml-validate.sh`。
- [x] 预期证据文件：`test/comet_runtime_management_flow.test.py` 与 `tools/ci/ci_test_manifest.json`。
- [x] 验收证据必须包括定向 Comet runtime 测试、OpenSpec Comet/Superpowers policy checker、implementation-plan rules、pre-commit update/archive review、local CI 与 local MR review。

## 2026-05-27 本地执行治理包

- [x] 本地执行范围先以这次 `docs_bilingual` 治理包开头，再进入 runtime 脚本和测试修改。
- [x] 范围：收紧 Comet runtime 的 Monitoring 前进门禁、guard 诊断、archive closing label 和 checker fixture。
- [x] 本治理包不需要派生 `openspec/` 或 `docs/` 更新，因为稳定 policy 与 spec 已经定义管理关注领域契约。
- [x] 下一次提交可以只修改 runtime 脚本、定向测试和 Comet/Superpowers policy checker fixture。
- [x] 远端发布仍受门控；除非用户明确要求远端发布，否则停在本地 `main`。

## 2026-05-27 Skill 指令对齐治理包

- [x] 本执行区间先记录这份 `docs_bilingual` 治理包，再修改 Comet skill 指令文件。
- [x] 范围：将面向操作员的 Comet phase skills 与已实现的管理勾选门禁、Monitoring 回退 transition、非瀑布式自适应路由保持一致。
- [x] 本批次归类为 skill-plus-checker 实施，不改变 runtime 状态机行为。
- [x] 本批次不需要派生更新 `openspec/` 或 `docs/`，因为稳定 policy 与 spec 已经要求勾选证据、Monitoring 回退 transition 和适应型/混合型控制。
- [x] 预期 skill 文件：`.codex/skills/comet-open/SKILL.md`、`.codex/skills/comet-design/SKILL.md`、`.codex/skills/comet-build/SKILL.md`、`.codex/skills/comet-verify/SKILL.md`、`.codex/skills/comet-archive/SKILL.md`、`.codex/skills/comet-hotfix/SKILL.md` 和 `.codex/skills/comet-tweak/SKILL.md`。
- [x] 预期 checker 证据：`tools/check_openspec_comet_superpowers_policy.py`，如聚合 guard fixture 输出变化则同步 `test/run_openspec_guard_json.test.py`。
- [x] 验收证据必须包括 Comet/Superpowers policy checker、implementation-plan rules、定向 guard fixture 测试、pre-commit update/archive review、local CI 和 local MR review。
- [x] 远端发布仍受门控；除非用户明确要求远端发布，否则停在本地 `main`。

## 2026-05-27 Skill 指令对齐证据

- [x] Comet phase skills 已说明 Monitoring 是横切控制，不是第六个 Comet phase。
- [x] Comet phase skills 已说明前进必须满足 `monitoring_status=clear` 和 `control_decision=continue`。
- [x] Comet phase skills 已加入 `monitor-return-open`、`monitor-return-design`、`monitor-return-build` 和 `monitor-return-verify` 的回退路由。
- [x] `tools/check_openspec_comet_superpowers_policy.py` 已从聚合 skill 文本检查升级为逐 phase skill 指令术语检查。
- [x] `test/run_openspec_guard_json.test.py` 已覆盖 phase skill 丢失 Monitoring 控制回路指令时必须失败。
- [x] 本批次不改变 runtime 状态机行为；不需要派生更新 `openspec/` 或 `docs/`。

## 2026-05-27 根 Comet 控制器路由治理包

- [x] 本地执行范围先从这次 `docs_bilingual` 治理包开始，再修改根 Comet 控制器 skill 或 checker 代码。
- [x] 范围：将 `.codex/skills/comet/SKILL.md` 的阶段检测与 Monitoring 回退决策对齐，确保存在 `control_decision=return-*` 时根调度器不会强制瀑布式前进。
- [x] 本批次归类为 root-skill-plus-checker 实施；不改变 runtime shell 状态机行为。
- [x] 本批次不需要派生更新 `openspec/` 或 `docs/`，因为稳定 policy 与 spec 已经要求自适应 Monitoring 回退路由和 Comet 五阶段契约。
- [x] 预期 skill 文件：`.codex/skills/comet/SKILL.md`。
- [x] 预期 checker 证据：`tools/check_openspec_comet_superpowers_policy.py` 和 `test/run_openspec_guard_json.test.py` 应在根 Comet skill 丢失回退调度指令时失败。
- [x] 验收证据必须包含 Comet/Superpowers policy checker、定向 guard fixture 测试、implementation-plan rules、pre-commit update/archive review、local CI 和 local MR review。
- [x] 远端发布仍受门控；除非用户明确要求远端发布，否则停在本地 `main`。

## 2026-05-27 Runtime 测试证据治理包

- [x] 本地执行范围先从这次 `docs_bilingual` 治理包开始，再修改定向 runtime 测试。
- [x] 范围：补强 Monitoring 回退事件、负向回退决策校验和重复 `iteration_count` 递增的任务级证据。
- [x] 本批次归类为 test-plus-docs 实施；不改变 Comet runtime shell 行为、治理 policy 或稳定 OpenSpec 需求。
- [x] 本批次不需要派生更新 `openspec/` 或 `docs/`，因为它只用更细测试证明已经定义的 runtime 行为。
- [x] 预期测试文件：`test/comet_runtime_management_flow.test.py`。
- [x] 验收证据必须包含定向 Comet runtime management flow 测试、implementation-plan rules、pre-commit update/archive review、local CI 和 local MR review。
- [x] 远端发布仍受门控；除非用户明确要求远端发布，否则停在本地 `main`。

## 2026-05-27 Monitoring 决策门禁证据治理包

- [x] 本地执行范围先从这次 `docs_bilingual` 治理包开始，再修改定向 runtime 测试。
- [x] 范围：增加静态证据，证明 Monitoring 中非 `continue` 的决策会阻断前进；这里的 `continue` 指“当前证据足够，可以前进”，而 `adjust-current`、`return-*` 或 `stop` 指当前阶段必须调整、回退或停止。archive completion 也要求最终 Monitoring 放行。
- [x] 本批次归类为 test-plus-docs 实施；不改变 Comet runtime shell 行为、治理 policy、稳定 OpenSpec 需求或 skill 指令。
- [x] 本批次不需要派生更新 `openspec/` 或 `docs/`，因为它只证明已经定义的 guard 与 archive 行为。
- [x] 预期测试文件：`test/comet_runtime_management_flow.test.py`。
- [x] 验收证据必须包含定向 Comet runtime management flow 测试、implementation-plan rules、pre-commit update/archive review、local CI 和 local MR review。
- [x] 远端发布仍受门控；除非用户明确要求远端发布，否则停在本地 `main`。

## 2026-05-28 UTF-8 管理标签证据包

- [x] 本次先更新 `docs_bilingual` 治理记录，再修改 Comet runtime 脚本和定向测试。
- [x] 范围：让 Comet runtime 管理清单标签以可读 UTF-8 中文呈现，同时保留英文标签和既有 legacy mojibake 标签兼容性。
- [x] 本批次归类为 script-plus-test 实施；不改变 Comet 阶段模型、Monitoring transition 语义、稳定 OpenSpec 要求或面向操作员的 skill workflow。
- [x] 本包不需要派生更新 `openspec/` 或 `docs/`，因为它只增强既有 management-record 契约的标签兼容性。
- [x] 预期 runtime 文件：`.codex/skills/comet/scripts/comet-state.sh`、`.codex/skills/comet/scripts/comet-guard.sh` 和 `.codex/skills/comet/scripts/comet-archive.sh`。
- [x] 预期证据文件：`test/comet_runtime_management_flow.test.py`。
- [x] 验收证据必须包括定向 Comet runtime management flow 测试、implementation-plan rules、pre-commit update/archive review、本地 MR review 和 local CI。
- [x] 远端发布仍受门控；除非用户明确要求远端发布，否则停在本地 `main`。

## 2026-05-28 管理记录校验证据包

- [x] 本地执行范围先从这次 `docs_bilingual` 治理包开始，然后再修改 Comet runtime 校验脚本和定向测试。
- [x] 范围：让 `comet-yaml-validate.sh` 在 `management_record` 为 `null`、空值或指向缺失文件时 fail closed，确保每个 active Comet change 都保留持久化清单证据，而不是在校验阶段静默回退。
- [x] 本批次归类为 script-plus-test 实施；不改变 Comet 阶段语义、Monitoring 回退语义、稳定 OpenSpec 要求或面向操作员的 skill workflow。
- [x] 本包不需要派生更新 `openspec/` 或 `docs/`，因为既有稳定契约已经要求带有勾选证据的 management record。
- [x] 预期 runtime 文件：`.codex/skills/comet/scripts/comet-yaml-validate.sh`。
- [x] 预期证据文件：`test/comet_runtime_management_flow.test.py`。
- [x] 验收证据必须包括定向 Comet runtime management flow 测试、implementation-plan rules、pre-commit update/archive review、本地 MR review 和 local CI。
- [x] 远端发布仍受门控；除非用户明确要求远端发布，否则停在本地 `main`。

## 2026-05-28 YAML 枚举校验证据包

- [x] 本地执行范围先从这次 `docs_bilingual` 治理包开始，然后再修改定向 Comet runtime 校验测试。
- [x] 范围：补强证据，证明 `comet-yaml-validate.sh` 持续维护上文“Runtime 状态契约”定义的受管枚举契约；该契约覆盖工作流类型、当前阶段、执行模式、隔离模式、验证状态、分支处理状态、归档标记、监控状态、控制决策、回退目标和返工原因。
- [x] 本批次归类为 test-plus-docs 实施；不改变 Comet 阶段语义、Monitoring 回退语义、稳定 OpenSpec 要求或面向操作员的 skill workflow。
- [x] 本包不需要派生更新 `openspec/` 或 `docs/`，因为既有稳定契约已经要求 runtime 字段校验和 fail-closed 枚举处理。
- [x] 预期 runtime 参考文件：`.codex/skills/comet/scripts/comet-yaml-validate.sh`。
- [x] 预期证据文件：`test/comet_runtime_management_flow.test.py`。
- [x] 验收证据必须包括定向 Comet runtime management flow 测试、implementation-plan rules、pre-commit update/archive review、本地 MR review 和 local CI。
- [x] 远端发布仍受门控；除非用户明确要求远端发布，否则停在本地 `main`。

## 2026-05-28 YAML 路径校验证据包

- [x] 本地执行范围先从这次 `docs_bilingual` 治理包开始，然后再修改定向 Comet runtime 校验测试。
- [x] 范围：补强证据，证明 `comet-yaml-validate.sh` 会校验非空的设计文档、实施计划和管理记录等运行时工件路径，同时把未知 YAML 字段作为 warning 而不是前进门禁 blocker。
- [x] 本批次归类为 test-plus-docs 实施；不改变 Comet 阶段语义、Monitoring 回退语义、稳定 OpenSpec 要求或面向操作员的 skill workflow。
- [x] 本包不需要派生更新 `openspec/` 或 `docs/`，因为既有稳定契约已经要求对已记录的运行时工件执行路径校验。
- [x] 预期 runtime 参考文件：`.codex/skills/comet/scripts/comet-yaml-validate.sh`。
- [x] 预期证据文件：`test/comet_runtime_management_flow.test.py`。
- [x] 验收证据必须包括定向 Comet runtime management flow 测试、implementation-plan rules、pre-commit update/archive review、本地 MR review 和 local CI。
- [x] 远端发布仍受门控；除非用户明确要求远端发布，否则停在本地 `main`。
## 2026-05-28 Verification Report 路径校验证据包
- [x] 本地执行范围先从这次 `docs_bilingual` 治理包开始，然后再修改 Comet runtime 校验脚本和定向 runtime 测试。
- [x] 范围：让 `comet-yaml-validate.sh` 在 `verification_report` 非 `null` 且指向缺失文件时 fail closed，同时保留待验证阶段可以使用 `verification_report: null` 的既有规则。
- [x] 本批次归类为 script-plus-test 实施；不改变 Comet 阶段语义、Monitoring 回退语义、稳定 OpenSpec 需求或面向操作员的 skill workflow。
- [x] 本包不需要派生更新 `openspec/` 或 `docs/`，因为既有稳定 policy 与 spec 已经要求 verification-report 证据和缺失 artifact 的 fail-closed 处理。
- [x] 预期 runtime 文件：`.codex/skills/comet/scripts/comet-yaml-validate.sh`。
- [x] 预期证据文件：`test/comet_runtime_management_flow.test.py`。
- [x] 验收证据必须包括定向 Comet runtime management flow 测试、implementation-plan rules、pre-commit update/archive review、本地 MR review 和 local CI。
- [x] 远端发布仍受门控；除非用户明确要求远端发布，否则停在本地 `main`。
## 2026-05-28 Artifact Path 安全校验证据包
- [x] 本地执行范围先从这次 `docs_bilingual` 治理包开始，然后再修改 Comet runtime 校验脚本和定向 runtime 测试。
- [x] 范围：让 `comet-yaml-validate.sh` 在受管 artifact 路径是绝对路径或包含路径穿越片段时 fail closed，同时保持既有仓库相对路径 artifact 有效。
- [x] 本批次受管 artifact 路径为 `design_doc`、`plan`、`verification_report` 和 `management_record`。
- [x] 本批次归类为 script-plus-test 实施；不改变 Comet 阶段语义、Monitoring 回退语义、稳定 OpenSpec 需求或面向操作员的 skill workflow。
- [x] 本包不需要派生更新 `openspec/` 或 `docs/`，因为既有稳定 policy 与 spec 已经要求记录 runtime artifacts，并对缺失 artifact 进行 fail-closed 处理。
- [x] 预期 runtime 文件：`.codex/skills/comet/scripts/comet-yaml-validate.sh`。
- [x] 预期证据文件：`test/comet_runtime_management_flow.test.py`。
- [x] 验收证据必须包括定向 Comet runtime management flow 测试、implementation-plan rules、pre-commit update/archive review、本地 MR review 和 local CI。
- [x] 远端发布仍受门控；除非用户明确要求远端发布，否则停在本地 `main`。
