# Read-access verification evidence

## Execution environment

- macOS Darwin 24.6.0, Python 3.12.8: scope suite executed against this worktree's source.
- Linux 6.10.14-linuxkit, local python:3.12-slim container, network disabled, read-only root, capabilities dropped:
  `flock_probe.py` passed on native Linux tmpfs. The probe tests O_RDONLY shared flock, independent-process
  exclusive-writer exclusion, simultaneous readers and close-based release. macOS passed the same probe.
- Docker Desktop host bind-mount execution failed writer exclusion; that shared filesystem is not evidence of
  supported local Linux filesystem behavior. No support is asserted for shared/virtualized mounts with broken
  flock semantics. Native Linux tmpfs was used to verify Linux kernel behavior.

## Sandbox smoke

The initialized registry uses the retained Git common directory; owner tokens remain in worktree Git metadata.
All three commands below ran with the default sandbox and no escalation, exit 0, with no notices:

- `uv run --no-sync devkit spec scope query --format json`
- `uv run --no-sync devkit spec scope query --spec specs/2026-10/20261020-scope-registry-sandbox-access --format json`
- `uv run --no-sync devkit spec scope query --history --format json`

The record query found this unit at revision 2; history reported 72 events and zero problems. Setup/scope updates
used separate scoped escalation. This demonstrates this host's read behavior, not mutation authority or universal
sandbox compatibility. Syscall guards separately reject writable opens (except subprocess /dev/null descriptors),
creation, mkdir, unlink, rename and replace; before/after record and journal byte snapshots and old token fixtures
cover suppressed-cleanup attempts too.

## Automated verification

Scope tests cover absent namespaces, existing namespaces without locks, namespace/lock permission errors,
symlink/directory/FIFO locks, deadline errors, shared readers excluding registration/update/release/history append,
reader cleanup after exceptions, all CLI query variants with and without registration, interrupted record/token
files, and existing ownership, revisions, stale sweep, journal corruption and linked-worktree behavior.
Fixture roots stay under the worktree's ignored `.pytest_cache`; `GIT_CEILING_DIRECTORIES` stops deliberately
non-repository fixture directories from inheriting the enclosing worktree's Git identity.

The initial fixture run failed because the ignored parent did not exist; the next exposed fixture Git discovery
and subprocess /dev/null handling. Correcting test setup produced 101 passing scope tests before the final two
permission/unsupported cases were added. Package lint and Pyright passed (zero type errors/warnings).

Final build verification: `just test-affected --basetemp=<worktree>/.pytest_cache/affected` selected partial mode
against main and passed 1099 tests in 17.68s, including the added permission/unsupported cases.
