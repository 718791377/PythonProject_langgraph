# 设计中文对照

## 上下文
两份目标文档是 implementation plans，不是 runtime state。它们必须让未来冷启动 Codex 会话不依赖历史聊天即可实施或评审模板变更。

## 决策
1. 保持 `PythonProject_General` 与 `PythonProject_General_2` 两个能力层级分离。
2. Comet 只作为 OpenSpec + Superpowers governance。
3. 每份计划都包含目标、非目标、能力图、实施顺序、验证、验收和回滚。
4. 当前会话事实不得进入模板默认值。
5. 把可复用的 plan-governance requirements 提升到 stable OpenSpec spec。

## 回滚
回退本地 Git 提交。如果后续目标模板目录已经按这些计划改动，则在对应目标仓库用其本地 Git 历史独立回退。
