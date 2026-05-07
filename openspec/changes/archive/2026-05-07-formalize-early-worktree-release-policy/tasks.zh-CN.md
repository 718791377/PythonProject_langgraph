# 任务

- [x] 1. 更新英文 worktree 隔离策略，加入提前释放 worktree、延后 branch 清理和文件分类清理规则。
- [x] 2. 更新中文对照 worktree 隔离策略，保持相同规则。
- [x] 3. 扩展 `tools/check_worktree_session_hygiene.py`，分别报告 worktree 释放候选状态和 branch 清理就绪状态。
- [x] 4. 增加干净 feature worktree 可释放、合并后 branch 可清理的单元测试。
- [x] 5. 更新 multi-session worktree isolation 的 stable OpenSpec requirement。
- [x] 6. 完成本地验证，并在发布前归档该 change。