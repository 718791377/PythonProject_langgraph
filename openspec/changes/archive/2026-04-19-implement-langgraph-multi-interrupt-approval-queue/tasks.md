## 1. Spec Delta Drafting

- [x] 1.1 Add multi-interrupt approval-queue requirements to `langgraph-durable-orchestration-backend`
- [x] 1.2 Add interrupt-queue inspection requirements to `codex-user-level-inspectable-team-state-surface`
- [x] 1.3 Add additive approval-queue inspection entrypoint requirements to `codex-user-level-team-mode-team-entrypoints`
- [x] 1.4 Add the new `codex-user-level-langgraph-multi-interrupt-approval-queue` capability spec

## 2. Python LangGraph Multi-Interrupt Implementation

- [x] 2.1 Add interrupt-queue and resume-mapping fields to `contracts.py`
- [x] 2.2 Persist bounded multi-interrupt queue metadata through the LangGraph CLI layer
- [x] 2.3 Add an inspectable approval-queue command or equivalent library surface for user-level tooling

## 3. User-Level Durable-State Surfaces

- [x] 3.1 Extend installer-generated LangGraph helper surfaces with an approval-queue inspection entrypoint
- [x] 3.2 Extend canonical durable-state projection with interrupt-queue and approval posture for tracked LangGraph threads
- [x] 3.3 Update generated playbook or quick-reference guidance for multi-interrupt approval queues

## 4. Validation

- [x] 4.1 Add or extend Python tests for multi-interrupt queue and resume-mapping posture
- [x] 4.2 Extend install-surface integration tests for approval-queue inspection behavior
- [x] 4.3 Run `openspec validate --all`
- [x] 4.4 Run `python .\\tools\\run_openspec_guard.py --root .`
