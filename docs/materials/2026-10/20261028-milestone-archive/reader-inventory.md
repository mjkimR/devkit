# Milestone archive reader inventory

Source snapshot: `982b9c1f` on the Planning branch; product base `b17db06f`. Scout was read-only, with equal
before/after tree `dbf30cbae3c5edfdfcbe94b95d75e4188fbf1be9` and unchanged HEAD. Codex emulated boundaries use
absolute cwd/read scope, no role writes and snapshots; there is no native isolation guarantee.

| Consumer | Current behavior and evidence | Required archive work / verification |
| --- | --- | --- |
| Document index | `packages/devkit-docs/src/devkit_docs/features/documents/repositories/index.py:123-152,220-260,309-319`: nested Markdown; history by status, canonical aliases and refs | Preserve indexing/history semantics; cover done, dropped, aliases and invalid active placement. |
| Global convention | `packages/devkit-docs/src/devkit_docs/features/governance/usecases/id_convention.py:368-405`: root-only three-part path | Allow only reserved flat archive; validate status/location without moves/state mutation; retain namespace rejection and explicit historical checks. |
| Kind table | `packages/devkit-docs/src/devkit_docs/features/documents/models/kinds.py:285-299`: milestone global format scope | Keep same kind and status model; verify recursive format selection, no new kind/registry. |
| Proposal membership | `packages/devkit-spec/src/devkit_spec/features/proposals/usecases/roadmap.py:11-28`: canonical ID/alias then exact root path | Permit either supported canonical location, keep inactive notice; `tests/integration/features/proposals/test_roadmap.py:115-167`. |
| Readiness | `ADR-roadmap-and-milestones`; spec-next `references/next-work.md:6-11`; viewer `frontend/src/lib/api/roadmap.ts:35-37,101-113` | done and dropped already satisfy; resolve whole set before display filters. Add isolated dropped-edge coverage. |
| Dashboard backend | viewer `features/browse/repositories/worktree.py:145-182`: direct roadmap list + root regex | Add archive candidate directory; retain frontmatter-only selective reads and paging contract. |
| Dashboard frontend | viewer `frontend/src/lib/features/dashboard/loading.ts:29-40,94-113`: root-only filter | Cover optimized dashboardList and generic tree fallback; keep counts/cache/history semantics. |
| Dashboard classification | viewer `frontend/src/lib/features/dashboard/dashboard.ts:109,229-230`: post-load root-only predicate and derived counts | Accept reserved archive paths after either loader; focused archived done/dropped extraction fixture must increase totalCount but not openCount. Challenger identified this separate consumer. |
| Roadmap frontend | viewer `frontend/src/lib/api/roadmap.ts:132-150`: root-only listing | Read the reserved archive too; preserve dependencies and detail/deep links. |
| Generic file/detail reads | viewer `features/browse/repositories/worktree.py:40-112`: arbitrary safe nested path, tree/blob | No new path restriction needed; actual bounded probe read an archive file successfully. Keep navigation coverage. |
| Lifecycle guidance | source spec skills `references/backlog.md.jinja`, `milestone-completion.md`, `roadmap-catalog.md`; docs template `templates/milestone.md` | Add close/drop/reopen storage movement, partial historical merge and exact reviewed batch procedure. |

## Bounded current-behavior probe

The authored probe stays in ignored `materials/.probe/archive_readers.py`. It creates only synthetic files beneath
that ignored location; no real roadmap file moved. Current result:

```text
archived done: indexed=true, historical=true, alias resolves=true, proposal membership=ARGUMENT_INVALID
archived dropped: indexed=true, historical=true, alias resolves=true, proposal membership=ARGUMENT_INVALID
archived active: indexed=true, historical=false, proposal membership=ARGUMENT_INVALID
nested viewer tree files=3; nested archive blob read=true
```

This confirms existing index/detail reuse and the authoring path gap. It does not claim an archive implementation,
frontend execution or rule acceptance. Development must exercise invalid-placement reporting and all reader paths.

## Scope and relocation notes

The current supported milestone scope is global; namespaces stay unsupported. No CLI-refactor prerequisite appeared
in the inspected owners. There is no archive directory yet. The terminal set is four done files, zero dropped; exact
source/destination/bytes/SHA256 are in relocation-candidates.json. The checksum is review evidence, not an authority token.
An exact-path search found only a historical feedback code fence naming the maintenance milestone's former observation
path (`specs/2026-10/20261028-performance-pass/feedback/proposal-new-accepts-a-done-milestone.md:48`), not a live Markdown
file link. Preserve that evidence. ID references and historical completed specs need no rewrite for a pure move.
