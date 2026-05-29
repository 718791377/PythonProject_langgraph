## Design

### Selected approach

Use a full Comet documentation refactor rather than a tweak. The PySide6 plan governs future cross-project runtime and consumer-project GUI work, so later maintainers need an executable plan that does not depend on chat history.

### Structure decision

The plan is organized around the same structural family as `pi_plugin_codex_user_level_sidecar_plan.*`:

1. review conclusion and readiness metadata;
2. relationship model and naming boundary;
3. goals and non-goals;
4. runtime architecture and usage;
5. repo-local source of truth;
6. shared runtime artifacts and helper contracts;
7. JSON/runtime state model;
8. gates, rollback, risks and self-check;
9. ordered implementation items and local integration order.

The plan also borrows control semantics from `comet_runtime_agile_focus_area_plan.*`:

- management records are phase evidence, not decoration;
- phase gates require clear checklist evidence;
- Monitoring is a cross-phase control loop, not a sixth phase;
- file ownership, evidence retention, and local integration order are explicit.

### Key boundary decisions

- The plan remains `status: draft`; `plan_readiness` carries structure readiness.
- Shared runtime readiness is not consumer-project GUI readiness.
- Consumer projects own their own GUI source, adapters, tests, docs, and runtime contract.
- `project-local-override`, visible GUI validation, and packaging remain explicit-trigger gates.
- Current work does not install PySide6 or write any consumer project.

### Verification design

Validation focuses on Markdown hygiene, OpenSpec validity, implementation-plan registry and text health, precommit update/archive review, OpenSpec guard, local gate, and local MR review.

### Comet script limitation

The current Windows shell may not expose usable `bash`, while Comet runtime scripts are `.sh`. Therefore `.comet.yaml` records `comet_script_state: blocked:bash_not_found_on_windows`; validation relies on OpenSpec and repository gates instead of claiming Comet script transitions ran.
