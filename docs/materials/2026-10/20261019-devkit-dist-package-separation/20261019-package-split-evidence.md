# Package split evidence and option comparison (Planning, 2026-10-19)

Planning material for the original proposal of `SPEC-devkit-dist-package-separation`: the evidence behind `ADR-dist-module-split`,
`ADR-dist-command-composition`, `ADR-dist-config-receipt-ownership` and `ADR-dist-bundles-compatibility`, and the
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
| `devkit` | auto | consumption, resource-kinds, in-repo-bundle, devkit-run; preset `run` adds an AGENTS.md pointer | text only; harness sections describe `devkit rules`, `devkit gate`, `devkit workflow`; `devkit-run` describes `devkit run` (compact) | `devkit-dist`; harness sections, `devkit-run`, `run-pointer` and the `run` preset move to the new `harness` bundle of `devkit-agt` (section 8) |
| `advisory` | auto | protocol guides | text only | `devkit-dist` |
| `git-commits` | opt-in | commit conventions, AGENTS.md pointer | text only | `devkit-dist` |
| `authoring` | opt-in | two playbooks, two rule assets | rule engine; area imports `devkit.rules` | `devkit-agt` |

Harness references in the `devkit` bundle text (for question `harness-guidance`):

- `AGENTS.md` (constitution): intro lines 3-5 (governance rules and commit gates), contract 5 (rules and gates run
  as code, `[rules]`/`[gates]`), contract 6 (snapshot gates trust the committed receipt).
- `instructions/consumption.md`: description and configuration table (rules, gates), "Workflows" (the
  `devkit-workflow` skill runs `devkit workflow next`), "Rules and commit gates" (`devkit rules check|fix|explain|
  test`, `devkit gate`, `.git/devkit.config`, `rules-check` gate).
- `instructions/resource-kinds.md`: decision tree and table rows for `rule` (run by `devkit rules`), `gate` (run by
  `devkit gate`) and `workflow` (`devkit workflow next`), `devkit rules test`.
- `instructions/in-repo-bundle.md`: rule tests and snapshot gates (`devkit rules check --staged`, `--rules-dir`), a
  `devkit-agt` development dependency in the example.
- `instructions/devkit-run.md`, `guidance/run-pointer.md`: `devkit run` (question `compact-home`).
- Distribution code: `installation/workflow_skill.py` generates the `devkit-workflow` entry skill, every step of
  which runs `uv run devkit workflow ...`, whenever a selected bundle ships a workflow asset (`inventory.py`).

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

## 7. Challenger review (envelope `challenger-01.yaml`) and disposition

| # | Finding | Disposition |
| --- | --- | --- |
| 1 | Distribution code emits harness directives (`devkit-workflow` skill; rule and gate assets never run standalone) | Inventoried in `ADR-dist-bundles-compatibility`; the standalone signal is user question `standalone-harness-signals` |
| 2 | Harness text in the `devkit` bundle under-inventoried; hash claim too strong | Full inventory in section 4 and in question `harness-guidance`; hash statement in `ADR-dist-config-receipt-ownership` made conditional |
| 3 | Missing-extra `[FIX]` directives undecided | Decided in `ADR-dist-module-split`: name the extra on the requirement the project declares, never a second direct requirement |
| 4 | No mechanism for dist-only tests | Decided in `ADR-dist-module-split`: a CI check runs `devkit-dist` tests without `devkit-agt`, asserting `devkit.rules` is absent |
| 5 | `compact-home` costs asymmetric | Costs stated in the question (keeping compact in `devkit-agt` breaks `devkit:run` selections and needs another bundle) |
| 6 | `uv tool install devkit-agt` finds no script | `ADR-dist-command-composition`: `uv tool install devkit-dist --with devkit-agt`, reconciled into `ARCH-05-3-command-plugins` and `CAP-DIST-content-packages` |
| 7 | Tool-version notice hides the package change | `ADR-dist-config-receipt-ownership`: the notice names both packages when they differ |
| 8 | Scan cost misquoted | Restated with both measurements |
| 9 | Benefit framed as smaller dependencies | Proposal section 1.1 and Consumer Impact restated; non-goal added |
| 10 | Root `AGENTS.md` not a reconcile target | Added to `ADR-dist-module-split` consequences |
| 11 | Harness command non-goal conflicts with agent-first output | Turned into user question `standalone-harness-signals` |

Re-review (envelope `challenger-02.yaml`): all eleven resolutions confirmed. Three low-severity issues in the draft
questions were fixed before asking: `harness-guidance` is asked first and `compact-home` states its costs per
`harness-guidance` answer; the `bundle-to-agt` option was dropped (it contradicted `ADR-dist-module-split`,
`ADR-dist-bundles-compatibility` and the rejected B2); `standalone-harness-signals` states that only third-party or
in-repo bundles can trigger it and that engine presence is detected by name only, through the `devkit.commands`
entry points (`rules`, `gate`, `workflow`), never by importing or locating a harness module.

## 8. User answers and folded decisions (envelope `answer-01.yaml`)

| Question | Answer | Folded into |
| --- | --- | --- |
| `harness-guidance` | `harness-bundle`: a new auto-selected `harness` bundle shipped by `devkit-agt` carries the harness guidance; the `devkit` bundle keeps only distribution guidance | `ADR-dist-bundles-compatibility` (H1), `ADR-dist-module-split` (area), proposal Q5 |
| `compact-home` | `agt`: `devkit.compact` stays in `devkit-agt`; `devkit-run`, `run-pointer` and the `run` preset move to `harness`; the `devkit:run` selection break is accepted in place | `ADR-dist-module-split`, `ADR-dist-command-composition` (`run` mounted), `ADR-dist-bundles-compatibility`, proposal Q2/Q4 |
| `standalone-harness-signals` | `both`: coded sync/status notice for rule, gate and workflow assets no engine runs, coded error for harness command names, name-only detection | `ADR-dist-bundles-compatibility` (notice), `ADR-dist-command-composition` (error, list, precedence) |

Evidence checked while folding (worktree head after `answer-01.yaml`):

- **`devkit:run` selections**: `.devkit/config.toml` has no `devkit` key under `[presets]`, and the receipt's
  `selection.presets.devkit` is `["core"]`, so this repository selects only `devkit:core`. No configuration of a
  first-party package (`devkit-spec`, `devkit-catalog`, `devkit-starter`) selects the `devkit` bundle's `run` preset;
  the only selections of it are the test `tests/distribution/test_guide_bundle.py`
  (`presets={"devkit": ["core", "run"]}`, `bundle.select(["run"])`, the managed path
  `.devkit/managed/devkit/instructions/devkit-run.md`). `tests/distribution/test_builtin_selection.py` expects the
  auto-selected built-ins `{"advisory": ["core"], "devkit": ["core"]}`, which gains `harness` where `devkit-agt` is
  installed. Correction after `challenger-03.yaml`: that `BUILTINS` constant is unused; the real-distribution tests
  compute the default selection, so no test asserts `harness` is auto-selected and built in until Development adds
  one. Consumer repositories outside this workspace were not read.
- **References naming `devkit:run` or the `devkit-run` instruction's bundle**: the `devkit` bundle manifest comment,
  `guides/install/bundle-recommendations.md`, `docs/development/reference/distribution.md` (section 4),
  `docs/development/reference/compact.md`, `CAP-CMP-bounded-execution`. `compact/execute.py` uses `devkit-run` only
  as its log directory prefix, unrelated to the bundle.
- **Cross-bundle references**: the `devkit-spec` bundle points to the `devkit` bundle's `in-repo-bundle` instruction
  from the `spec-rule` skill (rules in the in-repository bundle) and the `brownfield-adoption` and
  `feedback-hygiene` playbooks (where repository assets belong). The bundle setup stays in `in-repo-bundle`; rule
  tests and snapshot gates move to `harness`, which the `spec-rule` reference must also name.
- **Selection failure today**: an unknown preset raises `SelectionError` (`SELECTION_INVALID`) with the fix
  "Select one of: <bundle>:<preset>..." listing the bundle's own presets, `all` first (`preset_names` in
  `distribution/bundles/manifest.py`), so a `devkit:run` selection fails with a directive listing `devkit:all,
  devkit:core`, neither of which restores the pointer (corrected after `challenger-03.yaml`). A `devkit:all`
  selection keeps working after the split but silently drops `devkit-run` and `run-pointer`.
- **Harness command names** in the current root map (`devkit/cli.py` `COMMANDS`) that `devkit-agt` will mount:
  `run`, `rules`, `workflow`, `gate`, `worktree`, `generated`, `integration`; `host` stays a `devkit-dist` built-in.
- **Interpretation**: contract 6 of the `devkit` constitution has a distribution half (commit the receipt after
  `devkit sync`) and a harness half (snapshot gates trust the receipt); under "the `devkit` bundle keeps only
  distribution guidance" the first stays and the second moves, recorded in `ADR-dist-bundles-compatibility`.

## 9. Re-review of the folded answers (envelope `challenger-03.yaml`) and disposition

| # | Finding | Severity | Disposition |
| --- | --- | --- | --- |
| 1 | `devkit` bundle in-repo example naming `devkit-dist` would add a second direct requirement in `devkit-agt` projects | medium | `ADR-dist-bundles-compatibility`: the example keeps the requirement the project already declares, never both |
| 2 | Shared directive used bare package names | medium | `ADR-dist-command-composition`: runnable, source-explicit Git requirement in the form of the missing-extra fixes |
| 3 | Absolute "behaves as before" MUST contradicts planned changes | medium | Restated with enumerated exceptions and a before/after JSON comparison; proposal Consumer Impact aligned |
| 4 | `devkit:all` is a second, silent break; `SELECTION_INVALID` fix leads away from `harness:run` | medium | Second break recorded, evidence corrected; the generic cross-bundle hint is user question `preset-moved-hint` |
| 5 | `CAP-DIST-in-repo-bundles` missing as reconcile target | low | Added to the consequences with both mirrors |
| 6 | Layering scanner exempts `cli.py`/`__main__` and dict string targets | low | Per-wheel test MUST scan them and `devkit.<agt-area>` string constants; list-equality test lives in `devkit-agt` |
| 7 | Contract 6 split departs from the literal answer | low | User question `contract-6-split` |
| 8 | Bundle name `harness` collides with the `harness` capability area | low | User question `harness-bundle-name` |
| 9 | Contract 3 defaults list, overrides of moved assets, `devkit = false` projects | low | Contract 3 reworded generically; overrides named in upgrade consequences and release notes; opt-out kept in release notes |
| 10 | Two evidence details inaccurate | low | Corrected in section 8; a `devkit-agt` test asserting `harness` is built in and auto-selected is required |

## 10. Second re-review (envelope `challenger-04.yaml`) and disposition

Nine of the ten `challenger-03.yaml` dispositions were confirmed; the round found no new contradiction with
`answer-01.yaml` or `ADR-dist-foundation-ownership`.

| # | Finding | Severity | Disposition |
| --- | --- | --- | --- |
| 1 | Draft `preset-moved-hint` title over 40 characters | medium | Question dropped (finding 4) |
| 2 | `contract-6-split` attributes Planning's inventory to the user | low | Question dropped; the split is recorded in `ADR-dist-bundles-compatibility` as a correction of the Planning inventory, later settled by the user (`answer-02.yaml`) |
| 3 | `keep-harness` context omits `CAP-HARN-agent-guidance` | low | Question context states it; circular reason removed |
| 4 | `preset-moved-hint` incomplete; doing nothing needs no consent | low | Question dropped; the generic hint is a non-goal, later settled by the user (`answer-02.yaml`); `SELECTION_INVALID` stopping the whole sync recorded |
| 5 | Tool form still bare; tool branch lacks the `devkit-dist` requirement | low | Both places in `ADR-dist-command-composition` name full requirements; the section 7 row 6 form above is historical |
| 6 | Compatibility exceptions incomplete | low | Added the tool-version notice, the `[FIX]` texts, the harness-named plugin case; `devkit config template` stays byte-identical |
| 7 | Layering string match ambiguous; `devkit-agt` group map | low | Match limited to dotted module paths and `module:attribute` references; the `devkit-agt` test scans `devkit-dist`'s `*GROUP` constants too |
| 8 | Override consequence partly wrong | low | Split into moved-asset and split-asset cases |
| 9 | Release-notes list inconsistent | low | One list in the consequences |
| 10 | In-repo example test missing | low | Added to verification |

## 11. Last user round (envelope `answer-02.yaml`)

- `harness-bundle-name`: `keep-harness`. The bundle is `harness`, its data-only module `devkit.harness_guide`; its
  contract lives in `CAP-DIST-content-packages`, separate from the `devkit-spec` capability area `docs/capabilities/harness/`.
- Settled in the same round: the contract 6 split (receipt commit stays in `devkit`, the snapshot-gate part moves to
  `harness`) and the non-goal of a cross-bundle same-named-preset hint in `SELECTION_INVALID`, both previously
  worker assumptions open at plan-accept.
- The fold is wording only: the PADRs and the proposal already carried these three outcomes; they now cite the
  user's decision instead of presenting them as proposed or open. No re-review round was run for it.
