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

Initial verification: backend discovery/worktree 33 passed; frontend 130 passed; Python Ruff/Pyright and frontend
lint/check passed. The committed page was rebuilt successfully. Final selector, generated artifact and independent
review evidence is recorded in the unit envelopes.

The available Node runtime is v22.22.0; npm reports an engine warning because the package declares v22.22.2 or a
supported newer major. The recorded frontend checks/build ran successfully on v22.22.0. Other Node versions were
not separately exercised, and no dependency or engine declaration was changed.
