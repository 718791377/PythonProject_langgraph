# 验证

本地 feature branch 运行期间记录以下验证命令与结果：

- `python .\test\check_worktree_task_receipt.test.py` — 已通过；7 个测试。
- `python .\tools\check_worktree_task_receipt.py --root . --json` — commit 前必跑。
- `python .\tools\check_durable_artifact_state_surfaces.py --root . --json` — commit 前必跑。
- `openspec validate --all` — commit 前必跑。
- `python .\tools\check_implementation_plan_rules.py --root . --json` — commit 前必跑。
- `python .\tools\check_precommit_update_archive.py --root . --json` — commit 前必跑。
- `python .\tools\run_openspec_guard.py --root . --json` — commit 前必跑。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -StepTimeoutSeconds 600` — 本地 main 集成前必跑。
- `powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1` — 本地 main 集成前必跑。

远端发布不属于本验证记录。
