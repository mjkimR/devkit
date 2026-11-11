---
sources:
  ADR-worktrees-and-scope: 15b1f634c021a28952c5257a3e6e5795b8b0259d
  CAP-COLL-shared-artifacts: 092d06230b033004a559d4fa72907fac6d0e0f5d
  CAP-COLL-work-scope-registry: a2dea3a64550dfad9c3225650fbf433174d56773
  CAP-DLV-project-policy: 69045e11fa4d0e8998f0b1ac44a30b403ab93425
  CAP-MCP-runtime-registration: fa73a69e865c0b0e356d968a9d393df58e819942
  CAP-TRACE-code-entrypoints: f85e685d002096791b5d75d3954edc3782f59f9b
  CAP-WT-task-worktrees: 2f5c45415f121e1d1d47046f255be4d4163e24dc
  UC-run-parallel-work-safely: 0d974e0c636645b44666c8442980b3c83f3bdf72
title: Collaboration
---

# Collaboration

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.6` at source commit `f115e96c8059`, generated 2026-11-11. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Adopt SDD from adaptive development](../journeys/adopt-sdd-from-adaptive-development.md)
- [Advance an idea](../journeys/advance-an-idea.md)
- [Assess a selected test suite](../journeys/assess-test-management.md)
- [Design necessary command entry points](../journeys/design-command-entrypoints.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Execute an isolated command](../journeys/execute-an-isolated-command.md)
- [Explore a design problem](../journeys/explore-a-design-problem.md)
- [Find the latest maintenance run](../journeys/find-the-latest-maintenance-run.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Import selected third-party agent assets](../journeys/import-third-party-agent-assets.md)
- [Improve an interface and user flow](../journeys/improve-an-interface-and-user-flow.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Plan and hand off a proposal](../journeys/plan-and-hand-off-a-proposal.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Read decision supersession](../journeys/read-decision-supersession.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Record a maintenance run](../journeys/record-a-maintenance-run.md)
- [Research an idea and shape a roadmap](../journeys/research-an-idea-and-shape-a-roadmap.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Adopt and refresh bundle sources locally](../journeys/snapshot-bundle-sources.md)
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

Both are discovered through the repository's common Git identity, so every [task worktree](worktree.md) shares them without
configuration. The end-to-end story is the journey [Run parallel work safely](../journeys/run-parallel-work-safely.md)
(`UC-run-parallel-work-safely`); the terms used here (worktree, spec bundle, proposal) are explained in
[Concepts](../concepts.md).

## Compare declared scopes

Run `uv run devkit spec scope collect` after tasks have a `plan-*` or `dev-*` activity source. It compares declared and observed paths, reports each overlap and unresolved input, and preserves declaration disagreements rather than merging them. Queued drafts without an activity source are excluded. The result informs scheduling and grants no write authority.

## Observe running work

Once tasks run, the orchestrating Host observes them when it needs evidence for scheduling or integration order.
Workers have nothing to publish: they register no scope, send no updates and acknowledge nothing. One command
collects what the Host can see, read-only:

```sh
devkit spec scope collect [--base <ref>] [--fetch <remote>]
```

- **Collection.** One invocation reads creation snapshots, activity refs and accessible worktrees together. Drafts without a `plan-*` or `dev-*` source are excluded.
- **Network is opt-in.** Without `--fetch`, remote refs are whatever was last fetched. `--fetch <remote>` (repeatable,
  configured remotes only) refreshes just their remote-tracking branches. Another machine's unpushed work is never
  visible; for frequent multi-PC work, push declarations and changes through pull requests.
- **Gaps stay visible.** A missing base, an ambiguous task identity, an unreadable or changing source, or an exhausted
  time budget (`--timeout`, `--source-timeout`) leaves the usable evidence in place and reports
  `SPEC_SCOPE_COLLECTION_PARTIAL` with the missing coverage; uncomputed pairs never count as zero overlap. Only when
  no inventory source can be read at all does it fail with `SPEC_SCOPE_COLLECTION_FAILED`.

The output lists the candidates (`[SCOPE_CANDIDATE: ...]`), each observation and pairwise `[PAIR: ...]` and
`[EVIDENCE: ...]` lines, ending with a summary that says whether coverage and comparisons are complete.

### The shared registry

The registry holds a snapshot of each task's scope, shared by every worktree of the repository. Snapshots are taken
automatically when `devkit spec proposal handoff` or `devkit spec new` creates a unit in a linked worktree; this is
best effort, and a failure never affects the creation. `collect` reads these snapshots; they can lag behind the
worktree. You rarely need the registry commands directly:

| You want to | Run |
| --- | --- |
| Withdraw an abandoned task | `devkit spec scope release` |
| Remove records whose worktree is gone | `devkit spec scope sweep --apply` |

A few behaviours are worth knowing:

- One worktree holds one token. A second registration from the same worktree is refused
  (`SPEC_SCOPE_TOKEN_EXISTS`), so a record is never orphaned.
- Queries and `collect` are side-effect free: they create no directory, lock or file and never touch owner tokens.
  An empty or partly readable answer is not proof that nothing overlaps.
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

## Current and future overlap

`scope collect` labels each evidence entry `horizon=current|future` and reports pair counts plus
`summary.current_overlapping`. Observed Planning writes are current; its declared document/code/candidate scope is future.
Other observations are current. All overlaps stay listed, and horizon grants no write authority.
Current overlaps serialize running activities; future-only overlaps order handoff and integration while Planning can proceed independently.
Missing inputs, including lifecycle-normal absent blueprints or reconcile files, remain explicit coverage gaps.

Scope records live in the Git common directory; shared reports live under the retained main checkout's
`.devkit/.shared/artifacts`. The common Git identity lets linked worktrees find the same store.
Local-orchestrated callers verify connected project tools before dependent shared operations; a missing connection
needs repair rather than an automatic CLI fallback. An explicitly authorized CLI choice remains possible.

## Sources

- [CAP-COLL-work-scope-registry](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/collaboration/CAP-COLL-work-scope-registry.md):
  scope inputs, comparison, registry, commands, output and codes.
- [CAP-COLL-shared-artifacts](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/capabilities/collaboration/CAP-COLL-shared-artifacts.md):
  artifact identity, retention, storage and adapter extensions.
- [UC-run-parallel-work-safely](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/usecases/collaboration/UC-run-parallel-work-safely.md):
  the parallel-work scenario.
- [ADR-worktrees-and-scope](https://github.com/mjkimR/devkit/blob/v0.1.6/docs/decisions/2026-11/20261102-worktrees-and-scope.md):
  why the Host observes and workers publish nothing.
- Related: [Worktree](worktree.md) (`CAP-WT-task-worktrees`), [MCP](mcp.md).
