## Tasks（任务）

- [x] 1. 创建 `refresh-mainline-memory-after-cleanup-output-closeout` 的 OpenSpec artifacts。
- [x] 2. 更新英文 mainline memory summary，记录最新 MR 6 readiness、cleanup-output closeout 和本地 archive-worktree 清理状态。
- [x] 3. 通过显式 UTF-8 写入路径更新中文 mainline memory summary，保持同样状态。
- [x] 4. 修复 `codex-user-level-mainline-memory-handoff` 的中文 stable-spec companion 乱码。
- [x] 5. 运行验证命令：`git diff --check`、`openspec validate --all`、`python tools/check_document_governance_rules.py --root . --json`、`python tools/check_implementation_plan_rules.py --root . --json`、`python tools/check_name_clarity_rules.py --root . --json` 和 `python tools/run_openspec_guard.py --root . --tool codex --json`。
- [x] 6. 按 GitLab-first workflow 发布：推送分支到 GitLab，pipeline 通过后打开/合并 GitLab MR，然后同步 GitHub main。