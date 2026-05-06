## ADDED Requirements

### Requirement: Platform White Paper And MRD Are First-Class Lifecycle Documents

The repository SHALL maintain first-class bilingual white paper and MRD documents for the Codex CLI personal production durable-team platform before treating downstream implementation plans as complete lifecycle coverage.

#### Scenario: A maintainer follows the lifecycle stack

- **GIVEN** the maintainer reads the platform lifecycle documentation
- **WHEN** the maintainer needs the cognitive narrative and market requirements
- **THEN** the maintainer can find the canonical white paper under `docs_bilingual/whitepapers/`, which is the white-paper directory
- **AND** the maintainer can find the MRD under `docs_bilingual/market_requirements/`, which is the market-requirements directory
- **AND** concrete workload-to-profile mappings are available inside the MRD appendix rather than a separate implementation-plan reference
