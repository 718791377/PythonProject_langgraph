## Tasks / 任务

- [x] 1. 为 `refresh-mainline-memory-after-durable-rollout-status-sync` 创建 OpenSpec artifacts。
- [x] 2. 更新英文 mainline memory summary，写入最新落地的 durable rollout status-sync 和 MCP policy 状态。
- [x] 3. 通过显式 UTF-8 写入路径更新中文 mainline memory summary，保持同样状态。
- [x] 4. 运行验证命令：`git diff --check`、`openspec validate --all`、`python tools/check_document_governance_rules.py --root . --json`、`python tools/check_implementation_plan_rules.py --root . --json` 和 `python tools/run_openspec_guard.py --root . --json`。
- [x] 5. 按 GitLab-first workflow 发布：推送分支到 GitLab，GitLab MR pipeline 通过后合并，再同步 GitHub main。
- [x] 6. 当没有 active session 拥有 broad `openspec/specs` 范围后再归档；清楚记录该后续项。
