## MODIFIED Requirements

### Requirement: Fan-out and write-heavy parallel execution SHALL be bounded and ownership-isolated

Native Codex subagent use SHALL remain leader-side spawning with leader-owned fan-in. Raw Codex SHALL NOT be described as auto-spawning specialist roles by default. Managed fan-out SHALL stay within `agents.max_threads=6` and `agents.max_depth=1` unless an explicit override, reason, and approval are recorded.

Parallel fan-out SHOULD prefer read-heavy or otherwise tightly bounded independent work. Write-heavy parallel execution SHALL declare file/module ownership, disjoint write sets, hotspot serialization, and leader-owned final integration. Code-changing worker briefs SHALL tell workers they are not alone in the codebase, SHALL require them not to revert or overwrite other active owners, and SHALL require changed-path reporting.

Fan-out and write-ownership evidence SHALL be script-checkable. The repository SHALL provide `tools/check_fanout_write_ownership_evidence.py` to validate repository policy surfaces and saved run-summary or worker-brief evidence for managed fan-out limits, leader-side spawning, raw-Codex terminology, bounded read-heavy fan-out, write-heavy ownership isolation, hotspot serialization, leader-owned final integration, not-alone/do-not-revert worker instructions, and changed-path reporting.

#### Scenario: Managed fan-out stays within defaults

- **WHEN** saved evidence describes native subagent or expert fan-out
- **THEN** it SHALL stay within `agents.max_threads=6` and `agents.max_depth=1`
- **OR** it SHALL record an explicit override with reason and approval
- **AND** it SHALL show leader-side spawning and leader-owned fan-in rather than raw Codex auto-spawning specialist roles

#### Scenario: Write-heavy parallel work is ownership-isolated

- **WHEN** saved evidence describes write-heavy parallel execution or code-changing workers
- **THEN** it SHALL declare file/module ownership and disjoint write sets
- **AND** it SHALL identify hotspot serialization or state that no shared hotspot exists
- **AND** it SHALL identify leader-owned final integration
- **AND** worker briefs SHALL include not-alone/do-not-revert-or-overwrite instructions and changed-path reporting

#### Scenario: Overlapping write sets are serialized

- **WHEN** saved evidence mentions overlapping write sets or shared hotspot paths
- **THEN** the evidence SHALL show hotspot serialization, sequential ownership transfer, or a leader-owned merge plan before parallel write work proceeds
- **AND** it SHALL fail fan-out/write-ownership evidence if overlapping write-heavy workers are launched without serialization
