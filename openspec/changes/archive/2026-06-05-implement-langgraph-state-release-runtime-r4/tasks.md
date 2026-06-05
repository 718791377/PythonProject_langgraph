# Tasks

## 1. OpenSpec package

- [x] 1.1 Create the bounded R4 OpenSpec change package.
- [x] 1.2 Record scope, non-goals, validation path, and archive deferral.

## 2. Runtime implementation

- [x] 2.1 Add release receipt path helpers under repo-local `.omx/state/langgraph/store/releases/`.
- [x] 2.2 Add a `release-thread` CLI command for `close`, `release`, and `handoff`.
- [x] 2.3 Update thread state, backend projection, status output, and inspect output with release receipt evidence.
- [x] 2.4 Preserve rollback/restore note, redaction status, survivor queue status, checkpoint path, artifact path, handoff target, and timeout release fields.

## 3. Tests and plan updates

- [x] 3.1 Add failing runtime tests before implementation.
- [x] 3.2 Add runtime release-helper coverage to the existing CI-managed state-release test module.
- [x] 3.3 Update the bilingual implementation plan status and evidence index.

## 4. Validation and archive package

- [x] 4.1 Run targeted state-release runtime tests.
- [x] 4.2 Run durable artifact state-release checker tests.
- [x] 4.3 Run OpenSpec validation and repository guard before archive.
- [x] 4.4 Archive this change and promote the release-runtime requirement into the stable spec before local main integration.
- [x] 4.5 Preserve the local-main-first publication boundary: guarded local integration continues after archive and commit; remote publication remains unauthorized.
