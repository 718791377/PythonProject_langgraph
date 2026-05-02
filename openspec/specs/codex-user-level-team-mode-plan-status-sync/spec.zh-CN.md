# Codex 用户级 Team Mode 方案状态同步

## 目的

保持 Codex / oh-my-codex 用户级 team-mode 双语 canonical 实施方案与当前已实现状态、可选高级路径以及真实未来工作边界一致。

## 要求

### Requirement: canonical 双语 team-mode 实施方案必须反映当前真实实现状态

Codex / oh-my-codex 用户级 team-mode 的 canonical 双语实施方案必须清楚区分：

- 当前已实现状态
- 可选高级路径
- 真实未来工作

一旦某个用户级表面已经落地并通过验证，实施方案就不得继续把它只标成 planned。

#### Scenario: 某个能力批次已经落地

- **WHEN** 某个用户级 team-mode 能力已经实现、验证并进入当前 operator surface
- **THEN** canonical 实施方案必须把它描述为当前已实现状态
- **AND** 不得继续把该能力保留为仅 planned

### Requirement: 双语 team-mode 实施方案必须保持语义对齐

英文与中文实施方案在“当前状态 / 可选状态 / 未来状态”的语义上必须保持一致。

#### Scenario: 某一语言版本先更新了状态

- **WHEN** 某一语言版本的实施方案被更新，以反映新的当前实现状态
- **THEN** 配对语言版本也必须同步成同样的状态分类
- **AND** 双语文件之间不得保留互相冲突的实现状态含义

### Requirement: LangGraph capability-gap narrative 必须反映已经验证过的当前实现状态

一旦 LangGraph capability 工作已经落地并通过仓库验证，canonical bilingual implementation plan 与 startup-facing repository narrative 就必须把这些能力描述为已落地状态，而不是继续保留为“仍在计划中”。

至少要清楚区分：

- 已经实现的 current state
- 仍然受限但已经落地的 current state
- 真实尚未实现的 future work

#### Scenario: LangGraph appendix 仍把已落地能力写在 future-work 段落中

- **WHEN** 当前双语 implementation plan 仍把已经落地的 LangGraph surface 放在 future-work section
- **THEN** plan-status sync 过程必须把这些 surface 移入 current-state classification
- **AND** 只把真实尚未落地的 LangGraph gap 留在 future-work section

#### Scenario: Startup-facing summary 仍把已经完成的 sync pass 写成下一步

- **WHEN** startup-facing repository summary 在 capability-gap sync 已经完成之后，仍然把它写成 pending next step
- **THEN** plan-status sync 过程必须更新这类 startup-facing narrative
- **AND** 不得把已经完成的 sync pass 继续表述为下一个未完成优先项

### Requirement: Durable-state rollout queues SHALL not point at already archived slices as next active work / durable-state rollout ????????????????? active work

?????????? rollout slice ??????????????? durable-state implementation plans ???? slice ???????

#### Scenario: Helper mirror source-of-truth slice has already landed / helper mirror source-of-truth ??????

- **WHEN** ????? helper mirror source-of-truth ???????
- **AND** ?? specs ? tests ???? helper mirror provenance contract
- **THEN** cross-session durable-state isolation plan ??? MR 5 ??????
- **AND** ????? MR 5 ?????? active implementation slice
- **AND** ??? MR 6 ????? MR 6 readiness review ?????? decision point
