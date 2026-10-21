# devkit-spec

Spec-driven development for AI coding agents, built on [devkit](../../README.md). One Python package ships:

- the `spec` bundle (`devkit.bundles`): instructions, skills, workflows, rules, templates and an opt-in docs skeleton;
- the `devkit spec` command group (`devkit.commands`), mounted under the project's `devkit` executable.

Devkit provides asset distribution, rule/workflow/gate engines, document search, task worktrees and the Agent
Advisory Protocol. This extension adds the Living Spec document model, namespaces, IDs and references, proposals,
spec bundles, code entrypoints, scope registry and SDD guidance. Contracts start at `CAP-HARN-command-mount`
and `CAP-HARN-agent-guidance`; repository documentation starts at [docs/README.md](../../docs/README.md).

## Use in a project

Install from this monorepo's package subdirectory. uv resolves devkit-agt (the harness it builds on), devkit-dist
and devkit-advisory from the same commit:

```bash
uv add --dev "devkit-spec @ git+https://github.com/mjkimR/devkit.git#subdirectory=packages/devkit-spec"
uv run devkit sync                   # deploy the spec bundle's default preset
uv run devkit add spec:docs-skeleton  # optional: seed absent docs/ files, then leave them project-owned
uv run devkit spec --version         # [VERSION: devkit-spec <version>]
```

For release wheels, install the extension and its base dependencies explicitly because they are not hosted on a
package index. Use the filenames and commands in the chosen GitHub Release; see [Releasing](../../README.md#releasing).

A project opts out of the bundle with `[presets] spec = false` in `.devkit/config.toml`. `uv run devkit config
template` writes the supported keys as commented defaults, including this extension's `[tool.spec]` tables.

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

Repository roadmaps use global `docs/roadmap/MS-<slug>.md` milestone documents. Assign one with
`devkit spec proposal new <slug> --milestone MS-<slug>`; only direct PROP anchors are members.
Handoff does not carry milestone metadata into specs, and historical SPEC metadata is ignored.
Direct specs have no milestone creation option;
`proposal new --decomposed-from PROP-<parent>` preserves the original draft's identity. The Backlog and spec-next
skills own lifecycle decisions and next-work ordering. `devkit spec proposal accept <slug> --by user` records the
user's acceptance in one step, after Planning or, with `--direct`, for an eligible draft on the base checkout without
Planning. See `CAP-DOCS-document-model`, `CAP-DLV-proposal-incubation` and `CAP-HARN-agent-guidance`; GitHub issue
integration is excluded.

### Worker result inspection

`devkit spec worker inspect --format json` collects committed worker range and scope information, cleanliness,
envelope validation, rules and workflow checks. Inputs derive from the activity worktree and committed records;
`--unit`, `--base`, `--head`, `--scope` (repeat) or `--scope-file` (one prefix per line), and `--base-checkout` replace
individual inputs. Scope overrides replace the entire scope. Results include provenance and reviewer-ready compared
heads and changed paths. Exit 0 means no failed check, 1 a negative check, 2 an invalid invocation or unresolved
required input; unavailable checks are explicitly not-run. The Host retains scope and acceptance authority.
The command writes and repairs nothing. See `CAP-DLV-delivery-workflows`.
