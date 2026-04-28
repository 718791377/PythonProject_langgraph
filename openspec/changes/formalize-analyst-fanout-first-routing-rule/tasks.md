## 1. Routing model updates

- [x] 1.1 Update the structured routing-policy model in `tools/install-codex-user-level-team-mode.ps1` to define the bounded analyst-fanout-first task class.
- [x] 1.2 Update the same routing-policy model so `architect`, `planner`, and `writer` are described as post-fan-in escalation roles for that task class rather than default first-round roles.

## 2. Generated operator-facing assets

- [x] 2.1 Update generated leader instructions so they explain that bounded multi-face research should first fan out into homogeneous `analyst` calls.
- [x] 2.2 Update generated routing-policy inspection output so it exposes the analyst-fanout-first sequencing rule in operator-facing language.
- [x] 2.3 Update generated user-level assets such as `team-leader.toml` and playbook text so they explain when analyst fan-out comes first and when later escalation to `architect`, `planner`, or `writer` occurs.

## 3. Verification

- [x] 3.1 Add or update tests that verify bounded multi-face research prefers homogeneous `analyst` fan-out in the first round.
- [x] 3.2 Add or update tests that verify `architect`, `planner`, and `writer` are not described as default first-round research roles for that task class.
- [x] 3.3 Run the relevant repository tests and the current OpenSpec guard sequence after the routing-policy and generated-asset changes land.
