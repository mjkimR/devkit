# devkit.core

Shared foundation of the `devkit` modules: one implementation of what several
modules must agree on, so their behavior cannot drift apart. It carries no
document or workflow model; it is the SDD-agnostic base the other modules build on.
Part of the `devkit` package; it depends only on `pyyaml` and `devkit.advisory`.

## Modules

| Module | Purpose |
| --- | --- |
| `devkit.core.errors` | `DevkitCoreError`, an `AdvisoryError`, and its subclasses with their codes: `FrontmatterError` (`FRONTMATTER_INVALID`, `INPUT_ERROR`), `ReceiptError` (`RECEIPT_INVALID`, `MAINTENANCE`, fix: restore the receipt from version control, then `devkit sync`), `ConfigError` (`CONFIG_INVALID`, `INPUT_ERROR`, target `.devkit/config.toml`), `UnsafePathError` (`PATH_UNSAFE`, `INPUT_ERROR`), `AssetFileError` (`ASSET_FILE_INVALID`, `MAINTENANCE`) and `GitError` (`GIT_FAILED`, `MAINTENANCE`; also carries `command`, `returncode` and `stderr`). None is a `ValueError`. A module that knows more re-raises with its own code or fields; otherwise the CLI boundary renders them as they are. |
| `devkit.core.frontmatter` | The one YAML frontmatter grammar. `locate(text)` returns the block's character offsets (for byte-preserving rewrites), `parse(text)` returns `Frontmatter(data, body, body_line)`, `load_header(yaml)` parses a header alone. The grammar accepts a UTF-8 BOM, CRLF line endings, trailing whitespace on delimiters, and a `---` or `...` closer. It rejects an unclosed block, non-mapping YAML, non-string top-level keys and duplicate keys. |
| `devkit.core.receipt` | Strict typed reader for `.devkit/installation.json` (`RECEIPT_PATH`). `load_receipt(root)` returns `None` only when the file is absent; malformed JSON, duplicate keys, schema violations and unsafe paths raise `ReceiptError`. `parse_receipt(raw)` validates bytes or text the same way. `Receipt.assets(kind=...)`, `AssetRecord.files(suffix)`, `Receipt.file(path)`, `Receipt.file_hash(path)` and `FileRecord.matches(data)` cover the common queries. `verified_asset_file(root, item, receipt, asset, source_root=None)` is the one check applied before importing receipt-listed code (rules, gates, workflow plugin checks): the path must stay inside `root`, a recorded file must match its SHA-256 (an unrecorded project override is used as is), and for a Git snapshot a file absent from `root` is taken from `source_root` only when it matches its record; failures raise `AssetFileError` (`ASSET_FILE_INVALID`) with a `devkit sync` or `devkit override create` fix. |
| `devkit.core.paths` | `normalize_relpath(value, canonical=False)`, `is_safe_relpath(value)` and `resolve_within(root, rel)` (symlink-aware containment). Absolute paths, `..`, empty values, `.` and backslash escapes are rejected; a backslash inside a file name is accepted. |
| `devkit.core.git` | `run_git(cwd, *args, input=None, timeout=60) -> bytes`; raises `GitError` with the exit status and stderr. Decode paths with `errors="surrogateescape"`. |
| `devkit.core.plugins` | `load_subclasses(files, base, namespace=..., validate=None) -> PluginLoad` imports plugin files under stable module names. It instantiates the concrete subclasses defined in each file, atomically per file, and never leaves a failed module in `sys.modules`. `iter_plugin_files(dir)` scans a directory and skips `_`/`.` names. |
| `devkit.core.project` | `find_project_root(start)`: the nearest `.devkit/` directory up to the Git top level, else the Git top level, else `start`; this is the default of `-w/--workspace-root` for the distribution, `devkit rules` and `devkit workflow` commands (`devkit gate` uses the Git top level). `git_toplevel(start)` returns the work tree's top level or `None`. `read_project_config(root)` parses `.devkit/config.toml` (`CONFIG_PATH`); a missing file is `{}`, an invalid one raises `ConfigError`. |

Public names are exported from `devkit.core` (frontmatter functions through
their module, `devkit.core.frontmatter`).

## Used by

`devkit.rules`, `devkit.workflow`, `devkit.gate` and `devkit.distribution`.
`devkit.core` imports only `devkit.advisory`, for its error base class.
