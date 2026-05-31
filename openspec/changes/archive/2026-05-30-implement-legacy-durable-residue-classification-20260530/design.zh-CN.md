# 设计：Legacy Durable Residue 分类

## 决策

把既有 worktree receipt checker 作为第一层只读盘点表面，因为它已经在本地 pre-commit 与 worktree lifecycle 验证中运行。checker 现在把 repo-local `.omx/state/` residue 分类为证据，而不是 activation state。

## 分类模型

每条 durable residue record 包含：

- `kind`：稳定的机器可读 residue 类别。
- `path`：repo-relative 来源路径。
- `state_class`：面向 operator 处理的安全分组。本轮 rollout 使用的取值为：
  - `safe_cleanup_candidate`：空 residue 或陈旧 residue，只能通过已批准的 reconciliation path 清理。
  - `protected_residue`：模糊或非空 residue，需要人工检查后再处理。
  - `stale_selector`：指向当前仓库之外的 selector evidence，应刷新或忽略。
  - `selector_authority`：指向当前仓库的 selector evidence；它是 authority evidence，但自身不授予 adoption permission。
  - `legacy_completed_state`：已完成的 LangGraph state，可检查或归档，但不得自动 resume。
  - `inspectable_legacy_state`：仍作为证据保留的 legacy state，直到 operator 选择安全后续动作。
- `safe_next_action`：对 operator 安全的下一步动作。
- `auto_adopt_allowed`：本轮 rollout 始终为 false。
- `reason`：带来源归因的解释。

## 安全边界

- empty unmanaged native team directory 只可通过已批准 reconciliation path 作为安全清理候选。
- non-empty unmanaged native team directory 是 protected residue，需要人工检查。
- stale selector 只能 refresh 或 ignore，不是 adoption authority。
- active current selector 是 authority evidence，但自身不授权自动接管。
- completed LangGraph state 是 inspect-or-archive evidence，不得自动 resume。

## 备选方案

- 优先扩展生成的 PowerShell installer helper：本子方案拒绝，因为本地 checker 更快提供 repo-owned evidence，且避免触碰生成的用户级 helper 行为。
- 分类时修改 `.omx/state/`：拒绝，因为本子方案只做分类且必须保持只读。
