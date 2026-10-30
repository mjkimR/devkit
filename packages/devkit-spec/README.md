# devkit-spec

Spec-driven development for AI coding agents, built on [devkit](../../README.md). One Python package ships:

- the `spec` bundle (`devkit.bundles`): instructions, skills, workflows, rules, templates and an opt-in docs skeleton;
- the `devkit spec` command group (`devkit.commands`), mounted under the project's `devkit` executable.

Devkit provides asset distribution, rule/workflow/gate engines, task worktrees and the Agent Advisory Protocol.
[devkit-docs](../devkit-docs/README.md) provides the Living Spec document model (kinds, IDs, references,
namespaces), the `devkit docs` commands and the document rules' implementations. This extension adds proposals,
spec bundles, code entrypoints, scope registry, the lifecycle rules and SDD guidance; the `spec` bundle ships every
rule asset, including the document rules, whose wrappers import devkit-docs (`ADR-document-package`). Contracts
start at `CAP-HARN-command-mount` and `CAP-HARN-agent-guidance`; repository documentation starts at
[docs/README.md](../../docs/README.md).

## Use in a project

Install from this monorepo's package subdirectory. uv resolves devkit-docs (the document layer it builds on),
devkit-agt (the harness), devkit-dist, devkit-core, devkit-cli and devkit-advisory from the same commit. devkit-spec does not depend on devkit-mcp and
registers no MCP service: proposal acceptance and handoff run through the `devkit spec proposal` CLI (the optional
shared artifact tools are in [MCP runtime](../../guides/install/mcp.md)):

```bash
uv add --dev "devkit-spec @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-spec"
uv run devkit sync                   # deploy docs:core and spec:core
uv run devkit add docs:docs-skeleton  # optional: seed absent docs/ files, then leave them project-owned
uv run devkit spec --version         # [VERSION: devkit-spec <version>]
```

For release wheels, install the extension and its base dependencies explicitly because they are not hosted on a
package index; add the matching `devkit-mcp` wheel only for the optional shared artifact MCP tools. See
[Releasing](../../README.md#releasing).

A project opts out of the bundle with `[presets] spec = false` in `.devkit/config.toml`. `uv run devkit config
template` writes the supported keys as commented defaults, including this extension's `[tool.spec]` tables
(worktree, depth escalation, scope and feedback) and devkit-docs' `[tool.docs]` namespaces.

## Adopt SDD from adaptive development

Use the explicitly invoked or confirmed `sdd-baseline` playbook for a verified retained-product baseline before SDD
activation. Keep `[development] approach = "adaptive-dev"` while installing/selecting spec assets and preparing
current documents and actual check/usage evidence. Retrieve it with `uv run devkit playbook get spec/sdd-baseline`.
Package selection alone does not activate SDD; the ready source, scope and policy effects require matching user
authority. Configuring a missing spec provider or a necessary project-to-spec integration provider change is an explicit effect rather than an implicit
settings profile. See the [adaptive-development adoption guide](../../guides/install/adaptive-dev-sdd-adoption.md) and
`CAP-DLV-sdd-baseline-adoption`. Legacy rule containment remains the separate `brownfield-adoption` path.

## Development

Work from the monorepo root. Workspace sources link the local devkit packages:

```bash
just init                     # install all workspace packages and development dependencies
just lint-check devkit-spec
just check devkit-spec
just test devkit-spec
just rules-check              # repository-wide documentation and governance checks
just smoke                    # wheel installation, CLI mounting, bundle deployment and seeded document discovery
```

Python 3.12 or later, macOS or Linux. The [development guide](../../docs/development/setup.md) lists prerequisites.

Repository roadmaps use global `docs/roadmap/MS-<slug>.md` for planned/active milestones and
`docs/roadmap/_archive/MS-<slug>.md` for done/dropped history. Close/drop/reopen combine their existing
user decision, applicable assertions/disposition and movement in one commit; identities stay unchanged. Assign one with
`devkit spec proposal new <slug> --milestone MS-<slug>`; only direct PROP anchors are members.
Handoff does not carry milestone metadata into specs, and historical SPEC metadata is ignored.
Direct specs have no milestone creation option;
`proposal new --decomposed-from PROP-<parent>` preserves the original draft's identity. The Backlog and spec-next
skills own lifecycle decisions and next-work ordering. `devkit spec proposal accept <slug> --by user` records the
user's acceptance in one step, after Planning or, with `--direct`, for an eligible draft on the base checkout without
Planning. See `CAP-DOCS-document-model`, `CAP-DLV-proposal-planning` and `CAP-HARN-agent-guidance`; GitHub issue
integration is excluded.

### Worker result inspection

`devkit spec worker inspect --format json` collects compact committed worker evidence (`--details` includes full wrapped results and envelope history): range and scope information, cleanliness,
envelope validation, rules and workflow checks. Inputs derive from the activity worktree and committed records;
`--unit`, `--base`, `--head`, `--scope` (repeat) or `--scope-file` (one prefix per line), and `--base-checkout` replace
individual inputs. `--rules-base` overrides cumulative rules comparison, whose default is the recorded base-branch
merge base independent of the accepted-turn `--base`; manual inspection without a recorded base uses a labelled audit-base fallback.
Absent optional reconciliation adds no scope; malformed present records remain not-run. Scope overrides replace the entire scope. Results include provenance and reviewer-ready compared
heads and changed paths. Exit 0 means no failed check, 1 a negative check, 2 an invalid invocation or unresolved
required input; unavailable checks are explicitly not-run. The Host retains scope and acceptance authority.
The command writes and repairs nothing. See `CAP-DLV-delivery-workflows`.

## Package structure

`bundles/spec/bundle/` contains distributable agent assets. Runtime behavior lives in `features/`, grouped by proposals,
scope, entrypoints, worker inspection, delivery integration, policy and governance (the lifecycle rules). Each feature keeps
its CLI and MCP adapters beside its use cases, services, repositories and models; only layers the feature needs
are present. `cli.py` composes the command group. `base/errors.py` owns shared advisory contracts,
and `adapters/cli.py` holds the sentinel output the commands share.

CLI and MCP execution entrypoints implement `devkit_core.base.usecase.BaseUseCase` with a typed
`execute` method. Internal parsing, rendering and composition helpers remain functions. Constructors wire
dependencies and runtime state; approval and effect checks stay in the existing execution paths.
Delivery owns cross-feature orchestration: its Host-authorized proposal CLI group (acceptance and handoff)
combines proposal operations, worktrees and scope registration. The shared
handoff operation merges registration notices and permits a cancellation guard between the handoff and registry
mutation. Proposal mutation remains in the proposals feature. Scope repositories own Git observations and token
persistence; scope models retain the deadline and value contracts. Policy models hold storage-independent scope
configuration. Shared contracts do not depend on feature code, and domain code does not import CLI or MCP
adapters. Public command names, MCP tool names and bundle identifiers remain stable.

Tests mirror runtime features under `tests/unit/features/` for pure parsing and transformation, and
`tests/integration/features/` for filesystem, Git and component wiring. Bundle rendering and guidance contracts
live under `tests/integration/bundles/spec/`; installed entry-point contracts are under
`tests/integration/package/`. Shared fixtures live in `tests/support/spec_support/`. Rule-owned tests remain
with their distributable rule folders. Repository consumer smoke checks exercise wheel installation end to end.

Shared document instructions, templates and document rules belong to docs:core. SDD reads both
`uv run devkit get-context spec` and `uv run devkit get-context docs`. The supported SDD asset selection includes
both bundles; restore an explicitly removed docs selection with `uv run devkit add docs`. Removing spec assets
does not uninstall its command extensions or disable its runtime policies.


Development approach is shared project policy: inspect `uv run devkit config show`. `[development] approach`
accepts `sdd` (the absent default) or explicit `adaptive-dev`; bundle/package selection does not change it.
Adaptive development keeps document and project checks without implicit SDD records. The common reader belongs to
devkit-dist; the `project` readiness provider belongs to devkit-agt, and SDD mutation/applicability consumers to
devkit-spec.
