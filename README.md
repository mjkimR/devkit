# devkit

Personal developer tools monorepo.

## Structure

```text
devkit/
├── packages/
│   ├── agent-rule-engine/     # Agent-managed rule & governance engine with built-in CLI
│   ├── devkit-distribution/   # Installed resource synchronization (devkit CLI)
│   └── devkit-starter/        # Example content wheel for devkit sync
├── examples/bundles/          # Local distribution examples
├── scripts/                   # Shared shell helpers
└── docs/                      # Documentation and architecture notes
```

## Quick Start

```bash
# Initialize workspace and virtualenv
just init

# Run linter and type checker
just lint
just check

# Run tests
just test

# Run governance rules check
just rules-check
```

Python 3.12+, `uv`, and `just` are required. Module commands discover projects
from `packages/*/pyproject.toml` and `tools/*/pyproject.toml`; use a project name
(for example `just test agent-rule-engine`) or `all`. Extra pytest arguments can
be passed after the module: `just test agent-rule-engine -k cache`.

`just lint-check` verifies formatting without changes. `just test-cov` reports
coverage. See [agent-rule-engine](packages/agent-rule-engine/README.md) for its
feature layout, custom rule API, CLI behavior, and current limits.

The proposed unified lifecycle for agent-native assets, rule bundles, skills,
instructions, playbooks, and presets is documented in the
[agent distribution design](docs/architecture/agent-distribution.md).
The initial [devkit distribution CLI](packages/devkit-distribution/README.md)
supports local bundle validation, packaging, and managed inventory planning.
It also discovers installed content wheels and synchronizes their resources
with receipts, conflict checks, and interrupted-operation recovery.

Consumers install the CLI and content packages together as uv dev dependencies:

```bash
uv add --dev devkit-distribution devkit-starter
uv run devkit sync
uv run devkit list
```

For a local workspace smoke test, use an existing temporary project directory:
`uv run --package devkit-distribution devkit sync --target /tmp/my-project`.
Select native skill/subagent copies with `--agent codex` or `--agent claude-code`.
