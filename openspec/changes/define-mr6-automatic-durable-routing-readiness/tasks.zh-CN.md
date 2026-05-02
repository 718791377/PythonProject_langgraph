## 1. Readiness Review / 就绪复核

- [x] 1.1 确认当前 durable-state rollout queue 把 MR 6 写成下一步 decision point。
- [x] 1.2 确认 specs、generator source、tests 和 team-mode implementation plan 中已经存在 automatic durable routing 证据。

## 2. Plan and Spec Synchronization / 方案与规范同步

- [x] 2.1 创建 `define-mr6-automatic-durable-routing-readiness` 的双语 OpenSpec artifacts；这是防止重复 runtime hookup work 的 readiness-review change。
- [x] 2.2 更新双语 cross-session durable-state isolation plan：把 MR 6 readiness review 标记为完成，并把未来 runtime exercise 指向单独显式的 smoke 或 adoption gate。
- [x] 2.3 更新稳定的 plan-status-sync spec：要求 MR 6 queue 在开启重复 runtime work 前，先对账已有 automatic routing evidence。

## 3. Validation and Publication / 验证与发布

- [x] 3.1 运行验证命令：`openspec validate --all`、`python tools/run_openspec_guard.py --root . --json`、`python tools/check_implementation_plan_rules.py --root . --json`、`python tools/check_name_clarity_rules.py --root . --json` 和 `git diff --check`。
- [ ] 3.2 按 GitLab-first workflow 发布：推送分支到 GitLab，创建 merge request，等待 pipeline 通过，合并到 GitLab `main`，再把同一个 `main` commit 同步到 GitHub。
