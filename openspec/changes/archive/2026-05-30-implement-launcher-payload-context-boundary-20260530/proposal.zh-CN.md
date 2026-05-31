## 原因

用户级 Codex 包装启动器已经会生成较丰富的自动编排启动指令。如果把这段正文以内联 `developer_instructions` 命令行覆盖项传递，就可能触发 Windows 命令行长度限制，也可能把编码敏感文本带过错误的传输边界。

## 变更内容

- 新增仓库 checker，证明生成的启动器启动指令会写入 UTF-8 状态文件，并且只通过一个较短的 `model_instructions_file` 覆盖项传递。
- 将该 checker 注册到聚合 OpenSpec guard 和脚本背书安全规则登记表中。
- 增加针对当前仓库以及失败场景的回归覆盖：移除文件引用、内联 developer instructions、移除 UTF-8 写入、绕过启动参数构造器。
- 将文件化启动器指令传输要求提升到 startup-binding spec。

## 能力范围

### 新增能力

- 无。

### 修改能力

- `codex-user-level-team-mode-startup-binding`：启动器 payload 传输现在要求使用文件化 model-instructions 引用，而不是内联生成的指令正文。

## 影响

- 影响范围：launcher payload checker、聚合 guard 注册、安全规则登记表、定向测试以及 startup-binding OpenSpec spec。
- 明确非目标：不修改用户级配置、不手改已安装 wrapper、不进行远程发布、不启动持久团队。
- 推进顺序：添加 checker 和测试，验证现有 installer 行为，在同一个本地包内归档该 OpenSpec change，运行本地 gate，提交，然后仅合入本地 `main`。
- 回滚计划：回滚本地 feature commit，以移除 checker、测试、guard 注册、安全规则项和 spec 提升。
- 验证路径：运行聚焦编译、测试、checker 命令，OpenSpec 校验，仓库 guard，precommit update/archive review，local gate 和 local MR review。