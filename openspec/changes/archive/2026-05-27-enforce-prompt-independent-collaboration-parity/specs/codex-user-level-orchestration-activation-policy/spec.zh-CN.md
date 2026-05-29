## 新增需求

### 需求：提示词无关协同等价性必须由 checker 支撑

仓库必须提供 `tools/check_orchestration_collaboration_evidenceguard.py` 与提示词 fixture pairs，用于证明等价任务在包含或不包含协同短语时会产生等价 routing decision。

该 checker 还必须校验冷启动读取顺序证据、durable / persistent evidenceguard 记录、结构化 expert 生命周期审计事件，以及 LangGraph state release evidence。

#### 场景：校验提示词无关 fixture pairs

- **当** evidenceguard 校验提示词无关协同 fixture 时
- **则** 对于相同 task shape，包含与不包含协同短语的 paired cases 必须产生相同 route fields
- **并且** routing reasons 中不得出现“用户未提醒协同”等理由

#### 场景：durable evidenceguard 拒绝夸大声明

- **当** 保存后的 durable 或 persistent team 声明被检查时
- **则** selected、running 或 complete 声明必须在缺少对应状态所需 evidence 时失败
- **并且** 裸 plan、skill invocation、timeout、branch name 或 `.omx` 目录存在不得算作 runtime team evidence

#### 场景：校验 LangGraph release evidence

- **当** 已完成的 LangGraph 任务被检查时
- **则** 陈旧 `running` 状态必须失败，除非已记录 completion 或 handoff release 字段
