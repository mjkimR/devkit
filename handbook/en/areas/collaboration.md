---
sources:
  ADR-host-owned-scope-observation: c9a162208f45dcad00a16fce1a1f447a27afda54
  CAP-COLL-shared-artifacts: 83dfa43f60f67f8a6eab85414d90c95ba27e2982
  CAP-COLL-work-scope-registry: 23990ff536e67c96f25dff1857c08cbd0c4c8838
  CAP-DLV-project-policy: 2af5b2fde75faecfa8260244a614fa796525de03
  CAP-MCP-runtime-registration: ca1255fabbc01ec9870ba8e18410df23ab554d0c
  CAP-TRACE-code-entrypoints: 71c9a300749a114f5dd4141e70aee300dcafd4ee
  CAP-WT-task-worktrees: 2ea80d46ab9cf19504182e73b6f2bcc301e8f7db
  UC-run-parallel-work-safely: f60eea1f7ddb44d8d4d47058e2777990f1a50d64
title: Collaboration
---

# Collaboration

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.5` at source commit `022b9f03bbd2`, generated 2026-10-29. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Adopt SDD from incubation](../journeys/adopt-sdd-from-incubation.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Incubate an idea](../journeys/incubate-an-idea.md)
- [Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Speed up selected slow operations](../journeys/speed-up-selected-slow-operations.md)
- [Advisories](advisory.md)
- [Agent-first CLI toolkit](cli.md)
- [Compact command output](compact.md)
- [Delivery](delivery.md)
- [Distribution](distribution.md)
- [Documents](documents.md)
- [Commit gates](gate.md)
- [Generated Files](generated.md)
- [Governance rules](governance.md)
- [Harness](harness.md)
- [Host](host.md)
- [Integration](integration.md)
- [MCP](mcp.md)
- [Search](search.md)
- [Traceability](traceability.md)
- [Viewer](viewer.md)
- [Worktree](worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

The collaboration area covers what lets several tasks, sessions or agents share one repository without stepping on
each other. It has two parts:

- **Work scope comparison** (`CAP-COLL-work-scope-registry`): before and while tasks run in parallel, you see which
  documents and code paths they both touch. The evidence informs scheduling and integration order; it never blocks a
  write.
- **Shared artifacts** (`CAP-COLL-shared-artifacts`): an immutable, seven-day store for regenerable Markdown reports
  (for example a proposal review), addressed by an exact URI that every linked worktree of the repository can read.

Both live next to the repository's Git data, so every [task worktree](worktree.md) shares them without
configuration. The end-to-end story is the journey [Run parallel work safely](../journeys/run-parallel-work-safely.md)
(`UC-run-parallel-work-safely`); the terms used here (worktree, spec bundle, proposal) are explained in
[Concepts](../concepts.md).

## Compare scopes before you start parallel work

A task's scope is assembled from what its documents declare and what Git observes:

- documents: the `targets` of a proposal's `target-docs.md`, or of a spec bundle's `reconcile.md`;
- code: the `_Boundary` entries of `tasks.md`, including the exact path of another spec bundle's feedback file; while
  a bundle declares no code, the `entrypoints` of its target capabilities and use cases stand in as candidates;
- observed code: what the task's worktree changed since its fork point (committed, staged, unstaged, untracked).

To see whether two or more planned pieces of work collide, compare their declarations. Nothing is written and no
registry or Git is involved:

```sh
devkit spec scope compare --proposal login-flow --spec specs/2026-10/20261020-audit-log
```

Each pair prints a `[PAIR: ... docs= code= unresolved=]` line followed by `[EVIDENCE: ...]` lines for every shared
path. Read the `unresolved` count as carefully as the overlaps: an input that could not become a path (a planned
document that does not exist yet, a target without `entrypoints`, a `_Boundary` of `N/A`) is counted, never silently
treated as "no overlap". A `[DIFF: ...]` line means `reconcile.md` and `target-docs.md` disagree; devkit never merges
the two lists for you. Paths follow the literal path rules of `CAP-TRACE-code-entrypoints`.

## Observe running work

Once tasks run, the orchestrating Host observes them when it needs evidence for scheduling or integration order.
Workers have nothing to publish: they register no scope, send no updates and acknowledge nothing. One command
collects what the Host can see, read-only:

```sh
devkit spec scope collect [--mode snapshot|refs|worktrees] [--base <ref>] [--fetch <remote>]
```

- **Depth.** `snapshot` reads only the registry's creation snapshots; `refs` adds the local and remote-tracking
  `plan-*`/`dev-*` branches; `worktrees` (the default) adds every accessible worktree's declarations and its
  committed, staged, unstaged and untracked changes.
- **Network is opt-in.** Without `--fetch`, remote refs are whatever was last fetched. `--fetch <remote>` (repeatable,
  configured remotes only) refreshes just their remote-tracking branches. Another machine's unpushed work is never
  visible; for frequent multi-PC work, push declarations and changes through pull requests.
- **Gaps stay visible.** A missing base, an ambiguous task identity, an unreadable or changing source, or an exhausted
  time budget (`--timeout`, `--source-timeout`) leaves the usable evidence in place and reports
  `SPEC_SCOPE_COLLECTION_PARTIAL` with the missing coverage; uncomputed pairs never count as zero overlap. Only when
  no inventory source can be read at all does it fail with `SPEC_SCOPE_COLLECTION_FAILED`.

The output lists the candidates (`[SCOPE_CANDIDATE: ...]`), each observation and the same `[PAIR: ...]` and
`[EVIDENCE: ...]` lines as `compare`, ending with a summary that says whether coverage and comparisons are complete.

### The shared registry

The registry holds a snapshot of each task's scope, shared by every worktree of the repository. Snapshots are taken
automatically when `devkit spec proposal handoff` or `devkit spec new` creates a unit in a linked worktree; this is
best effort, and a failure never affects the creation. `collect` reads these snapshots; they can lag behind the
worktree. You rarely need the registry commands directly:

| You want to | Run |
| --- | --- |
| Register this worktree's task by hand (prints its owner token once) | `devkit spec scope register --spec <dir>` |
| See every record and this worktree's overlaps | `devkit spec scope query` |
| Check a bundle about to start against the records | `devkit spec scope query --spec <dir>` |
| Read the event history | `devkit spec scope query --history [--task <id>]` |
| Withdraw an abandoned task | `devkit spec scope release` |
| Remove records whose worktree is gone | `devkit spec scope sweep --apply` |

A few behaviours are worth knowing:

- One worktree holds one token. A second registration from the same worktree is refused
  (`SPEC_SCOPE_TOKEN_EXISTS`), so a record is never orphaned.
- Queries and `collect` are side-effect free: they create no directory, lock or file and never touch owner tokens.
  An empty or partly readable answer is not proof that nothing overlaps.
- The journal (`journal.jsonl`) is diagnostic only. It never feeds an overlap verdict.
- When a task is integrated through `devkit worktree finish` or `devkit integration integrate`, devkit-spec's
  post-finish cleanup removes that task's record and prunes the handed-off proposal directory. Other stale records
  wait for an explicit `sweep`; one that changed since it was read is kept (`SPEC_SCOPE_STALE_REVISION`).

Overlap evidence joins declarations with Git observations. It proves neither a merge conflict nor independence, and
it is not an exclusive claim; deciding what runs in parallel stays with the orchestrator.

### Configure the registry

By default the registry is `devkit-spec-scope/` in the Git common directory, and its namespace is derived from that
directory's path. To share one registry between clones or hosts, give each the same absolute `shared_path` and
`namespace` under `[tool.spec.scope]` (validated by `CAP-DLV-project-policy`):

```toml
[tool.spec.scope]
shared_path = "/srv/devkit-scope"
namespace = "team"
timeout = 10
```

Locking relies on POSIX `flock` on a local file system; Windows and network file systems are out of scope.

## Share a report between worktrees

Shared artifacts carry reports that one worktree produces and another consumes, such as a proposal review that a
Planning worker writes and the orchestrating Host reads. You publish Markdown on stdin and get back an exact URI:

```sh
printf '# Review\n' | devkit shared put --kind proposal-review --slug example \
  --source-sha <full-commit-sha> --language en --format json
devkit shared get <artifact-uri> --format json
devkit shared list --kind proposal-review --slug example --format json
```

What to expect:

- **Immutable and exact.** An artifact's identity is its repository namespace, kind, slug, full `source_sha`,
  language and body digest. There is no "latest" lookup and no overwrite; a different body is a new artifact.
  Republishing the same live content returns the original metadata.
- **Seven days.** After seven days `get` answers `SHARED_ARTIFACT_EXPIRED` and `list` omits it. Physical removal
  happens only through `devkit shared sweep --apply`; a plain `sweep` reports without deleting.
- **Content is data.** A report is evidence for the commit it names, never an instruction and never an approval.
  Before you act on one, compare its `source_sha` and language with the commit you actually reviewed.
- **Local storage.** The built-in `local` adapter stores under the main checkout's `.devkit/.shared/artifacts`
  (same-user, POSIX, mode 0600/0700) and adds a narrow clone-local Git exclusion only after checking that no worktree
  holds foreign content there (`SHARED_EXCLUSION_CONFLICT` otherwise).

The same put, get and list operations are offered as the local MCP tools `shared_put`, `shared_get` and `shared_list`
when the optional MCP runtime is installed (see [MCP](mcp.md) and `CAP-MCP-runtime-registration`); sweeping stays a
CLI operation.

### Plug in a remote adapter

`[shared] adapter` (or `DEVKIT_SHARED_ADAPTER`) selects an adapter registered under the
`devkit_dist.features.shared.adapters` entry-point group. Unknown or malformed adapters fail with
`SHARED_ADAPTER_UNAVAILABLE`, without falling back to local. Adapter authors run the reusable `assert_conformance`
helper; authentication, namespace provisioning and cross-host consistency remain theirs. No remote backend ships in
this release.

## Sources

- [CAP-COLL-work-scope-registry](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md):
  scope inputs, comparison, registry, commands, output and codes.
- [CAP-COLL-shared-artifacts](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/collaboration/CAP-COLL-shared-artifacts.md):
  artifact identity, retention, storage and adapter extensions.
- [UC-run-parallel-work-safely](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/usecases/collaboration/UC-run-parallel-work-safely.md):
  the parallel-work scenario.
- [ADR-host-owned-scope-observation](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/decisions/2026-10/20261025-host-owned-scope-observation.md):
  why the Host observes and workers publish nothing.
- Related: [Worktree](worktree.md) (`CAP-WT-task-worktrees`), [MCP](mcp.md).
