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

本策略不授权删除 worktree、重置分支或丢弃本地编辑。任何破坏性清理仍然必须先有 preservation-first plan（先保存再清理的计划）和操作者确认。

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

Feature worktree 是临时执行面。本地验证通过、所有计划保留的已跟踪改动已经提交、`git status` 干净，并且没有未处理的 `.local/`、未跟踪文件、证据文件、缓存、OCR 输出、私有文件、版权文件或大文件之后，feature worktree 可以在 GitLab 发布完成前释放。释放 worktree 是指用 Git worktree 命令删除本地文件系统 worktree；它不会删除 feature branch。

Feature branch 是发布载体。本地 feature branch 必须保留到本地 `main` 已包含预期结果；如果存在远端发布分支，则必须保留到 GitLab/GitHub 发布或镜像闭环已对齐预期本地 `main` commit。只有在这个闭环结束之后，才可以删除本地和远端 feature branch。

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
- 本地集成批准和远端发布批准是两个独立 release decisions。本地 `main` 集成后，会话必须停在 remote-publication approval gate；除非当前用户消息或 approved release record 明确授权该远端发布动作，否则不得推送 GitLab、创建/更新/合并 GitLab MR、同步 GitHub、删除远端发布分支或修改远端 refs。泛化的 `continue`、`继续`、`go on` 或 `proceed` 不是远端发布批准，除非它明确点名该远端动作。
- 主目录 `D:\PythonProject_langgraph` 是 primary main worktree，必须检出本地 `main`，其 HEAD 不得落后于本地 `main`，正常应与本地 `main` 完全一致。`tools/check_worktree_session_hygiene.py` 必须在主目录脏、主目录不在 `main`、主目录落后于本地 `main`，或本地 `main` 未经明确风险接受却落后于 `gitlab/main` 时失败。
- 本地 `main` 集成或首次远端推送前，先在本地完成 commits、checker runs、local MR review、rework 和 cleanup。
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
6. 提交所有计划保留的 tracked changes，并在集成审查前分类每个 untracked、ignored、本地证据、缓存、OCR 输出、私有、版权或大文件 artifact。
7. 在干净的 feature worktree 运行 `tools/ci/local_gate.ps1`。该脚本是 local CI gate，也是 remote CI mirror entrypoint。
8. 针对选定 base branch 运行 `tools/ci/local_mr_review.ps1`，先在本地查看本地集成和后续远端 MR 会展示的内容；如果 feature worktree 仍是 dirty，该脚本必须失败。
9. 如果 completed change 需要 two-step path，必须说明例外原因，保持 active change 或 follow-up archive task 可见，并在 implementation-only publication 前请求用户确认。
10. 由当前会话模型建议 integrate / publish 或 wait，并说明采用 single-package 还是 two-step 归档决策以及本地 gate 结果，然后请用户确认发布决策。
11. 用户批准后，先把已验证 feature branch 集成进本地 `main`，线性分支优先使用 fast-forward。
12. 验证主目录 `D:\PythonProject_langgraph` 检出本地 `main`、状态干净，并位于预期本地 `main` commit。
13. 如果本地 `main` 领先 `gitlab/main` 或 `github/main`，报告 intentional remote lag 并保留 publication carrier branch。
14. 当本地 `main` 领先 GitLab 或 GitHub 时，先请求明确的远端发布批准；不得把泛化的继续指令当作批准。只有当前用户消息或 approved release record 明确授权后，才推送到 GitLab 并创建或更新 GitLab MR。
15. 使用 GitLab 远端确认时等待 GitLab pipeline 通过；该 pipeline 必须调用同一个 `tools/ci/local_gate.ps1` 脚本。
16. 远端 CI 若与本地结果不一致，修复本地/共享 gate 或环境漂移，不得绕过证据。
17. GitLab 远端确认变绿后，或用户明确选择 direct mirroring 时，把预期本地 `main` commit 精确同步到 GitHub。
18. 只有当本地 `main`、GitLab 发布状态和 GitHub 镜像状态都达到预期闭环后，才删除 feature branch。

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
