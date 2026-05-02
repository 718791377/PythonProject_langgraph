## Tasks / 任务

- [x] 1. 创建 `codex-direct-browser-design-mcp-policy` 双语 OpenSpec artifacts；该 change 用来定义 Codex 直连 MCP 边界。
- [x] 2. 更新 `docs_bilingual/governance/codex_user_level_mcp_scope_policy.md` 和 `.zh-CN.md`；这些治理文件说明 Codex 直连使用 `chrome-devtools` 与 `pencil`，并保持 `mcp_router` 禁用。
- [x] 3. 更新 `openspec/specs/codex-user-level-mcp-scope-policy/spec.md` 和 `.zh-CN.md`；这些 stable specs 将验收要求对齐到 Codex 直连 MCP 规则。
- [x] 4. 更新 `tools/check_mcp_router_scope_policy.py` 和 `tools/mcp_router_scope_policy_exceptions.json`；checker 会强制 Codex 直连 MCP entry，并将旧的 disabled-bridge exception 标记为 resolved。
- [x] 5. 运行验证命令；包括 `python tools/check_mcp_router_scope_policy.py --root . --json` 这个 MCP scope checker、`openspec validate --all` 这个 OpenSpec 全量校验命令、`python tools/run_openspec_guard.py --root . --json` 这个仓库 guard 汇总命令，以及 `git diff --check` 这个 Git 空白错误检查命令。
- [ ] 6. 按 GitLab-first workflow 发布；先将 feature branch 推送到 GitLab 并创建 merge request，等待 pipeline 成功后合并到 GitLab `main`，再把同一个 `main` commit 同步到 GitHub。
