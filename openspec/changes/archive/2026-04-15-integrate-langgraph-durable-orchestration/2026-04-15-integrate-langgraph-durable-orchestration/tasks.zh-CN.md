## 1. 变更合同

- [x] 1.1 定义 LangGraph 持久化编排接入的 proposal、design 和 spec 范围
- [x] 1.2 定义 LangGraph 如何接在 Codex / oh-my-codex 之下，而不是替换当前 durable 路径

## 2. 控制面

- [x] 2.1 在生成出来的用户级 controls 中加入 durable orchestration backend selector
- [x] 2.2 定义 `.omx/state/langgraph/` 下的 repo-local LangGraph 运行态布局
- [x] 2.3 定义第一版 operator 可见的 LangGraph 状态检查表面

## 3. 图合同

- [x] 3.1 定义七阶段 root graph 合同
- [x] 3.2 定义 research、planning、execution、verification 和 adversarial review 的 subgraph 合同
- [x] 3.3 定义 repo-local `thread_id` 合同与 checkpoint persistence 模型

## 4. 持久化工作对象

- [x] 4.1 定义研究到实现交接所使用的冻结 implementation-brief schema
- [x] 4.2 定义 debugger lane 消费的 adversarial-review survivor-queue schema
- [x] 4.3 定义 plan freeze、高风险 stabilize 和 final verification failure 的 interrupt / resume 点

## 5. 入口与路由

- [x] 5.1 定义 additive 的 LangGraph run/status/resume/inspect 入口
- [x] 5.2 扩展 automatic durable routing，使其尊重 durable orchestration backend selector
- [x] 5.3 更新 playbook 合同，让 operator 能区分 direct `omx team` 执行和 LangGraph-backed durable orchestration

## 6. 验证

- [x] 6.1 定义 repo-local thread persistence 与 resume 的验证
- [x] 6.2 定义 interrupt -> approval -> resume 的验证
- [x] 6.3 定义 research brief persistence 与 fresh execution restart 的验证
- [x] 6.4 定义 adversarial-review survivor 如何进入 debugger lane 的验证
- [x] 6.5 运行 `openspec validate --all`，并确认该 change 已达到 apply-ready 状态
