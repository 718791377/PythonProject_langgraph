## Tasks / 任务

- [x] 1. 确认 MR 3 和 MR 4 在当前 implementation plan 中已经完成。
- [x] 2. 确认 MR 5 helper mirror source-of-truth 已经实施、验证并归档。
- [x] 3. 为 `sync-durable-rollout-plan-status` 创建双语 OpenSpec artifacts；此 change 用于防止 rollout queue 文案过期。
- [x] 4. 更新双语 cross-session durable-state isolation plan：把 MR 5 标记为完成，并把 MR 6 重述为下一步 decision point。
- [x] 5. 更新稳定的 plan-status-sync spec：要求已完成的 durable-state rollout slice 不得继续被标成 active slice。
- [x] 6. 运行验证命令：`openspec validate --all`、`python tools/run_openspec_guard.py --root . --json`、`python tools/check_name_clarity_rules.py --root . --json`、`python tools/check_implementation_plan_rules.py --root . --json` 和 `git diff --check`。
- [x] 7. 按 GitLab-first workflow 发布：推送分支到 GitLab，创建 merge request，等待 pipeline 通过，合并到 GitLab `main`，再把同一个 `main` commit 同步到 GitHub。
