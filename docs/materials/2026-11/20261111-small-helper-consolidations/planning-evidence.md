# Planning evidence (worktree HEAD after `4150477e`)

Probes ran from the ignored `tmp/probe/` path of the Planning worktree; this file keeps their results.

## X-13: UTF-8 output helper

- Copies: `devkit_cli.boundary._utf8_output` (run by `Boundary` before every command) and
  `devkit_dist.features.host.cli._utf8_output` (called by the hidden `devkit host hook` command, which does not go
  through `@boundary` because its stdout follows the host's native protocol). The bodies are identical
  (`reconfigure(encoding="utf-8", errors="backslashreplace")` on `io.TextIOWrapper` streams, `OSError` and
  `ValueError` suppressed).
- `devkit-dist` already depends on `devkit-cli` (exact pin in `packages/devkit-dist/pyproject.toml`) and imports it
  (`devkit_dist/cli.py`, `devkit_dist/adapters/cli.py`, `playbook_search.py`). A public `devkit_cli` helper adds no
  package edge.
- `devkit-cli` depends on `click` and `devkit-advisory` only and its package docstring says it imports nothing else;
  moving the helper to `devkit-core` would add a `devkit-cli -> devkit-core` dependency. Rejected.
- `CAP-CLI-agent-cli-toolkit` rule 10: adding a public name changes the shipped payload (shared release version);
  only a removed or renamed name forces a minor bump. Public names are pinned in
  `packages/devkit-cli/tests/integration/test_lazy_and_package.py`.

## DS-09: subagent projection YAML quoting

- `devkit_dist.features.distribution.services.bundles.subagents`: `_yaml_quote` (always double-quoted, used for
  `description`), `_yaml_scalar` (plain when it matches `^[A-Za-z][A-Za-z0-9_./-]*$` and is not a YAML 1.1 boolean
  or null word, else double-quoted; used for `name` and settings) and `_yaml_value` (bool, int, string, flow list).
  The shared serializer is `devkit_core.core.frontmatter.scalar` (plain when it reads back, else single-quoted, or
  double-quoted when it holds a line break).
- `CAP-DIST-agent-projections` (Role contracts): "The rendered `description` (`<title>. <description>`) is a quoted
  scalar whose line breaks are escaped, never folded." A plain description would break that contract.
- Switching to `scalar` as it is: all 11 `description` lines of `.claude/agents/*.md` change (double-quoted to plain);
  the 32 other header values are unchanged. Across the 17 shipped role contracts (240 host values plus roles), the
  one other difference is the value `off` in `devkit-adaptive` `swarm-planner.md` (`"off"` today, `'off'` from
  `scalar`).
- PyYAML double style (`safe_dump(v, default_style='"', allow_unicode=True, width=2**31)`) equals `_yaml_quote`
  for line breaks, tabs, quotes, backslashes, C0 controls, DEL, non-ASCII text, `: ` / ` #` and 400-character
  values; it differs only for NEL, LS, PS and non-printable characters such as U+FEFF, which PyYAML escapes
  (`\N`, `\L`, `﻿`) and the hand-rolled quoter writes raw. No shipped description contains one.
- Codex projections use `_toml_string` (TOML), outside DS-09.

## DS-10: Git tracked/ignored probes in devkit-dist

| Site | Tracked query | Ignore query | Failure handling |
| --- | --- | --- | --- |
| `host/usecases/registrations.py` `_tracked`, `_ignored`, `_Eligibility` | `ls-files -- <path>` (batch: `-z`, a path or a directory holding tracked files) | `check-ignore -- <path>` / `--stdin -z` (index-aware) | any `AdvisoryError` means not ignored; batch exit 1 means none |
| `shared/repositories/local.py` `_eligible`, `_initialize` | `ls-files -- .devkit/.shared` with a deadline | `check-ignore -- .devkit/.shared/` (index-aware, deadline) | Git failure raises `ExclusionError`; also `ls-files --others --exclude-standard` (a different query) |
| `distribution/services/installation/local_render.py` `require_ignored` | `ls-files -- <name>` | `check-ignore --no-index -- <name>` | exit 1 is not ignored; other `GitError` raised |
| `distribution/repositories/projection_git.py` `projection_git_notices` | `ls-files -z -- .` intersected with owned names | `check-ignore --no-index --stdin -z`, `ok_returncodes=(0, 1)` | non-repository exit 128 skips; other failures become a notice |
| `distribution/usecases/sync.py` locked-sync check | `ls-files -- <changes>` (tracked only) | none | `GitError` raised |

Differences that stay per caller: index-aware versus `--no-index` ignore checks, the deadline, and each caller's
failure mapping. All five sites already import `devkit_core.core.git`; current inputs are fixed devkit paths without
glob characters, so literal pathspecs change no current result.
