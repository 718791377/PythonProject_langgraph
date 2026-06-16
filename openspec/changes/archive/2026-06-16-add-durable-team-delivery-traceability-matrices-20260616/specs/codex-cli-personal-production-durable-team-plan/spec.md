## ADDED Requirements

### Requirement: Durable-Team Corpus Maintains Delivery Traceability Proof Surfaces

The production durable-team documentation corpus SHALL maintain explicit proof surfaces for delivery coverage, source traceability, and process-group execution grammar. The delivery matrix SHALL map user requirements UR1 through UR4 to refreshed documents and non-goals. The source traceability index SHALL identify the current fresh-reading run, tracked-versus-ignored evidence boundaries, and source-family to authority-document mappings. The process-group contract SHALL define when Inputs, Tools and Techniques, and Outputs are required for execution-facing lifecycle layers, delivery gates, and release slices.

These proof surfaces SHALL remain documentation-governance evidence only. They SHALL NOT be treated as runtime evidence that a durable or persistent team is implemented, selected, running, or approved for apply mode.

#### Scenario: Maintainer audits the durable-team corpus after a source refresh

- **GIVEN** a maintainer opens the durable-team white paper, research note, implementation plan, playbook, lifecycle maps, or OpenSpec specs
- **WHEN** they need to verify which user requirement, source run, or execution grammar rule justifies a refreshed conclusion
- **THEN** the corpus points to the delivery matrix, source traceability index, and process-group contract
- **AND** the proof surfaces identify the current source run without requiring raw extraction cache in Git
- **AND** the proof surfaces preserve the whitepaper/research split and the 10-layer to 12-layer bridge
- **AND** the proof surfaces state that draft documentation does not prove a running durable-team runtime
