## 1. 控制资产

- [x] 1.1 扩展用户级 team-mode installer / generator 清单，在不触碰原生 `codex` 入口的前提下加入 native-subagent 上限控制资产
- [x] 1.2 实现或补齐 native-subagent limit surface，使其能够查看，并在受支持时管理，`agents.max_threads` 与 `agents.max_depth`
- [x] 1.3 增加可验证的安全覆盖，确保该上限控制面保持 additive，且不会替换或修改原生 `codex`、`codex.cmd`、`codex.ps1`

## 2. 路由与生成指南

- [x] 2.1 扩展共享 routing-policy model，明确自动专家角色路由是 leader 侧 overlay，建立在原生 Codex subagent 的显式触发之上
- [x] 2.2 为 routing-policy 输出和生成指南增加“读多型优先 fan-out / 写多型并行受门控”规则
- [x] 2.3 更新生成出来的 `team-leader` 与 playbook 资产，明确区分原生 Codex subagent、durable `omx team`、`OpenHands` 与通用编排运行时

## 3. Agent TOML 边界

- [x] 3.1 把用户级与仓库级 agent TOML 放置规则补入生成指南和 operator-facing 文档
- [x] 3.2 增加最小 standalone custom-agent TOML 字段的校验或显式文档化：`name`、`description`、`developer_instructions`
- [x] 3.3 验证 wrapped 启动面仍然把 `oh_my_codex=off` 且 routing 开启描述为 wrapped native-routed mode，而不是裸未包装模式

## 4. 验证与同步

- [x] 4.1 验证资产可生成到 repo-local 目标 Codex home，并确认新的上限控制资产存在且可检查
- [x] 4.2 验证三种启动结果：enhanced mode、wrapped native-routed mode、plain single-agent mode
- [x] 4.3 验证写多型并行指南在批准前必须要求显式 ownership 隔离
- [x] 4.4 如果实现改变了相关措辞或 operator surface，则把最终结果同步回受影响的双语实施方案或 operator-facing 文档
- [x] 4.5 运行 `openspec validate --all`，并确认该 change 已达到 apply-ready 状态
