# Design: PPT Visual Review Tool

## Architecture

The tool is a local sidecar, not a PPT editor. It consumes slide PNGs produced by existing render helpers and creates a portable review package. The backend stays stdlib-only and can run in consumer projects without installing a web framework.

## Data Flow

1. Existing PPT render helpers produce slide PNGs under a consumer-owned output directory.
2. `ppt_review_tool.py` copies those PNGs into a review session folder and records source provenance.
3. Raw comments are normalized into a schema with `slide`, `roi`, `severity`, `category`, `comment`, `suggested_fix`, and `status`.
4. The tool writes JSON evidence and an offline HTML report. Static viewer assets support manual browser annotation workflows.

## Boundaries

The source PPTX is read-only metadata input. Generated review sessions belong under ignored project output paths. The tool does not run an HTTP server, modify PATH, download dependencies, or contact external services.
