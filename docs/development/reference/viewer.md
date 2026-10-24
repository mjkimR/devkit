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
GET /api/repos/<id>/blob?path=<file>        {"path", "encoding": "base64", "content", "size"}
error                                       {"error": {"code", "message"}}
```

| Code | Status |
| --- | --- |
| `VIEWER_REPO_UNKNOWN`, `VIEWER_PATH_NOT_FOUND`, `VIEWER_NOT_FOUND` | 404 |
| `VIEWER_PATH_INVALID` | 400 |
| `VIEWER_HOST_REFUSED` | 403 |
| `VIEWER_METHOD_NOT_ALLOWED` | 405 |

## Frontend

```bash
just viewer install   # npm ci in packages/devkit-viewer/frontend
just viewer lint      # prettier --check
just viewer check     # svelte-check
just viewer test      # vitest
just viewer build     # rebuild the committed app under src/devkit_viewer/static/
just viewer pack      # the library tarball autohub vendors, checked for its exports
uv run devkit generated check viewer-assets   # the committed build matches the sources
```


The exact local report page is `/review/<registered-id>/<generation-id>`; it displays escaped Markdown with source/language/expiry and never regenerates reports. See `CAP-VIEW-repository-viewer`.
