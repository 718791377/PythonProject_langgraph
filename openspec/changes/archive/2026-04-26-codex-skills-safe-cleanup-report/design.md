## Context

The skills governance plan is now past the inventory, policy/registry, and governance-check phases. Phase 3 requires a safe cleanup proposal with generated evidence before any destructive cleanup is considered.

Current implementation inputs:

- `tools/inventory_codex_skills.py` scans user, repository, and plugin skills.
- `tools/check_codex_skills_governance.py` reports blocking errors, warnings, and deferred cleanup candidates.
- `docs_bilingual/governance/codex_skills_profiles.registry.yaml` records profile policy, duplicate preferred-source decisions, and known same-layer exceptions.
- `docs_bilingual/governance/codex_skills_inventory_baseline.json` records the Phase 0 baseline.

The remaining Phase 3 gap is not deletion. The gap is an explicit, repeatable evidence artifact that explains which items are cleanup candidates, what policy says about them, and why destructive action remains blocked.

Constraints:

- Do not delete or edit user-level skills.
- Do not delete repository OpenSpec nested duplicates in this change.
- Do not edit plugin cache files or disable Vercel.
- Do not mutate user-level `config.toml`.
- Preserve browser and web verification capability.
- Keep GitLab as the review surface and GitHub as post-merge sync only.

## Goals / Non-Goals

**Goals:**

- Add a repeatable Phase 3 report command.
- Generate a repository-local JSON report artifact.
- Classify cleanup candidates into non-destructive dispositions.
- Surface preferred-source decisions for cross-layer GitHub duplicates.
- Keep OpenSpec nested duplicate cleanup explicitly deferred until clean-clone evidence exists.
- Add tests that prove report generation is non-destructive and classifies candidates correctly.

**Non-Goals:**

- No actual cleanup or deletion.
- No user-level skill description shortening.
- No plugin or Vercel changes.
- No launcher aliases or profile filtering.
- No user-level config mutation.
- No GitHub PR workflow.

## Decisions

### Decision 1: Implement a dedicated report command instead of extending the governance checker

`check_codex_skills_governance.py` answers "is this state acceptable?" The Phase 3 report answers "what cleanup candidates exist and what evidence is required before action?"

Alternatives considered:

- Extend the governance check with more fields: rejected because the check should stay concise and pass/fail-oriented.
- Hand-write a Markdown report only: rejected because the report must be repeatable and testable.

### Decision 2: Use JSON as the generated artifact format

The report will be machine-readable and reviewable. JSON is already used by inventory and governance checks, and it can later feed launcher/profile tooling if needed.

Alternatives considered:

- YAML: rejected because the existing command surfaces already use JSON.
- Markdown only: rejected because tests would need fragile text assertions.

### Decision 3: Treat cleanup candidates as dispositions, not actions

Candidate records will use explicit dispositions such as `deferred_requires_clean_clone_evidence`, `report_only_plugin_managed`, or `preferred_source_recorded`.

Alternatives considered:

- Emit delete recommendations: rejected because Phase 3 requires explicit evidence and approval before destructive cleanup.
- Hide known duplicate candidates after policy exceptions: rejected because review visibility is the point of Phase 3.

### Decision 4: Reuse existing inventory parser and lightweight registry parsing

The report command should import `build_inventory` from `inventory_codex_skills.py` and parse only the registry fields it needs.

Alternatives considered:

- Add a full YAML parser dependency: rejected to avoid new dependencies.
- Duplicate inventory scanning logic: rejected because it would drift from Phase 0.

## Risks / Trade-offs

- [Risk] The lightweight registry parser may not handle every YAML construct. -> Mitigation: keep the registry schema simple and add tests for the fields used by this report.
- [Risk] Generated JSON may include machine-specific user paths. -> Mitigation: this is already true of inventory evidence; the report is repository governance evidence, not a portable public fixture.
- [Risk] Operators may interpret "candidate" as approval to delete. -> Mitigation: every destructive candidate includes a blocking evidence checklist and non-destructive disposition.
- [Risk] Clean-clone guard evidence is not produced by this change. -> Mitigation: classify it as missing evidence and leave cleanup deferred.

## Migration Plan

1. Create OpenSpec proposal, spec, design, and tasks.
2. Implement `tools/report_codex_skills_cleanup_candidates.py`.
3. Add `test/report_codex_skills_cleanup_candidates.test.py`.
4. Generate `docs_bilingual/governance/codex_skills_safe_cleanup_report.json`.
5. Run local validation and OpenSpec guard.
6. Publish through GitLab-first workflow.

Rollback:

- Revert the script, test, report artifact, and OpenSpec change.
- No external cleanup rollback is needed because the implementation is non-destructive.

## Observability and Failure Classification

The report command returns:

- exit code `0` when report generation succeeds,
- invalid JSON never expected in `--json` mode,
- candidate dispositions for review rather than blocking errors.

Failure classes:

- `error`: required repository input is missing or unreadable.
- `deferred`: candidate exists but lacks clean-clone evidence or explicit approval.
- `report_only`: plugin-managed or vendor-managed item.
- `preferred_source_recorded`: duplicate has a policy decision but no immediate action.

## Open Questions

- Should a future Phase 4 launcher mapping consume this report directly, or only consume the profiles registry?
- Should future cleanup evidence be a separate JSON artifact, or appended to this report schema as `evidence` entries?
