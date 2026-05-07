# Design：主 main 工作区新鲜度

## 规则模型

该规则使用新鲜度链路表达，而不是笼统的“完全对齐”措辞：

```text
主 main 工作区不得落后于本地 main；本地 main 不得落后于最新 gitlab/main
```

正常情况下，主目录 `D:\PythonProject_langgraph` 检出本地 `main`，并且 HEAD 与本地 `main` 分支引用完全一致。功能实现仍然必须落在专用 feature worktree 和 feature branch 中。

## Checker 行为

`tools/check_worktree_session_hygiene.py` 保留现有主工作区检查，并把本地 `main` 与远端 `gitlab/main` 的比较从“只看是否相等”改为“基于祖先关系判断是否落后”：

- 本地 `main` 等于 `gitlab/main`：通过，并输出匹配信息；
- 本地 `main` 落后于 `gitlab/main`：失败，并要求在写入工作或发布前先快进；
- 本地 `main` 领先于 `gitlab/main`：按“不落后”通过，同时提醒操作者不要把主目录 `main` 当作功能工作区；
- 本地 `main` 与 `gitlab/main` 分叉：失败，并要求先处理主线对账。

## 回退

如需回退，可恢复之前的策略措辞和 equality-only checker warning；但更强的“落后即失败”检查更符合脚本控制要求。
