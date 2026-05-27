# 设计：协同证据守卫

该 checker 有意保持 repo-local 与 fixture-driven。Repository mode 校验政策表面、安全注册表、guard wiring 与必需 fixture set。Evidence mode 校验单个结构化 JSON case，供后续 run summary 或保存后的 activation artifact 使用。

设计上将五类 evidence contract 放在一起，是因为它们共享同一种失败模式：最终汇报可能从提示词、计划、readiness、陈旧 state 或部分生命周期证据中夸大协同运行事实。该 checker 不替代既有专项 checker；它为 Phase 4 实施方案增加一个验收层。

本变更不会启动 runtime team。durable / persistent team 执行仍然受阈值约束；在接受 selected / running / complete 声明前，仍必须提供 active selector、manifest 或 LangGraph thread state、heartbeat、close 与 leader absorption evidence。
