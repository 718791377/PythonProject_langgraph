## 1. OpenSpec Artifacts

- [x] 1.1 Create proposal, design, specs, and task artifacts for the script-backed safety and context-retention canary rule.

## 2. Script Controls

- [x] 2.1 Add a safety-rule script-backing registry.
- [x] 2.2 Add an aggregate checker for registered safety rules.
- [x] 2.3 Extend the context-retention canary checker so recovery text must mention `AGENTS.md`.
- [x] 2.4 Run the aggregate checker from `tools/run_openspec_guard.py`.

## 3. Prompt Reminder Surfaces

- [x] 3.1 Update the startup summary pair so canary recovery explicitly rereads `AGENTS.md`.
- [x] 3.2 Update active and final-target implementation plans so safety rules use script control plus prompt reminders.
- [x] 3.3 Preserve the rule that `AGENTS.md` must not contain the literal canary prompt.

## 4. Validation And Publication

- [x] 4.1 Run targeted checker, OpenSpec, and guard validation.
- [x] 4.2 Publish through GitLab-first MR and sync GitHub after GitLab main is green.
