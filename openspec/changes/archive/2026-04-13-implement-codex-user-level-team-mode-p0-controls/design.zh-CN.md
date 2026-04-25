## Context

双语实施方案已经完成，并且明确了长期运行模型：

- native Codex 永远是基础层
- `oh_my_codex` 是一套可选的全局开关
- `subagent_routing` 是独立的全局开关，支持 `auto / manual / off`
- `team-leader` 指的是“当前主 Codex CLI 会话”，不是一个 worker pane
- 纯净排障模式是 `oh_my_codex=off` 加 `subagent_routing=off`

现在缺的不是更复杂的编排，而是第一阶段的安全实现面。

当前状态：

- 还没有一个仓库内生成器来产出用户级 Codex 团队模式资产
- 还没有一个能把 `oh_my_codex` 与 `subagent_routing` 分开保存的状态文件
- 还没有生成版 `team-leader.toml`
- 还没有一组经过测试的开关脚本来切换这两套全局控制

当前瓶颈不是编排复杂度，而是缺少一个可以在不直接改写真实用户 Codex home 的前提下，被生成、测试、演进的安全控制层。

## Goals / Non-Goals

**Goals:**

- 实现一个仓库内安装器/生成器，用于用户级团队模式控制资产
- 把生成资产写入显式指定的 Codex home 目标路径
- 把 `oh_my_codex` 和 `subagent_routing` 作为两套独立的持久状态保存
- 在任何托管写入开始前创建安装期备份快照
- 如果安装在写入开始后失败，自动恢复之前的托管状态
- 生成 `team-leader.toml`，把“主会话即 leader”这条规则固化下来
- 证明 native `codex` 完全不被触碰
- 让这个 `P0` 切片可以在临时目录中完整测试

**Non-Goals:**

- 不直接通过这批生成资产启用完整团队执行能力
- 不实现 `omx-team-hybrid.ps1` 这类 hybrid staffing wrapper
- 不实现 compose-manifest 异构常驻 pane
- 不修改 OpenClaw runtime 或 proxy launcher
- 不在仓库开发过程中直接 patch `C:\Users\lenovo\.codex` 里的真实用户资产

## Decisions

### Decision 1：先做仓库内安装器/生成器，而不是在开发阶段直接改写真实用户 home

仓库提供一个脚本，接受显式的 `-CodexHome` 目标路径，并把用户级资产生成到该位置。

原因：

- 开发和测试都可以回退
- 可以跨项目复用，而不是和本仓库 runtime 绑死
- 在控制模型尚未完全跑通前，避免误伤用户正在使用的 Codex home

备选方案：

- 直接从仓库写入 `C:\Users\lenovo\.codex`
  否决，因为对迭代开发过于危险，也难以安全验证。
- 直接修改原生 `codex` 启动入口
  否决，因为这违反了方案里的安全边界。

### Decision 2：生成面必须完全是增量式的

安装器只生成这些新命名的资产：

- `agents/team-leader.toml`
- `bin/_codex-user-level-team-mode.ps1`
- `bin/codex-omx-*.ps1`
- `bin/codex-subagents-*.ps1`
- `bin/codex-routing-status.ps1`
- `state/user-level-team-mode.json`

它永远不会生成或覆盖：

- `codex`
- `codex.cmd`
- `codex.ps1`

原因：

- 保留原生 Codex 基础层是硬约束
- 增量式资产更容易推理，也更容易回滚

### Decision 3：用一个共享 JSON 状态文件，分别保存 `oh_my_codex` 与 `subagent_routing`

`P0` 需要一个简单、显式、所有生成脚本都能读写的状态源。

状态结构：

- `schema_version`
- `oh_my_codex`
- `subagent_routing`
- `updated_at`

默认值：

- `oh_my_codex = off`
- `subagent_routing = auto`

原因：

- 这和方案里“两套开关独立”的规则一致
- 纯净排障模式可以推导出来，而不是藏在隐式逻辑里
- JSON 易于测试和 PowerShell wrapper 处理

备选方案：

- 只用环境变量
  否决，因为对全局用户级模式来说不够持久。
- 用多个小 flag 文件
  否决，因为相关状态之间容易漂移。

### Decision 4：生成一个共享 support script，再配若干薄 wrapper

安装器会在 `bin/` 下生成一个共享 PowerShell support 文件，其余入口脚本尽量保持很薄。

原因：

- 避免把状态逻辑复制到每个 wrapper 里
- 方便后续扩展，而不用重写每一条脚本
- 让状态渲染与模式计算逻辑保持一致

### Decision 5：`team-leader.toml` 只固化“当前主会话即 leader”

生成的 leader profile 只描述当前主 Codex CLI 会话就是 leader lane，并明确否定“再开一个 leader pane”。

原因：

- 这是已经确认过的核心治理决策
- 主会话保留原生 subagent 路由权
- 避免 `team-executor` 与 leader 语义混淆

### Decision 6：生成文件带托管标记，默认拒绝覆盖非托管冲突文件

每个生成的 `.ps1` 与 `.toml` 文件都带一个托管标记头。

安装器行为：

- 对已托管文件允许重新生成覆盖
- 对非托管同名文件，除非显式 `-Force`，否则直接拒绝

原因：

- 保护用户信任
- 防止仓库静默删除或替换用户自己维护的资产

### Decision 7：安装写入必须包裹在“版本备份 + 自动回滚”的事务里

在安装器写入任何托管资产或创建共享状态文件之前，必须先在以下路径下创建一个时间戳快照：

- `<CodexHome>\backups\codex-user-level-team-mode\<timestamp>\`

快照至少要记录：

- 每一个目标生成路径
- 该路径在安装前是否存在
- 对于安装前已存在的目标文件，保存其原始内容副本
- 备份 manifest 元数据，便于运维排查与后续检查

如果写入已经开始后出现失败，安装器必须：

- 将所有目标路径恢复到安装前的内容
- 对安装前不存在、失败过程中才新建的托管文件执行删除
- 保留备份快照，便于诊断和后续人工回退

原因：

- 它把“可回滚”从承诺变成了可执行边界
- 它降低了用户 Codex home 被部分写坏的风险
- 它让“原生 Codex 必须保持可用”具备事务化保障

备选方案：

- 尽力写入，但不做回滚。
  否决，因为这会留下部分安装失败窗口。
- 只写文档，要求用户自己手工备份。
  否决，因为用户明确要求发生错误时及时还原。

## Risks / Trade-offs

- [Risk] `P0` 还不会真正改变 native Codex 或 oh-my-codex 的启动路径。
  Mitigation: 明确把 `P0` 定义为控制层基础设施，真正的 startup binding 留到后续阶段。

- [Risk] 生成版 `team-leader.toml` 未来可能与 oh-my-codex schema 演进出现漂移。
  Mitigation: 保持 profile 足够窄，只使用已有 agent TOML 的通用文本结构。

- [Risk] 用户可能误以为 `oh_my_codex=on` 就代表 durable team 已完全可用。
  Mitigation: 在生成的状态输出和 spec 中明确说明，`P0` 只负责持久化控制状态。

- [Risk] 不同 PowerShell 版本的 JSON 解析细节可能带来小故障。
  Mitigation: 使用简单 JSON 结构，并保持 Windows PowerShell 兼容实现。

- [Risk] 备份快照会随着安装次数逐步累积。
  Mitigation: 把它们统一放在 namespaced backup root 里，清理策略留到后续单独命令处理，而不放进当前安装事务。

## Migration Plan

1. 先完成 `P0` 的 proposal、design、spec、tasks 工件。
2. 实现安装器/生成器，以及生成出来的 support/wrapper 资产。
3. 给安装器增加版本备份快照与失败自动回滚逻辑。
4. 增加一个专用 PowerShell 测试，在临时 Codex home 中安装。
5. 验证默认模式、状态切换、纯净排障模式、非托管冲突拒绝逻辑，以及回滚行为。
6. 运行 OpenSpec 校验与仓库 guard 校验。
7. 真实用户 home 安装和更复杂 orchestration wrapper 留到后续阶段。

## Open Questions

- 下一阶段是应该先加生成版 playbook 与 hybrid wrapper，还是先把全局开关真正绑定到 startup 行为上。
