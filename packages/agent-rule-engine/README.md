# agent-rule-engine

Agent-managed rule engine for specifications and governance.

## Features

- **Sequential & Cached Execution**: High-speed unified in-memory cache for file reads, YAML frontmatter, markdown AST links, and document catalog.
- **Convergence Autofix**: Automatic remediation with cache invalidation and recheck convergence validation.
- **Pluggable Architecture**: Clear Protocol-based interfaces for deterministic rules and dynamic discovery.
- **CLI & Machine Integration**: Built-in CLI `agent-rules` and structured JSON outputs for external tool or agent integrations.

## CLI Usage

Install the package directly into any project or workspace:

```bash
uv add "git+https://github.com/mjkimR/devkit.git#subdirectory=packages/agent-rule-engine"
```

Run checks:

```bash
# Check files against governance rules
agent-rules check [files...]

# Automatically apply fixes
agent-rules fix [files...]

# Output machine-readable JSON
agent-rules check --format json
```
