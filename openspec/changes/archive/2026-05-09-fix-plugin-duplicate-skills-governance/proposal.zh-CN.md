## 背景

当前本地发布闸门被一个已经存在于 `main` 的 skills governance 错误阻塞：插件提供的重复 `Chrome` skill 被当成同层重复错误处理，但现行策略已经规定插件 skill 和插件重复项在支持细粒度过滤前属于 bundle-managed / report-only。

这会导致无关 feature 分支即使自身测试和 OpenSpec 工件健康，也无法通过 `tools/ci/local_gate.ps1`。

## 变更内容

- 调整 `tools/check_codex_skills_governance.py`，把 plugin 层内重复 skill 名称归类为非阻塞 warning。
- 保持 user / repo 同层重复为阻塞错误，除非 registry 明确声明临时例外。
- 增加 plugin 层重复 skill 名称的回归测试。
- 保持所有 plugin 和 user-level skill 文件只读；不修改插件缓存、用户 skill 或 `C:\Users\lenovo\.codex\config.toml`。

## 能力影响

### 新增能力

- 无。

### 修改能力

- `codex-user-level-skills-governance-lifecycle`：明确 plugin 层重复 skill 名称是 report-only warning，而未豁免的 user/repo 同层重复仍是阻塞错误。

## 影响范围

- 影响代码：`tools/check_codex_skills_governance.py`。
- 影响测试：`test/check_codex_skills_governance.test.py`。
- 影响规格：归档后更新 `openspec/specs/codex-user-level-skills-governance-lifecycle/spec.md`。
- 范围：仓库本地 guard 行为，以及 local/remote CI 复用的 gate 行为。
- 非目标：不删除插件，不改写 user-level skill，不移除 Vercel/browser 能力，不修改用户级 Codex 配置。
- 发布顺序：修 checker、加测试、验证 active change；本地验证通过后同分支归档，再按 GitLab-first 流程发布。
- 回滚：回滚 checker/test/spec delta；plugin/user skill 文件保持未改动。
- 验证路径：`openspec validate --all`、`python tools/run_openspec_guard.py --root . --json`、`python -m unittest test/check_codex_skills_governance.test.py`、`tools/ci/local_gate.ps1 -RequireCleanGit`、`tools/ci/local_mr_review.ps1`。
- 主线分类：active user-level skills governance 线下的小型跨主线 governance/CI blocker 修复。
