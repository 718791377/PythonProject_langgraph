## Why

当前这份 Codex / oh-my-codex 用户级 team-mode 双语实施方案，已经和真实实现状态出现部分漂移。特别是用户级控制面、LangGraph backend 接入、以及归档后的 P0-P7 能力批次，已经比方案文档里描述得更完整；如果不先做一轮“文档现实同步”，operator 很容易被“已实现 / 可选 / 未来”这些状态混杂的表述误导。

## What Changes

- 对照当前用户级 installer 输出、主 spec 和已归档的 P0-P7 变更，对双语 team-mode 实施方案做一轮状态审计。
- 更新已经过时的状态标记，尤其是仍把已落地能力写成 planned / future 的部分。
- 重新对齐 P0-P7 映射表及其上下文叙述，使其符合当前真实实现。
- 明确哪些表面是现在已实现的，哪些仍然只是高级可选路径，哪些才是真正的未来工作。
- 保持英文与中文实施方案文件的语义对齐。

## Capabilities

### New Capabilities
- `codex-user-level-team-mode-plan-status-sync`：让 Codex / oh-my-codex 用户级 team-mode 的双语 canonical 实施方案持续对齐当前实现状态、可选高级路径与未来工作边界

### Modified Capabilities
- `documentation-layering-and-bilingual-openspec-governance`：澄清 canonical implementation-plan 文档应如何区分“当前已实现状态”和“未来状态”

## Impact

- impact_scope:
  - Codex / oh-my-codex 用户级 team-mode 的双语实施方案文档
  - 文档治理层中“当前状态 vs 未来状态”的表达规则
  - operator 对“现在已经能用什么”的理解
- explicit_non_goals:
  - 默认不直接改运行时行为
  - 除非在同步中发现严重漂移，否则不改 installer / wrapper 实现
  - 不新增 durable backend
- rollout_sequence:
  - 先把当前方案文档和已实现表面对照
  - 再更新过时章节、阶段映射表和 operator 指南
  - 最后验证双语语义是否一致
- rollback_plan:
  - 只回滚本次同步的文档与文档类 spec 变更
  - 保持运行时和 installer 行为不变
- validation_path:
  - 确认方案文档能正确反映当前用户级资产和状态文件
  - 确认方案文档能正确区分 implemented / optional / future
  - 运行 `openspec validate --all`
- mainline_classification:
  - existing mainline continuation
  - 更具体地说，是 Codex / oh-my-codex 用户级 team-mode 主线上的 documentation-state synchronization
