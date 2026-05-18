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

### Requirement: Skills usage audit Markdown summaries SHALL expose evidence privacy gates

The skills usage audit sanitized Markdown summaries SHALL expose the same evidence-retention privacy gates that are used by the JSON report field contract and profile-candidate gate.

The audit Markdown summary MUST show explicit-skill noise-token privacy state and manual-note source-path privacy state. The profile-candidate Markdown summary MUST show source-report privacy status and any source-report privacy violations or blockers. These summaries MUST remain sanitized and MUST NOT include raw transcripts, raw local paths, tokens, cookies, or user-level configuration contents.

#### Scenario: Reviewer reads a sanitized audit summary

- **WHEN** the audit script renders `--summary-output`
- **THEN** the Markdown SHALL show whether raw explicit-skill noise tokens were retained
- **AND** it SHALL show a bounded sanitized sample list of removed explicit-skill noise tokens, or `none` when no token was removed
- **AND** it SHALL show the noise-token privacy policy and maximum retained token length
- **AND** it SHALL show whether manual-note source paths were retained
- **AND** it SHALL show the manual-note source-path privacy policy and maximum retained source-path length

#### Scenario: Reviewer reads a profile-candidate summary

- **WHEN** the audit script renders `--candidate-summary-output`
- **THEN** the Markdown SHALL show source-report privacy status
- **AND** it SHALL show source-report privacy violations or `none`
- **AND** it SHALL remain non-mutating and preview-only unless a later separate explicit apply authorization is given

### Requirement: Skills usage audit log excerpts SHALL preserve redaction marker integrity

The skills usage audit report SHALL preserve complete redaction markers when sanitized log excerpts are truncated for retention.

Sanitized log excerpts MUST redact private paths, access tokens, API keys, cookies, standalone secrets, and similar sensitive substrings before truncation. If truncation reaches the middle of a redaction marker, the retained excerpt MUST include a complete redaction marker and MUST NOT retain a partial marker such as `[RE`, `[REDACTED_`, or `[REDACTED_SE` as the only privacy indication.

#### Scenario: Log excerpt truncates across a redacted private path

- **WHEN** a budget-warning log message contains a private path near the excerpt limit
- **THEN** the retained `message_excerpt` SHALL include either no path marker or a complete `[REDACTED_PATH]` marker
- **AND** it SHALL NOT include the raw private path
- **AND** it SHALL NOT end with a partial redaction marker fragment

#### Scenario: Log excerpt truncates across a redacted secret

- **WHEN** a budget-warning log message contains a secret-like value near the excerpt limit
- **THEN** the retained `message_excerpt` SHALL include either no secret marker or a complete `[REDACTED_SECRET]` marker
- **AND** it SHALL NOT include the raw secret value
- **AND** it SHALL NOT end with a partial redaction marker fragment

### Requirement: Skills usage audit reports SHALL expose script capability boundaries

The skills usage audit report SHALL expose what the audit helper can reliably cover and what still requires human review.

The JSON report MUST include `script_capability_boundaries` with non-empty `policy`, `reliable_coverage`, `human_review_required_for`, and `enhancement_triggers` fields. The field contract MUST fail when those fields are missing, wrong-typed, or empty. The sanitized Markdown summary MUST render the same boundary so reviewers do not treat the audit helper as an omniscient source of truth.

#### Scenario: Reviewer reads script capability boundaries in a generated report

- **WHEN** the audit script generates JSON and Markdown summary output
- **THEN** the JSON SHALL include non-empty script capability boundary lists
- **AND** the Markdown summary SHALL show reliable coverage, human-review needs, and enhancement triggers
- **AND** the field contract SHALL pass only when those boundary fields are present and non-empty

#### Scenario: Candidate gate receives a report without script boundaries

- **WHEN** profile-candidate generation validates an audit report
- **AND** `script_capability_boundaries` is missing, wrong-typed, or contains empty boundary lists
- **THEN** the field contract SHALL fail
- **AND** candidate generation SHALL remain blocked until the report is regenerated or the script is fixed

### Requirement: Skills usage audit reports SHALL expose cadence-review drift

The skills usage audit report SHALL expose whether the audit run is on cadence, late, or recovering missed weekly reports.

The JSON report MUST include `cadence_review` with `late_run`, `missed_weekly_runs`, and `weekly_report_review`. The field contract MUST fail when those fields are missing or wrong-typed, when `missed_weekly_runs` is not `null` or a non-negative integer, or when `late_run=true` omits an explicit missed-run count. The sanitized Markdown summary MUST render the cadence fields in the audit-window section.

#### Scenario: Reviewer reads cadence state in a generated summary

- **WHEN** the audit script generates JSON and Markdown summary output
- **THEN** the JSON SHALL include the cadence-review fields
- **AND** the Markdown summary SHALL show late-run status, missed weekly runs, and weekly-report review status
- **AND** the field contract SHALL pass only when the cadence-review fields are present and valid

#### Scenario: Candidate gate receives a report with invalid cadence state

- **WHEN** profile-candidate generation validates an audit report
- **AND** `cadence_review` is missing, wrong-typed, has a negative missed-run count, or marks `late_run=true` without a missed-run count
- **THEN** the field contract SHALL fail
- **AND** candidate generation SHALL remain blocked until the report is regenerated or the script is fixed

### Requirement: Skills usage audit Markdown summaries SHALL expose audit-state blockers

The skills usage audit sanitized Markdown summary SHALL expose the audit-state next action, profile-apply allowance, and any state-machine blockers that explain why the report cannot advance.

The Markdown summary MUST render blockers from `close_blockers`, `candidate_blockers`, `summary_review_blockers`, `pause_blockers`, and `warning_triage_blockers`. When no audit-state blocker exists, the summary MUST render `none`.

#### Scenario: Reviewer reads a blocked closure summary

- **WHEN** the audit script generates a sanitized Markdown summary for a report whose closure is blocked
- **THEN** the Markdown SHALL show the audit state's next action
- **AND** it SHALL show that profile apply is not allowed
- **AND** it SHALL list the concrete closure blockers without requiring the reviewer to open raw JSON

#### Scenario: Reviewer reads a closed or unblocked summary

- **WHEN** the audit script generates a sanitized Markdown summary for a report with no audit-state blockers
- **THEN** the Markdown SHALL show `none` for audit-state blockers

### Requirement: Skills usage audit Markdown summaries SHALL expose advisory decision buckets

The skills usage audit sanitized Markdown summary SHALL expose advisory decision buckets derived from module evidence so reviewers can distinguish default/project profile review candidates from on-demand, manual-review, and dormant modules without opening raw JSON.

Decision buckets MUST remain non-mutating review inputs. They MUST NOT mark profile apply as allowed and MUST NOT replace a later profile apply candidate record or explicit apply authorization.

#### Scenario: Reviewer reads advisory decision buckets

- **WHEN** the audit script generates JSON and Markdown summary output
- **THEN** the report SHALL include advisory decision buckets for profile-review candidates, on-demand soft-load modules, manual-review medium/weak modules, and dormant/restorable modules
- **AND** the Markdown summary SHALL render those buckets in the decision recommendation section
- **AND** the summary SHALL state that profile apply is not allowed by the summary itself

### Requirement: Skills usage audit field contracts SHALL validate advisory decision recommendations

The skills usage audit report field contract SHALL validate that `decision_recommendation` remains an advisory-only, non-mutating review input.

The JSON report MUST include `decision_recommendation.status=advisory_only_no_profile_apply`, a non-empty policy string, `profile_apply_allowed=false`, the four required bucket lists (`profile_review_candidates`, `on_demand_soft_load`, `manual_review_medium_or_weak`, and `dormant_restorable`), and `bucket_counts` values that exactly match those bucket lengths. The field contract MUST fail when those fields are missing, wrong-typed, non-advisory, allow profile apply, contain non-string bucket entries, or carry stale bucket counts.

#### Scenario: Candidate gate receives a report with invalid decision recommendations

- **WHEN** profile-candidate generation validates an audit report
- **AND** `decision_recommendation` is missing, non-advisory, marks profile apply as allowed, omits a required bucket, includes a non-string bucket entry, or has a stale `bucket_counts` value
- **THEN** the field contract SHALL fail
- **AND** candidate generation SHALL remain blocked until the report is regenerated or the script is fixed

### Requirement: Skills usage audit field contracts SHALL validate module evidence rows

The skills usage audit report field contract SHALL validate every `module_evidence` row before that evidence can drive advisory decision buckets or profile-candidate generation.

Each module evidence row MUST include the module name, plugin list, strong helper-call count, strong skill-path-read count, strong total, default-candidate threshold, mapped-tool-call medium-evidence count and policy, medium-evidence rationale, weak plugin mentions, cross-project utility, and advisory recommendation. Numeric counts MUST be non-negative integers, `strong_total` MUST equal strong helper calls plus strong skill-path reads, plugin entries MUST be strings, mapped tool-call evidence MUST remain medium evidence only, cross-project utility MUST require manual review, and recommendations MUST remain within the approved advisory recommendation set.

The row recommendation MUST match the threshold rule for that row: `strong_total >= default_candidate_threshold` is a profile-review candidate, `0 < strong_total < default_candidate_threshold` stays on-demand, `strong_total == 0` with weak mentions is mentioned-only, and no strong or weak evidence stays dormant/restorable.

#### Scenario: Candidate gate receives a report with invalid module evidence

- **WHEN** profile-candidate generation validates an audit report
- **AND** any `module_evidence` row is missing required fields, has wrong-typed values, contains non-string plugin entries, has negative counts, has a stale `strong_total`, treats mapped tool calls as strong evidence, skips manual cross-project review, or uses an unsupported recommendation
- **THEN** the field contract SHALL fail
- **AND** candidate generation SHALL remain blocked until the report is regenerated or the script is fixed

#### Scenario: Candidate gate receives a report with stale recommendation thresholds

- **WHEN** profile-candidate generation validates an audit report
- **AND** a `module_evidence` row recommendation contradicts its `strong_total`, `weak_plugin_mentions`, or `default_candidate_threshold`
- **THEN** the field contract SHALL fail
- **AND** candidate generation SHALL remain blocked until the report is regenerated or the script is fixed

### Requirement: Skills usage audit output retention gates SHALL block local-only raw audit artifacts

The skills usage audit lifecycle SHALL keep raw audit outputs local-only unless they have been converted into an explicitly reviewed sanitized long-term evidence document.

The repository guard MUST run a Skills audit output-retention check that fails when any `.tmp/` artifact is tracked, staged, changed, or commit-visible untracked. The same check MUST fail when raw Skills usage audit JSON reports with names beginning `skills-usage-audit`, `skills-usage-baseline`, `skills-usage-warning`, or `skills-usage-report` are retained outside `.tmp/`.

Sanitized Markdown summaries MAY be retained as long-term evidence after privacy review. Raw session transcripts, raw JSON audit reports, private paths, tokens, and vendor-cache contents MUST NOT be retained as durable Git evidence for this audit.

#### Scenario: Forced `.tmp` raw audit report is staged

- **WHEN** `.tmp/skills-usage-audit-30d.json` is forced into Git or otherwise becomes tracked, staged, changed, or commit-visible untracked
- **THEN** the output-retention check SHALL fail
- **AND** it SHALL report both the `.tmp/` artifact retention violation and the raw audit JSON retention violation when both apply

#### Scenario: Raw audit JSON is retained outside `.tmp`

- **WHEN** `reports/skills-usage-baseline-2026-05-18.json` or another raw `skills-usage-*.json` audit report is tracked, staged, changed, or commit-visible untracked outside `.tmp/`
- **THEN** the output-retention check SHALL fail
- **AND** the reviewer SHALL regenerate or retain only a sanitized Markdown summary for long-term evidence

#### Scenario: Sanitized Markdown evidence is retained

- **WHEN** a reviewed `skills-usage-audit-30d-summary.md` or equivalent sanitized Markdown summary is retained
- **THEN** the output-retention check SHALL pass for that summary
- **AND** the summary SHALL remain subject to the audit privacy and data-minimization requirements
