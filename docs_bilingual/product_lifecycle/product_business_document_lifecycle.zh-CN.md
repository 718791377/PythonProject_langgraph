# 产品与商业文档生命周期

本文定义商业、互联网、产品、平台和工具链工作的通用 0-11 / 12 层文档栈。它不绑定具体产品，也不绑定任何单一项目管理来源。它解释每个阶段回答什么问题、需要哪些输入、使用哪些工具与技术，以及输出哪些可交付结果。

本文采用过程组式写法：每个层级都分成“输入”、“工具与技术”、“输出”三类。

- 输入：该层级接收的外部输入、项目外部约束，以及来自其他层级的输入。
- 工具与技术：该层级在分析、判断、设计或交付过程中使用的方法、文件、检查方式和治理技术。
- 输出：该层级最终形成的可交付结果，既可以对外发布，也可以传递给其他层级继续使用。

这些规则是通用治理叠加层。它们不替代白皮书、BRD、MRD、北极星 Plan、PRD、技术设计、implementation plans、OpenSpec 或仓库 checker，而是帮助这些文档按生命周期保持输入、处理和输出一致。

本地源库综合位于 `business_management_source_synthesis.zh-CN.md`。它总结被 Git 忽略的 `Business Management/` 源库逐页和 EPUB spine item 级读取结果，并把来源转译为仓库特定生命周期规则，而不是复制原书正文。

## 来源证据边界

当前生命周期栈指向 `fresh_source_reading_evidence.zh-CN.md`，作为本次 `fresh-source-lifecycle-whitepaper-pmi-refresh-20260614`（`2026-06-14T10:48:53Z`）证据边界；同时指向 `ten_to_twelve_layer_bridge.zh-CN.md`，用于打通研究稿与白皮书的分层关系。原始抽取文本保持在 Git 之外。

## 两种目标架构模式

本生命周期现在明确区分两种运行模式。

| 模式 | 清单规则 | 使用场景 |
| --- | --- | --- |
| Codex CLI 持久化团队平台 | 12 层 + 4 个虚拟部门 + 24 个责任域 + 18 个横切模块 + 48 个核心文档 + 12 个受治理 AI Agent + 12 本推荐书籍 | 变更影响 Codex 编排、原生 subagent 路由、`native_omx`、LangGraph、worktree 安全、OpenSpec 治理、本地 main 优先发布、模板、skill/profile 治理或可复用开发者工具 |
| 一人公司经营系统 | 12 层 + 5 个虚拟部门 + 30 个责任域 + 20 个横切模块 + 60 个核心文档 + 15 个受治理 AI Agent + 15 本推荐书籍 + 12 个最小启动文档 | 工作属于下游业务、产品、offer、客户、收入、运营、财务、风险或学习系统 |

两种模式共享同一套 12 层主干，但不共享权威。Codex 平台可以提供治理机制和模板；下游一人公司拥有自己的客户证据、收入事实、财务证据、产品承诺、法律风险、发布状态、持久化状态与经验教训。

## 面向执行的过程组式规则

任何会驱动工作的层级，都使用 PMI 过程组式写法作为执行语法：

- 输入：来源证据、上游层级输出、约束、风险、审批与当前状态。
- 工具与技术：分析方法、模板、检查器、评审、实验、Agent 角色、门禁与控制技术。
- 输出：已批准文档、决策、证据、发布工件、归档工件，或传递给其他层级的输入。

该规则适用于每一个生命周期层、每一个交付门和每一个发布切片，避免层级变成没有启动条件、控制技术和交付输出的散文。


## 按文档类型选择 PMI 叠加层规则

使用 `pmi_project_management_reference_map.zh-CN.md` 按文档类型选择 PMI 深度。白皮书与北极星计划主要使用 PMI 的价值、裁剪和度量 framing。生命周期层级与实施计划使用 Process Groups 作为执行语法；只有在产生执行工件时才展开 PMBOK 第 6 版 I/T/O 词汇。项目集、项目组合和 PMO 叠加层不是默认 ceremony；只有当多个倡议、共享容量、治理服务或监督需求出现时才进入。

## 价值交付叠加层

文档栈的价值不在于每个文件都存在。只有当它帮助项目识别价值、对齐干系人、交付可用结果、验证结果是否有效，并把学习反馈到下一轮时，文档栈才有价值。

所有层级都应使用以下价值检查：

- Value identification：判断可能存在什么用户价值、商业价值、运营价值、信任价值或学习价值。
- Value alignment：判断 stakeholders 是否同意 purpose、boundaries、success criteria 和 trade-offs。
- Value delivery：判断哪个 increment 会变成可用或可检查结果。
- Value verification：判断什么 evidence 能证明该 increment 有帮助。
- Value learning：判断下一轮应该继续、停止、扩大或废弃什么。

## 轻量项目画布

`project_canvas.md` 是轻量项目画布文件。很小的本地变更可以不写，但需求不确定或涉及跨角色协同时，建议先写项目画布，再展开完整 BRD、MRD、PRD 或 implementation plan。

画布应尽量控制在一页，覆盖：

- purpose 和 value hypothesis；
- target users、operators 或 stakeholders；
- success criteria 和 non-goals；
- scope boundary 和 constraints；
- main risks、assumptions 和 dependencies；
- delivery style：predictive、adaptive 或 hybrid；
- first value increment 和 feedback point；
- validation、rollback 和 learning evidence。

## 治理系统裁剪

裁剪不只是少写文档，而是按风险和不确定性选择合适的治理系统。

完整架构与轻量架构的显式裁剪权威位于 `lifecycle_tailoring_rules.zh-CN.md`。使用它判断完整架构适用于整个项目、只适用于受影响阶段、只适用于有边界模块，还是只适用于某个 release slice。

应一起裁剪以下维度：

- Governance depth：谁审批、谁审查、哪些 gates 必须存在。
- Document depth：短 canvas 是否足够，还是必须显式写 BRD、MRD、PRD、design、test、release、rollback 和 retrospective 文件。
- Role-collaboration depth：一个 maintainer、原生 `subagent` bursts、durable workers 或 graph-shaped orchestration 是否合理。
- Validation depth：需要 local checks、browser verification、CI、red-team review 还是 production smoke evidence。
- Release depth：变更是 local-only、MR-gated、staged rollout，还是 rollback-backed release。
- Learning depth：简短 note 是否足够，还是需要完整 retrospective 和 governance update。

## 快速区别：白皮书 vs 北极星 Plan

| 文档 | 核心问题 | 主要作用 | 典型读者 | 执行角色 |
| --- | --- | --- | --- | --- |
| 白皮书 | 为什么这个方向成立？ | 改变认知，并建立新叙事 | 决策者、合作方、未来维护者 | 它论证方向，但不是任务计划 |
| 北极星 Plan | 如何获胜并衡量进展？ | 把战略变成可量化系统 | 建设者、维护者、操作者 | 它指导阶段规划，但仍高于 implementation tasks |

白皮书论证一个新方向是真实且有价值的。北极星 Plan 定义长期目标、核心指标、输入指标、杠杆和分阶段靠近目标的路径。

## 生命周期通用裁剪规则

不同项目不需要一次性写满所有文档。应按风险、不确定性、影响范围和交付方式选择最小充分文档集。

- 预测式门禁适合需求清晰、风险较高、需要显式 release evidence 或 rollback evidence 的工作。
- 适应式切片适合需求不清楚、需要用户反馈、需要 spike、MVP 或小型实验的工作。
- 混合式方式适合仍要探索，但最终交付必须经过评审、测试、发布和复盘门禁的工作。

当工作触达金钱、外部用户、客户承诺、信任、合规、安全、隐私、数据 ownership、durable state、runtime entrypoints、跨项目模板、共享接口、release gates、rollback safety 或长期平台行为时，应对受影响范围采用完整架构。

只有早期想法、私有 spike、本地学习练习或小型内部工具，且没有外部用户、金钱或信任边界、敏感数据、共享 runtime entrypoint，并且结果可逆或可丢弃时，才允许整个项目轻量。

当项目整体需要更强治理，但某个阶段或模块边界清晰、低风险、可逆，并有明确升级触发条件时，可以采用阶段局部轻量或模块级轻量。如果风险、耦合、采用、支持、合规或回滚影响扩大，应先扩展受影响层级或模块；只有耦合变成系统性时，才扩展整个项目。

## 0. 认知叙事层

核心问题：这件事为什么存在？

### 输入

- 行业趋势、技术趋势、政策环境、用户行为变化或组织战略变化。
- 现有方案缺口、重复失败案例、长期摩擦和结构性痛点。
- 商业层、市场层或技术层发现的反复问题；这些下游反馈可反向触发新的认知叙事。

### 工具与技术

- 趋势分析：把外部变化整理成未来几年可能发生的方向。
- 问题建模：把表面需求还原成结构性矛盾、约束和机会。
- 叙事推演：说明为什么现有方案不足，以及新范式为什么可能成立。
- `whitepaper.md` 是白皮书文件；它解释行业趋势、结构性痛点、现有方案为什么不够，以及新范式是什么。

### 输出

- 白皮书或认知说明，用于说明方向为什么值得理解和讨论。
- 新范式定义、核心假设、证据链和非目标边界。
- 向商业层输出“是否值得进一步评估”的方向候选。

## 1. 商业层

核心问题：这件事值不值得做？

### 输入

- 认知叙事层输出的方向候选、问题定义和核心假设。
- 组织目标、预算边界、资源约束、合规约束和经营优先级。
- 市场层提供的用户规模、竞品证据和付费意愿信号。

### 工具与技术

- 商业模式分析：判断价值如何转化为收入、成本节省、效率提升或风险降低。
- 收益与成本估算：比较开发、运行、模型、维护、合规、获客和迁移成本。
- 市场规模估算：TAM 是总市场，SAM 是可服务市场，SOM 是可触达市场。
- 单位经济模型：CAC 是获客成本，LTV 是用户生命周期价值，ROI 是投入产出比。
- `brd.md` 是商业需求文档；它解释商业目标、收入逻辑、成本结构和投入产出。

### 输出

- BRD、商业假设、投资边界和成功标准。
- 做、不做、推迟，或继续研究后再决定的商业决策。
- 向市场层输出目标人群和价值假设，向战略层输出商业目标和约束。

## 2. 市场层

核心问题：用户到底需要什么？

### 输入

- 商业层输出的目标人群、价值假设和商业约束。
- 外部用户访谈、问卷、竞品观察、渠道反馈、客服反馈和使用数据。
- 认知叙事层提出的问题框架，以及产品层或增长层回传的真实使用摩擦。

### 工具与技术

- 用户分层：识别目标用户、影响者、付费者和操作者。
- 场景分析：描述用户什么时候、为什么、在什么约束下需要方案。
- 痛点分析：把功能请求背后的真实问题提炼出来。
- 竞品分析：比较替代方案、差异化机会和进入门槛。
- 反馈循环：用小样本验证、原型反馈或 MVP 反馈降低不确定性。
- `mrd.md` 是市场需求文档；它把市场证据和用户需求转化为产品方向。

### 输出

- MRD、目标用户、目标场景、市场切入位置和竞品差异化判断。
- 用户问题清单、优先级信号和进入策略。
- 向战略层输出市场机会，向产品层输出用户场景和需求证据。

## 3. 战略层

核心问题：我们如何获胜，以及明确不做什么？

### 输入

- 认知层输出的新范式和长期假设。
- 商业层输出的商业目标、成本边界和成功标准。
- 市场层输出的用户场景、需求证据、竞品差异和进入策略。
- 技术层反馈的能力边界、风险约束和可行性。

### 工具与技术

- 战略内核分析：在扩展 roadmap 前记录 diagnosis、guiding policy 和 coherent action。
- 滩头和定位分析：选择先在哪个细分场景获胜，以及相对哪些替代方案建立心智框架。
- 产品战略分析：决定哪些 offer、workflow 或 capability 进入范围，哪些必须拒绝。
- Critical path 分析：识别最限制下一阶段进展的约束。
- 阶段裁剪：根据风险和不确定性选择 predictive、adaptive 或 hybrid delivery。
- `strategy.md` 是战略文件；它记录诊断、指导方针、连贯行动、取舍和明确非目标。
- `product_strategy.md` 是产品战略文件；它把战略选择转成产品或 offer 方向。

### 输出

- 战略、指导方针、连贯行动集合、取舍和非目标边界。
- 输出给指标、产品、组织、执行和增长层的战略优先级。
- 聚焦、暂停、转向或继续发现的决策。

## 4. 指标层

核心问题：什么证据能说明战略有效？

### 输入

- 战略层输出的战略、取舍和目标结果。
- 商业层输出的商业目标、成本限制和价值假设。
- 市场、用户、产品、技术、增长、运营和复盘信号。
- 技术层给出的数据可用性、数据质量、隐私和埋点约束。

### 工具与技术

- 北极星指标设计：选择最能代表长期用户或操作员价值的指标。
- 输入指标拆解：识别驱动北极星指标的领先指标。
- OKR 设计：把战略转化为聚焦、对齐、跟踪和复盘节奏。
- OMTM 分析：选择当前阶段最重要的 One Metric That Matters。
- 护栏指标设计：保护质量、成本、信任、安全、可靠性和 operator attention。
- Tracking plan 和数据字典设计：定义事件、维度、owner 和指标口径。
- `metrics.yaml` 是机器可读指标契约；它定义北极星、输入、护栏和阶段指标。
- `tracking_plan.md` 是埋点计划；它定义事件、来源、owner 和质量检查。
- `data_dictionary.md` 是数据字典；它定义指标术语和数据 ownership。

### 输出

- 指标契约、OKR、OMTM、护栏指标、阈值和复盘节奏。
- 输出给产品、技术、执行、增长、运营和复盘工作的证据要求。
- continue、stop、expand、pivot、refactor 或 retire 的决策阈值。

## 5. 产品层

核心问题：产品应该是什么？

### 输入

- 战略层输出的优先级、取舍和非目标。
- 指标层输出的指标、阈值和证据要求。
- 市场层输出的用户分层、场景、痛点和需求证据。
- 技术层输出的可行性边界、接口约束、安全约束和成本约束。
- 增长层、运营层或复盘层回传的采用摩擦、反馈总结和实验结果。

### 工具与技术

- 用户流程设计：把用户目标拆成入口、动作、反馈和完成路径。
- 信息架构：组织内容、页面、对象和动作。
- PR/FAQ 和叙事规划：先描述客户倒推 outcome，再写实现细节。
- Opportunity mapping 和 product kata：连接用户问题、假设、实验和成功指标。
- 原型验证：用低保真或高保真原型测试交互和布局清晰度。
- 优先级排序：按价值、风险、成本和依赖把工作排成 P0、P1、P2。
- 验收标准设计：把功能需要转成可测试、可评审结果。
- `prd.md` 是产品需求文档；它把战略转成用户可见功能、流程、优先级和验收标准。
- `offer.md` 是 offer 文档；它定义卖什么或交付什么，以及承诺边界。
- `user_journey.md` 是用户旅程；它描述用户在使用前、使用中、使用后的完整体验。
- `information_architecture.md` 是信息架构文件；它说明内容、页面和动作如何组织。
- `prototype.fig` 或其他原型文件是设计原型；它展示预期交互和布局。

### 输出

- PRD、offer 定义、用户旅程、信息架构、原型和验收标准。
- 产品范围、非范围，以及移动到后续阶段的需求。
- 输出给技术层的系统需求来源；输出给执行层的功能范围和验收证据。

## 6. 技术层

核心问题：如何安全实现？

### 输入

- 产品层输出的 PRD、用户流程、验收标准和范围边界。
- 战略、指标、长期演进方向和非目标边界。
- 组织层输出的 owner 边界和审批约束。
- 外部技术约束，包括安全、隐私、性能、成本、兼容性、部署环境和供应链限制。
- 执行层、运营层或复盘层回传的缺陷、性能瓶颈、运维摩擦和技术债。

### 工具与技术

- 架构设计：拆解模块、接口、数据流、状态边界和信任边界。
- 依赖和组件边界设计：保护长期可变更性，防止意外耦合。
- 数据系统设计：检查可靠性、可扩展性、可维护性、一致性和派生数据责任。
- Secure-by-design 分析：把领域不变量、输入约束和失败模式转成默认安全行为。
- 风险分析：识别安全、隐私、可用性、成本、可维护性和迁移风险。
- 质量门禁：定义测试、评审、回滚、可观测性和兼容性要求。
- Build-or-buy 判断：决定构建、复用、购买、集成或推迟。
- `srs.md` 是系统需求规格；它定义系统级功能和非功能需求。
- `trd.md` 是技术需求或技术设计文档；它解释技术方案和取舍。
- `hld.md` 是高层设计；它定义主要模块、信任边界、数据流和集成点。
- `lld.md` 是低层设计；它定义具体组件、脚本、函数、schema 和边界情况。
- `api_spec.md` 是 API 规格；它定义输入、输出、权限、错误和兼容性。
- `data_model.md` 是数据模型；它定义实体、字段、关系和持久化规则。

### 输出

- SRS、TRD、HLD、LLD、API 规格、数据模型和风险控制说明。
- 证明系统可构建、可测试、可运行、可评审、可回滚的技术证据。
- 输出给组织层和执行层的实现边界、依赖、测试要求和发布风险。

## 7. 组织层

核心问题：谁或什么拥有每个责任、决策和审批？

### 输入

- 战略、指标、产品范围、技术边界和运营约束。
- 人类产能、Agent 能力、供应商或外部支持、权限边界和审批要求。
- 来自运营层的认知负载、team/agent 交互模式和支持预期。

### 工具与技术

- Role-map 设计：区分 founder、owner、reviewer、operator、agent、vendor 和 customer-success 职责。
- Agent 治理设计：定义 AI Agent 可以 read、write、propose、review、test、deploy 或必须人工审批的范围。
- RACI 式责任映射：定义关键决策谁负责、谁问责、咨询谁、通知谁。
- Team API 和 cognitive-load 分析：定义协作边界、handoff 预期和平台责任。
- Escalation 和 approval 设计：定义哪些决策需要人工确认。
- `role-map.md` 是角色地图；它定义人、Agent、供应商和 reviewer 的责任。
- `agent-governance.md` 是 Agent 治理文件；它定义 Agent 权限、审批门和回滚边界。
- `responsibility_matrix.md` 是责任矩阵；它映射决策、owner、reviewer 和升级规则。
- `operating_model.md` 是运营模型；它定义节奏、ownership、沟通和复盘循环。

### 输出

- 角色地图、Agent 治理、责任矩阵、运营模型和审批边界。
- 输出给执行、运营和复盘工作的 ownership 与 capacity 约束。
- 明确决策权，避免自动化变成隐藏权威。

## 8. 执行层

核心问题：如何交付？

### 输入

- 产品层输出的范围、优先级、验收标准和非目标边界。
- 技术层输出的设计、接口、依赖、风险控制和测试要求。
- 指标层输出的阈值、发布节奏和成功标准。
- 组织层输出的 ownership、approval、capacity 和 Agent 治理约束。
- 外部输入，包括时间窗口、发布限制、审批限制和运营窗口。

### 工具与技术

- 工作拆解：把范围拆成可验证、可回滚、可评审的小切片。
- Shaping：在团队或 Agent 大规模执行前定义 appetite、边界、rabbit holes 和 circuit breaker。
- Plan freeze：锁定关键设计、任务列表、验收标准和风险边界。
- 变更控制：用 OpenSpec、code review、CI、测试和 release gates 控制范围漂移。
- Monitoring and controlling：跟踪进度、风险、缺陷、依赖和验收状态。
- `implementation_plan.md` 是实施方案；它把已选阶段拆成可执行工作。
- `tasks.md` 是任务清单；它跟踪具体步骤和完成状态。
- `test_plan.md` 是测试计划；它定义 unit、integration、end-to-end、manual 和 regression 检查。
- `release_plan.md` 是发布计划；它定义 rollout 时间、release gates 和沟通。
- `rollback_plan.md` 是回滚计划；它定义如何回到安全的上一状态。

### 输出

- 可执行任务、测试计划、发布计划、回滚计划和交付证据。
- 已实现、已验证、已发布或可发布的工作结果。
- 输出给增长层和运营层的可采用能力；输出给复盘层的交付记录、问题记录和学习素材。

## 9. 增长层

核心问题：如何触达、激活、留存并变现正确受众？

### 输入

- 执行层输出的已发布或可发布能力、已知限制和采用入口。
- 战略、指标、输入指标、增长杠杆和护栏指标。
- 用户分层、定位、渠道信号和市场证据。
- 运营反馈、支持摩擦、信任信号和客户成功发现。

### 工具与技术

- 路线图规划：按用户价值、商业价值、技术依赖和风险排序后续版本。
- 增长实验：小批量测试 acquisition、activation、retention、revenue 或 adoption 机制。
- Traction channel testing：用明确 traction goal 和 critical path 比较候选渠道。
- 定位和 whole-product review：确保用户理解类别、替代方案、价值、onboarding、支持和信任故事。
- 指标系统：定义 DAU、MAU、retention、conversion、CAC、LTV、quality 或 adoption metrics。
- Adoption analysis：记录系统在哪里被使用、为什么被使用、还剩什么摩擦。
- `roadmap.md` 是产品路线图；它定义后续版本和优先级。
- `growth_plan.md` 是增长计划；它定义 acquisition、activation、retention、revenue 或 adoption 机制。
- `channel_tests.md` 记录渠道假设、测试和结果。
- `adoption_report.md` 是采用报告；它记录系统在哪里被使用和还剩什么摩擦。

### 输出

- Roadmap、增长计划、渠道测试、采用报告和后续版本候选。
- 系统扩展、被采用、改进或商业化的路径。
- 向指标层和战略层反馈指标进展；向产品层反馈需求变化；向运营层和复盘层输出采用证据。

## 10. 运营层

核心问题：系统发布后如何持续服务用户？

### 输入

- 执行层输出的已发布能力、changelog、回滚证据和已知限制。
- 增长层输出的采用、渠道和用户摩擦证据。
- 组织层输出的 ownership、升级、支持和 Agent 治理边界。
- 质量、可靠性、成本、安全、支持和客户成功信号。

### 工具与技术

- Support playbook 设计：定义响应路径、问题分类、服务边界和升级规则。
- Customer success 分析：跟踪 onboarding、activation、renewal、support outcome 和 trust recovery。
- Bug triage 设计：分类缺陷、事故、回归、功能请求和用户教育缺口。
- FAQ 和文档运营：把重复问题转成可维护知识资产。
- Operating cadence review：让周、月、季或 release 复盘保持轻量且基于证据。
- `ops-playbook.md` 是运营手册；它定义支持、问题处理、节奏和升级。
- `support-playbook.md` 是支持手册；它定义支持类别、响应规则和 handoff 路径。
- `faq.md` 是 FAQ；它把重复问题转成维护答案。
- `customer-success.md` 记录客户成功或 operator success 实践。
- `issue_log.md` 记录 active blockers、incidents 和 support issues。

### 输出

- 运营手册、支持记录、FAQ 更新、客户成功笔记和 issue-log 证据。
- 输出给产品、技术、增长和复盘层的支持、可靠性、信任和可用性反馈。
- 证明已发布工作仍可用、可支持、可恢复的运营证据。

## 11. 复盘层

核心问题：是否有效、发生了什么变化、什么应该沉淀复利？

### 输入

- 执行层输出的交付记录、测试结果、发布结果、缺陷记录和事故记录。
- 增长层和运营层输出的指标结果、采用报告、实验结果、支持证据和用户反馈。
- 市场、产品、技术、组织、执行和运营层回传的重复问题、未满足需求和技术债。
- 外部输入，包括客户反馈、审计发现、合规变化和运营事件。

### 工具与技术

- 复盘分析：识别发生了什么、为什么发生、影响范围、修复动作和预防动作。
- 实验分析：比较变体结果，决定继续、停止或扩大。
- 学习捕获：把事故、交付和反馈转成可复用规则、模板、checklist 或 follow-up task。
- Operating-system refinement：只有能降低未来摩擦时，才把重复工作转成 SOP、模板、指标、ownership rule 或自动化。
- Closing gates：确认 deliverables、documentation、release state、rollback evidence 和 lessons learned 已归档。
- `post_mortem.md` 是事故或项目复盘；它记录发生了什么、为什么发生、影响、修复和预防。
- `monthly-review.md` 是月度复盘；它汇总战略、指标、运营和学习决策。
- `ab_test_report.md` 是 A/B 测试报告；它比较变体并解释哪个更好。
- `feedback_summary.md` 是用户反馈总结；它捕获重复用户反应和请求。
- `lessons_learned.md` 是经验教训文档；它把经验转成可复用规则或未来任务。

### 输出

- 复盘报告、月度复盘、实验报告、反馈总结、经验教训和治理更新建议。
- 对下一周期继续、停止、扩大、重构、自动化、委派或退役的清晰判断。
- 向认知、商业、市场、战略、指标、产品、技术、组织、执行、增长和运营层反馈可复用经验。

## 按项目规模选择最小文件集

小型内部工具通常需要简短战略或北极星说明、指标说明、PRD、技术设计、owner 或角色说明、implementation plan、test plan、运营说明和 retrospective。implementation plan 是实施方案，用来把已选阶段拆成可执行工作；test plan 是测试计划，用来定义验证方式；retrospective 是复盘记录，用来沉淀经验。公共产品、商业产品或长期平台应该补齐白皮书、BRD、MRD、roadmap、metrics 和 release governance。roadmap 是路线图，用来安排后续版本；metrics 是指标文档，用来定义衡量方式；release governance 是发布治理，用来定义上线门禁和回滚要求。

对 Codex CLI durable-team 平台，`docs_bilingual/north_star_plan.zh-CN.md` 是仓库级北极星 Plan。它定义主成功指标、输入指标、护栏指标、分阶段决策阈值，以及 12 层平台/下游清单对照。

对下游一人公司操作系统，轻量起步底线是 `one_person_company_inventory_map.zh-CN.md` 定义的 12 个最小启动文档：`company-thesis.md`、`business-model.md`、`offer.md`、`pricing.md`、`user-segments.md`、`growth-model.md`、`finance-model.md`、`ops-playbook.md`、`metrics.yaml`、`risk-register.md`、`agent-governance.md`、`monthly-review.md`。只有当客户证据、收入暴露、交付复杂度、治理风险或长期运营成本证明需要更深覆盖时，下游项目才应扩展到 60 文档系统。

项目越影响金钱、用户、信任、合规或长期平台行为，这套文档栈就越应该显式化。轻量模式只有在低风险早期工作中才能覆盖整个项目；其他情况应让高风险阶段或模块保持完整架构路径，只对边界清晰的低风险切片轻量化。
