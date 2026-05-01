## Tasks（任务）

- [x] 1. 创建 `refresh-mainline-memory-after-mcp-scope-policy` 的双语 OpenSpec artifacts；该 change 目录用于说明为什么需要刷新 handoff，以及如何验证。
- [x] 2. 更新 `AGENTS.md`；这是仓库指令入口，用来让后续 MCP Router scope 问题路由到稳定 MCP policy 文档。
- [x] 3. 更新 `docs_bilingual/project_startup_summary.md` 和 `docs_bilingual/project_startup_summary.zh-CN.md`；这对 startup summary 文件需要把 MCP scope policy 加入冷启动阅读顺序，并清楚处理没有 active change 的状态。
- [x] 4. 更新当前 mainline memory summary 对照文件；这些位于 `docs_bilingual/memory/` 的易漂移 handoff 文件需要先识别最新落地的 MCP 与 memory-handoff 增量，再列出下一步。
- [x] 5. 运行验证命令；包括 `openspec validate --all`、`python tools/run_openspec_guard.py --root . --json`、`python tools/check_name_clarity_rules.py --root . --json` 和 `git diff --check`。
- [ ] 6. 按 GitLab-first workflow 发布；推送 feature branch 到 GitLab，打开 merge request，等待 pipeline 成功，合并到 GitLab `main`，再把同一个 `main` 提交同步到 GitHub。
