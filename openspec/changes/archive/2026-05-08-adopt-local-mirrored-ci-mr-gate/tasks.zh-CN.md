## 1. Implementation

- [x] 新增 `tools/ci/local_gate.ps1` 作为本地/远端 CI 共享入口。
- [x] 新增 `tools/ci/local_mr_review.ps1` 作为本地 MR review 和 merge simulation 入口。
- [x] 更新 `.gitlab-ci.yml`，改为调用共享 local gate 脚本。
- [x] 更新 `.github/workflows/openspec-guard.yml`，改为调用共享 local gate 脚本。
- [x] 更新 `AGENTS.md` 发布流程表述。
- [x] 更新英文和中文启动摘要里的发布姿态。
- [x] 更新英文和中文 multi-session worktree governance policy。
- [x] 为本 change 添加双语 OpenSpec artifacts。

## 2. Validation

- [x] 运行 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_gate.ps1 -Json`。
- [x] 运行 `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tools\ci\local_mr_review.ps1 -Json`。
- [x] 运行 `openspec validate --all`。
- [x] 运行 `python .\tools\run_openspec_guard.py --root . --tool codex --json`。
- [x] 运行 `git diff --check`。
