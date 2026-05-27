## Design

### Selected approach

Use a full Comet documentation refactor rather than a tweak. The target file is a long-lived implementation plan that will drive later toolchain implementation, so it needs durable OpenSpec artifacts, a delta spec, a design record, a build plan, and an explicit archive deferral record.

### Structure decision

The plan is organized around the same top-level pattern as `pi_plugin_codex_user_level_sidecar_plan.zh-CN.md`:

1. review conclusion and readiness metadata;
2. relationship model and naming boundary;
3. goals / non-goals;
4. runtime architecture and usage;
5. repo-local source of truth;
6. target install artifacts and manifest;
7. CLI / GUI / JSON contracts;
8. safety, privacy, rollback, uninstall;
9. readiness lanes;
10. ordered implementation items, validation plan, related-doc update rules, risks, self-checks.

The plan also borrows the control semantics from `comet_runtime_agile_focus_area_plan.zh-CN.md`:

- management records are phase evidence, not decoration;
- phase gates require checklist evidence and a clear Monitoring decision;
- Monitoring return is a cross-phase control loop, not a sixth phase;
- implementation work is expressed as slices plus item-level checkboxes;
- file ownership, local integration order, and evidence retention are explicit.

### Key boundary decisions

- The plan remains `status: draft` because it is not a runtime completion claim.
- `plan_readiness` records that the structure is ready for implementation slicing, not that GUI control is ready.
- The target project remains the owner of Agent TOML, private prompts, Phase 1 CLI and `.omx/state`.
- This repository remains the owner of the shared GUI toolchain source, templates, checker and installer.
- The GUI never edits target state JSON directly; it only calls target project CLI contracts.
- Existing `D:\PythonProject_paper_suggest` evidence remains blocked/repair-lane until a future readiness checker proves otherwise.
- Chinese support artifacts for this change must be valid UTF-8 Chinese, not mojibake or question-mark placeholders.

### Verification design

The change is documentation-only, so validation focuses on:

- markdown/diff hygiene;
- OpenSpec change validity;
- implementation plan frontmatter/structure guard;
- precommit update/archive gate including archive deferral;
- repository OpenSpec guard;
- local MR review after the commit.

### Comet script limitation

Current Windows shell does not expose usable `bash`, while Comet runtime scripts are `.sh`. Therefore `.comet.yaml` records `comet_script_state: blocked:bash_not_found_on_windows`; validation relies on OpenSpec and repository gates instead of claiming Comet script transitions ran.
