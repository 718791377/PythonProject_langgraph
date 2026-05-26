# Design: Enforce Comet Local Governance Gates

## Decisions
- Keep `docs_bilingual/` as the first durable decision surface, but do not force every decision into `implementation_plans/`.
- Make `openspec/` and `docs/` derived surfaces: update them only when the task itself needs stable spec lifecycle evidence or Superpowers runtime artifacts.
- Enforce bilingual Markdown pairs only for changed files so legacy archive gaps do not block unrelated work.
- Enforce Chinese commit subjects with a dedicated checker and commit-msg hook. ASCII conventional prefixes remain allowed when the subject contains Chinese.
- Reuse the existing implementation-plan checker for active-plan enforcement because it already owns registry integrity.

## Validation
- Unit tests cover pair policy, commit language, and active-plan references.
- The aggregate guard runs the new checks.
- Local MR review runs the commit-language check against the feature branch range.
