# codex-user-level-team-mode-native-subagent-boundaries Specification

## Purpose

Define the reusable native Codex subagent contract for the user-level Codex / oh-my-codex workflow, including explicit leader-side spawning semantics, custom-agent placement rules, bounded fan-out, write-heavy parallelism gating, and OMX terminology boundaries.

## Requirements

### Requirement: Native Codex subagents SHALL remain an explicit leader-orchestrated capability

The reusable user-level team-mode workflow SHALL describe native Codex subagents as an official native capability that is explicitly spawned by the leader lane and returned through leader-owned fan-in.

Generated routing policy, leader profile, and operator guidance SHALL NOT describe raw Codex as automatically spawning specialist roles by default.

#### Scenario: Operator inspects native-routed guidance

- **WHEN** the operator inspects generated guidance for wrapped native-routed startup
- **THEN** it SHALL describe expert roles as native Codex subagents selected by the leader lane
- **AND** it SHALL distinguish that behavior from both durable `omx team` workers and raw unwrapped Codex defaults

### Requirement: Custom native-subagent TOMLs SHALL use layered locations and a minimum standalone schema

The workflow SHALL preserve two layered custom-agent locations:

- user-level reusable roles under the Codex home agent directory
- repository-specific roles under `<repo>/.codex/agents/`

Every standalone custom-agent TOML used by this workflow SHALL define at least:

- `name`
- `description`
- `developer_instructions`

#### Scenario: Maintainer checks role placement rules

- **WHEN** a maintainer reads the generated guidance for reusable and repository-scoped roles
- **THEN** it SHALL distinguish user-level reusable agent TOMLs from repository-scoped agent TOMLs
- **AND** it SHALL state the minimum standalone custom-agent fields

### Requirement: Native-subagent fan-out SHALL remain bounded and inspectable

The workflow SHALL keep native-subagent fan-out bounded through explicit, operator-visible controls for `agents.max_threads` and `agents.max_depth`.

Generated controls or guidance SHALL explain that increasing these values raises token usage, latency, and local resource pressure.

#### Scenario: Operator inspects managed fan-out limits

- **WHEN** the operator inspects the generated native-subagent limit surface
- **THEN** it SHALL expose `agents.max_threads` and `agents.max_depth`
- **AND** it SHALL describe the cost and latency effect of broader or deeper fan-out

### Requirement: Native-subagent parallel execution SHALL distinguish read-heavy from write-heavy work

The routing policy SHALL prefer native-subagent parallelism for read-heavy or otherwise tightly bounded work.

The workflow SHALL treat write-heavy multi-agent execution as invalid unless all of the following are explicit:

- ownership isolation by file slice or worktree
- hotspot serialization rules
- leader-owned final integration

#### Scenario: Planner sees a read-heavy bounded task

- **WHEN** the task is primarily exploratory, analytical, or otherwise read-heavy
- **THEN** the routing policy SHALL allow bounded native-subagent fan-out

#### Scenario: Planner sees a write-heavy task without isolated ownership

- **WHEN** the task requires multiple writers but ownership isolation or hotspot serialization is missing
- **THEN** the workflow SHALL classify the task as not ready for write-heavy parallel execution
- **AND** it SHALL require ownership isolation before multi-writer execution proceeds

### Requirement: OMX terminology SHALL remain layered over Codex rather than replacing it

Generated leader, playbook, and operator-facing assets SHALL describe oh-my-codex as a workflow and durable-state layer around Codex rather than as a Codex replacement.

Those assets SHALL also distinguish:

- native Codex subagents as bounded in-session delegation
- durable `omx team` as long-running execution and recovery
- general orchestration runtimes such as `LangGraph`, `AutoGen`, and `CrewAI` as separate programmable runtime families

Generated guidance SHALL prefer `OpenHands` over archived `OpenDevin` terminology.

#### Scenario: Operator reads the terminology section

- **WHEN** the operator reads generated playbook or leader guidance
- **THEN** it SHALL describe OMX as layered around Codex instead of replacing it
- **AND** it SHALL keep `OpenHands` and general orchestration-runtime terminology distinct from native Codex subagents
