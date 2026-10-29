---
sources:
  ADR-package-split-and-namespaces: a098e6f78c36f83d9c0f0665cd365616f678f7a2
  CAP-DIST-agent-projections: a80245135911b3cc82c894d3d4bac7acd895cab4
  CAP-DIST-content-packages: 71d426703b854a24bdce4cd0c44b130ed8a106dc
  CAP-DIST-context-and-playbooks: 73e324739a17d8af4b885dce3d6cdf2593762fc0
  CAP-DIST-in-repo-bundles: 54b713a2bf73ff8a6684acb70990956e401585c5
  CAP-DIST-manifest-spec: 44c8ec1792cd306367a6cb09a3e7ef580ee7c2c9
  CAP-DIST-sync-and-transactions: 2759dc504dc98f758acf3b168122c97f35bd1dd6
  CAP-DIST-workspace-ownership: 11ecf337d2748f5d3f69272dfaf004bd8c83d9ba
  UC-reconcile-living-spec-drift: 972538db7ca3eccccada61d606ed7a176a4effe0
  UC-route-development-intent: b3ee3ac9c76d14a4b97f0645eef8954f339330d5
title: Distribution
---

# Distribution

<!-- handbook:provenance -->
> Snapshot of devkit `v0.1.4` at source commit `5e71d74c8e5a`, generated 2026-10-26. The Living Spec under `docs/` prevails on any conflict; this page is not updated between refreshes.
<!-- /handbook:provenance -->

<!-- handbook:generated toc -->
- [devkit handbook](../README.md)
- [Concepts](../concepts.md)
- [Adopt devkit in an existing repository](../journeys/adopt-in-an-existing-repository.md)
- [Drive development to integration](../journeys/drive-development-to-integration.md)
- [Find the right documents](../journeys/find-the-right-documents.md)
- [Handle delivery problems and exceptions](../journeys/handle-delivery-problems-and-exceptions.md)
- [Incubate and hand off a proposal](../journeys/incubate-and-hand-off-a-proposal.md)
- [Inspect weekly repository progress](../journeys/inspect-weekly-repository-progress.md)
- [Keep the Living Spec consistent](../journeys/keep-the-living-spec-consistent.md)
- [Publish a weekly report](../journeys/publish-a-weekly-report.md)
- [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
- [Resolve stale activity branches](../journeys/resolve-stale-activity-branches.md)
- [Review and refactor accumulated slop](../journeys/review-and-refactor-accumulated-slop.md)
- [Route a development request](../journeys/route-development-intent.md)
- [Run parallel work safely](../journeys/run-parallel-work-safely.md)
- [Advisories](advisory.md)
- [Agent-first CLI toolkit](cli.md)
- [Collaboration](collaboration.md)
- [Compact command output](compact.md)
- [Delivery](delivery.md)
- [Documents](documents.md)
- [Commit gates](gate.md)
- [Generated Files](generated.md)
- [Governance rules](governance.md)
- [Harness](harness.md)
- [Host](host.md)
- [Integration](integration.md)
- [MCP](mcp.md)
- [Search](search.md)
- [Traceability](traceability.md)
- [Viewer](viewer.md)
- [Worktree](worktree.md)
- [Decisions](../decisions.md)
- [Changes](../changes.md)
- [Glossary](../glossary.md)
<!-- /handbook:generated -->

Distribution is how agent assets (skills, subagents, instructions, playbooks, rules, workflows, gates, hooks and
documents) get from a Python package into your repository and into each coding agent's own directories. You install
packages with `uv`, pick bundles in `.devkit/config.toml`, and run `uv run devkit sync`. It writes managed copies,
native projections and a committed receipt in one transaction. The terms bundle, sync and receipt are explained in
[Concepts](../concepts.md).

The model in one paragraph: a **bundle** is a directory with a `bundle.toml` manifest, shipped inside a wheel that
registers it under the `devkit.bundles` entry point. Installing the wheel makes the bundle *available*; a bundle is
*selected* when `config.toml` names it or when it declares `auto_select`. `devkit sync` deploys the selected
presets, projects skills and subagents for each agent, and records every file it owns in
`.devkit/installation.json`.

## Install devkit and pick bundles

You declare exactly one devkit requirement in your dev dependencies: `devkit-dist` for distribution only, or
`devkit-agt` when you want the harness (rules, workflows, commit gates, worktrees, integration). `devkit-agt`
depends on `devkit-dist` at the same version, so never declare both (`ADR-package-split-and-namespaces`). Always run
the tool as `uv run devkit ...` from the project environment; a globally installed tool cannot see your project's
content packages. Setting devkit up in a repository that already has code is the journey
[Adopt in an existing repository](../journeys/adopt-in-an-existing-repository.md).

```bash
uv run devkit sync               # deploys auto-selected bundles (devkit, advisory, harness)
uv run devkit add starter        # selects a bundle that is not auto-selected, then syncs
uv run devkit add advisory:python  # joins another preset of a bundle
uv run devkit remove starter     # deselects; unchanged deployed files are removed
```

Things worth knowing when you choose:

- `devkit add` records the *resolved* preset name, so an upstream change to `default_preset` never changes your
  explicit choice. An auto-selected bundle with no entry follows its current default.
- An auto-selected bundle you do not want is opted out with `devkit remove <bundle>`, which writes
  `<bundle> = false`.
- Every sync lists installed but unselected bundles under `unselected`; a `BUNDLE_UNSELECTED` notice announces a
  new one once per clone.
- Upgrade with `uv lock --upgrade-package <package>` and then `uv run devkit sync`. Removal is always explicit: a
  deployed bundle whose package disappeared fails the sync (`SELECTION_INVALID`) instead of deleting committed files.

The built-in bundles (`devkit`, `advisory`, `git-commits`, `harness`, `authoring`) and the opt-in
`response-style` and `maintenance` bundles of `devkit-catalog` are listed in
[CAP-DIST-content-packages](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-content-packages.md),
together with the dependency rules for layering one content package on another. Methodology layers add their own
auto-selected bundles the same way: `devkit-docs` ships `docs` and `devkit-spec` ships `spec`
([Harness](harness.md)).

## What sync writes and what you commit

| Path | Owner | Commit it? |
| --- | --- | --- |
| `.devkit/config.toml` | you | yes |
| `.devkit/installation.json` (the receipt) | devkit | yes |
| `.devkit/overrides/` | you | yes |
| root `AGENTS.md` | you, except the `DEVKIT:START/END` block | yes |
| seeded files (written once, for example a docs skeleton) | you, after the first write | yes |
| `.devkit/managed/`, `.devkit/transient/` | devkit | no (ignored) |
| `.agents/`, `.claude/`, `.codex/` projections | devkit | your repository's choice |

devkit only touches files the receipt records. A planned write onto an unrecorded existing file stops the sync
before any byte is written (`SYNC_CONFLICT`), unless the file is already identical. A file you edited that devkit
still wants to deploy is also a `SYNC_CONFLICT`; one it no longer wants is left on disk as an orphan
(`ORPHAN_LEFT`). `CLAUDE.md` is never written: point it at `AGENTS.md` yourself. Details are in
[CAP-DIST-workspace-ownership](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-workspace-ownership.md).

## Keep clones, worktrees and CI in step

The receipt, the guidance block and seeded files are shared through Git; the managed copies are rebuilt per clone.

- A fresh clone, a new task worktree and CI run `uv sync` and then `uv run devkit sync --locked`. It only restores
  ignored copies to what the committed receipt records. If the receipt itself would change, it writes nothing and
  exits `1` with `RECEIPT_STALE`: someone changed a bundle source, the lock or the selection without committing the
  receipt. Run a plain `uv run devkit sync` and commit the result; an agent does not retry it away.
- `uv run devkit sync --check` is the read-only "is anything pending?" check: when a sync is needed it exits `1`
  with `NOT_SYNCHRONIZED`, whose fix is `uv run devkit sync`. `--dry-run` shows the planned actions, including what
  post-sync extensions such as the commit-gate hooks would change.
- `uv run devkit status` reports the installed state, errors and drift. Installed packages can add read-only checks
  to it; with `devkit-agt` it also warns about broken commit-gate hooks ([Commit gates](gate.md)).

## When a sync stops

Every writing command takes a project lock, journals its writes and replaces files atomically, so a failure never
leaves a half-written workspace.

| Code | What happened | What you do |
| --- | --- | --- |
| `LOCK_HELD` | another writer holds the project lock | wait and rerun |
| `TRANSACTION_PENDING` | an earlier sync was interrupted | `uv run devkit recover` |
| `RECOVERY_BLOCKED` | a file changed after the interrupted sync | follow the `[FIX]`; decide which content to keep |
| `SYNC_CONFLICT` | an unowned or user-edited file is in the way | move the file, or turn your edit into an override |
| `WORKSPACE_UNSAFE` | a symlink or file stands where devkit writes | move it out of the way |
| `HARNESS_ENGINE_MISSING` | rule, gate or workflow assets deployed without `devkit-agt` | add `devkit-agt` if you want them run |

The full transaction steps, the notice list and post-sync extensions are in
[CAP-DIST-sync-and-transactions](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-sync-and-transactions.md).

## Change an upstream asset without forking it

Never edit `.devkit/managed/`. To change one asset, create an override, a set of complete files you own:

```bash
uv run devkit override create starter:development   # copies the files to .devkit/overrides/starter/
uv run devkit override list                         # tracked overrides and their drift
uv run devkit override diff starter:development     # what upstream changed, what you changed
uv run devkit override accept starter:development   # record the new upstream as your baseline
uv run devkit override remove starter:development   # go back to upstream
```

When upstream changes an overridden asset, sync reports `OVERRIDE_DRIFT` with the `override diff` and
`override accept` commands to run. Under the default `override_drift = "warn"` it is a warning and the sync
continues; set `"block"` where an override shadows governance content, and the sync stops before writing anything
until you decide. `devkit status` follows the same policy. After you merge the upstream change into your files,
`override accept` records the new baseline and synchronizes in one step (under `"block"`, only once no other override
still drifts). `devkit remove <bundle>` keeps the bundle's override directory and says so with `OVERRIDE_RETAINED`.
To change a distributed rule's settings, use `[rules]` in `config.toml` instead of an override.

## Load context and find playbooks

Startup files stay small; guidance is loaded in stages
([CAP-DIST-context-and-playbooks](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-context-and-playbooks.md)):

- The root `AGENTS.md` block holds orientation only: installed bundles, the context rule, entry skills and short
  guidance pointers.
- `uv run devkit get-context <bundle>` returns a bundle's constitution, the headers of its instructions and, when
  the bundle declares a context document directory, the title and summary of each project file in it (the `docs`
  bundle lists `docs/steering/` this way). Every deployed skill carries a prerequisite telling the agent to run it
  once per bundle per agent context.
- Playbooks are occasional procedures that `get-context` never lists. You invoke the generated `devkit-playbook`
  skill explicitly; it runs `uv run devkit playbook search "<query>"` and reads the chosen body.
  `uv run devkit playbook get <bundle>/<playbook>` returns one playbook exactly, by asset ID or declared alias.

Ordinary task wording never starts a playbook. An entry skill such as `spec` may offer one candidate at intake, and
your confirmation is the explicit invocation; see [Route development intent](../journeys/route-development-intent.md)
(`UC-route-development-intent`) and [Reconcile Living Spec drift](../journeys/reconcile-living-spec-drift.md)
(`UC-reconcile-living-spec-drift`). Search ranking is described in [Search](search.md).

## Choose which agents get skills and subagents

By default every supported agent (`codex`, `claude-code`, `antigravity`) is a target; `agents` in `config.toml`
narrows the list, `uv run devkit sync --agent <name>` sets it and `--no-agents` turns projection off. Skills land in
`.claude/skills/` or the shared `.agents/skills/`; subagents in `.claude/agents/`, `.codex/agents/` or
`.agents/agents/`. A skill declared `invocation = "user"` gets each agent's native "explicit invocation only"
setting. A subagent ships either native files per agent or one host-neutral role contract rendered per agent. The
matrix and the role-contract format are in
[CAP-DIST-agent-projections](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-agent-projections.md).

By default a role contract runs on whatever model and effort the host would give it. To choose, set a subagent
model level: `inherit`, `minimal`, `compact`, `standard`, `deep` or `maximal`, each mapped to a native model and
effort per agent. A contract may name its own level (devkit's `scout` asks for `compact`); the project decides in
the tracked `[subagents]` table, with `default_level`, per-host `levels` remappings and per-role `roles` overrides:

```toml
[subagents]
default_level = "inherit"
[subagents.roles."spec:scout"]
level = "standard"
```

Run `uv run devkit sync` after changing it. A level is a resource preset, not a quality guarantee: the host and
your account still decide what actually runs.

## Personal preferences in one checkout

Two tables of `config.toml` are shared policy rather than preference: `[subagents]` above, and `[development]
approach`, which chooses between spec-driven delivery (`sdd`, the default) and `incubation` for the whole project
(see [Harness](harness.md)). `uv run devkit config show` reports both.

`.devkit/config.local.toml` is an ignored file for this checkout only. It accepts a short list of keys:
`[execution] environment`, `[mcp] register`, `[presentation] language`, `[shared] adapter`, `[playbooks]` search
settings and bundle variables. Anything else is `CONFIG_LOCAL_KEY_FORBIDDEN`. Personal values may change only the
bytes of skills, instructions, subagents and playbooks at ignored destinations; the receipt stays canonical.
`[subagents]` and `[development]` are rejected there too, since every clone has to agree on them.
`uv run devkit config show --effective` shows each value and where it came from, and
`uv run devkit config template` adds the commented template keys your `config.toml` lacks without changing a line.

## Author a bundle

A bundle manifest declares assets by `(kind, id, source)`, presets, and optional template variables. Run
`uv run devkit bundle validate <source>` and `uv run devkit bundle plan <source> --agent <name>` on a source
directory before it is installed. Key points from
[CAP-DIST-manifest-spec](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-manifest-spec.md):

- The schema is strict: unknown keys are errors, and slugs, versions and source paths are validated.
- `default_preset` is what `devkit add <bundle>` selects; `auto_select` deploys the bundle as soon as its package is
  installed. Use it only for content nearly every installer wants.
- A `guidance` asset adds at most 300 bytes of list items to the root `AGENTS.md` block.
- A seeded `document` is written once to a `target` and then belongs to the project.
- `context_documents` names one project directory whose Markdown titles and summaries `get-context` lists.
- A role contract may set `level` instead of native model and effort fields; combining the two is invalid.
- Explicit `.md.jinja` files render in a sandbox with declared `[variables.*]` inputs and the
  `execution.environment` value; ordinary Markdown stays literal.

### Ship assets that belong to your repository

For a repository-specific rule, skill or playbook, create an ordinary content package under `tools/<repo>-devkit/`
and add it to the dev dependency group next to your devkit requirement; there is no separate local asset directory.
Edit its sources, run `uv run devkit sync`, and commit the source change together with the updated receipt. A stale
receipt fails Git snapshot gates, so rule edits always travel with their receipt. The layout, the `pyproject.toml`
and the decision table for overrides versus in-repository bundles are in
[CAP-DIST-in-repo-bundles](https://github.com/mjkimR/devkit/blob/v0.1.5/docs/capabilities/distribution/CAP-DIST-in-repo-bundles.md).

## Capabilities in this area

| Capability | Read it when you need |
| --- | --- |
| `CAP-DIST-content-packages` | wheels, entry points, installation, built-in bundles, standalone signals |
| `CAP-DIST-manifest-spec` | the `bundle.toml` schema, asset kinds, validation, templates |
| `CAP-DIST-sync-and-transactions` | the receipt, selection, transactions, locked sync, shared policy and local configuration |
| `CAP-DIST-workspace-ownership` | who owns which path, the guidance block, seeded files, overrides and drift |
| `CAP-DIST-agent-projections` | per-agent destinations, invocation settings, role contracts, subagent model levels |
| `CAP-DIST-context-and-playbooks` | `get-context`, playbook search and exact retrieval |
| `CAP-DIST-in-repo-bundles` | packaging a repository's own assets |
