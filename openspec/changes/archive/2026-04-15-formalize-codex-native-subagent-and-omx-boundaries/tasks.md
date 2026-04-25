## 1. Control Assets

- [x] 1.1 Extend the user-level team-mode installer or generator manifest to include a native-subagent limit control asset without touching native `codex` entrypoints
- [x] 1.2 Implement or finalize the native-subagent limit surface so it can inspect, and where supported manage, `agents.max_threads` and `agents.max_depth`
- [x] 1.3 Add verifiable safety coverage that the limit surface remains additive and does not replace or modify native `codex`, `codex.cmd`, or `codex.ps1`

## 2. Routing and Generated Guidance

- [x] 2.1 Extend the shared routing-policy model so automatic expert-role routing is described as a leader-side overlay over explicit native Codex subagent spawning
- [x] 2.2 Add routing-policy output and generated guidance for read-heavy preferred fan-out versus gated write-heavy parallel execution
- [x] 2.3 Update generated `team-leader` and playbook assets to distinguish native Codex subagents, durable `omx team`, `OpenHands`, and general orchestration runtimes

## 3. Agent TOML Boundaries

- [x] 3.1 Add user-level versus repository-scoped agent TOML placement rules to generated guidance and operator-facing docs
- [x] 3.2 Add validation or explicit documentation for the minimum standalone custom-agent TOML fields: `name`, `description`, and `developer_instructions`
- [x] 3.3 Verify the wrapped startup surfaces continue to describe `oh_my_codex=off` plus routing enabled as wrapped native-routed mode rather than raw unwrapped mode

## 4. Validation and Sync

- [x] 4.1 Validate generation into a repo-local target Codex home and verify the new limit-control asset is present and inspectable
- [x] 4.2 Validate the three startup-mode outcomes: enhanced mode, wrapped native-routed mode, and plain single-agent mode
- [x] 4.3 Validate that write-heavy parallel guidance requires explicit ownership isolation before approval
- [x] 4.4 Sync the final implementation back into affected bilingual implementation-plan or operator-facing documentation if implementation changes their wording or operator surface
- [x] 4.5 Run `openspec validate --all` and confirm the change is apply-ready
