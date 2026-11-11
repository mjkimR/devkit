# Pytest runner assessment

## 1. Inspect configuration and isolation

- Record installed pytest/plugin versions and exact native commands. Read collection hooks, `testpaths`, markers,
  async fixture lifetimes and collection-time effects before invoking pytest.
- Preserve consumer marker spelling; path-derived markers are an ownership convention, not proof of purity or
  network independence.
- Inspect worker and run ownership of database names, file paths, ports and environment inputs; session fixtures
  may execute per worker. Keep shared-database serial guards and disposable-resource validation. Do not copy
  application-specific environment stripping or database fixtures.
- Worker caps establish no isolation and do not bound the cost of several overlapping runs: check run namespaces as
  well as worker namespaces before overlapping execution.
- Read the installed version's help/documentation before proposing flags. Official references:
  [distribution](https://pytest-xdist.readthedocs.io/en/stable/distribution.html) and
  [worker/run identity and fixture scope](https://pytest-xdist.readthedocs.io/en/stable/how-to.html).

## 2. Optional tuning comparison

This is a local within-run worker comparison, not a universal performance guarantee, a performance-pass contract or
a comparison of overlapping verification runs.

1. Keep one revision, lockfile, environment and selected test set. Record machine limits and exact commands.
2. Compare serial with the existing parallel candidate using one warmup and three interleaved timed repetitions
   per variant. Keep the machine otherwise idle; label cache state and failures.
3. Inspect collection code before collecting identities. Compare collected node-ID multisets, outcomes, optional
   skips, setup/teardown failures and cleanup as well as elapsed time, setup cost and resource contention; counts
   alone do not prove equal coverage.
4. Retain current settings when results are incomplete, noisy or slower. Promote no default until coverage and
   isolation are preserved and the named metric improves.
5. Report Host blocking separately from native duration, run count and CPU; scheduling overlap alone proves no
   runner speedup.

Example: a serial command and an eight-worker candidate with different skip sets are not equivalent even if both
exit successfully and the candidate is faster; report the mismatch and propose no promotion. Prescribe no worker
count, scheduler, fixture scope or two-/fifteen-second cutoff for all consumers.
