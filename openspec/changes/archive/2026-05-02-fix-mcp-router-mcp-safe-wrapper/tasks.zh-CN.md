## Tasks / 任务

- [x] 1. 创建 `fix-mcp-router-mcp-safe-wrapper` 双语 OpenSpec artifacts；该 change 用来定义 MCP-safe wrapper 修正范围。
- [x] 2. 更新 `tools/mcp_router_log_filter_wrapper.py`；这是 wrapper 的 Python core，负责 stdout/stdin byte-transparent 转发、stderr error-only filtering 和完整日志保留。
- [x] 3. 更新 `test/mcp_router_log_filter_wrapper.test.ps1`；这是 wrapper 的 PowerShell 测试入口，覆盖无换行 JSON-RPC、`Content-Length` frame、大 payload、stderr filtering、日志保留和非零退出码传播。
- [x] 4. 运行验证命令；包括 wrapper tests、`openspec validate --all` 这个 OpenSpec 全量校验命令、`python tools/run_openspec_guard.py --root . --json` 这个仓库 OpenSpec guard 汇总命令，以及 `git diff --check` 这个 Git 空白错误检查命令。
- [x] 5. 按 GitLab-first workflow 发布；先将 feature branch 推送到 GitLab 并创建 merge request，等待 pipeline 成功后合并到 GitLab `main`，再把同一个 `main` commit 同步到 GitHub。
