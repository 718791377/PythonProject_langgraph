## Context

Phase 4 of the Codex user-level skills governance plan calls for a profile-to-launcher mapping and optional future launcher support such as `codex-ohmy-core`, `codex-ohmy-browser`, `codex-ohmy-web`, and `codex-ohmy-full`.

Current repository state:

- The profiles registry exists and defines `core`, `browser`, `web`, `github`, `full`, plus supporting `openspec` and `orchestration` profiles.
- The skills governance policy states that profile defaults are declarative and must not mutate user-level `config.toml`.
- The launcher payload policy states that user-level launchers must keep startup arguments short and use file-backed payload references for large instructions.
- This repository owns policy and source-of-truth documents, not installed user-level wrapper files.

The bottleneck is therefore not an installed launcher implementation. The safe next step is a validated mapping contract that a later installer or launcher change can consume.

## Goals / Non-Goals

**Goals:**

- Document the profile-to-launcher mapping in bilingual governance docs.
- Add declarative launcher mapping metadata to the profiles registry.
- Validate the mapping with a repository-local script.
- Preserve browser and web capabilities.
- Keep `core` reduced-scope and `full` temporary.
- Avoid installed launcher or user-level config mutation.

**Non-Goals:**

- No installed wrapper changes under the user-level Codex bin directory.
- No mutation of user-level `config.toml`.
- No actual fine-grained plugin filtering.
- No Vercel plugin disablement.
- No user-level skill edits.
- No GitHub PR workflow.

## Decisions

### Decision 1: Put mapping metadata in the existing profiles registry

The mapping belongs with the profiles it references. Adding a `launcher_mapping` section keeps profile definitions, project defaults, and launcher-facing mappings in one declarative policy file.

Alternatives considered:

- Create a separate YAML registry: rejected because it would duplicate profile names and increase drift risk.
- Edit user-level launcher config directly: rejected because the plan forbids automatic `config.toml` mutation.

### Decision 2: Implement validation before installed launcher changes

The checker will validate that required profiles have mapping entries, aliases are future-optional, config mutation is forbidden, and browser/web plugin preservation rules remain intact.

Alternatives considered:

- Install aliases immediately: rejected because user-level wrapper installation needs a separate explicit change and safety review.
- Documentation only: rejected because the mapping should be testable in CI.

### Decision 3: Treat aliases as future-optional command surfaces

Aliases such as `codex-ohmy-browser` are documented as intended launcher names, not installed commands. The stable base command remains `codex-ohmy`.

Alternatives considered:

- Treat aliases as currently available: rejected because this repository change does not install them.
- Omit aliases entirely: rejected because Phase 4 explicitly asks for profile-to-launcher mapping and future launcher support.

## Risks / Trade-offs

- [Risk] Operators may assume documented aliases are installed. -> Mitigation: mark every alias `future_optional` until a launcher install change lands.
- [Risk] The registry grows beyond pure profile metadata. -> Mitigation: keep `launcher_mapping` declarative and validate it with a small checker.
- [Risk] Default profile expectations drift from browser/web preservation rules. -> Mitigation: checker enforces browser and web preservation constraints.
- [Risk] Fine-grained plugin filtering is still unavailable. -> Mitigation: mapping explicitly keeps Vercel as bundle-managed for browser/web profiles.

## Migration Plan

1. Complete OpenSpec artifacts.
2. Add `launcher_mapping` metadata to `codex_skills_profiles.registry.yaml`.
3. Add bilingual mapping governance docs and docs registry entries.
4. Add checker and tests.
5. Run validation and OpenSpec guard.
6. Publish through GitLab-first workflow.

Rollback:

- Revert the registry section, docs, checker, tests, and OpenSpec change.
- No user-level launcher rollback is needed because no installed launcher files are changed.

## Observability and Failure Classification

The checker emits JSON with:

- `errors` for missing mappings, unknown profiles, unsafe config mutation, or browser/web preservation violations.
- `warnings` for future-optional aliases that are documented but not installed.
- `info` for checked profiles and aliases.

User-visible failure handling:

- If validation fails, the operator sees the exact missing profile, alias, or policy constraint.
- If aliases are only documented, the checker reports that state as expected metadata rather than a runtime installation claim.

## Open Questions

- Should the eventual launcher implementation expose separate physical commands, flags such as `codex-ohmy --profile browser`, or both?
- Should plugin-skill filtering be implemented by the launcher layer, plugin manager layer, or a shared profile resolver?
