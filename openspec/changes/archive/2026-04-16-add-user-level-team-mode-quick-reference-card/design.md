## Context

The current user-level `team-mode-playbook.md` is now a rich operator reference. It covers modes, backends, entrypoints, inspectable durable state, cleanup or reconciliation, and lifecycle guidance. That is useful as a canonical playbook, but it is no longer optimized for the operator who only wants the most common commands without reading the whole document.

The current bottleneck is not missing capability. The bottleneck is command discoverability at operator speed. The user-level command surface now includes enough scripts that a short, stable, high-signal quick-reference companion would reduce friction without replacing the full playbook.

## Goals / Non-Goals

**Goals:**

- provide a concise user-level quick-reference card for the most common commands
- keep the quick-reference card aligned with the actually installed user-level assets
- separate “common command lookup” from “full playbook reading”
- explicitly distinguish read-only commands from mutating commands
- link the quick-reference card from the main user-level playbook

**Non-Goals:**

- replacing the full playbook
- introducing new runtime behavior or new command families
- documenting every possible helper or edge-case command
- adding repository-specific commands
- turning the quick-reference card into a policy document

## Decisions

### Decision 1: Treat the quick-reference card as a companion, not a replacement

The quick-reference card should sit beside the main playbook. It should not try to duplicate the full explanations in `team-mode-playbook.md`.

Alternative considered:

- compress the existing playbook directly into one shorter file
  - rejected because the playbook still needs to remain the canonical long-form operator reference

### Decision 2: Organize by operator task, not by file inventory

The quick-reference card should group commands by what the operator is trying to do:

- inspect current mode and switches
- inspect backend policy
- inspect current durable state
- preview or apply safe cleanup
- launch or operate a native `omx` team
- run or resume LangGraph durable execution

Alternative considered:

- mirror the directory listing of `C:\Users\lenovo\.codex\bin`
  - rejected because operators usually think in tasks, not filenames

### Decision 3: Explicitly mark read-only versus mutating commands

The quick-reference card should tell the operator whether each command is:

- read-only
- preview-only by default
- mutating

Alternative considered:

- rely on command naming alone
  - rejected because `status`, `preview`, `apply`, `run`, and `auto` differ in mutation posture and should be explicit

### Decision 4: Keep the first rollout intentionally small

The first rollout should focus on about ten high-frequency commands rather than trying to cover every helper surface.

Alternative considered:

- include every available helper from the user-level install
  - rejected because that would just create another long-form document

## Risks / Trade-offs

- [Risk] The quick-reference card may drift from the actual installed user-level surface. -> Mitigation: generate it from the same installer source that generates the playbook and wrappers.
- [Risk] The card may become another long-form document. -> Mitigation: keep the first rollout scoped to the most common commands only.
- [Risk] Operators may use the card without reading the main playbook when they really need policy detail. -> Mitigation: keep the quick-reference card concise and point back to the main playbook for semantics and lifecycle detail.

## Migration Plan

1. Define the quick-reference capability and scope.
2. Add a generated quick-reference asset under the user-level docs directory.
3. Link the main playbook to the quick-reference card.
4. Validate that the quick-reference commands match the actually installed user-level scripts.

## Open Questions

- Should the quick-reference card live as `team-mode-quick-reference.md` or a similar name under `C:\Users\lenovo\.codex\docs\`?
- Should the first rollout include only one-line commands, or also brief one-line “when to use” notes for each command?
