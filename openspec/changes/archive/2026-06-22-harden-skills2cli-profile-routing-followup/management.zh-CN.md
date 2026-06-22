# 管理记录：硬化 Skills2CLI Profile Routing 后续契约

## Open / Initiating

- [x] 已记录 value/why：在初始 Skills2CLI profile-routing 基线之后，收口专家复核指出的 routing quality 与 safety gaps。
- [x] 已记录 success criteria：Stage A 冻结 contract；Stage B 实施 checker/runtime/test hardening；不发生远端发布或 profile apply。
- [x] 已记录 stakeholders / constraints：不改 `config.toml`、不改 plugin cache、不改 vendor `SKILL.md`、不修改 remote，skills/profiles 不是 native expert evidence。

## Design / Planning

- [x] 已记录 delivery tailoring：两个 local-main packages，先 Stage A plan-freeze，再 Stage B runtime implementation。
- [x] 已记录 major risks / assumptions：只有字段没有行为证明、`full` fallback 膨胀、apply-boundary drift、installed-copy drift。
- [x] 已定义 acceptance evidence path：plan docs、delta spec、focused checker/test output、representative suggestions、OpenSpec guard、local gate、local MR review、completed claim。

## Build / Executing

- [x] 已选择 execution mode：主会话实现，专家只读 fan-in，LangGraph durable checkpoint state，并使用 worktree isolation。
- [x] 已记录 quality evidence：`python test\skills2cli.test.py`、`python test\check_skills2cli_profile_routing.test.py`、`python test\check_plugin_modules_skill.test.py`、`python -X utf8 tools\check_plugin_modules_skill.py --root . --json`、`python -X utf8 tools\check_skills2cli_profile_routing.py --root . --json`、代表性 `skills2cli profile suggest` smoke、`python tools\run_openspec_guard.py --root . --tool codex --json`、`python tools\check_precommit_update_archive.py --root . --json`，以及 local gate / local MR review。
- [x] Blockers 已清理或有明确决策：此前 expert timeout/stall 视为非证据；主会话接管 implementation，verifier 执行只读 review。没有发生 config/cache/vendor/remote mutation。

## Verify / Controlling

- [x] 已检查 scope、design 与 acceptance criteria 的 variance：diff 限定在 profiles registry、Skills2CLI runtime/contract/checkers、plugin-modules helper scripts、focused tests 与 OpenSpec bookkeeping/archive。
- [x] 已评估 risk / change impact：`full` 为 explicit-only，advisory output 保持 no-auto-apply，installed-copy drift 只报告不信任，hard-load 仍限 top-level。
- [x] 已记录 control decision：clean local validation 后继续归档；因为未授权 GitLab/GitHub publication，所以停止在 remote publication gate。

## Archive / Closing

- [x] 已总结 value outcome：Skills2CLI routing 具备 scenario metadata、orthogonal scope checks、task-module identity、显式 `full` eligibility、installed-artifact drift reporting 与 advisory no-apply evidence。
- [x] 已记录 lessons learned / reusable guidance：profile suggestions 只能作为 advisory/preview surfaces；不得把 profile/skill routing 当作 native expert evidence；user-level install/apply 前必须报告 installed-copy drift。
- [x] 已确认 delta spec sync、verification evidence 与 archive path：delta spec 将同步到 `openspec/specs/codex-user-level-plugin-modules-profile-helper/spec.md`；archive target 为 `openspec/changes/archive/2026-06-22-harden-skills2cli-profile-routing-followup/`；verification report path 已写入 `.comet.yaml`。

## Monitoring Loop

- [x] 已检查 current facts：Stage A 已集成到 local `main` at `6919f0b`；Phase B implementation 位于 worktree branch `implement-skills2cli-profile-routing-followup-runtime`。
- [x] 已作出 continue / adjust / stop / return decision：继续；不需要返回早期阶段。
- [x] ?? return???? target_phase ? rework_reason?target_phase means ??????? Comet phase?rework_reason means ???????????????????? `target_phase=null` ? `rework_reason=null`?
