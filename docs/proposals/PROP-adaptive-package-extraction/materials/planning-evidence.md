# Planning evidence for PROP-adaptive-package-extraction

Scope: the evidence and option comparisons Planning collected at `plan-adaptive-package-extraction` (base
`881bced1`) for spike questions Q1 to Q7 of `PROP-adaptive-package-extraction`. Paths are relative to the repository
root. Each set closes with the recommendation; the proposal's Planning decisions record what is settled and on
which ground. The user's decisions replaced the recommendation of set 3 and settled the question set 2 left open;
both sets say so where they close.

## Evidence boundary

- Read: repository sources, tests, contracts and decisions at the base commit.
- Run: the six existing `devkit-dist` integration tests that exercise a selected bundle whose package is absent and
  two entry points with one name (`uv run pytest packages/devkit-dist/tests/integration/features/distribution/test_builtin_selection.py
  packages/devkit-dist/tests/integration/features/distribution/test_output_contract.py
  packages/devkit-dist/tests/integration/features/distribution/test_sync.py -k "uninstalled or not_installed or
  must_be_installed or entry_point"`: 6 passed).
- Not run: a built-wheel consumer that upgrades across the move. The wheels and a virtual environment were built
  under the proposal's ignored `.probe/`, but the host refused the script that edits the installed catalog metadata,
  so set 3 rests on the code, the contracts and the tests above. `.probe/s1_s2.sh` holds the unexecuted scenario.
  The proposal no longer needs the run: an upgrade across the move is out of scope (set 3).

## Set 1: names and layout (Q1)

| Item | Value | Evidence |
| --- | --- | --- |
| Distribution | `devkit-adaptive` | The user's decision; the pattern `devkit-<area>` of `devkit-spec`, `devkit-docs`, `devkit-viewer` |
| Directory | `packages/devkit-adaptive/` | Root `pyproject.toml:2-5`: the workspace is `packages/*` and `tools/*`, so membership needs no root edit (set 6 lists the root lists that do) |
| Import package | `devkit_adaptive` | `ADR-package-ownership-and-release-version`: each wheel owns a regular package named after its distribution; no installed path belongs to two wheels |
| Bundle resource module | `devkit_adaptive.bundles.adaptive_dev` at `src/devkit_adaptive/bundles/adaptive_dev/bundle/` | `ARCH-05-2-components` 1.1 and `CAP-DIST-content-packages` §1: an application package places a bundle under `<namespace>/bundles/<name>/bundle/`, also for one bundle. `devkit_dist/bundles/git_commits` is the precedent for a hyphenated bundle name |
| Initializers | `devkit_adaptive/__init__.py`, `bundles/__init__.py`, `bundles/adaptive_dev/__init__.py`, each a docstring only | `packages/devkit-spec/src/devkit_spec/__init__.py`, `bundles/__init__.py`, `bundles/spec/__init__.py`; `CAP-DIST-content-packages` §1 requires an initializer without side effects |
| `features/`, `cli.py`, `base/`, `utils/`, `adapters/` | Absent until the first command | `ARCH-05-2-components` 1.1: "Do not create empty layers"; `base/` and `utils/` are optional |
| Tests | `tests/integration/bundles/`, `tests/e2e/bundles/adaptive_dev/`, `tests/support/` | `ARCH-05-2-components` 1.3 |

Recommendation: the values above. Nothing here is a choice between viable options.

## Set 2: base dependency (Q2)

Facts:

- No file under `packages/devkit-catalog/src/devkit_catalog/adaptive_dev/` is Python code besides the empty
  initializer, so the moved package imports nothing.
- `packages/devkit-docs/pyproject.toml:7-11` pins `devkit-agt`, so the documented installation "devkit-docs plus
  the bundle's package" already contains the harness. Rule 2 of `CAP-DLV-adaptive-development` excludes only
  `devkit-spec`.
- `guides/install/bundle-recommendations.md:36` states that `devkit-dist` and the catalog suffice for the `agents`
  and `import` presets, so a consumer without `devkit-agt` is a documented installation.
- `devkit-agt` ships the auto-selected `harness` bundle (`packages/devkit/pyproject.toml:34-36`,
  `guides/INSTALL_GUIDE.md:87-91`). A package that depends on `devkit-agt` brings that bundle and its gates into
  every environment that installs it.
- `devkit bundle snapshot` accepts only a source project with empty runtime dependencies and only `devkit.bundles`
  entry points and refuses anything else with `BUNDLE_SNAPSHOT_UNSUPPORTED`
  (`CAP-DIST-in-repo-bundles` §8 rules 1 and 3;
  `packages/devkit-dist/src/devkit_dist/features/distribution/services/snapshots/source.py:57-66`). The catalog's
  project metadata meets both conditions today; no snapshot of it was run in this Planning.
- `devkit-mcp` mounts a `devkit.commands` group on `devkit-core` and `devkit-dist` alone
  (`packages/devkit-mcp/pyproject.toml:7-15`), so commands do not require `devkit-agt`.
- `ARCH-07-deployment` 1.1: an internal runtime requirement pins the dependency's actual version, and a package
  advances with the fixed point of its exact-pin reverse dependencies.

| Option | Evidence | Cost | Risk | Open |
| --- | --- | --- | --- | --- |
| 2a. `dependencies = []` in this unit; the first command adds its requirements | The catalog's own metadata (`packages/devkit-catalog/pyproject.toml:7`); no import exists | None in this unit; `PROP-adaptive-assignment-cli` edits `pyproject.toml` | None: the same closure as today | The base of the commands, at the time of this comparison |
| 2b. Pin `devkit-dist` (with `devkit-core`, `click`) in this unit | `devkit-mcp` precedent | Exact-pin and release-closure wiring for a package without code | The source stops being a snapshot source (`BUNDLE_SNAPSHOT_UNSUPPORTED`) in a unit that promises no behavior change | Same as 2a |
| 2c. Pin `devkit-agt` in this unit | `devkit-spec`, `devkit-docs`, `devkit-viewer` precedent; worktree and execution features become importable | As 2b | As 2b, and a consumer of `adaptive-dev:agents` or `adaptive-dev:import` on `devkit-dist` alone receives `devkit-agt` and the auto-selected `harness` bundle, against `guides/install/bundle-recommendations.md:36` | Whether the commands need harness features at all |

Recommendation: 2a. It is the only option that keeps the unit free of behavior change, and it leaves the base of
the commands open instead of fixing it before their design exists.

Decision (user): 2a for this unit, so the wheel is bundle-only at the move. The base is settled as `devkit-docs`,
which itself requires `devkit-agt` and so `devkit-dist`, and `PROP-adaptive-assignment-cli` introduces it together
with the first commands. Options 2b and 2c compared a base of `devkit-dist` or `devkit-agt` before that decision;
they and the list below remain as evidence and bind neither unit.

What this evidence shows for `PROP-adaptive-assignment-cli` (Q5 there):

- A requirement on `devkit-dist` and `devkit-core` keeps the `agents` and `import` presets installable without the
  harness; a requirement on `devkit-agt` changes what a `devkit-dist`-only consumer deploys.
- Any runtime requirement or `devkit.commands` entry point ends snapshot support for the `adaptive-dev` source
  (`BUNDLE_SNAPSHOT_UNSUPPORTED`).
- Rule 2 (installation without `devkit-spec`) holds under 2a, 2b and 2c alike, because none of them reaches
  `devkit-spec`.

## Set 3: a selected bundle whose distribution is missing (Q3)

Decision (user): no compatibility for existing selections. Nothing uses the `adaptive-dev` bundle outside this
repository, so the move has no migration path, no bridge and no guide step, and Development writes and tests none.
The recommendation Planning had made here, a documented installation step for an existing selection, is withdrawn
with its option table. The rest of this set is an observation of current `devkit-dist` behavior, kept because a
Development worktree can reach the same states. It is not a requirement, and no acceptance criterion rests on it.

What the code does when a configuration selects `adaptive-dev` and no installed distribution registers it:

| Command | Result | Evidence |
| --- | --- | --- |
| `devkit sync` (and every command that synchronizes) | Fails with `SELECTION_INVALID`, message `selected bundle is not installed: adaptive-dev`, `[FIX]` `uv run devkit remove adaptive-dev`, target `.devkit/config.toml`; nothing is written or deleted | `usecases/sync.py:233-239`, `services/installation/config.py:259-276` under `packages/devkit-dist/src/devkit_dist/features/distribution/`; `test_output_contract.py:116-122` |
| The same, when only the receipt records the bundle | Same code; the message adds `(deployed per .devkit/installation.json)` and the target is the receipt; the receipt bytes and the deployed files stay | `config.py:238-256`; `test_builtin_selection.py:241-262` |
| `devkit status` | Reports the same `SELECTION_INVALID` under `errors` with exit `1` | `usecases/status.py:209-220`; `test_builtin_selection.py:265-279` |
| `devkit add adaptive-dev` | Fails with `SELECTION_INVALID`, message `bundle is not installed: adaptive-dev`, `[FIX]` `uv run devkit list` | `test_output_contract.py:109-113` |
| `devkit remove adaptive-dev` | Succeeds without the package and deletes the bundle's deployed files | `CAP-DIST-content-packages` §2 (Teardown); `test_builtin_selection.py:254-259` |

If an environment holds two distributions that register `adaptive-dev`, every command fails with
`BUNDLE_PACKAGE_INVALID`, `duplicate installed bundle: adaptive-dev`
(`services/installation/discovery.py:97-99`; `test_sync.py:299`; `CAP-DIST-content-packages` §1). This is why the
catalog keeps no second registration.

For Development: this repository does not select `adaptive-dev` (`.devkit/config.toml`), so its own `devkit sync`
does not meet the first state. A test that runs `devkit add adaptive-dev` with the workspace interpreter (set 7)
would meet it in an environment that lacks `devkit-adaptive`, and an environment that still holds the catalog's
entry-point metadata from before the edit beside the new package would meet the second. Run `just init` after
editing the two `pyproject.toml` files and before any `devkit` command or test. A stale environment was not
reproduced in this Planning.

## Set 4: decision clauses (Q4)

| Document | Clause | Change | Kind |
| --- | --- | --- | --- |
| `ADR-adaptive-development-and-research` | §4 "Adaptive-dev bundle", first clause: the bundle is `adaptive-dev:core` in devkit-catalog with entry point `adaptive-dev = "devkit_catalog.adaptive_dev"` | Owner and entry point | Superseded in part by the new decision |
| `ADR-adaptive-development-and-research` | §4 "Adaptive-dev bundle", fourth clause: content-only catalog ownership and independent docs/catalog installation are preserved | For `adaptive-dev`: ownership moves; independent installation becomes devkit-docs plus `devkit-adaptive` without `devkit-spec`. For `deep-research` the clause stays | Superseded in part |
| `ADR-adaptive-development-and-research` | §3 "Adaptive-dev bundle": "Add a dedicated wheel" rejected because no runtime dependency required it; §2 driver "without another release wheel or runtime service" | The planned commands are the requirement the rejection named as missing; the wheel is accepted, a runtime service stays excluded | Superseded in part |
| `ADR-adaptive-development-and-research` | Approach policy, SDD adoption, discovery, materials and deep-research clauses; the names `adaptive-dev`, `/adaptive-dev`, `.devkit/adaptive-dev.md` | None | Stay in force |
| `ADR-skill-local-swarm-roles` | The sentence "`ARCH-05-2-components` restates catalog ownership" and the driver "Keep docs/catalog installation independent of SDD" | Its decision clauses name no owning wheel; the trace sentence is a reference repair | Wording repair, no supersession |
| `ADR-package-ownership-and-release-version` | "Application extensions use their own regular packages"; "No installed path belongs to two wheels" | The new package follows both | None |
| `CAP-DLV-adaptive-development` | §1 "catalog bundle"; §2 Scope Excluded "new wheel"; rule 2; the test paths of rules 1, 2, 18, 26, 27, 28 and 38 and of the closing paragraph; §4 "Install devkit-docs and devkit-catalog"; the scorer path; `entrypoints` | Restated to the new owner and paths. "No adaptive-development runtime or CLI is added" stays true for this unit and is `PROP-adaptive-assignment-cli`'s to change | Capability edit carried by the new decision |
| `ARCH-05-2-components` | 1.1: the catalog "owns the opt-in `adaptive-dev` and `deep-research` bundles"; the package list of section 1 | `adaptive-dev` leaves the catalog sentence; `devkit_adaptive` joins the application packages | Architecture edit |
| `ARCH-07-deployment` | The paragraph "The devkit-catalog wheel registers `adaptive-dev = ...`" and the installation command list of 1.1 | Restated to `devkit-adaptive` | Architecture edit |

Recommendation: one superseding decision limited to the owning wheel and its installation, promoted from
`PADR-adaptive-dev-distribution`. The decision on a command line or runtime belongs to
`PROP-adaptive-assignment-cli`, because this unit adds neither.

## Set 5: entry points (Q5)

A `devkit.commands` entry point names a click group that the root command mounts
(`packages/devkit-dist/src/devkit_dist/features/distribution/services/installation/engines.py:27`,
`ARCH-05-3-command-plugins`), so an "empty" registration is a visible `devkit adaptive` command without
subcommands: a new command in a unit that adds none. It also ends snapshot support (set 2).

Recommendation: register `adaptive-dev = "devkit_adaptive.bundles.adaptive_dev"` under `devkit.bundles` and nothing
else.

## Set 6: repository wiring (Q6)

`envelopes/scout-01.yaml` holds the inventory with its line evidence. The table lists what Development edits; a row
marked "no edit" was checked and needs none.

| Area | File | Edit |
| --- | --- | --- |
| New package | `packages/devkit-adaptive/pyproject.toml`, `README.md`, `src/devkit_adaptive/` | Metadata as in set 1 and set 2; version `0.1.6` beside the bundle's unchanged `0.1.6`; `[dependency-groups] dev = ["devkit-dist"]` with its workspace source, as `packages/devkit-starter/pyproject.toml:12-16` |
| Catalog | `packages/devkit-catalog/pyproject.toml:15`, `README.md:9` and `:26-49` | Remove the entry point, the table row and the "Adaptive development" section (moved to the new README) |
| Root project | `pyproject.toml:41`, `:87` | Add `./packages/devkit-adaptive/src` to pyright `extraPaths` and `packages/devkit-adaptive/tests` to pytest `testpaths`, as the catalog's entries; no `pythonpath` entry (the scorer test runs the script by path) and no dev-group entry (the catalog has none; `just init` syncs `--all-packages`, `scripts/module.sh:95`) |
| Lock | `uv.lock` | `uv lock` adds the editable member |
| Architecture data | `.devkit/architecture.toml:191-195` | Declare `devkit_adaptive` (`kind = "content"`, `data_roots = ["bundles"]`); remove `adaptive_dev` from the `devkit_catalog` data roots. `RULE-architecture` reports an undeclared source root (`tools/devkit-dev/src/devkit_dev/bundle/rules/architecture/rule.py:232-238`) |
| `just` | `scripts/_lib.sh:64-76` | Add the short name `adaptive devkit-adaptive`; the recipes discover modules from `packages/*/pyproject.toml` and need no edit |
| Affected tests | `scripts/affected_tests.py` | No edit: packages are discovered by directory (`:203-216`). The change selects the full suite, because it edits `pyproject.toml` files, `uv.lock` and a `tests/support` directory (`:49-50`, `:430-436`) |
| Citation test | `tools/devkit-dev/tests/integration/test_bundle_citations.py:17-33` | Import `devkit_adaptive.bundles` and add it to `SHIPPING`; otherwise the bundle's document citations are no longer checked |
| Consumer smoke | `tests/e2e/smoke.sh:54`, `:194`, `:228` | Install the `devkit_adaptive` wheel in the consumer; assert that `devkit-adaptive` provides `adaptive-dev`; set the bundles owned by `devkit-catalog` to the seven it registers after the move |
| Release | `scripts/releases/prepare.py:225` | The bundle lookup of set 8. Otherwise no edit: members come from the workspace (`identity.py:102-112`), and a package absent from the baseline counts as changed and takes the release version (`prepare.py:199-209`; `SPEC-selective-package-releases` 3.1). No installation variant is added (`install.py:12-22` has none for the catalog either) |
| CI | `.github/workflows/ci.yml:3-4` | Comment only; the workflows hold no package list |
| This repository's selection | `.devkit/config.toml`, `.devkit/installation.json` | No edit: `adaptive-dev` is not selected here |
| Root documents | `AGENTS.md:80`, `README.md:29-32`, `:70-71`, `:82`, `:205` | Add the package to the tables and lists |
| Guides | `guides/INSTALL_GUIDE.md:83-125`, `:140`; `guides/install/existing-repository.md:256-257`; `guides/install/new-repository.md:104-105`; `guides/install/adaptive-dev-sdd-adoption.md:21`; `guides/install/bundle-recommendations.md:35-36`, `:88` | Name `devkit-adaptive` as the package of `adaptive-dev` for a fresh installation and add its installation and upgrade commands beside the catalog's. No migration subsection and no edit to the `SELECTION_INVALID` row (`guides/INSTALL_GUIDE.md:217`) |
| Living Spec | Set 4, plus the `entrypoints` of `UC-advance-an-idea` (2), `UC-import-third-party-agent-assets` (2) and `CAP-HARN-agent-guidance` (1) and the body of `CAP-HARN-agent-guidance` lines 473-475 and of `ARCH-05-1-containers` (container diagram and 2.7) | `RULE-code-entrypoints` fails on a frontmatter path that no longer exists; body paths are not rule-checked |

Two existing inaccuracies sit on lines this change edits. `tests/e2e/smoke.sh:228` asserts five bundle names for
`devkit-catalog`, while `discover_bundles()` in the workspace environment returns eight (`command-design`,
`uiux-improve` and `design-explore` are missing from the assertion); by reading, `just smoke` fails there at the
base, and it was not run in this Planning. `.devkit/architecture.toml:195` lists a `host_observer` data root that
has no directory; the rule does not check data roots for existence.

## Set 7: tests (Q7)

| Test | Destination | Edit |
| --- | --- | --- |
| `packages/devkit-catalog/tests/integration/bundles/test_adaptive_dev.py` | `packages/devkit-adaptive/tests/integration/bundles/` | Bundle path constant (`:22`), package name `devkit-catalog` (`:30`), entry point value (`:182`) |
| `.../integration/bundles/test_adaptive_dev_documents.py` | Same directory | Bundle path constant (`:10`) |
| `.../integration/bundles/test_adaptive_import.py` | Same directory | Path constants (`:22-23`); the forbidden-word list (`:276`) gains `devkit_adaptive` |
| `.../integration/bundles/test_adaptive_behavior_scorer.py` | Same directory | None: the scorer path (`:8`) is relative to the tests directory |
| `packages/devkit-catalog/tests/support/adaptive_behavior_scorer.py` | `packages/devkit-adaptive/tests/support/` | None; `CAP-DLV-adaptive-development` restates the command path |
| `packages/devkit-catalog/tests/e2e/bundles/adaptive_dev/test_installed_consumer.py` | `packages/devkit-adaptive/tests/e2e/bundles/adaptive_dev/` | `ROOT` depth (`:13`); the wheel list (`:25-33`) builds `devkit-adaptive` instead of `devkit-catalog` |
| `packages/devkit-catalog/tests/integration/bundles/test_deep_research.py` | Stays | `ADAPTIVE_DEV` (`:21`) is derived from a static import of `devkit_adaptive.bundles`. The selector links a test to a package by ownership or a static import (`scripts/affected_tests.py:233-249`, `:391-424`), so a path-only read would drop the role-conflict test from the selection for a bundle change |
| `packages/devkit-catalog/tests/integration/bundles/test_bundles.py` | Stays | None: it iterates the catalog's own entry points |

The moved tests import `devkit.advisory`, `devkit_dist`, `distsupport` (the support directory of `devkit-dist`),
`click` and `yaml`, and none of `devkit_agt`, `devkit_docs` or `devkit_spec`, so the package's development group
needs `devkit-dist` only.

`just test-dist` runs `scripts/dist_only.sh`, which syncs `--package devkit-dist` into a temporary environment and
collects `packages/devkit-dist/tests` only (`scripts/dist_only.sh:13`, `:35-36`). It neither installs nor collects
`devkit-adaptive`, and no `devkit-dist` test names the catalog's `adaptive_dev` path, so the check is unaffected. With
`dependencies = []` the new wheel cannot bring `devkit-agt` into any environment.

`packages/devkit-spec/tests/e2e/bundles/spec/test_sdd_baseline_scenarios.py:95` runs `devkit add adaptive-dev` with
the workspace interpreter (`:111-112`), so it needs `devkit-adaptive` in the workspace environment, which
`just init` provides as it provides the catalog today.

A check that the bundle is unchanged needs no other checkout: the Git tree object of
`packages/devkit-catalog/src/devkit_catalog/adaptive_dev/bundle` at the base equals that of
`packages/devkit-adaptive/src/devkit_adaptive/bundles/adaptive_dev/bundle` at the head
(`git rev-parse <base>:<old path>` against `git rev-parse HEAD:<new path>`).

## Set 8: bundle version at the first release after the move

Release preparation computes each bundle's version from the baseline entry of the same package
(`scripts/releases/prepare.py:222-228`): a bundle keeps its version when its fingerprint equals the baseline's and
takes the release version otherwise or when the baseline has none. The fingerprint is computed relative to the
bundle root (`scripts/releases/identity.py:124-149`), so the moved tree has the fingerprint the baseline records
under `devkit-catalog`, but the lookup under `devkit-adaptive` finds nothing and the bundle advances.
`ARCH-07-deployment` 1.1 and `ADR-selective-package-versions` state that a bundle advances only when its own
enumerated content changes (MUST).

| Option | Evidence | Cost | Risk | Open |
| --- | --- | --- | --- | --- |
| 8a. Look up a moved bundle by name: when the package has no baseline entry for the bundle, use the baseline package that registered a bundle of that name | Bundle names are unique across installed packages (`CAP-DIST-content-packages` §1); the lookup is one expression at `prepare.py:225`; the fixture of `test_selective_releases.py:44-110` already builds a package with a bundle | One edit and one test case in the release tooling | A regression in release preparation, bounded by the new and existing cases | None |
| 8b. Accept the advance and state it: a bundle first registered by a distribution takes the release version | No code | A clause in the PADR that makes an exception to a MUST of `ARCH-07-deployment` 1.1 and a partial supersession of `ADR-selective-package-versions` | A release contract changed to fit one lookup; a bundle version changes without an asset change | None |
| 8c. No change | None | None | The first release after the move violates the MUST unless the bundle's text changed before it | Not viable as a plan |

Recommendation: 8a. The contract stays as accepted and the implementation follows it.
