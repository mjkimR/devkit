# Python rule runner: implementation and experiment plan

The original investigation is preserved in the root `tmp` memo. It described
an experiment for replacing custom Go rule builds with one Python runner
invocation. This repository currently provides a standalone Python library and
CLI; integration with the Go CLI has not been implemented.

## Implemented boundaries

- `engine/`: rule protocols, contexts, dynamic discovery and sequential evaluation.
- `workspace/`: session caches for file lists, bytes, text, YAML frontmatter,
  lightweight Markdown links and the document catalog.
- `rules/specification/`: required metadata, document IDs and references.
- `rules/markdown/`: relative link validation and repair.
- `rules/hygiene/`: optional file length warnings.
- `cli/`: command options, text/JSON output and exit status.

Public imports remain available from `agent_rule_engine` and built-in rule
classes from `agent_rule_engine.rules`. Tests follow these feature groups outside
`src/`.

## Evaluation lifecycle

```text
Initialize context and cache
  → Select rules (hygiene also includes linter checks)
  → Run specification formatting checks first
  → Collect initial findings and execution errors
  → If fix requested, no initial errors, and not dry-run:
      → Run fix methods sequentially
      → Invalidate modified files and dependent indexes after each fix
      → Recheck all active rules once
      → Mark resolved fixable findings as fixed if recheck succeeds
  → Return findings and execution errors
```

This is one repair pass followed by a convergence check, not an unbounded loop.
Fix failures clear the cache and trigger a recheck so reported findings reflect
partial writes. There is no rollback. Invalid or unclosed YAML frontmatter is
reported as an error instead of being replaced by generated metadata.

The catalog spans `docs/` and `specs/` even for checks of selected files. Paths
are matched exactly relative to the workspace. File and reference ordering is
deterministic. Dynamic rule import failures fail the command and go to stderr,
leaving JSON stdout parseable.

## Pending experiments

The memo's sequential-first approach remains the baseline. There are no
validated speed comparisons with Go yet. Measure these costs separately:

1. Runner startup and custom rule imports.
2. File discovery (first scan versus cached calls).
3. File reads, frontmatter/link extraction and catalog construction.
4. Each rule check and the autofix/recheck pass.
5. Serialization and eventual Go CLI invocation overhead.

Record file count, total bytes, environment, cold/repeated runs and result parity.
Compare changed-file checks, full workspace checks and checks immediately after
custom rule edits. Choose an acceptable latency before deciding whether worker
processes are needed. Persistent caches, full Markdown parsing, Git snapshots,
Go IPC and metadata-based discovery require separate designs and tests.
