## Context

The bilingual Codex / oh-my-codex user-level team-mode implementation plan is still the main long-form canonical reference for operator-facing understanding of the user-level orchestration model. Since the earlier plan-sync pass landed, the current user-level installation under `C:\Users\lenovo\.codex` has moved further: layered capability switches are real, effective-lane selection is now operator-visible, and the global provider-pacing interpretation is now also installed into startup-read user-level surfaces such as `team-leader.toml`, `team-mode-playbook.md`, and the generated routing-policy JSON.

The current bottleneck is not missing runtime capability. The bottleneck is renewed document drift. Parts of the bilingual implementation plan still describe already-landed user-level state as later direction, and they do not yet fully reflect the current operator-facing interpretation that startup and session routing now read from user-level assets. If left unchanged, the bilingual plan weakens as a canonical reality map and becomes less useful as a cross-check against the actual installed user-level orchestration layer.

## Goals / Non-Goals

**Goals:**

- resync the bilingual implementation-plan pair with the current installed user-level state
- ensure the plan no longer mislabels already-landed layered capability behavior as future work
- ensure the plan reflects current operator-facing user-level interpretation where that interpretation is already installed and validated
- preserve explicit boundaries among implemented current state, optional advanced paths, and true future work
- keep English and Chinese plan files semantically aligned

**Non-Goals:**

- introducing a new orchestration backend or new runtime behavior
- rewriting the whole implementation plan from scratch
- turning the plan into a changelog or installation transcript
- changing current user-level global switch values
- adding repository-specific LangGraph migration policy into the user-level plan

## Decisions

### Decision 1: Treat installed user-level operator surfaces as evidence, not just repository-local plan text

This sync pass should classify state based on current installed user-level evidence, especially:

- `C:\Users\lenovo\.codex\agents\team-leader.toml`
- `C:\Users\lenovo\.codex\docs\team-mode-playbook.md`
- `C:\Users\lenovo\.codex\bin\codex-routing-policy.ps1 -Json`
- `C:\Users\lenovo\.codex\bin\codex-durable-backend-status.ps1 -Json`

This avoids leaving the bilingual plan behind when the real startup-read user-level layer has already advanced.

Alternative considered:

- sync only against repository-local implementation-plan prose
  - rejected because it can preserve stale wording even after user-level assets are already installed and validated

### Decision 2: Preserve the plan as a state map, not a feature backlog

The bilingual plan should continue to answer three different questions cleanly:

- what is implemented now
- what is optional but already available
- what is still future work

Already-landed layered capability behavior, effective-lane interpretation, and provider-pacing guidance should move into implemented current state where appropriate. Optional future layers such as mixed-pane compose should remain explicitly future.

Alternative considered:

- keep older “later target” wording for caution even after implementation lands
  - rejected because it makes the canonical plan less trustworthy than the installed user-level surfaces

### Decision 3: Sync semantic meaning, not only section presence

This change should not stop at checking whether both bilingual files contain roughly the same headings. The sync standard should include semantic parity on:

- current state classification
- optional-path classification
- future-work classification
- operator-facing interpretation already exposed by user-level startup-read surfaces

Alternative considered:

- treat bilingual sync as heading-level or paragraph-count parity only
  - rejected because status meaning can still drift while file shape stays superficially similar

### Decision 4: Keep provider pacing framed as orchestration backpressure, not as a feature blocker

The provider proxy pacing rule is now part of the user-level startup-readable operator layer. The plan should reflect the same meaning:

- rolling 1-minute true-upstream-forward budget
- overflow waits for a slot
- this does not by itself disable LangGraph, `native_omx`, or native subagents

Alternative considered:

- leave pacing interpretation only in project-level startup or runtime docs
  - rejected because the user-level team-mode plan now also serves as a canonical operator-facing orchestration reference

## Risks / Trade-offs

- [Risk] The sync pass could accidentally restate every installed surface and turn the plan into a changelog. -> Mitigation: update only the status-classification and operator-meaning sections that are stale.
- [Risk] Current-state wording may over-promote optional advanced paths into defaults. -> Mitigation: preserve explicit labels for default path, optional available path, and future path.
- [Risk] The bilingual pair may remain textually different after the sync. -> Mitigation: validate semantic parity explicitly as part of the change scope instead of treating translation as follow-up cleanup.
- [Risk] Installed user-level surfaces may later drift again after future changes land. -> Mitigation: keep this capability under the existing plan-status-sync spec so future changes can reuse the same maintenance obligation.

## Migration Plan

1. Audit the current bilingual implementation-plan pair against the installed user-level operator surfaces and relevant stable specs.
2. Identify wording that still describes already-landed layered capability behavior or operator-facing pacing interpretation as future.
3. Update the English and Chinese plan files so they classify current state, optional available paths, and future work consistently.
4. Update the `codex-user-level-team-mode-plan-status-sync` delta spec to reflect the tightened sync contract.
5. Validate the bilingual pair against the real user-level installation and run `openspec validate --all`.

## Open Questions

- Should the bilingual plan include a small “validated against current user-level installation on <date>” marker, or is that too changelog-like for this layer?
- Should future user-level orchestration changes be required by policy to update both the bilingual plan and the installed user-level operator surfaces in the same change whenever status classification changes?
