# devkit

Personal developer tools monorepo.

## Structure

```text
devkit/
├── packages/
│   └── agent-rule-engine/     # Agent-managed rule & governance engine with built-in CLI
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
