# Package split evidence and option comparison (Planning, 2026-10-19)

Planning material for `PROP-devkit-dist-package-separation`: the evidence behind `PADR-dist-module-split`,
`PADR-dist-command-composition`, `PADR-dist-config-receipt-ownership` and `PADR-dist-bundles-compatibility`, and the
open questions left to the user. Measured on the plan-intent head of the Planning branch; paths are
repository-relative.

## 1. Import closure of `devkit.distribution`

A static scan of every `import`/`from ... import` (lazy imports inside functions included) in
`packages/devkit/src/devkit`, following module edges transitively from `devkit.distribution`:

| Area reached | Modules reached | Via |
| --- | --- | --- |
| `devkit.distribution` | 39 | start |
| `devkit.core` | 15 of 15 | `devkit.core` re-exports every module (`core/__init__.py`) |
| `devkit.search` | 6 of 6 | `distribution.cli` (playbook search) |
| `devkit.host` | 9 (configuration, hooks, hooks.model, runner, status, observation, errors, adapters.codex, package) | `distribution.bundles.manifest`, `installation.host_hooks` |
| `devkit.advisory` | 4 | `devkit.core.errors` |
| `rules`, `workflow`, `gate`, `worktree`, `compact`, `generated`, `integration` | 0 | never reached |

Direct cross-area imports per area (excluding tests): `core` imports only `advisory`; `host` only `core` and
`advisory`; `search` only `core` and `advisory`; `compact` only `core` and `advisory`. These match `ALLOWED` in
`packages/devkit/tests/test_layering.py`. The projected Codex hook command is
`devkit host hook --host codex --asset <asset>` (`host/adapters/codex.py`), so native hooks need `devkit host`,
which is in `devkit.host.cli`, outside the closure above: moving `host` whole is required for standalone hooks.

Users of each `core` module across areas: `receipt` (core, distribution, gate, host, rules, workflow, worktree),
`project` (compact, core, distribution, host, integration, rules, workflow, worktree), `cli` (every command area),
`plugins` (core, distribution, gate, rules), `git` (core, gate, integration, rules, workflow, worktree), `locks`
(core, integration), `deadline` (core only, plus devkit-spec). No `core` module is used only by harness areas
except through `core/__init__` re-exports, which distribution imports.

## 2. Entry point groups and who loads them

| Group | Loaded by (area) | Registered by |
| --- | --- | --- |
| `devkit.commands` | `cli` | devkit-spec (`spec`) |
| `devkit.bundles` | `distribution` | devkit-agt (`devkit`, `advisory`, `authoring`, `git-commits`), devkit-spec, devkit-catalog, devkit-starter |
| `devkit.config_template` | `distribution` | devkit-spec (`spec`) |
| `devkit.post_sync` | `distribution` (through `core.extensions`) | devkit-agt gate (`gate-hooks`) |
| `devkit.host.handlers` | `host` | devkit-agt host (`observe`) |
| `devkit.host.services` | `host` (MCP) | devkit-agt integration (`integration`) |
| `devkit.embedding_models` | `search` | devkit-embed |
| `devkit.hygiene` | `rules` | devkit-agt worktree, devkit-spec |
| `devkit.finish_guard`, `devkit.attach_check` | `worktree` | devkit-agt workflow, devkit-spec |
| `devkit.post_finish`, `devkit.integration.readiness` | `integration` | devkit-spec |

Every group a `devkit-dist` area loads is either fed by `devkit-dist` itself or by a package above it through
dependency inversion (`post_sync`, `host.services`), so no group needs to move or be renamed.

## 3. Configuration and receipt

- `distribution/installation/config.py`: `FIELDS` accepts `schema`, `agents`, `presets`, `playbooks`, `rules`,
  `workflow`, `gates`, `worktree`, `integration`, `guidance_block`, `override_drift`, `tool`, `bundles`; the comment
  says `rules`, `workflow`, `gates` and `worktree` belong to their engines and are passed through. `TEMPLATE_TABLES`
  hard-codes `[workflow.approvals]`, `[workflow.stages]` and `[worktree]` "so distribution does not import higher
  layers".
- `distribution/installation/config_template.py`: `devkit.config_template` entries render only under
  `[tool.<name>]` (`TOOL_NAME` check on the entry name).
- `distribution/installation/sync.py`: `TOOL_PACKAGE = "devkit-agt"` is recorded as the receipt's `tool`; a receipt
  that differs only in `tool` is not rewritten, any other change records the running tool and raises the tool-version
  notice.
- `distribution/installation/discovery.py`: `BUILTIN_DISTRIBUTION = "devkit-agt"` marks built-in bundles; `builtin`
  excludes first-party auto-selected bundles from the "new auto-selected bundle" notice (`sync.py`) and appears in
  `devkit status` output.
- The receipt's per-bundle `package` records are rebuilt on every writing sync; no reader compares them with the
  installed distribution (`status.py` checks bundle names only), so a changed package name is not a conflict.

## 4. Built-in bundle dependencies

| Bundle | Selection | Assets | Needs | Assigned to |
| --- | --- | --- | --- | --- |
| `devkit` | auto | consumption, resource-kinds, in-repo-bundle, devkit-run; preset `run` adds an AGENTS.md pointer | text only; harness sections describe `devkit rules`, `devkit gate`, `devkit workflow`; `devkit-run` describes `devkit run` (compact) | `devkit-dist` (harness sections: question `harness-guidance`; `devkit-run`: question `compact-home`) |
| `advisory` | auto | protocol guides | text only | `devkit-dist` |
| `git-commits` | opt-in | commit conventions, AGENTS.md pointer | text only | `devkit-dist` |
| `authoring` | opt-in | two playbooks, two rule assets | rule engine; area imports `devkit.rules` | `devkit-agt` |

## 5. Scout findings (envelope `scout-01.yaml`)

- **Tests**: the import split is clean in production code, but four `devkit-dist`-side test locations reach harness
  code: `tests/distribution/test_config_template.py` imports the `workflow` and `worktree` config readers to check
  the hard-coded harness template tables (which C2 moves to `devkit-agt` together with this test);
  `tests/core/test_cli.py` asserts `rules`, `workflow` and `gate` are root commands; the hook assertion in
  `tests/distribution/test_sync.py` depends on the gate `post_sync` extension; `tests/testsupport/gate.py` imports
  `devkit.gate` at module level. `testsupport.distribution` and `testsupport.search` are shared by distribution, host
  and search tests only; `testsupport.rules`, `.gate` and `.workflow` are harness-side.
- **Latency**: `entry_points(group="devkit.commands")` costs 18 to 24 ms in-process against 10 to 13 ms for
  `import devkit.cli`; whole-process medians: `devkit --version` 38 ms, `devkit gate --help` 71 ms, `devkit spec
  --help` (plugin path) 106 ms. A harness command mounted as a plugin pays about 10 to 13 ms more per call. Git hooks
  run `devkit.gate` through a bootstrap that never imports `devkit.cli`, so commits pay nothing; the gate hook
  wrapper and the worktree lifecycle probe `devkit_agt-*.dist-info` to pick the interpreter, which stays valid while
  `devkit.gate` ships in `devkit-agt`.
- **Namespace overlap**: `packages/devkit/src/devkit/` holds `__main__.py`, `cli.py` and an empty `py.typed`;
  `devkit-advisory` ships only `devkit/advisory/` (with its own `py.typed`). Two wheels shipping `devkit/py.typed`
  would clash in RECORD ownership and uninstall; PEP 561 puts markers in the subpackages of a namespace.
- **Python API consumers**: `devkit-spec` imports `core` (67), `rules` (24), `advisory` (14), `workflow` (6),
  `search`, `worktree` and `integration` (2 each), and none of `distribution`, `host`, `compact`, `gate`,
  `generated` or `cli`; its entry points feed groups of both wheels, so it needs `devkit-agt`. Rule plugin code
  (spec and authoring bundles) imports only `devkit.rules` and `devkit.core`. `devkit-catalog` and `devkit-starter`
  tests import only `devkit.distribution`.
- **Wiring**: `scripts/release.sh` (tag check against `packages/devkit/pyproject.toml`, wheel names, release-note
  install lines), `scripts/smoke.sh` (one wheel per package, `tool_identity().package == "devkit-agt"`, built-in
  bundle packages, `devkit-agt[mcp]`), `scripts/_lib.sh` (devkit-embed URL read from `packages/devkit/pyproject.toml`,
  `devkit` alias), root `pyproject.toml` (ruff namespace packages, Pyright paths, dev group, sources, pytest paths),
  `.github/workflows/ci.yml` (model pin comment, compact test path) and `docs/development/ci-cd.md` (lockstep tag).
- **Hard-coded identities**: `BUILTIN_DISTRIBUTION`, `TOOL_PACKAGE`, `version("devkit-agt")` in `cli.py` and
  `host/mcp/server.py`, extra names in `search/errors.py`, `host/errors.py`, `host/cli.py` and
  `distribution/cli/__init__.py`, and the bundled `in-repo-bundle` and `agent-advisory-python` instructions.
- **Documents naming the current owner**: `ARCH-01-introduction-and-goals`, `ARCH-03-context`,
  `ARCH-05-1-containers`, `ARCH-05-2-components`, `ARCH-05-3-command-plugins`, `ARCH-05-4-distribution-components`,
  `ARCH-07-deployment`, the architecture README, every `CAP-DIST-*` (frontmatter code paths, receipt tool record,
  built-in bundles, extras), `CAP-SRCH-document-search`, `CAP-INT-mcp-services`, `CAP-HOST-lifecycle-observation`,
  `docs/development/reference/*`, `guides/*`, the package READMEs and the root README.

## 6. Option comparison summary

| Question | Selected | Rejected | Deciding reason |
| --- | --- | --- | --- |
| Q1 namespace | N1 shared `devkit.*` namespace | N2 `devkit_dist`, N3 mixed | zero import churn; mechanism already used by devkit-advisory |
| Q2 commands | M1 `devkit.commands` | M2 hard-coded harness paths, M3 first-party group, M4 second script | reuses the existing plugin path; keeps dependency direction |
| Q3 config/receipt | C2 reserved names + agt templates via `devkit.config_tables` | C1 status quo, C3 open names, C4 `[tool.devkit-agt]` | config valid with or without the harness; defaults live with their engine |
| Q4 foundation | F1 core/search/host whole | F2 split core, F3 partial host | closure reaches all of core; hooks need `devkit host` |
| Q5 bundles | B1 by dependency, K1 preserve behavior | B2 all agt, B3 all dist, K2 shims | each wheel's bundles work in its minimal environment |
