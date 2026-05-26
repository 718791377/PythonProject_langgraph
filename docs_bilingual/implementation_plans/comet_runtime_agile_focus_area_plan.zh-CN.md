---
doc_id: comet_runtime_agile_focus_area_plan
lang: zh-CN
canonical: docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.md
translation_of: docs_bilingual/implementation_plans/comet_runtime_agile_focus_area_plan.md
status: draft
doc_class: implementation_plan
---

# Comet Runtime 敏捷/混合式管理关注领域落地方案

## 目标

把 Comet 从单向 `Open -> Design -> Build -> Verify -> Archive` 文案流程，升级为可前进、可回退、可迭代校准的 runtime 管理循环。

核心原则：

- [ ] 每个阶段都有勾选项作为 runtime evidence。
- [ ] Monitoring 不是单纯检查或阻拦，而是横切控制回路。
- [ ] 任一阶段发现前序不充分时，可以回退到 `open/design/build/verify` 中任意需要更新的阶段。
- [ ] 实施采用敏捷/混合式小步迭代，不做一次性大瀑布方案。

## Runtime Model

`.comet.yaml` 新增或调整字段：

- [ ] `management_record: openspec/changes/<name>/management.md` - 指向当前变更的管理证据记录。
- [ ] `monitoring_status: clear|needs_decision|blocked` - 表示 Monitoring 循环是否允许继续推进。
- [ ] `control_decision: continue|adjust-current|return-open|return-design|return-build|return-verify|stop` - 记录本轮控制决策。
- [ ] `target_phase: null|open|design|build|verify` - 标识需要回退或调整的目标阶段。
- [ ] `rework_reason: null|scope-gap|planning-gap|execution-gap|verification-gap|value-gap|risk-change|stakeholder-change` - 说明返工触发原因。
- [ ] `iteration_count: <number>` - 统计 Monitoring 触发的返工迭代次数。

新增 transition 语义：

- [ ] `monitor-return-open` - 返回 Open/Initiating 以补充目标或干系人证据。
- [ ] `monitor-return-design` - 返回 Design/Planning 以修正方案、风险或验收路径。
- [ ] `monitor-return-build` - 返回 Build/Executing 以继续实现或返工执行结果。
- [ ] `monitor-return-verify` - 返回 Verify/Controlling 以重跑验证或控制检查。

## Management Checklist Template

`management.md` 采用勾选项作为 runtime evidence：

```markdown
# Comet Management Record

## Open / Initiating
- [ ] 价值/Why 已说明
- [ ] 成功标准已说明
- [ ] stakeholders 或 constraints 已识别

## Design / Planning
- [ ] 交付方式已裁剪
- [ ] 风险与关键假设已记录
- [ ] 验收证据路径已定义

## Build / Executing
- [ ] execution mode 已选择
- [ ] TDD / review / quality evidence 已记录
- [ ] 当前阻塞项已清空或已有处理决策

## Verify / Controlling
- [ ] 偏差检查完成
- [ ] 风险/变更影响已评估
- [ ] control decision 已记录

## Archive / Closing
- [ ] 价值结果已总结
- [ ] 经验沉淀已记录
- [ ] delta spec sync / verification evidence / archive path 已确认

## Monitoring Loop
- [ ] 当前阶段事实已检查
- [ ] 是否需要回退已判断
- [ ] 若需回退，target_phase 与 rework_reason 已记录
```

## Iterative Implementation Slices

### Slice 1 — 最小可用管理记录
- [ ] 更新 `comet-state.sh init`，自动创建 `management.md`
- [ ] 初始化 `.comet.yaml` 新字段
- [ ] 更新 `comet-yaml-validate.sh` 校验字段
- [ ] 添加测试：新 change 初始化后包含管理记录

### Slice 2 — 阶段勾选项硬门控
- [ ] `comet-guard.sh open` 检查 Open 勾选项
- [ ] `comet-guard.sh design` 检查 Design 勾选项
- [ ] `comet-guard.sh build` 检查 Build 勾选项
- [ ] `comet-guard.sh verify` 检查 Verify 勾选项
- [ ] `comet-archive.sh` 检查 Archive 勾选项

### Slice 3 — Monitoring 回退控制
- [ ] `comet-state.sh transition` 支持 `monitor-return-*`
- [ ] `monitoring_status=blocked` 时要求 `target_phase`
- [ ] `control_decision=return-*` 时回退到对应 phase
- [ ] 回退时递增 `iteration_count` 并保留 `rework_reason`
- [ ] 回退后允许重新补 OpenSpec / Superpowers artifacts

### Slice 4 — Skills 接入
- [ ] `comet-open` 退出前要求补 Open 勾选项
- [ ] `comet-design` 退出前要求补 Design 勾选项
- [ ] `comet-build` 退出前要求补 Build 勾选项
- [ ] `comet-verify` 根据 Monitoring 决策继续、回退或停止
- [ ] `comet-archive` 只在 Closing 勾选项完成后归档

### Slice 5 — Checker 与文档对齐
- [ ] 更新 governance policy：说明 Comet 是迭代式控制层，不是瀑布流程
- [ ] 更新 OpenSpec spec：增加任意阶段回退场景
- [ ] 更新 checker：检查 runtime 是否具备回退 transition，而不是只检查文字映射
- [ ] 更新测试：覆盖 `return-open/design/build/verify`

## Acceptance Tests
- [ ] 缺少 Open 勾选项时不能进入 Design
- [ ] Verify 发现设计不足时可 `return-design`
- [ ] Build 发现目标不清时可 `return-open`
- [ ] Archive 前发现价值结果未沉淀时不能归档
- [ ] 回退后再次完成勾选项可继续推进
- [ ] Monitoring 不新增第六个 phase

## Assumptions
- Runtime 字段不用 `PMBOK8` 命名，只吸收其管理逻辑。
- Comet 五阶段仍保留，但不再被当作不可回头的瀑布线。
- 本方案使用 project-local Comet skills/scripts，不直接修改上游 package。
