---
doc_id: user_level_launcher_payload_policy
lang: zh-CN
doc_class: governance
status: active
---

# 用户级启动器 Payload 策略

## 1. 目的

本文定义用户级 Codex 或 OMX 启动器如何避免 Windows 命令行长度超限，同时保持稳定的启动契约。

## 2. 问题定义

这类故障的典型链路很直接：

- 用户级 launcher 生成了较大的运行时指令 payload
- 该 payload 被内联放进命令行参数
- Windows 命令行长度上限被击穿
- Codex 还没真正启动，launcher 就先失败了

对本仓库来说，这次的具体故障就是 `codex-ohmy` 把很长的 `-c developer_instructions=...` 直接塞进启动参数。

## 3. 硬规则

- 用户级 launcher 不得再把大体积生成指令通过 `-c developer_instructions=...` 内联传递。
- 用户级 launcher 不得把大 JSON、完整策略对象、展开后的路径清单或完整运行时状态直接塞进命令行参数。
- 用户级 launcher 的启动参数必须保持短小且有上界。
- 只要启动时确实需要长指令，就必须改走短文件引用，例如 `model_instructions_file`，而不是直接传整段正文。
- 用户级 launcher state 文件可以承载共享启动 payload 工件，但不得替代任何仓库自己的 repo-local canonical durable state。
- `C:\Users\lenovo\.codex\bin\` 下生成出来的 installed wrapper 只是安装产物，不是 payload 策略修复的源码真相面。
- 运行时 payload 组装应放在共享 launcher / support-script 层，不得分散到每个 generated wrapper 各自处理。
- installer 可以负责把修复后的 launcher 行为发布出去，但不应成为运行时 payload 语义散落的地方。
- 不应把“删字”“缩文案”当成长期主解法；必须修 transport path 本身。

## 4. 必须采用的传输模式

推荐采用下面这套分层传输：

1. 命令行层：
   只放短控制参数
2. 文件 / 状态层：
   放大体积指令正文与结构化 payload
3. support-script 层：
   负责生成 payload、写文件、再拼出短引用

对启动指令来说，具体要求是：

- 把生成后的长指令写入 `C:\Users\lenovo\.codex\state\` 下的受控文件
- 启动时只传短配置键，例如 `model_instructions_file="<path>"`

## 5. 分层归属

- launcher 层：
  只负责短启动调用
- support-script 层：
  负责生成长指令并写入文件
- installer 层：
  负责把 launcher 和 support-script 正确发布出去
- installed wrapper 层：
  只是验证面，不是架构真相面
- repository 层：
  继续负责 repo-local source、repo-local durable state，以及 launcher 可能引用到的仓库级运行时真相

## 6. 推荐规则

- 优先传“引用”，不要传“正文”。
- 优先传 `thread_id`、`repo_root`、`view`、文件路径，而不是传完整展开后的状态正文。
- 能从磁盘重建的运行时状态，就在运行时重新读取，不要在 launcher 链路里重复转发。
- payload 生成逻辑必须集中在共享 support logic 中。
- 只要 startup argument 行为变动，就必须补一条长 payload 场景回归测试。

## 7. 反模式

- 继续追加新的 inline `-c key=value` payload 去掩盖旧 launcher 问题
- 明明可以传文件路径，却还把大策略文本塞进环境变量或参数
- 直接手改 `C:\Users\lenovo\.codex\bin\codex-ohmy.ps1` 之类的 installed wrapper 作为主修复路径
- 在多个 generated wrapper 里重复实现各自的临时文件逻辑
- 把一次性删文案当成稳定架构方案

## 8. 验证规则

任何 launcher payload 变更都必须验证下面四项：

1. `codex-ohmy --version` 在 Windows 上正常
2. `codex-ohmy exec --help` 在 Windows 上正常
3. 一个定时的无参 `codex-ohmy` 启动能跨过启动边界，而不是立刻报“命令行太长”
4. 仓库回归测试已经覆盖 file-backed startup instructions 路径

## 9. 当前仓库规则

对本仓库而言，当前必须执行的预防规则是：

- 不再把生成后的用户级编排指令以内联 `developer_instructions` 方式传递
- 把它写入用户级 state 目录下的 `user-level-team-mode-model-instructions.md`
- 启动时只传短的 `model_instructions_file` 引用


## 10. 旧会话 Resume 启动兼容

旧会话 `/resume` 的继续使用不能迫使全局重写 launcher，也不能迫使移除 Codex 直连 MCP。

规则：

- 路径稳定时，先正常启动 `codex-ohmy`，再从临时会话进入 `/resume`。`codex-ohmy` 是日常 Codex 编排工作的稳定包装入口。
- 如果某个旧 thread 需要临时启动 workaround（绕过方案），使用 scoped one-launch override（单次启动覆盖），不要直接编辑 installed wrapper 文件。
- 不要把手工编辑 `C:\Users\lenovo\.codex\bin\codex-ohmy.ps1` 当成主要修复方式。该文件是已安装 wrapper 产物，不是 launcher 行为的源码真相。
- 长期修复必须保留在仓库拥有的源码或 installer generation logic 中，并在发布前有 checker 覆盖。
