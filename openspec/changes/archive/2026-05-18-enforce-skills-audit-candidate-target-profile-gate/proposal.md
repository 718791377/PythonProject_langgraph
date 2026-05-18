# Proposal: enforce Skills audit candidate target-profile gate

## Why

The Skills usage audit can generate preview-only profile apply candidates after a 30-day reviewed summary. Candidate generation must not infer the target profile from ambient state, filenames, or generic continuation, because that could make an ambiguous candidate look reviewable or closable.

## What changes

- Require an explicit `--target-profile` when candidate JSON or Markdown output is requested.
- Block `--close-audit with-candidate` when a target profile is missing.
- Keep missing-target candidates as structured blocked preview records instead of unstructured exceptions.
- Render whether the target profile was provided in candidate Markdown.
- Add regression coverage for candidate gate, audit state, closure state, and missing-target preview behavior.
- Update the bilingual audit plan and stable skills-governance lifecycle spec.

## Safety

This is audit-only and preview-only. It does not mutate `config.toml`, plugin cache, hard-load profiles, user-level files, remote refs, or live plugin state.
