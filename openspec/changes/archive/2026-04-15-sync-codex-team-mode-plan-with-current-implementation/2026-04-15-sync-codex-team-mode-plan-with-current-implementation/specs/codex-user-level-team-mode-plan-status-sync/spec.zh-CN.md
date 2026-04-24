## ADDED Requirements

### Requirement: canonical 双语 team-mode 实施方案必须反映当前真实实现状态
Codex / oh-my-codex 用户级 team-mode 的 canonical 双语实施方案必须清晰区分：

- 当前已实现状态
- 可选高级路径
- 真正未来工作

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
