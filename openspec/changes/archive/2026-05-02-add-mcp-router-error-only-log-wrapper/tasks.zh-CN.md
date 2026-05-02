## Tasks（任务）

- [x] 1. 创建 `add-mcp-router-error-only-log-wrapper` 的双语 OpenSpec artifacts；该 change 定义可选启用的 MCP Router 日志过滤行为。
- [x] 2. 新增 `tools/mcp-router-log-filter-wrapper.ps1` 和 `tools/mcp_router_log_filter_wrapper.py`；前者是 launcher，后者是 Python core，用来保留 protocol stdout、把完整日志写入文件，并且只转发可操作错误。
- [x] 3. 新增 `test/mcp_router_log_filter_wrapper.test.ps1`；这是 PowerShell 测试，用来覆盖无害噪音压制、协议保留、错误转发、日志留存和非零退出传播。
- [x] 4. 运行验证命令；包括 wrapper tests、`openspec validate --all`、`python tools/run_openspec_guard.py --root . --json` 和 `git diff --check`。
- [x] 5. 按 GitLab-first workflow 发布；推送 feature branch 到 GitLab，打开 merge request，等待 pipeline 成功，合并到 GitLab `main`，再把同一个 `main` 提交同步到 GitHub。
