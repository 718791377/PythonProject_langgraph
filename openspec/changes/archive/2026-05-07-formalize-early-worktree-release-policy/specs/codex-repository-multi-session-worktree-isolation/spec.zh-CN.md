## ADDED Requirements

### Requirement: Feature Worktree Release SHALL Be Separate From Branch Cleanup

仓库 SHALL 将 feature worktree 视为临时执行面，并将 feature branch 视为发布载体。干净且已本地验证的 feature worktree MAY 在远端发布前释放，但 feature branch SHALL 保留到 GitLab MR 已合并、本地 `main` 已对齐且 GitHub `main` 已同步之后。

#### Scenario: Clean locally validated worktree is ready to release

- **GIVEN** 所有计划保留的已跟踪改动都已经提交到 feature branch
- **AND** 本地验证已经通过
- **AND** feature worktree 的 `git status` 干净
- **AND** `.local/`、未跟踪文件、本地证据、缓存、OCR 输出、私有文件、版权文件和大文件已经按分类结果提交、转移、摘要记录或明确丢弃
- **WHEN** 操作者希望减少本地 worktree 噪声
- **THEN** 可以使用 Git worktree 命令删除该 feature worktree
- **AND** 删除 worktree 不会删除 feature branch

#### Scenario: Feature branch cleanup waits for publication closure

- **GIVEN** 某个 feature branch 已用于 GitLab MR
- **WHEN** GitLab MR 已合并
- **AND** 本地 `main` 已快进到 GitLab main commit
- **AND** GitHub `main` 已同步到同一 commit
- **THEN** 可以清理本地和远端 feature branch
- **AND** 不能仅因为 feature worktree 已释放就清理 branch

#### Scenario: Hygiene checker reports cleanup readiness without deleting anything

- **WHEN** `tools/check_worktree_session_hygiene.py` 运行
- **THEN** 它分别报告干净 feature worktree 的释放候选状态和 branch 清理就绪状态
- **AND** 它保持只读
- **AND** 它列出阻塞项，例如脏文件、未合并 branch、过期的本地 `main` 或未同步的 GitHub mirror 状态