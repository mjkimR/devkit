# Namespace roadmap implementation evidence

The baseline fixture was measured in the Development worktree before source edits, then measured again with the
same saved files and `WorkingTreeReader.dashboard_headers("milestones")`. No checkout or Git repository was needed.

| Measurement | Candidate paths | Errors |
| --- | --- | --- |
| Before | `docs/roadmap/MS-global.md` | none |
| After | `docs/packages/api/roadmap/_archive/MS-package.md`, `docs/roadmap/MS-global.md` | none |

This is an observed candidate-set change, not a timing benchmark. Frontend tests execute the equivalent global/two
package/config/archive matrix through generic dashboard and roadmap loaders; the optimized dashboard receives the
same structural namespace paths and preserves page-scoped body reads.

The implementation adds no namespace registry parser or `RepositoryDataSource` method. Frontend discovery retains
root metadata so the roadmap can distinguish absent proposal roots from a listed root that disappears. Generic
milestone bodies use at most six continuous workers. The Python reader and generic frontend both use shallow
metadata discovery rather than recursive scans of unrelated package documents.

Verification: backend discovery/worktree 33 passed; selector partial 14 paths, 165 tests passed, with full fallback
retained; frontend 130 passed. The exact selector-named frontend install/lint/check/test/pack/build chain passed.
Python Ruff/Pyright and frontend lint/check passed. The committed page was rebuilt, and generated viewer-assets
verification reported checked=1, stale=0 at implementation commit 91a77226. Independent review evidence is recorded
in the unit envelopes.

The available Node runtime is v22.22.0; npm reports an engine warning because the package declares v22.22.2 or a
supported newer major. The recorded frontend checks/build ran successfully on v22.22.0. Other Node versions were
not separately exercised, and no dependency or engine declaration was changed.

## Optional-root completion correction

Host completion review found that direct optional `tree("docs")` treated absence by HTTP404 text, although only
`blob` has that error-format contract. Two added regressions failed before the correction: absent docs with ENOENT
was reported as an error, while advertised docs disappearing with HTTP404 was hidden. Root metadata now establishes
absence, and every failed advertised-directory read remains an error. No host interface or error-text requirement
was added. Existing dashboard fixtures now expose their real root directory entries without weakening assertions.

The correction passed the complete frontend suite: 132 tests, lint and type checks, package generation and page
build. Python165 and focused33 results are reused because no Python source changed. Fresh review, generated-asset
and reconciliation evidence is recorded after this correction; earlier record history is retained.
