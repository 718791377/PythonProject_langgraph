## ADDED Requirements

### Requirement: Publication SHALL use mirrored local and remote CI/MR gates

仓库发布应采用 local-first + mirrored CI/MR gate。

Feature work 应先在专用 feature worktree 或 feature branch 中完成本地 CI 和本地 MR review，之后才能推送到远端 MR review；除非用户明确要求提前运行远端 pipeline。

本地 CI 和远端 CI 应复用同一个仓库脚本入口。远端 CI 配置只应安装必要工具并调用该共享脚本；不得维护另一套会漂移的 checker sequence。

本地和远端共享的 CI 入口必须包含仓库 guard 检查、whitespace diff check（空白差异检查），以及仓库测试面中可用的 unit test / integration test runner（单元测试 / 集成测试运行器）。

本地 MR review 必须有脚本控制，并且在远端 MR 发布前汇总 feature branch 的 diff、commit log、diff stat 和 merge simulation（合并模拟）。如果 `git status --porcelain` 检测到 dirty worktree entries（脏工作区条目），它必须默认失败；除非操作者明确执行非发布用途的 dirty draft review（脏草稿审查）。

需要远端审查的变更，仍应保留远端 MR 和远端 CI 作为 remote confirmation 和 audit-record layer。

#### Scenario: Feature branch is ready for remote MR

- **WHEN** 会话准备把 feature branch 推送到远端 MR review
- **THEN** 它应运行共享 local CI gate
- **AND** 它应基于选定 base branch 运行 local MR review
- **AND** 汇总两个本地 gate 结果后，应询问用户是否推送到远端 MR review

#### Scenario: Remote CI runs

- **WHEN** GitLab CI 或其他远端 CI job 验证仓库
- **THEN** 远端 job 应调用本地会话使用的同一个 local gate 脚本
- **AND** 如果本地和远端结果不一致，应优先修复脚本、环境设置或配置漂移，而不是绕过任一 gate

#### Scenario: Low-risk remote deferral

- **WHEN** 低风险文档或本地草稿变更不需要立即远端 review
- **THEN** 会话可以建议暂缓远端发布
- **AND** 该建议仍应保留后续远端 push 前的 local CI 和 local MR review 要求
