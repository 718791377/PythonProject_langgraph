# codex-user-level-skills-governance-lifecycle Specification

## Purpose
Define the phase-gated lifecycle for Codex user-level skills governance, including inventory, policy, governance checks, cleanup deferral, validation evidence, and local-main-first publication constraints.
## Requirements
### Requirement: Skills governance lifecycle phases SHALL be explicit and gated

The Codex user-level skills governance lifecycle SHALL define separate acceptance gates for Phase 0 baseline inventory, Phase 1 policy and registry, Phase 2 governance checks, Phase 3 safe cleanup proposal, and later launcher/profile integration.

Each phase gate MUST preserve the safety boundaries from the implementation plan: no user-level skill mutation without an explicit installer invocation, no Vercel plugin disablement as a shortcut, no automatic user-level `config.toml` mutation during repository checks, and no GitHub PR publication by default.

#### Scenario: Operator reviews the lifecycle phase map

- **WHEN** the operator reviews the skills governance lifecycle
- **THEN** the lifecycle SHALL show Phase 0, Phase 1, Phase 2, Phase 3, and launcher/profile integration as distinct gates
- **AND** it SHALL identify which validation commands and safety boundaries apply to each gate

#### Scenario: Profile-helper implementation is requested

- **WHEN** the operator explicitly approves a plugin module profile-helper implementation
- **THEN** the lifecycle MAY proceed to a script-backed `plugin-modules` skill implementation
- **AND** repository validation SHALL remain non-mutating unless the operator separately runs the user-level installer or hard-load profile helper with `-Apply`

### Requirement: Phase 0 audit SHALL verify the inventory baseline without mutating skills or plugins

Phase 0 SHALL verify that the repository contains a repeatable skills inventory command and a baseline inventory artifact that reports counts, source layers, duplicate skill-name groups, description lengths, suspected profiles, and status suggestions.

Phase 0 MUST NOT delete, move, rename, or rewrite user-level skills. Phase 0 MUST NOT disable plugins or plugin skills.

#### Scenario: Phase 0 inventory command is run
- **WHEN** `python tools/inventory_codex_skills.py --root . --json` is run for Phase 0 acceptance
- **THEN** the command SHALL emit JSON that reports current skill counts by source layer
- **AND** it SHALL report duplicate skill-name groups and profile/status suggestions without changing any scanned skill file

#### Scenario: Phase 0 detects duplicate or long-description candidates
- **WHEN** the inventory finds duplicate skill names or long descriptions
- **THEN** Phase 0 SHALL record them as inventory facts
- **AND** it SHALL not perform cleanup or description rewrites as part of the baseline step

### Requirement: Phase 1 audit SHALL verify governance policy, profile registry, and docs registry coverage

Phase 1 SHALL verify that repository-local governance artifacts exist for the skills governance policy, the profiles registry, and the documentation registry entry.

The profile registry MUST define at least the `core`, `browser`, `web`, `github`, and `full` profiles, and it MUST preserve browser automation expectations for the browser-profile legacy application project and `D:\PythonProject_CLIProxyAPI`.

The registry MUST remain declarative and MUST NOT automatically modify `C:\Users\lenovo\.codex\config.toml`.

#### Scenario: Phase 1 governance artifacts are audited
- **WHEN** Phase 1 acceptance is checked
- **THEN** the audit SHALL verify the bilingual skills governance policy files
- **AND** it SHALL verify the profiles registry file and the docs registry entry

#### Scenario: Browser-profile projects are checked
- **WHEN** the profiles registry is audited for browser-capable projects
- **THEN** the browser-profile legacy application project SHALL retain a browser-capable profile assignment
- **AND** `D:\PythonProject_CLIProxyAPI` SHALL retain a browser-capable profile assignment
- **AND** the audit SHALL not require disabling the Vercel plugin to reduce startup skill load

### Requirement: Phase 2 normalization SHALL be OpenSpec-controlled before guard or CI integration proceeds

Phase 2 SHALL define repository-local skills governance checks and tests before integrating those checks into broader guard or CI workflows.

Any existing external Phase 2 candidate, including GitLab MR !6, MUST remain frozen unless the user explicitly approves reuse, update, closure, or replacement after this OpenSpec change is reviewed.

#### Scenario: Phase 2 checks are accepted locally
- **WHEN** `python tools/check_codex_skills_governance.py --root . --json` and the related test command are run
- **THEN** Phase 2 SHALL classify required failures and expected warnings according to policy
- **AND** it SHALL pass locally before any new guard or CI integration is treated as accepted

#### Scenario: Existing MR candidate is present
- **WHEN** an existing GitLab MR candidate exists for Phase 2 guard or CI integration
- **THEN** the lifecycle SHALL treat that MR as a frozen candidate
- **AND** it SHALL not push to, force-update, close, merge, or otherwise mutate that MR without explicit user approval

### Requirement: Phase 3 cleanup SHALL remain deferred until clean-clone evidence exists

Phase 3 SHALL be limited to a safe cleanup proposal until official OpenSpec regeneration behavior and repository guard health are verified in a clean temporary clone.

No duplicate OpenSpec skill files, user-level skills, plugin cache files, or browser automation capabilities may be removed by Phase 3 unless the required evidence exists and the user explicitly approves the cleanup.

#### Scenario: Cleanup is requested without clean-clone evidence
- **WHEN** cleanup of duplicate OpenSpec skills or other skills is requested without clean-clone guard evidence
- **THEN** Phase 3 SHALL classify the cleanup as deferred
- **AND** it SHALL leave all user-level skills, plugin files, and repository skill files unchanged

#### Scenario: Cleanup evidence is prepared
- **WHEN** cleanup evidence is prepared for future review
- **THEN** it SHALL include clean temporary clone evidence for OpenSpec regeneration commands and guard validation
- **AND** it SHALL distinguish official generated output from migration leftovers before any deletion is proposed

### Requirement: Governance checks SHALL classify errors, warnings, and deferred cleanup separately

The skills governance validation surface SHALL distinguish blocking errors, non-blocking warnings, and deferred cleanup candidates.

Blocking errors MUST include missing required repository artifacts, same-layer user or repository-local duplicate skills not covered by policy, unknown profile tags, and broken documentation registry coverage. Warnings MAY include known cross-layer duplicates, plugin-layer duplicate skill names, known plugin bundle limitations, known Vercel bulk-load behavior, and user-level long descriptions that are intentionally not edited in the current phase. Deferred cleanup MUST include candidates that require future clean-clone evidence.

#### Scenario: Validation reports a blocking defect
- **WHEN** a required repository-local artifact or registry entry is missing
- **THEN** the governance check SHALL report an error
- **AND** the affected lifecycle phase SHALL not be accepted until the defect is fixed

#### Scenario: Validation reports an expected non-blocking issue
- **WHEN** the check detects a known user-level long description, a plugin-layer duplicate skill name, or known plugin bundle limitation
- **THEN** the governance check SHALL report a warning
- **AND** it SHALL not rewrite user-level or plugin-managed files as part of reporting that warning

#### Scenario: Validation reports cleanup candidates
- **WHEN** the check detects duplicate files that require OpenSpec regeneration evidence before removal
- **THEN** the governance check SHALL report the candidate as deferred cleanup
- **AND** it SHALL not treat the candidate as permission to delete files

### Requirement: Validation evidence SHALL be repeatable and local before publication

The lifecycle SHALL require repeatable local validation evidence before any publication decision.

At minimum, local evidence SHALL include `git diff --check`, repository document governance checks, implementation-plan governance checks, the skills inventory command, the skills governance check, the related skills governance test command, and OpenSpec status or validation for the active change.

If a validation requires `--require-clean-git`, it MUST be run in a clean temporary clone when the working tree contains unrelated drafts.

#### Scenario: Local validation is run in a dirty working tree
- **WHEN** the working tree contains unrelated local drafts
- **THEN** validation SHALL avoid treating those drafts as OpenSpec guard evidence
- **AND** any `--require-clean-git` guard run SHALL be deferred to a clean temporary clone

#### Scenario: Validation evidence is reported
- **WHEN** the operator reports lifecycle progress
- **THEN** the report SHALL list the commands run and their outcomes
- **AND** it SHALL identify any skipped clean-clone guard separately from passing local checks

### Requirement: Publication SHALL follow explicit approval and local-main-first workflow

Repository publication for this lifecycle SHALL require explicit user approval before commit, local `main` integration, push, MR update, MR creation, merge, or GitHub sync.

When local integration is approved, the repository SHALL use the local-main-first workflow: create a feature branch, run local CI and local MR review, keep the feature worktree clean, integrate the approved result into local `main`, and report any intentional remote lag. GitLab remote publication and GitHub sync SHALL remain later confirmation, backup, and mirror steps unless the user explicitly chooses a remote gate before local integration. GitHub PRs MUST NOT be created by default.

#### Scenario: Local OpenSpec artifacts are drafted

- **WHEN** OpenSpec artifacts are created locally for this lifecycle
- **THEN** the work SHALL remain uncommitted and unpublished unless the user explicitly requests commit, local integration, or remote publication
- **AND** existing remote MR candidates SHALL remain untouched unless the user explicitly requests an action on them

#### Scenario: Publication is explicitly approved

- **WHEN** the user explicitly approves publishing repository changes
- **THEN** the workflow SHALL use local `main` as the primary integration surface after local validation and local review pass
- **AND** GitLab SHALL be used as a remote publication and clean-environment confirmation surface
- **AND** GitHub SHALL be used only as the mirror/sync target unless the user explicitly overrides that rule

### Requirement: Skills usage audit reports SHALL sanitize explicit-skill noise tokens

The skills usage audit report SHALL sanitize and bound tokens that were rejected from explicit skill evidence before retaining them in `session_evidence.explicit_skill_noise_removed` or `noise_review.explicit_skill_noise_removed`.

Rejected explicit-skill noise tokens SHALL NOT be counted as strong evidence. They SHALL redact private paths, access tokens, API keys, cookies, standalone secrets, and similar sensitive substrings before report retention. They SHALL be truncated to a fixed maximum length.

#### Scenario: Noise token contains a private path or secret

- **WHEN** a session transcript contains an explicit-skill announcement candidate that is rejected as generic or unknown noise
- **AND** that rejected token contains a private path, token, cookie, or secret-like value
- **THEN** the audit report SHALL retain only a redacted and bounded noise token
- **AND** the raw private path, token, cookie, or secret-like value SHALL NOT appear in report JSON or sanitized Markdown summaries

#### Scenario: Noise review contract is incomplete or unsanitized

- **WHEN** the report field contract validates a generated or candidate-source audit report
- **AND** `noise_review` omits its privacy fields, retains raw noise tokens, contains raw private paths or secrets, or permits overlong noise tokens
- **THEN** the field contract SHALL fail
- **AND** the report SHALL be treated as incomplete evidence until regenerated or the script is fixed

### Requirement: Skills usage audit reports SHALL sanitize manual-note source paths

The skills usage audit report SHALL sanitize and bound manual-note source paths before retaining them in `manual_evidence.invalid_notes`, candidate source references, or sanitized Markdown summaries.

Manual-note source paths SHALL NOT be treated as retained raw evidence. They SHALL redact private Windows paths, POSIX home paths, UNC shares, access tokens, API keys, cookies, standalone secrets, and similar sensitive substrings before report retention.

#### Scenario: Manual note path contains a private path or secret

- **WHEN** a manual-note file path is missing, invalid, or otherwise included in invalid-note metadata
- **AND** that path contains a private path, token, cookie, or secret-like value
- **THEN** the audit report SHALL retain only a redacted and bounded path placeholder
- **AND** the raw private path, token, cookie, or secret-like value SHALL NOT appear in report JSON or sanitized Markdown summaries

#### Scenario: Manual evidence contract is incomplete or unsanitized

- **WHEN** the report field contract validates a generated or candidate-source audit report
- **AND** `manual_evidence` omits source-path privacy fields, marks source paths as retained, contains raw private paths or secrets, or permits overlong retained path values
- **THEN** the field contract SHALL fail
- **AND** the report SHALL be treated as incomplete evidence until regenerated or the script is fixed
