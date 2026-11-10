# Planning evidence for the assignment commands

Evidence and comparisons behind the settled design in `SPEC-adaptive-assignment-cli`. The four `scout` envelopes
(historical Git `f0434e6ed0c981340754256022750527f8887e7a:docs/proposals/PROP-adaptive-assignment-cli/envelopes/scout-01.yaml` to historical Git `f0434e6ed0c981340754256022750527f8887e7a:docs/proposals/PROP-adaptive-assignment-cli/envelopes/scout-04.yaml`) hold the findings; this file keeps the comparisons and the
probe results.

## 1. Evidence boundary

- Sections 2 to 8 are reads of this worktree at `67750e0596f0` (first Planning turn). Sections 9 to 13 are reads and
  one Git probe at `fe1f18852a9e` (second turn). Nothing was installed or built, and no test ran.
- The first turn's probe command was denied by the host permission system. The second turn ran the probe as single
  Git commands in a throwaway repository under the proposal's ignored `.probe/` path (Git 2.49.0, macOS). Section 9
  holds the results.
- `uv run devkit adaptive` in this worktree exits `2` with click's `No such command 'adaptive'` usage text and no
  advisory code (scout-02).
- `PROP-adaptive-package-extraction` is read as the draft in this worktree. Its Planning runs in another worktree
  that this unit's Planning does not read.

## 2. Git plumbing already used in the repository

| Need | Command in existing code | Location |
| --- | --- | --- |
| Committed changed paths | `git diff --no-renames --name-only -z <base> <head> --` | `packages/devkit-spec/src/devkit_spec/features/worker/usecases/inspect.py:178-184` |
| Uncommitted and untracked paths | `git --no-optional-locks status --porcelain=v1 -z --untracked-files=all`, reading the second record of a rename or copy entry | `inspect.py:125-142` |
| Ancestry | `git merge-base --is-ancestor <base> <head>`; exit `1` is "not an ancestor" | `packages/devkit-core/src/devkit_core/core/git.py:184-197` |
| Shared Git directory | `git rev-parse --path-format=absolute --git-common-dir` | `packages/devkit/src/devkit_agt/features/isolated_execution/repositories/runs.py:39`, `packages/devkit-dist/src/devkit_dist/features/project/repositories/invocation.py:34` |
| Worktree list | `git worktree list --porcelain -z` | `packages/devkit-spec/src/devkit_spec/features/scope/services/inventory.py:35-58`, `packages/devkit/src/devkit_agt/features/worktree/usecases/lifecycle.py:179-198` |

`--no-renames` makes a rename appear as one deleted and one added path, so both names are compared with the write
scope. `--untracked-files=all` lists each untracked file instead of its directory. Ignored files appear in neither
command.

The existing helpers differ on the base: `inspect.py` compares the two trees `<base> <head>`, the scope collector
compares from the merge base. With the ancestry check passing, both give the same paths, so the commands use the
two-tree form and run the ancestry check first.

## 3. Reuse by owning package (first turn)

Section 10 re-decides this table with `devkit_agt` and `devkit_docs` importable.

| Piece | Owner | Reachable without `devkit_agt` or `devkit_spec` |
| --- | --- | --- |
| `run_git`, `run_git_text`, `is_ancestor` | `devkit_core.core` | Yes |
| `file_lock` (`fcntl.flock`, bounded wait, `LOCK_HELD`) | `devkit_core.core` | Yes |
| `atomic_write_text`, `normalize_relpath`, `resolve_within` | `devkit_core.core` | Yes |
| Toplevel and common-directory lookup | `devkit_dist.features.project` public modules | Yes |
| `boundary`, `FORMAT_OPTION`, `echo_json`, `echo_notices`, `exit_on_warnings`, `field_value` | `devkit_dist.adapters.cli` | Yes |
| Changed-path collection, scope containment, head and ancestry checks of a worker | `devkit_spec.features.worker` | No: importing `devkit_spec` is excluded |
| Worktree list parser | private in `devkit_agt.features.worktree`, private in `devkit_spec.features.scope` | No public function in any package |
| Segment-aware `**` glob matcher `match_path` | `devkit_agt.features.rules.models.settings` (public) | Only with `devkit_agt` |
| Worktree lifecycle and isolated execution use cases | `devkit_agt.features.worktree`, `devkit_agt.features.isolated_execution` | Only with `devkit_agt`; the commands create no worktree and run no process |

What the commands need from Git is about five subprocess calls. Each is available through `devkit_core.core.run_git`.

## 4. Ledger location

| Option | Seen from every linked worktree | Tracked or shown by `git status` | Survives `git clean -fdx` | Host sandbox | Precedent |
| --- | --- | --- | --- | --- | --- |
| Tracked project file | No: each branch has its own copy until merged | Yes: every write dirties the Host checkout and enters the verification's own changed paths | Yes | Writable in the checkout | None for runtime state |
| `.devkit/transient/` of one checkout | No: the directory is per checkout and ignored; a lead in another worktree would need the main worktree resolved for it | No | No | Writable in that checkout only | Checkout-local state only (`CAP-DIST-workspace-ownership` §1, §2.8) |
| `<git common dir>/devkit/adaptive/` | Yes | No | Yes | Codex `workspace-write` treats shared Git as outside sandbox access and asks approval (`.devkit/managed/spec/subagents/planning-worker.md` step 5) | `devkit exec` runs (`<common>/devkit/executions`), the spec scope registry (`<common>/devkit-spec-scope`), the integration lock |

A tracked file also turns the ledger into a per-change record in history, which adaptive development excludes.

## 5. Ledger format

| Option | Partial write | History of transitions | Concurrency | Precedent |
| --- | --- | --- | --- | --- |
| One JSON document | Atomic replace of the whole board | Lost unless embedded | One lock; every write rewrites all assignments | None |
| One JSON file per assignment | Atomic replace per file | Lost unless embedded | Per-file writes, a lock for ID allocation and overlap checks | `devkit exec` run files |
| Append-only JSON Lines events | Only the last line can be torn; earlier events are never rewritten | Kept in order with timestamps | One lock around read, validate, append | The spec scope registry's `journal.jsonl` |

The overlap, narrowing and nesting checks read every open assignment before a write, so one lock around the whole
ledger is needed in each option. The event log adds the transition history that resume and a later hook consumer
read, at the cost of folding events into state on each read.

## 6. Write-scope semantics

| Option | Containment | Overlap of two scopes | Child within parent | Precedent |
| --- | --- | --- | --- | --- |
| Literal path prefix (a file, or a directory with its subtree) | Exact: equal, or under the entry plus `/` | Exact: one entry covers the other | Exact: a parent entry covers each child entry | `inspect.py:196-199`, `devkit_docs/utils/paths.py:28-39`; both reject glob characters |
| Globs with `*` and `**` | Exact with a segment-aware matcher | Needs a pattern-intersection decision, or a conservative literal-prefix comparison with false refusals | Same problem | `match_path`, owned by `devkit_agt` |

The bundle guidance names ownership as paths ("exclusive absolute ownership", "assigned product and test paths") and
uses no pattern. Literal prefixes keep the three decisions exact; adding globs later keeps every literal entry valid.

## 7. Base dependency of `devkit-adaptive` (first turn's comparison)

| Answer | Allows | Forbids or costs |
| --- | --- | --- |
| `devkit-dist` only | Installing the bundle and the commands without the harness; the commands on `devkit_core` and `devkit_dist` helpers; guidance that names `devkit worktree` only as the project's documented procedure when a harness is installed | Importing `devkit_agt` worktree, workflow or rules modules; a small worktree-list parser and a prefix matcher are written in the feature |
| `devkit-agt` | Importing public `devkit_agt` modules (`match_path`, the hex-validating `is_ancestor`) and declaring edges to `devkit_agt.features.worktree` | Installing the harness wheel with every adaptive installation; the orchestration reference's "without assuming a harness is installed" no longer describes the package; the adaptive test suite depends on `devkit-agt` |

The user chose neither option: `devkit-adaptive` requires `devkit-docs` (historical Git `f0434e6ed0c981340754256022750527f8887e7a:docs/proposals/PROP-adaptive-assignment-cli/envelopes/answer-01.yaml`, q1). Section 11
holds what follows from that requirement.

## 8. Contract statements that the commands touch

- `ADR-adaptive-development-and-research`: the decision clause "Identifiers and commands use `adaptive-dev`."
  (traced to rule 18). "No new runtime, CLI or distribution mechanism." (a driver of its deep-research part) and
  "Reuse distribution and projection mechanisms without another release wheel or runtime service." (a driver of its
  adaptive-dev bundle part) are decision drivers and are not superseded (challenger-01, finding 5). The outcome clause
  "Content-only catalog ownership, explicit installation, the shared approach check, independent docs/catalog
  installation, ..." holds the installation decision that section 11 changes.
- `CAP-DLV-adaptive-development` §2 Scope Excluded: "a runtime scheduler, agent bus, new wheel"; §4: "No
  adaptive-development runtime or CLI is added."; the final section: "No implicit Unit or verification ledger is
  created."; rule 18: "identifiers and commands MUST use `adaptive-dev`".
- `CAP-HARN-command-mount` §4.7: no `devkit spec` or `devkit docs` command reports a negative result. The statement
  names those two groups only; `ARCH-08-1-agent-output` §7 defines exit `1` for every command.

## 9. Git probe results (second turn)

One throwaway repository with a base commit, two linked worktrees and a bare clone with a linked worktree. Every
command ran as `git -C <dir> ...`.

| Question | Command | Observed |
| --- | --- | --- |
| Unborn repository | `rev-parse --verify -q "HEAD^{commit}"`; `worktree list --porcelain` | Exit `1`; the record reads `HEAD 0000000000000000000000000000000000000000` |
| Shared Git directory from a linked worktree | `rev-parse --path-format=absolute --git-common-dir` | The main repository's `.git`, the same value as from the main worktree |
| Committed rename from `src/a/x.py` to `other/x.py` | `diff --no-renames --name-only -z <base> HEAD --` | `other/x.py` and `src/a/x.py`; without `--no-renames` only `other/x.py` |
| Ancestry | `merge-base --is-ancestor` | Exit `0` for an ancestor, `1` for a non-ancestor, `128` for an unknown revision |
| Uncommitted rename, modification and untracked files | `--no-optional-locks status --porcelain=v1 -z --untracked-files=all` | ` M docs/d.md`, then `R  src/a/kept.py` followed by a separate record `src/a/keep.py` (new name first, old name second), then one `??` record per untracked file |
| Untracked nested repository | same | One record `?? nested/` with a trailing slash, also under `--untracked-files=all`; its files are not listed |
| Untracked directory under the default mode | `status --porcelain=v1 -z` | `?? new/` instead of `?? new/deep/u.txt` |
| Index write | SHA of `.git/index` around `status` after `touch` of a tracked file | Unchanged after `--no-optional-locks status`; changed after a plain `status` |
| A held `index.lock` in the worktree | `--no-optional-locks status`, `rev-parse HEAD`, two-tree `diff` | Each exits `0`; `git add` fails |
| A file written under `<common dir>/devkit/adaptive/` | `status` in the main and the linked worktree before and after | Identical output in both |
| A worktree whose directory is gone | `worktree list --porcelain -z`; `git -C <path> rev-parse HEAD` | The record stays, with `prunable gitdir file points to non-existent location`; the second command exits `128` |
| Revision resolution | `rev-parse --verify -q "<rev>^{commit}"` | The full ID for a branch; exit `1` for an unknown name and for a tree |
| Bare repository with a linked worktree | `rev-parse --show-toplevel`, `--git-common-dir`, `worktree list --porcelain -z` | In the linked worktree: its path, and the bare directory as the common directory. In the bare directory: exit `128`. The first list record is `worktree <bare dir>` and `bare`, without `HEAD` |

Consequences for the design:

- A missing worktree is a path whose directory does not exist or whose record carries `prunable`; absence from the
  list is not the test.
- The status parser strips a trailing `/` from a record, so a write entry covers an untracked nested repository by
  its directory name.
- Reading a worktree in which an assignee holds `index.lock` works with the commands of section 2.
- A linked worktree of a bare repository is supported; the bare directory itself is not a work tree.

Not probed: submodules, a repository with `GIT_DIR` or `GIT_WORK_TREE` set in the environment, a file system
without `fcntl` locks, and concurrent appends.

## 10. Reuse with `devkit_agt` and `devkit_docs` importable (second turn)

`RULE-architecture` admits a cross-package import when the target namespace is among the package's `dependencies`,
the target feature is in `feature_dependencies` of the importing feature, and the target module is the feature
facade or a `public_modules` entry (scout-03). Modules outside a feature skip the feature and public checks.

| Need | Candidate | Public | Decision |
| --- | --- | --- | --- |
| List worktrees with HEAD and prunable state | `devkit_agt.features.worktree.usecases.lifecycle._entries` | No: private function of a public module. `locate` and `find` are public, branch-based and resolve activity-branch paths only | Parser written in the feature |
| Same | `devkit_dist.features.shared.repositories.local.discover` | Yes, but it returns the main checkout and the common directory only and needs a checkout top level | Not used |
| Run Git | `devkit_core.core.run_git`, `run_git_text`, `is_ancestor` | Yes | Reused |
| Run Git without inherited `GIT_*` variables | `devkit_agt.features.worktree.repositories.execution.git` | Yes, but it raises `subprocess.CalledProcessError`, not an advisory | Not used |
| Resolve a revision to a full commit ID | none | No public function | `rev-parse --verify --quiet <rev>^{commit}` through `run_git_text` in the feature |
| Parse `git status` records | `devkit_agt.features.compact.services.porcelain.status_records` | No: `compact` has no public module | Parser written in the feature |
| Top level of the work tree | `devkit_dist.features.project.repositories.project.git_toplevel` | Yes | Reused |
| Shared Git directory | `devkit_dist.features.project.repositories.invocation.common_directory` | Yes, but its failure code is `MCP_WORKSPACE_UNAVAILABLE` | `rev-parse --path-format=absolute --git-common-dir` through `run_git_text` in the feature |
| Literal path containment and overlap | `devkit_docs.utils.paths.covers`, `overlaps` | Importable, but not a `public_modules` entry; `overlaps` normalizes with a document-entrypoint error | Two pure functions written in the feature's models |
| Glob matching | `devkit_agt.features.rules.models.settings.match_path` | Yes | Not used: write scopes are literal (section 6) |
| Path normalization and confinement | `devkit_core.core.normalize_relpath`, `resolve_within` | Yes | Reused |
| Lock | `devkit_core.core.file_lock` | Yes | Reused |
| JSON Lines append | none | No public helper | Written in the feature |
| Document ID grammar and resolution | `devkit_docs.features.documents.models.ids.is_id`, `devkit_docs.features.documents.repositories.index.DocumentIndex` | Yes | Reused |
| CLI boundary and workspace option | `devkit_dist.adapters.cli` | Yes | Reused |

No public harness module supplies a piece the commands need, so the feature declares no `devkit_agt` edge. Five
private parsers of `git worktree list` exist in the repository (`lifecycle._entries`, `shared/local._worktrees`,
`integration/usecases/service.py:362`, `host/usecases/registrations.py:289`, `devkit_spec` scope inventory); a
shared public one in `devkit-core` would be a separate change to those callers.

## 11. What the `devkit-docs` requirement changes (second turn)

| Subject | Before | After | Evidence |
| --- | --- | --- | --- |
| Requirement form | `dependencies = []` after the extraction | `devkit-core==<version>`, `click>=8.1.7`, `devkit-docs==<version>` with a workspace source per sibling, as `devkit-spec` and `devkit-docs` declare theirs | `packages/devkit-spec/pyproject.toml:7-12,54-58`; `packages/devkit-docs/pyproject.toml:7-11,41-43` |
| Pin mechanism | none | The exact pin is checked by `scripts/releases/identity.py:56-70` and `packages/devkit/tests/integration/package/test_lockstep.py:27-47`, rewritten by `scripts/releases/metadata.py:102-134` and locked by `uv lock`; all read every `packages/*/pyproject.toml`, so no registration is needed | scout-04 |
| Release coupling | The wheel changes version with its own payload | Also whenever `devkit-docs`, `devkit-agt`, `devkit-dist` or `devkit-core` changes version | `scripts/releases/metadata.py:93-99`; `ARCH-07-deployment` |
| Installed closure | The consumer declares `devkit-docs` and the bundle's wheel | `devkit-adaptive` alone brings `devkit-docs`, `devkit-agt`, `devkit-dist`, `devkit-core`, `devkit-cli`, `devkit-advisory` | `packages/devkit-docs/pyproject.toml:7-11`; `packages/devkit/pyproject.toml:8-11` |
| Selection after `devkit sync` | `docs:core` auto-selected because the consumer installed `devkit-docs`; `harness:core` as a built-in | The same selection from one requirement; `docs:core` is announced once with `BUNDLE_AUTO_SELECTED`; `adaptive-dev` stays unselected until `devkit add adaptive-dev`; `devkit remove docs` opts out | `config.py:226-290`; `sync.py:842-900`; `CAP-DIST-sync-and-transactions` |
| `devkit bundle snapshot` of the source | Accepted while the wheel is bundle-only | Refused with `BUNDLE_SNAPSHOT_UNSUPPORTED`: "source project runtime dependencies/optional-dependencies must be empty"; the `devkit.commands` group alone is refused too | `packages/devkit-dist/src/devkit_dist/features/distribution/services/snapshots/source.py:55-65`; `models/snapshots.py:20-24` |
| Guides | "devkit-docs plus devkit-catalog"; `devkit-docs` described as an alternative to the harness | `devkit-adaptive` alone | scout-04, finding 5 |

No current document or guide tells a consumer to snapshot the `adaptive-dev` bundle; the snapshot examples name a
private team-assets checkout (`guides/install/existing-repository.md:283-285`).

## 12. Governing document validation (second turn)

| Option | Catches | Misses or costs |
| --- | --- | --- |
| Record the text unverified (first turn) | Nothing | A mistyped ID, or a document the assignee cannot read |
| Resolve IDs in the invoking checkout | A mistyped or unknown ID | A document that exists in the Host checkout and not in the assignee's worktree |
| Resolve IDs and relative paths in the assignment's worktree (chosen) | Both | One index load of that worktree's `docs/` and `specs/` per `new` that names an ID; the index may write its parse memo under the worktree's ignored `.devkit/transient/` |
| Check again at `verify` or `list` | A document removed later | A second index load per verification for a fact the scope check already covers when the assignee deleted it |

`DocumentIndex.load(root).resolve(id)` raises `DOCS_ID_UNRESOLVED` or `DOCS_ID_DUPLICATE`; `is_id` tests the ID
grammar; proposals, specs, feedback and materials resolve through the same index; a directory without `docs/` loads
an empty index (scout-03).

## 13. Size assessment (second turn)

| Part | Content | Verified by |
| --- | --- | --- |
| Feature | Six verbs, the ledger, verification, governing validation | Unit and integration tests of the package |
| Packaging | The requirement, the lock file, the architecture declaration, the installed-consumer test, the smoke script | The installed-consumer test, `RULE-architecture`, the lockstep test |
| Guidance | Six bundle references and templates, three archetypes, the constitution | Bundle content tests |
| Living Spec | One capability added; two capabilities, one use case and three architecture documents edited; five guide files; one reference page | `devkit rules check`, the documented-codes test, the reconcile review |

A split into "requirement and guidance" and "commands" was weighed. The requirement exists because the feature
imports the document index, the guidance sentences name the commands, and the installed-consumer test asserts the
requirement and a command call in one consumer. Splitting would land a requirement with no importing code first and
edit the same capability, bundle references and consumer test twice. The parts are one spec; the size stays `L`.
