## 1. Define Durable Artifact Contracts

- [x] 1.1 Draft delta requirements for the frozen implementation brief as a stable LangGraph durable artifact.
- [x] 1.2 Draft delta requirements for the survivor queue as a stable LangGraph durable artifact.
- [x] 1.3 Specify minimum artifact fields, lifecycle rules, and fresh-context or repair-lane consumption boundaries.

## 2. Align Inspectable State

- [x] 2.1 Extend the LangGraph durable-state projection contract to expose brief and survivor-queue presence explicitly.
- [x] 2.2 Extend the canonical inspectable durable-state summary to expose artifact pointers and summary-level status without reopening backend-selection policy.
- [x] 2.3 Keep artifact inspection read-oriented by default.

## 3. Keep Scope Bounded

- [x] 3.1 Confirm the change text does not redefine stable default backend, explicit switching rules, or activation re-check behavior.
- [x] 3.2 Confirm the change remains additive to the current user-level bilingual plan and existing archived backend-policy changes.

## 4. Validation and Synchronization

- [x] 4.1 Validate that research handoff persists a frozen implementation brief before implementation begins in a fresh context.
- [x] 4.2 Validate that adversarial review persists only judged survivors into a resumable repair queue.
- [x] 4.3 Run `openspec validate --all`.
- [x] 4.4 Keep the user-level bilingual implementation plan synchronized with the hardened artifact terms.
