# Pytest runner assessment

## 1. Inspect configuration and isolation

Record installed pytest/plugin versions and exact native commands. Read collection hooks, `testpaths`, markers,
async fixture lifetimes and collection-time effects before invoking pytest. Preserve consumer marker spelling;
path-derived markers are an ownership convention, not proof of purity or network independence.

Inspect worker/run ownership of database names, file paths, ports and environment inputs. Session fixtures may
execute per worker. Keep shared-database serial guards and disposable-resource validation. Worker caps do not
establish isolation; do not copy application-specific environment stripping or database fixtures.
Use the installed version's help/documentation before proposing flags. Official references:
[distribution](https://pytest-xdist.readthedocs.io/en/stable/distribution.html) and
[worker/run identity and fixture scope](https://pytest-xdist.readthedocs.io/en/stable/how-to.html).

## 2. Optional tuning comparison

1. Keep one revision, lockfile, environment and selected test set. Record machine limits and exact commands.
2. Compare serial with the existing parallel candidate using one warmup and three interleaved timed repetitions
   per variant. Keep the machine otherwise idle; label cache state and failures. This is a local runner comparison,
   not a universal performance guarantee or a replacement for a separately selected performance-pass contract.
3. Compare collected node-ID multisets, outcomes, optional skips, setup/teardown failures and cleanup as well as
   elapsed time. Counts alone do not prove equal coverage. Inspect collection code before collecting identities.
4. Retain current settings when results are incomplete, noisy or slower; record `not_run` for missing evidence.
   Promote no default until coverage and isolation are preserved and the named metric improves.

For example, a serial command and an eight-worker candidate with different skip sets are not equivalent even if
both exit successfully and the candidate is faster. Report the mismatch and propose no promotion.
Do not prescribe a worker count, scheduler, fixture scope or two-/fifteen-second cutoff for all consumers.
