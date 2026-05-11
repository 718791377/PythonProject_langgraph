## 1. OpenSpec Artifacts

- [x] Create the proposal for replacing GitLab-first with local-main-first publication.
- [x] Create the design for local-main-first integration, remote-lag visibility, and stale-upstream protection.
- [x] Add delta specs for affected publication, lifecycle, alignment, product-lifecycle, and memory-handoff capabilities.

## 2. Governance and Startup Surfaces

- [x] Update `AGENTS.md` and `README.md` publication workflow wording.
- [x] Update bilingual startup summaries.
- [x] Update bilingual worktree-isolation, skills-governance, profile-mapping, and OPSX governance docs.
- [x] Update active implementation-plan and product-lifecycle references that still say GitLab-first.

## 3. Checker Wording

- [x] Update `tools/check_worktree_session_hygiene.py` wording so `gitlab/main` is a remote publication baseline rather than an authoritative mainline target.
- [x] Update related tests for the new wording while preserving local-ahead behavior.

## 4. Validation and Archive

- [x] Run `openspec validate replace-gitlab-first-with-local-main-first-publication --strict`.
- [x] Run `openspec validate --all` before archive.
- [x] Archive the OpenSpec change so stable specs reflect local-main-first publication.
- [x] Re-run `openspec validate --all`, repository guard, relevant unit tests, and `git diff --check` after archive.
