---
doc_id: comet_runtime_agile_focus_area_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.md
translation_of: docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.md
status: active
doc_class: implementation_plan
last_reviewed: 2026-05-27
---

# Comet Runtime 敏捷/混合式管理关注领域落地方案

## 复核结论

原方案尚不完善：状态仍为 `draft`，中文对照版存在乱码，执行切片没有充分定义 runtime 字段、阶段门禁、测试、回退路径和所有权边界。本版本将方案提升为可执行的 `active` 实施方案。

2026-05-27 颗粒度复核：方案已经通过仓库 implementation-plan checker，但仅有大切片仍不足以让 agentic worker 在不重新摸索文件所有权和测试顺序的情况下直接执行。本次修订保留五个实施切片，并补充明确的文件职责图、就绪清单、任务级 backlog、命令证据、回退规则和本地集成顺序。

2026-05-27 完备性复核：方案内容和颗粒度已经达到可实施状态。本次复核不新增 runtime 范围，只记录 active 方案已经包含五个执行切片、Task A-E 任务项、文件所有权、逐任务测试证据、中文提交示例、本地集成门禁、验收标准和风险缓解，足以让 worker 在不重新摸索方案结构的情况下继续执行。

## 目标

将 Comet runtime 治理从单向阶段标签升级为自适应管理循环，同时保留 Comet 五阶段：

`Open -> Design -> Build -> Verify -> Archive`

runtime 仍使用这些阶段名，但按项目管理关注领域进行治理：

- Open = Initiating
- Design = Planning
- Build = Executing
- Verify = Controlling
- Archive = Closing
- Monitoring = 跨阶段控制回路，不是第六个 phase

runtime 要吸收 PMBOK 第 8 版所强调的非强制性、可裁剪的管理逻辑，但 runtime 状态、提示或脚本输出不依赖 `PMBOK8` 字样。

守卫兼容声明：任一阶段发现前序不充分时，可以回退到 `open/design/build/verify` 中任意需要更新的阶段；实施采用敏捷/混合式小步迭代，不做一次性大瀑布方案。

## 非目标

- [ ] 不用第六个 phase 替代 Comet 五阶段。
- [ ] 不把 workflow 做成只能一次性向前的大瀑布流程。
- [ ] 不把 Monitoring 降级成被动检查清单。
- [ ] 不绕过 OpenSpec 对 WHAT 的治理，也不绕过 Superpowers 对 HOW 的指导。
- [ ] 不要求 runtime 字段名包含 PMP 或 PMBOK 标签。

## Runtime 治理原则

- [ ] 每个阶段在前进前必须有显式勾选证据。
- [ ] 每次前进 transition 都必须执行 Monitoring，Monitoring 可以决定继续、调整当前阶段、停止，或回退到更早的关注领域。
- [ ] 当当前证据显示前序工作不充分时，回退目标可以是 `open`、`design`、`build` 或 `verify`。
- [ ] 回退决策必须保留原因、目标阶段和迭代次数。
- [ ] workflow 要支持敏捷或混合式增量：小切片、快速反馈、受控返工。
- [ ] 控制层必须保持 OpenSpec 负责 WHAT、Superpowers 负责 HOW。

## Runtime 状态契约

`.comet.yaml` 必须包含或保留以下字段：

- [ ] `management_record`：当前 change 的管理勾选记录路径，通常是 `openspec/changes/<name>/management.md`。
- [ ] `monitoring_status`：`clear`、`needs_decision` 或 `blocked`。
- [ ] `control_decision`：`continue`、`adjust-current`、`return-open`、`return-design`、`return-build`、`return-verify` 或 `stop`。
- [ ] `target_phase`：`null`、`open`、`design`、`build` 或 `verify`。
- [ ] `rework_reason`：`null`、`scope-gap`、`planning-gap`、`execution-gap`、`verification-gap`、`value-gap`、`risk-change` 或 `stakeholder-change`。
- [ ] `iteration_count`：Monitoring 触发回退的累计次数。

### 状态不变式

- [ ] 前进 transition 要求 `monitoring_status=clear`。
- [ ] 前进 transition 要求 `control_decision=continue`。
- [ ] `control_decision=return-*` 必须有匹配的 `target_phase`。
- [ ] `control_decision=return-*` 必须有非空 `rework_reason`。
- [ ] `monitoring_status=blocked` 时不能向前推进。
- [ ] 一次回退 transition 只能让 `iteration_count` 增加一次。
- [ ] 回退 transition 不得删除既有 OpenSpec 或 Superpowers artifacts。

## 管理记录模板

每个 active change 必须有 `management.md`，并包含以下勾选区段。脚本可以按区段标题和勾选状态匹配。

```markdown
# Comet Management Record

## Open / Initiating
- [ ] Value and why are stated.
- [ ] Success criteria are measurable.
- [ ] Stakeholders, constraints, or operating boundaries are identified.

## Design / Planning
- [ ] Delivery approach is tailored: predictive, agile, or hybrid.
- [ ] Major risks and assumptions are recorded.
- [ ] Acceptance evidence path is defined.

## Build / Executing
- [ ] Execution mode is selected.
- [ ] Quality evidence is recorded: TDD, review, test, or equivalent.
- [ ] Blockers are cleared or have an explicit decision.

## Verify / Controlling
- [ ] Variance from scope, design, and acceptance criteria is checked.
- [ ] Risk and change impact are assessed.
- [ ] Control decision is recorded.

## Archive / Closing
- [ ] Value outcome is summarized.
- [ ] Lessons learned or reusable guidance are recorded.
- [ ] Delta spec sync, verification evidence, and archive path are confirmed.

## Monitoring Loop
- [ ] Current facts are checked.
- [ ] Continue, adjust, stop, or return decision is made.
- [ ] If returning, target_phase and rework_reason are recorded.
```

## 阶段门禁矩阵

| Transition | 必需关注领域证据 | Monitoring 要求 | 允许结果 |
| --- | --- | --- | --- |
| `open -> design` | Open 勾选项完成 | Monitoring 已勾选且 `continue` | 继续、调整 Open、停止 |
| `design -> build` | Design 勾选项完成 | Monitoring 已勾选且 `continue` | 继续、return-open、调整 Design、停止 |
| `build -> verify` | Build 勾选项完成 | Monitoring 已勾选且 `continue` | 继续、return-open、return-design、调整 Build、停止 |
| `verify -> archive` | Verify 勾选项完成 | Monitoring 已勾选且 `continue` | 继续、return-open、return-design、return-build、调整 Verify、停止 |
| `archive -> done` | Archive 勾选项完成 | Monitoring 已勾选且 `continue` | 完成、return-open、return-design、return-build、return-verify、停止 |

## Monitoring 回退语义

- [ ] `monitor-return-open`：用于价值、成功标准、干系人、范围或约束不完整的情况。
- [ ] `monitor-return-design`：用于计划、架构、风险、验收证据或交付方式不完整的情况。
- [ ] `monitor-return-build`：用于实现、测试、质量证据或阻塞项处理不完整的情况。
- [ ] `monitor-return-verify`：用于 Archive 或后续复核发现验证证据必须重跑或修正的情况。
- [ ] 任意回退后，目标阶段必须被重新补强，并再次通过自己的前进门禁。
- [ ] 回退循环是预期的自适应行为，默认不应被视为 workflow 失败。

## 实施切片

### Slice 1：状态与管理记录初始化

范围：
- [ ] 更新 `.codex/skills/comet/scripts/comet-state.sh init`，自动创建 `management.md`。
- [ ] 初始化 `.comet.yaml` 中的管理字段。
- [ ] 更新 `.codex/skills/comet/scripts/comet-yaml-validate.sh`，校验枚举值。
- [ ] 新增或更新 change 初始化 fixture。

完成标准：
- [ ] 新 Comet change 包含 `.comet.yaml` 字段和 `management.md`。
- [ ] 既有 change 可以校验且不丢失当前元数据。
- [ ] 非法枚举值 fail closed。

测试：
- [ ] 初始化测试覆盖 management record 创建。
- [ ] YAML 校验测试覆盖所有允许枚举。
- [ ] 负向测试覆盖非法枚举和缺失 management record。

### Slice 2：阶段勾选门禁

范围：
- [ ] 在 `comet-guard.sh` 或 helper 中增加可复用 checklist 解析。
- [ ] `open -> design` 前要求 Open 勾选项。
- [ ] `design -> build` 前要求 Design 勾选项。
- [ ] `build -> verify` 前要求 Build 勾选项。
- [ ] `verify -> archive` 前要求 Verify 勾选项。
- [ ] archive 完成前要求 Archive 勾选项。

完成标准：
- [ ] 缺失勾选项会阻断对应 transition。
- [ ] 错误输出指出缺失的 section 和 item。
- [ ] 既有非管理类 guard 约束仍然执行。

测试：
- [ ] 每个 phase 一个通过 fixture。
- [ ] 每个 phase 一个失败 fixture。
- [ ] 回归测试确认旧有 guard 约束仍生效。

### Slice 3：Monitoring 回退 transition

范围：
- [ ] 在 `comet-state.sh transition` 中增加 `monitor-return-open`、`monitor-return-design`、`monitor-return-build`、`monitor-return-verify`。
- [ ] 强制校验匹配的 `control_decision` 和 `target_phase`。
- [ ] 回退决策必须有非空 `rework_reason`。
- [ ] 成功回退时递增 `iteration_count`。
- [ ] 回退时保留既有 artifacts 和路径。

完成标准：
- [ ] 回退 transition 会把 `.comet.yaml phase` 移到目标 phase。
- [ ] 缺少 target 或 reason 时 fail closed。
- [ ] 修复勾选证据后，回退循环可以再次向前推进。

测试：
- [ ] 从 Build 回退到 Open。
- [ ] 从 Verify 回退到 Design。
- [ ] 从 Verify 回退到 Build。
- [ ] 从 Archive 回退到 Verify。
- [ ] `iteration_count` 每次回退只增加一次。

### Slice 4：Skill 指令接入

范围：
- [ ] 更新 `comet-open`，离开 Open 前要求 Open 勾选证据。
- [ ] 更新 `comet-design`，离开 Design 前要求 Design 勾选证据。
- [ ] 更新 `comet-build`，离开 Build 前要求 Build 勾选证据。
- [ ] 更新 `comet-verify`，记录偏差、风险/变更影响和回退/不回退决策。
- [ ] 更新 `comet-archive`，要求 Closing 勾选证据。
- [ ] 更新根 `comet` skill，说明自适应 Monitoring 回退。

完成标准：
- [ ] skill 指令与脚本行为一致。
- [ ] skill 明确 Monitoring 是跨阶段控制，不是第六阶段。
- [ ] skill 能把回退决策路由到正确 phase，而不是强迫继续瀑布式前进。

测试：
- [ ] 静态文本检查覆盖必需 runtime 字段。
- [ ] 静态文本检查覆盖必需回退命令。
- [ ] 使用示例 change 做一次手工 dry-run。

### Slice 5：Policy、OpenSpec 与 Checker 对齐

范围：
- [ ] 更新治理 policy，说明 Comet 是迭代式控制层。
- [ ] 更新 OpenSpec specs，加入阶段勾选和回退 transition 场景。
- [ ] 更新 `tools/run_openspec_guard.py` 或相关 checker，覆盖 runtime 管理规则。
- [ ] 如需新增测试，注册到 `tools/ci/ci_test_manifest.json`。
- [ ] 保持 `docs_bilingual` 使用英文主版和中文对照版。

完成标准：
- [ ] policy、spec、skills、scripts 和 tests 描述同一套 runtime 行为。
- [ ] implementation plan checker 通过。
- [ ] OpenSpec guard 通过。

测试：
- [ ] `python tools/check_implementation_plan_rules.py --root . --json` - 校验 implementation plan registry、双语配对、文本健康和 active 方案状态。
- [ ] `python tools/run_openspec_guard.py --root .` - 校验 OpenSpec、文档治理、implementation-plan rules 和命名清晰度门禁。
- [ ] 定向 Comet runtime 单元测试。

## 文件职责图

- [ ] `.codex/skills/comet/scripts/comet-state.sh`：负责 `.comet.yaml` 默认字段、transition 事件、Monitoring 回退 transition 和 `iteration_count` 修改。
- [ ] `.codex/skills/comet/scripts/comet-guard.sh`：负责前进 transition 门禁、管理勾选解析和 fail-closed 诊断输出。
- [ ] `.codex/skills/comet/scripts/comet-yaml-validate.sh`：负责 `monitoring_status`、`control_decision`、`target_phase`、`rework_reason`、`iteration_count` 的枚举值和跨字段不变式校验。
- [ ] `.codex/skills/comet/scripts/comet-archive.sh`：负责归档时 Closing 证据检查，以及归档完成前的最终 Monitoring 决策。
- [ ] `.codex/skills/comet/SKILL.md` 和 `.codex/skills/comet-{open,design,build,verify,archive,hotfix,tweak}/SKILL.md`：负责面向操作者的 workflow 指令和路由文字。
- [ ] `docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md` 和 `.zh-CN.md`：负责用户可见的治理语言。
- [ ] `openspec/specs/codex-user-level-comet-controlled-openspec-superpowers/spec.md` 和 `.zh-CN.md`：负责稳定 WHAT 需求。
- [ ] `test/run_openspec_guard_json.test.py`：新增 checker 或 guard 依赖时，负责 guard 聚合 fixture 覆盖。
- [ ] 如需新增定向 runtime 测试，应放在 `test/` 下，并使用能描述 runtime contract 的文件名，再注册到 `tools/ci/ci_test_manifest.json`。

## 实施前就绪定义

- [ ] 实施分支或工作树从当前本地 `main` 开始。
- [ ] `docs_bilingual/docs_registry.yaml` 中 active plan 状态保持 `active`。
- [ ] 先更新英文主版和中文对照版，再修改 runtime 脚本。
- [ ] worker 记录本次实施属于 script-only、skill-only 还是 script-plus-skill。
- [ ] 每次修改脚本前，先确认正在修改的确切 transition。
- [ ] 每个 runtime 行为变更必须在同一提交中有匹配的 test 或 checker 更新。

## 任务级执行 Backlog

### Task A：增加 runtime-state bootstrap 覆盖

**文件：**
- 修改：`.codex/skills/comet/scripts/comet-state.sh`
- 修改：`.codex/skills/comet/scripts/comet-yaml-validate.sh`
- 测试：新增或扩展 `test/comet_runtime_management_flow.test.py`
- 如新增测试则注册：`tools/ci/ci_test_manifest.json`

- [ ] Step A1：先写失败测试，初始化一个 sample change，并断言 `.comet.yaml` 包含 `management_record`、`monitoring_status: clear`、`control_decision: continue`、`target_phase: null`、`rework_reason: null`、`iteration_count: 0`。
- [ ] Step A2：运行 `python test/comet_runtime_management_flow.test.py -k bootstrap`，确认失败原因是缺少管理默认值，而不是测试搭建错误。
- [ ] Step A3：更新 `comet-state.sh` 初始化逻辑，让新 change 写入必需字段，并在缺失时创建 `openspec/changes/<name>/management.md`。
- [ ] Step A4：更新 `comet-yaml-validate.sh`，让缺失管理字段和非法枚举值按字段 fail closed。
- [ ] Step A5：重新运行 bootstrap 测试和 `python tools/check_openspec_comet_superpowers_policy.py --root . --json`。
- [ ] Step A6：使用中文提交，例如 `运行时：初始化 Comet 管理字段`。

### Task B：强制阶段勾选门禁

**文件：**
- 修改：`.codex/skills/comet/scripts/comet-guard.sh`
- 测试：新增或扩展 `test/comet_runtime_management_flow.test.py`
- 如新增测试则注册：`tools/ci/ci_test_manifest.json`

- [ ] Step B1：为 Open、Design、Build、Verify、Archive 管理区段未勾选的情况编写失败 fixture。
- [ ] Step B2：运行定向 guard 测试，确认每个 transition 当前会错误放行，或以错误原因失败。
- [ ] Step B3：在 `comet-guard.sh` 中新增一个可复用 checklist parser，不要为每个 phase 重复解析逻辑。
- [ ] Step B4：将 `open -> design`、`design -> build`、`build -> verify`、`verify -> archive` 和 archive completion 接入 parser。
- [ ] Step B5：确保诊断输出同时指出缺失的 section 和 item。
- [ ] Step B6：重新运行定向测试；如果 full guard 被无关本地状态阻塞，则运行 `python tools/run_openspec_guard.py --root . --skip-validate --json` 并记录阻塞项。
- [ ] Step B7：使用中文提交，例如 `运行时：强制阶段管理勾选门禁`。

### Task C：实现 Monitoring 回退 transition

**文件：**
- 修改：`.codex/skills/comet/scripts/comet-state.sh`
- 修改：`.codex/skills/comet/scripts/comet-yaml-validate.sh`
- 测试：新增或扩展 `test/comet_runtime_management_flow.test.py`

- [ ] Step C1：为 `monitor-return-open`、`monitor-return-design`、`monitor-return-build`、`monitor-return-verify` 编写失败测试。
- [ ] Step C2：新增负向测试：`target_phase` 缺失、`control_decision` 与事件不匹配、`rework_reason` 为 `null`、`iteration_count` 非数字。
- [ ] Step C3：在 `comet-state.sh` 中实现一个统一 return helper，将 return event 映射到目标 phase，并保留既有 artifact 路径。
- [ ] Step C4：每次成功 return event 只递增一次 `iteration_count`。
- [ ] Step C5：连续运行两次定向测试，确认重复回退能从 `0` 到 `1` 再到 `2`，且不会重置其他字段。
- [ ] Step C6：使用中文提交，例如 `运行时：支持 Monitoring 回退转换`。

### Task D：对齐 Comet skill 指令

**文件：**
- 修改：`.codex/skills/comet/SKILL.md`
- 修改：`.codex/skills/comet-open/SKILL.md`
- 修改：`.codex/skills/comet-design/SKILL.md`
- 修改：`.codex/skills/comet-build/SKILL.md`
- 修改：`.codex/skills/comet-verify/SKILL.md`
- 修改：`.codex/skills/comet-archive/SKILL.md`
- 如 preset 行为变更则修改：`.codex/skills/comet-hotfix/SKILL.md`、`.codex/skills/comet-tweak/SKILL.md`

- [ ] Step D1：补充 Monitoring 是跨阶段控制回路、不是第六 phase 的指令文字。
- [ ] Step D2：补充每个 phase 离开前必须对应管理勾选区段的要求。
- [ ] Step D3：补充 return routing 指令，使 `return-open`、`return-design`、`return-build`、`return-verify` 回到对应 Comet phase，而不是强迫继续瀑布式前进。
- [ ] Step D4：运行 `python tools/check_openspec_comet_superpowers_policy.py --root . --json`，确认所有 skill 必需术语仍存在。
- [ ] Step D5：使用中文提交，例如 `技能：对齐 Comet 管理回退指令`。

### Task E：对齐 policy、spec、checker 覆盖与集成门禁

**文件：**
- 修改：`docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.md`
- 修改：`docs_bilingual/governance/openspec_comet_superpowers_workflow_policy.zh-CN.md`
- 修改：`openspec/specs/codex-user-level-comet-controlled-openspec-superpowers/spec.md`
- 修改：`openspec/specs/codex-user-level-comet-controlled-openspec-superpowers/spec.zh-CN.md`
- checker 术语变化时修改：`tools/check_openspec_comet_superpowers_policy.py`
- guard 步骤变化时修改：`tools/run_openspec_guard.py` 和 `test/run_openspec_guard_json.test.py`
- 注册测试：`tools/ci/ci_test_manifest.json`

- [ ] Step E1：先更新英文 policy，再用相同治理含义更新中文对照版。
- [ ] Step E2：更新 stable OpenSpec requirements，覆盖 checklist evidence、Monitoring return transitions 和非瀑布式自适应执行。
- [ ] Step E3：如果引入新 checker，把它加入 `tools/run_openspec_guard.py`，并同步 `test/run_openspec_guard_json.test.py` fixture steps。
- [ ] Step E4：运行 `python tools/check_implementation_plan_rules.py --root . --json`。
- [ ] Step E5：运行 `python tools/check_openspec_comet_superpowers_policy.py --root . --json`。
- [ ] Step E6：运行 `python tools/run_openspec_guard.py --root . --json`；如果被无关 worktree hygiene 阻塞，记录准确的本地状态阻塞项。
- [ ] Step E7：使用中文提交，例如 `治理：同步 Comet 敏捷管理关注领域`。

## 本地集成顺序

- [ ] 集成前保持 feature worktree 干净：`git status --short` 不返回路径。
- [ ] 针对变更前 base 运行本地 MR review gate：`powershell -NoProfile -ExecutionPolicy Bypass -File tools/ci/local_mr_review.ps1 -Root . -BaseRef <base-sha> -HeadRef HEAD -Json`。
- [ ] 只有本地检查通过后，才 fast-forward 或 merge feature branch 到本地 `main`。
- [ ] 除非用户明确要求远端发布，否则不要推送远端。
- [ ] 在用户决定是否发布或清理前，保留 feature branch。

## 完成复核清单

- [ ] 每个 scope item 都有匹配的任务级 step。
- [ ] 每个 runtime 字段都有 bootstrap、validation 和至少一个负向测试。
- [ ] 每个前进 transition 都有通过和失败 checklist fixture。
- [ ] 每个 Monitoring return event 都有成功、缺 target、缺 reason、iteration-count 证据。
- [ ] 英文和中文文档语义一致。
- [ ] 所有提交信息使用中文。

## 验收标准

- [ ] 缺少 Open 勾选项时不能进入 Design。
- [ ] 缺少 Design 勾选项时不能进入 Build。
- [ ] 缺少 Build 勾选项时不能进入 Verify。
- [ ] 缺少 Verify 勾选项时不能进入 Archive。
- [ ] 缺少 Archive 勾选项时不能完成归档。
- [ ] Monitoring 可以在目标不清时从 Build 回退到 Open。
- [ ] Monitoring 可以在计划或验收缺口时从 Verify 回退到 Design。
- [ ] Monitoring 可以在验证证据不足时从 Archive 回退到 Verify。
- [ ] 回退决策保留 `target_phase`、`rework_reason` 和 `iteration_count`。
- [ ] runtime 对外仍然只暴露 Comet 五阶段。
- [ ] runtime 输出不要求出现 `PMBOK8` 字样。

## 需要保留的证据

- [ ] 更新后的方案对：英文主版与中文对照版。
- [ ] registry 中 `status: active` 的条目。
- [ ] state、guard、archive 和 validation helper 的脚本 diff。
- [ ] 所有 Comet phase skills 的指令 diff。
- [ ] 测试输出和 checker 输出。
- [ ] 实施完成后的归档或收尾说明。

## 风险与缓解

- [ ] 风险：checklist 解析变脆。缓解：集中维护必需 item 标签，并测试缺失项输出。
- [ ] 风险：回退循环掩盖真实失败。缓解：强制 `rework_reason` 并递增 `iteration_count`。
- [ ] 风险：用户误以为 Monitoring 是第六阶段。缓解：只把 Monitoring 作为 transition evidence。
- [ ] 风险：docs 与 runtime 漂移。缓解：checker 覆盖，并成对更新 skills、scripts 和 specs。

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
