## 1. Spec and Contract Updates

- [x] 1.1 Add a new capability spec for user-level LangGraph quality-gated loops.
- [x] 1.2 Update the LangGraph backend spec to require structured gate verdicts and bounded iterative loop execution.
- [x] 1.3 Update the inspectable durable-state spec to expose LangGraph loop progress as projection data.

## 2. Runtime and State Semantics

- [x] 2.1 Define the structured gate verdict contract used by LangGraph conditional edges.
- [x] 2.2 Define which user-level flows are loop-capable in the first rollout.
- [x] 2.3 Define persisted loop metadata, iteration budgets, and explicit termination reasons.

## 3. Inspectability and Operator Handling

- [x] 3.1 Extend LangGraph thread projection so inspect and status surfaces expose active loop, iteration count, last gate verdict, and stop reason.
- [x] 3.2 Ensure loop state survives interrupt, resume, and restart without restarting the loop from iteration one.
- [x] 3.3 Keep non-looping LangGraph fallback behavior intact while the new loop path is introduced.

## 4. Validation and Synchronization

- [x] 4.1 Validate one `draft -> review -> revise -> review -> accept` path.
- [x] 4.2 Validate one `execute -> verify -> revise -> execute` path.
- [x] 4.3 Validate explicit termination on budget exhaustion and operator interrupt.
- [x] 4.4 Run `openspec validate --all`.
- [x] 4.5 Keep the user-level bilingual implementation plan synchronized with the delivered loop semantics.
