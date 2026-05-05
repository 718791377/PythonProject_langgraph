# Formalize Shared Local Model Assets Migration

## Why

The personal production durable-team plan needs an executable migration path for local llama and GGUF model assets. The operator wants `Qwen3.5-9B-Q4_K_M-GGUF` and `jina-embeddings-v5-text-small-retrieval-GGUF` to be centrally managed under `D:\PythonProject_langgraph` while still allowing OpenClaw to start or call the same local model services through controlled provider profiles.

## What Changes

- Add a bilingual shared local model assets migration plan.
- Add a bilingual local model provider policy.
- Add a bilingual production durable-team playbook that turns the draft target into implementation slices.
- Update the draft production durable-team plan to point to the migration plan, provider policy, and playbook.
- Update the active team-mode plan with expert fan-out and stalled-subagent handling rules.
- Register the new bilingual documents.

## Non-Goals

- Do not move real GGUF model files.
- Do not start a model server.
- Do not modify `D:\PythonProject_OpenClaw`.
- Do not modify `C:\Users\lenovo\.codex\config.toml`.
- Do not write project durable state under `.omx/state/`.
- Do not make any local model provider an approval authority or durable truth source.
