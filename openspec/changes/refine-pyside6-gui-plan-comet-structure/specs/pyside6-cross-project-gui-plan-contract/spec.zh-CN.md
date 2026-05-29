## 新增需求

### 需求：PySide6 GUI 方案使用完整 Comet 可执行结构

PySide6 跨项目 GUI 能力方案必须使用完整 Comet 可执行方案结构，并区分共享 runtime readiness、消费项目 GUI readiness、高影响显式触发门、本地集成和远端发布授权。

#### 场景：方案结构达到 implementation-slicing ready

- **GIVEN** 实施者打开 `docs_bilingual/implementation_plans/pyside6_cross_project_gui_capability_plan.md`
- **WHEN** 他们在 runtime 或消费项目工作前复核方案
- **THEN** 方案暴露关系模型、目标/非目标、工作边界、运行时架构、source of truth、helper contract、状态模型、readiness gate、实施事项、验证路径、回滚规则、风险和自检
- **AND** 在没有目标项目证据时，不声称任何消费项目已经 GUI-ready。

#### 场景：runtime 能力不被夸大

- **GIVEN** 共享 runtime 可以在本机 import PySide6
- **WHEN** 没有具名消费项目通过 preview 和 import-only smoke
- **THEN** 方案让该消费项目保持在 `project_gui_verified_with_shared_runtime` 以下状态
- **AND** 可见 GUI 和打包状态保持 false，除非显式触发并有证据。

#### 场景：高影响动作保持显式

- **GIVEN** 用户只说“继续”或泛化要求继续本方案
- **WHEN** 下一步可能是 project-local override、可见 GUI 验证或可执行文件打包
- **THEN** 方案要求具名目标项目和明确理由后才继续。

#### 场景：Comet 脚本证据保持诚实

- **GIVEN** 当前 Windows shell 不能运行 Comet `.sh` 脚本
- **WHEN** change 记录 Comet state
- **THEN** state 记录脚本 blocker，并使用 OpenSpec/repository gate 作为替代证据
- **AND** 不声称 `comet-state.sh` 或 `comet-guard.sh` 已通过。
