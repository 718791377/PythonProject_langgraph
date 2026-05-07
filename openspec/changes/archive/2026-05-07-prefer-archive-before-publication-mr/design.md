# Design: Archive-before-publication default

## Decision

The repository will treat archive-before-publication as the default packaging rule for completed local OpenSpec changes that are ready to publish.

The sequence is:

1. Implement the change in a dedicated feature worktree.
2. Run local implementation validation while the change is still active.
3. If the change is small and locally complete, archive it in the same feature branch so delta specs promote into stable specs.
4. Run post-archive validation.
5. Ask the user to confirm publication.
6. Open one GitLab MR containing implementation, archive movement, and stable spec updates.

## Single-MR path

Use the single-MR path for small governance, documentation, checker, and test changes when:

- local validation passes;
- the review surface is coherent;
- the rollback boundary is shared;
- archive promotion does not create heavy stable-spec conflicts.

## Two-MR exception path

Use a two-MR path only when:

- implementation is large or risky;
- remote CI or MR review should confirm implementation before archive;
- archive promotion would create substantial stable spec conflicts;
- the user explicitly asks for an implementation-only MR.

A two-MR implementation MR must state why archive is deferred and leave a visible follow-up archive path.

## Script-backed surfaces

The rule is backed by existing repository checks rather than prompt memory alone:

- `tools/check_worktree_session_hygiene.py` keeps writable work off primary `main` and prevents stale-base publication.
- `tools/check_session_ownership_claims.py` prevents overlapping sessions from taking the same OpenSpec change or path scope.
- `tools/check_openspec_code_archive_evidence.py` rejects code-class archives without source, executable check, CI, or test evidence.
- `tools/run_openspec_guard.py` aggregates the repository validation surface used before publication.
