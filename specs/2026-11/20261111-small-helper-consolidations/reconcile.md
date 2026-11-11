---
reconcile_id: REC-small-helper-consolidations
status: pending
targets:
  - file: docs/capabilities/cli/CAP-CLI-agent-cli-toolkit.md
    resolution: modified
  - file: docs/development/reference/core.md
    resolution: modified
---

# Reconcile: `SPEC-small-helper-consolidations`

## Living Spec changes

- `CAP-CLI-agent-cli-toolkit` section 4: the `devkit_cli` public-name table lists `utf8_output()` (rule 7's
  reconfiguration, run by `Boundary` and called directly by a command whose stdout bypasses the boundary). Rule 10
  holds: an added name ships with the shared release version, so devkit-cli gets no own minor bump.
- `docs/development/reference/core.md`: the `devkit_core.core.frontmatter` row documents
  `scalar(value, *, quote="'", always_quote=False)`; the `devkit_core.core.git` row documents `tracked_paths` and
  `ignored_paths`; the `devkit_dist.adapters.cli` row names the re-exported `utf8_output()`.
- `packages/devkit-cli/README.md` (quick reference, not a Living Spec document) lists `utf8_output()`.

## No-impact reasoning

- `CAP-DIST-agent-projections`: unchanged. Its rule that the rendered `description` is a quoted scalar whose line
  breaks are escaped keeps holding (`always_quote=True`, double style). All 78 renderings of the 26 shipped role
  contract files (15 sources plus installed copies, the 2 templated contracts included) for `claude-code`, `codex`
  and `antigravity` hash identically before and after (probe `tmp/probe/bytes.py`, baseline taken on `c78848bc`
  before any source edit, rerun on `753d53b0` after the review-01 fix), and `uv run devkit sync --check` exits `0`.
  Projection keeps its identifier-only plain gate in front of `frontmatter.scalar` (spec assumption 2), so
  project-owned contracts keep their bytes too, apart from the escape spellings of spec assumption 1.
- Host registrations, shared storage, local render and projection Git notice behavior: unchanged; each site keeps its
  ignore mode, deadline and failure mapping, so no capability describing them changes.
- `docs/architecture/`: no package dependency or feature edge is added.

## Entrypoints

`devkit spec entrypoints derive` proposed 15 new paths for `CAP-CLI-agent-cli-toolkit`, all rejected: they are
devkit-core helpers, devkit-dist feature modules and tests, not doorways of the CLI toolkit, whose entrypoints
already name `packages/devkit-cli/` and `packages/devkit-dist/src/devkit_dist/adapters/cli.py`.

## Deferred work and source feedback

None: no deferred work, and the Unit has no FB source feedback (the items are X-13, DS-09 and DS-10 of the code pass
report).
