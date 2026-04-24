## Context

P3 已经把角色路由阈值、先研究后实现的分离规则，以及对抗式 bug review 规则写进了生成出来的策略输出。

但 P3 之后的真实状态仍然是：

- `codex-routing-policy.ps1` 只能把 bug-review triad 作为“文档中的阈值”展示出来
- `team-leader.toml` 与 `team-mode-playbook.md` 也只是提到了这三个角色，但仍停留在说明层
- 真实用户级 agent roster 里仍然没有 `bug-finder`、`bug-rebutter`、`bug-judge`
- 这意味着 Codex CLI 虽然“知道该什么时候用这条通道”，但这条最强审查通道本身还不能被真实调用

P4 的目标，就是在不改变核心启动模型的前提下补齐这条缺口：

- 原生 Codex 仍然是永久底座
- oh-my-codex 仍然是全局特性开关，而不是按 session 改写
- burst-review 角色仍然是 leader 侧短突发角色，而不是持久 pane

## Goals / Non-Goals

**Goals:**

- 生成真正存在的 `bug-finder`、`bug-rebutter`、`bug-judge` 用户级 agent profiles
- 保持这些角色为 leader 侧、短突发、默认只读
- 让 routing-policy 检查面能把这些角色显示为“已安装可调用资产”
- 更新生成出来的 `team-leader.toml` 与 `team-mode-playbook.md`，使其与现实中的 burst-review 角色一致
- 将新文件纳入同一套 additive-only 备份与回滚事务
- 在触碰真实用户安装前，先在临时 Codex home 里完成可测试验证

**Non-Goals:**

- 不创建持久化 bug-review 团队或 compose manifest
- 不在每次 `codex` 启动时自动调用 burst-review 角色
- 不改变全局开关模型
- 不修改原生 `codex.cmd`、原生 `omx.cmd` 或 OpenClaw runtime 行为
- 不强制每个项目都必须使用 bug-review triad

## Decisions

### Decision 1: 生成稳定的用户级 agent 文件，并使用精确可调用名称

安装器将生成：

- `agents/bug-finder.toml`
- `agents/bug-rebutter.toml`
- `agents/bug-judge.toml`

这些精确名称就是 routing policy、playbook 说明以及真实 `omx agents list --scope user` 验证的统一契约。

Why:

- 路由阈值中已经显式使用了这些角色名
- 稳定名称可以跨仓库复用
- 用户级生成方式保持了功能的增量性与可逆性

### Decision 2: 保持 burst-review triad 为 leader 侧、默认只读

这三个角色不是持久 worker pane。

它们的默认姿态是：

- 检查代码、测试、diff 和证据
- 默认不编辑文件
- 只有经过 judge 保留的幸存项，才允许进入 `executor` 或 `debugger`

Why:

- 这能保持“短突发专家”和“持久 worker”之间的边界
- 这符合用户要求的“研究 / 仲裁”和“实现”分离
- 这能减少争议 bug 审查期间的跨角色写冲突

### Decision 3: 把激励结构直接写进生成的角色 prompt

`bug-finder` 采用偏召回率的激励：

- 低影响 bug：`+1`
- 中等 bug：`+5`
- 严重 bug：`+10`

`bug-rebutter` 采用偏证伪的激励：

- 证伪成功，获得对应分数
- 未能证伪真实问题，则扣双倍分数

`bug-judge` 负责仲裁：

- 以“存在隐藏正确答案”为前提
- 正确判决加分，错误判决扣分
- 输出唯一值得继续升级处理的幸存项集合

Why:

- 用户明确要求把这套更强的对抗式审查闭环落地
- 这套激励结构本身就是操作契约的一部分，不只是可有可无的说明文字

### Decision 4: 扩展共享 support runtime，增加 burst-role 元数据与安装可见性检测

P0 到 P3 已经把 `bin/_codex-user-level-team-mode.ps1` 作为生成出来的共享运行时。

P4 会继续扩展它，加入：

- 解析用户级 `agents/` 目录的辅助函数
- 结构化的 burst-review 角色元数据
- 每个生成角色的安装可见性检测
- 在 routing-policy 输出中展示已安装的 burst-role 集合

Why:

- routing policy 应该描述“真实可调用面”，而不仅是概念说明
- 测试需要一个直接可检查的输出面来证明角色已经安装
- launcher、policy script、playbook 与测试都应共享同一份运行时事实来源

### Decision 5: 把更强闭环同步到生成出来的面向操作者资产中

`team-leader.toml` 与 `team-mode-playbook.md` 会更新为明确说明：

- burst-review triad 是生成出来的用户级可调用角色
- triad 保持短突发、leader 侧使用
- 只有经过 judge 保留的幸存项，才允许升级到执行 / 调试 lane

Why:

- 操作者需要准确的解释层
- 这些新角色必须能在本仓库之外也被理解为通用的用户级资产

## Risks / Trade-offs

- [Risk] 更多生成文件会扩大安装面。
  Mitigation: 保持 additive-only，并纳入现有备份与回滚事务。

- [Risk] burst-review 角色可能被误解为持久 pane。
  Mitigation: 在 routing policy、team-leader 与 playbook 中统一标注为 leader 侧 burst roles。

- [Risk] 激励 prompt 可能鼓励“高噪音但低证据”的输出。
  Mitigation: 强制每个 claim / rebuttal 都必须附带具体文件、测试、diff 或运行时证据。

- [Risk] 如果安装失败，routing policy 仍错误声称角色存在。
  Mitigation: 由生成后的 `agents/` 目录文件存在性来推导安装可见性。

## Migration Plan

1. 创建 P4 的 proposal、design、tasks 与 spec artifacts。
2. 扩展安装器，生成 burst-review agent profiles。
3. 扩展共享 runtime、leader profile 与 playbook，加入 burst-role 安装元数据。
4. 扩展 PowerShell 测试，验证生成、策略可见性与回滚。
5. 校验 OpenSpec 与仓库 guard。
6. 重装到真实用户 Codex home，并验证 live user-level agent roster。
