---
id: CAP-DIST-content-packages
title: "Content Packages"
summary: "Content wheel packaging, bundle distribution and dependency boundaries, the devkit-dist and devkit-agt installations and their built-in bundles, including the auto-selected harness bundle, opt-in response-style instructions and standalone signals."
area: distribution
status: active
entrypoints:
  - packages/devkit-dist/src/devkit/distribution/installation/discovery.py
  - packages/devkit/src/devkit/harness_guide/
  - packages/devkit-catalog/src/devkit_catalog/response_style/
created_at: 2026-10-17
---

# [CAP-DIST-content-packages] Content Packages

Bundles reach a project as Python packages installed with `uv`; `devkit` relies on standard packaging instead of a
registry, resolver or download cache of its own. The bundle itself is specified in the
`CAP-DIST-manifest-spec`; repository-owned bundles in `CAP-DIST-in-repo-bundles`.

## 1. Content Wheel Contract

A content wheel registers a resource module under the `devkit.bundles` entry-point group:

```toml
[project.entry-points."devkit.bundles"]
team = "package_b_playbooks"

[tool.hatch.build.targets.wheel]
packages = ["src/package_b_playbooks"]
```

```text
src/package_b_playbooks/
  __init__.py               # empty; no runtime side effects
  bundle/                   # the bundle: bundle.toml, optional AGENTS.md, asset sources
```

- The entry point value names an importable module, not a callable; the bundle lives in its `bundle/` directory.
- The entry point name is the bundle name (`team` above registers the bundle `name = "team"`); a mismatch makes the
  package unusable (`BUNDLE_PACKAGE_INVALID`). The name identifies the bundle even when the package cannot be loaded.
- Loading the module runs ordinary module initialization, so `__init__.py` must have no runtime side effects.
- A sync reads files only through `importlib.resources.as_file`; it never executes or imports rule code.
- Bundle names are unique across the installed packages; two packages declaring the same name are an error
  (`BUNDLE_PACKAGE_INVALID`) for every command.
- An installed package that cannot be used (its module fails to import, its bundle is invalid, its entry point is
  malformed or misnamed) stops only what needs it: when the project selects its bundle, `sync`, `add`, `list` and the
  override commands fail with `BUNDLE_PACKAGE_INVALID` and `devkit status` reports it under `errors`; otherwise each
  of them reports it as a `BUNDLE_PACKAGE_INVALID` warning and continues, so `devkit remove <bundle>` can still
  deselect it while the package is upgraded or uninstalled.
- A repository without Python code (a prompt collection, a Go tool) can map its own layout into a content wheel at
  build time with Hatch `force-include`.
- The same wheel may also mount commands under `devkit` through the `devkit.commands` entry-point group
  (`ARCH-05-3-command-plugins`).

## 2. Installation and Lifecycle

```bash
base=https://github.com/mjkimR/devkit/releases/download/v<version>
uv add --dev "devkit-dist @ $base/devkit_dist-<version>-py3-none-any.whl" \
  "devkit-advisory @ $base/devkit_advisory-<version>-py3-none-any.whl" \
  "devkit-starter @ $base/devkit_starter-0.1.0-py3-none-any.whl"
uv run devkit sync               # deploys auto-selected bundles with their default preset
uv run devkit add starter        # a bundle without auto_select: records the selection and synchronizes
```

Run `devkit` through `uv run` from the project's environment. A globally installed tool runs in an isolated
environment where `importlib.metadata` cannot see the content packages of the project; it names the owner of the
`devkit` executable and adds what it needs: `uv tool install <devkit-dist requirement> --with <devkit-agt
requirement>`, each a wheel path or a full Git requirement
(`devkit-dist @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-dist`), never a bare package
name the default index would resolve (`ADR-dist-command-composition`).

- **Upgrade**: `uv lock --upgrade-package <package>`, then `uv run devkit sync`.
- **Teardown**: `uv run devkit remove <bundle>`, then `uv remove --dev <package>`. Removal is always explicit: a
  deployed bundle whose package is no longer installed is a sync error (`SELECTION_INVALID`), whether an entry or
  `auto_select` selected it, so a partial environment never deletes committed files. `devkit remove <bundle>` also
  works after the package is gone; for a bundle without an entry it then writes no `false`.
- **Clean checkout**: `uv sync`, then `uv run devkit sync --locked`, which rebuilds ignored managed and native files
  from the installed wheels and fails (exit `1`, `RECEIPT_STALE`) instead of changing the committed receipt
  (`CAP-DIST-sync-and-transactions`).

## 3. Dependency Boundaries

Availability follows Python dependency resolution; deployment follows the bundle's `auto_select` and the consumer's
`.devkit/config.toml` (`CAP-DIST-sync-and-transactions`). When a content package
`packageB` depends on `packageA`:

- **`[project.dependencies]`** puts `packageA` in the wheel's `Requires-Dist`. A consumer that adds `packageB` gets
  `packageA` installed as well, and its bundle is treated as if the consumer had added it: deployed with its default
  preset when it declares `auto_select`, otherwise listed under `unselected` until `devkit add <bundle>`. Use this to
  layer bundles (a `team-backend` bundle on top of a `company-base` bundle).
- **`[dependency-groups].dev`** is omitted from the built wheel, so `packageA` is neither installed nor discovered
  downstream. Use this for tooling and tests local to the authoring repository.

A consumer that does not want an auto-selected bundle opts it out with `[presets] <bundle> = false`
(`devkit remove <bundle>` writes it).

## 4. The devkit Wheels and Their Built-in Bundles

The CLI ships in two wheels released in lockstep with `devkit-advisory` (`ADR-dist-foundation-ownership`,
`ADR-dist-bundles-compatibility`):

- **`devkit-dist`** owns the `devkit` executable, distribution (this capability area), native host hooks, context
  loading and playbooks. Installed alone, it deploys every asset kind and runs none of the harness.
- **`devkit-agt`** depends on `devkit-dist` at the same version and adds the harness engines (rules, workflows,
  commit gates, task worktrees, generated files, integration, `devkit run`), mounted as `devkit.commands` plugins
  (`ARCH-05-3-command-plugins`).

A project declares exactly one of them as its devkit requirement, `devkit-agt` when it uses the harness; a
release-wheel installation of `devkit-agt` also names the `devkit-dist` and `devkit-advisory` wheels of the same release,
because no index serves them.
Bundles registered by either wheel are built in (`builtin` in `devkit list` and `devkit status`), so the
`BUNDLE_AUTO_SELECTED` notice never names them:

| Bundle | Wheel | Selection | Contents |
| --- | --- | --- | --- |
| `devkit` | `devkit-dist` | Auto-selected (`core`, its only preset) | The consumption contracts and instructions of distribution; it names no harness command as a directive, and describes rule, gate and workflow assets only as kinds it deploys. |
| `advisory` | `devkit-dist` | Auto-selected (`core`); opt-in `python` | The Agent Advisory Protocol guides; `python` adds the library guide and `RULE-advisory-unique-code`. |
| `git-commits` | `devkit-dist` | Opt-in | Commit message conventions and their `AGENTS.md` pointer. |
| `harness` | `devkit-agt` | Auto-selected (`core`); opt-in `run`; `harness = false` opts out | The constitution with the rules-and-gates contract and the snapshot-gate contract (snapshot gates trust the committed receipt), the instructions `harness-consumption` (configuration tables of the engines, workflows, rules and commit gates), `harness-assets` (running and testing rule, gate and workflow assets, rules of an in-repository bundle in Git snapshot gates) and `devkit-run`; the `run` preset adds the `run-pointer` guidance line. |
| `authoring` | `devkit-agt` | Opt-in | Size rules and restructuring playbooks for skills and agent guides. |

The `harness` bundle is the bundle of this capability; the `devkit-spec` capability area of the same name
(`CAP-HARN-agent-guidance`) is unrelated to it. The `run` preset and the `devkit-run` and `run-pointer` assets belong
to `harness`; the `devkit` bundle has no `run` preset, so a `devkit:run` selection fails with `SELECTION_INVALID`
(whose fix lists `devkit:all, devkit:core`) and a project selects `harness:run` instead, and `devkit:all` deploys no
`devkit run` guidance. No alias preset exists (`ADR-dist-bundles-compatibility`).

### 4.1 Standalone Signals

An installation without `devkit-agt` reports what it cannot run instead of failing silently, with one directive
(`HARNESS_INSTALL_FIX`): in a project, replace the `devkit-dist` requirement with
`devkit-agt @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit` in the same dependency group; for
a tool installation, `uv tool install --reinstall '<devkit-dist requirement>' --with '<devkit-agt requirement>'`.

- A harness command name (`rules`, `workflow`, `gate`, `worktree`, `generated`, `integration`, `run`) that no
  installed command provides answers with `HARNESS_COMMAND_UNAVAILABLE` (exit `2`; `ARCH-05-3-command-plugins`).
- Deployed `rule`, `gate` or `workflow` assets with no `devkit.commands` entry point named `rules`, `gate` or
  `workflow` raise a `HARNESS_ENGINE_MISSING` warning from `devkit sync` and `devkit status`
  (`CAP-DIST-sync-and-transactions`). The first-party bundles that reach a standalone installation ship no such asset
  except the opt-in `advisory:python` rule.

Engine presence is read from entry point names only: `devkit-dist` never imports or locates a harness module.

## 5. Opt-in Response Style

The `devkit-catalog` wheel makes `response-style` available without selecting it. `devkit add response-style`
deploys one portable skill and one guidance pointer through the existing native projections; it adds no
host-specific style or alternate style preset.

The skill's ordinary reply format is `→ **Core sentence.** Supporting explanation`, with blank lines between
points. The first sentence gives the overall answer, recommendation or current result, including essential
conditions or what is missing when the answer is unknown. Later points state distinct conclusions and provide
needed reasons, conditions and examples, without fixed block or sentence counts. Requested depth determines
the explanation needed. Decision-relevant facts, quantities, units, identifiers, qualifications, risks and
tradeoffs remain attached to their claims; omission or distortion is the more serious failure, and unnecessary
repetition must not obscure required information. Concise reporting does not reduce required work.

Required user and workflow formats take precedence over the ordinary point format, including every required
field. Artifact-only requests receive the artifact without conversational framing. Work reports distinguish
what is finished from what remains, give actual verification and material limitations, and put a necessary
user decision at the end. Style instructions authorize no invented actions or outcomes.

The `language` variable opts into `default_from = "presentation.language"`, retaining its ordinary `auto` default.
The shared/local presentation preference supplies it only when no bundle-specific value exists. A shared explicit
`[bundles.response-style.variables] language = "auto"` still wins over local `[presentation] language = "ko"`.
Remove the consumer override to inherit, or set a personal bundle variable to override it locally. Existing free-text
consumer overrides remain supported and never control MCP approval language. Rerun sync to update rendered assets;
MCP instead rereads the owning-workspace preference for each form. See `CAP-DIST-sync-and-transactions`.

The `language` variable is rendered by Jinja: `auto` follows the current request; a configured value supplies
the conversation default; an explicit user language request overrides either. Repository and task language
requirements govern deliverables. Korean replies retain natural sentences, a consistent polite register and
exact technical identifiers.

The single pointer inserted into `AGENTS.md` stays within `CAP-DIST-manifest-spec`'s 300 UTF-8 bytes per fragment,
including LF. This is not a limit on the whole guide or skill body. Deployment checks verify rendered text and
projections; the authored examples in `MAT-response-style-rewrite-draft` illustrate the accepted design and do
not measure model adherence, reader comprehension, comparative quality or host compaction behavior
(`ADR-response-style-adaptive-replies`, `ADR-response-style-measurement`).
