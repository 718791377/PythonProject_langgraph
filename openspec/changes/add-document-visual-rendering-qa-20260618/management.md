# Management: Add Document Visual Rendering QA

## Open

- [x] Value: enable honest visual QA evidence for document deliverables instead of silently downgrading when render dependencies are missing.
- [x] Success criteria: Stage A freezes the backend/evidence contract; Stage B implements runtime and tests from `D:\PythonProject_langgraph` without touching `D:\project`.
- [x] Constraints: local-only integration, no tracked third-party binaries, optional backends skip by default, strict backends fail when unavailable.

## Design

- [x] Delivery tailoring: two local-main packages, first plan freeze and then runtime implementation.
- [x] Risks/assumptions: `pdf2image` wraps Poppler for rendering on Windows; LibreOffice may be absent; tests must remain skip-safe.
- [x] Acceptance evidence path: OpenSpec validation, focused document-tool tests, local gate, local MR review, and local-main helper evidence.

## Build

- [x] Execution mode for Stage A: isolated worktree and leader-owned local integration.
- [x] Quality evidence for Stage A: this management checklist plus proposal/design/tasks/spec/plan artifacts.
- [x] Blocker decision: durable team launch waits until the Stage A frozen plan is integrated and Stage B opens 2+ implementation slices.

## Verify

- [ ] Variance review after Stage A validation.
- [ ] Risk/change impact review after Stage A validation.
- [ ] Control decision after Stage A validation.

## Archive

- [ ] Value outcome recorded after Stage B runtime work.
- [ ] Lessons learned recorded after Stage B runtime work.
- [ ] Archive/sync evidence recorded after Stage B runtime work.

## Monitoring

- [x] Current facts: Poppler `pdftoppm` is present in ignored `.local`; `pdf2image` belongs in `.venv`; LibreOffice belongs under the Windows program installation path.
- [x] Return/no-return decision for Stage A: continue to local validation and local-main integration; no return loop needed.
