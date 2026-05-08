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

主目录新鲜度规则是强制规则：主目录 `D:\PythonProject_langgraph` 是 primary main worktree（主 main 工作区），必须检出本地 `main`，其 HEAD 不得落后于本地 `main`，正常应与本地 `main` 完全一致。本地 `main` 在开始新写入工作、发布判断、创建/更新 MR、声明主线状态前，必须先 fetch（拉取远端引用）`gitlab/main`，并确保不落后于最新 `gitlab/main`。若本地 `main` 落后于 `gitlab/main`，应先 fast-forward（快进）；若主目录有脏文件或不在 `main`，必须先停止写入并处理 hygiene（卫生检查）问题。功能实现仍不得直接落在主目录 `main`，应落在 feature worktree / feature branch（功能工作区 / 功能分支）。`D:\PythonProject_langgraph` 是 primary directory（主目录），用于协调和本地 mainline 镜像，不是 feature-task workspace（功能任务工作区）。

## 2. 权威边界

本策略属于仓库级治理。它适用于所有会修改本仓库的 Codex 会话，包括普通 Codex、oh-my-codex 包装会话、native subagents、durable-team workers，以及后续 LangGraph 驱动的执行上下文。

本策略不授权删除 worktree、重置分支或丢弃本地编辑。任何破坏性清理仍然必须先有 preservation-first plan（先保存再清理的计划）和操作者确认。

## 3. 必需 Worktree 模型

- `main` - 本地镜像已评审 `gitlab/main` 的分支；不要把它当作可写任务分支。
- `gitlab/main` - 指向权威 GitLab mainline 的远端跟踪分支。
- `github/main` - GitLab main 变绿后同步过去的 GitHub 镜像分支。
- `.worktrees/` - 本地 secondary Git worktrees 的容器；它是本地工作区基础设施，不是文档或源码目录。
- `backup/*` - 在风险对齐操作前保存脏工作区快照的本地备份分支命名空间。

每个可写任务必须使用：

1. 一个能说明任务的专用 feature branch。
2. 一个位于 `.worktrees/` 下的专用 worktree。
3. 一个 GitLab-first MR，合并后才能进入 `main`。

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
- GitLab MR 合并后，先把本地 `main` 分支引用快进到同一个 GitLab main commit，再把该 exact commit 同步到 GitHub。

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

Feature worktree 是临时执行面。本地验证通过、所有计划保留的已跟踪改动已经提交、`git status` 干净，并且没有未处理的 `.local/`、未跟踪文件、证据文件、缓存、OCR 输出、私有文件、版权文件或大文件之后，feature worktree 可以在 GitLab 发布完成前释放。释放 worktree 是指用 Git worktree 命令删除本地文件系统 worktree；它不会删除 feature branch。

Feature branch 是发布载体。本地和远端 feature branch 必须保留到 GitLab MR 已合并、本地 `main` 已快进到 GitLab main commit，并且 GitHub `main` 已同步到同一 commit。只有在这个发布闭环结束之后，才可以删除本地和远端 feature branch。

释放 worktree 前必须先处理文件分类：

- 已跟踪文件：释放 worktree 前必须先提交。
- 应进入仓库的未跟踪文件：释放 worktree 前必须先 `git add` 并提交。
- `.local/`、抽取证据、缓存、OCR 输出和其他本地生成文件：默认不提交；如果后续还需要使用，先移动到明确的本地证据目录，或生成可提交的 run summary（运行摘要）。
- 私有文件、版权文件或大文件：不提交原始 payload；仓库需要证据时，只提交 manifest（清单）、summary（摘要）、path（路径）、hash（哈希）、quality metric（质量指标）或 provenance record（来源记录）。
- 无法判断的文件：不能跟随 worktree 一起删除；必须先让操作者选择保留、提交、移动、摘要记录或丢弃。

安全总结是：feature worktree 只要已经干净且文件完成分类，就可以更早清理；feature branch 必须保留到远端发布闭环结束。
## 6. 脚本控制

这个安全边界不能只靠提示词提醒。

仓库提供：

- `tools/check_worktree_session_hygiene.py` - 只读 checker，用来检查已登记 Git worktrees、脏状态、重复脏路径和 `main` 对齐风险。

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
Hygiene checker（工作区卫生检查器）还会在 JSON 输出中报告 `worktree_release_candidates`。`worktree_release_candidates` 是只读状态列表，用来区分 `worktree_release_ready` 和 `branch_cleanup_ready`：前者表示 feature worktree 在本地验证和文件分类后已经干净到可以删除，后者表示 feature branch 已合并且 GitLab / GitHub mainline refs 已对齐。
```

上面的命令会运行只读会话认领 checker，并输出 JSON 报告，供冷启动会话或本地发布前检查使用。

任务认领 checker 的补充要求：

- 每个 active claim（活跃认领文件）都必须写入 `.omx/session-claims/*.json`。`.omx/session-claims/*.json` 是 ignored JSON 文件，用来声明当前会话认领的 OpenSpec change 或路径范围。
- 任务认领预检必须覆盖 worktrees、branches、remote-tracking branches、active OpenSpec changes、active claim files、target paths，以及 ignored 或 local-only 的 guard-scanned files，避免新会话绕过 checker-backed ownership（脚本支撑的归属判断）。

推荐在创建 worktree 或修复 guard 问题前运行：

```powershell
python .\tools\check_session_ownership_claims.py --root . --precheck-task "<task-slug-or-description>" --target-path "<repo-relative-path>" --openspec-change "<change-id>" --json
```

上面的命令会运行任务预检 checker。`--precheck-task` 用来说明准备处理的任务，`--target-path` 用来说明仓库相对热点路径，`--openspec-change` 用来说明准备处理的 OpenSpec change id，`--json` 用来输出机器可读报告。token 可用时，可以加 `--check-gitlab-mrs` 读取打开中的 GitLab MRs；必须在无法检查 GitLab MRs 时 fail closed（失败关闭）时，才加 `--require-gitlab-mrs`。

## 7. Local-First Mirrored CI/MR 集成

所有仓库变更采用 local-first + mirrored CI/MR gate（本地优先且本地/远端镜像复用的 CI/MR 闸门）。GitLab 仍然是权威远端 review 与 merge 面，但远端 CI/MR 是本地 gate 已经运行之后的确认层和审查留痕层；这不表示每个本地 checkpoint commit（检查点提交）都必须推送到远端服务器。

Runner 配额与发布包规则：

- 使用 local-first batching（本地优先批量发布）节省 GitLab runner minutes。GitLab runner minutes 是 GitLab pipeline 消耗的有限远端 CI 配额。
- Local CI（本地持续集成）是主要检查逻辑。远端发布前必须运行 `tools/ci/local_gate.ps1`；`tools/ci/local_gate.ps1` 是仓库共享 CI gate（持续集成闸门）脚本，用来运行 OpenSpec guard、仓库 checker / guard、可选本地测试和 whitespace diff check（空白差异检查）。
- 进入 CI 管理的测试必须登记在 `tools/ci/ci_test_manifest.json`。`tools/ci/ci_test_manifest.json` 是稳定测试清单，用来防止本地或远端 CI 意外运行历史测试、环境依赖测试或尚未纳入发布 gate 的实验测试。
- Local MR review（本地合并请求审查）是推远端前的审查面。必须在所有计划保留的改动已提交、feature worktree 干净之后，远端发布之前运行 `tools/ci/local_mr_review.ps1`；`tools/ci/local_mr_review.ps1` 会汇总 feature branch 相对 base branch 的 diff、commit log、diff stat 和 merge simulation（合并模拟），并且在 `git status --porcelain` 报告 dirty worktree entries（脏工作区条目）时默认失败。
- Remote CI（远端持续集成）必须镜像复用本地 CI gate。GitLab CI 和 GitHub mirror workflow 可以安装必要工具并调用 `tools/ci/local_gate.ps1`，但不得维护一套会与本地 CI 漂移的独立 checker sequence（检查序列）。
- Remote MR review（远端合并请求审查）和 remote CI 保留为干净环境确认、权限、合并状态和审查留痕层。
- 如果本地 gate 与远端 CI 结果不一致，必须修复共享脚本、环境安装或 CI 配置漂移；不得绕过本地或远端任一 gate。
- 本地 `main` 不得落后于权威远端。新建可写任务、判断发布时机、push、创建/更新 MR 或声明主线状态之前，必须刷新 `gitlab/main`；如果本地 `main` 落后，就先 fast-forward（快进）本地 `main` 再继续。如果 feature branch 基于陈旧远端基线准备，发布前必须 rebase（变基）或 merge（合并）到刷新后的基线，除非用户明确接受 stale-base risk（陈旧基线风险）。
- 主目录 `D:\PythonProject_langgraph` 是 primary main worktree（主 main 工作区），必须检出本地 `main`，其 HEAD 不得落后于本地 `main`，正常应与本地 `main` 完全一致。若本地 `main` 落后于 `gitlab/main`，应先 fast-forward；若主目录有脏文件或不在 `main`，必须先停止写入并处理 hygiene 问题。功能实现仍不得直接落在主目录 `main`，应落在 feature worktree / feature branch。`tools/check_worktree_session_hygiene.py` 必须在主目录脏、主目录不在 `main`、主目录落后于本地 `main` 或本地 `main` 落后于 `gitlab/main` 时失败。
- 首次推送前，先在本地完成 commits、checker runs、local MR review、rework 和 cleanup。commits 是本地 Git 提交，checker runs 是本地检查命令执行，local MR review 是本地合并请求审查，rework 是本地返工，cleanup 是提交前清理。
- 对已经本地完成、准备发布的 OpenSpec change，默认采用 single-MR archive package（单 MR 归档发布包）。single-MR archive package 是指同一个 feature branch 同时包含实现或文档变更、`openspec/changes/archive/` 下的归档结果，以及 `openspec/specs/` 下被提升后的 stable spec。
- 小型 governance（治理）、documentation（文档）、checker（检查脚本）和 test（测试）类变更，只要本地验证已经证明完成且 review scope（评审范围）共享同一个 rollback boundary（回退边界），就应采用 single-MR archive package。
- 只有在实现规模大或风险高、需要先让远端 CI 或 MR review 确认实现、归档提升会产生大量 stable-spec 冲突，或用户明确要求 implementation-only MR（只发实现 MR）时，才使用 two-MR flow（双 MR 流程）。two-MR flow 必须记录 archive follow-up（归档跟进），不得把 completed active change 视为已经关闭。
- 只有在主题、验证面和 rollback boundary（回退边界）相同的情况下，才把相关小变更合并进一个 MR。rollback boundary 是可以安全回退而不混入无关工作的最小单位。
- 不要为了减少 runner 使用量而把无关主题合并到同一个 MR；可评审性和回退安全优先。
- 远端发布前，当前会话的模型必须根据 local validation state（本地验证状态）、active-change state（active change 状态）、archive-package state（归档发布包状态）、review scope（评审范围）、rollback boundary（回退边界）和 runner-budget value（runner 配额价值）判断发布时机，然后向用户建议 publish（发布）或 wait（继续等待）。用户仍然是 release decision authority（发布决策权威）。
- 只有 local CI 和 local MR review 都通过后，才推送到 GitLab；除非用户明确要求提前跑远端 pipeline。

默认本地优先流程：

1. 刷新 `gitlab/main`；如果本地 `main` 落后则先快进，并确认主目录 `D:\PythonProject_langgraph` 干净、检出本地 `main` 且没有落后于本地 `main`。
2. 从已对 `gitlab/main` 做过新鲜度检查的最新本地 `main` 创建 feature branch。
3. 为该分支使用专用 `.worktrees/<task>` worktree。
4. 实施 OpenSpec change，并在该 change 仍处于 active 状态时先运行本地实现验证。
5. 如果 completed change 适合 single-MR path（单 MR 路径），就在同一个 feature branch 内 archive 它，把可复用 delta specs 提升进 stable specs，并重新运行本地验证命令。
6. 提交所有计划保留的 tracked changes，并在发布审查前分类每个 untracked、ignored、本地证据、缓存、OCR 输出、私有、版权或大文件 artifact。
7. 在干净的 feature worktree 运行 `tools/ci/local_gate.ps1`。该脚本是 local CI gate，也是 remote CI mirror entrypoint。
8. 针对选定 base branch 运行 `tools/ci/local_mr_review.ps1`，先在本地查看远端 MR 会展示的内容；如果 feature worktree 仍是 dirty，该脚本必须失败。
9. 如果 completed change 需要 two-MR path（双 MR 路径），必须说明例外原因，保持 active change 或 follow-up archive task 可见，并在发布 implementation-only MR 前请求用户确认。
10. Local CI 和 local MR review 通过，且所有文件都已提交、移动、摘要记录或明确丢弃后，可以释放 feature worktree，但必须保留 feature branch 作为发布载体。
11. 再次刷新 `gitlab/main`，并确认 feature branch 没有基于陈旧远端状态。
12. 由当前会话模型建议 publish 或 wait，并说明采用 single-MR 还是 two-MR 归档决策以及本地 gate 结果，然后请用户确认发布决策。
13. 推送到 GitLab 并创建或更新 GitLab MR。
14. 等 GitLab pipeline 通过。该 pipeline 必须调用同一个 `tools/ci/local_gate.ps1` 脚本。
15. 合并到 GitLab `main`。
16. 将同一个 GitLab main commit 同步到 GitHub。
17. 将本地 `main` 分支引用快进到 GitLab `main`。
18. 确认主目录 `D:\PythonProject_langgraph` 检出本地 `main`、状态干净，并且 HEAD 没有落后于本地 `main` 分支引用；正常状态是完全相等。

本仓库默认不使用 GitHub PR。

## 8. OpenSpec 生命周期

任何创建或修改本策略的变更都属于结构性仓库治理变更，必须遵守本仓库 OpenSpec 生命周期。

必需生命周期：

1. 实施前先创建或更新 OpenSpec change。
2. 让治理策略、checker 行为和 guard 集成与该 change 保持一致。
3. 实现后、change 仍为 active 状态时，先运行仓库验证命令。
4. 对已经完成且准备发布的本地 change，默认在同一个 feature branch 内 archive 该 OpenSpec change，使 delta spec 在打开 GitLab MR 之前进入 stable spec。
5. archive 提升后再次运行仓库验证命令。
6. 除非明确选择 two-MR exception（双 MR 例外），否则通过一个 GitLab-first MR 同时发布实现、归档移动和 stable spec。

归档隔离规则：

- 如果 change 会影响代码、可执行检查、CI、stable specs、startup instructions、仓库指令面或结构性治理规则，并且适合 single-MR path，应在同一个隔离 feature worktree 中完成归档。若单独 archive worktree 更安全，也必须先合回同一个发布分支，再打开 MR。
- archive worktree 或 feature worktree 必须先通过相关验证命令，之后才能提交 archive 结果。archive 结果合入发布分支后，该分支必须再次通过验证。
- 纯说明性文本改动如果不改变可执行的仓库行为，可以使用轻量归档流程；无法判断时应使用 archive-before-publication package flow（发布前归档包流程）。
- 不要留下实现已经合并到 `main`、但 OpenSpec change 仍 active 的 worktree-isolation change。completed active change（已完成但仍 active 的 change）是生命周期缺口，即使 tasks 全部打勾也一样。
- 如果使用 two-MR exception，implementation MR 必须说明为什么推迟 archive，并留下可见的 follow-up archive path（后续归档路径）；不得宣称 OpenSpec 生命周期已经关闭。
