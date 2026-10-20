# Registry access comparison

## Evidence and choice

`scope/localfs.py` routes query and history through `_locked`: directory creation, exclusive lock and temp cleanup.
`scope/location.py` also removes old token temporaries from `load_token`. The query CLI uses ownership lookup before
rendering records. Atomic record replacement alone cannot provide a coherent multi-record read without locking.

| Direction | Discovery and identity | Permissions and lifecycle | Outcome |
| --- | --- | --- | --- |
| Git common directory plus scoped approvals | Linked worktrees share resolved common-dir path; separate clones normally differ | Namespace and per-worktree token writes remain explicit; no daemon | Recommended with read-only queries |
| Shared `.devkit/state/` | Existing absolute shared_path can select it; each checkout's own .devkit is insufficient | Shared path must be allowed from every worker; tokens still in Git unless redesigned; exact runtime ignore rules needed | No demonstrated advantage sufficient to justify relocation |
| MCP service | Needs explicit repository identity and bounded operations | Server filesystem authority, tool authorization, token custody, startup, crash recovery and unavailable-service behavior required | Not selected; runtime feasibility unverified |

The default namespace hashes the absolute common directory. Moving it changes default identity; deleting the base
Git administration can break linked worktrees. Preserve that existing limitation, do not promise move-stable
identity. Explicit shared_path and namespace can retain registry identity, but do not repair missing Git metadata.
An unrelated clone shares nothing by default; explicit identical overrides intentionally share state.

## Query alternatives

A lock-free per-record scan prevents torn individual JSON through atomic replacement but permits mixed generations,
missing newly registered records and concurrent release gaps. A separately maintained snapshot adds writer publication
and recovery complexity. Read-opening the existing lock and taking shared flock preserves writer exclusion without
filesystem writes. Missing lock files must not be created or treated as evidence of no records.

## Development verification map

- V1: Extend scope location/flow fixtures with base plus two linked worktrees and unrelated clone; compare resolved
  shared paths/namespaces and mutually visible registrations, revisions and overlaps.
- V2: Run record and history queries with writable opens, mkdir, unlink and mutation helpers instrumented to fail.
  Include own-token lookup, old token and record temporaries, configured external shared_path and denied reads.
  Verify mutation errors remain explicit under denied write access. Check Linux and macOS read-only-fd flock
  compatibility; an actual sandbox smoke verifies the host separately, without implying approval on other hosts.
- V3: Assert absent query creates nothing; missing, symlink and nonregular locks (including nonblocking FIFO rejection) fail; timeout/unsupported-lock
  errors persist. Use process barriers: hold writer lock while querying, confirm waiting then coherent results;
  hold reader lock while update/register/release runs, confirm writer waits. Include history append contention,
  unreadable record warnings and corrupt journal lines. Compare namespace and token-tree bytes and directory entries
  before/after queries; instrument syscalls as well so suppressed write failures cannot pass unnoticed.
- V4: Retain ownership, stale revision, atomic interruption, restart and stale sweep regression tests. Confirm only
  mutating paths clean interrupted temporaries and missing tokens remain missing after queries.
- V5: Neither MCP nor relocation is selected; no transport or path migration acceptance checks apply.

Run relevant scope tests, lint/type checks and just test-affected during Development. This Planning turn performs
source/contract analysis and document validation; it does not claim a prototype, sandbox matrix or production tests.
