## Design

The checker already separates skill inventory rows by source layer and already emits general plugin-bundle warnings. The bug is the same-layer duplicate loop: it treats every duplicate `(layer, name)` pair as an error unless a registry exception exists. That contradicts the policy for `plugin` rows, because plugin cache entries are vendor/bundle managed and repository changes must not edit them.

The implementation will add an explicit `layer == "plugin"` branch before the existing registry-exception/error logic:

1. If duplicate rows are in the `plugin` layer, emit a warning that the plugin duplicate is report-only until fine-grained plugin filtering exists.
2. If duplicate rows are in `repo` or `user`, keep the existing behavior: known registry exceptions become deferred cleanup; otherwise the duplicate is a blocking error.
3. Keep cross-layer user/plugin duplicates as warnings.

This keeps the guard strict for repository-owned and user-owned skill collisions while preventing plugin bundle artifacts from blocking unrelated repository publication.

## Safety

- The change is read-only with respect to `C:\Users\lenovo\.codex\skills`, plugin cache directories, and `C:\Users\lenovo\.codex\config.toml`.
- It does not suppress all skills governance errors; it only downgrades same-layer `plugin` duplicates to warnings.
- It preserves the existing warning that plugin skills are bundle-managed until filtering exists.

## Validation

Validation focuses on policy classification rather than live plugin mutation:

- Add a unit test that creates a fake plugin cache with duplicate `Chrome` skill entries and verifies the checker exits successfully with warnings.
- Keep the existing same-layer repo duplicate failure test so repository-local duplicates remain blocking.
- Run OpenSpec validation, repository guard, local gate, and local MR review before publication.
