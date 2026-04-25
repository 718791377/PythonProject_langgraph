## 1. Change Contract

- [x] 1.1 Define the LangGraph durable orchestration proposal, design, and spec scope
- [x] 1.2 Define how LangGraph fits under Codex / oh-my-codex without replacing the current durable path

## 2. Control Surface

- [x] 2.1 Add a durable orchestration backend selector to the generated user-level controls
- [x] 2.2 Define the repo-local LangGraph runtime-state layout under `.omx/state/langgraph/`
- [x] 2.3 Define the first operator-visible LangGraph status surface

## 3. Graph Contract

- [x] 3.1 Define the seven-phase root graph contract
- [x] 3.2 Define the subgraph contract for research, planning, execution, verification, and adversarial review
- [x] 3.3 Define the repo-local `thread_id` contract and checkpoint persistence model

## 4. Durable Workflow Objects

- [x] 4.1 Define the frozen implementation-brief schema for research-to-implementation handoff
- [x] 4.2 Define the adversarial-review survivor-queue schema for debugger-lane consumption
- [x] 4.3 Define interrupt and resume points for plan freeze, risky stabilization, and failed final verification

## 5. Entry Points and Routing

- [x] 5.1 Define additive LangGraph run/status/resume/inspect entrypoints
- [x] 5.2 Extend automatic durable routing to honor the selected durable orchestration backend
- [x] 5.3 Update the playbook contract so operators can distinguish direct `omx team` execution from LangGraph-backed durable orchestration

## 6. Validation

- [x] 6.1 Define validation for repo-local thread persistence and resume
- [x] 6.2 Define validation for interrupt -> approval -> resume
- [x] 6.3 Define validation for research brief persistence and fresh execution restart
- [x] 6.4 Define validation for adversarial-review survivors entering a debugger lane
- [x] 6.5 Run `openspec validate --all` and confirm the change is apply-ready
