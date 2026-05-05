# Map PMI Project Management To Codex Lifecycle

## Why

The repository now has a product and business lifecycle map, but it still needs a project-management overlay that explains how PMI references fit into Codex platform work and downstream project work.

The local `PMP/` directory is a private reference directory for PMI PDFs. It should inform lifecycle mapping, but it must not become tracked repository content. The repository also needs a clear distinction between product/business documents and project-governance documents.

## What Changes

- Add a bilingual PMI project-management reference map under `docs_bilingual/product_lifecycle/`.
- Update the Codex durable-team platform-build lifecycle to explain how PMI concepts tailor OpenSpec and GitLab-first delivery.
- Add OpenSpec requirements for using PMI as a governance overlay rather than replacing the product/business lifecycle.
- Keep `PMP/` ignored so local reference PDFs are not committed.

## Non-Goals

- Do not reproduce PMI book content.
- Do not implement runtime behavior.
- Do not launch `native_omx`; this is the durable backend lane for worker-centric execution.
- Do not launch `langgraph`; this is the graph checkpoint and approval-gate backend lane.
- Do not write `.omx/state/`; this is the repo-local durable state directory.
- Do not modify user-level Codex configuration.
