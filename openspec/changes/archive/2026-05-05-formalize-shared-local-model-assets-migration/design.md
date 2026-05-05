# Design: Shared Local Model Assets Migration

## Boundary

This change is documentation and governance only. It records how future work should migrate local model assets without creating dirty work in either Git repository.

## Model Asset Ownership

`D:\PythonProject_langgraph` is the orchestration repository. It may own ignored local model asset directories, provider profile templates, health checks, and adapter contracts.

`D:\PythonProject_OpenClaw` is a consumer and domain-agent platform. It may start or call the shared local model service through explicit profiles, but it must not own the authoritative model asset policy or Codex durable-team state.

## Provider Profiles

The migration plan standardizes two advisory profiles:

- `local-judge-qwen` - local lightweight judgement and summarization provider backed by `Qwen3.5-9B-Q4_K_M-GGUF`.
- `local-embed-jina` - local embedding provider backed by `jina-embeddings-v5-text-small-retrieval-GGUF`.

Both profiles are providers only. They are not durable backends, approval authorities, routing selectors, or sources of project truth.

## Git Hygiene

The actual GGUF files belong under ignored paths such as `.local/models/` or `.runtime/models/`. Git should track only scripts, templates, checksums, manifests, and documentation.

## Expert Routing

For bounded multi-face research, the first round should use homogeneous analyst fan-out. Specialist roles such as architect or planner should be invoked after analyst fan-in shows an architecture or execution-ordering need.

If a specialist subagent does not complete, the leader must diagnose whether it is still working, blocked by startup, or suspected stalled before closing it. The leader must not silently skip that analysis step.
