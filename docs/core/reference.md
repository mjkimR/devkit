# devkit.core

Shared foundation of the `devkit` modules: one implementation of what several
modules must agree on, so their behavior cannot drift apart. It carries no
document or workflow model; it is the SDD-agnostic base the other modules build on.
Part of the `devkit` package; it depends only on `pyyaml`.

## Modules

| Module | Purpose |
| --- | --- |
| `devkit.core.errors` | `DevkitCoreError` and its subclasses `FrontmatterError`, `ReceiptError`, `ConfigError`, `UnsafePathError` (all also `ValueError`) and `GitError`. Plain exceptions; packages map them to their own reporting (advisories, exit codes) at their boundaries. |
| `devkit.core.frontmatter` | The one YAML frontmatter grammar. `locate(text)` returns the block's character offsets (for byte-preserving rewrites), `parse(text)` returns `Frontmatter(data, body, body_line)`, `load_header(yaml)` parses a header alone. The grammar accepts a UTF-8 BOM, CRLF line endings, trailing whitespace on delimiters, and a `---` or `...` closer. It rejects an unclosed block, non-mapping YAML, non-string top-level keys and duplicate keys. |
| `devkit.core.receipt` | Strict typed reader for `.devkit/installation.json` (`RECEIPT_PATH`). `load_receipt(root)` returns `None` only when the file is absent; malformed JSON, duplicate keys, schema violations and unsafe paths raise `ReceiptError`. `parse_receipt(raw)` validates bytes or text the same way. `Receipt.assets(kind=...)`, `AssetRecord.files(suffix)`, `Receipt.file(path)`, `Receipt.file_hash(path)` and `FileRecord.matches(data)` cover the common queries. |
| `devkit.core.paths` | `normalize_relpath(value, canonical=False)`, `is_safe_relpath(value)` and `resolve_within(root, rel)` (symlink-aware containment). Absolute paths, `..`, empty values, `.` and backslash escapes are rejected; a backslash inside a file name is accepted. |
| `devkit.core.git` | `run_git(cwd, *args, input=None, timeout=60) -> bytes`; raises `GitError` with the exit status and stderr. Decode paths with `errors="surrogateescape"`. |
| `devkit.core.plugins` | `load_subclasses(files, base, namespace=..., validate=None) -> PluginLoad` imports plugin files under stable module names. It instantiates the concrete subclasses defined in each file, atomically per file, and never leaves a failed module in `sys.modules`. `iter_plugin_files(dir)` scans a directory and skips `_`/`.` names. |
| `devkit.core.project` | `find_project_root(start)`: the nearest `.devkit/` directory up to the Git top level, else the Git top level, else `start`; this is the default of `-w/--workspace-root` for the distribution, `devkit rules` and `devkit workflow` commands (`devkit gate` uses the Git top level). `git_toplevel(start)` returns the work tree's top level or `None`. `read_project_config(root)` parses `.devkit/config.toml` (`CONFIG_PATH`); a missing file is `{}`, an invalid one raises `ConfigError`. |

Public names are exported from `devkit.core` (frontmatter functions through
their module, `devkit.core.frontmatter`).

## Used by

`devkit.rules`, `devkit.workflow`, `devkit.gate` and `devkit.distribution`.
`devkit.core` itself imports no other devkit module.
