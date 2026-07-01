## Why

The durable-team document family has a fresh local reading run, but the tracked corpus still needs explicit delivery, source-traceability, and process-group proof surfaces. Without those surfaces, a cold-start maintainer can see refreshed white paper, research, lifecycle, implementation, playbook, and OpenSpec documents, but cannot quickly verify which user requirement each file satisfies, which evidence is tracked, and when Inputs / Tools and Techniques / Outputs are mandatory.

This change keeps the white paper and research note separate. It adds bridge and proof documents so the 10-layer runtime/governance capability core can land cleanly in the 12-layer product/business lifecycle planning frame.

## What Changes

- Add a durable-team delivery matrix under `docs_bilingual/implementation_plans/`.
- Add a durable-team source traceability index under `docs_bilingual/product_lifecycle/`.
- Add a durable-team process-group contract under `docs_bilingual/product_lifecycle/`.
- Refresh active durable-team corpus references from the prior 20260614 run to `fresh-source-lifecycle-whitepaper-pmi-refresh-20260616`, generated at `2026-06-15T17:33:52Z`.
- Update docs registry and OpenSpec requirements so the proof surfaces are governed and discoverable.

## Non-Goals

- Do not physically merge the white paper and research note.
- Do not claim a durable or persistent team runtime is implemented or running.
- Do not commit raw extraction text, per-unit streams, or local cache logs.
- Do not change launcher behavior, subagent routing, `native_omx`, LangGraph runtime state, model providers, or remote publication state.

## Governance Fields

- `impact_scope`: docs-only proof surfaces and stable-spec synchronization for the durable-team corpus.
- `explicit_non_goals`: no runtime launch, no remote publication, no raw-source-text commit, no whitepaper/research physical merge.
- `rollout_sequence`: create OpenSpec artifacts; add proof surfaces; update active corpus references; update stable and delta specs; validate; archive the change; commit the bounded package.
- `rollback_plan`: revert this branch commit or restore touched documentation/spec files from local `main`.
- `validation_path`: OpenSpec strict validation, document pair policy, implementation-plan rules, name clarity, mojibake guard, precommit update/archive review, local gate, and local MR review before local-main integration.
