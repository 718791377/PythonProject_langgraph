# Change: enforce pre-commit update/archive gate

## Why
Local commits can otherwise land before existing governance files, CI manifests, checker registrations, or completed OpenSpec lifecycle artifacts are updated and archived.

## What changes
- Add a pre-commit update/archive checker.
- Run the checker from the aggregate OpenSpec guard and therefore from the installed pre-commit hook.
- Document the rule in AGENTS and bilingual governance docs.
- Register the safety rule and CI test coverage.

## Impact
- Local commits fail fast when a completed active OpenSpec change is not archived or explicitly deferred.
- New Python test files must be added to the CI manifest before commit.
- New checker scripts must be registered before commit.
