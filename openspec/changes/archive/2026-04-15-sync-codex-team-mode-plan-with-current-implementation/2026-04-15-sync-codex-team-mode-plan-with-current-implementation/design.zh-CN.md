## Context

双语 team-mode 实施方案一直承担着 Codex / oh-my-codex 用户级工作流的 operator-facing roadmap 角色。但在这份方案形成之后，controls、startup binding、routing thresholds、原生 Windows durable-team backend、startup leader protocol、native-subagent boundaries、以及 LangGraph durable orchestration integration 等能力都已经陆续落地、验证并归档。

当前真正的瓶颈已经不是能力缺失，而是文档漂移：部分方案段落仍把已落地行为写成 planned，或者把已经出现在真实用户级安装里的 additive surface 继续写成 future direction。这会削弱方案文档作为 canonical operator reference 的可信度。

## Goals / Non-Goals

**Goals:**

- 让双语实施方案与当前实现状态重新对齐
- 明确 implemented / optional / future 的状态边界
- 保持双语方案语义一致
- 提高 operator 对实施方案作为现实地图的信任度

**Non-Goals:**

- 不从头重写整份方案
- 不扩大到 team-mode 线以外的大范围治理重写
- 除非审计发现真正的 plan/runtime 矛盾，否则不直接改变运行时行为

## Decisions

### Decision 1：把实施方案视为 canonical 状态图，而不是纯 brainstorming 文档

这份方案不应只保留想法，而应准确表达：

- 现在已实现了什么
- 哪些是可选但已可用
- 哪些才是真正未来工作

### Decision 2：同步时以真实生成资产和主 spec 为准，而不是凭记忆改文档

同步必须以当前生成出来的用户级表面、主 spec 和归档 change 为证据源。

这样才能避免把已经过期的 roadmap 表述继续带下去。

### Decision 3：保留 future section，但必须明确标成“可选未来层”

像 mixed persistent pane compose 这种 future layer 可以继续保留，但必须清晰地放在当前默认路径之外。

### Decision 4：双语对齐必须严格

英文和中文两份方案必须保持语义一致。

如果一边已经更新状态而另一边还保留旧表述，那么滞后的那一边就应视为未完成同步。

## Risks / Trade-offs

- [Risk] 文档同步容易把实施方案写成变更日志。 → Mitigation：保持方案按阶段和决策组织，不做文件级流水账。
- [Risk] 后续实现继续推进后又会再次漂移。 → Mitigation：把文档同步本身也做成正式 capability，作为持续维护责任。
- [Risk] 可选 future layer 会被误读为默认路径。 → Mitigation：始终显式区分 default path 和 optional path。

## Migration Plan

1. 先把双语实施方案与当前已安装、已规格化的表面对照。
2. 再更新过时的 roadmap marker 和 operator-facing 状态措辞。
3. 再跑一次 OpenSpec 校验。
4. 以后凡是会实质改变 operator model 的 change，都应负责同步这份方案。

## Open Questions

- 是否要在方案里加入一条“last validated against implementation on <date>”的标记？
- 后续所有 runtime-affecting change 是否都应强制连带更新这份方案？
