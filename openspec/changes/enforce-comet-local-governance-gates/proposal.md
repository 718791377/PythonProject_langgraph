# Change: Enforce Comet Local Governance Gates

## Why
The repository needs executable controls for the corrected Comet governance rule: after a confirmed `/plan`, non-documentation implementation must first land a local governance package, use `docs_bilingual/` as the first durable decision surface, derive `openspec/` and `docs/` only when needed, use bilingual Markdown pairs, use Chinese commit subjects, and require active implementation plans before implementation.

## What Changes
- Update repository governance documents for docs_bilingual-first routing and complete local commit flow behavior.
- Add forward bilingual Markdown pair checking for changed files under `docs_bilingual/`, `openspec/`, and `docs/`.
- Add Chinese commit-subject checking for local commits and local MR review.
- Extend implementation-plan checks so Comet build/verify/archive phases require referenced implementation plans to be active.
- Record stable OpenSpec requirements for the new governance and script controls.

## Impact
- Local feature branches get stricter checks before local integration.
- Historical unchanged Markdown gaps remain baseline and do not block unrelated work.
- Remote publication remains separately gated.
