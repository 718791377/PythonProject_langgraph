# 10-To-12 Layer Bridge

This bridge explains why the research note and the white paper remain separate and how their layer models connect.

## Relationship

- The research note uses a 10-layer runtime/governance decomposition to study what a solo-maintainable persistent team must do at execution time.
- The white paper uses the repository 12-layer product/business lifecycle to explain why the Codex CLI durable-team platform should exist and how it becomes governable.
- They should not be physically merged now because they have different audiences, review paths, and downstream references.

## Bridge Table

| 10-layer research model | 12-layer lifecycle landing zones | Bridge rule |
| --- | --- | --- |
| Interaction and execution | Product, Execution, Operations | Convert runtime interaction capability into product promises, execution workflow, and operating runbooks |
| Team orchestration | Organization, Execution | Convert worker/leader coordination into responsibility domains, agent governance, and execution gates |
| Agent state persistence | Technical, Operations | Convert state fields into architecture contracts and operational recovery evidence |
| Task-flow persistence | Technical, Execution, Operations | Convert workflow state into plans, checkpoints, resumption rules, and runbooks |
| Memory and context | Cognitive narrative, Technical, Operations | Convert memory capability into cold-start narrative, context-store design, and retention operations |
| Retrieval and knowledge | Metrics, Technical, Growth | Convert retrieval into evidence metrics, source maps, and reusable learning loops |
| Quality/evaluation | Metrics, Execution, Retrospective | Convert evaluation into acceptance gates, regression checks, and lessons learned |
| Security/governance | Technical, Organization, Operations | Convert security constraints into trust boundaries, approvals, and operating controls |
| Observability/audit | Metrics, Execution, Operations, Retrospective | Convert observability into metric guardrails, trace evidence, and closure records |
| Control center / operator surface | Cognitive narrative, Organization, Operations | Convert control surfaces into recoverable operator workflows and authority boundaries |

## Added 12-Layer Context

The 12-layer lifecycle adds four business-facing trunks that the 10-layer runtime research does not own directly: cognitive narrative, business, market, and growth. Those trunks explain purpose, value, adoption, and learning.

## Governance Rule

Use the 10-layer model when evaluating runtime capability completeness, state, orchestration, memory, auditability, and operator control. Use the 12-layer model when deciding whether the platform or a downstream one-person company has enough business, market, product, delivery, operations, and learning evidence. If a document cites both, state which model is being used and which lifecycle layer receives the result.
