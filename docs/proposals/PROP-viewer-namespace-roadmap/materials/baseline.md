# Viewer namespace roadmap baseline

The fixture in `baseline.json` was executed at the recorded baseline head through the current
`WorkingTreeReader.dashboard_headers("milestones")`. Its files were saved beneath the ignored
`scratch/viewer-namespace-roadmap-baseline/` directory, without initializing or committing a Git repository.

The reader returned one global milestone and no errors. The namespace archived milestone was absent even though
its package is registered. The fixture's global milestone depends on the archived namespace milestone, and a
proposal names that namespace milestone. Source inspection of `api/roadmap.ts` shows that its global-only path
predicate and root discovery also omit the package file; graph/member consequences follow from filtering over
that loaded set. Frontend execution was not measured in this Planning probe.

Reproduce in the Development worktree by reading `fixture_files` from `baseline.json`, writing them beneath its
ignored scratch directory, constructing `WorkingTreeReader` at that fixture root and comparing the method's item
paths with `expected_after_candidate_paths`. Capture the current result before enabling the discovery change and
rerun afterward. Do not check out the base or treat this count as a performance benchmark.

## Required scenario extensions during Development

- Add another namespace root, reverse and package-to-package dependencies, unfinished and missing prerequisites.
- Cover the accepted registration policy with registered, unregistered, missing-config and malformed-config fixtures.
- Cover generic dashboard sources both with and without `treeRecursive`, optimized `dashboardList`, roadmap loading,
  flat-archive boundaries, symlinks, absent roots and per-root failures.
- Preserve page ordering/counts, six-request concurrency, cancellation, refresh/generation and cache-error behavior.

## Planning evidence boundaries

Only the baseline backend read was executed. Symlink/error/cancellation/frontend cases above are required
Development checks, not claimed Planning passes. No live browser, server socket, external request or timing probe
was used. No production source or current repository roadmap file was changed.
