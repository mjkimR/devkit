# devkit_viewer

A local, read-only page for the Living Spec, proposals, specs and roadmap of devkit repositories, from the
`devkit-viewer` distribution. Semantics: `CAP-VIEW-repository-viewer`.

## Usage

```bash
uv run devkit viewer serve                          # the devkit project containing the current directory
uv run devkit viewer serve --repo ../a --repo ../b  # top levels of Git work trees; the ID is the directory name
uv run devkit viewer serve --scan repos/            # each direct child holding .devkit/config.toml
uv run devkit viewer serve --port 0                 # any free port (default 8765)
uv run devkit viewer --version
```

`serve` binds `127.0.0.1` only and runs in the foreground until `SIGINT` or `SIGTERM`, then exits `0`. `-v` prints one
`[INFO]` line per request on stderr.

## Output

```text
[VIEWER: url=http://127.0.0.1:8765/ repos=3]
[VERSION: devkit-viewer 0.1.0]
```

| Code | Exit | When |
| --- | --- | --- |
| `VIEWER_REPO_DUPLICATE` | 2 | Two registered repositories have the same directory name |
| `VIEWER_REPO_INVALID` | 2 | A `--repo` path is not the top level of a Git work tree |
| `VIEWER_NO_REPOSITORY` | 2 | No `--repo`, no eligible `--scan` child, and not inside a devkit project |
| `VIEWER_PORT_IN_USE` | 2 | The port is already bound on `127.0.0.1` |

## HTTP API

`GET` only; another method is `405`, a `Host` other than `127.0.0.1:<port>` or `localhost:<port>` is `403`. The
checked-out branch (or `HEAD` when detached) is displayed. Tree and blob reads use saved files from the working
directory; a legacy `ref` parameter is ignored.

```text
GET /api/repos                              {"repos": [{"id", "default_branch"}]}
GET /api/repos/<id>/info                    {"repo_id", "default_branch"}
GET /api/repos/<id>/tree?path=<dir>         {"items": [{"name", "path", "type": "tree"|"blob", "size"?}]}
GET /api/repos/<id>/tree?path=<dir>&recursive=true  {"items": [...descendant metadata...] }
GET /api/repos/<id>/dashboard-list?path=<section>  {"items": [{"path", "content", "encoding": "utf-8"}], "errors": []}
GET /api/repos/<id>/blob?path=<file>        {"path", "encoding": "base64", "content", "size"}
GET /api/repos/<id>/planning-proposals      {"sources": [{"id", "kind", "label", "slug"}], "items": [{"source", "path", "content", "encoding"}], "errors": []}
GET /api/repos/<id>/tree?path=<dir>&recursive=true&source=<source id>   the source's proposal directory
GET /api/repos/<id>/blob?path=<file>&source=<source id>                 one file of it
error                                       {"error": {"code", "message"}}
```

| Code | Status |
| --- | --- |
| `VIEWER_REPO_UNKNOWN`, `VIEWER_PATH_NOT_FOUND`, `VIEWER_NOT_FOUND` | 404 |
| `VIEWER_PATH_INVALID`, `VIEWER_SOURCE_PATH_REFUSED` | 400 |
| `VIEWER_SOURCE_UNKNOWN` | 404 |
| `VIEWER_HOST_REFUSED` | 403 |
| `VIEWER_METHOD_NOT_ALLOWED` | 405 |

The dashboard loads each section independently: candidate frontmatter supplies sorted lists and counts; only visible pages fetch full bodies (6 milestones, 9 proposals, 6 feedback per page). Load more appends one page in the existing order. Cached lists and displayed pages remain reusable for 30 seconds from list completion; use Dashboard Refresh to reload saved changes and reset to the first page. Recursive tree reads list metadata only and omit symlinks and `.git`.

The **Read** tab (view id `book`) opens `handbook/<lang>/README.md` where `handbook/manifest.json` exists, through the
ordinary `blob` read: the manifest, `VERSION` and one page, nothing under `docs/` or `specs/`. Without a manifest it
says so after that one read. The header orders the manifest tag against `v<VERSION>` and notes a snapshot behind the
repository. The Living Spec book is computed only after `Living Spec book` is selected, and the request lasts until
the repository or branch changes. A host's `initialView="book"` with an `initialPath` file under `docs/` counts as
the request. Contract: `CAP-VIEW-repository-viewer` §4.3.

Proposals under Planning overlay the checkout's: a separate `planning-proposals` request reads
`docs/proposals/PROP-<slug>/proposal.md` from each `plan-<slug>` worktree (saved files), else the local branch, else
the first remote-tracking `<remote>/plan-<slug>` as of the last fetch (refs merged into the checkout are skipped), through one `git worktree list`, one
`git for-each-ref` and one `git cat-file --batch`. Cards update in place with a source badge (`worktree plan-x`,
`plan-x`, `origin/plan-x`); the next list build orders with the overlay. Source IDs are `worktree:plan-<slug>`,
`branch:plan-<slug>` and `remote:<remote>/plan-<slug>`; `source` is accepted only by `tree` and `blob` for paths in
that source's proposal directory. Nothing fetches, calls `gh` or writes; the roadmap and every other tab read the
checkout.

## Frontend

```bash
just viewer install   # npm ci in packages/devkit-viewer/frontend
just viewer lint      # prettier --check
just viewer check     # svelte-check
just viewer test      # vitest
just viewer probe <abs-dir> [vitest args]   # vitest on the *.test.ts files of a directory outside src/ (review probes)
just viewer build     # rebuild the committed app under src/devkit_viewer/static/
just viewer pack      # the library tarball autohub vendors, checked for its exports
uv run devkit generated check viewer-assets   # the committed build matches the sources
```

`just viewer probe` collects only the test files under the given absolute directory, for example a reviewer's
`<worktree>/scratch/review-NN/`, with the package's Vite config and every dependency the package declares resolved from
the package, so a probe imports `vitest`, `@testing-library/svelte` or a component by relative path like a test under
`src/`. It writes a temporary `.viewer-probe.vitest.config.mts` into that directory and removes it on exit. A failing
probe exits `1`; a relative or missing directory exits `2`.


The exact local report page is `/review/<registered-id>/<generation-id>`; it displays escaped Markdown with source/language/expiry and never regenerates reports. See `CAP-VIEW-repository-viewer`.
