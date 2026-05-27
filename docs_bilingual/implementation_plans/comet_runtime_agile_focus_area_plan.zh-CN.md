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
