## ADDED Requirements

### Requirement: The generated playbook SHALL link to a quick-reference companion
The generated user-level playbook SHALL link to a concise quick-reference companion for the most common operator commands.

That companion SHALL live in the user-level docs layer and SHALL remain aligned with the actually installed user-level command surface.

#### Scenario: Operator starts from the full playbook but only needs common commands
- **WHEN** the operator opens the generated playbook and only needs the most common commands
- **THEN** the playbook SHALL point to the quick-reference companion
- **AND** the operator SHALL not need to scan the full playbook to find the most common command entrypoints
