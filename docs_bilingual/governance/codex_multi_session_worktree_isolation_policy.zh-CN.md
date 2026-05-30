---
doc_id: codex_multi_session_worktree_isolation_policy
lang: zh-CN
doc_class: governance
status: active
---

# Codex 多会话 Worktree 隔离治理策略

## 1. 目的

本策略定义多个 Codex 会话同时处理本仓库时，如何避免脏文件、分支漂移和跨会话覆盖风险。

核心规则是：

```text
一个可写任务 = 一个 Git worktree + 一个 feature branch
```

仓库根目录 `D:\PythonProject_langgraph` 是协调区和 mainline 镜像区；它不能变成多个会话共享的临时写入目录。

主目录新鲜度规则是强制规则：主目录 `D:\PythonProject_langgraph` 是 primary main worktree（主 main 工作区），必须检出本地 `main`，其 HEAD 不得落后于本地 `main`，正常应与本地 `main` 完全一致。本地 `main` 在开始新写入工作、发布判断、远端 push、创建/更新 MR、声明主线状态前，必须先 fetch（拉取远端引用）`gitlab/main`，并确保不落后于最新 `gitlab/main`，除非用户明确接受 stale-base risk。经批准本地集成后，本地 `main` 可以有意领先 `gitlab/main` 和 `github/main`；必须报告这种远端滞后直到发布或镜像同步追上。若主目录有脏文件或不在 `main`，必须先停止写入并处理 hygiene（卫生检查）问题。功能实现仍不得直接落在主目录 `main`，应落在 feature worktree / feature branch。`D:\PythonProject_langgraph` 是 primary directory（主目录），用于协调和本地 mainline 集成，不是 feature-task workspace。

## 2. 权威边界

本策略属于仓库级治理。它适用于所有会修改本仓库的 Codex 会话，包括普通 Codex、oh-my-codex 包装会话、native subagents、durable-team workers，以及后续 LangGraph 驱动的执行上下文。

本策略只授权经过脚本门禁的本地清理：当 helper 证明 feature worktree 已干净、feature branch 已被本地 `main` 包含、completed claim 已被保留、且本地 rollback backup ref 存在时，可以清理已合入的本地 feature worktree 与本地 feature branch。它不授权 reset、强制删除、删除远端 ref、删除 backup ref 或丢弃本地编辑；这些破坏性动作仍然必须先有 preservation-first plan（先保存再清理的计划）和操作者确认。

## 3. 必需 Worktree 模型

- `main` - 经批准本地验证后的第一本地集成分支；不要把它当作可写任务分支。
- `gitlab/main` - 用作上游新鲜度基线和 GitLab 发布目标的远端跟踪分支。
- `github/main` - 预期本地 `main` commit 的 GitHub 镜像/同步目标。
- `.worktrees/` - 本地 secondary Git worktrees 的容器；它是本地工作区基础设施，不是文档或源码目录。
- `backup/*` - 在风险对齐操作前保存脏工作区快照的本地备份分支命名空间。

每个可写任务必须使用：

1. 一个能说明任务的专用 feature branch。
2. 一个位于 `.worktrees/` 下的专用 worktree。
3. 一个 local-main-first 集成决策，使结果先进入本地 `main`，之后按用户批准执行远端发布/同步。

## 4. 多会话安全规则

多个会话可以并行准备相互独立的工作，但前提是写入范围相互隔离。

必需规则：

- 不要让两个会话写同一个 worktree。
- 不要让两个会话同时编辑同一批热点文件，除非由 leader 串行整合。
- 不要直接在 `main` 上写文件。
- 保持主目录 `D:\PythonProject_langgraph` 检出本地 `main`；它的 HEAD 不得落后于本地 `main`，正常应与本地 `main` 完全一致。可写 feature branch 应使用 `.worktrees/`，不要让主目录停留在旧分支。
- 不要手动删除 `.worktrees/`；需要清理时，先做保存检查，再使用 Git worktree 命令。
- 不要假设某个脏文件一定属于当前会话。
- 在确认归属前，不要 reset、checkout、clean、move 或 delete 未知脏文件。
- 将旧会话视为 compatibility-scoped sessions（兼容范围会话）。旧会话是较早的 Codex `/resume` thread，可能保留 stale context（陈旧上下文）、stale MCP assumptions（陈旧 MCP 假设）或 stale launcher behavior（陈旧启动器行为）。
- 除非当前会话重新验证仓库 startup summary、OpenSpec state、Git state 和 session-ownership claims，否则不要让旧会话认领新的治理实施、脏文件归属或发布权威。
- 如果旧会话与当前仓库文件不一致，在没有操作者批准的 reconciliation plan（对账计划）前，以当前仓库文件和当前本地 Git 状态为准。
- 在创建新的任务 worktree、编辑文件、修复 guard 失败项，或接手 OpenSpec / governance artifacts 之前，必须先执行任务认领预检。任务认领预检是一种只读扫描，用来在创建新写入范围前识别语义上的归属信号。
- 任务认领预检必须检查已登记 Git worktrees、本地分支、远端跟踪分支、打开中的 GitLab MRs、active OpenSpec changes、本地 `.omx/session-claims/*.json` 认领文件，以及目标路径，包括 ignored files。
- 只要 worktree 名称、branch 名称、MR 标题、MR source branch、OpenSpec change id、claim path 或目标文件路径出现语义匹配，就应视为 ownership signal（归属信号）；即使对应 worktree 是干净的、也没有领先 `main` 的提交，也仍然算作认领信号。
- 如果发现匹配的 ownership signal，在 leader 明确串行化 handoff、继续使用已有 worktree，或把该信号归类为 completed stale residue 之前，都必须把该任务视为已认领。
- 位于 guard 扫描目录中的 ignored 或 local-only 文件，只要会影响仓库检查结果，就仍然是 task object（任务对象）。在修复、移动、排除或删除它们之前，必须先判断其预期归属。
- 本地集成后，确认主目录 `D:\PythonProject_langgraph` 位于预期本地 `main` commit。如果后续执行远端发布，再把 GitLab/GitHub 对齐到该预期 commit。

## 5. 脏文件分类

处理脏文件前必须先分类：

- current-task edits（当前任务编辑） - 当前会话故意修改的文件。
- other-session edits（其他会话编辑） - 可能属于其他仍在运行或刚中断会话的文件。
- generated artifacts（生成产物） - checker、refresh 或 report 生成的文件。
- scratch notes（临时笔记） - 尚未批准进入正式文档的本地笔记。
- stale residue（陈旧残留） - 废弃 worktree 或生成输出，需要 preservation-first cleanup plan（先保存再清理的计划）。

如果归属未知，保留该文件并报告，不要为了图省事直接删除。

接管任务前必须先分类任务认领状态：

- unclaimed（未认领） - worktrees、branches、MRs、OpenSpec changes、claim files 或目标路径中都不存在语义匹配。
- claimed-not-started（已认领但未开始） - 存在匹配 worktree、branch、MR、OpenSpec change、claim file 或 ignored target path，但还没有 dirty diff、额外提交或打开中的 MR 进展。
- in-progress（处理中） - 匹配 worktree 已经有 dirty files、领先提交、open MR、active OpenSpec change，或带有重叠路径的 active claim。
- completed-stale（已完成但残留） - 匹配 branch 或 claim 属于已经合并或归档的工作；只有 leader 明确把 handoff 串行化并确认 preservation-safe 后，才可以复用。

## 5.1 Feature Worktree 释放与 Branch 清理

Feature worktree 是临时执行面。本地验证通过、所有计划保留的已跟踪改动已经提交、`git status` 干净、没有未处理的 `.local/`、未跟踪文件、证据文件、缓存、OCR 输出、私有文件、版权文件或大文件、本地 `main` 已包含该 branch 结果、rollback backup ref 已存在、completed claim 已保留到主目录之后，feature worktree 可以在 GitLab 发布完成前释放。释放 worktree 是指用 Git worktree 命令删除本地文件系统 worktree。

本地 feature branch 在本地 `main` 已包含预期结果且存在 rollback backup ref 之后，也属于可清理的临时本地执行面。`tools/cleanup_integrated_worktree.py` 通过门禁后，可以先保留 completed claim，再删除 `.worktrees/` 下的 feature worktree，并用 `git branch -d` 删除已合入的本地 feature branch。远端发布分支、远端 refs 和 backup refs 仍受保护：本地清理不得删除它们，远端发布仍必须由用户明确授权。

释放 worktree 前必须先处理文件分类：

- 已跟踪文件：释放 worktree 前必须先提交。
- 应进入仓库的未跟踪文件：释放 worktree 前必须先 `git add` 并提交。
- `.local/`、抽取证据、缓存、OCR 输出和其他本地生成文件：默认不提交；如果后续还需要使用，先移动到明确的本地证据目录，或生成可提交的 run summary（运行摘要）。
- 私有文件、版权文件或大文件：不提交原始 payload；仓库需要证据时，只提交 manifest（清单）、summary（摘要）、path（路径）、hash（哈希）、quality metric（质量指标）或 provenance record（来源记录）。
- 无法判断的文件：不能跟随 worktree 一起删除；必须先让操作者选择保留、提交、移动、摘要记录或丢弃。

安全总结是：本地 `main` 集成后，干净的 `.worktrees/` feature worktree 与已合入的本地 feature branch 可以由受保护 helper 自动清理；远端 refs 和 backup refs 不自动清理。
## 5.2 Worktree 任务 Receipt 与生命周期状态

每个新建 feature worktree 在开始可写工作前，必须携带 durable task metadata（持久任务元数据）。元数据有两个 local-only surface（仅本地表面）：

1. `.omx/session-claims/<session>.json` 声明 session ownership，用于冲突检查。
2. `.omx/worktree-task-receipt.json` 放在 worktree 内部，作为简短 receipt，让任何恢复会话都能第一眼知道这个 worktree 为什么存在。

两个 surface 至少必须记录：任务名、任务摘要、worktree 路径、branch、创建或接管会话、创建时间、是否只是文档计划、是否还需要后续代码实现、涉及路径、下一步动作、是否需要合入本地 `main`、是否需要远端同步，以及预计 merge-or-pause 时间点。

允许的生命周期标签是：`active`、`paused`、`ready-to-merge`、`merged-local-main`、`cleaned`、`remote-sync-needed`、`completed`、`superseded`。如果 worktree 暂时不能合入，必须留下其中一个明确标签和具体下一步动作。只写计划文档的 worktree 默认不长期保留：写完计划，运行本地验证，合入本地 `main`，创建 rollback ref，保留 completed receipt，然后清理 worktree 和本地 feature branch。

每次本地 `main` 合入或远端发布/同步后，操作者流程必须扫描 `git worktree list --porcelain`、active session claims 和残留 worktree 分类。后续回答“接下来做什么”时，必须把残留 worktree 单独列出，不允许混在大任务 backlog 里被遗忘。completed receipt 必须保存 rollback ref、合入后的 local-main commit、已清理 worktree、已删除 branch，以及远端同步状态。

`tools/check_worktree_task_receipt.py` 是这个生命周期的脚本控制。普通 guard 模式下，为兼容历史 worktree，缺少 receipt 会报告 warning；当前工作流新建的 worktree 必须立即写入 receipt。严格模式（`--require-all-feature-worktrees`）可用于迁移或审计所有残留 worktree。


## 5.3 Portable No-Backend parallel session fallback

ASCII-safe zh-CN companion summary: when OMX, LangGraph, or any durable backend is unavailable, a session may still start a bounded parallel implementation slice with repository-local portable files only. The fallback startup entrypoint is `python tools/claim_implementation_plan.py start ...`; before tracked implementation edits begin, it must write three metadata surfaces.

1. an active `.omx/session-claims/<session>.json` implementation-plan claim; the claim helper and `tools/check_implementation_plan_claim_lock.py` enforce one active session per child implementation plan.
2. `.omx/worktree-task-receipt.json`, so a resumed session can read task name, branch, write scope, lifecycle status, next action, and remote-publication boundary without relying on a durable backend.
3. a predicted `.omx/commit-rob/entries/<entry>.json` ROB entry, so the Phase 1A scheduler/ROB contract can compare predicted and actual write sets before any local-main retire attempt.

The portable status entrypoint is `python tools/claim_implementation_plan.py status ...`. Its JSON output must show claim status, receipt lifecycle status, ROB state, and the `local-main-retire.lock` serialization boundary. This diagnostic output does not grant permission to mutate `main`.

For non-document implementation, portable startup metadata must also preserve the Stage A confirmation gate: `requires_user_confirmation_before_implementation=true`, docs-only `governance_package_commit`, `governance_package_merged_to_local_main=true`, `implementation_confirmed_by_user=true`, and `implementation_confirmation_recorded_at`. The local MR review gate reads receipt and claim metadata to verify that the confirmed implementation plan already exists on local `main`.

Portable release is metadata-only. `python tools/claim_implementation_plan.py release ...` may mark the claim released, update receipt lifecycle, and optionally flush or supersede the predicted ROB entry. It must not delete files, remove worktrees, delete branches, mutate remotes, or bypass `tools/cleanup_integrated_worktree.py`. Destructive local cleanup still requires the guarded cleanup helper after local `main` contains the branch result, a rollback ref exists, the feature worktree is clean, and the completed claim or receipt has been preserved.

## 6. 脚本控制

这个安全边界不能只靠提示词提醒。

仓库提供：

- `tools/check_worktree_session_hygiene.py` - 只读 checker，用来检查已登记 Git worktrees、脏状态、重复脏路径、branch cleanup readiness、rollback backup ref 是否存在，以及 `main` 对齐风险。
- `tools/cleanup_integrated_worktree.py` - 本地-only 的受保护清理 helper；只有在 completed claim 已保留、rollback backup ref 已确认、feature worktree 干净、branch 已合入 local `main` 时，才删除 `.worktrees/` 下的 worktree，并用 `git branch -d` 删除本地 feature branch。
- `tools/check_worktree_task_receipt.py` - 只读 checker，用来检查 feature worktree 的 task receipt、生命周期标签、branch-matching claim、只写计划文档的清理意图，以及 completed receipt 字段。

推荐用法：

```powershell
python .\tools\check_worktree_session_hygiene.py --root . --json
```

上面的命令会运行只读 hygiene checker（工作区卫生检查器），并输出给冷启动会话或 CI 使用的 JSON 报告。

如果本地 feature branch 正在编辑，当前 worktree 有意处于 dirty 状态，可以使用：

```powershell
python .\tools\check_worktree_session_hygiene.py --root . --allow-current-dirty --json
```

`--allow-current-dirty` 选项允许当前非 main worktree 处于 dirty 状态，但仍会检查 dirty `main` 和跨 worktree 冲突风险。



### 6.1 会话认领规则

在任何会把 feature worktree 变成 dirty 状态的写入任务开始前，当前会话必须先创建本地会话认领文件。

- `.omx/session-claims/` - 本地忽略的会话认领目录，用来声明当前会话拥有哪个 OpenSpec change 或路径范围；它不是 `.omx/state/` durable truth。
- `.omx/session-claims/<session>.json` - 单个会话认领文件，用 JSON 记录会话 ID、分支、worktree、任务类型、OpenSpec change 和路径范围。
- `tools/check_session_ownership_claims.py` - 只读 checker，用来扫描所有已注册 Git worktree 的本地 claim 文件，并在重复认领同一个 OpenSpec change 或重叠路径范围时失败。

示例 claim 文件：

```json
{
  "schema_version": 1,
  "session_id": "session-ownership-claims",
  "status": "active",
  "branch": "feature/session-ownership-claims",
  "worktree": "D:\\PythonProject_langgraph\\.worktrees\\session-ownership-claims",
  "task_type": "implementation",
  "openspec_changes": ["formalize-session-ownership-claims"],
  "paths": [
    "tools/check_session_ownership_claims.py",
    "docs_bilingual/governance/codex_multi_session_worktree_isolation_policy.zh-CN.md",
    "openspec/changes/formalize-session-ownership-claims"
  ]
}
```

`session_id` 是本地操作者可读的会话名称，`openspec_changes` 是当前会话认领的 OpenSpec change 列表，`paths` 是当前会话认领的仓库相对热点路径范围。

推荐检查命令：

```powershell
python .\tools\check_session_ownership_claims.py --root . --allow-current-dirty --json
```

上面的命令会运行只读会话认领 checker，并输出 JSON 报告，供冷启动会话或本地发布前检查使用。

Hygiene checker（工作区卫生检查器）还会在 JSON 输出中报告 `worktree_release_candidates`。`worktree_release_candidates` 是只读状态列表，用来区分 `worktree_release_ready` 和 `branch_cleanup_ready`：前者表示 feature worktree 在本地验证和文件分类后已经干净到可以删除，后者表示 feature branch 已合入本地 `main` 且存在 rollback backup ref。GitLab/GitHub 对齐状态只作为发布状态单独报告，不再阻断本地-only branch cleanup。

任务认领 checker 的补充要求：

- 每个 active claim（活跃认领文件）都必须写入 `.omx/session-claims/*.json`。`.omx/session-claims/*.json` 是 ignored JSON 文件，用来声明当前会话认领的 OpenSpec change 或路径范围。
- 任务认领预检必须覆盖 worktrees、branches、remote-tracking branches、active OpenSpec changes、active claim files、target paths，以及 ignored 或 local-only 的 guard-scanned files，避免新会话绕过 checker-backed ownership（脚本支撑的归属判断）。

推荐在创建 worktree 或修复 guard 问题前运行：

```powershell
python .\tools\check_session_ownership_claims.py --root . --precheck-task "<task-slug-or-description>" --target-path "<repo-relative-path>" --openspec-change "<change-id>" --json
```

上面的命令会运行任务预检 checker。`--precheck-task` 用来说明准备处理的任务，`--target-path` 用来说明仓库相对热点路径，`--openspec-change` 用来说明准备处理的 OpenSpec change id，`--json` 用来输出机器可读报告。token 可用时，可以加 `--check-gitlab-mrs` 读取打开中的 GitLab MRs；必须在无法检查 GitLab MRs 时 fail closed（失败关闭）时，才加 `--require-gitlab-mrs`。

## 7. Local-First Mirrored CI/MR 集成

所有仓库变更采用 local-main-first integration（本地 main 优先集成）和本地/远端镜像复用的 CI 证据。GitLab 是本地 gate 已经运行之后的远端发布、干净环境确认、备份和审查留痕面；它不再是本地 `main` 集成前的默认权威闸门。这不表示每个本地 checkpoint commit（检查点提交）都必须推送到远端服务器。

Runner 配额与发布包规则：

- 使用 local-first batching（本地优先批量发布）节省 GitLab runner minutes。GitLab runner minutes 是 GitLab pipeline 消耗的有限远端 CI 配额。
- Local CI 是主要检查逻辑。本地 `main` 集成或远端发布前必须运行 `tools/ci/local_gate.ps1`；该脚本是仓库共享 CI gate，用来运行 OpenSpec guard、仓库 checker / guard、可选本地测试和 whitespace diff check。
- 进入 CI 管理的测试必须登记在 `tools/ci/ci_test_manifest.json`，防止本地或远端 CI 意外运行历史测试、环境依赖测试或实验测试。
- Local MR review 是本地集成前审查面。必须在所有计划保留的改动已提交、feature worktree 干净之后、本地 `main` 集成或远端发布之前运行 `tools/ci/local_mr_review.ps1`；它会汇总 feature branch 相对 base branch 的 diff、commit log、diff stat 和 merge simulation，并且在 `git status --porcelain` 报告 dirty worktree entries 时默认失败。
- Remote CI 必须镜像复用本地 CI gate。GitLab CI 和 GitHub mirror workflow 可以安装必要工具并调用 `tools/ci/local_gate.ps1`，但不得维护一套会与本地 CI 漂移的独立 checker sequence。
- Remote MR review 和 remote CI 保留为干净环境确认、权限、备份、镜像状态和审查留痕层。
- 如果本地 gate 与远端 CI 结果不一致，必须修复共享脚本、环境安装或 CI 配置漂移；不得绕过任一证据层。
- 本地 `main` 不得从陈旧远端基线继续。新建可写任务、判断发布时机、远端 push、创建/更新 MR 或声明主线状态之前，必须刷新 `gitlab/main`；如果本地 `main` 落后，就先 fast-forward 本地 `main` 再继续，除非用户明确接受 stale-base risk。如果 feature branch 基于陈旧远端基线准备，本地集成或发布前必须 rebase 或 merge 到刷新后的基线，除非用户明确接受风险。
- 经批准本地集成后允许 intentional remote lag（有意远端滞后）。本地 `main` 可以领先 `gitlab/main` 和 `github/main`；会话必须明确报告该状态，直到远端发布或镜像同步追上。
- 本地集成批准和远端发布批准是两个独立 release decisions。本地 `main` 集成后，会话必须停在 remote-publication approval gate；除非当前用户消息或 approved release record 明确授权该远端发布动作，否则不得推送 GitLab、创建/更新/合并 GitLab MR、同步 GitHub、删除远端发布分支或修改远端 refs。泛化的 `continue`、`继续`、`go on` 或 `proceed` 不是远端发布批准，除非它明确点名该远端动作。 规则：不得把泛化的继续指令当作批准。
- 当前用户消息如果明确说 `推送远端`、`publish remote`、`push remote`、`remote publication`、`走 GitLab MR 后同步 GitHub` 或等价远端发布措辞，就视为一次性批准正常绿色路径的完整远端发布流程：推送或更新 GitLab publication branch、创建或更新 GitLab MR、等待 GitLab CI、CI 绿色后合并 MR、fetch 并确认 GitLab `main`、把同一个预期 commit 同步到 GitHub `main`，以及运行发布后状态检查。正常绿色路径中不得拆成多次授权。
- 已批准远端发布流程中，应优先使用 sandbox 已允许的命令和已批准 command prefixes，尽量不请求权限提升。如果 Codex sandbox 仍要求对 GitLab push / MR / CI / merge 或 GitHub sync 这类已批准流程内命令进行提升，则只请求一次覆盖整个 `推送 GitLab / 开 MR / 合并 MR / 同步 GitHub` 流程的 scoped escalation，不得每条命令重复询问。若需要 force push、修改 protected branch 设置、删除远端 ref、改写历史、扩大 scope 或修改凭据/安全配置，必须停止并重新请求授权。
- 主目录 `D:\PythonProject_langgraph` 是 primary main worktree，必须检出本地 `main`，其 HEAD 不得落后于本地 `main`，正常应与本地 `main` 完全一致。`tools/check_worktree_session_hygiene.py` 必须在主目录脏、主目录不在 `main`、主目录落后于本地 `main`，或本地 `main` 未经明确风险接受却落后于 `gitlab/main` 时失败。
- 每次提交本地仓库 commit 前，必须运行 `tools/check_precommit_update_archive.py --root . --json`，或依赖已安装的 `.githooks/pre-commit` hook 间接调用 `tools/run_openspec_guard.py`。该提交前复核必须检查 existing governance、CI manifest、checker registration 或 OpenSpec lifecycle 文件是否需要同步更新或 archive movement；必要更新与 completed OpenSpec archives 必须先处理完才能 `git commit`。如果走 two-step exception，必须同时记录 `x_archive_deferred_reason` 与 `x_archive_follow_up`。
- 本地 `main` 集成或首次远端推送前，先在本地完成 commits、checker runs、local MR review、rework 和 cleanup。
- 本地 feature commit 必须使用中文提交主题。`docs:`、`fix:` 等 ASCII conventional prefix 可以保留，但主题正文必须包含中文。
- 对已经授权实施的仓库本地任务，本地流程默认授权到远端发布门为止：会话可以创建 feature worktree、本地提交、验证、创建 rollback ref、fast-forward 合入本地 `main`、运行合入后 local gate、保留 completed claim，并通过受保护 helper 清理本地 worktree/branch，不需要再次询问本地集成授权。该默认授权不包含任何 GitLab 或 GitHub 变更。
- 对已经本地完成、准备集成的 OpenSpec change，默认采用 single integration package（单本地集成包）。该包是指同一个 feature branch 同时包含实现或文档变更、`openspec/changes/archive/` 下的归档结果，以及 `openspec/specs/` 下被提升后的 stable spec。
- 小型 governance、documentation、checker 和 test 类变更，只要本地验证已经证明完成且 review scope 共享同一个 rollback boundary，就应采用 single integration package。
- 只有在实现规模大或风险高、需要先让远端 CI 或 MR review 确认实现、归档提升会产生大量 stable-spec 冲突，或用户明确要求 implementation-only publication 时，才使用 two-step flow。two-step flow 必须记录 archive follow-up，不得把 completed active change 视为已经关闭。
- 只有在主题、验证面和 rollback boundary 相同的情况下，才把相关小变更合并进一个包。
- 不要为了减少 runner 使用量而把无关主题合并到同一个包；可评审性和回退安全优先。
- 本地集成或远端发布前，当前会话的模型必须根据 local validation state、active-change state、archive-package state、review scope、rollback boundary 和 runner-budget value 判断时机，然后向用户建议 integrate / publish 或 wait。用户仍然是 release decision authority。
- 只有 local CI 和 local MR review 都通过后，才推送到 GitLab；除非用户明确要求提前跑远端 pipeline。

默认 local-main-first 流程：

1. 刷新 `gitlab/main`；如果本地 `main` 落后则先快进（除非明确接受 stale-base risk），并确认主目录 `D:\PythonProject_langgraph` 干净、检出本地 `main` 且没有落后于本地 `main`。
2. 从最新可接受的本地 `main` 基线创建 feature branch。
3. 为该分支使用专用 `.worktrees/<task>` worktree。
4. 实施 OpenSpec change，并在该 change 仍处于 active 状态时先运行本地实现验证。
5. 如果 completed change 适合 single-package path，就在同一个 feature branch 内 archive 它，把可复用 delta specs 提升进 stable specs，并重新运行本地验证命令。
6. 每次本地 commit 前先运行 pre-commit update/archive checker，并处理所有 required existing-file update、CI manifest registration、checker registration 或 completed-change archive；之后再提交所有计划保留的 tracked changes，并在集成审查前分类每个 untracked、ignored、本地证据、缓存、OCR 输出、私有、版权或大文件 artifact。
7. 在干净的 feature worktree 运行 `tools/ci/local_gate.ps1`。该脚本是 local CI gate，也是 remote CI mirror entrypoint。
8. 针对选定 base branch 运行 `tools/ci/local_mr_review.ps1`，先在本地查看本地集成和后续远端 MR 会展示的内容；如果 feature worktree 仍是 dirty，该脚本必须失败。
9. 如果 completed change 需要 two-step path，必须说明例外原因，保持 active change 或 follow-up archive task 可见，并在 implementation-only publication 前请求用户确认。
10. 当前会话模型必须判断本地 package 是否 ready，包括 single-package 或 two-step 归档决策以及本地 gate 结果。如果 package 已 ready 且仍处于本地默认授权边界内，则不再询问额外本地集成确认，继续执行。
11. 再次刷新 `gitlab/main`，确认本地 `main` 不落后。
12. 在 `refs/backup/local-main/*-before-<branch>` 下为合入前本地 `main` 创建本地 rollback backup ref。
13. 使用 `git merge --ff-only <feature-branch>` 把已验证 feature branch 合入本地 `main`。
14. 在主目录 `main` worktree 运行合入后 local gate。
15. 用本地 `main` commit 与 rollback ref 标记 claim completed，然后使用 `tools/cleanup_integrated_worktree.py --execute` 保留 completed claim、删除干净且已合入的 feature worktree，并用 `git branch -d` 删除已合入的本地 feature branch。
16. 停在远端发布门。如果本地 `main` 现在领先 `gitlab/main` 或 `github/main`，报告 intentional remote lag；不得 push、创建/更新/合并 GitLab MR、同步 GitHub、删除 remote refs 或删除 backup refs，除非用户明确批准远端发布。
17. 当前用户消息如果明确说 `推送远端`、`publish remote`、`push remote`、`remote publication`、`走 GitLab MR 后同步 GitHub` 或等价远端发布措辞，就视为一次性批准正常绿色路径：推送或更新 GitLab publication branch、创建或更新 GitLab MR、等待 GitLab CI、CI 绿色后合并 MR、fetch 并确认 GitLab `main`、把同一个预期 commit 同步到 GitHub `main`，以及运行发布后状态检查。
18. 已批准远端发布流程中，优先使用 sandbox 已允许的命令和已批准 command prefixes。如果 Codex sandbox 仍要求对 GitLab push / MR / CI / merge 或 GitHub sync 这类已批准流程内命令进行提升，则只请求一次覆盖整个 `推送 GitLab / 开 MR / 合并 MR / 同步 GitHub` 流程的 scoped escalation，不得每条命令重复询问。
19. 远端 CI 若与本地结果不一致，修复本地/共享 gate 或环境漂移，不得绕过证据。若需要 force push、修改 protected branch 设置、删除远端 ref、改写历史、扩大 scope 或修改凭据/安全配置，必须停止并重新请求授权。
20. 远端 publication branches、remote refs 与 backup refs 的清理仍需要单独明确授权。

本仓库默认不使用 GitHub PR。

## 8. OpenSpec 生命周期

任何创建或修改本策略的变更都属于结构性仓库治理变更，必须遵守本仓库 OpenSpec 生命周期。

必需生命周期：

1. 实施前先创建或更新 OpenSpec change。
2. 让治理策略、checker 行为和 guard 集成与该 change 保持一致。
3. 实现后、change 仍为 active 状态时，先运行仓库验证命令。
4. 对已经完成且准备本地集成或远端发布的本地 change，默认在同一个 feature branch 内 archive 该 OpenSpec change，使 delta spec 在集成本地 `main` 之前进入 stable spec。
5. archive 提升后再次运行仓库验证命令。
6. 除非明确选择 two-step exception（双步骤例外），否则通过一个 local-main-first package 同时集成实现、归档移动和 stable spec。

归档隔离规则：

- 如果 change 会影响代码、可执行检查、CI、stable specs、startup instructions、仓库指令面或结构性治理规则，并且适合 single-MR path，应在同一个隔离 feature worktree 中完成归档。若单独 archive worktree 更安全，也必须先合回同一个发布分支，再打开 MR。
- archive worktree 或 feature worktree 必须先通过相关验证命令，之后才能提交 archive 结果。archive 结果合入发布分支后，该分支必须再次通过验证。
- 纯说明性文本改动如果不改变可执行的仓库行为，可以使用轻量归档流程；无法判断时应使用 archive-before-publication package flow（发布前归档包流程）。
- 不要留下实现已经合并到 `main`、但 OpenSpec change 仍 active 的 worktree-isolation change。completed active change（已完成但仍 active 的 change）是生命周期缺口，即使 tasks 全部打勾也一样。
- 如果使用 two-MR exception，implementation MR 必须说明为什么推迟 archive，并留下可见的 follow-up archive path（后续归档路径）；不得宣称 OpenSpec 生命周期已经关闭。
