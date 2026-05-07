# 设计：发布前归档默认规则

## 决策

仓库将 archive-before-publication（发布前归档）作为默认发布包规则，用于已经本地完成且准备发布的 OpenSpec change。

流程是：

1. 在专用 feature worktree 中实施 change。
2. change 仍处于 active 状态时，先运行本地实现验证。
3. 如果该 change 小型、且本地已确认完成，就在同一个 feature branch 内 archive，使 delta specs 提升为 stable specs。
4. 运行 archive 后验证。
5. 请用户确认发布。
6. 打开一个 GitLab MR，同时包含实现、归档移动和 stable spec 更新。

## 单 MR 路径

以下情况下使用 single-MR path（单 MR 路径）：

- 本地验证通过；
- review surface（评审面）清晰；
- rollback boundary（回退边界）一致；
- archive promotion（归档提升）不会产生大量 stable-spec 冲突。

适用对象包括小型 governance（治理）、documentation（文档）、checker（检查脚本）和 test（测试）类变更。

## 双 MR 例外路径

只有以下情况才使用 two-MR path（双 MR 路径）：

- 实现规模大或风险高；
- 需要先用远端 CI 或 MR review 确认实现；
- archive promotion 会产生大量 stable spec 冲突；
- 用户明确要求 implementation-only MR。

two-MR implementation MR 必须说明为什么推迟 archive，并留下可见的 follow-up archive path（后续归档路径）。

## 脚本支撑面

该规则不只依赖提示词记忆，而是由已有仓库检查共同支撑：

- `tools/check_worktree_session_hygiene.py`：确保可写工作不落在 primary `main`，并防止基于陈旧主线发布。
- `tools/check_session_ownership_claims.py`：防止多个会话认领同一个 OpenSpec change 或重叠路径范围。
- `tools/check_openspec_code_archive_evidence.py`：拒绝缺少 source、executable check、CI 或 test 证据的 code-class archives。
- `tools/run_openspec_guard.py`：聚合发布前使用的仓库验证面。
