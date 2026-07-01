# Vector Tools Framework

Generic, config-driven local vector/retrieval helper framework. Consumer projects own data and filled configs.

## Smoke boundary

Repository smoke tests use temporary JSONL manifests to validate
`validate-manifest` and `query-jsonl`. They do not migrate live vector data.

Consumer projects keep their own manifests, LanceDB/SQLite stores, embedding
caches, source authority, and report/output roots. Use the tracked
`../config/vector_tools_config.example.json` as a template only.
